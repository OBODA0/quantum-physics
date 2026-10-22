"""Lattice geometry: d-spacings, Bragg angles and lattice-parameter refinement.

Lengths are in angstrom, angles in degrees. Only the settings a powder scan needs are
supported here: cubic, tetragonal, hexagonal and orthorhombic.
"""

from __future__ import annotations

import math


def d_spacing(h: int, k: int, l: int, *, a: float, b: float | None = None,
              c: float | None = None, hexagonal: bool = False) -> float:
    """Interplanar spacing in angstrom.

    `hexagonal=True` selects the hexagonal setting (a = b, gamma = 120 degrees).
    Otherwise `b` and `c` both None is cubic, `c` given with `b` None is tetragonal, and
    both `b` and `c` given is orthorhombic. A lone `b` is rejected rather than guessed.
    """
    if a <= 0:
        raise ValueError("lattice parameter must be positive")
    if hexagonal:
        if c is None:
            raise ValueError("the hexagonal setting needs c")
        inv_sq = 4.0 / 3.0 * (h * h + h * k + k * k) / a**2 + l * l / c**2
    elif b is None and c is None:
        inv_sq = (h * h + k * k + l * l) / a**2
    elif b is None:
        inv_sq = (h * h + k * k) / a**2 + l * l / c**2
    elif c is None:
        raise ValueError("an orthorhombic cell needs both b and c; for a tetragonal cell pass c and leave b None")
    else:
        inv_sq = h * h / a**2 + k * k / b**2 + l * l / c**2
    if inv_sq == 0:
        raise ValueError("(0,0,0) has no d-spacing")
    return 1.0 / math.sqrt(inv_sq)


def two_theta(d: float, wavelength: float) -> float:
    """Bragg angle in degrees for a d-spacing, or ValueError if the reflection is unreachable."""
    if d <= 0:
        raise ValueError("d-spacing must be positive")
    s = wavelength / (2.0 * d)
    if s > 1.0:
        raise ValueError(
            f"d = {d:.4f} A is unreachable at lambda = {wavelength:.4f} A (needs sin(theta) > 1)")
    return math.degrees(2.0 * math.asin(s))


def d_from_two_theta(two_theta_deg: float, wavelength: float) -> float:
    """d-spacing in angstrom from a measured 2theta, by Bragg's law."""
    theta = math.radians(two_theta_deg / 2.0)
    s = math.sin(theta)
    if s == 0:
        raise ValueError("2theta = 0 carries no information")
    return wavelength / (2.0 * s)


def refine_cubic_a(peaks: list[tuple[float, int, int, int]], wavelength: float) -> float:
    """Least-squares cubic lattice parameter from indexed peaks.

    `peaks` is a list of (two_theta_deg, h, k, l). The fit is an unweighted least squares
    through the origin, sin^2(theta) = (lambda^2 / 4a^2) * (h^2 + k^2 + l^2): no per-peak
    uncertainties, and no zero-offset term, so a displaced specimen biases the result.
    """
    xs, ys = [], []
    for two_theta_deg, h, k, l in peaks:
        n_sq = h * h + k * k + l * l
        if n_sq == 0:
            raise ValueError("(0,0,0) cannot be indexed")
        xs.append(n_sq)
        ys.append(math.sin(math.radians(two_theta_deg / 2.0)) ** 2)
    denom = sum(x * x for x in xs)
    if denom == 0:
        raise ValueError("no peaks given")
    slope = sum(x * y for x, y in zip(xs, ys)) / denom
    if slope <= 0:
        raise ValueError("degenerate peak list")
    return wavelength / (2.0 * math.sqrt(slope))


def peak_positions(hkls, wavelength: float, **cell) -> list[tuple[tuple[int, int, int], float, float]]:
    """(hkl, d, 2theta) for every reflection the wavelength can reach, sorted by 2theta."""
    out = []
    for h, k, l in hkls:
        d = d_spacing(h, k, l, **cell)
        try:
            out.append(((h, k, l), d, two_theta(d, wavelength)))
        except ValueError:
            continue
    return sorted(out, key=lambda row: row[2])
