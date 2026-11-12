"""Brownian motion and the DLS decay rate.

A sphere of diameter d in a liquid of viscosity eta at temperature T has the
Stokes-Einstein diffusion coefficient

    D = k_B T / (3 pi eta d).

Light scattered at angle theta from a laser of wavelength lambda in a medium of
refractive index n has the scattering vector

    q = (4 pi n / lambda) sin(theta / 2),

and the field correlation decays at the rate

    Gamma = D q^2.
"""

from __future__ import annotations

import numpy as np

from .constants import K_B


def diffusion_coefficient(diameter_m: float, viscosity_pa_s: float, temperature_c: float) -> float:
    """Stokes-Einstein diffusion coefficient, m^2/s."""
    if diameter_m <= 0:
        raise ValueError("diameter must be positive")
    if viscosity_pa_s <= 0:
        raise ValueError("viscosity must be positive")
    temperature_k = temperature_c + 273.15
    if temperature_k <= 0:
        raise ValueError("temperature must be above absolute zero")
    return K_B * temperature_k / (3.0 * np.pi * viscosity_pa_s * diameter_m)


def scattering_vector(refractive_index: float, wavelength_m: float, angle_deg: float) -> float:
    """Scattering vector q, 1/m."""
    if not 0.0 < angle_deg < 180.0:
        raise ValueError("scattering angle must lie between 0 and 180 degrees")
    if wavelength_m <= 0:
        raise ValueError("wavelength must be positive")
    return 4.0 * np.pi * refractive_index / wavelength_m * np.sin(np.deg2rad(angle_deg) / 2.0)


def decay_rate(
    diameter_m: float,
    viscosity_pa_s: float,
    temperature_c: float,
    refractive_index: float,
    wavelength_m: float,
    angle_deg: float,
) -> float:
    """Field-correlation decay rate Gamma = D q^2, 1/s."""
    d = diffusion_coefficient(diameter_m, viscosity_pa_s, temperature_c)
    q = scattering_vector(refractive_index, wavelength_m, angle_deg)
    return d * q**2


def correlation_time(gamma: float) -> float:
    """Characteristic decay time 1/Gamma, s."""
    if gamma <= 0:
        raise ValueError("decay rate must be positive")
    return 1.0 / gamma


def diameter_from_decay_rate(
    gamma: float,
    viscosity_pa_s: float,
    temperature_c: float,
    refractive_index: float,
    wavelength_m: float,
    angle_deg: float,
) -> float:
    """Invert Gamma = D q^2 to a hydrodynamic diameter, m."""
    if gamma <= 0:
        raise ValueError("decay rate must be positive")
    q = scattering_vector(refractive_index, wavelength_m, angle_deg)
    diffusion = gamma / q**2
    temperature_k = temperature_c + 273.15
    return K_B * temperature_k / (3.0 * np.pi * viscosity_pa_s * diffusion)
