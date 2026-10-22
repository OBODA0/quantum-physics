import math

import pytest

from xrdsim.lattice import (d_from_two_theta, d_spacing, peak_positions,
                            refine_cubic_a, two_theta)

LAM = 1.540598
A_SI = 5.4311946  # NIST SRM 640d, 22.5 C


def test_silicon_d_spacings_match_the_literature():
    assert d_spacing(1, 1, 1, a=A_SI) == pytest.approx(3.1357, abs=1e-4)
    assert d_spacing(4, 2, 2, a=A_SI) == pytest.approx(1.10864, abs=1e-4)


@pytest.mark.parametrize("hkl,expected", [
    # NIST SRM 640d certificate, Cu K-alpha1; the 0.01 deg window absorbs the
    # wavelength convention (certificate 1.5405929 A, here 1.540598 A)
    ((1, 1, 1), 28.4425),
    ((2, 2, 0), 47.3034),
    ((3, 1, 1), 56.1211),
    ((4, 0, 0), 69.1295),
    ((3, 3, 1), 76.3771),
    ((4, 2, 2), 88.0324),
])
def test_silicon_peak_positions(hkl, expected):
    d = d_spacing(*hkl, a=A_SI)
    assert two_theta(d, LAM) == pytest.approx(expected, abs=1e-2)


def test_hexagonal_zinc_oxide():
    cell = dict(a=3.2498, c=5.2066, hexagonal=True)
    assert d_spacing(1, 0, 1, **cell) == pytest.approx(2.4758, abs=5e-5)
    assert two_theta(d_spacing(1, 0, 1, **cell), LAM) == pytest.approx(36.254, abs=2e-3)
    assert two_theta(d_spacing(0, 0, 2, **cell), LAM) == pytest.approx(34.422, abs=2e-3)


def test_unreachable_reflection_raises():
    with pytest.raises(ValueError):
        two_theta(0.5, LAM)


def test_bragg_round_trip():
    for angle in (20.0, 45.0, 120.0):
        assert two_theta(d_from_two_theta(angle, LAM), LAM) == pytest.approx(angle)


def test_refine_cubic_recovers_the_cell():
    peaks = []
    for hkl in [(1, 1, 1), (2, 2, 0), (3, 1, 1), (4, 0, 0), (3, 3, 1)]:
        peaks.append((two_theta(d_spacing(*hkl, a=A_SI), LAM), *hkl))
    assert refine_cubic_a(peaks, LAM) == pytest.approx(A_SI, abs=1e-6)


def test_peak_positions_are_sorted_and_reachable():
    rows = peak_positions([(1, 1, 1), (2, 2, 0), (4, 0, 0)], LAM, a=A_SI)
    angles = [r[2] for r in rows]
    assert angles == sorted(angles)
    assert all(0 < angle < 180 for angle in angles)


def _d_from_metric(a, b, c, alpha, beta, gamma, hkl):
    """d-spacing from the metric tensor, an independent path to the same number."""
    import numpy as np
    al, be, ga = np.radians([alpha, beta, gamma])
    va = np.array([a, 0.0, 0.0])
    vb = np.array([b * np.cos(ga), b * np.sin(ga), 0.0])
    cx = c * np.cos(be)
    cy = c * (np.cos(al) - np.cos(be) * np.cos(ga)) / np.sin(ga)
    cz = np.sqrt(max(c * c - cx * cx - cy * cy, 0.0))
    vc = np.array([cx, cy, cz])
    metric = np.array([va, vb, vc]) @ np.array([va, vb, vc]).T
    vector = np.array(hkl, dtype=float)
    return float(1.0 / np.sqrt(vector @ np.linalg.inv(metric) @ vector))


@pytest.mark.parametrize("cell,hkl", [
    (dict(a=5.431144), (1, 3, 2)),
    (dict(a=4.0495, c=4.0495), (2, 1, 3)),
    (dict(a=3.2494, c=5.2038, hexagonal=True), (1, 0, 2)),
    (dict(a=3.2494, c=5.2038, hexagonal=True), (2, 2, 1)),
    (dict(a=5.0, b=6.0, c=7.0), (1, 2, 3)),
])
def test_d_spacing_agrees_with_the_metric_tensor(cell, hkl):
    kwargs = dict(cell)
    if kwargs.pop("hexagonal", False):
        alpha, beta, gamma = 90.0, 90.0, 120.0
        b = kwargs["a"]
    else:
        b = kwargs.get("b", kwargs["a"])
        c = kwargs.get("c", b)
        alpha = beta = gamma = 90.0
    c = kwargs.get("c", b)
    expected = _d_from_metric(kwargs["a"], b, c, alpha, beta, gamma, hkl)
    assert d_spacing(*hkl, **cell) == pytest.approx(expected, rel=1e-12)
