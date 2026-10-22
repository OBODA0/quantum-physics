"""Excitation end: xenon lamp, monochromator, harmonic filter."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .bands import FWHM_TO_SIGMA, gaussian

# Relative amplitudes and wavelengths of the strongest xenon emission lines in
# the visible / near-infrared region. Illustrative values, not measured lamp data.
XE_LINES_NM = (
    (450.1, 0.20),
    (462.4, 0.32),
    (467.1, 0.40),
    (823.2, 0.55),
    (828.0, 0.35),
    (881.9, 0.50),
)

LAMP_GRID_NM = (200.0, 1100.0, 0.5)


@dataclass(frozen=True)
class XenonLamp:
    """Xenon arc lamp at the excitation end.

    The spectrum is a smooth approximation of the arc continuum (weak in the
    deep UV, rising through the blue, peaking in the green, tailing into the
    near infrared) plus the strongest xenon emission lines. It is a shape
    model, not a measured lamp spectrum.
    """

    continuum_peak_nm: float = 550.0
    continuum_fwhm_nm: float = 700.0
    line_strength: float = 0.5
    line_fwhm_nm: float = 2.5

    def spectral_radiance(self, wavelength_nm):
        """Relative spectral radiance."""
        continuum = gaussian(wavelength_nm, self.continuum_peak_nm, self.continuum_fwhm_nm)
        lines = np.zeros_like(np.asarray(wavelength_nm, dtype=float))
        for center, amplitude in XE_LINES_NM:
            lines += gaussian(wavelength_nm, center, self.line_fwhm_nm, amplitude)
        return continuum + self.line_strength * lines


@dataclass(frozen=True)
class Monochromator:
    """Grating monochromator: splits light and passes one wavelength band."""

    bandwidth_nm: float = 5.0
    throughput: float = 0.5

    def transmission(self, wavelength_nm, center_nm):
        return gaussian(wavelength_nm, center_nm, self.bandwidth_nm, self.throughput)

    def broaden(self, power, step_nm):
        """Pass a spectrum through the instrument: convolve it with the passband.

        A spectrum measured through the monochromator is the true spectrum
        smeared by the passband, so narrow features (like a stray excitation
        line) come out with the passband width.
        """
        sigma_nm = self.bandwidth_nm * FWHM_TO_SIGMA
        half_width_nm = 4.0 * sigma_nm
        offsets_nm = np.arange(-half_width_nm, half_width_nm + 0.5 * step_nm, step_nm)
        kernel = np.exp(-0.5 * (offsets_nm / sigma_nm) ** 2)
        kernel = kernel / (kernel.sum() * step_nm)
        return np.convolve(power, kernel, mode="same") * step_nm

    def line_at(self, wavelength_nm, center_nm, power):
        """Power density of a line of total power `power` centred on center_nm."""
        sigma_nm = self.bandwidth_nm * FWHM_TO_SIGMA
        return power * gaussian(wavelength_nm, center_nm, self.bandwidth_nm) / (sigma_nm * np.sqrt(2.0 * np.pi))


@dataclass(frozen=True)
class HarmonicFilter:
    """Long-pass filter that blocks the harmonics leaving the monochromator.

    With the grating set to lambda, second-order diffraction also passes
    lambda/2. The filter removes that short-wavelength light before it reaches
    the sample, so the sample is excited by lambda_exc only.
    """

    cutoff_nm: float = 400.0
    blocked_transmission: float = 1e-3

    def transmission(self, wavelength_nm):
        wl = np.asarray(wavelength_nm, dtype=float)
        return np.where(wl >= self.cutoff_nm, 1.0, self.blocked_transmission)


@dataclass(frozen=True)
class ExcitationArm:
    """Lamp -> monochromator -> harmonic filter, delivering light to the sample."""

    lamp: XenonLamp = field(default_factory=XenonLamp)
    monochromator: Monochromator = field(default_factory=Monochromator)
    harmonic_filter: HarmonicFilter = field(default_factory=HarmonicFilter)

    def transmission_profile(self, wavelength_nm, lambda_exc_nm):
        """Fraction of the lamp light at each wavelength that reaches the sample."""
        return self.monochromator.transmission(
            wavelength_nm, lambda_exc_nm
        ) * self.harmonic_filter.transmission(wavelength_nm)

    def power_at(self, lambda_exc_nm):
        """Excitation power delivered to the sample, in relative units."""
        lo, hi, step = LAMP_GRID_NM
        grid = np.arange(lo, hi + step, step)
        profile = self.transmission_profile(grid, lambda_exc_nm)
        return float(np.trapezoid(self.lamp.spectral_radiance(grid) * profile, grid))
