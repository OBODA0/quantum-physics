"""Dispersion liquids: refractive index and dynamic viscosity.

Viscosity is interpolated with a monotone cubic through measured tables (PCHIP), so
the value between table points is smooth and never overshoots. Extrapolation outside
the measured range is refused rather than guessed.

Refractive index uses a two-term Cauchy form n(lambda) = A + B / lambda^2 fitted to
measured values at 20 deg C (residuals below 2e-4 for water, 3e-5 for ethanol), plus
a linear temperature correction dn/dT.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import PchipInterpolator

# Dynamic viscosity, mPa s, measured at 1 atm. Provenance in data/SOURCES.md.
_VISCOSITY_TABLES: dict[str, tuple[list[float], list[float]]] = {
    "water": (
        [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 60.0],
        [1.7914, 1.5188, 1.3059, 1.1375, 1.0016, 0.8900, 0.7972, 0.7191, 0.6527, 0.5468, 0.4660],
    ),
    "ethanol": (
        [0.0, 10.0, 20.0, 25.0, 30.0, 40.0, 50.0],
        [1.773, 1.466, 1.200, 1.074, 0.983, 0.834, 0.702],
    ),
}

# Cauchy coefficients at 20 deg C, wavelength in um.
_CAUCHY: dict[str, tuple[float, float]] = {
    "water": (1.323950, 0.003101),
    "ethanol": (1.348566, 0.004346),
}

# Temperature coefficient of the refractive index near 20 deg C, 1/K.
_DN_DT: dict[str, float] = {
    "water": -1.0e-4,
    "ethanol": -4.0e-4,
}


@dataclass(frozen=True)
class Solvent:
    """A dispersion liquid.

    Attributes:
        name: key in :data:`SOLVENTS`.
        description: short human-readable label.
    """

    name: str
    description: str

    def _table(self) -> tuple[np.ndarray, np.ndarray]:
        temperatures, viscosities = _VISCOSITY_TABLES[self.name]
        return np.asarray(temperatures, float), np.asarray(viscosities, float)

    @property
    def temperature_range_c(self) -> tuple[float, float]:
        temperatures, _ = self._table()
        return float(temperatures[0]), float(temperatures[-1])

    def viscosity(self, temperature_c: float) -> float:
        """Dynamic viscosity in Pa s at the given temperature.

        Raises:
            ValueError: temperature outside the measured table.
        """
        temperatures, viscosities = self._table()
        low, high = float(temperatures[0]), float(temperatures[-1])
        if not low <= temperature_c <= high:
            raise ValueError(
                f"{self.name}: temperature {temperature_c:.1f} C is outside the measured "
                f"viscosity range {low:.0f}-{high:.0f} C"
            )
        interpolator = PchipInterpolator(temperatures, viscosities, extrapolate=False)
        return float(interpolator(temperature_c)) * 1e-3

    def refractive_index(self, wavelength_m: float, temperature_c: float) -> float:
        """Refractive index at wavelength and temperature."""
        a, b = _CAUCHY[self.name]
        wavelength_um = wavelength_m * 1e6
        n_20 = a + b / wavelength_um**2
        return float(n_20 + _DN_DT[self.name] * (temperature_c - 20.0))


SOLVENTS: dict[str, Solvent] = {
    "water": Solvent("water", "deionised water"),
    "ethanol": Solvent("ethanol", "absolute ethanol"),
}
