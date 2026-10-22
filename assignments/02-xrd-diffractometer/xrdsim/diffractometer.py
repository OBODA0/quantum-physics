"""The diffractometer: reflections, peak profiles and the scan itself.

A scan is built in counts per step. Reflection intensities are relative (I/I0), as in
Assignment 1: the model reproduces patterns and intensity ratios, not absolute
radiometry.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from . import sources
from .detector import apply_dead_time, expected_counts
from .lattice import d_spacing
from .profile import add_in_quadrature, caglioti_fwhm, pseudo_voigt, size_fwhm
from .samples import Phase
from .structure import lorentz_polarisation, multiplicity, structure_factor


@dataclass(frozen=True)
class Instrument:
    wavelength: float = sources.CU_KA1
    ka2: bool = True
    monochromator_two_theta: float | None = None
    caglioti: tuple[float, float, float] = (0.004, -0.002, 0.003)
    eta: float = 0.5
    reference_counts: float = 20_000.0     # counts at the strongest reflection
    background_rate: float = 0.5           # counts per second, flat
    dwell_s: float = 1.0
    dead_time_s: float = 0.0
    rng_seed: int | None = None      # None: no counting noise; an int seeds the Poisson draws
    max_two_theta: float = 150.0      # no goniometer reaches 180 deg, and LP diverges there
    sample_displacement_mm: float = 0.0  # specimen surface off the goniometer axis
    goniometer_radius_mm: float = 240.0


@dataclass(frozen=True)
class Reflection:
    hkl: tuple[int, int, int]
    d: float
    two_theta: float
    multiplicity: int
    f_squared: float
    intensity: float


@dataclass
class Scan:
    two_theta: np.ndarray
    counts: np.ndarray
    reflections: list[Reflection] = field(default_factory=list)
    phase: Phase | None = None
    instrument: Instrument | None = None



def reflections(phase: Phase, instrument: Instrument, hmax: int = 6) -> list[Reflection]:
    """Every reflection the wavelength reaches, with its relative intensity."""
    rows: list[Reflection] = []
    for h in range(0, hmax + 1):
        for k in range(0, hmax + 1):
            for l in range(0, hmax + 1):
                if h == 0 and k == 0 and l == 0:
                    continue
                if not _representative(h, k, l, phase.system):
                    continue
                try:
                    d = d_spacing(h, k, l, **phase.cell_kwargs())
                except ValueError:
                    continue
                if 2.0 * d < instrument.wavelength:
                    continue
                two_theta = 2.0 * math.degrees(
                    math.asin(instrument.wavelength / (2.0 * d)))
                if two_theta > instrument.max_two_theta:
                    continue
                f = structure_factor(phase, h, k, l, instrument.wavelength)
                m = multiplicity(h, k, l, phase.system)
                lp = lorentz_polarisation(two_theta, instrument.monochromator_two_theta)
                rows.append(Reflection((h, k, l), d, two_theta, m, abs(f) ** 2,
                                       abs(f) ** 2 * m * lp))
    rows.sort(key=lambda r: r.two_theta)
    return rows


def scan(phase: Phase, two_theta_min: float, two_theta_max: float, step: float,
         instrument: Instrument | None = None, size_a: float | None = None,
         hmax: int = 6) -> Scan:
    """Simulate one 2theta scan, with Poisson noise and optional crystallite size."""
    if instrument is None:
        instrument = Instrument()
    if step <= 0 or two_theta_max <= two_theta_min:
        raise ValueError("the scan range and step must be positive")
    grid = np.arange(two_theta_min, two_theta_max + step / 2.0, step)
    rows = reflections(phase, instrument, hmax)
    if not rows:
        raise ValueError("no reachable reflections in this range")

    strongest = max(row.intensity for row in rows)
    if strongest <= 0:
        raise ValueError("every reflection has zero intensity")

    lines = [(instrument.wavelength, 1.0)]
    if instrument.ka2:
        # the doublet is scaled from the instrument's own K-alpha1 so that another anode
        # keeps its own wavelengths instead of silently getting copper's
        ka2 = instrument.wavelength * sources.CU_KA2 / sources.CU_KA1
        lines = [(instrument.wavelength, 1.0), (ka2, sources.KA2_TO_KA1)]

    mean = np.full_like(grid, expected_counts(instrument.background_rate, instrument.dwell_s),
                        dtype=float)
    for row in rows:
        area_total = instrument.reference_counts * row.intensity / strongest
        for wavelength, weight in lines:
            d = d_spacing(*row.hkl, **phase.cell_kwargs())
            centre = 2.0 * math.degrees(math.asin(min(1.0, wavelength / (2.0 * d))))
            centre += displacement_shift(centre, instrument.sample_displacement_mm,
                                         instrument.goniometer_radius_mm)
            width = caglioti_fwhm(centre, *instrument.caglioti)
            if size_a is not None:
                width = add_in_quadrature(width, size_fwhm(size_a, centre, wavelength))
            if not (two_theta_min - 5.0 * width <= centre <= two_theta_max + 5.0 * width):
                continue
            profile = np.array([pseudo_voigt(x, centre, width, instrument.eta) for x in grid])
            mean += area_total * weight * profile * step

    if instrument.dead_time_s:
        rate = mean / instrument.dwell_s
        mean = np.array([apply_dead_time(r, instrument.dead_time_s) * instrument.dwell_s
                         for r in rate])

    if instrument.rng_seed is None:
        counts = mean
    else:
        rng = np.random.default_rng(instrument.rng_seed)
        counts = rng.poisson(np.clip(mean, 0.0, None)).astype(float)

    return Scan(grid, counts, rows, phase, instrument)


def _representative(h: int, k: int, l: int, system: str) -> bool:
    """True for one member of each symmetry family.

    Enumerating h, k, l >= 0 visits every permutation of a reflection; the multiplicity
    already counts the whole orbit, so only the canonical member may be used.
    """
    if system == "cubic":
        return h >= k >= l
    if system == "tetragonal":
        return h >= k
    if system == "hexagonal":
        return h >= k
    return True


def displacement_shift(two_theta_deg: float, displacement_mm: float,
                       radius_mm: float) -> float:
    """2theta shift in degrees for a flat specimen displaced from the goniometer axis.

    Delta(2theta) = -2 s cos(theta) / R, in radians.
    """
    if displacement_mm == 0.0:
        return 0.0
    if radius_mm <= 0:
        raise ValueError('the goniometer radius must be positive')
    theta = math.radians(two_theta_deg / 2.0)
    return math.degrees(-2.0 * displacement_mm * math.cos(theta) / radius_mm)
