"""
Assignment figures for the PL spectrometer simulation.

Question 1: emission spectrum of Cy3, Cy5 and methylene blue.
Question 2: Cy3 with the excitation wavelength swept from 400 nm to 700 nm.
Question 3: the three dyes on one graph at 450 nm, 550 nm and 650 nm excitation.

All three use the same two settings, which the report must state:
  - the dyes are at the SAME CONCENTRATION (1 micromolar, 1 cm cuvette), so the
    peak absorbances differ by their extinction coefficients;
  - the detection range is wide enough to contain the whole emission band, so a
    measured intensity reflects how much light the dye absorbed rather than
    where the detection window happened to end.

Usage: python report/generate_assignment_figures.py [--database model]
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
from plsim.samples import SAMPLE_DATABASE, get_sample, with_concentration
from plsim.spectrometer import PLSpectrometer

FIG_DIR = Path(__file__).resolve().parent / "report_figures"

CONCENTRATION_M = 1.0e-6
PATH_LENGTH_CM = 1.0
SCATTER_FRACTION = 0.005
DETECTION_RANGE_NM = (450.0, 900.0)
EXCITATION_START_NM = 400.0
EXCITATION_STOP_NM = 700.0
EXCITATION_STEP_NM = 2.0

DYE_KEYS = ["cy3", "cy5", "methylene-blue"]
DYE_COLORS = {"cy3": "#d95f02", "cy5": "#7570b3", "methylene-blue": "#1b9e77"}
EXCITATION_WAVELENGTHS_NM = [450.0, 550.0, 650.0]

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})


def database(choice):
    """The dyes used in every figure, at the same concentration."""
    source = SAMPLE_DATABASE if choice == "model" else load_reference_database()
    return {
        key: with_concentration(dye, CONCENTRATION_M, PATH_LENGTH_CM)
        for key, dye in source.items()
    }


def spectrometer(dye, scatter=0.0):
    return PLSpectrometer(sample=dye, scatter_fraction=scatter)


def report(rows):
    """Print the numbers the figures rest on, so a screenshot can show them."""
    for row in rows:
        print(row)


# --- question 1 -------------------------------------------------------------


def generate_part1(dyes):
    print("Part 1: baseline spectra of the three dyes")
    review = []

    for key, dye in dyes.items():
        scan = spectrometer(dye, SCATTER_FRACTION).acquire(
            lambda_exc_nm=absorption_maximum_nm(key),
            lambda_min_nm=DETECTION_RANGE_NM[0],
            lambda_max_nm=DETECTION_RANGE_NM[1],
            dlambda_nm=1.0,
        )
        band = measured_emission_band(scan)
        review.append(
            "  {:<16s} lambda_exc {:6.1f} nm  A_peak {:.3f}  absorbed {:.1%}  "
            "emission peak {:6.1f} nm  FWHM {:5.1f} nm".format(
                dye.name,
                scan.lambda_exc_nm,
                dye.peak_absorbance,
                dye.absorbed_fraction(scan.lambda_exc_nm),
                band.peak_nm,
                band.fwhm_nm,
            )
        )

        figure, axis = plt.subplots(figsize=(6.5, 4.2), constrained_layout=True)
        axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=2.2,
                  label="detected PL ({} at {:.0f} nm)".format(dye.name, scan.lambda_exc_nm))
        if scan.scatter_power.max() > 0:
            axis.plot(scan.wavelengths_nm, scan.scatter_power, color="#c1440e", lw=1.2, ls=":",
                      label="stray excitation light")
        axis.axvline(scan.lambda_exc_nm, color="gray", ls="--", alpha=0.7,
                     label=r"$\lambda_{exc}$ = " + "{:.0f} nm".format(scan.lambda_exc_nm))
        axis.set_title("Simulated PL spectrum of {}\n{} at {:.0f} nm, {:.0f} nM, A = {:.3f}".format(
            dye.name, r"$\lambda_{exc}$", scan.lambda_exc_nm, CONCENTRATION_M * 1e9, dye.peak_absorbance))
        axis.set_xlabel(r"wavelength $\lambda$ (nm)")
        axis.set_ylabel("photodetector current (relative a.u.)")
        axis.legend(loc="upper right")
        figure.savefig(FIG_DIR / "part1_{}.png".format(key), dpi=300)
        plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for axis, key in zip(axes, DYE_KEYS):
        dye = dyes[key]
        lambda_exc = absorption_maximum_nm(key)
        scan = spectrometer(dye, SCATTER_FRACTION).acquire(
            lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
            lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
        axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=2.2,
                  label="{} PL".format(dye.name))
        axis.axvline(scan.lambda_exc_nm, color="gray", ls="--", alpha=0.7,
                     label=r"$\lambda_{exc}$ = " + "{:.0f} nm".format(scan.lambda_exc_nm))
        axis.set_title("{}\nA = {:.3f}, {}= {:g}".format(
            dye.name, dye.peak_absorbance, r"$\Phi_f$", dye.quantum_yield))
        axis.set_xlabel(r"wavelength $\lambda$ (nm)")
        axis.set_ylabel("photodetector current (relative a.u.)")
        axis.legend(loc="upper right")
    figure.suptitle("Part 1: simulated PL spectra, all dyes at {} nM in a 1 cm cuvette".format(
        CONCENTRATION_M * 1e9), fontweight="bold")
    figure.savefig(FIG_DIR / "part1_combined_overview.png", dpi=300)
    plt.close(figure)
    report(review)


def _band_peak(band):
    """Peak wavelength of a tabulated band."""
    grid = np.arange(band.wavelength_nm[0], band.wavelength_nm[-1], 0.1)
    return float(grid[int(np.argmax(band(grid)))])


def absorption_maximum_nm(key):
    """The absorption maximum the sources report for a dye.

    The digitized curve peaks a few nm away from the quoted maximum (the Cy3
    curve peaks at 554 nm, the vendor value is 550 nm). The figures are drawn at
    the quoted value so that they agree with the numbers in the report text.
    """
    record = json.loads(Path(DEFAULT_PATH).read_text())[key]
    return float(record["absorption_max_nm"])


# --- question 2 -------------------------------------------------------------


def generate_part2(dyes):
    print("Part 2: Cy3 with the excitation wavelength swept {} to {} nm".format(
        EXCITATION_START_NM, EXCITATION_STOP_NM))
    dye = dyes["cy3"]
    instrument = spectrometer(dye, 0.0)

    figure, (left, right) = plt.subplots(1, 2, figsize=(14.5, 5.4), constrained_layout=True)

    cmap = plt.get_cmap("viridis")
    norm = plt.Normalize(vmin=440.0, vmax=660.0)
    for lambda_exc in (450.0, 470.0, 500.0, 520.0, 540.0, 550.0, 560.0, 600.0, 650.0):
        scan = instrument.acquire(lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
                                  lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
        left.plot(scan.wavelengths_nm, scan.emitted_power, color=cmap(norm(lambda_exc)), lw=1.9,
                  label=r"$\lambda_{{exc}}$ = {:.0f} nm".format(lambda_exc))
    left.set_title("Emission spectra for nine excitation wavelengths\nthe band does not move "
                   "(Kasha's rule); only its height changes")
    left.set_xlabel(r"emission wavelength $\lambda$ (nm)")
    left.set_ylabel("PL power (relative a.u.)")
    left.legend(loc="upper right", fontsize=8.5, ncol=1)

    sweep = excitation_scan(instrument, np.arange(EXCITATION_START_NM, EXCITATION_STOP_NM + 0.1,
                                                  EXCITATION_STEP_NM))
    measured = sweep.integrated_pl / sweep.integrated_pl.max()
    predicted = sweep.predicted / sweep.predicted.max()
    absorbance = np.array([dye.absorbance(w) for w in sweep.wavelengths_nm])
    absorbance = absorbance / absorbance.max()

    right.plot(sweep.wavelengths_nm, measured, color="#d95f02", lw=2.6,
               label="simulated PL intensity (integrated band)")
    right.plot(sweep.wavelengths_nm, predicted, color="#1f4e9c", lw=1.4, ls="--",
               label=r"model: $P_{exc}(1-10^{-A})\Phi_f$")
    right.plot(sweep.wavelengths_nm, absorbance, color="#1b9e77", lw=1.4, ls=":",
               label=r"absorbance $A(\lambda)$, normalized")
    right.set_title("PL intensity while $\\lambda_{exc}$ is swept\n"
                    "measured vs the model prediction")
    right.set_xlabel("excitation wavelength (nm)")
    right.set_ylabel("normalized intensity")
    right.legend(loc="upper right", fontsize=9)

    figure.suptitle("Part 2: excitation wavelength sweep of Cy3 ({} to {} nm), A = {:.3f} at the "
                    "absorption maximum".format(EXCITATION_START_NM, EXCITATION_STOP_NM,
                                                dye.peak_absorbance), fontweight="bold")
    figure.savefig(FIG_DIR / "part2_cy3_excitation_sweep.png", dpi=300)
    plt.close(figure)

    report([
        "  excitation scan peak at {:.1f} nm".format(sweep.measured_peak_wavelength_nm),
        "  max |measured - model| = {:.2e} of full scale".format(sweep.agreement),
        "  band integral drift across the sweep = {:.2e}".format(sweep.band_integral_drift),
    ])
    return sweep


# --- question 3 -------------------------------------------------------------


def generate_part3(dyes):
    print("Part 3: three dyes at the same concentration, excited at {} nm".format(
        ", ".join("{:.0f}".format(w) for w in EXCITATION_WAVELENGTHS_NM)))
    review = []

    figure, axes = plt.subplots(1, 3, figsize=(16, 5.0), constrained_layout=True, sharey=True)
    for axis, lambda_exc in zip(axes, EXCITATION_WAVELENGTHS_NM):
        for key in DYE_KEYS:
            dye = dyes[key]
            scan = spectrometer(dye, 0.0).acquire(
                lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
                lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
            axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=2.0,
                      label="{} (A = {:.3f})".format(dye.name, dye.peak_absorbance))
            integrated = float(np.trapezoid(scan.emitted_power, scan.wavelengths_nm))
            peak = "{:6.1f} nm".format(measured_emission_band(scan).peak_nm) if integrated > 0 else "no emission"
            review.append(
                "  lambda_exc {:5.0f} nm  {:<16s} A = {:.3f}  absorbed {:6.2%}  peak {}".format(
                    lambda_exc, dye.name, dye.peak_absorbance, dye.absorbed_fraction(lambda_exc), peak))
        axis.axvline(lambda_exc, color="black", ls="--", alpha=0.5)
        axis.set_title(r"$\lambda_{exc}$ = " + "{:.0f} nm".format(lambda_exc))
        axis.set_xlabel(r"wavelength $\lambda$ (nm)")
        axis.legend(loc="upper right", fontsize=9)
    axes[0].set_ylabel("photodetector current (relative a.u.)")
    figure.suptitle("Part 3: emission spectra of the three dyes at the same concentration ({} nM),"
                    " identical optical conditions".format(CONCENTRATION_M * 1e9), fontweight="bold")
    figure.savefig(FIG_DIR / "part3_three_dyes_comparison.png", dpi=300)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(10.5, 6.0), constrained_layout=True)
    styles = {450.0: (2.4, "-"), 550.0: (1.9, "--"), 650.0: (1.4, ":")}
    for lambda_exc in EXCITATION_WAVELENGTHS_NM:
        for key in DYE_KEYS:
            dye = dyes[key]
            scan = spectrometer(dye, 0.0).acquire(
                lambda_exc_nm=lambda_exc, lambda_min_nm=DETECTION_RANGE_NM[0],
                lambda_max_nm=DETECTION_RANGE_NM[1], dlambda_nm=1.0)
            width, style = styles[lambda_exc]
            axis.plot(scan.wavelengths_nm, scan.photocurrent, color=DYE_COLORS[key], lw=width,
                      ls=style, label="{} at {:.0f} nm".format(dye.name, lambda_exc))
    axis.set_title("Part 3: all nine spectra on one canvas\nsame concentration, three excitation "
                   "wavelengths")
    axis.set_xlabel(r"wavelength $\lambda$ (nm)")
    axis.set_ylabel("photodetector current (relative a.u.)")
    axis.legend(loc="upper right", fontsize=9, ncol=1)
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
    print("dye data: {} bands, concentration {} nM, path length {} cm".format(
        arguments.database, CONCENTRATION_M * 1e9, PATH_LENGTH_CM))

    actions = {"part1": generate_part1, "part2": generate_part2, "part3": generate_part3}
    chosen = list(actions) if arguments.only == "all" else [arguments.only]
    output = [actions[name](dyes) for name in chosen]
    print("figures written to {}".format(FIG_DIR))
    return output


if __name__ == "__main__":
    main()
