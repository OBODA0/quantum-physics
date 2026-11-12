"""Recover a size distribution from the simulated correlation curve.

The field correlation is linear in the intensity-weighted distribution on a fixed
diameter grid:

    g1(tau_k) = sum_j w_j exp(-Gamma_j tau_k)

so the weights follow from a non-negative least-squares problem with a
second-difference penalty on w. Lags below g1 = 0.01 are dropped (they carry no size
information), and a constant baseline is fitted because the square root used to get
g1 from g2 is concave and leaves a small positive offset where g1 is small.

The recovered w is an intensity distribution. The number distribution divides by the
intensity scattered per particle (d^6 P(qd/2)) and is reported only where the
intensity is above 1 % of its peak: outside that support the measurement has no
sensitivity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import nnls

from .autocorrelation import BOLTZMANN_K
from .mie import scattering_cross_section_weight


@dataclass(frozen=True)
class RecoveredDistribution:
    """Size distribution recovered from the correlation curve."""

    diameter_nm: np.ndarray
    intensity_dist: np.ndarray
    number_dist: np.ndarray
    peak_intensity_nm: float
    peak_number_nm: float
    residual: float
    baseline: float
    support_nm: tuple[float, float]


def _second_difference(points: int) -> np.ndarray:
    matrix = np.zeros((max(points - 2, 0), points))
    for i in range(points - 2):
        matrix[i, i : i + 3] = (1.0, -2.0, 1.0)
    return matrix


def invert_correlation(
    tau_s: np.ndarray,
    g2_minus_1: np.ndarray,
    beta: float,
    q_m_inv: float,
    viscosity_pa_s: float,
    temperature_k: float,
    particle_ri: float,
    solvent_ri: float,
    wavelength_nm: float,
    angle_deg: float,
    grid_points: int = 240,
    regularization: float = 1e-6,
    min_g1: float = 0.01,
    support_fraction: float = 0.01,
) -> RecoveredDistribution:
    """Regularised NNLS inversion of a measured correlation curve."""
    tau = np.asarray(tau_s, dtype=float)
    amplitude = np.clip(np.asarray(g2_minus_1, dtype=float) / beta, 0.0, None)
    g1 = np.sqrt(amplitude)

    keep = g1 >= min_g1
    if int(np.count_nonzero(keep)) < 10:
        keep = np.zeros_like(g1, dtype=bool)
        keep[np.argsort(tau)[: min(10, tau.size)]] = True

    grid = np.geomspace(1.0, 10000.0, int(grid_points))
    diameter_m = grid * 1.0e-9
    gamma = (
        BOLTZMANN_K * float(temperature_k)
        / (3.0 * math.pi * float(viscosity_pa_s) * diameter_m)
    ) * float(q_m_inv) ** 2

    design = np.exp(-np.outer(tau[keep], gamma))
    n = grid.size
    offset = np.hstack(
        [np.ones((int(keep.sum()), 1)), -np.ones((int(keep.sum()), 1))]
    )
    top = np.hstack([design, offset])

    penalty = _second_difference(n)
    scale = float(np.mean(np.diag(design.T @ design))) or 1.0
    middle = np.hstack(
        [np.sqrt(regularization * scale) * penalty, np.zeros((penalty.shape[0], 2))]
    )
    bottom = np.hstack([np.zeros((2, n)), 1e-9 * np.eye(2)])

    solution, _ = nnls(
        np.vstack([top, middle, bottom]),
        np.concatenate([g1[keep], np.zeros(penalty.shape[0]), np.zeros(2)]),
    )
    weights = solution[:n]
    baseline = float(solution[n] - solution[n + 1])
    if weights.sum() <= 0:
        raise ValueError("inversion produced an empty distribution")
    intensity = weights / weights.sum()
    residual = float(
        np.linalg.norm(design @ weights + baseline - g1[keep])
        / max(np.linalg.norm(g1[keep]), 1e-12)
    )

    per_particle = scattering_cross_section_weight(
        grid, particle_ri, solvent_ri, q_m_inv * 1.0e-9
    )
    supported = intensity >= support_fraction * intensity.max()
    number = np.where(supported, intensity / per_particle, 0.0)
    number = number / number.sum()
    supported_grid = grid[supported]

    return RecoveredDistribution(
        diameter_nm=grid,
        intensity_dist=intensity,
        number_dist=number,
        peak_intensity_nm=float(grid[int(np.argmax(intensity))]),
        peak_number_nm=float(grid[int(np.argmax(number))]),
        residual=residual,
        baseline=baseline,
        support_nm=(float(supported_grid[0]), float(supported_grid[-1])),
    )
