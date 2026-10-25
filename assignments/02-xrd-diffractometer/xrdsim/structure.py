"""Structure factors, multiplicities and systematic absences.

A phase carries its cell and an explicit, symmetry-expanded basis; this module turns
that into |F(hkl)|^2 and the multiplicity the powder average needs.
"""

from __future__ import annotations

import cmath
import math

from .atoms import debye_waller, f0
from .lattice import d_spacing


def structure_factor(phase, h: int, k: int, l: int, wavelength: float) -> complex:
    """F(hkl) in electrons, including the Debye-Waller term of every site."""
    d = d_spacing(h, k, l, **phase.cell_kwargs())
    s = 1.0 / (2.0 * d)                 # sin(theta)/lambda, by Bragg's law
    total = 0j
    for site in phase.sites:
        phase_angle = 2.0 * math.pi * (h * site.x + k * site.y + l * site.z)
        total += (site.occupancy * f0(site.element, s) * debye_waller(site.b_iso, s)
                  * cmath.exp(1j * phase_angle))
    return total


def multiplicity(h: int, k: int, l: int, system: str) -> int:
    """Number of symmetry-equivalent planes in the powder average."""
    h, k, l = abs(h), abs(k), abs(l)
    if system == "cubic":
        perms = 6 if len({h, k, l}) == 3 else (3 if len({h, k, l}) == 2 else 1)
        return perms * 2 ** sum(v != 0 for v in (h, k, l))
    if system == "tetragonal":
        hk = 2 if h != k else 1
        return (hk * 2 ** sum(v != 0 for v in (h, k))) * (2 if l else 1)
    if system == "hexagonal":
        if h == 0 and k == 0:
            return 2 if l else 1
        # (h, k) on a mirror plane (h == 0, k == 0 or h == k) has a 6-member in-plane
        # orbit; a general (h, k) has 12. A non-zero l doubles either.
        in_plane = 6 if (h == 0 or k == 0 or h == k) else 12
        return 2 * in_plane if l else in_plane
    raise ValueError(f"multiplicity is not defined for {system!r}")


def lorentz_polarisation(
    two_theta_deg: float, monochromator_two_theta: float | None = None
) -> float:
    """LP factor for an unpolarised tube, optionally with a monochromator."""
    t = math.radians(two_theta_deg)
    theta = t / 2.0
    cos2t = math.cos(t) ** 2
    if monochromator_two_theta is None:
        numerator = 1.0 + cos2t
    else:
        numerator = 1.0 + cos2t * math.cos(math.radians(monochromator_two_theta)) ** 2
    return numerator / (math.sin(theta) ** 2 * math.cos(theta))


def relative_intensity(phase, h: int, k: int, l: int, wavelength: float,
                       monochromator_two_theta: float | None = None) -> float:
    """I/I0 for one reflection: |F|^2 m LP, normalised later across the pattern."""
    f = structure_factor(phase, h, k, l, wavelength)
    d = d_spacing(h, k, l, **phase.cell_kwargs())
    two_theta = math.degrees(2.0 * math.asin(wavelength / (2.0 * d)))
    m = multiplicity(h, k, l, phase.system)
    return abs(f) ** 2 * m * lorentz_polarisation(two_theta, monochromator_two_theta)
