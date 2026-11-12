"""Fractal aggregation of primary particles.

Aggregates are modelled as fractal clusters of N primary particles with fractal
dimension df:

    Rg = (d_primary / 2) * N^(1/df)
    Rh = 0.9 * Rg

The hydrodynamic radius is what DLS measures, so the aggregate appears as a sphere of
diameter 2 Rh. Its scattered intensity uses the Debye structure factor S(q, Rg) and
grows with the square of its mass, which is why a small number of aggregates can
dominate an intensity-weighted distribution.

The 0.9 factor between Rh and Rg is a stated shape assumption for clusters; the
aggregate model is a coarse one, declared in docs/model.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .materials import Material
from .population import Population
from .scattering import debye_structure_factor, particle_mass, sphere_form_factor


@dataclass(frozen=True)
class Aggregation:
    """Aggregation parameters named in the brief."""

    fraction: float = 0.0
    number: int = 10
    fractal_dimension: float = 1.8

    def __post_init__(self) -> None:
        if not 0.0 <= self.fraction <= 1.0:
            raise ValueError("aggregation fraction must lie in [0, 1]")
        if self.number < 1:
            raise ValueError("aggregation number must be at least 1")
        if not 1.0 <= self.fractal_dimension <= 3.0:
            raise ValueError("fractal dimension must lie in [1, 3]")

    @property
    def enabled(self) -> bool:
        return self.fraction > 0.0 and self.number > 1


def build_population(
    size,
    aggregation: Aggregation,
    q: float,
    material: Material,
    label: str = "",
) -> Population:
    """Population of primaries plus fractal aggregates."""
    primaries = Population.from_size_distribution(size, q, material, label=label)
    if not aggregation.enabled:
        return primaries

    n = aggregation.number
    diameters = primaries.diameters_m
    rg = 0.5 * diameters * n ** (1.0 / aggregation.fractal_dimension)
    rh = 0.9 * rg
    aggregate_diameters = 2.0 * rh
    aggregate_masses = n * primaries.masses_kg
    aggregate_form = debye_structure_factor(q, rg)

    keep = (1.0 - aggregation.fraction) * primaries.number_weights
    # one aggregate consumes N primaries, so its number weight is f * w / N
    aggregated = aggregation.fraction * primaries.number_weights / n

    return Population(
        diameters_m=np.concatenate([diameters, aggregate_diameters]),
        masses_kg=np.concatenate([primaries.masses_kg, aggregate_masses]),
        number_weights=np.concatenate([keep, aggregated]),
        form_factors=np.concatenate([primaries.form_factors, aggregate_form]),
        label=label or f"aggregated f={aggregation.fraction:.2f} N={n}",
    )
