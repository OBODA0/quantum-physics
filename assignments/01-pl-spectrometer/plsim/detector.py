"""Detection end: silicon photodiode."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Photodetector:
    """Silicon photodiode converting the selected light into a photocurrent.

    Responsivity R(lambda) is in A/W and the photocurrent is I = R(lambda) * P,
    where P is the optical power reaching the detector. The curve is a smooth
    approximation of a silicon photodiode: weak in the UV, peaking in the near
    infrared, cut off beyond about 1100 nm. Shape model, not a calibration.
    """

    peak_responsivity_aw: float = 0.55
    peak_nm: float = 880.0
    short_sigma_nm: float = 330.0
    long_sigma_nm: float = 110.0

    def responsivity(self, wavelength_nm):
        wl = np.asarray(wavelength_nm, dtype=float)
        sigma = np.where(wl < self.peak_nm, self.short_sigma_nm, self.long_sigma_nm)
        return self.peak_responsivity_aw * np.exp(-0.5 * ((wl - self.peak_nm) / sigma) ** 2)

    def current(self, optical_power, wavelength_nm):
        """Photocurrent for an optical power spectrum, in relative units."""
        return self.responsivity(wavelength_nm) * np.asarray(optical_power, dtype=float)
