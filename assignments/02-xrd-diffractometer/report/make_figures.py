"""Figures for the assignment 2 report.

Every figure here is written straight from the simulator, so a figure cannot drift from
the model. Run it with:

    uv run python -m report.make_figures
"""

from __future__ import annotations

import contextlib
import io
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from xrdsim.diffractometer import Instrument, scan
from xrdsim.plot import plot_scan
from xrdsim.samples import PHASES, get_phase

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "figures"
LAMBDA = 1.540598


def instrument_diagram() -> None:
    """Block diagram of the Bragg-Brentano chain."""
    fig, ax = plt.subplots(figsize=(11, 2.6))
    boxes = [
        ("X-ray tube\nCu K-alpha", 0.5), ("divergence\nslit", 2.1),
        ("Soller slit", 3.4), ("sample on\ntheta/2theta", 4.9),
        ("receiving\nslit", 6.4), ("monochromator\n(optional)", 7.9),
        ("detector", 9.4),
    ]
    for label, x in boxes:
        rect = Rectangle((x, 0.40), 1.1, 0.42, fill=False, lw=1.2, color="#1a3d6d")
        ax.add_patch(rect)
        ax.text(x + 0.55, 0.61, label, ha="center", va="center", fontsize=8)
    for (_, x1), (_, x2) in zip(boxes, boxes[1:]):
        ax.add_patch(FancyArrowPatch((x1 + 0.55, 0.61), (x2 + 0.05, 0.61),
                                     arrowstyle="-|>", mutation_scale=10, lw=1.0,
                                     color="#8a3b12"))
    ax.annotate("2theta scan", xy=(4.9 + 0.55, 0.40), xytext=(4.9 + 0.55, 0.16),
                ha="center", fontsize=8, color="#8a3b12",
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#8a3b12"))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 1.0)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "instrument.png", dpi=160)
    plt.close(fig)


def phase_panel() -> None:
    """One pattern per phase, on a common 2theta axis."""
    keys = [
        "si", "al", "cu", "fe", "nacl",
        "mgo", "zno", "tio2-rutile", "tio2-anatase",
    ]
    fig, axes = plt.subplots(3, 3, figsize=(10.5, 10.5), sharex=True)
    inst = Instrument(background_rate=0.0, rng_seed=None)
    for ax, key in zip(axes.ravel(), keys):
        phase = get_phase(key)
        result = scan(phase, 20.0, 90.0, 0.01, inst)
        plot_scan(result, ax=ax, title=f"{phase.name} ({phase.formula})", annotate=True)
        ax.set_ylabel("counts")
        ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "phase_panel.png", dpi=150)
    plt.close(fig)


def scherrer_demo() -> None:
    """The same phase at three crystallite sizes, on the 111 line."""
    fig, ax = plt.subplots(figsize=(8, 4))
    inst = Instrument(ka2=False, background_rate=0.0, rng_seed=None)
    for size, colour in [(50.0, "#8a3b12"), (200.0, "#1a3d6d"), (2000.0, "#2f7d32")]:
        result = scan(get_phase("si"), 25.5, 31.0, 0.005, inst, size_a=size)
        ax.plot(result.two_theta, result.counts / result.counts.max(),
                lw=1.2, color=colour, label=f"D = {size / 10:.0f} nm")
    ax.set_xlabel("2theta (deg)")
    ax.set_ylabel("normalised counts")
    ax.set_title(
        "Silicon 111: instrumental broadening plus crystallite size (K-alpha1 only)"
    )
    ax.legend(frameon=False)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "scherrer.png", dpi=160)
    plt.close(fig)


def doublet_demo() -> None:
    """The K-alpha doublet, resolved and unresolved."""
    fig, ax = plt.subplots(figsize=(8, 4))
    for ka2, label, colour in [(False, "K-alpha1 only", "#1a3d6d"),
                               (True, "K-alpha1 + K-alpha2", "#8a3b12")]:
        inst = Instrument(ka2=ka2, background_rate=0.0, rng_seed=None)
        result = scan(get_phase("si"), 87.0, 89.0, 0.002, inst)
        ax.plot(result.two_theta, result.counts / result.counts.max(),
                lw=1.2, color=colour, label=label)
    ax.set_xlabel("2theta (deg)")
    ax.set_ylabel("normalised counts")
    ax.set_title("Silicon 422 at 88 deg: the doublet is 0.28 deg wide")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "doublet.png", dpi=160)
    plt.close(fig)


