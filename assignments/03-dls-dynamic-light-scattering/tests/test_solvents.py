"""Solvent properties against measured tables."""

import numpy as np
import pytest

from dlssim.solvents import SOLVENTS


def test_water_viscosity_matches_table():
    water = SOLVENTS["water"]
    assert water.viscosity(20.0) == pytest.approx(1.0016e-3, rel=1e-6)
    assert water.viscosity(25.0) == pytest.approx(0.8900e-3, rel=1e-6)


def test_ethanol_more_viscous_than_water_at_20c():
    assert SOLVENTS["ethanol"].viscosity(20.0) == pytest.approx(1.200e-3, rel=1e-6)
    assert SOLVENTS["ethanol"].viscosity(20.0) > SOLVENTS["water"].viscosity(20.0)


def test_viscosity_falls_with_temperature():
    water = SOLVENTS["water"]
    values = [water.viscosity(t) for t in (10.0, 20.0, 30.0, 40.0)]
    assert all(a > b for a, b in zip(values, values[1:]))


def test_viscosity_outside_table_is_refused():
    with pytest.raises(ValueError):
        SOLVENTS["water"].viscosity(95.0)


def test_water_refractive_index_at_633_nm():
    n = SOLVENTS["water"].refractive_index(633e-9, 20.0)
    assert n == pytest.approx(1.3317, abs=5e-4)
    assert SOLVENTS["ethanol"].refractive_index(633e-9, 20.0) == pytest.approx(1.3594, abs=5e-4)


def test_refractive_index_falls_with_temperature():
    water = SOLVENTS["water"]
    assert water.refractive_index(633e-9, 30.0) < water.refractive_index(633e-9, 20.0)
