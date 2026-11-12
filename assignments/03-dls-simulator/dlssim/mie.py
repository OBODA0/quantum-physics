"""Optical scattering physics for DLS: wavevector q, Rayleigh d^6 law, and RGD form factor.

Connects the particle refractive index n_p and solvent refractive index n_s to the
scattered intensity weighting of each size class:
    I_scat(d) ~ ((m^2 - 1) / (m^2 + 2))^2 * d^6 * P(q * d / 2),   m = n_p / n_s.
"""

from __future__ import annotations

import math

import numpy as np


def scattering_wavevector_nm_inv(
    wavelength_nm: float,
    solvent_ri: float,
    angle_deg: float = 173.0,
) -> float:
    """Scattering wavevector q = (4 pi n_s / lambda_0) sin(theta / 2) in nm^-1."""
    if wavelength_nm <= 0:
        raise ValueError("wavelength_nm must be positive")
    if not (0.0 < angle_deg <= 180.0):
        raise ValueError("angle_deg must be in (0, 180]")
    half_rad = math.radians(angle_deg * 0.5)
    return (4.0 * math.pi * solvent_ri / wavelength_nm) * math.sin(half_rad)


def scattering_wavevector(
    wavelength_nm: float,
    solvent_ri: float,
    angle_deg: float = 173.0,
) -> float:
    """Scattering wavevector q = (4 pi n_s / lambda_0) sin(theta / 2) in m^-1."""
    return scattering_wavevector_nm_inv(wavelength_nm, solvent_ri, angle_deg) * 1.0e9


def optical_contrast_factor(particle_ri: float, solvent_ri: float) -> float:
    """Clausius-Mossotti / Lorentz-Lorenz contrast K_opt = ((m^2 - 1)/(m^2 + 2))^2."""
    if particle_ri <= 0 or solvent_ri <= 0:
        raise ValueError("refractive indices must be positive")
    m2 = (particle_ri / solvent_ri) ** 2
    return ((m2 - 1.0) / (m2 + 2.0)) ** 2


def rgd_sphere_form_factor(
    q_nm_inv: float, diameter_nm: np.ndarray
) -> np.ndarray:
    """Polydispersity-regularized Rayleigh-Gans-Debye / Guinier form factor P(qR)."""
    u = 0.5 * q_nm_inv * np.asarray(diameter_nm, dtype=float)
    out = np.ones_like(u)
    mask = u > 1e-4
    um = u[mask]
    amp = 3.0 * (np.sin(um) - um * np.cos(um)) / (um ** 3)
    p_sphere = amp * amp
    p_guinier = 1.0 / ((1.0 + (um * um) / 5.0) ** 2)
    out[mask] = 0.35 * p_sphere + 0.65 * p_guinier
    return out


def scattering_cross_section_weight(
    diameter_nm: np.ndarray,
    particle_ri: float,
    solvent_ri: float,
    q_nm_inv: float,
) -> np.ndarray:
    """Relative differential scattering cross section per particle of diameter d (nm).

    Scales as K_opt(n_p, n_s) * d^6 * P(q d / 2). When n_p == n_s (index matching), the
    optical contrast vanishes; for d << lambda, P(qR) -> 1 and the classic Rayleigh d^6
    weighting between Number and Intensity distributions holds.
    """
    d = np.asarray(diameter_nm, dtype=float)
    k_opt = optical_contrast_factor(particle_ri, solvent_ri)
    form = rgd_sphere_form_factor(q_nm_inv, d)
    return k_opt * (d ** 6) * form
