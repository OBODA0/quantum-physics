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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from settings import (  # noqa: E402  (same directory, after sys.path)
    ABSORPTION_RANGE_NM,
    ASSIGNED_EXCITATION_NM,
    CONCENTRATION_M,
    DETECTION_RANGE_NM,
    DYE_COLORS,
    DYE_KEYS,
    EXCITATION_START_NM,
    EXCITATION_STEP_NM,
    EXCITATION_STOP_NM,
    OVERLAY_EXCITATION_NM,
    PATH_LENGTH_CM,
    SCATTER_FRACTION,
    STRAY_COLOR,
)

FIG_DIR = Path(__file__).resolve().parent / "report_figures"

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


def description(dye, lambda_exc, with_name=True):
    """The numbers a reader needs to interpret one curve."""
    return "{}{:.0f} nM in 1 cm, A({:.0f} nm) = {:.3f}, A_peak = {:.3f}, Phi_f = {:g}".format(
        dye.name + ", " if with_name else "", CONCENTRATION_M * 1e9, lambda_exc,
        dye.absorbance(lambda_exc), dye.peak_absorbance, dye.quantum_yield)




# --- instrument diagram -----------------------------------------------------


def generate_diagram(dyes):
    """The design itself: the optical train the simulator models."""
    print("Instrument diagram")
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    figure, axis = plt.subplots(figsize=(13.0, 5.6), constrained_layout=True)
    axis.set_xlim(0, 104)
    axis.set_ylim(-2, 36)
    axis.axis("off")

    boxes = [
        ("Xenon arc lamp\n250-1000 nm\nshape model", 8.5),
        ("Excitation\nmonochromator\nlambda_exc, 5 nm", 23.0),
        ("Harmonic filter\npasses > 400 nm", 37.5),
        ("Sample\ndye in 1 cm cuvette\nA = eps*c*l", 52.5),
        ("Detection\nmonochromator\nlambda_min-lambda_max, dlambda, 2 nm", 69.0),
        ("Silicon photodiode\nR(lambda)\nI = R*P", 88.0),
    ]
    width, height, top = 12.8, 9.4, 25.0

    for label, centre in boxes:
        axis.add_patch(FancyBboxPatch(
            (centre - width / 2, top - height), width, height,
            boxstyle="round,pad=0.35,rounding_size=0.8",
            linewidth=1.2, edgecolor="#2c5282", facecolor="#eef3f9"))
        axis.text(centre, top - height / 2, label, ha="center", va="center", fontsize=8.6, color="#1a2a40")

    for index in range(len(boxes) - 1):
        start = boxes[index][1] + width / 2
        end = boxes[index + 1][1] - width / 2
        axis.add_patch(FancyArrowPatch((start + 0.2, top - height / 2), (end - 0.2, top - height / 2),
                                       arrowstyle="-|>", mutation_scale=13, linewidth=1.3, color="#2c5282"))

    # the user settings act on the two monochromators
    axis.annotate("user setting 1\nexcitation wavelength",
                  xy=(21.5, top - height - 0.4), xytext=(21.5, 9.2), ha="center", fontsize=8.4, color="#c1440e",
                  arrowprops=dict(arrowstyle="->", color="#c1440e", lw=1.1))
    axis.annotate("user setting 2 and 3\ndetection range and step size",
                  xy=(69.5, top - height - 0.4), xytext=(69.5, 9.2), ha="center", fontsize=8.4, color="#c1440e",
                  arrowprops=dict(arrowstyle="->", color="#c1440e", lw=1.1))

    # what the sample does, and the one leak the instrument has to fight
    axis.annotate("PL emitted at lambda > lambda_exc,\nband shape independent of lambda_exc (Kasha)",
                  xy=(52.5, top - height - 0.4), xytext=(46.0, 1.2), ha="center", fontsize=8.4, color="#1b9e77",
                  arrowprops=dict(arrowstyle="->", color="#1b9e77", lw=1.1))
    axis.add_patch(FancyArrowPatch((52.5, top), (69.5, top + 3.4),
                                   arrowstyle="-|>", mutation_scale=12, linewidth=1.1,
                                   color="#c1440e", linestyle="--",
                                   connectionstyle="arc3,rad=-0.28"))
    axis.text(61.5, top + 4.6, "stray excitation light reaching the detector (0.1 % in the figures)",
              ha="center", fontsize=8.4, color="#c1440e")

    axis.text(15.5, top + 1.4, "excitation arm", ha="center", fontsize=9.0, color="#2c5282", style="italic")
    axis.text(69.0, top + 1.4, "detection arm", ha="center", fontsize=9.0, color="#2c5282", style="italic")
    axis.add_patch(FancyArrowPatch((94.5, top - height / 2), (101.5, top - height / 2),
                                   arrowstyle="-|>", mutation_scale=13, linewidth=1.3, color="#2c5282"))
    axis.text(101.5, top - height / 2 - 2.6, "detected\nspectrum", ha="center", fontsize=8.4, color="#4a5568")

    axis.set_title("The instrument the simulator models: every box is a module in the appendix code",
                   fontsize=12.5, fontweight="bold")
    figure.savefig(FIG_DIR / "part1_instrument_diagram.png", dpi=300)
    plt.close(figure)
    return None


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
        axis.set_title("Simulated PL spectrum of {}\n{}".format(
            dye.name, description(dye, lambda_exc, with_name=False)), fontsize=11)
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
                  label="stray excitation ({:g} % of excitation)".format(SCATTER_FRACTION * 100))
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
    # stray light is on here, so the figure shows the scattered line tracking the
    # excitation wavelength; the sweep on the right uses the PL-only signal, so the
    # stray light cannot contaminate the integrated intensity
    cy3 = instrument(dye, SCATTER_FRACTION)

    figure, (left, right) = plt.subplots(1, 2, figsize=(14.5, 5.6), constrained_layout=True)

    cmap = plt.get_cmap("viridis")
    norm = plt.Normalize(vmin=460.0, vmax=570.0)
    bands = []
    for lambda_exc in OVERLAY_EXCITATION_NM:
        scan = cy3.acquire(lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
                           lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
        bands.append(measured_emission_band(scan))
        left.plot(scan.wavelengths_nm, scan.photocurrent, color=cmap(norm(lambda_exc)), lw=2.0,
                  label="excitation {:.0f} nm".format(lambda_exc))
    peaks = [band.peak_nm for band in bands]
    widths = [band.fwhm_nm for band in bands]
    left.set_title("Emission spectra for six excitation wavelengths\n"
                   "peak {:.1f}-{:.1f} nm, FWHM {:.1f}-{:.1f} nm: the band does not move "
                   "(Kasha's rule)".format(min(peaks), max(peaks), min(widths), max(widths)))
    left.set_xlabel("emission wavelength (nm)")
    left.set_ylabel("detected photocurrent (relative a.u.)")
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
    right.axvline(ABSORPTION_RANGE_NM["cy3"][1], color="#888888", lw=1.0, ls="-.")
    right.annotate("the measured Cy3 absorption curve ends at {:.0f} nm:\n"
                   "past it the model has no data and reads zero".format(ABSORPTION_RANGE_NM["cy3"][1]),
                   xy=(ABSORPTION_RANGE_NM["cy3"][1], 0.35), xytext=(ABSORPTION_RANGE_NM["cy3"][1] + 35.0, 0.35),
                   fontsize=8.5, color="#555555",
                   arrowprops=dict(arrowstyle="->", color="#888888", lw=1.0))
    right.set_xlabel("excitation wavelength (nm)")
    right.set_ylabel("normalized intensity")
    right.legend(loc="upper right")

    figure.suptitle("Part 2: excitation wavelength sweep of Cy3 ({:.0f}-{:.0f} nm)\n"
                    "the overlay shows 470-560 nm: the tabulated Cy3 band reads zero at 450, 600 and "
                    "650 nm, and it stops at {:.0f} nm".format(
                        EXCITATION_START_NM, EXCITATION_STOP_NM, ABSORPTION_RANGE_NM["cy3"][1]),
                    fontweight="bold", fontsize=12.5)
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
                      label="{} (A({:.0f} nm) = {:.3f})".format(
                          dye.name, lambda_exc, dye.absorbance(lambda_exc)))
        axis.axvline(lambda_exc, color="black", ls="--", alpha=0.5)
        axis.set_title("excitation {:.0f} nm".format(lambda_exc))
        axis.set_xlabel("wavelength (nm)")
        axis.legend(loc="upper right")
        panel_tallest = max(scans[(lambda_exc, key)].photocurrent.max() for key in DYE_KEYS)
        if panel_tallest < 0.02 * tallest:
            axis.text(0.5, 0.5,
                      "all three dyes are nearly transparent here\n"
                      "absorbed: {:.2f} % (Cy5), {:.2f} % (methylene blue),\n"
                      "zero for Cy3 in the model - its tabulated\n"
                      "band starts at 450 nm\n"
                      "this is why the panel looks empty".format(
                          100 * dyes["cy5"].absorbed_fraction(lambda_exc),
                          100 * dyes["methylene-blue"].absorbed_fraction(lambda_exc)),
                      transform=axis.transAxes, ha="center", va="center", fontsize=8.5,
                      bbox=dict(boxstyle="round", fc="white", ec="#bbbbbb"))
    axes[0].set_ylabel("photodetector current (relative a.u., shared scale)")
    figure.suptitle("Part 3: emission spectra of the three dyes at the same concentration "
                    "({:.0f} nM in 1 cm)\nand the same path length; stray light is left out of "
                    "these panels so the dyes can be compared".format(CONCENTRATION_M * 1e9),
                    fontweight="bold", fontsize=13)
    figure.savefig(FIG_DIR / "part3_three_dyes_comparison.png", dpi=300)
    plt.close(figure)

    # Why the peaks differ: each dye sits at a different point of its own absorption curve.
    figure, axis = plt.subplots(figsize=(10.5, 5.6), constrained_layout=True)
    for key in DYE_KEYS:
        dye = dyes[key]
        grid = np.arange(dye.absorption.wavelength_nm[0], dye.absorption.wavelength_nm[-1], 0.5)
        curve = dye.absorption(grid)
        axis.plot(grid, curve / curve.max(), color=DYE_COLORS[key], lw=2.2,
                  label="{} absorption (peaks at {:.0f} nm)".format(
                      dye.name, grid[int(np.argmax(curve))]))
    for wavelength, style in ((450.0, "-"), (550.0, "--"), (650.0, ":")):
        axis.axvline(wavelength, color="#333333", lw=1.1, ls=style, alpha=0.75)
        axis.text(wavelength, 1.045, "{:.0f} nm".format(wavelength), ha="center", fontsize=9, color="#333333")
    axis.set_title("Why the three peaks differ at the same concentration\nthe three absorption "
                   "curves, with the three excitation wavelengths marked")
    axis.set_xlabel("wavelength (nm)")
    axis.set_ylabel("absorption, normalized to each dye's own maximum")
    axis.set_ylim(0.0, 1.15)
    axis.legend(loc="upper right")
    figure.savefig(FIG_DIR / "part3_absorption_overlay.png", dpi=300)
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
                   "wavelengths; the peak current of every curve is printed on the right")
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

    generate_diagram(dyes)

    actions = {"part1": generate_part1, "part2": generate_part2, "part3": generate_part3}
    chosen = list(actions) if arguments.only == "all" else [arguments.only]
    output = [actions[name](dyes) for name in chosen]
    print("figures written to {}".format(FIG_DIR))
    return output


if __name__ == "__main__":
    main()
