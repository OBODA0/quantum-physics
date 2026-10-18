"""The full instrument, from lamp to photocurrent."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .detector import Photodetector
from .samples import Dye
from .sources import ExcitationArm, Monochromator


@dataclass(frozen=True)
class PLScan:
    """One simulated PL measurement."""

    sample_name: str
    lambda_exc_nm: float
    wavelengths_nm: np.ndarray
    excitation_power: float
    emitted_power: np.ndarray
    scatter_power: np.ndarray
    emitted_photocurrent: np.ndarray
    scatter_photocurrent: np.ndarray
    photocurrent: np.ndarray
    scatter_fraction: float

    @property
    def detected_power(self):
        """Optical power reaching the detector: PL plus stray excitation light."""
        return self.emitted_power + self.scatter_power

    @property
    def emission_peak_nm(self):
        """Wavelength of the strongest emitted PL."""
        return float(self.wavelengths_nm[int(np.argmax(self.emitted_power))])

    @property
    def scatter_inside_range(self):
        """True when stray excitation light falls inside the detection range."""
        return (
            self.scatter_fraction > 0.0
            and self.wavelengths_nm[0] <= self.lambda_exc_nm <= self.wavelengths_nm[-1]
        )


@dataclass(frozen=True)
class PLSpectrometer:
    """Photoluminescence spectrometer simulator.

    Excitation end: xenon lamp, monochromator set to lambda_exc, harmonic
    filter. Sample: a dye from the sample database. Detection end: monochromator
    scanning lambda_min to lambda_max in steps of dlambda, then a photodiode.
    """

    sample: Dye
    excitation: ExcitationArm = field(default_factory=ExcitationArm)
    detection_monochromator: Monochromator = field(
        default_factory=lambda: Monochromator(bandwidth_nm=2.0)
    )
    detector: Photodetector = field(default_factory=Photodetector)
    scatter_fraction: float = 0.01
    """Fraction of the excitation light that reaches the detector as stray
    light. The harmonic filter and the detection monochromator reduce it, but
    never remove it."""

    def acquire(
        self,
        lambda_exc_nm=550.0,
        lambda_min_nm=500.0,
        lambda_max_nm=750.0,
        dlambda_nm=1.0,
    ):
        if dlambda_nm <= 0.0:
            raise ValueError("dlambda must be positive")
        if lambda_max_nm <= lambda_min_nm:
            raise ValueError("lambda_max must be greater than lambda_min")

        wavelengths = np.arange(lambda_min_nm, lambda_max_nm + 0.5 * dlambda_nm, dlambda_nm)

        step_nm = float(wavelengths[1] - wavelengths[0]) if wavelengths.size > 1 else dlambda_nm
        detection = self.detection_monochromator

        excitation_power = self.excitation.power_at(lambda_exc_nm)
        emitted_power = detection.throughput * detection.broaden(
            self.sample.emitted_power(wavelengths, lambda_exc_nm, excitation_power), step_nm
        )
        scatter_power = detection.throughput * detection.line_at(
            wavelengths, lambda_exc_nm, self.scatter_fraction * excitation_power
        )

        # Optical powers and photocurrents are kept separate: a figure that draws
        # an optical power on an axis labelled in current is drawn in two units.
        emitted_photocurrent = self.detector.current(emitted_power, wavelengths)
        scatter_photocurrent = self.detector.current(scatter_power, wavelengths)
        photocurrent = emitted_photocurrent + scatter_photocurrent

        return PLScan(
            sample_name=self.sample.name,
            lambda_exc_nm=float(lambda_exc_nm),
            wavelengths_nm=wavelengths,
            excitation_power=excitation_power,
            emitted_power=emitted_power,
            scatter_power=scatter_power,
            emitted_photocurrent=emitted_photocurrent,
            scatter_photocurrent=scatter_photocurrent,
            photocurrent=photocurrent,
            scatter_fraction=self.scatter_fraction,
        )
