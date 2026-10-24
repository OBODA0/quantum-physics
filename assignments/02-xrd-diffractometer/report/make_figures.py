"""Figures for the assignment 2 report.

Every figure here is written straight from the simulator, so a figure cannot drift from
the model. Run it with:

    uv run python -m report.make_figures
"""

from __future__ import annotations

import pathlib

import numpy as np
import matplotlib

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
        ax.add_patch(Rectangle((x, 0.40), 1.1, 0.42, fill=False, lw=1.2, color="#1a3d6d"))
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
    keys = ["si", "al", "cu", "fe", "nacl", "mgo", "zno", "tio2-rutile", "tio2-anatase"]
    fig, axes = plt.subplots(3, 3, figsize=(10.5, 10.5), sharex=True)
    for ax, key in zip(axes.ravel(), keys):
        phase = get_phase(key)
        result = scan(phase, 20.0, 90.0, 0.01, Instrument(background_rate=0.0, rng_seed=None))
        plot_scan(result, ax=ax, title=f"{phase.name} ({phase.formula})", annotate=True)
        ax.set_ylabel("counts")
        ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "phase_panel.png", dpi=150)
    plt.close(fig)


def scherrer_demo() -> None:
    """The same phase at three crystallite sizes, on the 111 line."""
    fig, ax = plt.subplots(figsize=(8, 4))
    for size, colour in [(50.0, "#8a3b12"), (200.0, "#1a3d6d"), (2000.0, "#2f7d32")]:
        result = scan(get_phase("si"), 25.5, 31.0, 0.005,
                      Instrument(ka2=False, background_rate=0.0, rng_seed=None), size_a=size)
        ax.plot(result.two_theta, result.counts / result.counts.max(),
                lw=1.2, color=colour, label=f"D = {size / 10:.0f} nm")
    ax.set_xlabel("2theta (deg)")
    ax.set_ylabel("normalised counts")
    ax.set_title("Silicon 111: instrumental broadening plus crystallite size (K-alpha1 only)")
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
        result = scan(get_phase("si"), 87.0, 89.0, 0.002,
                      Instrument(ka2=ka2, background_rate=0.0, rng_seed=None))
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
    """R1: the same phase at six crystallite sizes, raw and normalised."""
    sizes = [(50.0, "5 nm"), (100.0, "10 nm"), (250.0, "25 nm"),
             (500.0, "50 nm"), (1000.0, "100 nm"), (5000.0, "500 nm")]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True)
    colours = ["#8a3b12", "#b5651d", "#c98a2b", "#7a8b3a", "#2f7d32", "#1a3d6d"]
    for (size, label), colour in zip(sizes, colours):
        result = scan(get_phase("si"), 27.4, 29.4, 0.002,
                      Instrument(ka2=False, background_rate=0.0, rng_seed=None), size_a=size)
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
    fig.suptitle("Silicon 111: crystallite size changes the width, not the position", y=1.0)
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
        left.loglog(1.0 / np.array(sizes), widths, "o-", ms=4, lw=1.1, color=colour, label=f"{hkl}")
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
    for size, colour in [(200.0, "#1a3d6d"), (500.0, "#8a3b12")]:
        result = scan(get_phase("si"), 20.0, 120.0, 0.005,
                      Instrument(ka2=False, background_rate=0.0, rng_seed=None), size_a=size)
        peaks = [peak for peak in find_peaks(result.two_theta, result.counts)
                 if peak.fwhm > 0 and peak.height > 0.02 * result.counts.max()]
        ax.plot([peak.two_theta for peak in peaks], [peak.fwhm for peak in peaks],
                "o", ms=4, color=colour, label=f"D = {size / 10:.0f} nm")
    angles = np.linspace(22.0, 118.0, 200)
    scale = 0.9 * 1.540598 / (200.0 * np.cos(np.radians(angles / 2.0))) * 180 / np.pi
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
    """R3: ideal comb -> size response -> instrument response -> instrument-limited."""
    fig, axes = plt.subplots(4, 1, figsize=(9, 8.0), sharex=True)
    x = np.linspace(27.4, 29.4, 2000)
    comb = np.zeros_like(x)
    comb[np.argmin(np.abs(x - 28.441))] = 1.0 / (x[1] - x[0])
    axes[0].plot(x, comb, lw=1.0, color="#1a3d6d")
    axes[0].set_title("ideal crystal: a line at the Bragg angle")
    for ax, size, label, colour in [
            (axes[1], 200.0, "40 nm crystallite, size broadening only (narrow instrument)", "#8a3b12"),
            (axes[2], 200.0, "same crystal seen through the real instrument: a second convolution", "#2f7d32"),
            (axes[3], 5000.0, "500 nm crystallite: the instrument now sets the width", "#6a3d9a")]:
        instrument = Instrument(ka2=False, background_rate=0.0, rng_seed=None,
                                caglioti=((0.0, 0.0, 0.0001) if ax is axes[1]
                                          else (0.004, -0.002, 0.003)))
        result = scan(get_phase("si"), 27.4, 29.4, 0.002, instrument, size_a=size)
        ax.plot(result.two_theta, result.counts, lw=1.2, color=colour)
        ax.set_title(label)
    for ax in axes:
        ax.set_ylabel("intensity")
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
    ax.set_title("the finite chain: width ~ 1/N, height ~ N^2, area constant")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "laue.png", dpi=160)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    instrument_diagram()
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
