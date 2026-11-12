"""Physical constants and instrument defaults (SI units unless stated)."""

from __future__ import annotations

#: Boltzmann constant, J/K. Exact under the 2019 SI definition.
K_B = 1.380649e-23

#: He-Ne laser wavelength, m.
DEFAULT_WAVELENGTH_M = 633e-9

#: Detection angle from the class debrief (notebook page W7 L2 12/10). Backscatter
#: instruments commonly use 173 deg; keep this configurable.
DEFAULT_ANGLE_DEG = 178.0

#: Reference temperature, deg C.
DEFAULT_TEMPERATURE_C = 25.0

#: Stokes-Einstein denominator for a solid sphere: 3 pi eta d.
STOKES_DENOMINATOR = 3.0
