import math

import numpy as np
import pytest

from xrdsim.detector import (apply_dead_time, count_noise, expected_counts,
                             observe)
from xrdsim.profile import (add_in_quadrature, caglioti_fwhm, gaussian,
                            lorentzian, pseudo_voigt, scherrer_size, size_fwhm)


def _integral(fn, center, fwhm, n=50001, half_span=500.0):
    xs = np.linspace(center - half_span * fwhm, center + half_span * fwhm, n)
    return np.trapezoid([fn(x) for x in xs], xs)


def test_profiles_have_unit_area():
    for fn in (gaussian, lorentzian):
        assert _integral(lambda x: fn(x, 30.0, 0.2), 30.0, 0.2) == pytest.approx(1.0, abs=2e-3)
    for eta in (0.0, 0.3, 1.0):
        assert _integral(lambda x: pseudo_voigt(x, 30.0, 0.2, eta), 30.0, 0.2) == pytest.approx(1.0, abs=2e-3)


def test_fwhm_is_the_declared_width():
    for fn in (gaussian, lorentzian):
        half = fn(30.0, 30.0, 0.3) / 2.0
        xs = np.linspace(29.0, 31.0, 200001)
        above = xs[[fn(x, 30.0, 0.3) >= half for x in xs]]
        assert above[-1] - above[0] == pytest.approx(0.3, abs=2e-4)


def test_caglioti_matches_the_polynomial():
    U, V, W = 0.004, -0.002, 0.003
    t = math.tan(math.radians(30.0))
    assert caglioti_fwhm(60.0, U, V, W) == pytest.approx(math.sqrt(U * t * t + V * t + W))


def test_caglioti_never_returns_a_negative_width():
    assert caglioti_fwhm(10.0, -1.0, 0.0, 0.0) == 0.0


def test_scherrer_and_its_inverse_agree():
    size = 500.0
    fwhm = size_fwhm(size, 40.0, 1.540598)
    assert scherrer_size(fwhm, 40.0, 1.540598) == pytest.approx(size, rel=1e-12)


def test_quadrature_combination():
    assert add_in_quadrature(3.0, 4.0) == pytest.approx(5.0)


def test_poisson_mean_and_spread():
    rng = np.random.default_rng(7)
    draws = np.array([observe(25.0, rng) for _ in range(20000)])
    assert draws.mean() == pytest.approx(25.0, rel=0.02)
    assert draws.std() == pytest.approx(5.0, rel=0.03)
    assert count_noise(25.0) == pytest.approx(5.0)


def test_dead_time_reduces_the_rate():
    assert apply_dead_time(1e5, 1e-6) == pytest.approx(1e5 / 1.1)
    assert apply_dead_time(0.0, 1e-6) == 0.0


def test_expected_counts_scales_with_dwell():
    assert expected_counts(100.0, 2.0) == 200.0
    with pytest.raises(ValueError):
        expected_counts(100.0, 0.0)
