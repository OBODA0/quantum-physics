"""Reading a simulated or measured pattern: peak finding, widths and indexing.

The functions here work on arrays (2theta, counts) and make no assumption about where
they came from, so the same code is used on simulator output and on a measured scan.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .profile import scherrer_size


@dataclass(frozen=True)
class Peak:
    two_theta: float
    height: float
    fwhm: float
    area: float


def find_peaks(two_theta: np.ndarray, counts: np.ndarray,
               min_height_fraction: float = 0.02) -> list[Peak]:
    """Local maxima above a fraction of the tallest point, with width and area."""
    x = np.asarray(two_theta, dtype=float)
    y = np.asarray(counts, dtype=float)
    if x.size != y.size or x.size < 3:
        raise ValueError("need matching arrays of at least three points")
    threshold = min_height_fraction * y.max()
    peaks: list[Peak] = []
    for i in range(1, len(y) - 1):
        if not (y[i] >= y[i - 1] and y[i] > y[i + 1] and y[i] >= threshold):
            continue
        centre, height = _refine(x, y, i)
        half = (height + _local_floor(y, i)) / 2.0
        fwhm = _width_at(x, y, i, half)
        area = _area(x, y, i, 4.0 * fwhm if fwhm > 0 else x[1] - x[0])
        peaks.append(Peak(centre, height, fwhm, area))
    return peaks


def _local_floor(y: np.ndarray, i: int, reach: int = 200) -> float:
    left = max(0, i - reach)
    right = min(len(y), i + reach)
    return float(min(y[left:i + 1].min(), y[i:right].min()))


def _width_at(x: np.ndarray, y: np.ndarray, i: int, half: float) -> float:
    left = i
    while left > 0 and y[left] > half:
        left -= 1
    right = i
    while right < len(y) - 1 and y[right] > half:
        right += 1
    if left == i or right == i:
        return 0.0
    x_left = np.interp(half, [y[left], y[left + 1]], [x[left], x[left + 1]])
    x_right = np.interp(half, [y[right], y[right - 1]], [x[right], x[right - 1]])
    return float(x_right - x_left)


def _area(x: np.ndarray, y: np.ndarray, i: int, half_window: float) -> float:
    window = np.abs(x - x[i]) <= half_window
    return float(np.trapezoid(y[window] - np.median(y[window]), x[window]))


def pure_width(observed: float, instrumental: float) -> float:
    """Sample-only FWHM by Gaussian quadrature subtraction, guarded at zero."""
    value = observed * observed - instrumental * instrumental
    return math.sqrt(value) if value > 0 else 0.0


def scherrer_from_peak(peak: Peak, instrumental_fwhm: float, wavelength: float,
                       k: float = 0.9) -> float:
    """Crystallite size in angstrom from one peak, corrected for instrumental width."""
    beta = pure_width(peak.fwhm, instrumental_fwhm)
    if beta <= 0:
        raise ValueError("the peak is not broader than the instrument")
    return scherrer_size(beta, peak.two_theta, wavelength, k)


def index_cubic(two_thetas: list[float],
                max_n_squared: int = 30, tolerance: float = 0.02) -> list[tuple[tuple[int, int, int], float]]:
    """Assign (hkl) to a cubic pattern by the sin^2(theta) ratios.

    The cell returned is the smallest one that fits, so a body-centred pattern comes back
    as a primitive cell with half the conventional edge; `lattice_hint` names that.

    Returns the assignments and the implied n^2 = h^2 + k^2 + l^2. The first reflection
    is taken as the lowest-angle one; every other angle must fall on an integer multiple
    of its sin^2(theta) to within `tolerance` (relative).
    """
    if not two_thetas:
        raise ValueError("no peaks to index")
    s2 = [math.sin(math.radians(t / 2.0)) ** 2 for t in two_thetas]
    base = s2[0]
    for n2_first in range(1, max_n_squared + 1):
        ratios = [value / base * n2_first for value in s2]
        if all(abs(r - round(r)) <= tolerance * max(round(r), 1) for r in ratios):
            assignments = []
            for angle, ratio in zip(two_thetas, ratios):
                n2 = int(round(ratio))
                assignments.append((_hkl_from_n2(n2), angle))
            return assignments
    raise ValueError("the pattern does not index as cubic")


def lattice_hint(n_squared: list[int]) -> str:
    """Describe the lattice from the observed n^2 sequence.

    All-even n^2 means a body-centred lattice described on half the cell; the FCC sequence
    starts 3, 4, 8, 11, 12, 16, 19, 20, 24. Anything else is primitive.
    """
    values = sorted({int(value) for value in n_squared})
    fcc = {3, 4, 8, 11, 12, 16, 19, 20, 24, 27}
    if values and all(value % 2 == 0 for value in values):
        return "body-centred, conventional cell twice the refined edge"
    if set(values) <= fcc:
        return "face-centred (the 3, 4, 8, 11 sequence)"
    if 1 in values:
        return "primitive cell; a body-centred sample would have twice this edge"
    return "primitive lattice"


def _hkl_from_n2(n2: int) -> tuple[int, int, int]:
    for h in range(0, 8):
        for k in range(0, 8):
            l_sq = n2 - h * h - k * k
            if l_sq < 0:
                continue
            l = round(math.isqrt(l_sq))
            if l * l == l_sq:
                return tuple(sorted((h, k, l), reverse=True))
    raise ValueError(f"no (hkl) has n^2 = {n2}")


def _refine(x: np.ndarray, y: np.ndarray, i: int) -> tuple[float, float]:
    """Parabolic refinement of a sampled maximum: position and height between bins."""
    y0, y1, y2 = y[i - 1], y[i], y[i + 1]
    denom = y0 - 2.0 * y1 + y2
    if denom == 0:
        return float(x[i]), float(y[i])
    delta = 0.5 * (y0 - y2) / denom
    if abs(delta) > 0.5:
        return float(x[i]), float(y[i])
    return float(x[i] + delta * (x[i + 1] - x[i])), float(y1 - 0.25 * (y0 - y2) * delta)


def williamson_hall(peaks: list[Peak], instrumental_fwhm_for,
                    wavelength: float, k: float = 0.9) -> tuple[float, float]:
    """Crystallite size and microstrain from the Williamson-Hall plot.

    beta cos(theta) = K lambda / D + 4 epsilon sin(theta), fitted by least squares over the
    peaks given. `instrumental_fwhm_for(two_theta)` returns the instrument width at that
    angle. Returns (size in angstrom, strain) and raises when fewer than two peaks are
    usable.
    """
    xs, ys = [], []
    for peak in peaks:
        beta = pure_width(peak.fwhm, instrumental_fwhm_for(peak.two_theta))
        if beta <= 0 or peak.two_theta <= 0:
            continue
        theta = math.radians(peak.two_theta / 2.0)
        xs.append(4.0 * math.sin(theta))
        ys.append(math.radians(beta) * math.cos(theta))
    if len(xs) < 2:
        raise ValueError("Williamson-Hall needs at least two peaks broader than the instrument")
    slope, intercept = np.polyfit(xs, ys, 1)
    if intercept <= 0:
        raise ValueError("the fit has no positive intercept, so no size can be reported")
    return k * wavelength / intercept, float(slope)


def identify_phase(two_thetas: list[float], phase, instrument,
                   tolerance: float = 0.15,
                   min_intensity_fraction: float = 0.15) -> float:
    """Fraction of a phase's strong reflections that the observed peaks contain.

    A score of 1.0 means every predicted line above `min_intensity_fraction` of the
    phase's strongest has an observed peak within `tolerance` degrees.
    """
    from .diffractometer import reflections
    rows = reflections(phase, instrument)
    if not rows:
        return 0.0
    strongest = max(row.intensity for row in rows)
    predicted = [row.two_theta for row in rows
                 if row.intensity > min_intensity_fraction * strongest]
    if not predicted or not two_thetas:
        return 0.0
    matched = sum(1 for angle in predicted
                  if min(abs(angle - seen) for seen in two_thetas) <= tolerance)
    return matched / len(predicted)


def identify(two_thetas: list[float], phases: dict, instrument,
             tolerance: float = 0.15) -> list[tuple[str, float]]:
    """Rank the phases of a database by how well they explain the observed peak positions."""
    scored = [(key, identify_phase(two_thetas, phase, instrument, tolerance))
              for key, phase in phases.items()]
    return sorted(scored, key=lambda row: (-row[1], row[0]))
