"""Every figure in the assignment 3 report, drawn from the simulator.

    uv run python -m report.make_figures

The only images this module does not draw are ``figures/gui_screenshot.png`` (a capture of
the real Tk GUI, produced by ``report/capture_gui.py`` and checked in, because a screen
capture is not reproducible pixel-for-pixel) and the terminal transcript, which is rendered
here from the output of the CLI itself.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from dlssim.cli import format_terminal_report
from dlssim.plot import plot_dls_dashboard

from .cases import (ALPHA_FIGURE, BASE, PDI_LIMIT, RI_SWEEP, SIGMA_FIGURE,
                    SIZES_FIGURE_NM, SOLVENTS, TEMPERATURES_C, run)
from .tables import aggregation_rows, polydispersity_rows, refractive_index_rows, solvent_rows
from .size_study import rows as size_rows

HERE = pathlib.Path(__file__).resolve().parent
FIG = HERE / "figures"
FIG.mkdir(parents=True, exist_ok=True)

MONO = "#2563eb"
CLUSTER = "#dc2626"
RECOVERED = "#9333ea"
NUMBER = "#16a34a"
INK = "#1f2937"
GRID = dict(alpha=0.28, lw=0.6)
SIZE_COLOURS = ["#0ea5e9", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0f766e"]

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "legend.fontsize": 7.6,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "axes.edgecolor": "#4b5563",
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def _save(fig, name: str) -> pathlib.Path:
    path = FIG / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path.name}")
    return path


# --------------------------------------------------------------------------- figure 1
def measurement_chain() -> pathlib.Path:
    """The optical bench and the signal chain, drawn as a block diagram."""
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 74)
    ax.axis("off")

    def box(x, y, w, h, text, face="#eef2ff", edge="#3730a3", size=7.4):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.2",
                                    linewidth=1.0, facecolor=face, edgecolor=edge))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
                linespacing=1.5)

    def arrow(x1, y1, x2, y2, text="", colour="#374151", size=6.8, offset=(0, 1.2)):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9,
                                     lw=1.1, color=colour))
        if text:
            ax.text((x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1], text,
                    ha="center", va="bottom", fontsize=size, color=colour)

    # ---- (a) optics
    ax.text(0.5, 70.6, "(a) the optical bench the simulator models", fontsize=8.4,
            fontweight="bold", color="#1b365d")
    box(1, 53, 13, 13, "He-Ne laser\n632.8 nm", "#fef3c7", "#b45309")
    box(19, 51.5, 19, 16, "cuvette, 10 mm\nparticles in solvent\n$n_s(T)$, $\\eta(T)$",
        "#dcfce7", "#15803d")
    box(44, 54, 12, 11, "beam stop", "#f3f4f6", "#4b5563")
    box(19, 31, 14, 12, "detector\n$\\theta = 173^\\circ$", "#fee2e2", "#b91c1c")
    box(38, 31, 15, 12, "photon counter\nand correlator", "#e0e7ff", "#3730a3")

    arrow(14, 59.5, 19, 59.5)
    arrow(38, 59.5, 44, 59.5)
    arrow(26, 51.5, 26, 43.2)
    ax.text(27.4, 47.4, "scattered at $\\theta$", fontsize=6.8, color="#b91c1c", va="bottom")
    arrow(33.6, 37, 38, 37)
    ax.text(70.0, 40.0, "$q=\\dfrac{4\\pi n_s}{\\lambda_0}\\sin\\dfrac{\\theta}{2}$",
            fontsize=9.0, ha="center", va="center")
    ax.text(70.0, 30.5, "$\\Gamma = D q^2$,\u2003$D = k_BT/(3\\pi\\eta d)$",
            fontsize=8.6, ha="center", va="center")
    ax.text(86, 59.5, "transmitted beam", fontsize=6.8, color="#6b7280", va="center")
    arrow(56.6, 59.5, 84, 59.5, colour="#9ca3af")

    # ---- (b) signal chain
    ax.text(0.5, 22.0, "(b) the signal chain: what is computed from what the bench measures",
            fontsize=8.4, fontweight="bold", color="#1b365d")
    box(1, 4, 15, 13, "photon counts\n$I(t)$, speckle", "#f0f9ff", "#0369a1")
    box(19, 4, 17, 13, "auto-correlation\n$g_2(\\tau)-1=\\beta|g_1|^2$\nlog lag axis",
        "#f0f9ff", "#0369a1")
    box(39, 10.5, 19, 9.5, "cumulant fit\n$\\bar{\\Gamma}$, $\\mu_2$", "#fdf4ff", "#86198f")
    box(39, 0.5, 19, 9.5, "regularised\ninversion", "#fdf4ff", "#86198f")
    box(62, 10.5, 20, 9.5, "number and intensity\ndistributions", "#f0fdf4", "#15803d")
    box(62, 0.5, 20, 9.5, "$z$-average, PDI,\nverdict", "#f0fdf4", "#15803d")
    arrow(16, 10.5, 19, 10.5)
    arrow(36, 12.5, 39, 15)
    arrow(36, 8.5, 39, 6)
    arrow(58, 15.2, 62, 15.2)
    arrow(58, 5.2, 62, 5.2)

    return _save(fig, "fig_chain.png")


# --------------------------------------------------------------------------- figure 3
def base_dashboard() -> pathlib.Path:
    """The 4-panel dashboard of the base case, exactly as the CLI draws it."""
    outputs = run(**BASE)
    fig = plot_dls_dashboard(outputs, out_path=None, dpi=200)
    path = FIG / "fig_dashboard.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path.name}")
    return path


# --------------------------------------------------------------------------- figure 4
def cli_transcript() -> pathlib.Path:
    """Render the CLI's own output to an image: this is the program talking, not a mock-up."""
    import os

    commands = [
        ["--solvent", "water", "--ri", "1.59", "--size-nm", "50", "--sigma", "0.12",
         "--aggregation", "0.08", "--temp-c", "25", "--out", ""],
        ["--solvent", "ethanol", "--size-nm", "120", "--sigma", "0.10",
         "--aggregation", "0.25", "--temp-c", "25", "--out", ""],
        ["--list-solvents"],
    ]
    chunks = []
    for arguments in commands:
        chunks.append("$ uv run python -m dlssim " + " ".join(arguments))
        result = subprocess.run([sys.executable, "-m", "dlssim", *arguments],
                                capture_output=True, text=True, cwd=str(HERE.parent),
                                env={**os.environ, "MPLBACKEND": "Agg"})
        chunks.append((result.stdout + result.stderr).rstrip())
        chunks.append("")
    text = "\n".join(chunks)

    lines = text.splitlines()
    width_in, font_pt, spacing = 7.4, 6.0, 1.22
    line_height_in = font_pt * spacing / 72.0
    height_in = 0.35 + line_height_in * len(lines)
    fig = plt.figure(figsize=(width_in, height_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="#0b1220", edgecolor="none"))
    ax.text(0.008, 1.0 - 0.12 * line_height_in / height_in, "\n".join(lines),
            family="monospace", fontsize=font_pt, va="top", ha="left", color="#d1e9ff",
            transform=ax.transAxes, linespacing=spacing)
    return _save(fig, "fig_cli.png")


