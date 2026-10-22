"""Bragg-Brentano geometry: sample illumination and absorption.

Angles in degrees, lengths in mm, mass attenuation in cm^2/g. The flat-plate,
infinite-thickness case is the one a laboratory powder scan approximates.
"""

from __future__ import annotations

import math


def bragg_angle(two_theta_deg: float) -> float:
    """theta for a given 2theta."""
    return two_theta_deg / 2.0


def footprint_length(two_theta_deg: float, divergence_slit_mm: float,
                     sample_length_mm: float = 20.0) -> float:
    """Length of sample illuminated by the beam, in mm.

    The beam leaves the divergence slit with a fixed width, so the footprint on the
    flat plate grows as 1/sin(theta) and is clipped by the sample holder.
    """
    theta = math.radians(bragg_angle(two_theta_deg))
    if theta <= 0:
        raise ValueError("2theta must be positive")
    return min(sample_length_mm, divergence_slit_mm / math.sin(theta))


def linear_attenuation(density_g_cm3: float, mass_attenuation_cm2_g: float) -> float:
    """mu in 1/cm."""
    if density_g_cm3 <= 0 or mass_attenuation_cm2_g <= 0:
        raise ValueError("density and mass attenuation must be positive")
    return density_g_cm3 * mass_attenuation_cm2_g


def is_infinitely_thick(mu_per_cm: float, thickness_cm: float, threshold: float = 0.01) -> bool:
    """True when exp(-2 mu t / sin(theta)) is negligible; here the worst case theta -> 90 deg."""
    return math.exp(-2.0 * mu_per_cm * thickness_cm) < threshold


def flat_plate_absorption(mu_per_cm: float) -> float:
    """Absorption factor for a thick flat plate: A = 1 / (2 mu), independent of theta."""
    if mu_per_cm <= 0:
        raise ValueError("mu must be positive")
    return 1.0 / (2.0 * mu_per_cm)


def penetration_depth(mu_per_cm: float, two_theta_deg: float, fraction: float = 0.99) -> float:
    """Depth in cm that carries `fraction` of the diffracted intensity."""
    if not 0.0 < fraction < 1.0:
        raise ValueError("fraction must lie in (0, 1)")
    theta = math.radians(bragg_angle(two_theta_deg))
    return -math.log(1.0 - fraction) * math.sin(theta) / (2.0 * mu_per_cm)
