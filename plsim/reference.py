"""Measured reference data: digitized absorption and emission bands.

The pack in `data/reference_spectra.json` was collected from vendor spec
sheets, spectral databases and peer-reviewed papers; `data/SOURCES.md` gives a
source and a confidence for every number.
"""

from __future__ import annotations

import json
from pathlib import Path

from .bands import TabulatedBand
from .samples import Dye

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "reference_spectra.json"
SOURCE = "data/reference_spectra.json (see data/SOURCES.md)"


def available(path=DEFAULT_PATH):
    """True when the reference pack is present."""
    return Path(path).exists()


def load_reference_database(path=DEFAULT_PATH):
    """Build the sample database from the measured reference pack."""
    records = json.loads(Path(path).read_text())
    database = {}
    for key, record in records.items():
        database[key] = Dye(
            name=record["display_name"].split("(")[0].strip(),
            absorption=_band(record, "digitized_absorption", key),
            emission=_band(record, "digitized_emission", key),
            quantum_yield=record["quantum_yield"],
            solvent=record["quantum_yield_solvent"],
            extinction_coefficient=record.get("extinction_coefficient_per_M_per_cm"),
            note=record["notes"],
            source=SOURCE,
        )
    return database


def _band(record, field, key):
    curve = record.get(field)
    if not curve or not curve.get("wavelength_nm"):
        raise ValueError("{} has no {}".format(key, field))
    return TabulatedBand.from_lists(curve["wavelength_nm"], curve["value"], name="{}/{}".format(key, field))
