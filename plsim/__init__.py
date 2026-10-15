"""Photoluminescence spectrometer simulator.

Chain: xenon lamp -> excitation monochromator -> harmonic filter -> sample ->
detection monochromator -> silicon photodiode.
"""

from .bands import FWHM_TO_SIGMA, GaussianBand, gaussian
from .detector import Photodetector
from .samples import SAMPLE_DATABASE, Dye, get_sample
from .sources import ExcitationArm, HarmonicFilter, Monochromator, XenonLamp
from .spectrometer import PLScan, PLSpectrometer

__all__ = [
    "Dye",
    "ExcitationArm",
    "FWHM_TO_SIGMA",
    "GaussianBand",
    "HarmonicFilter",
    "Monochromator",
    "PLScan",
    "PLSpectrometer",
    "Photodetector",
    "SAMPLE_DATABASE",
    "XenonLamp",
    "gaussian",
    "get_sample",
]
