"""X-ray source: the copper tube and its emission lines.

Wavelengths in angstrom. The K-alpha doublet is what a powder pattern shows; K-beta is
normally removed by a filter or a monochromator and is only modelled to show why.
"""

from __future__ import annotations

from dataclasses import dataclass

CU_KA1 = 1.540598
CU_KA2 = 1.544426
CU_KB = 1.392250

# K-alpha2 / K-alpha1 intensity ratio, and K-beta / K-alpha ratio for a Cu tube.
KA2_TO_KA1 = 0.497
KB_TO_KA = 0.20


@dataclass(frozen=True)
class Line:
    wavelength: float
    weight: float


def emission_lines(ka2: bool = True, kbeta: bool = False) -> list[Line]:
    """Emission lines of a Cu tube with their relative intensities."""
    lines = [Line(CU_KA1, 1.0)]
    if ka2:
        lines.append(Line(CU_KA2, KA2_TO_KA1))
    if kbeta:
        lines.append(Line(CU_KB, KB_TO_KA * (1.0 + (KA2_TO_KA1 if ka2 else 0.0))))
    return lines


def weighted_wavelength(lines: list[Line]) -> float:
    """Intensity-weighted mean wavelength of the lines in use."""
    total = sum(line.weight for line in lines)
    if total <= 0:
        raise ValueError("no lines")
    return sum(line.wavelength * line.weight for line in lines) / total
