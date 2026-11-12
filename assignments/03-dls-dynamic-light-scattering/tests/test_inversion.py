"""Regularised inversion and the number/intensity conversion."""

import numpy as np
import pytest

from dlssim.inversion import diameter_grid, invert
from dlssim.model import DLSModel


def _invert(model, tau, g2, **kwargs):
    g1 = np.sqrt(np.clip((g2 - 1.0) / model.beta, 0.0, None))
    return model.invert(tau, g2, **kwargs)


def test_noise_free_recovery_of_a_single_size():
    model = DLSModel()
    tau = model.lags()
    result = model.invert(tau, model.g2(tau))
    assert result.peak_intensity_m == pytest.approx(100e-9, rel=0.05)
    assert result.residual < 0.01


def test_number_peak_is_not_above_intensity_peak():
    model = DLSModel(geometric_sd=1.2)
    tau, g2 = model.measure(seed=2)
    result = model.invert(tau, g2)
    assert result.peak_number_m <= result.peak_intensity_m * 1.01


def test_number_distribution_is_zero_outside_support():
    model = DLSModel()
    tau, g2 = model.measure(seed=2)
    result = model.invert(tau, g2)
    outside = (result.diameters_m < result.support_m[0]) | (result.diameters_m > result.support_m[1])
    assert np.all(result.number_weights[outside] == 0.0)


def test_bimodal_mixture_produces_two_intensity_modes():
    model = DLSModel(aggregation_fraction=0.5, aggregation_number=10)
    tau = model.lags()
    result = model.invert(tau, model.g2(tau))
    weights = result.intensity_weights
    peaks = [
        i for i in range(1, len(weights) - 1)
        if weights[i] > weights[i - 1] and weights[i] > weights[i + 1] and weights[i] > 0.05 * weights.max()
    ]
    assert len(peaks) >= 2


def test_grid_is_log_spaced_and_validated():
    grid = diameter_grid(1e-9, 1e-6, 10)
    assert np.allclose(np.diff(np.log(grid)), np.diff(np.log(grid))[0])
    with pytest.raises(ValueError):
        diameter_grid(1e-6, 1e-9, 10)
