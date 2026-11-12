"""A scattering population: diameters, masses, number weights and form factors.

Keeping all four arrays together prevents the classic bug where the number
distribution and the intensity distribution are built from different populations.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .materials import Material
from .sizes import SizeDistribution
from .scattering import particle_mass, sphere_form_factor


@dataclass(frozen=True)
class Population:
    """Particles present in the scattering volume."""

    diameters_m: np.ndarray
    masses_kg: np.ndarray
    number_weights: np.ndarray
    form_factors: np.ndarray
    label: str = ""

    def __post_init__(self) -> None:
        weights = np.asarray(self.number_weights, float)
        total = weights.sum()
        if total <= 0:
            raise ValueError("number weights must not all be zero")
        object.__setattr__(self, "diameters_m", np.asarray(self.diameters_m, float))
        object.__setattr__(self, "masses_kg", np.asarray(self.masses_kg, float))
        object.__setattr__(self, "form_factors", np.asarray(self.form_factors, float))
        object.__setattr__(self, "number_weights", weights / total)

    def intensity_weights(self, contrast: float = 1.0) -> np.ndarray:
        """Normalised intensity weights (Rayleigh mass-squared times form factor)."""
        raw = self.number_weights * self.masses_kg**2 * self.form_factors * contrast**2
        total = raw.sum()
        if total <= 0:
            raise ValueError("intensity weights sum to zero")
        return raw / total

    @classmethod
    def from_size_distribution(
        cls, size: SizeDistribution, q: float, material: Material, label: str = ""
    ) -> "Population":
        """Build solid spheres from a number distribution."""
        masses = particle_mass(size.diameters_m, material.density_kg_m3)
        form = sphere_form_factor(q, size.diameters_m)
        return cls(size.diameters_m, masses, size.number_weights, form, label or size.label)
