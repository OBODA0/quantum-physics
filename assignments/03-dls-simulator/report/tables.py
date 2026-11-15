"""Generate publication-quality tables and parameter studies for Assignment 3."""

from __future__ import annotations

import math

from dlssim.autocorrelation import BOLTZMANN_K
from dlssim.simulator import DLSInputs, simulate_dls
from dlssim.solvents import SOLVENTS, get_solvent


def table_solvents_properties() -> list[list[str]]:
    """Table of standard solvent physical and optical properties at 25 C."""
    header = [
        "Solvent",
        "Formula",
        "Refractive Index n (25 C)",
        "Viscosity eta (mPa*s)",
        "Temperature Coeff dn/dT (1/K)",
    ]
    rows = [header]
    for _, s in SOLVENTS.items():
        rows.append([
            s.name,
            s.formula,
            f"{s.ri_25c:.4f}",
            f"{s.eta_25c_mpas:.3f}",
            f"{s.dn_dt:.1e}",
        ])
    return rows


def table_stokes_einstein_validation() -> list[list[str]]:
    """Validation table comparing theoretical Stokes-Einstein diffusion with simulator."""
    header = [
        "Nominal Size d0 (nm)",
        "Theoretical D (um^2/s)",
        "Theoretical Gamma (s^-1)",
        "Simulator D_z (um^2/s)",
        "Fitted D_z (nm)",
        "Relative Error (%)",
    ]
    rows = [header]
    water = get_solvent("water")
    eta = water.viscosity_pa_s(298.15)
    test_sizes = [20.0, 50.0, 100.0, 200.0]
    for d in test_sizes:
        d_m = d * 1e-9
        d_theory = BOLTZMANN_K * 298.15 / (3.0 * math.pi * eta * d_m)
        res = simulate_dls(
            DLSInputs(
                solvent="water",
                particle_ri=1.590,
                size_nm=d,
                size_std_rel=0.04,  # near monodisperse baseline
                aggregation=0.0,
                temperature_c=25.0,
            )
        )
        q = res.q_m_inv
        gamma_theory = d_theory * (q ** 2)
        d_sim = res.cumulants.z_avg_diffusion_m2_s
        dz_fitted = res.cumulants.z_average_nm
        rel_err = abs(dz_fitted - d) / d * 100.0
        rows.append([
            f"{d:.1f}",
            f"{d_theory * 1e12:.3f}",
            f"{gamma_theory:.1f}",
            f"{d_sim * 1e12:.3f}",
            f"{dz_fitted:.2f}",
            f"{rel_err:.2f} %",
        ])
    return rows


def table_size_variation() -> list[list[str]]:
    """Study of varying particle hydrodynamic diameter d_0 in water at 25 C."""
    sizes = [10.0, 25.0, 50.0, 100.0, 200.0, 500.0]
    header = [
        "d_0 (nm)",
        "D_z (um^2/s)",
        "Gamma_bar (s^-1)",
        "tau_c (ms)",
        "D_z fitted (nm)",
        "PDI",
        "Verdict",
    ]
    rows = [header]
    for d in sizes:
        res = simulate_dls(
            DLSInputs(
                solvent="water",
                particle_ri=1.590,
                size_nm=d,
                size_std_rel=0.10,
                aggregation=0.0,
                temperature_c=25.0,
            )
        )
        c = res.cumulants
        tau_c = 1e3 / max(c.gamma_bar_s_inv, 1e-9)
        rows.append([
            f"{d:.1f}",
            f"{c.z_avg_diffusion_m2_s * 1e12:.3f}",
            f"{c.gamma_bar_s_inv:.1f}",
            f"{tau_c:.3f}",
            f"{c.z_average_nm:.1f}",
            f"{c.pdi:.4f}",
            "Monodisperse" if c.is_monodisperse else "Polydisperse",
        ])
    return rows


def table_aggregation_study() -> list[list[str]]:
    """Study of varying aggregation parameter alpha_agg at fixed d_0 = 50 nm, sigma/d0 = 0.12."""
    aggs = [0.00, 0.05, 0.10, 0.14, 0.20, 0.35]
    header = [
        "alpha_agg",
        "N-mean (nm)",
        "I-mean (nm)",
        "Z-avg D_z (nm)",
        "PDI",
        "PDI < 0.2 Criterion",
    ]
    rows = [header]
    for a in aggs:
        res = simulate_dls(
            DLSInputs(
                solvent="water",
                particle_ri=1.590,
                size_nm=50.0,
                size_std_rel=0.12,
                aggregation=a,
                temperature_c=25.0,
            )
        )
        c = res.cumulants
        dist = res.distribution
        rows.append([
            f"{a:.2f}",
            f"{dist.number_mean_nm:.1f}",
            f"{dist.intensity_mean_nm:.1f}",
            f"{c.z_average_nm:.1f}",
            f"{c.pdi:.4f}",
            "PASSED (< 0.20)" if c.is_monodisperse else "FAILED (>= 0.20)",
        ])
    return rows


def table_temperature_dependence() -> list[list[str]]:
    """Study of temperature variation T = 15 to 50 C for 50 nm particles in water."""
    temps = [15.0, 20.0, 25.0, 37.0, 50.0]
    header = [
        "T (C)",
        "eta(T) (mPa*s)",
        "n_s(T)",
        "q (10^7 m^-1)",
        "D_z (um^2/s)",
        "Gamma_bar (s^-1)",
        "tau_c (ms)",
    ]
    rows = [header]
    for t in temps:
        res = simulate_dls(
            DLSInputs(
                solvent="water",
                particle_ri=1.590,
                size_nm=50.0,
                size_std_rel=0.10,
                aggregation=0.0,
                temperature_c=t,
            )
        )
        c = res.cumulants
        tau_c = 1e3 / max(c.gamma_bar_s_inv, 1e-9)
        rows.append([
            f"{t:.1f}",
            f"{res.viscosity_mpa_s:.3f}",
            f"{res.solvent_ri:.4f}",
            f"{res.q_m_inv * 1e-7:.3f}",
            f"{c.z_avg_diffusion_m2_s * 1e12:.3f}",
            f"{c.gamma_bar_s_inv:.1f}",
            f"{tau_c:.3f}",
        ])
    return rows