# --------------------------------------------------------------------------- figure 5
def size_series() -> pathlib.Path:
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2))
    ax_corr, ax_dist, ax_tau = axes
    data = {row["size_nm"]: row for row in size_rows()}
    for colour, size in zip(SIZE_COLOURS, SIZES_FIGURE_NM):
        outputs = run(size_nm=size, size_std_rel=0.10, aggregation=0.0)
        ac = outputs.autocorrelation
        ax_corr.semilogx(ac.tau_s, ac.g2_minus_1, color=colour, lw=1.5,
                         label=f"{size:.0f} nm")
        dist = outputs.distribution
        ax_dist.semilogx(dist.diameter_nm, dist.intensity_dist / dist.intensity_dist.max(),
                         color=colour, lw=1.5)
        rec = outputs.recovered
        ax_dist.semilogx(rec.diameter_nm, rec.intensity_dist / rec.intensity_dist.max(),
                         color=colour, lw=1.5, ls=":")
    ax_corr.set_xlabel("lag time $\\tau$ (s)")
    ax_corr.set_ylabel("$g_2(\\tau)-1$")
    ax_corr.set_title("(a) the correlation decays faster\nfor smaller particles", fontsize=8.6)
    ax_corr.grid(True, which="both", **GRID)
    ax_corr.legend(title="primary diameter", title_fontsize=7.2, loc="upper right")
    ax_corr.set_ylim(-0.04, 0.95)

    ax_dist.set_xlim(3, 2000)
    ax_dist.set_xlabel("diameter $d$ (nm)")
    ax_dist.set_ylabel("intensity distribution (norm.)")
    ax_dist.set_title("(b) truth (solid) and inversion (dotted):\nsame mode, no second mode", fontsize=8.6)
    ax_dist.grid(True, which="both", **GRID)

    diameters = np.array([row_["size_nm"] for row_ in size_rows()])
    taus = np.array([row_["tau_c_ms"] for row_ in size_rows()])
    ax_tau.loglog(diameters, taus, "o-", color=INK, ms=4, lw=1.2, label="measured $\\tau_c$")
    guide = taus[0] * diameters / diameters[0]
    ax_tau.loglog(diameters, guide, "--", color="#9ca3af", lw=1.0, label="$\\tau_c \\propto d$")
    ax_tau.set_xlabel("primary diameter $d_0$ (nm)")
    ax_tau.set_ylabel("$\\tau_c = 1/\\bar{\\Gamma}$ (ms)")
    ax_tau.set_title("(c) one decade of size,\none decade of decay time", fontsize=8.6)
    ax_tau.grid(True, which="both", **GRID)
    ax_tau.legend(loc="upper left")
    fig.tight_layout()
    return _save(fig, "fig_size_series.png")


