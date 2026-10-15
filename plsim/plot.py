"""Matplotlib rendering of a simulated PL scan."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

TRACE_COLOR = "#1f4e9c"
SCATTER_COLOR = "#c1440e"
EXC_COLOR = "#555555"


def plot_scan(scan, path=None, show=False):
    """Draw one PL scan. Returns the figure."""
    power = scan.detected_power
    scale = float(power.max())
    if scale <= 0.0:
        scale = 1.0

    fig, ax = plt.subplots(figsize=(9.0, 5.6), dpi=140)
    ax.plot(
        scan.wavelengths_nm,
        power / scale,
        color=TRACE_COLOR,
        lw=1.8,
        label="detected PL spectrum",
    )
    if scan.scatter_power.max() > 1e-3 * scale:
        ax.plot(
            scan.wavelengths_nm,
            scan.scatter_power / scale,
            color=SCATTER_COLOR,
            lw=1.2,
            ls=":",
            label="stray excitation light",
        )
    ax.axvline(
        scan.lambda_exc_nm,
        color=EXC_COLOR,
        lw=1.0,
        ls="--",
        label="excitation {:g} nm".format(scan.lambda_exc_nm),
    )
    peak_nm = scan.emission_peak_nm
    ax.plot([peak_nm], [1.0], marker="o", ms=4.0, color=TRACE_COLOR)
    ax.annotate(
        "PL peak {:.0f} nm".format(peak_nm),
        xy=(peak_nm, 1.0),
        xytext=(peak_nm + 8.0, 0.92),
        fontsize=9,
        color=TRACE_COLOR,
    )

    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("photocurrent (norm.)")
    ax.set_ylim(0.0, 1.15)
    ax.set_xlim(scan.wavelengths_nm[0], scan.wavelengths_nm[-1])
    ax.grid(alpha=0.25, lw=0.6)
    ax.set_title(
        "{} — PL spectrum, excitation {:g} nm".format(scan.sample_name, scan.lambda_exc_nm)
    )

    settings = (
        "sample: {}\n"
        "excitation: {:g} nm\n"
        "detection range: {:g} - {:g} nm\n"
        "step size: {:g} nm\n"
        "stray excitation: {:g} of excitation power"
    ).format(
        scan.sample_name,
        scan.lambda_exc_nm,
        scan.wavelengths_nm[0],
        scan.wavelengths_nm[-1],
        float(scan.wavelengths_nm[1] - scan.wavelengths_nm[0]),
        scan.scatter_fraction,
    )
    ax.text(
        0.985,
        0.95,
        settings,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        family="monospace",
        bbox=dict(boxstyle="round", fc="white", ec="#bbbbbb", alpha=0.9),
    )
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    fig.tight_layout()

    if path is not None:
        fig.savefig(path)
    if show:
        plt.show()
    return fig
