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
