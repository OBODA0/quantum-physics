"""Sanity checks: numbers the physics requires, not implementation details."""

import dataclasses

import numpy as np

from plsim.samples import SAMPLE_DATABASE, get_sample
from plsim.sources import Monochromator
from plsim.spectrometer import PLSpectrometer


def fwhm_nm(x, y):
    """Full width at half maximum of a simple peak."""
    above_half = x[y >= y.max() / 2.0]
    return float(above_half[-1] - above_half[0])


def test_detection_grid_follows_the_step_size():
    scan = PLSpectrometer(sample=get_sample("cy3")).acquire(
        lambda_exc_nm=520.0, lambda_min_nm=540.0, lambda_max_nm=640.0, dlambda_nm=0.5
    )
    assert scan.wavelengths_nm.size == 201
    assert np.allclose(np.diff(scan.wavelengths_nm), 0.5)


def test_each_dye_emits_at_its_emission_maximum():
    for key, dye in SAMPLE_DATABASE.items():
        scan = PLSpectrometer(sample=dye, scatter_fraction=0.0).acquire(
            lambda_exc_nm=dye.absorption.center_nm,
            lambda_min_nm=dye.absorption.center_nm + 5.0,
            lambda_max_nm=dye.absorption.center_nm + 150.0,
            dlambda_nm=0.5,
        )
        peak = scan.wavelengths_nm[int(np.argmax(scan.emitted_power))]
        assert abs(peak - dye.emission.center_nm) <= 1.0, key


def test_a_dye_does_not_emit_far_below_its_excitation_wavelength():
    scan = PLSpectrometer(sample=get_sample("cy5"), scatter_fraction=0.0).acquire(
        lambda_exc_nm=649.0, lambda_min_nm=400.0, lambda_max_nm=800.0, dlambda_nm=1.0
    )
    far_below = scan.wavelengths_nm < 649.0 - 20.0
    assert np.all(scan.emitted_power[far_below] == 0.0)


def test_the_monochromator_broadens_the_measured_band():
    dye = get_sample("cy3")
    spectrometer = PLSpectrometer(
        sample=dye,
        scatter_fraction=0.0,
        detection_monochromator=Monochromator(bandwidth_nm=10.0),
    )
    scan = spectrometer.acquire(
        lambda_exc_nm=520.0, lambda_min_nm=530.0, lambda_max_nm=640.0, dlambda_nm=0.25
    )
    measured = fwhm_nm(scan.wavelengths_nm, scan.emitted_power)
    expected = np.hypot(dye.emission.fwhm_nm, 10.0)
    assert abs(measured - expected) < 1.0


def test_excitation_inside_the_range_leaves_a_stray_light_line():
    scan = PLSpectrometer(sample=get_sample("cy5"), scatter_fraction=0.02).acquire(
        lambda_exc_nm=649.0, lambda_min_nm=600.0, lambda_max_nm=750.0, dlambda_nm=0.5
    )
    at_excitation = scan.scatter_power[int(np.argmin(np.abs(scan.wavelengths_nm - 649.0)))]
    assert at_excitation > 10.0 * np.median(scan.scatter_power)


def test_the_harmonic_filter_blocks_ultraviolet_excitation():
    spectrometer = PLSpectrometer(sample=get_sample("cy3"))
    assert spectrometer.excitation.power_at(300.0) < 1e-3 * spectrometer.excitation.power_at(550.0)


def test_emitted_power_scales_with_quantum_yield():
    dye = get_sample("cy3")
    dim = dataclasses.replace(dye, quantum_yield=dye.quantum_yield / 2.0)
    window = dict(lambda_exc_nm=550.0, lambda_min_nm=560.0, lambda_max_nm=600.0, dlambda_nm=1.0)
    bright_scan = PLSpectrometer(sample=dye, scatter_fraction=0.0).acquire(**window)
    dim_scan = PLSpectrometer(sample=dim, scatter_fraction=0.0).acquire(**window)
    assert np.isclose(bright_scan.emitted_power.max(), 2.0 * dim_scan.emitted_power.max())


def test_cy5_is_the_brighter_dye_at_its_own_optimum():
    cy3 = PLSpectrometer(sample=get_sample("cy3"), scatter_fraction=0.0)
    cy5 = PLSpectrometer(sample=get_sample("cy5"), scatter_fraction=0.0)
    cy3_scan = cy3.acquire(lambda_exc_nm=550.0, lambda_min_nm=560.0, lambda_max_nm=620.0, dlambda_nm=1.0)
    cy5_scan = cy5.acquire(lambda_exc_nm=649.0, lambda_min_nm=655.0, lambda_max_nm=715.0, dlambda_nm=1.0)
    assert cy5_scan.emitted_power.max() > cy3_scan.emitted_power.max()
