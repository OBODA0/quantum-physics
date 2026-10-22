import math

import numpy as np
import pytest

from xrdsim.analysis import (find_peaks, index_cubic, pure_width, scherrer_from_peak)
from xrdsim.detector import expected_counts
from xrdsim.diffractometer import Instrument, scan
from xrdsim.profile import caglioti_fwhm, gaussian
from xrdsim.samples import get_phase

SI = get_phase("si")


def _two_gaussians():
    x = np.arange(20.0, 60.0, 0.01)
    y = (1000 * np.array([gaussian(v, 30.0, 0.2) for v in x])
         + 400 * np.array([gaussian(v, 45.0, 0.4) for v in x]))
    return x, y


def test_find_peaks_recovers_positions_widths_and_heights():
    x, y = _two_gaussians()
    peaks = find_peaks(x, y)
    assert len(peaks) == 2
    assert peaks[0].two_theta == pytest.approx(30.0, abs=0.02)
    assert peaks[0].fwhm == pytest.approx(0.2, abs=0.02)
    assert peaks[1].two_theta == pytest.approx(45.0, abs=0.02)
    assert peaks[1].fwhm == pytest.approx(0.4, abs=0.03)


def test_peak_area_is_the_integral():
    x, y = _two_gaussians()
    peaks = find_peaks(x, y)
    assert peaks[0].area == pytest.approx(1000.0, rel=0.05)
    assert peaks[1].area == pytest.approx(400.0, rel=0.05)


def test_pure_width_subtracts_in_quadrature_and_guards_negative():
    assert pure_width(0.5, 0.3) == pytest.approx(0.4)
    assert pure_width(0.2, 0.5) == 0.0


def test_index_cubic_on_silicon_angles():
    angles = [28.441, 47.300, 56.120, 69.126, 76.372, 88.025]
    rows = index_cubic(angles, 1.540598)
    assert [hkl for hkl, _ in rows] == [(1, 1, 1), (2, 2, 0), (3, 1, 1), (4, 0, 0), (3, 3, 1), (4, 2, 2)]


def test_scherrer_recovers_a_known_crystallite_size():
    instrument = Instrument(reference_counts=100_000.0, background_rate=0.0,
                            ka2=False, rng_seed=None)
    s = scan(SI, 27.5, 29.5, 0.002, instrument, size_a=200.0)
    peak = find_peaks(s.two_theta, s.counts)[0]
    instrumental = caglioti_fwhm(peak.two_theta, *instrument.caglioti)
    size = scherrer_from_peak(peak, instrumental, instrument.wavelength)
    assert size == pytest.approx(200.0, rel=0.15)
