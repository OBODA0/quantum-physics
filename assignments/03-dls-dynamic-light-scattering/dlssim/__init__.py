"""Dynamic light scattering simulator.

Physics: Brownian motion of suspended particles sets a diffusion coefficient
(Stokes-Einstein); light scattered at angle theta interferes with a delay-dependent
phase, so the measured intensity autocorrelation decays with rate Gamma = D q^2.
The decay-rate spectrum of a polydisperse sample is recovered from the correlation
curve by cumulant analysis and by regularised inversion.
"""

from .constants import K_B, DEFAULT_ANGLE_DEG, DEFAULT_WAVELENGTH_M
from .materials import MATERIALS, Material
from .solvents import SOLVENTS, Solvent
from .sizes import SizeDistribution
from .brownian import diffusion_coefficient, scattering_vector, decay_rate, correlation_time
from .correlation import field_correlation, intensity_correlation, cumulant_fit, CumulantResult
from .model import DLSModel

__all__ = [
    "K_B", "DEFAULT_ANGLE_DEG", "DEFAULT_WAVELENGTH_M",
    "MATERIALS", "Material", "SOLVENTS", "Solvent", "SizeDistribution",
    "diffusion_coefficient", "scattering_vector", "decay_rate", "correlation_time",
    "field_correlation", "intensity_correlation", "cumulant_fit", "CumulantResult",
    "DLSModel",
]
__version__ = "0.1.0"
