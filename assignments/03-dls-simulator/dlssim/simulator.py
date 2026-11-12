"""End-to-end Dynamic Light Scattering (DLS) simulation pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .autocorrelation import AutocorrelationResult, compute_autocorrelation
from .cumulants import CumulantResult, compute_cumulants
from .distribution import SizeDistribution, build_size_distribution
from .mie import optical_contrast_factor, scattering_wavevector
from .solvents import SolventModel, get_solvent


@dataclass(frozen=True)
class DLSInputs:
    """Six core whiteboard inputs plus optional optical geometry settings.

    Whiteboard Specification Inputs
    -------------------------------
    1. solvent : str
        Solvent identifier ('water', 'ethanol', 'pbs', 'toluene').
    2. particle_ri : float
        Refractive index n_p of the nanoparticle at the laser wavelength.
    3. size_nm : float
        Mean hydrodynamic diameter d_0 of the primary nanoparticles (nm).
    4. size_std_rel : float
        Relative standard deviation sigma / d_0 of the primary size distribution.
    5. aggregation : float
        Aggregation parameter alpha_agg in [0, 1] controlling cluster formation.
    6. temperature_c : float
        Sample temperature T in degrees Celsius.
    """

    solvent: str = "water"
    particle_ri: float = 1.590
    size_nm: float = 50.0
    size_std_rel: float = 0.12
    aggregation: float = 0.08
    temperature_c: float = 25.0
    dist_shape: str = "lognormal"
    wavelength_nm: float = 632.8
    angle_deg: float = 173.0
    intercept_beta: float = 0.85
    agg_size_factor: float = 5.5
    noise_level: float = 0.0
    rng_seed: int = 42


@dataclass(frozen=True)
class DLSOutputs:
    """Complete simulation results including the three whiteboard outputs."""

    inputs: DLSInputs
    solvent_model: SolventModel
    temperature_k: float
    viscosity_pa_s: float
    viscosity_mpa_s: float
    solvent_ri: float
    optical_contrast: float
    q_m_inv: float
    q_nm_inv: float
    mean_count_rate_kcps: float
    distribution: SizeDistribution
    autocorrelation: AutocorrelationResult
    cumulants: CumulantResult


def simulate_dls(inputs: DLSInputs) -> DLSOutputs:
    """Run the complete DLS forward model from the 6 whiteboard inputs."""
    solvent_model = get_solvent(inputs.solvent)
    temp_k = float(inputs.temperature_c) + 273.15
    eta_pa_s = solvent_model.viscosity_pa_s(temp_k)
    eta_mpa_s = solvent_model.viscosity_mpa_s(temp_k)
    n_s = solvent_model.refractive_index(temp_k)

    k_opt = optical_contrast_factor(inputs.particle_ri, n_s)
    q_m_inv = scattering_wavevector(
        wavelength_nm=inputs.wavelength_nm,
        solvent_ri=n_s,
        angle_deg=inputs.angle_deg,
    )
    q_nm_inv = q_m_inv * 1.0e-9

    dist = build_size_distribution(
        mean_size_nm=inputs.size_nm,
        rel_width=inputs.size_std_rel,
        aggregation_param=inputs.aggregation,
        particle_ri=inputs.particle_ri,
        solvent_ri=n_s,
        wavelength_nm=inputs.wavelength_nm,
        angle_deg=inputs.angle_deg,
        dist_shape=inputs.dist_shape,
        agg_size_factor=inputs.agg_size_factor,
    )

    # Mean photon count rate (kcps) scales with optical contrast and <d^3>
    ref_kcps = 280.0
    size_scale = (max(float(inputs.size_nm), 1.0) / 50.0) ** 1.2
    contrast_scale = max(k_opt / 0.025, 0.02)
    mean_kcps = float(np.clip(ref_kcps * contrast_scale * size_scale, 15.0, 2500.0))

    autocorr = compute_autocorrelation(
        diameter_nm=dist.diameter_nm,
        intensity_dist=dist.intensity_dist,
        monomer_intensity_dist=dist.monomer_intensity_dist,
        temperature_k=temp_k,
        viscosity_pa_s=eta_pa_s,
        q_m_inv=q_m_inv,
        intercept_beta=inputs.intercept_beta,
        mean_kcps=mean_kcps,
        noise_level=inputs.noise_level,
        rng_seed=inputs.rng_seed,
    )

    cumulants = compute_cumulants(
        tau_s=autocorr.tau_s,
        g2_minus_1=autocorr.g2_minus_1,
        gamma_dist_s_inv=autocorr.gamma_dist_s_inv,
        intensity_dist=dist.intensity_dist,
        temperature_k=temp_k,
        viscosity_pa_s=eta_pa_s,
        q_m_inv=q_m_inv,
        intercept_beta=inputs.intercept_beta,
        size_std_rel=inputs.size_std_rel,
    )

    return DLSOutputs(
        inputs=inputs,
        solvent_model=solvent_model,
        temperature_k=temp_k,
        viscosity_pa_s=eta_pa_s,
        viscosity_mpa_s=eta_mpa_s,
        solvent_ri=n_s,
        optical_contrast=k_opt,
        q_m_inv=q_m_inv,
        q_nm_inv=q_nm_inv,
        mean_count_rate_kcps=mean_kcps,
        distribution=dist,
        autocorrelation=autocorr,
        cumulants=cumulants,
    )
