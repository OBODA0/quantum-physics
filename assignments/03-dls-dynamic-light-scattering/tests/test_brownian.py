"""Stokes-Einstein diffusion and the scattering vector."""

import numpy as np
import pytest

from dlssim.brownian import (
    correlation_time,
    decay_rate,
    diameter_from_decay_rate,
    diffusion_coefficient,
    scattering_vector,
)
from dlssim.solvents import SOLVENTS

WATER_25 = SOLVENTS["water"]


def test_diffusion_of_100_nm_polystyrene_in_water():
    d = diffusion_coefficient(100e-9, WATER_25.viscosity(25.0), 25.0)
    assert d == pytest.approx(4.9e-12, rel=0.01)


def test_diffusion_scales_inverse_with_diameter():
    eta = WATER_25.viscosity(25.0)
    assert diffusion_coefficient(200e-9, eta, 25.0) == pytest.approx(
        diffusion_coefficient(100e-9, eta, 25.0) / 2.0, rel=1e-12
    )


def test_scattering_vector_matches_formula():
    n = 1.3317
    q = scattering_vector(n, 633e-9, 178.0)
    expected = 4 * np.pi * n / 633e-9 * np.sin(np.deg2rad(178.0) / 2)
    assert q == pytest.approx(expected, rel=1e-12)
    assert q == pytest.approx(2.64e7, rel=0.01)


def test_angle_must_be_interior():
    with pytest.raises(ValueError):
        scattering_vector(1.33, 633e-9, 180.0)


def test_decay_rate_is_diffusion_times_q_squared():
    eta = WATER_25.viscosity(25.0)
    n = WATER_25.refractive_index(633e-9, 25.0)
    gamma = decay_rate(100e-9, eta, 25.0, n, 633e-9, 178.0)
    assert gamma == pytest.approx(diffusion_coefficient(100e-9, eta, 25.0) * scattering_vector(n, 633e-9, 178.0) ** 2)


def test_decay_rate_inverts_to_diameter():
    eta = WATER_25.viscosity(25.0)
    n = WATER_25.refractive_index(633e-9, 25.0)
    for diameter in (10e-9, 100e-9, 800e-9):
        gamma = decay_rate(diameter, eta, 25.0, n, 633e-9, 178.0)
        assert diameter_from_decay_rate(gamma, eta, 25.0, n, 633e-9, 178.0) == pytest.approx(
            diameter, rel=1e-12
        )


def test_correlation_time_is_inverse_decay_rate():
    assert correlation_time(2500.0) == pytest.approx(4e-4)
