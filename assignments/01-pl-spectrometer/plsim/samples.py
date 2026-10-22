"""Sample database: the dyes of the class task, as a Gaussian model.

Band centres and quantum yields are the sourced values from the data-sources appendix of
the report, where each number carries its solvent and its spread. The band shapes are
Gaussian approximations; `plsim/reference.py` loads the measured band shapes
for the same three dyes.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

import numpy as np

from .bands import GaussianBand


@dataclass(frozen=True)
class Dye:
    """A fluorescent sample: one absorption band and one emission band."""

    name: str
    absorption: object
    emission: object
    quantum_yield: float
    peak_absorbance: float = 1.0
    solvent: str = "water"
    extinction_coefficient: float | None = None
    note: str = ""
    source: str = ""

    def absorbance(self, wavelength_nm):
        """Absorbance (optical density) of the sample at that wavelength."""
        return self.peak_absorbance * self.absorption(wavelength_nm)

    def absorbed_fraction(self, lambda_exc_nm):
        """Fraction of the excitation light the sample absorbs (A at the peak)."""
        return float(1.0 - 10.0 ** (-self.absorbance(lambda_exc_nm)))

    def emission_shape(self, wavelength_nm):
        """Emission band shape, 1 at its maximum."""
        return self.emission(wavelength_nm)

    def emitted_power(self, wavelength_nm, lambda_exc_nm, excitation_power):
        """PL power emitted per wavelength, in relative units.

        The emission band shape does not depend on the excitation wavelength.
        A molecule that has absorbed a photon relaxes to the bottom of S1 before
        it emits, so every excitation wavelength produces the same spectrum and
        only the amount of absorbed light changes with it (Kasha's rule, which
        is the subject of the assignment's second question).

        Two deliberate omissions, both documented here because they are the
        difference between a simulator that shows Kasha's rule and one that
        quietly breaks it:

        - No cut of the emission at lambda_exc. An earlier version multiplied the
          band by a step at lambda_exc, which truncated the band whenever the
          excitation fell inside it and made the simulated spectrum move with
          the excitation wavelength.
        - No anti-Stokes term. Anti-Stokes emission (emitted photon more energetic
          than the absorbed one) is weak, and adding a Boltzmann factor on top of
          a measured band double-counts the vibronic envelope that is already in
          the measured band shape.
        """
        return (
            excitation_power
            * self.absorbed_fraction(lambda_exc_nm)
            * self.quantum_yield
            * self.emission_shape(wavelength_nm)
        )


SAMPLE_DATABASE = {
    "cy3": Dye(
        name="Cy3",
        absorption=GaussianBand(center_nm=550.0, fwhm_nm=45.0),
        emission=GaussianBand(center_nm=570.0, fwhm_nm=28.6),
        quantum_yield=0.04,
        solvent="PBS, pH 7.4 (free dye)",
        extinction_coefficient=150000.0,
        note=(
            "Absorption 550 nm / emission 570 nm (vendor values; the literature spreads 544-555 nm and "
            "563-570 nm). Quantum yield 0.04 holds for the free dye in PBS; conjugates and sulfo-Cy3 are "
            "reported at 0.10-0.31, so quote it together with the solvent."
        ),
        source="the data-sources appendix of the report",
    ),
    "cy5": Dye(
        name="Cy5",
        absorption=GaussianBand(center_nm=649.0, fwhm_nm=37.7),
        emission=GaussianBand(center_nm=670.0, fwhm_nm=33.5),
        quantum_yield=0.28,
        solvent="water / PBS (free dye)",
        extinction_coefficient=250000.0,
        note=(
            "Absorption 649 nm / emission 670 nm. Quantum yield 0.28 is the value cited for Cy5 in aqueous "
            "solution; individual measurements span 0.19-0.30, and 0.4 in methanol is disputed by an "
            "integrating-sphere measurement of 0.17."
        ),
        source="the data-sources appendix of the report",
    ),
    "methylene-blue": Dye(
        name="Methylene blue",
        absorption=GaussianBand(center_nm=664.0, fwhm_nm=55.9),
        emission=GaussianBand(center_nm=685.0, fwhm_nm=48.7),
        quantum_yield=0.02,
        solvent="water",
        extinction_coefficient=67000.0,
        note=(
            "Absorption 664 nm / emission 685 nm. Quantum yield 0.02 in water, which is the value used when "
            "methylene blue serves as a reference in photodynamic therapy; the classic ethanol value is 0.04. "
            "The molar extinction coefficient depends on how the dimer is treated: 67,000-74,000 in dilute "
            "water as measured, 107,800 for the deconvoluted monomer."
        ),
        source="the data-sources appendix of the report",
    ),
}


def with_concentration(dye, concentration_M, path_length_cm=1.0):
    """The same dye at a given concentration, with the absorbance that follows.

    A_peak = epsilon * c * l, so the same concentration of two dyes does NOT mean
    the same peak absorbance unless their extinction coefficients match. Pass the
    result to the spectrometer when the experiment is "equal concentrations".
    """
    if dye.extinction_coefficient is None:
        raise ValueError("{} has no extinction coefficient, so no concentration can be applied".format(dye.name))
    return dataclasses.replace(
        dye, peak_absorbance=dye.extinction_coefficient * concentration_M * path_length_cm
    )


def normalise_key(name):
    """Dye names are matched ignoring case, spaces and dashes."""
    key = name.strip().lower().replace("_", "-").replace(" ", "-")
    return "methylene-blue" if key == "mb" else key


def get_sample(name, database=None):
    """Look a dye up by name in the given database (the Gaussian model by default)."""
    database = SAMPLE_DATABASE if database is None else database
    key = normalise_key(name)
    try:
        return database[key]
    except KeyError:
        raise KeyError(
            "unknown sample {!r}; available: {}".format(name, ", ".join(database))
        ) from None
