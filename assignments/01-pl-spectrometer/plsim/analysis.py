"""Measurements taken with the instrument: excitation spectra and their checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .spectrometer import PLSpectrometer


@dataclass(frozen=True)
class ExcitationScan:
    """PL intensity as a function of excitation wavelength.

    For every excitation wavelength the whole emitted band inside the detection
    range is integrated, so the result depends on how much light the sample
    absorbed, not on a detection window that would go dark for the wrong reason.
    (An earlier version sampled a fixed 565-575 nm window, which collapsed to
    zero once lambda_exc passed 570 nm and produced a fake absorption edge.)

    Every field is either a measurement or the model quantity it is checked
    against, so the scan verifies itself:

    predicted        P_exc * (1 - 10**-A(lambda_exc)) * QY * band_integral
                     -> must reproduce integrated_pl; this checks the sampling,
                     the throughput bookkeeping and linearity.

    Because the emission band shape is independent of the excitation wavelength,
    band_integral is a constant for a fixed detection range, and the measured
    curve must follow the absorbed light exactly.
    """

    wavelengths_nm: np.ndarray
    integrated_pl: np.ndarray
    peak_pl: np.ndarray
    excitation_power: np.ndarray
    absorbed_fraction: np.ndarray
    band_integral: np.ndarray
    quantum_yield: float
    sample_name: str
    detection_range_nm: tuple

    @staticmethod
    def _scaled(curve):
        curve = np.asarray(curve, dtype=float)
        top = curve.max()
        return curve / top if top > 0 else curve

    @property
    def predicted(self):
        """The model's own prediction, including the band integral."""
        return self.excitation_power * self.absorbed_fraction * self.quantum_yield * self.band_integral

    @property
    def agreement(self):
        """Largest relative difference between measurement and model prediction."""
        measured = self._scaled(self.integrated_pl)
        predicted = self._scaled(self.predicted)
        return float(np.max(np.abs(measured - predicted)))

    @property
    def band_integral_drift(self):
        """How far the band integral moves across the sweep (should be ~0)."""
        band = np.asarray(self.band_integral, dtype=float)
        return float(np.max(np.abs(self._scaled(band) - self._scaled(band[:1]))))

    @property
    def measured_peak_wavelength_nm(self):
        """Excitation wavelength that gives the strongest PL."""
        return float(self.wavelengths_nm[int(np.argmax(self.integrated_pl))])


def excitation_scan(
    spectrometer: PLSpectrometer,
    excitation_wavelengths_nm,
    detection_range_nm=(450.0, 800.0),
    dlambda_nm=1.0,
):
    """Measure the PL intensity while the excitation wavelength is swept."""
    wavelengths = np.asarray(excitation_wavelengths_nm, dtype=float)
    if wavelengths.size < 2:
        raise ValueError("an excitation scan needs at least two excitation wavelengths")

    sample = spectrometer.sample
    throughput = spectrometer.detection_monochromator.throughput

    integrated = np.zeros(wavelengths.size)
    peak = np.zeros(wavelengths.size)
    power = np.zeros(wavelengths.size)
    absorbed = np.zeros(wavelengths.size)
    band = np.zeros(wavelengths.size)

    for index, lambda_exc in enumerate(wavelengths):
        scan = spectrometer.acquire(
            lambda_exc_nm=float(lambda_exc),
            lambda_min_nm=detection_range_nm[0],
            lambda_max_nm=detection_range_nm[1],
            dlambda_nm=dlambda_nm,
        )
        emitted = scan.emitted_power
        if emitted.size:
            integrated[index] = float(np.trapezoid(emitted, scan.wavelengths_nm))
            peak[index] = float(emitted.max())

        grid = scan.wavelengths_nm
        density = sample.emission_shape(grid)
        band[index] = float(np.trapezoid(density, grid)) * throughput

        power[index] = scan.excitation_power
        absorbed[index] = sample.absorbed_fraction(float(lambda_exc))

    return ExcitationScan(
        wavelengths_nm=wavelengths,
        integrated_pl=integrated,
        peak_pl=peak,
        excitation_power=power,
        absorbed_fraction=absorbed,
        band_integral=band,
        quantum_yield=sample.quantum_yield,
        sample_name=sample.name,
        detection_range_nm=tuple(float(x) for x in detection_range_nm),
    )


@dataclass(frozen=True)
class EmissionBand:
    """Where a simulated emission band sits and how wide it is."""

    peak_nm: float
    fwhm_nm: float


def measured_emission_band(scan):
    """Peak wavelength and FWHM of the PL band in a scan, ignoring stray light."""
    wavelengths = scan.wavelengths_nm
    emitted = scan.emitted_power
    peak_index = int(np.argmax(emitted))
    half = emitted[peak_index] / 2.0
    above_half = wavelengths[emitted >= half]
    return EmissionBand(
        peak_nm=float(wavelengths[peak_index]),
        fwhm_nm=float(above_half[-1] - above_half[0]),
    )
