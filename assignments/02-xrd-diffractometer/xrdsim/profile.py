"""Peak profiles and the instrument resolution function.

The profile is normalised to unit area, so a peak's height follows from its integrated
intensity and its width. Angles are in degrees, widths are FWHM in degrees.
"""

from __future__ import annotations

import math

TWO_LN2 = 2.0 * math.log(2.0)


def gaussian(x: float, center: float, fwhm: float) -> float:
    """Unit-area Gaussian."""
    sigma = fwhm / (2.0 * math.sqrt(TWO_LN2))
    z = (x - center) / sigma
    return math.exp(-0.5 * z * z) / (sigma * math.sqrt(2.0 * math.pi))


def lorentzian(x: float, center: float, fwhm: float) -> float:
    """Unit-area Lorentzian."""
    half = fwhm / 2.0
    return (half / math.pi) / ((x - center) ** 2 + half * half)


def pseudo_voigt(x: float, center: float, fwhm: float, eta: float) -> float:
    """Unit-area pseudo-Voigt: eta of Lorentzian mixed with (1 - eta) of Gaussian."""
    if not 0.0 <= eta <= 1.0:
        raise ValueError("eta must lie in [0, 1]")
    return eta * lorentzian(x, center, fwhm) + (1.0 - eta) * gaussian(x, center, fwhm)


def caglioti_fwhm(two_theta_deg: float, U: float, V: float, W: float) -> float:
    """Instrumental FWHM in degrees: U tan^2(theta) + V tan(theta) + W."""
    t = math.tan(math.radians(two_theta_deg / 2.0))
    value = U * t * t + V * t + W
    return math.sqrt(max(value, 0.0))


def scherrer_size(fwhm_deg: float, two_theta_deg: float, wavelength: float,
                  k: float = 0.9) -> float:
    """Crystallite size in angstrom from a sample-broadened FWHM (Scherrer).

    `fwhm_deg` must already be corrected for instrumental broadening.
    """
    if fwhm_deg <= 0:
        raise ValueError("FWHM must be positive")
    beta = math.radians(fwhm_deg)
    theta = math.radians(two_theta_deg / 2.0)
    return k * wavelength / (beta * math.cos(theta))


def size_fwhm(size_a: float, two_theta_deg: float, wavelength: float,
              k: float = 0.9) -> float:
    """FWHM in degrees produced by a crystallite of `size_a` angstrom (inverse Scherrer)."""
    if size_a <= 0:
        raise ValueError("size must be positive")
    theta = math.radians(two_theta_deg / 2.0)
    return math.degrees(k * wavelength / (size_a * math.cos(theta)))


def add_in_quadrature(*fwhms: float) -> float:
    """Combine Gaussian widths."""
    return math.sqrt(sum(f * f for f in fwhms))


def pseudo_voigt_array(x, center: float, fwhm: float, eta: float):
    """Unit-area pseudo-Voigt over an array; same numbers as pseudo_voigt, vectorised."""
    import numpy as np
    if not 0.0 <= eta <= 1.0:
        raise ValueError("eta must lie in [0, 1]")
    values = np.asarray(x, dtype=float)
    sigma = fwhm / (2.0 * math.sqrt(TWO_LN2))
    half = fwhm / 2.0
    z = (values - center) / sigma
    gaussian_part = np.exp(-0.5 * z * z) / (sigma * math.sqrt(2.0 * math.pi))
    lorentzian_part = (half / math.pi) / ((values - center) ** 2 + half * half)
    return eta * lorentzian_part + (1.0 - eta) * gaussian_part


def laue_interference_array(two_theta_deg, two_theta_bragg_deg: float, d_a: float,
                            n_planes: int, wavelength: float):
    """Unit-area exact N-plane Laue profile |sin(N u) / (N sin u)|^2 in 2theta.

    Contains no empirical Scherrer constant K: the width and sinc^2 sidelobes emerge
    solely from summing N coherent atomic planes of spacing `d_a`.
    """
    import numpy as np
    if n_planes < 1:
        raise ValueError("n_planes must be at least 1")
    angles = np.asarray(two_theta_deg, dtype=float)
    theta_b = math.radians(two_theta_bragg_deg / 2.0)
    sin_diff = np.sin(np.radians(angles / 2.0)) - math.sin(theta_b)
    u = 2.0 * math.pi * d_a * sin_diff / wavelength
    denom = n_planes * np.sin(u)
    safe_denom = np.where(np.abs(denom) < 1e-12, 1.0, denom)
    profile = np.where(
        np.abs(denom) < 1e-12, 1.0, (np.sin(n_planes * u) / safe_denom) ** 2
    )
    trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
    area = float(trapz(profile, angles))
    return profile / area if area > 0 else profile


def convolve_laue_with_instrument(
    two_theta_deg, two_theta_bragg_deg: float, d_a: float,
    n_planes: int, wavelength: float, inst_fwhm_deg: float,
):
    """Direct numerical convolution of the N-plane Laue profile with h_inst."""
    import numpy as np
    angles = np.asarray(two_theta_deg, dtype=float)
    step = float(angles[1] - angles[0])
    laue = laue_interference_array(
        angles, two_theta_bragg_deg, d_a, n_planes, wavelength
    )
    sigma = inst_fwhm_deg / (2.0 * math.sqrt(TWO_LN2))
    half_span = max(0.5, 6.0 * sigma)
    kx = np.arange(-half_span, half_span + step / 2.0, step)
    kernel = np.exp(-0.5 * (kx / sigma) ** 2) / (sigma * math.sqrt(2.0 * math.pi))
    return np.convolve(laue, kernel, mode="same") * step