# --------------------------------------------------------------------------- figure 6
def polydispersity_series() -> pathlib.Path:
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2))
    ax_corr, ax_pdi, ax_dist = axes
    for colour, sigma in zip(["#0ea5e9", "#f59e0b", "#dc2626"], SIGMA_FIGURE):
        outputs = run(size_nm=100.0, size_std_rel=sigma, aggregation=0.0)
        ax_corr.loglog(outputs.autocorrelation.tau_s,
                       np.clip(outputs.autocorrelation.g2_minus_1, 1e-6, None),
                       color=colour, lw=1.5, label=f"$\\sigma/d$ = {sigma:.2f}")
        dist = outputs.distribution
        ax_dist.semilogx(dist.diameter_nm, dist.intensity_dist / dist.intensity_dist.max(),
                         color=colour, lw=1.5, label=f"$\\sigma/d$ = {sigma:.2f}")
        rec = outputs.recovered
        ax_dist.semilogx(rec.diameter_nm, rec.intensity_dist / rec.intensity_dist.max(),
                         color=colour, lw=1.3, ls=":")
    ax_corr.set_xlim(1e-5, 1e-2)
    ax_corr.set_ylim(1e-5, 1.2)
    ax_corr.set_xlabel("lag time $\\tau$ (s)")
    ax_corr.set_ylabel("$g_2(\\tau)-1$")
    ax_corr.set_title("(a) a monodisperse decay is a straight\nline here; width bends it", fontsize=8.6)
    ax_corr.grid(True, which="both", **GRID)
    ax_corr.legend(loc="lower left")

    rows_ = polydispersity_rows()
    sigmas = np.array([r["sigma_rel"] for r in rows_])
    pdis = np.array([r["pdi"] for r in rows_])
    ax_pdi.plot(sigmas, pdis, "o-", color=INK, ms=4, lw=1.2, label="PDI from the fit")
    ax_pdi.plot(sigmas, 2.0 * sigmas ** 2, "--", color="#9ca3af", lw=1.0,
                label="2$(\\sigma/d)^2$")
    ax_pdi.axhline(PDI_LIMIT, color="#b91c1c", ls=":", lw=1.0)
    ax_pdi.text(0.015, PDI_LIMIT + 0.005, "class criterion 0.2", fontsize=6.8,
                color="#b91c1c", ha="left")
    ax_pdi.set_xlabel("input $\\sigma/d$")
    ax_pdi.set_ylabel("PDI $=2\\mu_2/\\bar{\\Gamma}^2$")
    ax_pdi.set_title("(b) PDI tracks $2(\\sigma/d)^2$; a 30 % width\nstill passes the 0.2 test", fontsize=8.6)
    ax_pdi.grid(True, **GRID)
    ax_pdi.legend(loc="lower right")
    ax_pdi.set_ylim(0, 0.22)

    ax_dist.set_xlim(40, 400)
    ax_dist.set_xlabel("diameter $d$ (nm)")
    ax_dist.set_ylabel("intensity distribution (norm.)")
    ax_dist.set_title("(c) the inversion follows the width\n(solid truth, dotted recovered)", fontsize=8.6)
    ax_dist.grid(True, which="both", **GRID)
    ax_dist.legend(loc="upper right")
    ax_dist.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    fig.tight_layout()
    return _save(fig, "fig_polydispersity.png")


