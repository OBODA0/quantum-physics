"""Atomic scattering factors and the Debye-Waller term.

`f0` is interpolated from data/scattering_factors.json, sampled once from the
Waasmaier-Kirfel analytic form factors (Acta Cryst. A51, 416-431, 1995).
`s = sin(theta) / lambda` in 1/angstrom.
"""

from __future__ import annotations

import json
import math
import pathlib

DATA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "data" / "scattering_factors.json"
)

_table: dict | None = None


def _load() -> dict:
    global _table
    if _table is None:
        payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        _table = {
            "s_max": payload["grid_s_inv_A"][-1],
            "step": payload["grid_s_inv_A"][1] - payload["grid_s_inv_A"][0],
            "elements": payload["f0"],
        }
    return _table


def f0(element: str, s: float) -> float:
    """Elastic form factor f0 in electrons. `s = sin(theta)/lambda` in 1/angstrom."""
    table = _load()
    values = table["elements"].get(element)
    if values is None:
        raise KeyError(
            f"no scattering factor for {element!r}; rebuild data/scattering_factors.json"
        )
    if s < 0:
        raise ValueError("s must be non-negative")
    position = s / table["step"]
    last = len(values) - 1
    if position >= last:
        return float(values[last])
    i = int(position)
    frac = position - i
    return float(values[i] * (1.0 - frac) + values[i + 1] * frac)


def debye_waller(b_iso: float, s: float) -> float:
    """Temperature factor exp(-B s^2), with B = 8 pi^2 <u^2> in square angstrom."""
    if b_iso < 0:
        raise ValueError("B must be non-negative")
    return math.exp(-b_iso * s * s)
