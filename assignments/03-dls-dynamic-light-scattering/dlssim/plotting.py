"""One-page dashboard for a simulated measurement."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullLocator


def _plain_nm(value, _position):
    return f"{value:g}"


def dashboard(model, tau, g2_measured, fit, inversion, trace=None, path=None):
    """Draw correlation, photon trace and size distributions."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.2))

    ax = axes[0, 0]
    ax.semilogx(tau * 1e6, model.g2(tau), "-", lw=1.2, label="ideal")
    ax.semilogx(tau * 1e6, g2_measured, ".", ms=2.5, alpha=0.6, label="measured")
    ax.set_xlabel("delay time (us)")
    ax.set_ylabel("g2(tau)")
    ax.set_title(
        f"autocorrelation, z-average {float(fit.z_average_diameter_m) * 1e9:.1f} nm, "
        f"PDI {fit.pdi:.3f}"
    )
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    if trace is not None:
        ax.plot(trace, lw=0.7)
    ax.set_xlabel("sample")
    ax.set_ylabel("counts per bin")
    ax.set_title("photon count trace")

    ax = axes[1, 0]
    ax.axvspan(
        inversion.support_m[0] * 1e9,
        inversion.support_m[1] * 1e9,
        color="0.92",
        zorder=0,
        label="reported support",
    )
    ax.semilogx(inversion.diameters_m * 1e9, inversion.intensity_weights, lw=1.5, label="intensity")
    ax.semilogx(inversion.diameters_m * 1e9, inversion.number_weights, lw=1.5, label="number")
    ax.axvline(model.diameter_m * 1e9, color="0.5", ls=":", lw=1, label="input median")
    ax.set_xlabel("diameter (nm)")
    ax.set_ylabel("normalised weight")
    ax.set_title("recovered distribution")
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    population = model.population
    x = population.diameters_m * 1e9
    ax.semilogx(x, population.number_weights, lw=1.5, label="true number")
    ax.semilogx(x, population.intensity_weights(model.contrast), lw=1.5, label="true intensity")
    ax.set_xlim(x.min() / 2, x.max() * 2)
    ax.set_xlabel("diameter (nm)")
    ax.set_ylabel("normalised weight")
    ax.set_title("input population")
    ax.xaxis.set_major_formatter(FuncFormatter(_plain_nm))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.legend(fontsize=8)

    fig.tight_layout()
    if path is not None:
        fig.savefig(Path(path), dpi=150)
        plt.close(fig)
    return fig
