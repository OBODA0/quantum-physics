"""Field and intensity autocorrelation, and cumulant analysis.

For a population with decay rates Gamma_i and intensity weights w_i,

    g1(tau) = sum_i w_i exp(-Gamma_i tau)
    g2(tau) = 1 + beta |g1(tau)|^2

where beta is the coherence factor of the detection optics (0 < beta <= 1).

Cumulant analysis (Koppel 1972, ISO 22412) expands ln g1:

    ln g1(tau) = -Gamma_mean tau + (mu2 / 2) tau^2 - ...

and defines the polydispersity index as PDI = 2 mu2 / Gamma_mean^2.

Fitting ln g1 needs care: at long lags g1 approaches zero and a small absolute error
in g2 becomes a large error in ln g1. The fit therefore weights each lag by the
inverse variance of ln g1 implied by the correlator noise model (see detector.py).
Without those weights the second cumulant is dominated by the noisiest points.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit

from .brownian import diameter_from_decay_rate


@dataclass(frozen=True)
class CumulantResult:
    """Result of a cumulant fit to a measured correlation curve."""

    gamma_mean: float          # 1/s
    mu2: float                 # 1/s^2
    pdi: float                 # dimensionless
    z_average_diameter_m: float
    points_used: int
    window_s: tuple[float, float]
    baseline: float


def field_correlation(tau: np.ndarray, decay_rates: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Normalised field correlation g1(tau)."""
    tau = np.atleast_1d(np.asarray(tau, float))[:, None]
    gammas = np.asarray(decay_rates, float)[None, :]
    w = np.asarray(weights, float)[None, :]
    return (np.exp(-gammas * tau) * w).sum(axis=1)


def intensity_correlation(
    tau: np.ndarray, decay_rates: np.ndarray, weights: np.ndarray, beta: float = 0.9
) -> np.ndarray:
    """Intensity correlation g2(tau) = 1 + beta |g1|^2."""
    if not 0.0 < beta <= 1.0:
        raise ValueError("beta must lie in (0, 1]")
    return 1.0 + beta * field_correlation(tau, decay_rates, weights) ** 2


def analytic_cumulants(decay_rates: np.ndarray, weights: np.ndarray) -> tuple[float, float, float]:
    """Mean, second cumulant and PDI of the decay-rate distribution itself."""
    gammas = np.asarray(decay_rates, float)
    w = np.asarray(weights, float)
    w = w / w.sum()
    mean = float(np.sum(w * gammas))
    mu2 = float(np.sum(w * (gammas - mean) ** 2))
    return mean, mu2, 2.0 * mu2 / mean**2


def cumulant_fit(
    tau: np.ndarray,
    g2: np.ndarray,
    beta: float,
    viscosity_pa_s: float,
    temperature_c: float,
    refractive_index: float,
    wavelength_m: float,
    angle_deg: float,
    duration_s: float = 10.0,
    window_factor: float = 1.5,
    min_points: int = 10,
) -> CumulantResult:
    """Second-order cumulant fit of a measured g2 curve.

    The fit window runs from the shortest lag to ``window_factor`` mean decay times.
    A wider window carries more curvature (better PDI) but more weight from the noisy
    tail; 1.5 decay times keeps the size estimate unbiased and the PDI readable.
    """
    tau = np.asarray(tau, float)
    g2 = np.asarray(g2, float)
    # g2 - 1 = beta |g1|^2, so the field correlation is the square root.
    g1 = np.sqrt(np.clip((g2 - 1.0) / beta, 0.0, None))
    if not np.any(g1 > 0):
        raise ValueError("correlation curve has no decay above the baseline")

    below = np.where(g1 <= 0.5)[0]
    tau_half = float(tau[below[0]]) if len(below) else float(tau[-1])
    if tau_half <= 0:
        raise ValueError("decay time could not be estimated")
    gamma0 = np.log(2.0) / tau_half

    cut = window_factor / gamma0
    mask = (tau > 0) & (tau <= cut)
    if mask.sum() < min_points:
        order = np.argsort(tau)
        mask = np.zeros_like(tau, dtype=bool)
        mask[order[: min(min_points, len(tau))]] = True
    if mask.sum() < 3:
        raise ValueError("not enough points for a quadratic cumulant fit")

    selected = g1[mask]
    # sigma of g2 from the correlator model, propagated to ln g1
    sigma = np.sqrt(2.0 * tau[mask] / duration_s) * (1.0 + beta * selected**2)
    sigma = np.maximum(sigma, 1e-4)
    weights = (selected**2 / sigma) ** 2
    if not np.any(weights > 0):
        weights = np.ones_like(weights)

    y = np.log(np.clip(selected, 1e-12, None))
    coeffs = np.polyfit(tau[mask], y, 2, w=np.sqrt(weights))
    a2, a1, _ = coeffs
    gamma_mean = float(-a1)
    if gamma_mean <= 0:
        raise ValueError("cumulant fit produced a non-positive decay rate")
    mu2 = float(2.0 * a2)

    # Refine on g2 itself. The log-space fit above is the standard initial guess, but
    # it amplifies noise where g1 is small; fitting the second-order cumulant model
    # g2 = 1 + A exp(-2 Gamma tau + mu2 tau^2) with the same weights does not.
    def model(t, amplitude, gamma, second):
        return 1.0 + amplitude * np.exp(-2.0 * gamma * t + second * t * t)

    try:
        popt, _ = curve_fit(
            model,
            tau[mask],
            g2[mask],
            p0=[beta, gamma_mean, mu2],
            sigma=sigma,
            absolute_sigma=True,
            bounds=([0.0, 0.1 * gamma_mean, -1e6], [1.5, 10.0 * gamma_mean, 1e8]),
            maxfev=20000,
        )
        if popt[1] > 0:
            gamma_mean = float(popt[1])
            mu2 = float(popt[2])
    except (RuntimeError, ValueError):
        pass

    pdi = max(0.0, 2.0 * mu2 / gamma_mean**2)
    diameter = diameter_from_decay_rate(
        gamma_mean, viscosity_pa_s, temperature_c, refractive_index, wavelength_m, angle_deg
    )
    return CumulantResult(
        gamma_mean=gamma_mean,
        mu2=mu2,
        pdi=pdi,
        z_average_diameter_m=diameter,
        points_used=int(mask.sum()),
        window_s=(float(tau[mask].min()), float(tau[mask].max())),
        baseline=1.0,
    )
