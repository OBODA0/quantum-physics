"""Physics checks for the DLS simulator."""

import numpy as np
import pytest

from dlssim.autocorrelation import compute_autocorrelation, stokes_einstein_diffusion
from dlssim.cumulants import PDI_MONODISPERSE_LIMIT, compute_cumulants
from dlssim.inversion import invert_correlation
from dlssim.mie import optical_contrast_factor, rgd_sphere_form_factor, scattering_wavevector
from dlssim.simulator import DLSInputs, simulate_dls
from dlssim.solvents import get_solvent


def test_stokes_einstein_100_nm_in_water():
    eta = get_solvent("water").viscosity_pa_s(298.15)
    d = stokes_einstein_diffusion(100.0, 298.15, eta)
    assert d == pytest.approx(4.9e-12, rel=0.02)


def test_diffusion_scales_inverse_with_diameter():
    eta = get_solvent("water").viscosity_pa_s(298.15)
    ratio = stokes_einstein_diffusion(20.0, 298.15, eta) / stokes_einstein_diffusion(100.0, 298.15, eta)
    assert float(ratio) == pytest.approx(5.0, rel=1e-9)


def test_scattering_vector_at_backscatter():
    q = scattering_wavevector(632.8, 1.3325, 173.0)
    assert q == pytest.approx(2.64e7, rel=0.01)


def test_contrast_vanishes_when_indices_match_and_grows_with_density():
    assert optical_contrast_factor(1.33, 1.33) == pytest.approx(0.0, abs=1e-15)
    assert optical_contrast_factor(2.50, 1.33) > 10.0 * optical_contrast_factor(1.45, 1.33)


def test_form_factor_limits():
    assert rgd_sphere_form_factor(1e-6, np.array([100.0]))[0] == pytest.approx(1.0, abs=1e-5)
    large = rgd_sphere_form_factor(0.0264, np.array([5000.0]))[0]
    assert large < 0.01


def test_pdi_uses_the_iso_factor_of_two():
    gamma = np.array([1000.0, 2000.0])
    weights = np.array([0.5, 0.5])
    tau = np.logspace(-5, -2, 120)
    g1 = (np.exp(-np.outer(tau, gamma)) * weights).sum(axis=1)
    g2_minus_1 = 0.9 * g1**2
    result = compute_cumulants(
        tau_s=tau,
        g2_minus_1=g2_minus_1,
        gamma_dist_s_inv=gamma,
        intensity_dist=weights,
        temperature_k=298.15,
        viscosity_pa_s=0.89e-3,
        q_m_inv=2.64e7,
        intercept_beta=0.9,
        size_std_rel=0.1,
    )
    # mu2 = 250000, Gamma = 1500 -> PDI = 2 mu2 / Gamma^2 = 0.2222
    assert result.pdi_exact == pytest.approx(0.2222, rel=0.01)
    assert result.pdi_fitted == pytest.approx(result.pdi_exact, rel=0.05)


def test_correlation_decays_faster_for_smaller_particles():
    small = simulate_dls(DLSInputs(size_nm=25.0, size_std_rel=0.08, aggregation=0.0))
    large = simulate_dls(DLSInputs(size_nm=125.0, size_std_rel=0.08, aggregation=0.0))
    assert small.cumulants.gamma_bar_s_inv > large.cumulants.gamma_bar_s_inv


def test_temperature_reduces_viscosity_and_shortens_correlation():
    cold = simulate_dls(DLSInputs(size_nm=100.0, temperature_c=10.0))
    warm = simulate_dls(DLSInputs(size_nm=100.0, temperature_c=40.0))
    assert warm.viscosity_pa_s < cold.viscosity_pa_s
    assert warm.cumulants.gamma_bar_s_inv > cold.cumulants.gamma_bar_s_inv


def test_intensity_distribution_is_shifted_to_larger_sizes():
    out = simulate_dls(DLSInputs(size_nm=60.0, size_std_rel=0.15, aggregation=0.0))
    assert out.distribution.intensity_mean_nm > out.distribution.number_mean_nm


def test_aggregation_increases_size_and_pdi():
    plain = simulate_dls(DLSInputs(size_nm=80.0, size_std_rel=0.08, aggregation=0.0))
    clumped = simulate_dls(DLSInputs(size_nm=80.0, size_std_rel=0.08, aggregation=0.45))
    assert clumped.cumulants.z_average_nm > plain.cumulants.z_average_nm
    assert clumped.cumulants.pdi > plain.cumulants.pdi
    assert plain.cumulants.is_monodisperse
    assert not clumped.cumulants.is_monodisperse


def test_inversion_recovers_a_single_size():
    out = simulate_dls(DLSInputs(size_nm=100.0, size_std_rel=0.05, aggregation=0.0))
    rec = invert_correlation(
        tau_s=out.autocorrelation.tau_s,
        g2_minus_1=out.autocorrelation.g2_minus_1,
        beta=out.inputs.intercept_beta,
        q_m_inv=out.q_m_inv,
        viscosity_pa_s=out.viscosity_pa_s,
        temperature_k=out.temperature_k,
        particle_ri=out.inputs.particle_ri,
        solvent_ri=out.solvent_ri,
        wavelength_nm=out.inputs.wavelength_nm,
        angle_deg=out.inputs.angle_deg,
    )
    assert rec.peak_intensity_nm == pytest.approx(100.0, rel=0.10)
    assert rec.peak_number_nm <= rec.peak_intensity_nm * 1.02
    assert rec.residual < 0.05


def test_pdi_threshold_constant():
    assert PDI_MONODISPERSE_LIMIT == 0.20


def test_unknown_solvent_is_refused():
    with pytest.raises(KeyError):
        get_solvent("benzene")
