"""Stokes-Einstein diffusion, Siegert autocorrelation, and photon count traces."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

BOLTZMANN_K: float = 1.380649e-23  # J / K (exact SI definition)


@dataclass(frozen=True)
class AutocorrelationResult:
    """Simulated DLS autocorrelation functions and photon-count trace I(t)."""

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
    photon_counts_per_bin: np.ndarray
    gate_time_us: float
    trace_contrast: float


def stokes_einstein_diffusion(
    diameter_nm: np.ndarray | float,
    temperature_k: float,
    viscosity_pa_s: float,
) -> np.ndarray | float:
    """Return translational diffusion coefficient D = k_B T / (3 pi eta d) [m^2/s]."""
    d_m = np.asarray(diameter_nm, dtype=float) * 1.0e-9
    d_coeff = BOLTZMANN_K * float(temperature_k) / (
        3.0 * math.pi * float(viscosity_pa_s) * np.maximum(d_m, 1.0e-12)
    )
    if np.ndim(diameter_nm) == 0:
        return float(d_coeff)
    return d_coeff


def _ou_complex_field(
    gamma_s_inv: float,
    dt_s: float,
    n_points: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate a unit-variance complex Ornstein-Uhlenbeck field E(t)."""
    alpha = math.exp(-max(float(gamma_s_inv), 1.0) * dt_s)
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
    return ex + 1j * ey


def simulate_photon_trace(
    gamma_eff_s_inv: float,
    mean_kcps: float,
    intercept_beta: float = 0.85,
    agg_fraction: float = 0.0,
    agg_size_factor: float = 5.5,
    n_points: int = 400,
    rng_seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    """Simulate a Brownian speckle photon-count trace I(t) vs time t.

    Superposes the fast monomer Ornstein-Uhlenbeck field E_mono(t) with a slow
    aggregate field E_agg(t) when agg_fraction > 0, then forms the instantaneous
    intensity I(t) = |E(t)|^2 obeying the Siegert relation:
        G_2(tau) = <I(t) I(t+tau)> = <I>^2 (1 + beta |g_1(tau)|^2).

    Returns (time_ms, counts_kcps, counts_per_bin, gate_time_us, trace_contrast).
    """
    rng = np.random.default_rng(rng_seed)
    gamma_mono = max(float(gamma_eff_s_inv), 10.0)
    tau_char_s = 1.0 / gamma_mono
    total_time_s = 14.0 * tau_char_s
    dt_s = total_time_s / max(n_points - 1, 1)
    time_ms = np.linspace(0.0, total_time_s * 1.0e3, n_points)
    gate_time_us = max(dt_s * 1.0e6, 0.5)

    f_agg = min(max(float(agg_fraction), 0.0), 0.95)
    e_mono = _ou_complex_field(gamma_mono, dt_s, n_points, rng)
    if f_agg > 1.0e-4:
        gamma_agg = gamma_mono / max(float(agg_size_factor), 1.5)
        e_agg = _ou_complex_field(gamma_agg, dt_s, n_points, rng)
        e_tot = math.sqrt(1.0 - f_agg) * e_mono + math.sqrt(f_agg) * e_agg
    else:
        e_tot = e_mono

    speckle = np.abs(e_tot) ** 2
    speckle = speckle / max(float(np.mean(speckle)), 1.0e-12)
    beta_clamped = min(max(float(intercept_beta), 0.05), 1.0)
    s_frac = math.sqrt(beta_clamped)
    norm_intensity = (1.0 - s_frac) + s_frac * speckle

    counts_kcps = float(mean_kcps) * norm_intensity
    # Photon counts per sampling gate bin: N_phot = kcps * 1e3 * dt_s
    mean_counts_bin = counts_kcps * 1.0e3 * (gate_time_us * 1.0e-6)
    counts_per_bin = np.maximum(mean_counts_bin, 0.0)
    contrast = float(
        np.var(counts_kcps) / max(float(np.mean(counts_kcps)) ** 2, 1.0e-12)
    )
    return time_ms, counts_kcps, counts_per_bin, gate_time_us, contrast


def empirical_autocorrelation_from_trace(
    gamma_eff_s_inv: float,
    intercept_beta: float = 0.85,
    agg_fraction: float = 0.0,
    agg_size_factor: float = 5.5,
    n_steps: int = 120_000,
    rng_seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute empirical time-average g_2(tau)-1 directly from a photon trace I(t)."""
    rng = np.random.default_rng(rng_seed)
    gamma_mono = max(float(gamma_eff_s_inv), 10.0)
    tau_char_s = 1.0 / gamma_mono
    dt_s = 0.025 * tau_char_s

    f_agg = min(max(float(agg_fraction), 0.0), 0.95)
    e_mono = _ou_complex_field(gamma_mono, dt_s, n_steps, rng)
    if f_agg > 1.0e-4:
        gamma_agg = gamma_mono / max(float(agg_size_factor), 1.5)
        e_agg = _ou_complex_field(gamma_agg, dt_s, n_steps, rng)
        e_tot = math.sqrt(1.0 - f_agg) * e_mono + math.sqrt(f_agg) * e_agg
    else:
        e_tot = e_mono

    speckle = np.abs(e_tot) ** 2
    speckle = speckle / max(float(np.mean(speckle)), 1.0e-12)
    s_frac = math.sqrt(min(max(float(intercept_beta), 0.05), 1.0))
    intensity = (1.0 - s_frac) + s_frac * speckle
    mean_i = float(np.mean(intensity))

    lag_indices = np.unique(
        np.geomspace(1, min(n_steps // 10, 2500), 45).astype(int)
    )
    tau_emp = lag_indices.astype(float) * dt_s
    g2_emp = np.zeros_like(tau_emp)
    for idx, lag in enumerate(lag_indices):
        prod = float(np.mean(intensity[:-lag] * intensity[lag:]))
        g2_emp[idx] = prod / (mean_i * mean_i) - 1.0
    return tau_emp, g2_emp


def compute_autocorrelation(
    diameter_nm: np.ndarray,
    intensity_dist: np.ndarray,
    monomer_intensity_dist: np.ndarray,
    temperature_k: float,
    viscosity_pa_s: float,
    q_m_inv: float,
    intercept_beta: float = 0.85,
    mean_kcps: float = 250.0,
    agg_fraction: float = 0.0,
    agg_size_factor: float = 5.5,
    n_tau: int = 220,
    tau_min_s: float = 1.0e-7,
    tau_max_s: float = 1.0e0,
    noise_level: float = 0.0,
    rng_seed: int = 42,
) -> AutocorrelationResult:
    """Compute g_1(tau), g_2(tau)-1, G_2(tau), and the photon count trace I(t)."""
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
    mono_gamma = float(np.sum(mono_w * gamma_s_inv))
    mean_diffusion = float(np.sum(weights * d_m2_s))

    (
        time_ms,
        counts_kcps,
        counts_per_bin,
        gate_us,
        contrast,
    ) = simulate_photon_trace(
        gamma_eff_s_inv=mono_gamma,
        mean_kcps=mean_kcps,
        intercept_beta=beta,
        agg_fraction=agg_fraction,
        agg_size_factor=agg_size_factor,
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
        photon_counts_per_bin=counts_per_bin,
        gate_time_us=gate_us,
        trace_contrast=contrast,
    )
