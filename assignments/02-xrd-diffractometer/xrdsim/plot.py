"""Matplotlib rendering of a scan.

A scan is drawn as counts against 2theta, with the reflections the model predicts
marked clearly above each peak.
"""

from __future__ import annotations

import matplotlib
import numpy as np

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from .diffractometer import Scan


def plot_scan(scan: Scan, ax=None, title: str | None = None, annotate: bool = True):
    """Draw one scan; returns the axes."""
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(scan.two_theta, scan.counts, lw=0.85, color="#1a3d6d")
    y_max = float(scan.counts.max()) if len(scan.counts) else 1.0
    ax.set_ylim(-0.03 * y_max, 1.22 * y_max)
    if annotate and scan.reflections:
        strongest = max(row.intensity for row in scan.reflections)
        placed: list[float] = []
        for row in sorted(scan.reflections, key=lambda r: -r.intensity):
            if row.intensity < 0.10 * strongest:
                continue
            if not (scan.two_theta[0] <= row.two_theta <= scan.two_theta[-1]):
                continue
            if any(abs(row.two_theta - angle) < 2.2 for angle in placed):
                continue
            placed.append(row.two_theta)
            idx = int(np.argmin(np.abs(scan.two_theta - row.two_theta)))
            y_pos = min(float(scan.counts[idx]), 0.94 * y_max)
            ax.annotate("".join(str(v) for v in row.hkl), (row.two_theta, y_pos),
                        textcoords="offset points", xytext=(0, 3),
                        fontsize=8.0, fontweight="bold", ha="center", va="bottom",
                        color="#8a3b12")
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
