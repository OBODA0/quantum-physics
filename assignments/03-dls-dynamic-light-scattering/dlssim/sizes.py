"""Size distributions by number.

A distribution is held as a log-spaced diameter grid plus normalised number weights.
Every other weighting (intensity, volume) is derived from these two arrays, so there
is one source of truth for the sample.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class SizeDistribution:
    """Diameter grid (m) with normalised number weights."""

    diameters_m: np.ndarray
    number_weights: np.ndarray
    label: str = ""

    def __post_init__(self) -> None:
        diameters = np.asarray(self.diameters_m, float)
        weights = np.asarray(self.number_weights, float)
        if diameters.ndim != 1 or weights.shape != diameters.shape:
            raise ValueError("diameters and weights must be 1-D arrays of equal length")
        if np.any(diameters <= 0):
            raise ValueError("diameters must be positive")
        if np.any(weights < 0):
            raise ValueError("weights must be non-negative")
        total = weights.sum()
        if total <= 0:
            raise ValueError("weights must not all be zero")
        object.__setattr__(self, "diameters_m", diameters)
        object.__setattr__(self, "number_weights", weights / total)

    @classmethod
    def monodisperse(cls, diameter_m: float, label: str = "monodisperse") -> "SizeDistribution":
        """Single diameter."""
        return cls(np.array([diameter_m]), np.array([1.0]), label=label)

    @classmethod
    def lognormal(
        cls,
        median_diameter_m: float,
        geometric_sd: float = 1.0,
        points: int = 161,
        span: float = 6.0,
        label: str = "",
    ) -> "SizeDistribution":
        """Lognormal number distribution with the given geometric standard deviation.

        Args:
            median_diameter_m: median diameter (m).
            geometric_sd: geometric standard deviation; 1.0 gives a monodisperse sample.
            points: number of grid points.
            span: half-width of the grid in units of ln(geometric_sd) (ignored when
                geometric_sd == 1).
        """
        if median_diameter_m <= 0:
            raise ValueError("median diameter must be positive")
        if geometric_sd < 1.0:
            raise ValueError("geometric standard deviation must be >= 1")
        if geometric_sd == 1.0:
            return cls.monodisperse(median_diameter_m, label=label or "monodisperse")
        log_sigma = np.log(geometric_sd)
        log_d = np.linspace(
            np.log(median_diameter_m) - span * log_sigma,
            np.log(median_diameter_m) + span * log_sigma,
            points,
        )
        diameters = np.exp(log_d)
        weights = np.exp(-0.5 * ((log_d - np.log(median_diameter_m)) / log_sigma) ** 2)
        return cls(diameters, weights, label=label or f"lognormal sg={geometric_sd:.3f}")

    @property
    def median_m(self) -> float:
        cumulative = np.cumsum(self.number_weights)
        return float(np.interp(0.5, cumulative, self.diameters_m))

    @property
    def mean_m(self) -> float:
        return float(np.sum(self.number_weights * self.diameters_m))

    @property
    def relative_std(self) -> float:
        mean = self.mean_m
        variance = np.sum(self.number_weights * (self.diameters_m - mean) ** 2)
        return float(np.sqrt(variance) / mean)

    def scaled_weights(self, factor: np.ndarray) -> "SizeDistribution":
        """Return the same diameters with number weights multiplied by factor."""
        return SizeDistribution(self.diameters_m, self.number_weights * np.asarray(factor, float), self.label)
