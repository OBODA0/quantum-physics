"""Build data/scattering_factors.json from xraydb.

The table is sampled once, here, so the simulator itself needs only numpy. The values
are the Waasmaier-Kirfel analytic form factors (Acta Cryst. A51, 416-431, 1995), which
xraydb carries and which reproduce f(0) = Z.
"""

from __future__ import annotations

import json
import pathlib

import numpy as np
import xraydb

ELEMENTS = [
    "H", "B", "C", "N", "O", "F", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "K",
    "Ca", "Ti", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Sr", "Zr", "Ba", "La", "Pb",
]
S_MAX = 0.80          # 1/A; Cu K-alpha at 180 deg corresponds to 1/lambda = 0.649
STEP = 0.002


def main() -> None:
    grid = np.arange(0.0, S_MAX + STEP / 2, STEP)
    table = {}
    for element in ELEMENTS:
        f0 = np.ravel(xraydb.f0(element, grid))
        table[element] = [round(float(value), 5) for value in f0]
    payload = {
        "source": "Waasmaier & Kirfel, Acta Cryst. A51, 416-431 (1995); tabulated by xraydb 4.5.8",
        "doi": "10.1107/S0108767394013292",
        "grid_s_inv_A": [round(float(s), 5) for s in grid],
        "f0": table,
    }
    out = pathlib.Path(__file__).resolve().parent.parent / "data" / "scattering_factors.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} kB, {len(table)} elements)")


if __name__ == "__main__":
    main()
