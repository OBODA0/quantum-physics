"""Unit and physics verification tests for the Task 3 DLS simulator."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from dlssim.autocorrelation import (
    empirical_autocorrelation_from_trace,
    stokes_einstein_diffusion,
)
from dlssim.cli import main as cli_main
from dlssim.mie import optical_contrast_factor, scattering_wavevector
from dlssim.simulator import DLSInputs, simulate_dls
from dlssim.solvents import get_solvent, list_solvents


def test_solvents_water_and_ethanol_at_25c() -> None:
    """Verify water and ethanol viscosity and refractive index at 25 C."""
    assert "water" in list_solvents()
    assert "ethanol" in list_solvents()

    water = get_solvent("water")
    ethanol = get_solvent("ethanol")

    eta_w = water.viscosity_mpa_s(298.15)
    eta_e = ethanol.viscosity_mpa_s(298.15)
    assert pytest.approx(eta_w, rel=0.02) == 0.890
    assert pytest.approx(eta_e, rel=0.03) == 1.074
    assert eta_e > eta_w

    # Viscosity must decrease when temperature increases from 20 C to 50 C
    assert water.viscosity_pa_s(323.15) < water.viscosity_pa_s(293.15)
    assert ethanol.viscosity_pa_s(323.15) < ethanol.viscosity_pa_s(293.15)


def test_optical_contrast_and_wavevector() -> None:
    """Verify Lorentz-Lorenz optical contrast and scattering wavevector q."""
    assert pytest.approx(optical_contrast_factor(1.333, 1.333), abs=1e-12) == 0.0
    k_silica = optical_contrast_factor(1.45, 1.333)
    k_tio2 = optical_contrast_factor(2.50, 1.333)
    assert k_tio2 > 10.0 * k_silica

    q_back = scattering_wavevector(632.8, 1.3325, 173.0)
    q_90 = scattering_wavevector(632.8, 1.3325, 90.0)
    assert q_back > q_90 > 0.0


def test_stokes_einstein_scaling() -> None:
    """Verify D(d, T, eta) scales as T / (eta * d)."""
    d_20 = stokes_einstein_diffusion(20.0, 298.15, 0.89e-3)
    d_100 = stokes_einstein_diffusion(100.0, 298.15, 0.89e-3)
    assert pytest.approx(float(d_20) / float(d_100), rel=1e-9) == 5.0


def test_photon_counts_trace_and_empirical_autocorrelation() -> None:
    """Verify Photon Counts vs Time trace I(t) and empirical Siegert convergence."""
    out = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=50.0,
            size_std_rel=0.05,
            aggregation=0.0,
            temperature_c=25.0,
        )
    )
    ac = out.autocorrelation
    assert ac.time_trace_ms.size == ac.photon_counts_kcps.size == 400
    assert ac.photon_counts_per_bin.size == 400
    assert ac.gate_time_us > 0.0
    assert float(np.mean(ac.photon_counts_kcps)) > 10.0

    tau_emp, g2_emp = empirical_autocorrelation_from_trace(
        gamma_eff_s_inv=out.cumulants.gamma_bar_s_inv,
        intercept_beta=0.85,
        agg_fraction=0.0,
        n_steps=80_000,
        rng_seed=42,
    )
    g2_theory = 0.85 * np.exp(-2.0 * out.cumulants.gamma_bar_s_inv * tau_emp)
    assert float(np.max(np.abs(g2_emp - g2_theory))) < 0.06


def test_smaller_vs_larger_particles_and_aggregation() -> None:
    """Verify whiteboard behavior: smaller decays faster; aggregation adds tail."""
    small = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=25.0,
            size_std_rel=0.08,
            aggregation=0.0,
            temperature_c=25.0,
        )
    )
    large = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=125.0,
            size_std_rel=0.08,
            aggregation=0.0,
            temperature_c=25.0,
        )
    )
    aggregated = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=125.0,
            size_std_rel=0.08,
            aggregation=0.35,
            temperature_c=25.0,
        )
    )

    assert small.cumulants.gamma_bar_s_inv > large.cumulants.gamma_bar_s_inv
    assert (
        large.distribution.intensity_mean_nm
        > large.distribution.number_mean_nm
    )
    assert small.cumulants.is_monodisperse is True
    assert small.cumulants.pdi < 0.20
    assert aggregated.cumulants.is_monodisperse is False
    assert aggregated.cumulants.pdi >= 0.20
    assert aggregated.cumulants.z_average_nm > large.cumulants.z_average_nm


def test_cli_generates_all_figures(tmp_path: Path) -> None:
    """Verify CLI runs end-to-end and saves dashboard, trace, and comparison PNGs."""
    dash_png = tmp_path / "dash.png"
    trace_png = tmp_path / "trace.png"
    cmp_png = tmp_path / "cmp.png"
    rc = cli_main(
        [
            "--solvent",
            "ethanol",
            "--ri",
            "1.59",
            "--size-nm",
            "60",
            "--sigma",
            "0.10",
            "--aggregation",
            "0.05",
            "--temp-c",
            "25",
            "--out",
            str(dash_png),
            "--trace-out",
            str(trace_png),
            "--compare-out",
            str(cmp_png),
        ]
    )
    assert rc == 0
    assert dash_png.exists() and dash_png.stat().st_size > 10_000
    assert trace_png.exists() and trace_png.stat().st_size > 10_000
    assert cmp_png.exists() and cmp_png.stat().st_size > 10_000
