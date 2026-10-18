"""Checks on the physics the report claims, not on the implementation."""

import dataclasses

import numpy as np
import pytest

from plsim.analysis import excitation_scan, measured_emission_band
from plsim.cli import main
from plsim.reference import load_reference_database
from plsim.samples import SAMPLE_DATABASE, get_sample, with_concentration
from plsim.sources import Monochromator
from plsim.spectrometer import PLSpectrometer


def fwhm_nm(x, y):
    """Full width at half maximum of a simple peak."""
    above_half = x[y >= y.max() / 2.0]
    return float(above_half[-1] - above_half[0])


# --- the instrument ---------------------------------------------------------


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


# --- the sample -------------------------------------------------------------


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


def test_a_scan_keeps_power_and_current_in_separate_units():
    """A figure that draws an optical power on a current axis is drawn in two units.

    This went wrong once: the stray-light curve was plotted from `scatter_power`
    on an axis labelled in photocurrent, which made it look taller than the
    spectrum it sits on.
    """
    scan = PLSpectrometer(sample=get_sample("methylene-blue"), scatter_fraction=0.001).acquire(
        lambda_exc_nm=664.0, lambda_min_nm=450.0, lambda_max_nm=900.0, dlambda_nm=1.0
    )
    assert np.allclose(scan.photocurrent, scan.emitted_photocurrent + scan.scatter_photocurrent)
    assert np.all(scan.scatter_photocurrent <= scan.photocurrent + 1e-12)
    # in the same units the stray line is a fraction of the PL, never the tallest feature
    assert scan.scatter_photocurrent.max() < scan.emitted_photocurrent.max()


def test_emission_is_linear_in_the_absorbed_light():
    """Doubling what is absorbed doubles the emission, wavelength by wavelength."""
    dye = get_sample("cy3")
    grid = np.array([550.0, 570.0, 590.0])
    once = dye.emitted_power(grid, 550.0, 1.0)
    twice = dye.emitted_power(grid, 550.0, 2.0)
    assert np.allclose(twice, 2.0 * once)


def test_the_emission_band_does_not_move_with_the_excitation_wavelength():
    """Kasha's rule: the spectrum is the same whatever excites the sample."""
    dye = load_reference_database()["cy3"]
    spectrometer = PLSpectrometer(sample=dye, scatter_fraction=0.0)
    bands = [
        measured_emission_band(
            spectrometer.acquire(
                lambda_exc_nm=lambda_exc,
                lambda_min_nm=450.0,
                lambda_max_nm=800.0,
                dlambda_nm=0.5,
            )
        )
        for lambda_exc in (480.0, 500.0, 520.0, 540.0)
    ]
    peaks = [band.peak_nm for band in bands]
    widths = [band.fwhm_nm for band in bands]
    assert max(peaks) - min(peaks) <= 0.5
    assert max(widths) - min(widths) <= 0.5


def test_there_is_no_cut_of_the_emission_at_the_excitation_wavelength():
    """A step at lambda_exc used to truncate the band; it must not come back."""
    dye = get_sample("cy5")
    grid = np.arange(660.0, 701.0, 1.0)
    emitted = dye.emitted_power(grid, 650.0, 1.0)
    ratio = emitted[1:] / emitted[:-1]
    assert ratio.max() < 1.2


# --- the measured reference data -------------------------------------------


def test_the_reference_database_peaks_where_the_sources_say():
    import json

    from plsim.reference import DEFAULT_PATH

    records = json.loads(DEFAULT_PATH.read_text())
    database = load_reference_database()
    assert set(database) == set(SAMPLE_DATABASE)
    for key, dye in database.items():
        grid = np.arange(dye.emission.wavelength_nm[0], dye.emission.wavelength_nm[-1], 0.1)
        peak = grid[int(np.argmax(dye.emission(grid)))]
        assert abs(peak - records[key]["emission_max_nm"]) <= 4.0, key


