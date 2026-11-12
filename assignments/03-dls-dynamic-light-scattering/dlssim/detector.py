"""Photon detection: count-rate trace and correlator noise.

Two separate models, both declared as models rather than first-principles photon
transport:

1. The count trace used in figures is an intensity process whose normalised
   covariance is exactly beta |g1|^2. It is built from a complex Gaussian field E,
   so the intensity is non-negative by construction:

       I(t) = 1 - sqrt(beta) + sqrt(beta) |E(t)|^2

2. The measured correlation curve carries correlator noise. With a total
   acquisition time T, the number of independent pairs at lag tau is about T/(2 tau),
   so the standard deviation of g2 is

       sigma(tau) = sqrt(2 tau / T) * (1 + beta |g1|^2).

   This reproduces the two properties that matter: longer acquisition gives less
   noise, and long lags are noisier than short ones.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DetectorConfig:
    """Acquisition settings."""

    duration_s: float = 30.0
    sample_interval_s: float = 1e-6
    beta: float = 0.9
    count_rate_cps: float = 1.0e5
    dead_time_s: float = 0.0

    def __post_init__(self) -> None:
        if self.duration_s <= 0:
            raise ValueError("duration must be positive")
        if self.sample_interval_s <= 0:
            raise ValueError("sample interval must be positive")
        if not 0.0 < self.beta <= 1.0:
            raise ValueError("beta must lie in (0, 1]")
        if self.count_rate_cps < 0:
            raise ValueError("count rate must be non-negative")
        if self.dead_time_s < 0:
            raise ValueError("dead time must be non-negative")


def photon_trace(
    field_correlation,
    tau_c: float,
    config: DetectorConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Photon counts per sample interval for an illustrative trace.

    The sample interval is chosen from the correlation time (one tenth of it), so the
    trace shows the fluctuation envelope rather than single-photon clicks. The
    requested acquisition time is an upper bound; the trace covers at most 200
    correlation times, which is enough to see the decay.

    Args:
        field_correlation: callable tau -> g1(tau), normalised.
        tau_c: mean correlation time, s.
        config: acquisition settings.
        rng: random generator.
    """
    dt = max(config.sample_interval_s, tau_c / 10.0)
    n = int(min(config.duration_s / dt, 2_000))
    if n < 64:
        raise ValueError("trace needs at least 64 samples; increase duration")
    lags = np.arange(n) * dt

    # Evaluate g1 in blocks: the full lag-by-population outer product would need
    # (n x number of decay rates) memory.
    blocks = np.array_split(lags, max(1, n // 5000))
    g1 = np.concatenate([np.asarray(field_correlation(block), float) for block in blocks])
    g1[0] = 1.0
    spectrum = np.real(np.fft.fft(g1))
    spectrum = np.clip(spectrum, 0.0, None)

    white = (rng.normal(size=n) + 1j * rng.normal(size=n)) / np.sqrt(2.0)
    field = np.fft.ifft(np.sqrt(spectrum) * white)
    power = np.abs(field) ** 2
    power = power / power.mean()

    root_beta = np.sqrt(config.beta)
    intensity = 1.0 - root_beta + root_beta * power

    if config.dead_time_s > 0:
        # non-paralyzable dead-time correction on the mean rate
        intensity = intensity / (1.0 + config.count_rate_cps * config.dead_time_s)

    expected = config.count_rate_cps * dt * intensity
    return rng.poisson(expected)


def measured_correlation(
    tau: np.ndarray,
    g2: np.ndarray,
    beta: float,
    duration_s: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Add correlator noise to an ideal g2 curve.

    The returned curve has the same lags as the input.
    """
    tau = np.asarray(tau, float)
    g2 = np.asarray(g2, float)
    if duration_s <= 0:
        raise ValueError("duration must be positive")
    amplitude = np.clip(g2 - 1.0, 0.0, None)
    sigma = np.sqrt(2.0 * np.maximum(tau, 1e-12) / duration_s) * (1.0 + amplitude)
    return g2 + rng.normal(0.0, 1.0, size=g2.shape) * sigma
