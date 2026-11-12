"""Correlation functions and cumulant analysis."""

import numpy as np
import pytest

from dlssim.correlation import (
    analytic_cumulants,
    cumulant_fit,
    field_correlation,
    intensity_correlation,
)
from dlssim.model import DLSModel


def test_correlation_limits():
    gammas = np.array([1000.0])
    weights = np.array([1.0])
    assert field_correlation([0.0], gammas, weights)[0] == pytest.approx(1.0)
    assert intensity_correlation([0.0], gammas, weights, beta=0.7)[0] == pytest.approx(1.7)
    assert intensity_correlation([1.0], gammas, weights, beta=0.7)[0] == pytest.approx(1.0, abs=1e-9)


def test_beta_is_validated():
    with pytest.raises(ValueError):
        intensity_correlation([0.0], np.array([1.0]), np.array([1.0]), beta=0.0)


def test_analytic_cumulants_of_two_rate_mixture():
    gammas = np.array([1000.0, 2000.0])
    weights = np.array([0.5, 0.5])
    mean, mu2, pdi = analytic_cumulants(gammas, weights)
    assert mean == pytest.approx(1500.0)
    assert mu2 == pytest.approx(250000.0)
    assert pdi == pytest.approx(2.0 * 250000.0 / 1500.0**2)


def test_noise_free_cumulant_recovers_size_and_pdi():
    model = DLSModel(geometric_sd=1.1)
    tau = model.lags()
    g2 = model.g2(tau)
    fit = model.fit(tau, g2)
    assert float(fit.z_average_diameter_m) == pytest.approx(model.true_z_average_m, rel=0.01)
    assert fit.pdi == pytest.approx(model.true_cumulants[2], abs=0.01)


def test_pdi_grows_with_polydispersity():
    pd = [DLSModel(geometric_sd=s).true_cumulants[2] for s in (1.0, 1.1, 1.2, 1.3, 1.5)]
    assert all(b > a for a, b in zip(pd, pd[1:]))


def test_fit_rejects_flat_curve():
    model = DLSModel()
    tau = model.lags()
    with pytest.raises(ValueError):
        model.fit(tau, np.ones_like(tau))