def test_the_reference_pack_is_well_formed():
    """The data file is an input, so its shape and ranges are checked, not assumed."""
    import json

    from plsim.reference import DEFAULT_PATH

    records = json.loads(DEFAULT_PATH.read_text())
    assert set(records) == set(SAMPLE_DATABASE)
    for key, record in records.items():
        for field in (
            "absorption_max_nm",
            "emission_max_nm",
            "quantum_yield",
            "quantum_yield_solvent",
            "extinction_coefficient_per_M_per_cm",
            "digitized_absorption",
            "digitized_emission",
            "notes",
        ):
            assert field in record, (key, field)
        assert 0.0 < record["quantum_yield"] <= 1.0, key
        assert record["extinction_coefficient_per_M_per_cm"] > 0, key
        for field, quoted_maximum in (
            ("digitized_absorption", record["absorption_max_nm"]),
            ("digitized_emission", record["emission_max_nm"]),
        ):
            wavelengths = np.asarray(record[field]["wavelength_nm"], dtype=float)
            values = np.asarray(record[field]["value"], dtype=float)
            assert wavelengths.size == values.size > 50, (key, field)
            assert np.all(np.diff(wavelengths) > 0), (key, field)
            assert np.all(np.isfinite(values)), (key, field)
            # digitization leaves a few thousandths below zero on the
            # methylene blue absorption curve; anything larger is a real fault
            assert values.min() > -0.01, (key, field, values.min())
            assert abs(values.max() - 1.0) < 1e-6, (key, field)
            assert wavelengths[0] < quoted_maximum < wavelengths[-1], (key, field)


def test_the_reference_database_runs_through_the_instrument():
    dye = load_reference_database()["cy5"]
    scan = PLSpectrometer(sample=dye, scatter_fraction=0.0).acquire(
        lambda_exc_nm=649.0, lambda_min_nm=600.0, lambda_max_nm=780.0, dlambda_nm=0.5
    )
    assert abs(scan.emission_peak_nm - 670.0) <= 4.0


def test_model_and_reference_agree_on_the_band_width():
    measured = load_reference_database()["cy3"]
    x = np.arange(520.0, 640.0, 0.25)
    assert abs(fwhm_nm(x, measured.emission(x)) - get_sample("cy3").emission.fwhm_nm) < 2.0


# --- concentration, which is what the third question turns on --------------


def test_equal_concentration_does_not_mean_equal_peak_absorbance():
    database = load_reference_database()
    one_micromolar = 1.0e-6
    absorbances = {
        key: with_concentration(dye, one_micromolar).peak_absorbance for key, dye in database.items()
    }
    assert np.isclose(absorbances["cy3"], 0.150)
    assert np.isclose(absorbances["cy5"], 0.250)
    assert np.isclose(absorbances["methylene-blue"], 0.067)
    assert absorbances["cy5"] > absorbances["cy3"] > absorbances["methylene-blue"]


def test_concentration_needs_an_extinction_coefficient():
    dye = dataclasses.replace(get_sample("cy3"), extinction_coefficient=None)
    with pytest.raises(ValueError):
        with_concentration(dye, 1.0e-6)


# --- the excitation scan ----------------------------------------------------


def test_the_excitation_scan_reproduces_the_model():
    """The measured sweep must equal P_exc * (1 - 10**-A) * QY * band integral."""
    for key in ("cy3", "cy5", "methylene-blue"):
        spectrometer = PLSpectrometer(sample=load_reference_database()[key], scatter_fraction=0.0)
        sweep = excitation_scan(
            spectrometer, np.arange(400.0, 701.0, 2.0), detection_range_nm=(450.0, 900.0)
        )
        assert sweep.agreement < 1e-6, key
        assert sweep.band_integral_drift < 1e-9, key


def test_the_excitation_scan_peaks_at_the_absorption_maximum():
    spectrometer = PLSpectrometer(sample=load_reference_database()["cy3"], scatter_fraction=0.0)
    sweep = excitation_scan(spectrometer, np.arange(450.0, 620.0, 1.0))
    assert abs(sweep.measured_peak_wavelength_nm - 550.0) <= 5.0


# --- the command line -------------------------------------------------------


def test_the_cli_rejects_bad_input():
    for arguments in (
        ["--sample", "cy3", "--dlambda", "0"],
        ["--sample", "cy3", "--range", "700", "500"],
        ["--sample", "not-a-dye"],
        ["--sample", "cy3", "--concentration", "1e-6", "--peak-absorbance", "1.0"],
        ["--sample", "cy3", "--concentration", "-1e-6"],
    ):
        with pytest.raises(SystemExit):
            main(arguments)