# --------------------------------------------------------------------------- figure 7
def aggregation_series() -> pathlib.Path:
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2))
    ax_corr, ax_dist, ax_pdi = axes
    colours = {0.0: "#0ea5e9", 0.10: "#f59e0b", 0.30: "#dc2626"}
    for alpha in ALPHA_FIGURE:
        outputs = run(size_nm=100.0, size_std_rel=0.10, aggregation=alpha)
        ax_corr.loglog(outputs.autocorrelation.tau_s,
                       np.clip(outputs.autocorrelation.g2_minus_1, 1e-7, None),
                       color=colours[alpha], lw=1.5, label=f"$\\alpha$ = {alpha:.2f}")
        ax_dist.semilogx(outputs.distribution.diameter_nm,
                         outputs.distribution.intensity_dist
                         / outputs.distribution.intensity_dist.max(),
                         color=colours[alpha], lw=1.5, label=f"$\\alpha$ = {alpha:.2f}")
        rec = outputs.recovered
        ax_dist.semilogx(rec.diameter_nm, rec.intensity_dist / rec.intensity_dist.max(),
                         color=colours[alpha], lw=1.0, ls=":")
    ax_corr.set_xlabel("lag time $\\tau$ (s)")
    ax_corr.set_ylabel("$g_2(\\tau)-1$")
    ax_corr.set_title("(a) clusters leave a slow tail\nbeyond the monomer decay", fontsize=8.6)
    ax_corr.grid(True, which="both", **GRID)
    ax_corr.legend(loc="lower left")
    ax_corr.set_xlim(2e-5, 1e-2)
    ax_corr.set_ylim(1e-6, 1.3)

    ax_dist.set_xlabel("diameter $d$ (nm)")
    ax_dist.set_ylabel("intensity distribution (norm.)")
    ax_dist.set_title("(b) second mode at 5.5 $d_0$, recovered too", fontsize=8.6)
    ax_dist.grid(True, which="both", **GRID)
    ax_dist.legend(loc="upper right")
    ax_dist.set_xlim(40, 2000)
    ax_dist.axvline(550, color="#9ca3af", ls="--", lw=0.8)
    ax_dist.text(560, 0.35, "5.5 $d_0$", fontsize=6.6, color="#6b7280")

    rows_ = aggregation_rows()
    alphas = np.array([r["aggregation"] for r in rows_])
    pdis = np.array([r["pdi"] for r in rows_])
    ax_pdi.plot(alphas, pdis, "o-", color=INK, ms=4, lw=1.2, label="PDI from the fit")
    ax_pdi.plot(alphas, [r["pdi_exact"] for r in rows_], "s--", color="#9ca3af", ms=3,
                lw=1.0, label="PDI of the input distribution")
    ax_pdi.axhline(PDI_LIMIT, color="#b91c1c", ls=":", lw=1.0)
    ax_pdi.set_xlabel("aggregation parameter $\\alpha$ (cluster intensity share)")
    ax_pdi.set_ylabel("PDI")
    ax_pdi.set_title("(c) 10 % cluster intensity is enough\nto cross PDI = 0.2", fontsize=8.6)
    ax_pdi.grid(True, **GRID)
    ax_pdi.legend(loc="upper left")
    fig.tight_layout()
    return _save(fig, "fig_aggregation.png")


