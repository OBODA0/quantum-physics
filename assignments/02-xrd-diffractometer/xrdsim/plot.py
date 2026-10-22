"""Matplotlib rendering of a scan.

Assignment 1 already fixed the house style: a scan is drawn as counts against 2theta,
with the reflections the model predicts marked, and nothing decorated that the data do
not carry.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from .diffractometer import Scan


def plot_scan(scan: Scan, ax=None, title: str | None = None, annotate: bool = True):
    """Draw one scan; returns the axes."""
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(scan.two_theta, scan.counts, lw=0.8, color="#1a3d6d")
    if annotate and scan.reflections:
        strongest = max(row.intensity for row in scan.reflections)
        for row in scan.reflections:
            if row.intensity < 0.02 * strongest:
                continue
            ax.annotate("".join(str(v) for v in row.hkl), (row.two_theta, 0),
                        textcoords="offset points", xytext=(0, 6),
                        fontsize=7, ha="center", color="#8a3b12")
    ax.set_xlabel("2theta (deg)")
    ax.set_ylabel("counts")
    if title:
        ax.set_title(title)
    ax.grid(alpha=0.25, lw=0.5)
    return ax


def save_scan(scan: Scan, path, title: str | None = None, dpi: int = 160) -> None:
    """Write one scan to an image file."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    plot_scan(scan, ax=ax, title=title or (scan.phase.name if scan.phase else None))
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def plot_overview(scans, path, dpi: int = 160) -> None:
    """One panel per scan, stacked."""
    fig, axes = plt.subplots(len(scans), 1, figsize=(9, 3.0 * len(scans)), sharex=True)
    if len(scans) == 1:
        axes = [axes]
    for ax, scan in zip(axes, scans):
        plot_scan(scan, ax=ax, title=scan.phase.name if scan.phase else None)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
