"""Scattered intensity per particle.

The intensity a particle contributes to the correlation measurement depends on its
mass (more polarisable material scatters more) and on a form factor that accounts for
intra-particle interference at large q d.

Solid spheres use the Rayleigh-Gans-Debye (RGD) sphere form factor. That is exact in
the small-particle limit and approximate when the size approaches the wavelength in
the medium; the limitation is declared in docs/model.md. Aggregates use the Debye
structure factor of a Gaussian chain.
"""

from __future__ import annotations

import numpy as np


def contrast_factor(particle_index: float, solvent_index: float) -> float:
    """Relative refractive-index contrast (m^2 - 1) / (m^2 + 2) with m = n_p / n_s."""
    m = particle_index / solvent_index
    return (m**2 - 1.0) / (m**2 + 2.0)


def particle_mass(diameter_m: np.ndarray | float, density_kg_m3: float) -> np.ndarray | float:
    """Mass of a solid sphere, kg."""
    return density_kg_m3 * np.pi * np.asarray(diameter_m, float) ** 3 / 6.0


def sphere_form_factor(q: float, diameter_m: np.ndarray | float) -> np.ndarray:
    """RGD form factor P(q) of a homogeneous sphere, normalised to 1 at q = 0."""
    d = np.atleast_1d(np.asarray(diameter_m, float))
    x = q * d / 2.0
    out = np.ones_like(x)
    large = x > 1e-3
    xs = x[large]
    out[large] = (3.0 * (np.sin(xs) - xs * np.cos(xs)) / xs**3) ** 2
    return out


def debye_structure_factor(q: float, radius_of_gyration_m: np.ndarray | float) -> np.ndarray:
    """Debye structure factor of a Gaussian coil, normalised to 1 at q = 0."""
    rg = np.atleast_1d(np.asarray(radius_of_gyration_m, float))
    x = (q * rg) ** 2
    out = np.ones_like(x)
    large = x > 1e-6
    xs = x[large]
    out[large] = 2.0 * (np.exp(-xs) - 1.0 + xs) / xs**2
    return out


def intensity_weight(
    mass_kg: np.ndarray,
    form_factor: np.ndarray,
    contrast: float,
    include_contrast: bool = False,
) -> np.ndarray:
    """Relative scattered intensity per particle.

    Rayleigh scattering scales with mass squared. The contrast factor is common to
    all particles of one material and cancels in normalised weights, so it is only
    included when an absolute count rate is wanted.
    """
    weight = np.asarray(mass_kg, float) ** 2 * np.asarray(form_factor, float)
    if include_contrast:
        weight = weight * contrast**2
    return weight
