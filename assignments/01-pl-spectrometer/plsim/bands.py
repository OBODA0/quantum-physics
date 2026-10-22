"""Spectral band shapes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

FWHM_TO_SIGMA = 1.0 / 2.3548200450309493


def gaussian(wavelength_nm, center_nm, fwhm_nm, peak=1.0):
    """Gaussian band centred on center_nm, with the given FWHM and peak value."""
    wl = np.asarray(wavelength_nm, dtype=float)
    sigma = fwhm_nm * FWHM_TO_SIGMA
    return peak * np.exp(-0.5 * ((wl - center_nm) / sigma) ** 2)


@dataclass(frozen=True)
class GaussianBand:
    """A band with a Gaussian shape, described by centre and FWHM in nm."""

    center_nm: float
    fwhm_nm: float
    peak: float = 1.0

    def __call__(self, wavelength_nm):
        return gaussian(wavelength_nm, self.center_nm, self.fwhm_nm, self.peak)


@dataclass(frozen=True)
class TabulatedBand:
    """A measured band: points on a wavelength grid, interpolated in between.

    Outside the tabulated wavelength range the band is zero, so a spectrum from
    measured data is only defined where it was measured.
    """

    wavelength_nm: tuple
    value: tuple
    name: str = ""

    @classmethod
    def from_lists(cls, wavelength_nm, value, name=""):
        wavelengths = np.asarray(wavelength_nm, dtype=float)
        values = np.asarray(value, dtype=float)
        if wavelengths.size < 2 or wavelengths.size != values.size:
            raise ValueError("a tabulated band needs at least two matching wavelength/value points")
        return cls(tuple(wavelengths), tuple(values), name)

    def __call__(self, wavelength_nm):
        wavelengths = np.asarray(self.wavelength_nm, dtype=float)
        values = np.asarray(self.value, dtype=float)
        return np.interp(np.asarray(wavelength_nm, dtype=float), wavelengths, values, left=0.0, right=0.0)
