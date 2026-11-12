"""Particle materials: refractive index and density at the He-Ne wavelength.

Values are quoted at 633 nm and 20-25 deg C. They are dispersion-corrected
literature values, not fitted to the assignment; provenance in data/SOURCES.md.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Material:
    """A homogeneous, non-absorbing particle material."""

    name: str
    refractive_index: float
    density_kg_m3: float
    description: str


MATERIALS: dict[str, Material] = {
    "polystyrene": Material("polystyrene", 1.5872, 1050.0, "polystyrene latex sphere"),
    "silica": Material("silica", 1.4571, 2000.0, "amorphous silica sphere"),
    "pmma": Material("pmma", 1.4893, 1180.0, "poly(methyl methacrylate) sphere"),
    "titania": Material("titania", 2.6140, 4230.0, "rutile titanium dioxide sphere"),
}
