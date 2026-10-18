"""Photoluminescence spectrometer simulator.

Chain: xenon lamp -> excitation monochromator -> harmonic filter -> sample ->
detection monochromator -> silicon photodiode.
"""

from .analysis import ExcitationScan, excitation_scan, measured_emission_band
from .bands import FWHM_TO_SIGMA, GaussianBand, gaussian
from .detector import Photodetector
from .samples import SAMPLE_DATABASE, Dye, get_sample, with_concentration
from .sources import ExcitationArm, HarmonicFilter, Monochromator, XenonLamp
from .spectrometer import PLScan, PLSpectrometer

__all__ = [
    "Dye",
    "ExcitationArm",
    "ExcitationScan",
    "FWHM_TO_SIGMA",
    "GaussianBand",
    "HarmonicFilter",
    "Monochromator",
    "PLScan",
    "PLSpectrometer",
    "Photodetector",
    "SAMPLE_DATABASE",
    "XenonLamp",
    "excitation_scan",
    "gaussian",
    "get_sample",
    "measured_emission_band",
    "with_concentration",
]