# --------------------------------------------------------------------------- figure 8
def solvent_temperature() -> pathlib.Path:
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2))
    ax_tau, ax_corr, ax_d = axes
    rows_ = solvent_rows()
    colours = {"water": "#2563eb", "ethanol": "#ea580c"}
    for solvent in SOLVENTS:
        subset = [r for r in rows_ if r["solvent"] == solvent]
        ax_tau.plot([r["temperature_c"] for r in subset], [r["tau_c_ms"] for r in subset],
                    "o-", color=colours[solvent], ms=4, lw=1.2, label=solvent)
    ax_tau.set_xlabel("temperature (C)")
    ax_tau.set_ylabel("$\\tau_c = 1/\\bar{\\Gamma}$ (ms)")
    ax_tau.set_title("(a) the same 100 nm particle decays faster\nas either solvent warms", fontsize=8.6)
    ax_tau.grid(True, **GRID)
    ax_tau.legend(loc="upper right")

    for temperature, colour in [(10.0, "#1d4ed8"), (55.0, "#dc2626")]:
        outputs = run(solvent="water", temperature_c=temperature, size_nm=100.0,
                      size_std_rel=0.10, aggregation=0.0)
        ax_corr.semilogx(outputs.autocorrelation.tau_s, outputs.autocorrelation.g2_minus_1,
                         color=colour, lw=1.5,
                         label=f"{temperature:.0f} C: $\\eta$ = "
                               f"{outputs.viscosity_mpa_s:.3f} mPa s")
    ax_corr.set_xlim(1e-5, 1e-2)
    ax_corr.set_ylim(-0.04, 0.95)
    ax_corr.set_xlabel("lag time $\\tau$ (s)")
    ax_corr.set_ylabel("$g_2(\\tau)-1$")
    ax_corr.set_title("(b) warmer solvent, faster decay: the slope\nof a semilog plot is $-\\Gamma$", fontsize=8.6)
    ax_corr.grid(True, which="both", **GRID)
    ax_corr.legend(loc="lower left")

    predicted = []
    measured = []
    for entry in rows_:
        predicted.append(3.0 * np.pi * entry["viscosity_mpas"] * 1e-3 * 100.0e-9
                         / (1.380649e-23 * (entry["temperature_c"] + 273.15)
                            * (entry["q_nm_inv"] * 1e9) ** 2) * 1e3)
        measured.append(entry["tau_c_ms"])
        ax_d.plot(predicted[-1], measured[-1], "o", ms=5,
                  color=colours[entry["solvent"]],
                  label=f"{entry['solvent']}" if entry["temperature_c"] == 10.0 else None)
    limits = [0.1, 0.6]
    ax_d.plot(limits, limits, "-", color="#9ca3af", lw=1.0, label="1:1")
    ax_d.plot(limits, [1.02 * v for v in limits], ":", color="#9ca3af", lw=0.9)
    ax_d.plot(limits, [0.98 * v for v in limits], ":", color="#9ca3af", lw=0.9)
    ax_d.set_xlabel("predicted $\\tau_c$ (ms)")
    ax_d.set_ylabel("measured $\\tau_c$ (ms)")
    ax_d.set_title("(c) all eight cases sit on the 1:1 line:\nthe code reproduces Stokes-Einstein", fontsize=8.6)
    ax_d.grid(True, **GRID)
    ax_d.tick_params(labelsize=8)
    ax_d.set_xlim(*limits)
    ax_d.set_ylim(*limits)
    ax_d.legend(loc="lower right", fontsize=6.8)
    fig.tight_layout()
    return _save(fig, "fig_solvent_temperature.png")


# --------------------------------------------------------------------------- figure 9
def refractive_index() -> pathlib.Path:
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2))
    ax_rate, ax_corr = axes
    rows_ = refractive_index_rows()
    nps = np.array([r["particle_ri"] for r in rows_])
    rates = np.array([r["count_rate_kcps"] for r in rows_])
    clipped = rates <= 15.05
    ax_rate.semilogy(nps[~clipped], rates[~clipped], "o-", color=INK, ms=4, lw=1.2,
                     label="mean count rate (measured model)")
    ax_rate.semilogy(nps[clipped], rates[clipped], "o", color="#b91c1c", ms=5,
                     mfc="white", label="on the 15 kcps model floor")
    ax_rate.axhline(2500.0, color="#b91c1c", ls=":", lw=1.0)
    ax_rate.text(1.55, 1400.0, "model ceiling 2500 kcps", fontsize=6.6, color="#b91c1c")
    ax_rate.axvline(1.3312, color="#6b7280", lw=0.8, ls="--")
    ax_rate.text(1.337, 300.0, "index match\n$n_p = n_s$", fontsize=6.8, color="#6b7280")
    ax_rate.set_xlabel("particle refractive index $n_p$")
    ax_rate.set_ylabel("mean count rate (kcps)")
    ax_rate.set_title("(a) the particle index sets the signal\nover more than two decades", fontsize=8.6)
    ax_rate.grid(True, which="both", **GRID)
    ax_rate.legend(loc="lower right", fontsize=6.8)

    styles = [(1.40, "#0ea5e9", "-", 0), (1.59, "#2563eb", "--", 0), (2.00, "#dc2626", "-", 14)]
    for ri, colour, style, markevery in styles:
        outputs = run(particle_ri=ri, size_nm=100.0, size_std_rel=0.10, aggregation=0.0)
        kwargs = dict(color=colour, lw=1.6, ls=style, label=f"$n_p$ = {ri:.2f}")
        if markevery:
            kwargs.update(marker="o", ms=3.2, markevery=markevery, mfc="white")
        ax_corr.semilogx(outputs.autocorrelation.tau_s, outputs.autocorrelation.g2_minus_1,
                         **kwargs)
    ax_corr.set_xlim(1e-5, 1e-2)
    ax_corr.set_ylim(-0.04, 0.95)
    ax_corr.set_xlabel("lag time $\\tau$ (s)")
    ax_corr.set_ylabel("$g_2(\\tau)-1$")
    ax_corr.set_title("(b) three indices, one curve:\nshape, $z$-average and PDI do not move", fontsize=8.6)
    ax_corr.grid(True, which="both", **GRID)
    ax_corr.legend(loc="lower left")
    fig.tight_layout()
    return _save(fig, "fig_refractive_index.png")