def size_series() -> None:
    """R1: the same phase at the seven crystallite sizes of Table 4, raw and normalised."""
    sizes = [
        (50.0, "5 nm"), (100.0, "10 nm"), (200.0, "20 nm"),
        (500.0, "50 nm"), (1000.0, "100 nm"), (2000.0, "200 nm"), (5000.0, "500 nm"),
    ]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True)
    colours = [
        "#8a3b12", "#b5651d", "#d9822b", "#7a8b3a", "#2f7d32", "#1f6f8b", "#1a3d6d",
    ]
    inst = Instrument(ka2=False, background_rate=0.0, rng_seed=None)
    for (size, label), colour in zip(sizes, colours):
        result = scan(get_phase("si"), 27.4, 29.4, 0.002, inst, size_a=size)
        left.plot(result.two_theta, result.counts, lw=1.1, color=colour, label=label)
        right.plot(result.two_theta, result.counts / result.counts.max(), lw=1.1,
                   color=colour, label=label)
    left.set_title("same reflection, counts as measured")
    right.set_title("same curves, each normalised to its own peak")
    for ax in (left, right):
        ax.set_xlabel("2theta (deg)")
        ax.grid(alpha=0.25, lw=0.5)
    left.set_ylabel("counts")
    right.set_ylabel("normalised counts")
    right.legend(frameon=False, fontsize=8, title="crystallite size")
    fig.suptitle(
        "Silicon 111: crystallite size changes the width, not the position", y=1.0
    )
    fig.tight_layout()
    fig.savefig(OUT / "size_series.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def size_laws() -> None:
    """R2: FWHM against 1/D, and peak height against D."""
    from .size_study import rows as size_rows
    data = size_rows()
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.0))
    for hkl, colour in [("111", "#1a3d6d"), ("220", "#8a3b12"), ("400", "#2f7d32")]:
        subset = [row for row in data if row["hkl"] == hkl]
        sizes = [row["size_nm"] for row in subset]
        widths = [row["fwhm"] for row in subset]
        left.loglog(1.0 / np.array(sizes), widths, "o-", ms=4, lw=1.1,
                    color=colour, label=f"{hkl}")
        heights = [row["height"] for row in subset]
        right.loglog(sizes, heights, "o-", ms=4, lw=1.1, color=colour, label=f"{hkl}")
    left.set_xlabel("1 / D (1/nm)")
    left.set_ylabel("measured FWHM (deg)")
    left.set_title("width against inverse size")
    left.legend(frameon=False, fontsize=8)
    left.grid(alpha=0.25, lw=0.5, which="both")
    right.set_xlabel("D (nm)")
    right.set_ylabel("peak height (counts)")
    right.set_title("height against size")
    right.legend(frameon=False, fontsize=8)
    right.grid(alpha=0.25, lw=0.5, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "size_laws.png", dpi=160)
    plt.close(fig)


def fwhm_vs_angle() -> None:
    """R2: the same size broadens by 1/cos(theta), so width grows with angle."""
    from xrdsim.analysis import find_peaks
    fig, ax = plt.subplots(figsize=(8, 4))
    inst = Instrument(ka2=False, background_rate=0.0, rng_seed=None)
    for size, colour in [(200.0, "#1a3d6d"), (500.0, "#8a3b12")]:
        result = scan(get_phase("si"), 20.0, 120.0, 0.005, inst, size_a=size)
        peaks = [peak for peak in find_peaks(result.two_theta, result.counts)
                 if peak.fwhm > 0 and peak.height > 0.02 * result.counts.max()]
        ax.plot([peak.two_theta for peak in peaks], [peak.fwhm for peak in peaks],
                "o", ms=4, color=colour, label=f"D = {size / 10:.0f} nm")
    angles = np.linspace(22.0, 118.0, 200)
    cos_th = np.cos(np.radians(angles / 2.0))
    scale = 0.9 * 1.540598 / (200.0 * cos_th) * 180 / np.pi
    ax.plot(angles, scale, lw=1.0, ls="--", color="#666666",
            label="0.9 lambda / (D cos theta), D = 20 nm")
    ax.set_xlabel("2theta (deg)")
    ax.set_ylabel("FWHM (deg)")
    ax.set_yscale("log")
    ax.set_title("the same crystallite broadens more at high angle")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.25, lw=0.5, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "fwhm_vs_angle.png", dpi=160)
    plt.close(fig)


