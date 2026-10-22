import math

import numpy as np
import pytest

from xrdsim.diffractometer import Instrument, reflections, scan
from xrdsim.samples import get_phase

SI = get_phase("si")


def _quiet(**kwargs):
    return Instrument(reference_counts=50_000.0, background_rate=0.0, rng_seed=None, **kwargs)


def test_silicon_scan_peaks_land_on_the_certified_angles():
    s = scan(SI, 20.0, 90.0, 0.02, _quiet())
    peaks = []
    for i in range(1, len(s.counts) - 1):
        if s.counts[i] > s.counts[i - 1] and s.counts[i] >= s.counts[i + 1] \
                and s.counts[i] > 0.02 * s.counts.max():
            peaks.append(s.two_theta[i])
    for expected in (28.44, 47.30, 56.12):
        assert min(abs(p - expected) for p in peaks) < 0.05


def test_diamond_222_is_absent():
    rows = {row.hkl: row for row in reflections(SI, _quiet())}
    assert rows[(2, 2, 2)].intensity == pytest.approx(0.0, abs=1e-9)
    assert rows[(1, 1, 1)].intensity > 0


def test_doublet_toggle_changes_the_peak_width():
    wide = scan(SI, 27.5, 29.5, 0.005, _quiet(ka2=True))
    narrow = scan(SI, 27.5, 29.5, 0.005, _quiet(ka2=False))
    def fwhm(s):
        half = s.counts.max() / 2.0
        above = s.two_theta[s.counts >= half]
        return above[-1] - above[0]
    assert fwhm(wide) > fwhm(narrow)


def test_crystallite_size_broadens_the_peaks():
    big = scan(SI, 27.5, 29.5, 0.005, _quiet(), size_a=500.0)
    small = scan(SI, 27.5, 29.5, 0.005, _quiet(), size_a=20.0)
    def fwhm(s):
        half = s.counts.max() / 2.0
        above = s.two_theta[s.counts >= half]
        return above[-1] - above[0]
    assert fwhm(small) > 3.0 * fwhm(big)


def test_poisson_noise_is_reproducible_and_proportional():
    a = scan(SI, 27.0, 30.0, 0.01, Instrument(rng_seed=1))
    b = scan(SI, 27.0, 30.0, 0.01, Instrument(rng_seed=1))
    c = scan(SI, 27.0, 30.0, 0.01, Instrument(rng_seed=2))
    assert np.array_equal(a.counts, b.counts)
    assert not np.array_equal(a.counts, c.counts)
    window = np.abs(a.two_theta - 28.44) < 0.5
    assert a.counts[window].sum() == pytest.approx(20_000 * (1 + 0.497), rel=0.03)


def test_dead_time_compresses_strong_peaks():
    normal = scan(SI, 27.0, 30.0, 0.01, _quiet())
    dead = scan(SI, 27.0, 30.0, 0.01, _quiet(dead_time_s=1e-4))
    assert dead.counts.max() < normal.counts.max()


def test_bad_scan_range_is_rejected():
    with pytest.raises(ValueError):
        scan(SI, 60.0, 40.0, 0.02)


def test_only_one_member_of_each_family_is_listed():
    for row in reflections(SI, _quiet()):
        h, k, l = row.hkl
        assert h >= k >= l, row.hkl


def test_silicon_relative_intensities_match_the_standard_pattern():
    rows = {row.hkl: row for row in reflections(SI, _quiet())}
    top = rows[(1, 1, 1)].intensity
    assert rows[(1, 1, 1)].intensity == pytest.approx(top)
    assert rows[(2, 2, 0)].intensity / top == pytest.approx(0.64, abs=0.04)
    assert rows[(3, 1, 1)].intensity / top == pytest.approx(0.37, abs=0.04)
    assert rows[(4, 0, 0)].intensity / top == pytest.approx(0.10, abs=0.03)


def test_sample_displacement_shifts_low_angles_more():
    from xrdsim.diffractometer import displacement_shift
    low = displacement_shift(28.44, 0.1, 240.0)
    high = displacement_shift(120.0, 0.1, 240.0)
    assert low < 0 and high < 0
    assert abs(low) > abs(high)
    assert displacement_shift(28.44, 0.0, 240.0) == 0.0


def test_displacement_moves_the_measured_peak():
    from xrdsim.analysis import find_peaks
    normal = scan(SI, 27.5, 29.5, 0.005, Instrument(ka2=False, background_rate=0.0,
                                                    rng_seed=None))
    shifted = scan(SI, 27.5, 29.5, 0.005, Instrument(ka2=False, background_rate=0.0,
                                                     rng_seed=None,
                                                     sample_displacement_mm=0.2))
    peak_normal = find_peaks(normal.two_theta, normal.counts)[0]
    peak_shifted = find_peaks(shifted.two_theta, shifted.counts)[0]
    assert peak_shifted.two_theta < peak_normal.two_theta - 0.05
