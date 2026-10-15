"""Sample database: organic dyes.

Band centres and quantum yields are typical literature values for the free dye
in the given solvent, rounded. The band shapes are Gaussian approximations of
the real, slightly asymmetric bands.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .bands import GaussianBand


@dataclass(frozen=True)
class Dye:
    """A fluorescent sample: one absorption band and one emission band."""

    name: str
    absorption: GaussianBand
    emission: GaussianBand
    quantum_yield: float
    peak_absorbance: float = 1.0
    solvent: str = "water"
    note: str = ""

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

        Emission below the excitation wavelength is zero (Stokes shift): the
        sample cannot emit photons it was not given.
        """
        stokes = np.where(np.asarray(wavelength_nm, dtype=float) >= lambda_exc_nm, 1.0, 0.0)
        return (
            excitation_power
            * self.absorbed_fraction(lambda_exc_nm)
            * self.quantum_yield
            * self.emission_shape(wavelength_nm)
            * stokes
        )


SAMPLE_DATABASE = {
    "cy3": Dye(
        name="Cy3",
        absorption=GaussianBand(center_nm=550.0, fwhm_nm=40.0),
        emission=GaussianBand(center_nm=570.0, fwhm_nm=32.0),
        quantum_yield=0.04,
        solvent="PBS",
        note="Cyanine dye: absorption maximum 550 nm, emission maximum 570 nm, quantum yield ~0.04.",
    ),
    "cy5": Dye(
        name="Cy5",
        absorption=GaussianBand(center_nm=649.0, fwhm_nm=40.0),
        emission=GaussianBand(center_nm=670.0, fwhm_nm=32.0),
        quantum_yield=0.28,
        solvent="PBS",
        note="Cyanine dye: absorption maximum 649 nm, emission maximum 670 nm, quantum yield ~0.2-0.3.",
    ),
    "methylene-blue": Dye(
        name="Methylene blue",
        absorption=GaussianBand(center_nm=664.0, fwhm_nm=55.0),
        emission=GaussianBand(center_nm=686.0, fwhm_nm=45.0),
        quantum_yield=0.04,
        solvent="water",
        note="Thiazine dye: absorption maximum 664 nm, emission maximum 686 nm, quantum yield ~0.04.",
    ),
}


def get_sample(name):
    """Look a dye up by name, ignoring case, spaces and dashes."""
    key = name.strip().lower().replace("_", "-").replace(" ", "-")
    if key == "mb":
        key = "methylene-blue"
    try:
        return SAMPLE_DATABASE[key]
    except KeyError:
        raise KeyError(
            "unknown sample {!r}; available: {}".format(name, ", ".join(SAMPLE_DATABASE))
        ) from None