# --------------------------------------------------------------------------- figure 10
def inversion_validation() -> pathlib.Path:
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2))
    ax_line, ax_err, ax_shape = axes
    data = size_rows()
    diameters = np.array([r["size_nm"] for r in data])
    z = np.array([r["z_avg_nm"] for r in data])
    rec = np.array([r["recovered_i_nm"] for r in data])
    rec_n = np.array([r["recovered_n_nm"] for r in data])
    ax_line.loglog(diameters, diameters, "-", color="#9ca3af", lw=1.0, label="1:1")
    ax_line.loglog(diameters, rec, "o-", color=RECOVERED, ms=4, lw=1.2,
                   label="recovered intensity mode")
    ax_line.loglog(diameters, z, "s--", color=MONO, ms=3.5, lw=1.0, label="cumulant $z$-average")
    ax_line.loglog(diameters, rec_n, "^:", color=NUMBER, ms=3.5, lw=1.0, label="recovered number mode")
    ax_line.set_xlabel("input diameter $d_0$ (nm)")
    ax_line.set_ylabel("recovered size (nm)")
    ax_line.set_title("(a) both routes lie on the 1:1 line\nover 50x in diameter", fontsize=8.6)
    ax_line.grid(True, which="both", **GRID)
    ax_line.legend(loc="upper left")

    width = 0.26
    index = np.arange(len(diameters))
    ax_err.bar(index - width, [r["z_error_pct"] for r in data], width, color=MONO,
               label="$z$-average")
    ax_err.bar(index, [r["recovered_i_error_pct"] for r in data], width, color=RECOVERED,
               label="recovered I mode")
    ax_err.bar(index + width, [r["recovered_n_error_pct"] for r in data], width, color=NUMBER,
               label="recovered N mode")
    ax_err.axhline(0, color=INK, lw=0.8)
    ax_err.set_xticks(index)
    ax_err.set_xticklabels([f"{d:.0f}" for d in diameters])
    ax_err.set_xlabel("input diameter $d_0$ (nm)")
    ax_err.set_ylabel("error (%)")
    ax_err.set_title("(b) every route is within 6 % of the input", fontsize=8.6)
    ax_err.grid(True, axis="y", **GRID)
    ax_err.legend(loc="lower right", fontsize=6.8)

    for size, colour in [(10.0, "#0ea5e9"), (100.0, "#dc2626")]:
        outputs = run(size_nm=size, size_std_rel=0.10, aggregation=0.0)
        dist = outputs.distribution
        norm = dist.intensity_dist.max()
        ax_shape.semilogx(dist.diameter_nm * 1.0, dist.intensity_dist / norm,
                          color=colour, lw=1.4, label=f"truth, {size:.0f} nm")
        recovered = outputs.recovered
        ax_shape.semilogx(recovered.diameter_nm,
                          recovered.intensity_dist / recovered.intensity_dist.max(),
                          color=colour, lw=1.1, ls=":", label=f"inversion, {size:.0f} nm")
    ax_shape.set_xlim(3, 2000)
    ax_shape.set_xlabel("diameter $d$ (nm)")
    ax_shape.set_ylabel("intensity distribution (norm.)")
    ax_shape.set_title("(c) the inversion reproduces the shape,\nincluding the width", fontsize=8.6)
    ax_shape.grid(True, which="both", **GRID)
    ax_shape.legend(loc="upper right", fontsize=6.8)
    fig.tight_layout()
    return _save(fig, "fig_inversion.png")


def main() -> None:
    measurement_chain()
    base_dashboard()
    cli_transcript()
    size_series()
    polydispersity_series()
    aggregation_series()
    solvent_temperature()
    refractive_index()
    inversion_validation()
    gui = FIG / "gui_screenshot.png"
    print(f"gui capture {'present' if gui.exists() else 'MISSING'} ({gui.name})")


if __name__ == "__main__":
    main()
