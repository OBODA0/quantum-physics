"""End-to-end model behaviour across the five inputs."""

import numpy as np
import pytest

from dlssim.detector import DetectorConfig
from dlssim.model import DLSModel


def test_q_and_diffusion_consistency():
    model = DLSModel()
    assert model.q == pytest.approx(2.64e7, rel=0.01)
    assert model.diffusion() == pytest.approx(4.9e-12, rel=0.01)
    assert model.correlation_time == pytest.approx(1.0 / (model.diffusion() * model.q**2), rel=1e-9)


def test_measured_fit_recovers_size():
    model = DLSModel(diameter_m=250e-9)
    tau, g2 = model.measure(seed=4)
    fit = model.fit(tau, g2)
    assert float(fit.z_average_diameter_m) == pytest.approx(250e-9, rel=0.02)


def test_temperature_changes_diffusion_through_viscosity():
    cold = DLSModel(temperature_c=10.0)
    warm = DLSModel(temperature_c=40.0)
    assert warm.viscosity < cold.viscosity
    assert warm.diffusion() > cold.diffusion()
    assert warm.correlation_time < cold.correlation_time


def test_solvent_changes_correlation_time():
    water = DLSModel(solvent_name="water")
    ethanol = DLSModel(solvent_name="ethanol")
    assert ethanol.correlation_time > water.correlation_time


def test_aggregation_increases_size_and_pdi():
    values = [DLSModel(aggregation_fraction=f).true_z_average_m for f in (0.0, 0.2, 0.5)]
    pdis = [DLSModel(aggregation_fraction=f).true_cumulants[2] for f in (0.0, 0.2, 0.5)]
    assert all(b > a for a, b in zip(values, values[1:]))
    assert all(b > a for a, b in zip(pdis, pdis[1:]))


def test_aggregates_dominate_intensity_but_not_number():
    model = DLSModel(aggregation_fraction=0.5, aggregation_number=20)
    population = model.population
    weights = population.intensity_weights()
    big = population.diameters_m > 200e-9
    small = population.diameters_m < 150e-9
    assert weights[big].sum() > 0.5
    assert population.number_weights[small].sum() > 0.4


def test_count_rate_scales_with_concentration_and_size():
    model = DLSModel()
    assert model.count_rate_cps(1e8) == pytest.approx(1e5, rel=0.02)
    assert model.count_rate_cps(2e8) == pytest.approx(2e5, rel=0.02)
    assert DLSModel(diameter_m=200e-9).count_rate_cps(1e8) > 10 * model.count_rate_cps(1e8)


def test_photon_trace_has_expected_mean():
    model = DLSModel()
    config = DetectorConfig(duration_s=0.02, sample_interval_s=1e-6, count_rate_cps=1e5, beta=0.5)
    trace = model.photon_trace(config, seed=1)
    interval = max(config.sample_interval_s, model.correlation_time / 10.0)
    assert trace.mean() == pytest.approx(config.count_rate_cps * interval, rel=0.2)
    assert trace.min() >= 0


def test_invalid_inputs_are_refused():
    with pytest.raises(ValueError):
        DLSModel(solvent_name="acetone")
    with pytest.raises(ValueError):
        DLSModel(material_name="unobtainium")
    with pytest.raises(ValueError):
        DLSModel(geometric_sd=0.9)
