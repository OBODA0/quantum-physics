"""Solvent database with temperature-dependent viscosity and refractive index.

Provides the solvents requested on the in-class specification (water, ethanol) plus
common laboratory dispersion media. Dynamic viscosity eta(T) is modelled with the
Vogel-Fulcher-Tammann (VFT) / Andrade relation anchored to standard 25 C values.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Solvent:
    """Thermophysical and optical model for a liquid dispersion medium."""

    key: str
    name: str
    formula: str
    ri_25c: float          # refractive index at 25 C (589/633 nm)
    dn_dt: float           # thermo-optic coefficient dn/dT (K^-1)
    eta_25c_mpas: float    # dynamic viscosity at 25 C (mPa.s = cP)
    vft_a: float           # Andrade / VFT prefactor (mPa.s)
    vft_b: float           # activation parameter B (K)
    vft_t0: float          # VFT reference temperature T0 (K)

    @property
    def label(self) -> str:
        """Human-readable label with chemical formula."""
        return f"{self.name} ({self.formula})"

    def viscosity_pas(self, temp_k: float) -> float:
        """Dynamic viscosity eta(T) in Pa.s (kg m^-1 s^-1)."""
        if temp_k <= self.vft_t0 + 5.0:
            raise ValueError(
                f"temperature {temp_k} K is below liquid range of {self.name}"
            )
        eta_mpas = self.vft_a * math.exp(self.vft_b / (temp_k - self.vft_t0))
        return eta_mpas * 1e-3

    def viscosity_pa_s(self, temp_k: float) -> float:
        """Alias for viscosity_pas(temp_k) in Pa.s."""
        return self.viscosity_pas(temp_k)

    def viscosity_mpas(self, temp_k: float) -> float:
        """Dynamic viscosity eta(T) in mPa.s (cP)."""
        return self.viscosity_pas(temp_k) * 1e3

    def viscosity_mpa_s(self, temp_k: float) -> float:
        """Alias for viscosity_mpas(temp_k) in mPa.s."""
        return self.viscosity_mpas(temp_k)

    def refractive_index(self, temp_k: float) -> float:
        """Temperature-corrected solvent refractive index n_s(T)."""
        return self.ri_25c + self.dn_dt * (temp_k - 298.15)


SolventModel = Solvent

SOLVENTS: dict[str, Solvent] = {
    "water": Solvent(
        key="water",
        name="Water",
        formula="H2O",
        ri_25c=1.3312,
        dn_dt=-1.0e-4,
        eta_25c_mpas=0.890,
        vft_a=0.02414,
        vft_b=570.58,
        vft_t0=140.0,
    ),
    "ethanol": Solvent(
        key="ethanol",
        name="Ethanol",
        formula="C2H5OH",
        ri_25c=1.3594,
        dn_dt=-4.0e-4,
        eta_25c_mpas=1.074,
        vft_a=0.00593,
        vft_b=1550.0,
        vft_t0=0.0,
    ),
    "pbs": Solvent(
        key="pbs",
        name="Phosphate-buffered saline",
        formula="PBS",
        ri_25c=1.3340,
        dn_dt=-1.0e-4,
        eta_25c_mpas=0.910,
        vft_a=0.02468,
        vft_b=570.58,
        vft_t0=140.0,
    ),
    "toluene": Solvent(
        key="toluene",
        name="Toluene",
        formula="C7H8",
        ri_25c=1.4941,
        dn_dt=-5.6e-4,
        eta_25c_mpas=0.554,
        vft_a=0.01564,
        vft_b=1063.0,
        vft_t0=0.0,
    ),
}


def list_solvents() -> list[str]:
    """Return the list of supported solvent keys."""
    return list(SOLVENTS.keys())


def get_solvent(key: str) -> Solvent:
    """Look up a solvent model by case-insensitive key."""
    norm = key.strip().lower()
    if norm not in SOLVENTS:
        choices = ", ".join(sorted(SOLVENTS))
        raise KeyError(f"unknown solvent {key!r}; choose from {choices}")
    return SOLVENTS[norm]
