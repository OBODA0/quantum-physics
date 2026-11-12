"""Stokes-Einstein diffusion, Siegert autocorrelation, and photon traces."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

BOLTZMANN_K: float = 1.380649e-23  # J / K (exact SI definition)


@dataclass(frozen=True)
class AutocorrelationResult:
    """Simulated DLS autocorrelation functions and photon-count trace."""

    tau_s: np.ndarray
    g1_field: np.ndarray
    g2_minus_1: np.ndarray
    g2_full: np.ndarray
    g2_monomer_only: np.ndarray
    gamma_dist_s_inv: np.ndarray
    diffusion_dist_m2_s: np.ndarray
    mean_diffusion_m2_s: float
    mean_gamma_s_inv: float
    time_trace_ms: np.ndarray
    photon_counts_kcps: np.ndarray


def stokes_einstein_diffusion(
    diameter_nm: np.ndarray | float,
    temperature_k: float,
    viscosity_pa_s: float,
) -> np.ndarray | float:
    """Return translational diffusion coefficient D = k_B T / (3 pi eta d) [m^2/s].

    Parameters
    ----------
    diameter_nm :
        Hydrodynamic diameter d in nanometers.
    temperature_k :
        Absolute temperature T in Kelvin.
    viscosity_pa_s :
        Dynamic viscosity eta(T) of the solvent in Pa*s.
    """
    d_m = np.asarray(diameter_nm, dtype=float) * 1.0e-9
    d_coeff = BOLTZMANN_K * float(temperature_k) / (
        3.0 * math.pi * float(viscosity_pa_s) * np.maximum(d_m, 1.0e-12)
    )
    if np.ndim(diameter_nm) == 0:
        return float(d_coeff)
    return d_coeff


def simulate_photon_trace(
    gamma_eff_s_inv: float,
    mean_kcps: float,
    intercept_beta: float = 0.85,
    n_points: int = 350,
    rng_seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate a Brownian speckle photon-count trace I(t) with exponential G2(tau).

    A complex Ornstein-Uhlenbeck electric field E(t) = E_x(t) + i E_y(t) has
    |g_1(tau)| = exp(-Gamma * tau), and its intensity I(t) = |E(t)|^2 obeys
    the Siegert relation G_2(tau) = <I>^2 (1 + beta |g_1(tau)|^2).
    """
    rng = np.random.default_rng(rng_seed)
    gamma = max(float(gamma_eff_s_inv), 10.0)
    tau_char_s = 1.0 / gamma
    total_time_s = 12.0 * tau_char_s
    dt_s = total_time_s / max(n_points - 1, 1)
    time_ms = np.linspace(0.0, total_time_s * 1.0e3, n_points)

    alpha = math.exp(-gamma * dt_s)
    sigma_step = math.sqrt(max(1.0 - alpha * alpha, 1.0e-12) * 0.5)

    ex = np.zeros(n_points, dtype=float)
    ey = np.zeros(n_points, dtype=float)
    ex[0] = rng.normal(0.0, math.sqrt(0.5))
    ey[0] = rng.normal(0.0, math.sqrt(0.5))
    shocks_x = rng.normal(0.0, sigma_step, size=n_points - 1)
    shocks_y = rng.normal(0.0, sigma_step, size=n_points - 1)
    for k in range(n_points - 1):
        ex[k + 1] = alpha * ex[k] + shocks_x[k]
        ey[k + 1] = alpha * ey[k] + shocks_y[k]

    speckle = ex * ex + ey * ey
    speckle = speckle / max(float(np.mean(speckle)), 1.0e-12)
    beta_clamped = min(max(float(intercept_beta), 0.05), 1.0)
    # Mix coherent speckle with incoherent background to match intercept beta
    s_frac = math.sqrt(beta_clamped)
    norm_intensity = (1.0 - s_frac) + s_frac * speckle
    counts_kcps = float(mean_kcps) * norm_intensity
    return time_ms, counts_kcps


def compute_autocorrelation(
    diameter_nm: np.ndarray,
    intensity_dist: np.ndarray,
    monomer_intensity_dist: np.ndarray,
    temperature_k: float,
    viscosity_pa_s: float,
    q_m_inv: float,
    intercept_beta: float = 0.85,
    mean_kcps: float = 250.0,
    n_tau: int = 220,
    tau_min_s: float = 1.0e-7,
    tau_max_s: float = 1.0e0,
    noise_level: float = 0.0,
    rng_seed: int = 42,
) -> AutocorrelationResult:
    """Compute g_1(tau), g_2(tau)-1, G_2(tau), and a photon count trace I(t)."""
    tau_s = np.logspace(
        math.log10(tau_min_s), math.log10(tau_max_s), n_tau
    )
    d_m2_s = np.asarray(
        stokes_einstein_diffusion(diameter_nm, temperature_k, viscosity_pa_s),
        dtype=float,
    )
    gamma_s_inv = d_m2_s * (float(q_m_inv) ** 2)

    weights = np.asarray(intensity_dist, dtype=float)
    weights = weights / max(float(np.sum(weights)), 1.0e-30)

    mono_w = np.asarray(monomer_intensity_dist, dtype=float)
    mono_w = mono_w / max(float(np.sum(mono_w)), 1.0e-30)

    # Matrix exponential: shape (n_sizes, n_tau)
    decay_matrix = np.exp(-np.outer(gamma_s_inv, tau_s))
    g1_field = weights @ decay_matrix
    g1_mono = mono_w @ decay_matrix

    beta = min(max(float(intercept_beta), 0.05), 1.0)
    g2_minus_1 = beta * (g1_field ** 2)
    g2_monomer_only = beta * (g1_mono ** 2)

    if noise_level > 0.0:
        rng = np.random.default_rng(rng_seed)
        g2_minus_1 = np.clip(
            g2_minus_1 + rng.normal(0.0, noise_level, size=tau_s.size),
            0.0,
            1.2,
        )

    g2_full = 1.0 + g2_minus_1
    mean_gamma = float(np.sum(weights * gamma_s_inv))
    mean_diffusion = float(np.sum(weights * d_m2_s))

    time_ms, counts_kcps = simulate_photon_trace(
        gamma_eff_s_inv=mean_gamma,
        mean_kcps=mean_kcps,
        intercept_beta=beta,
        rng_seed=rng_seed,
    )

    return AutocorrelationResult(
        tau_s=tau_s,
        g1_field=g1_field,
        g2_minus_1=g2_minus_1,
        g2_full=g2_full,
        g2_monomer_only=g2_monomer_only,
        gamma_dist_s_inv=gamma_s_inv,
        diffusion_dist_m2_s=d_m2_s,
        mean_diffusion_m2_s=mean_diffusion,
        mean_gamma_s_inv=mean_gamma,
        time_trace_ms=time_ms,
        photon_counts_kcps=counts_kcps,
    )
