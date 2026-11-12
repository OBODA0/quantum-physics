"""Summaries of a simulated measurement."""

from __future__ import annotations

import numpy as np


def peak_position(diameters_m: np.ndarray, weights: np.ndarray) -> float:
    """Diameter at the maximum weight."""
    return float(np.asarray(diameters_m)[int(np.argmax(weights))])


def fwhm(diameters_m: np.ndarray, weights: np.ndarray) -> float:
    """Full width at half maximum of a distribution, in diameter units.

    Linear interpolation between grid points; returns 0 when the distribution never
    falls below half of its peak inside the grid.
    """
    d = np.asarray(diameters_m, float)
    w = np.asarray(weights, float)
    peak = w.max()
    if peak <= 0:
        return 0.0
    above = np.where(w >= 0.5 * peak)[0]
    if len(above) < 2:
        return 0.0
    left = right = None
    i = above[0]
    if i > 0:
        left = np.interp(0.5 * peak, [w[i - 1], w[i]], [d[i - 1], d[i]])
    else:
        left = d[0]
    j = above[-1]
    if j < len(w) - 1:
        right = np.interp(0.5 * peak, [w[j], w[j + 1]], [d[j], d[j + 1]])
    else:
        right = d[-1]
    return float(right - left)


def relative_error(measured: float, truth: float) -> float:
    """(measured - truth) / truth."""
    if truth == 0:
        raise ValueError("truth must be non-zero")
    return float(measured / truth - 1.0)