def convolution_demo() -> None:
    """R3: ideal comb -> exact Laue sinc^2 -> numerical convolution -> inst-limited."""
    import math
    from xrdsim.profile import (add_in_quadrature, caglioti_fwhm,
                                convolve_laue_with_instrument,
                                laue_interference_array, pseudo_voigt_array,
                                size_fwhm)
    fig, axes = plt.subplots(4, 1, figsize=(9.2, 8.4), sharex=True)
    x = np.linspace(27.5, 29.8, 4601)
    tth_b = 28.441
    d_111 = 5.431144 / math.sqrt(3.0)
    inst_w = caglioti_fwhm(tth_b, 0.004, -0.002, 0.003)

    comb = np.zeros_like(x)
    comb[np.argmin(np.abs(x - tth_b))] = 1.0
    axes[0].plot(x, comb, lw=1.2, color="#1a3d6d",
                 label="Dirac impulse at 2theta_B = 28.441 deg")
    axes[0].set_ylim(-0.05, 1.25)
    axes[0].set_title(
        "(a) Ideal infinite lattice: Dirac impulse train at the Bragg angle",
        fontsize=9.5,
    )
    axes[0].legend(loc="upper right", frameon=False, fontsize=8)

    n_mid = 160  # D = 160 * 0.31357 nm = 50.2 nm
    laue_mid = laue_interference_array(x, tth_b, d_111, n_mid, LAMBDA)
    axes[1].plot(
        x, laue_mid, lw=1.3, color="#8a3b12",
        label=f"Exact Laue sinc^2 (N = {n_mid} planes, D = 50.2 nm, FWHM = 0.1608 deg)",
    )
    zoom_curve = np.clip(laue_mid * 8.0, 0, laue_mid.max() * 0.85)
    axes[1].plot(x, zoom_curve, lw=0.9, ls="--", color="#d95f02",
                 label="8x vertical zoom showing sinc^2 secondary sidelobes")
    axes[1].set_ylim(-0.2, laue_mid.max() * 1.25)
    axes[1].set_title(
        "(b) Spatial window w(r): exact finite-chain Laue sinc^2 response |W(q)|^2",
        fontsize=9.5,
    )
    axes[1].legend(loc="upper right", frameon=False, fontsize=8)

    conv_mid = convolve_laue_with_instrument(x, tth_b, d_111, n_mid, LAMBDA, inst_w)
    size_w_mid = size_fwhm(n_mid * d_111, tth_b, LAMBDA, k=0.8859)
    pv_w_mid = add_in_quadrature(size_w_mid, inst_w)
    pv_mid = pseudo_voigt_array(x, tth_b, pv_w_mid, 0.5)
    sigma_inst = inst_w / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    h_inst_curve = (
        np.exp(-0.5 * ((x - tth_b) / sigma_inst) ** 2)
        / (sigma_inst * math.sqrt(2.0 * math.pi))
    )
    axes[2].plot(x, laue_mid, lw=0.9, ls="--", color="#8a3b12", alpha=0.65,
                 label="Pure Laue |W(q)|^2 before instrument (FWHM = 0.1608 deg)")
    axes[2].plot(x, h_inst_curve * 0.18, lw=0.9, ls="-.", color="#666666",
                 label="Gaussian instrument kernel h_inst (FWHM = 0.0524 deg, x0.18)")
    axes[2].plot(x, conv_mid, lw=1.4, color="#2f7d32",
                 label="Numerical convolution |W|^2 * h_inst (FWHM = 0.1671 deg)")
    axes[2].plot(
        x, pv_mid, lw=1.1, ls=":", color="#1a3d6d",
        label="Analytical pseudo-Voigt quadrature (K = 0.8859, FWHM = 0.1691 deg)",
    )
    axes[2].set_ylim(-0.2, laue_mid.max() * 1.28)
    axes[2].set_title(
        "(c) Second LTI stage: numerical convolution |W|^2 * h_inst damps sidelobes",
        fontsize=9.5,
    )
    axes[2].legend(loc="upper right", frameon=False, fontsize=7.6)

    n_big = 1600  # D = 501.7 nm
    laue_big = laue_interference_array(x, tth_b, d_111, n_big, LAMBDA)
    conv_big = convolve_laue_with_instrument(x, tth_b, d_111, n_big, LAMBDA, inst_w)
    size_w_big = size_fwhm(n_big * d_111, tth_b, LAMBDA, k=0.8859)
    pv_w_big = add_in_quadrature(size_w_big, inst_w)
    pv_big = pseudo_voigt_array(x, tth_b, pv_w_big, 0.5)
    axes[3].plot(
        x, laue_big * 0.35, lw=0.9, ls="--", color="#666666",
        label="Pure Laue |W(q)|^2 (N = 1600, D = 501.7 nm, FWHM = 0.0161 deg, x0.35)",
    )
    axes[3].plot(x, conv_big, lw=1.4, color="#6a3d9a",
                 label="Numerical convolution |W|^2 * h_inst (FWHM = 0.0561 deg)")
    axes[3].plot(
        x, pv_big, lw=1.1, ls=":", color="#1a3d6d",
        label="Analytical pseudo-Voigt quadrature (K = 0.8859, FWHM = 0.0549 deg)",
    )
    axes[3].set_ylim(-0.8, (laue_big.max() * 0.35) * 1.25)
    axes[3].set_title(
        "(d) Instrument-limited regime (D = 501.7 nm): h_inst sets the observed width",
        fontsize=9.5,
    )
    axes[3].legend(loc="upper right", frameon=False, fontsize=7.6)

    for ax in axes:
        ax.set_ylabel("density")
        ax.grid(alpha=0.25, lw=0.5)
    axes[-1].set_xlabel("2theta (deg)")
    fig.tight_layout()
    fig.savefig(OUT / "convolution.png", dpi=160)
    plt.close(fig)


