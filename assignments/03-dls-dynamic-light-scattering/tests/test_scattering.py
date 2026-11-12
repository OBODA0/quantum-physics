"""Scattering weights and form factors."""

import numpy as np
import pytest

from dlssim.materials import MATERIALS
from dlssim.scattering import (
    contrast_factor,
    debye_structure_factor,
    particle_mass,
    sphere_form_factor,
)


def test_contrast_vanishes_when_indices_match():
    assert contrast_factor(1.33, 1.33) == pytest.approx(0.0, abs=1e-15)


def test_contrast_is_positive_for_denser_particles():
    assert contrast_factor(1.59, 1.33) > 0
    assert contrast_factor(1.45, 1.33) < contrast_factor(1.59, 1.33)


def test_sphere_mass():
    mass = particle_mass(100e-9, MATERIALS["polystyrene"].density_kg_m3)
    assert mass == pytest.approx(1050.0 * np.pi * (100e-9) ** 3 / 6.0, rel=1e-12)


def test_form_factor_tends_to_one_at_small_q():
    assert sphere_form_factor(1.0, 100e-9)[0] == pytest.approx(1.0, abs=1e-6)


def test_form_factor_falls_with_size_at_fixed_q():
    q = 2.64e7
    assert sphere_form_factor(q, 500e-9)[0] < sphere_form_factor(q, 100e-9)[0] < 1.0


def test_debye_structure_factor_limits():
    assert debye_structure_factor(1.0, 1e-9)[0] == pytest.approx(1.0, abs=1e-6)
    assert debye_structure_factor(2.64e7, 300e-9)[0] < 0.1


def test_rayleigh_weight_scales_with_sixth_power():
    q_small = 1.0
    a = (particle_mass(100e-9, 1050.0) ** 2) * sphere_form_factor(q_small, 100e-9)[0]
    b = (particle_mass(200e-9, 1050.0) ** 2) * sphere_form_factor(q_small, 200e-9)[0]
    assert float(b / a) == pytest.approx(64.0, rel=1e-3)
