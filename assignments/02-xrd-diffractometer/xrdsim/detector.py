"""Detector: counting statistics and dead time.

A powder scan is a counting experiment. The model returns expected counts per step; the
detector turns them into observed counts with Poisson noise.
"""

from __future__ import annotations

import math


def expected_counts(intensity: float, dwell_s: float) -> float:
    """Mean counts at a step: intensity (counts per second) times dwell time."""
    if dwell_s <= 0:
        raise ValueError("dwell time must be positive")
    return max(intensity, 0.0) * dwell_s


def observe(mean_counts: float, rng) -> float:
    """One Poisson draw for a step. `rng` is a numpy Generator."""
    return float(rng.poisson(max(mean_counts, 0.0)))


def count_noise(mean_counts: float) -> float:
    """Standard deviation of a Poisson count (sqrt(N)); zero for an empty step."""
    return math.sqrt(max(mean_counts, 0.0))


def apply_dead_time(true_rate: float, tau_s: float) -> float:
    """Observed rate for a non-paralysable detector: n = m / (1 + m tau)."""
    if true_rate < 0 or tau_s < 0:
        raise ValueError("rates and dead time must be non-negative")
    return true_rate / (1.0 + true_rate * tau_s)