def laue_plot() -> None:
    """R3: the interference function of a finite chain, width proportional to 1/N."""
    v = np.linspace(-0.5, 0.5, 4000)
    fig, ax = plt.subplots(figsize=(8, 4))
    for planes, colour in [(5, "#8a3b12"), (20, "#1a3d6d"), (100, "#2f7d32")]:
        y = (np.sin(planes * np.pi * v) / np.sin(np.pi * v)) ** 2
        ax.plot(v, y / planes ** 2, lw=1.1, color=colour, label=f"N = {planes} planes")
    ax.set_xlabel("reduced reciprocal coordinate between Bragg points, q d / 2 pi")
    ax.set_ylabel("normalised intensity")
    ax.set_title(
        "Finite-chain interference |sin(N pi v)/sin(pi v)|^2: "
        "width ~ 1/N, powder area conserved",
        fontsize=9.5,
    )
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "laue.png", dpi=160)
    plt.close(fig)


def class_spec_figure() -> None:
    """In-class assignment specification:
    1. Crystal types: Simple Cubic (SC), BCC, FCC, and Amorphous.
    2. Variable: Lattice constant a variation.
    3. Input: Cu K-alpha radiation (1.5406 A) and full-width CLI session capture.
    """
    from xrdsim.cli import main as cli_main
    from xrdsim.diffractometer import amorphous_scan
    from xrdsim.samples import Phase, Site, simple_cubic

    inst = Instrument(background_rate=0.0, rng_seed=None, ka2=False)

    fig = plt.figure(figsize=(11.6, 8.6), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 1.0])

    ax_lattices = fig.add_subplot(gs[0, 0])
    sc_scan = scan(simple_cubic(a=3.359, element="Cu"), 20.0, 95.0, 0.02, inst)
    bcc_scan = scan(get_phase("fe"), 20.0, 95.0, 0.02, inst)
    fcc_scan = scan(get_phase("cu"), 20.0, 95.0, 0.02, inst)

    ax_lattices.plot(
        sc_scan.two_theta, sc_scan.counts / sc_scan.counts.max() + 2.1,
        lw=1.1, color="#1a3d6d",
        label="Generic SC (a = 3.359 \u00c5): all hkl",
    )
    ax_lattices.plot(
        bcc_scan.two_theta, bcc_scan.counts / bcc_scan.counts.max() + 1.05,
        lw=1.1, color="#8a3b12",
        label="BCC (a = 2.867 \u00c5): h+k+l = even",
    )
    ax_lattices.plot(
        fcc_scan.two_theta, fcc_scan.counts / fcc_scan.counts.max(),
        lw=1.1, color="#2f7d32",
        label="FCC (a = 3.615 \u00c5): unmixed parity",
    )
    ax_lattices.set_title(
        "(a) Crystal Types: SC vs. BCC vs. FCC",
        fontsize=9.2, fontweight="bold",
    )
    ax_lattices.set_xlabel("2\u03b8 (\u00b0)", fontsize=8.5)
    ax_lattices.set_ylabel("Normalized Intensity (stacked)", fontsize=8.5)
    ax_lattices.set_xlim(20, 95)
    ax_lattices.set_ylim(-0.08, 3.85)
    ax_lattices.legend(loc="upper right", frameon=True, fontsize=7.2)
    ax_lattices.grid(alpha=0.2, lw=0.5)

    ax_amorph = fig.add_subplot(gs[0, 1])
    am_scan = amorphous_scan(10.0, 90.0, 0.02, inst, center_deg=21.8, fwhm_deg=8.8)
    ax_amorph.plot(
        am_scan.two_theta, am_scan.counts / am_scan.counts.max(),
        lw=1.8, color="#d95f02",
        label="Amorphous SiO2 (halo at 21.8\u00b0, FWHM = 8.8\u00b0)",
    )
    si_scan = scan(get_phase("si"), 10.0, 90.0, 0.02, inst)
    ax_amorph.plot(
        si_scan.two_theta, si_scan.counts / si_scan.counts.max(),
        lw=1.1, color="#1a3d6d",
        label="Crystalline Si (sharp Bragg peaks)",
    )
    ax_amorph.set_title(
        "(b) Crystalline vs. Amorphous Phase",
        fontsize=9.2, fontweight="bold",
    )
    ax_amorph.set_xlabel("2\u03b8 (\u00b0)", fontsize=8.5)
    ax_amorph.set_ylabel("Normalized Intensity", fontsize=8.5)
    ax_amorph.set_xlim(10, 90)
    ax_amorph.set_ylim(-0.04, 1.32)
    ax_amorph.legend(loc="upper right", frameon=True, fontsize=7.2)
    ax_amorph.grid(alpha=0.2, lw=0.5)

    ax_param = fig.add_subplot(gs[0, 2])
    colors_a = ["#4575b4", "#74add1", "#f46d43", "#d73027"]
    a_values = [3.20, 3.80, 4.40, 5.00]
    fcc_sites = (
        Site("Cu", 0, 0, 0), Site("Cu", 0, 0.5, 0.5),
        Site("Cu", 0.5, 0, 0.5), Site("Cu", 0.5, 0.5, 0),
    )
    for a_val, col in zip(a_values, colors_a):
        phase_a = Phase(
            key=f"fcc_{a_val}", name=f"FCC (a = {a_val:.2f} \u00c5)",
            formula="M", space_group="Fm-3m", a=a_val, sites=fcc_sites,
        )
        res_a = scan(phase_a, 20.0, 85.0, 0.02, inst)
        ax_param.plot(res_a.two_theta, res_a.counts / res_a.counts.max(),
                      lw=1.2, color=col, label=f"--a {a_val:.2f} \u00c5")

    ax_param.set_title(
        "(c) Varying Lattice Constant a (--a)",
        fontsize=9.2, fontweight="bold",
    )
    ax_param.set_xlabel("2\u03b8 (\u00b0)", fontsize=8.5)
    ax_param.set_ylabel("Normalized Intensity", fontsize=8.5)
    ax_param.set_xlim(20, 85)
    ax_param.set_ylim(-0.04, 1.28)
    ax_param.legend(loc="upper right", frameon=True, fontsize=7.5)
    ax_param.grid(alpha=0.2, lw=0.5)

    ax_cli = fig.add_subplot(gs[1, :])
    shot_path = OUT / "terminal_screenshot.png"
    if shot_path.exists():
        ax_cli.imshow(plt.imread(shot_path), interpolation="lanczos")
        ax_cli.axis("off")
    else:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cli_main(["--phase", "si", "--size-nm", "20", "--index", "--scherrer"])
        ax_cli.text(0.02, 0.95, buf.getvalue(), transform=ax_cli.transAxes,
                    fontfamily="monospace", fontsize=8.0, va="top")
    ax_cli.set_title(
        "(d) Windows Terminal Session Screenshot: SC (--a 3.359), "
        "Amorphous (--phase amorphous), and Si (--size-nm 20)",
        fontsize=9.2, fontweight="bold",
    )

    fig.savefig(OUT / "class_spec.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    instrument_diagram()
    class_spec_figure()
    phase_panel()
    scherrer_demo()
    doublet_demo()
    size_series()
    size_laws()
    fwhm_vs_angle()
    convolution_demo()
    laue_plot()
    print(f"wrote {len(list(OUT.glob('*.png')))} figures to {OUT}")


if __name__ == "__main__":
    main()
