"""Figures for the assignment 2 report.

Every figure here is written straight from the simulator, so a figure cannot drift from
the model. Run it with:

    uv run python report/make_figures.py
"""

from __future__ import annotations

import pathlib

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
    fig, axes = plt.subplots(3, 3, figsize=(11, 7.5), sharex=True)
    for ax, key in zip(axes.ravel(), keys):
        phase = get_phase(key)
        result = scan(phase, 20.0, 90.0, 0.01, Instrument(background_rate=0.0, rng_seed=None))
        plot_scan(result, ax=ax, title=f"{phase.name} ({phase.formula})", annotate=True)
        ax.set_ylabel("counts")
    fig.tight_layout()
    fig.savefig(OUT / "phase_panel.png", dpi=150)
    plt.close(fig)


def scherrer_demo() -> None:
    """The same phase at three crystallite sizes, on the 111 line."""
    fig, ax = plt.subplots(figsize=(8, 4))
    for size, colour in [(50.0, "#8a3b12"), (200.0, "#1a3d6d"), (2000.0, "#2f7d32")]:
        result = scan(get_phase("si"), 27.5, 29.0, 0.002,
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    instrument_diagram()
    phase_panel()
    scherrer_demo()
    doublet_demo()
    print(f"wrote {len(list(OUT.glob('*.png')))} figures to {OUT}")


if __name__ == "__main__":
    main()
