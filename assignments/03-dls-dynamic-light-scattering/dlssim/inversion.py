"""Recover a size distribution from a correlation curve.

The field correlation is linear in the intensity-weighted distribution:

    g1(tau_k) = sum_j w_j exp(-Gamma_j tau_k)

so the weights w_j on a fixed log-spaced diameter grid follow from a non-negative
least-squares problem. Second differences of w are penalised so that noise does not
produce spikes; the regularisation weight is a stated parameter, not hidden.

Three corrections keep the inversion honest:

* lags where g1 has decayed below ``min_g1`` carry no size information and are
  dropped instead of being fitted as noise;
* each lag is weighted by the inverse standard deviation of the correlator model;
* a constant baseline offset is fitted alongside the distribution. The square root
  used to get g1 from g2 is concave, so noise at long lags leaves a small positive
  offset. Without a baseline term, the inversion explains that offset with spurious
  mass at the largest grid sizes.

The recovered w is an *intensity* distribution. The number distribution is obtained
by dividing by the intensity scattered per particle, and is only reported where the
intensity distribution is above ``support_fraction`` of its peak. Outside that
support the measurement has no sensitivity: one million 1 nm particles and one
100 nm particle scatter the same light, so the data cannot tell them apart.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import nnls

from .constants import K_B
from .scattering import particle_mass, sphere_form_factor


@dataclass(frozen=True)
class InversionResult:
    diameters_m: np.ndarray
    intensity_weights: np.ndarray
    number_weights: np.ndarray
    volume_weights: np.ndarray
    peak_intensity_m: float
    peak_number_m: float
    regularization: float
    residual: float
    support_m: tuple[float, float]
    baseline: float


def diameter_grid(min_m: float = 1e-9, max_m: float = 5e-6, points: int = 200) -> np.ndarray:
    """Log-spaced diameter grid."""
    if min_m <= 0 or max_m <= min_m:
        raise ValueError("grid bounds must satisfy 0 < min < max")
    return np.geomspace(min_m, max_m, points)


def _second_difference(points: int) -> np.ndarray:
    if points < 3:
        return np.zeros((0, points))
    matrix = np.zeros((points - 2, points))
    for i in range(points - 2):
        matrix[i, i : i + 3] = (1.0, -2.0, 1.0)
    return matrix


def decay_rates_for_grid(
    diameters_m: np.ndarray,
    q: float,
    viscosity_pa_s: float,
    temperature_c: float,
) -> np.ndarray:
    """Gamma = D q^2 for each grid diameter."""
    temperature_k = temperature_c + 273.15
    diffusion = K_B * temperature_k / (3.0 * np.pi * viscosity_pa_s * diameters_m)
    return diffusion * q**2


def invert(
    tau: np.ndarray,
    g1: np.ndarray,
    grid_m: np.ndarray,
    q: float,
    viscosity_pa_s: float,
    temperature_c: float,
    density_kg_m3: float,
    regularization: float = 1e-6,
    duration_s: float = 30.0,
    beta: float = 0.9,
    min_g1: float = 0.01,
    support_fraction: float = 0.01,
) -> InversionResult:
    """Regularised NNLS inversion of g1 onto a diameter grid."""
    tau = np.asarray(tau, float)
    g1 = np.asarray(g1, float)
    grid = np.asarray(grid_m, float)

    keep = g1 >= min_g1
    if keep.sum() < 8:
        keep = np.zeros_like(g1, dtype=bool)
        keep[np.argsort(tau)[: min(10, len(tau))]] = True

    selected_tau = tau[keep]
    selected_g1 = g1[keep]
    gammas = decay_rates_for_grid(grid, q, viscosity_pa_s, temperature_c)
    design = np.exp(-np.outer(selected_tau, gammas))

    sigma = np.sqrt(2.0 * np.maximum(selected_tau, 1e-12) / duration_s) * (
        1.0 + beta * selected_g1**2
    )
    sigma = np.maximum(sigma, 1e-4)
    design = design / sigma[:, None]
    target = selected_g1 / sigma

    n = len(grid)
    # free baseline as the difference of two non-negative columns
    offset = np.hstack([np.ones((len(selected_tau), 1)), -np.ones((len(selected_tau), 1))])
    offset = offset / sigma[:, None]
    top = np.hstack([design, offset])

    penalty = _second_difference(n)
    scale = float(np.mean(np.diag(design.T @ design))) or 1.0
    middle = np.hstack([np.sqrt(regularization * scale) * penalty, np.zeros((penalty.shape[0], 2))])
    bottom = np.hstack([np.zeros((2, n)), 1e-9 * np.eye(2)])

    augmented = np.vstack([top, middle, bottom])
    rhs = np.concatenate([target, np.zeros(penalty.shape[0]), np.zeros(2)])
    solution, _ = nnls(augmented, rhs)

    weights = solution[:n]
    baseline = float(solution[n] - solution[n + 1])
    if weights.sum() <= 0:
        raise ValueError("inversion produced an empty distribution")
    intensity = weights / weights.sum()
    residual = float(
        np.linalg.norm(design @ weights + baseline - target) / max(np.linalg.norm(target), 1e-12)
    )

    mass = particle_mass(grid, density_kg_m3)
    per_particle = mass**2 * sphere_form_factor(q, grid)
    supported = intensity >= support_fraction * intensity.max()
    number = np.where(supported, intensity / per_particle, 0.0)
    number = number / number.sum()
    volume = number * grid**3
    volume = volume / volume.sum()

    supported_diameters = grid[supported]
    return InversionResult(
        diameters_m=grid,
        intensity_weights=intensity,
        number_weights=number,
        volume_weights=volume,
        peak_intensity_m=float(grid[np.argmax(intensity)]),
        peak_number_m=float(grid[np.argmax(number)]),
        regularization=float(regularization),
        residual=residual,
        support_m=(float(supported_diameters[0]), float(supported_diameters[-1])),
        baseline=baseline,
    )
