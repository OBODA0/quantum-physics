import math

import pytest

from xrdsim.geometry import (bragg_angle, flat_plate_absorption, footprint_length,
                             linear_attenuation, penetration_depth)
from xrdsim.sources import (CU_KA1, CU_KA2, CU_KB, KA2_TO_KA1, emission_lines,
                            weighted_wavelength)


def test_bragg_angle_is_half_of_two_theta():
    assert bragg_angle(60.0) == 30.0


def test_footprint_grows_as_the_sample_turns():
    slit = 1.0
    low = footprint_length(20.0, slit)
    high = footprint_length(80.0, slit)
    assert low > high
    assert footprint_length(90.0, slit) == pytest.approx(1.0 / math.sin(math.radians(45.0)))


def test_footprint_is_clipped_by_the_holder():
    assert footprint_length(10.0, 1.0, sample_length_mm=5.0) == 5.0


def test_attenuation_and_absorption():
    mu = linear_attenuation(2.33, 63.0)
    assert mu == pytest.approx(146.79)
    assert flat_plate_absorption(mu) == pytest.approx(1.0 / (2.0 * mu))


def test_penetration_depth_grows_with_angle():
    mu = 100.0
    assert penetration_depth(mu, 20.0) < penetration_depth(mu, 80.0)
    expected = -math.log(0.01) * math.sin(math.radians(45.0)) / 200.0
    assert penetration_depth(100.0, 90.0) == pytest.approx(expected)


def test_cu_lines():
    lines = emission_lines(ka2=True, kbeta=False)
    assert [line.wavelength for line in lines] == [CU_KA1, CU_KA2]
    assert lines[1].weight == pytest.approx(KA2_TO_KA1)
    assert len(emission_lines(ka2=False)) == 1
    assert emission_lines(kbeta=True)[-1].wavelength == CU_KB


def test_weighted_wavelength_lies_between_the_lines():
    mean = weighted_wavelength(emission_lines())
    assert CU_KA1 < mean < CU_KA2
