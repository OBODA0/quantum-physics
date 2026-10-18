"""
Assignment figures for the PL spectrometer simulation.

Question 1: emission spectrum of Cy3, Cy5 and methylene blue.
Question 2: Cy3 with the excitation wavelength swept from 400 nm to 700 nm.
Question 3: the three dyes on one graph at 450 nm, 550 nm and 650 nm excitation.

Fixed settings, which the report must state:
  - all dyes at the SAME CONCENTRATION (1 micromolar, 1 cm cuvette), so the peak
    absorbances differ by their extinction coefficients;
  - detection range wide enough to contain the whole emission band, so a measured
    intensity reflects absorbed light rather than where the window happened to end;
  - stray excitation light at 0.1 % of the excitation power (a double monochromator
    with a harmonic filter rejects most of it; the figure legends say so).

Usage: python report/generate_assignment_figures.py [--database model] [--only part2]
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from plsim.analysis import excitation_scan, measured_emission_band
from plsim.reference import DEFAULT_PATH, load_reference_database
from plsim.samples import SAMPLE_DATABASE, with_concentration
from plsim.spectrometer import PLSpectrometer

FIG_DIR = Path(__file__).resolve().parent / "report_figures"

CONCENTRATION_M = 1.0e-6
PATH_LENGTH_CM = 1.0
SCATTER_FRACTION = 0.001
DETECTION_RANGE_NM = (450.0, 900.0)
EXCITATION_START_NM = 400.0
EXCITATION_STOP_NM = 700.0
EXCITATION_STEP_NM = 2.0
# Excitation wavelengths used in the overlay: Cy3 is transparent at 450 and 650 nm,
# so those curves would be flat lines at zero and would only clutter the legend.
OVERLAY_EXCITATION_NM = (470.0, 500.0, 520.0, 540.0, 550.0, 560.0)
ASSIGNED_EXCITATION_NM = (450.0, 550.0, 650.0)

DYE_KEYS = ["cy3", "cy5", "methylene-blue"]
DYE_COLORS = {"cy3": "#d95f02", "cy5": "#7570b3", "methylene-blue": "#1b9e77"}
STRAY_COLOR = "#c1440e"

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})


def database(choice):
    source = SAMPLE_DATABASE if choice == "model" else load_reference_database()
    return {key: with_concentration(dye, CONCENTRATION_M, PATH_LENGTH_CM) for key, dye in source.items()}


def absorption_maximum_nm(key):
    """The absorption maximum the sources report (the curve peaks a few nm away)."""
    return float(json.loads(Path(DEFAULT_PATH).read_text())[key]["absorption_max_nm"])


def instrument(dye, scatter=0.0):
    return PLSpectrometer(sample=dye, scatter_fraction=scatter)


def report(rows):
    for row in rows:
        print(row)


def description(dye, lambda_exc):
    """The numbers a reader needs to interpret one curve."""
    return "{}, {:.0f} nM in 1 cm, A({:.0f} nm) = {:.3f}, A_peak = {:.3f}, Phi_f = {:g}".format(
        dye.name, CONCENTRATION_M * 1e9, lambda_exc, dye.absorbance(lambda_exc),
        dye.peak_absorbance, dye.quantum_yield)


# --- question 1 -------------------------------------------------------------


def generate_part1(dyes):
    print("Part 1: baseline spectra of the three dyes")
    review = []

    for key, dye in dyes.items():
        lambda_exc = absorption_maximum_nm(key)
        scan = instrument(dye, SCATTER_FRACTION).acquire(
            lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
            lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
        band = measured_emission_band(scan)
        review.append(
            "  {:<16s} lambda_exc {:5.0f} nm  A(exc) {:.3f}  absorbed {:6.2%}  "
            "emission peak {:6.1f} nm  FWHM {:5.1f} nm  stray/PL {:.3f}".format(
                dye.name, lambda_exc, dye.absorbance(lambda_exc), dye.absorbed_fraction(lambda_exc),
                band.peak_nm, band.fwhm_nm,
                scan.scatter_photocurrent.max() / scan.emitted_photocurrent.max()))

        figure, axis = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
        axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=2.2,
                  label="detected photocurrent (PL + stray)")
        axis.plot(scan.wavelengths_nm, scan.scatter_photocurrent, color=STRAY_COLOR, lw=1.3, ls=":",
                  label="stray excitation light ({:g} % of excitation)".format(SCATTER_FRACTION * 100))
        axis.axvline(scan.lambda_exc_nm, color="gray", ls="--", alpha=0.7,
                     label="excitation {:.0f} nm".format(scan.lambda_exc_nm))
        axis.set_title("Simulated PL spectrum of {}\n{}".format(dye.name, description(dye, lambda_exc)),
                       fontsize=11)
        axis.set_xlabel("wavelength (nm)")
        axis.set_ylabel("photodetector current (relative a.u.)")
        axis.legend(loc="upper right")
        figure.savefig(FIG_DIR / "part1_{}.png".format(key), dpi=300)
        plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(16, 4.8), constrained_layout=True)
    for axis, key in zip(axes, DYE_KEYS):
        dye = dyes[key]
        lambda_exc = absorption_maximum_nm(key)
        scan = instrument(dye, SCATTER_FRACTION).acquire(
            lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
            lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
        axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=2.2,
                  label="detected photocurrent")
        axis.plot(scan.wavelengths_nm, scan.scatter_photocurrent, color=STRAY_COLOR, lw=1.2, ls=":",
                  label="stray excitation")
        axis.axvline(scan.lambda_exc_nm, color="gray", ls="--", alpha=0.7,
                     label="excitation {:.0f} nm".format(scan.lambda_exc_nm))
        axis.set_title("{}\nA({:.0f} nm) = {:.3f}, Phi_f = {:g}".format(
            dye.name, lambda_exc, dye.absorbance(lambda_exc), dye.quantum_yield))
        axis.set_xlabel("wavelength (nm)")
        axis.legend(loc="upper right")
    axes[0].set_ylabel("photodetector current (relative a.u.)")
    figure.suptitle("Part 1: simulated PL spectra, all three dyes at {:.0f} nM in a 1 cm cuvette "
                    "(note: each panel has its own current scale)".format(CONCENTRATION_M * 1e9),
                    fontweight="bold")
    figure.savefig(FIG_DIR / "part1_combined_overview.png", dpi=300)
    plt.close(figure)
    report(review)


# --- question 2 -------------------------------------------------------------


def generate_part2(dyes):
    print("Part 2: Cy3 with the excitation wavelength swept {:.0f} to {:.0f} nm".format(
        EXCITATION_START_NM, EXCITATION_STOP_NM))
    dye = dyes["cy3"]
    cy3 = instrument(dye, 0.0)

    figure, (left, right) = plt.subplots(1, 2, figsize=(14.5, 5.6), constrained_layout=True)

    cmap = plt.get_cmap("viridis")
    norm = plt.Normalize(vmin=460.0, vmax=570.0)
    bands = []
    for lambda_exc in OVERLAY_EXCITATION_NM:
        scan = cy3.acquire(lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
                           lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
        bands.append(measured_emission_band(scan))
        left.plot(scan.wavelengths_nm, scan.emitted_photocurrent, color=cmap(norm(lambda_exc)), lw=2.0,
                  label="excitation {:.0f} nm".format(lambda_exc))
    peaks = [band.peak_nm for band in bands]
    widths = [band.fwhm_nm for band in bands]
    left.set_title("Emission spectra for six excitation wavelengths\n"
                   "peak {:.1f}-{:.1f} nm, FWHM {:.1f}-{:.1f} nm: the band does not move "
                   "(Kasha's rule)".format(min(peaks), max(peaks), min(widths), max(widths)))
    left.set_xlabel("emission wavelength (nm)")
    left.set_ylabel("PL photocurrent (relative a.u.)")
    left.legend(loc="upper right")

    sweep = excitation_scan(cy3, np.arange(EXCITATION_START_NM, EXCITATION_STOP_NM + 0.1,
                                           EXCITATION_STEP_NM))
    measured = sweep.integrated_pl / sweep.integrated_pl.max()
    predicted = sweep.predicted / sweep.predicted.max()
    absorbance = np.array([dye.absorbance(w) for w in sweep.wavelengths_nm])
    absorbance = absorbance / absorbance.max()

    right.plot(sweep.wavelengths_nm, measured, color="#d95f02", lw=2.8,
               label="simulated PL intensity (whole band)")
    right.plot(sweep.wavelengths_nm, predicted, color="#1f4e9c", lw=1.4, ls="--",
               label="model: P_exc x (1 - 10^-A) x Phi_f")
    right.plot(sweep.wavelengths_nm, absorbance, color="#1b9e77", lw=1.4, ls=":",
               label="absorbance A(wavelength), normalized")
    right.set_title("PL intensity while the excitation wavelength is swept\n"
                    "measured vs model vs absorbance")
    right.set_xlabel("excitation wavelength (nm)")
    right.set_ylabel("normalized intensity")
    right.legend(loc="upper right")

    figure.suptitle("Part 2: excitation wavelength sweep of Cy3 ({:.0f}-{:.0f} nm); Cy3 is "
                    "transparent at 450 and 650 nm, so only 470-560 nm produces a visible "
                    "spectrum".format(EXCITATION_START_NM, EXCITATION_STOP_NM), fontweight="bold")
    figure.savefig(FIG_DIR / "part2_cy3_excitation_sweep.png", dpi=300)
    plt.close(figure)

    report([
        "  emission peak across the six wavelengths: {:.1f} to {:.1f} nm".format(min(peaks), max(peaks)),
        "  emission FWHM across the six wavelengths: {:.1f} to {:.1f} nm".format(min(widths), max(widths)),
        "  excitation scan peaks at {:.1f} nm".format(sweep.measured_peak_wavelength_nm),
        "  max |measured - model| = {:.2e} of full scale".format(sweep.agreement),
        "  band integral drift across the sweep = {:.2e}".format(sweep.band_integral_drift),
    ])
    return sweep


# --- question 3 -------------------------------------------------------------


def generate_part3(dyes):
    print("Part 3: three dyes at the same concentration, excited at {}".format(
        ", ".join("{:.0f} nm".format(w) for w in ASSIGNED_EXCITATION_NM)))
    review = []

    # Every curve first, so the panels can be judged against the tallest curve of
    # all of them rather than against the axis of whichever panel is being drawn.
    scans = {}
    for lambda_exc in ASSIGNED_EXCITATION_NM:
        for key in DYE_KEYS:
            dye = dyes[key]
            scans[(lambda_exc, key)] = instrument(dye, 0.0).acquire(
                lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
                lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
            review.append(
                "  lambda_exc {:5.0f} nm  {:<16s} A(exc) {:.4f}  absorbed {:6.2%}  peak current {:.5f}".format(
                    lambda_exc, dye.name, dye.absorbance(lambda_exc),
                    dye.absorbed_fraction(lambda_exc), scans[(lambda_exc, key)].photocurrent.max()))
    tallest = max(scan.photocurrent.max() for scan in scans.values())

    figure, axes = plt.subplots(1, 3, figsize=(16, 5.2), constrained_layout=True, sharey=True)
    for axis, lambda_exc in zip(axes, ASSIGNED_EXCITATION_NM):
        for key in DYE_KEYS:
            dye = dyes[key]
            scan = scans[(lambda_exc, key)]
            axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=2.0,
                      label="{} (A = {:.3f})".format(dye.name, dye.peak_absorbance))
        axis.axvline(lambda_exc, color="black", ls="--", alpha=0.5)
        axis.set_title("excitation {:.0f} nm".format(lambda_exc))
        axis.set_xlabel("wavelength (nm)")
        axis.legend(loc="upper right")
        panel_tallest = max(scans[(lambda_exc, key)].photocurrent.max() for key in DYE_KEYS)
        if panel_tallest < 0.02 * tallest:
            axis.text(0.5, 0.5,
                      "all three dyes are nearly transparent here\n"
                      "absorbed {:.2f} % (Cy3), {:.2f} % (Cy5), {:.2f} % (methylene blue)\n"
                      "this is why the panel looks empty".format(
                          100 * dyes["cy3"].absorbed_fraction(lambda_exc),
                          100 * dyes["cy5"].absorbed_fraction(lambda_exc),
                          100 * dyes["methylene-blue"].absorbed_fraction(lambda_exc)),
                      transform=axis.transAxes, ha="center", va="center", fontsize=9,
                      bbox=dict(boxstyle="round", fc="white", ec="#bbbbbb"))
    axes[0].set_ylabel("photodetector current (relative a.u., shared scale)")
    figure.suptitle("Part 3: emission spectra of the three dyes at the same concentration "
                    "({:.0f} nM in 1 cm), identical optical conditions".format(CONCENTRATION_M * 1e9),
                    fontweight="bold")
    figure.savefig(FIG_DIR / "part3_three_dyes_comparison.png", dpi=300)
    plt.close(figure)

    styles = {450.0: (2.4, "-"), 550.0: (1.6, "--"), 650.0: (1.2, ":")}
    figure, axis = plt.subplots(figsize=(11.5, 6.5), constrained_layout=True)
    heights = []
    for lambda_exc in ASSIGNED_EXCITATION_NM:
        for key in DYE_KEYS:
            dye = dyes[key]
            scan = instrument(dye, 0.0).acquire(
                lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
                lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
            width, style = styles[lambda_exc]
            axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=width,
                      ls=style, label="{} at {:.0f} nm".format(dye.name, lambda_exc))
            heights.append("{} at {:.0f} nm: peak {:.4f}".format(dye.name, lambda_exc, scan.photocurrent.max()))
    axis.set_title("Part 3: all nine spectra on one canvas\nsame concentration, three excitation "
                   "wavelengths (the four visible peaks are the whole answer)")
    axis.set_xlabel("wavelength (nm)")
    axis.set_ylabel("photodetector current (relative a.u.)")
    axis.legend(loc="upper right", fontsize=8.5)
    axis.text(0.985, 0.55, "\n".join(heights), transform=axis.transAxes, ha="right", va="top",
              fontsize=8, family="monospace",
              bbox=dict(boxstyle="round", fc="white", ec="#bbbbbb", alpha=0.9))
    figure.savefig(FIG_DIR / "part3_single_canvas_overlay.png", dpi=300)
    plt.close(figure)
    report(review)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Draw the assignment figures.")
    parser.add_argument("--database", choices=("reference", "model"), default="reference",
                        help="measured reference bands (default) or the Gaussian model")
    parser.add_argument("--only", choices=("all", "part1", "part2", "part3"), default="all",
                        help="draw one question's figures instead of all of them (default: %(default)s)")
    arguments = parser.parse_args(argv)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    dyes = database(arguments.database)
    print("dye data: {} bands, concentration {:.0f} nM, path length {:g} cm, stray light {:.1%}".format(
        arguments.database, CONCENTRATION_M * 1e9, PATH_LENGTH_CM, SCATTER_FRACTION))

    actions = {"part1": generate_part1, "part2": generate_part2, "part3": generate_part3}
    chosen = list(actions) if arguments.only == "all" else [arguments.only]
    output = [actions[name](dyes) for name in chosen]
    print("figures written to {}".format(FIG_DIR))
    return output


if __name__ == "__main__":
    main()
