"""Publication-quality Matplotlib figures for the DLS simulator."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .autocorrelation import (
     _ou_complex_field,
    empirical_autocorrelation_from_trace,
)
from .simulator import DLSInputs, DLSOutputs, simulate_dls


def plot_dls_dashboard(
    outputs: DLSOutputs,
    out_path: str | Path | None = None,
    dpi: int = 200,
) -> plt.Figure:
    """Plot a 4-panel DLS simulator dashboard matching the whiteboard layout."""
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 8.7), dpi=dpi)
    ax_trace, ax_corr = axes[0, 0], axes[0, 1]
    ax_dist, ax_card = axes[1, 0], axes[1, 1]

    inp = outputs.inputs
    ac = outputs.autocorrelation
    dist = outputs.distribution
    cum = outputs.cumulants

    # Panel (a): Photon Counts vs t (Whiteboard Output 1)
    ax_trace.plot(
        ac.time_trace_ms,
        ac.photon_counts_kcps,
        color="#0284c7",
        lw=1.5,
        label="Scattered photon counts $I(t)$",
    )
    ax_trace.axhline(
        outputs.mean_count_rate_kcps,
        color="#0f172a",
        ls="--",
        lw=1.1,
        label=(
            f"Mean $\\langle I \\rangle = {outputs.mean_count_rate_kcps:.1f}$ kcps "
            f"($\\Delta t = {ac.gate_time_us:.1f}\\,\\mu$s)"
        ),
    )
    ax_trace.set_title(
        "(a) Output 1: Photon Counts vs Time $I(t)$ (Brownian Speckle)",
        fontsize=10.8,
        fontweight="bold",
    )
    ax_trace.set_xlabel("Time $t$ (ms)")
    ax_trace.set_ylabel("Photon Count Rate (kcps)")
    ax_trace.grid(True, alpha=0.28)
    ax_trace.legend(loc="upper right", fontsize=8.3)

    # Secondary y-axis showing raw photon counts per correlator gate bin
    ax_trace_rhs = ax_trace.twinx()
    y_min_kcps, y_max_kcps = ax_trace.get_ylim()
    bin_scale = ac.gate_time_us * 1.0e-3  # counts/bin = kcps * (gate_us * 1e-3)
    ax_trace_rhs.set_ylim(y_min_kcps * bin_scale, y_max_kcps * bin_scale)
    ax_trace_rhs.set_ylabel(
        f"Photons / Gate Bin ($\\Delta t = {ac.gate_time_us:.1f}\\,\\mu$s)",
        fontsize=8.5,
        color="#334155",
    )
    ax_trace_rhs.tick_params(axis="y", labelsize=8, colors="#334155")

    # Panel (b): Auto-correlation function on log axis (Whiteboard Output 2)
    ax_corr.semilogx(
        ac.tau_s,
        ac.g2_minus_1,
        color="#dc2626",
        lw=2.3,
        label="Total $g_2(\\tau) - 1 = \\beta |g_1(\\tau)|^2$",
    )
    if inp.aggregation > 1.0e-4:
        ax_corr.semilogx(
            ac.tau_s,
            ac.g2_monomer_only,
            color="#2563eb",
            ls="--",
            lw=1.6,
            label="Monomer-only reference (no aggregation)",
        )
        shoulder_idx = int(np.argmin(np.abs(ac.g2_monomer_only - 0.08)))
        tau_sh = float(ac.tau_s[shoulder_idx])
        y_sh = float(ac.g2_minus_1[shoulder_idx])
        ax_corr.annotate(
            "Aggregation tail\n(slow cluster decay)",
            xy=(tau_sh, y_sh),
            xytext=(tau_sh * 6.0, min(y_sh + 0.22, 0.78)),
            arrowprops={"arrowstyle": "->", "color": "#7c2d12", "lw": 1.3},
            fontsize=8.5,
            fontweight="bold",
            color="#7c2d12",
        )
    tau_char = 1.0 / max(cum.gamma_bar_s_inv, 1.0)
    ax_corr.axvline(
        tau_char,
        color="#475569",
        ls=":",
        lw=1.2,
        label=f"$\\tau_c = 1/\\bar{{\\Gamma}} = {tau_char * 1e3:.3f}$ ms",
    )
    ax_corr.set_title(
        "(b) Output 2: Auto-Correlation $g_2(\\tau) - 1$ (Log Time Axis)",
        fontsize=10.8,
        fontweight="bold",
    )
    ax_corr.set_xlabel("Lag Time $\\tau$ (s) [log scale]")
    ax_corr.set_ylabel("$g_2(\\tau) - 1$")
    ax_corr.set_ylim(-0.04, max(inp.intercept_beta + 0.10, 0.95))
    ax_corr.grid(True, which="both", alpha=0.28)
    ax_corr.legend(loc="upper right", fontsize=8.3)

    # Panel (c): Size Distribution [Number, Intensity] on log size axis
    d_nm = dist.diameter_nm
    p_num_pct = dist.number_dist * 100.0
    p_int_pct = dist.intensity_dist * 100.0
    ax_dist.semilogx(
        d_nm,
        p_num_pct,
        color="#16a34a",
        lw=2.1,
        label=f"Number dist. (mean = {dist.number_mean_nm:.1f} nm)",
    )
    ax_dist.fill_between(d_nm, 0.0, p_num_pct, color="#16a34a", alpha=0.18)
    ax_dist.semilogx(
        d_nm,
        p_int_pct,
        color="#9333ea",
        lw=2.2,
        label=f"Intensity dist. (mean = {dist.intensity_mean_nm:.1f} nm)",
    )
    ax_dist.fill_between(d_nm, 0.0, p_int_pct, color="#9333ea", alpha=0.18)
    rec = outputs.recovered
    ax_dist.semilogx(
        rec.diameter_nm,
        rec.intensity_dist * 100.0,
        color="#9333ea",
        ls="--",
        lw=1.5,
        label=f"Recovered intensity (peak {rec.peak_intensity_nm:.0f} nm)",
    )
    ax_dist.semilogx(
        rec.diameter_nm,
        rec.number_dist * 100.0,
        color="#16a34a",
        ls="--",
        lw=1.5,
        label=f"Recovered number (peak {rec.peak_number_nm:.0f} nm)",
    )
    ax_dist.axvline(
        cum.z_average_nm,
        color="#0f172a",
        ls="--",
        lw=1.4,
        label=f"Cumulant $Z$-average $D_z = {cum.z_average_nm:.1f}$ nm",
    )
    ax_dist.set_title(
        "(c) Output 3: Size Distribution [Number, Intensity] (Log Axis)",
        fontsize=10.8,
        fontweight="bold",
    )
    ax_dist.set_xlabel("Hydrodynamic Diameter $d$ (nm) [log scale]")
    ax_dist.set_ylabel("Normalized Weight (%)")
    ax_dist.grid(True, which="both", alpha=0.28)
    ax_dist.legend(loc="upper right", fontsize=8.3)

    # Panel (d): Parameter & PDI Summary Card (Output 4)
    ax_card.axis("off")
    badge_color = "#dcfce7" if cum.is_monodisperse else "#fee2e2"
    border_color = "#15803d" if cum.is_monodisperse else "#b91c1c"
    mean_bin_phot = float(np.mean(ac.photon_counts_per_bin))

    summary_lines = [
        "DLS SIMULATOR — 6 INPUTS & 4 WHITEBOARD OUTPUTS",
        "------------------------------------------------------------",
        f"1. Solvent            : {outputs.solvent_model.label}",
        f"   Viscosity eta(T)   : {outputs.viscosity_mpa_s:.3f} mPa*s | "
        f"RI n_s = {outputs.solvent_ri:.4f}",
        f"2. Particle RI n_p    : {inp.particle_ri:.4f} "
        f"(contrast K = {outputs.optical_contrast:.4f})",
        f"3. Primary Size d_0   : {inp.size_nm:.1f} nm",
        f"4. Size Width sigma/d : {inp.size_std_rel:.3f} ({inp.dist_shape})",
        f"5. Aggregation alpha  : {inp.aggregation:.3f} "
        f"(cluster ~ {inp.agg_size_factor * inp.size_nm:.0f} nm)",
        f"6. Temperature T      : {inp.temperature_c:.1f} C "
        f"({outputs.temperature_k:.2f} K)",
        "------------------------------------------------------------",
        f"Out 1. Photon Counts  : <I> = {outputs.mean_count_rate_kcps:.1f} kcps (gate dt = {ac.gate_time_us:.1f} us)",
        f"Out 2. Autocorrelation: Gamma_bar = {cum.gamma_bar_s_inv:.1f} s^-1, D_z = {cum.z_avg_diffusion_m2_s * 1e12:.3f} um^2/s",
        f"Out 3. Size Dist (nm) : Number = {dist.number_mean_nm:.1f}, Intensity = {dist.intensity_mean_nm:.1f}, D_z = {cum.z_average_nm:.1f}",
        f"Out 4. PDI & Quality  : PDI = {cum.pdi:.4f} (exact {cum.pdi_exact:.4f}, fit = {cum.pdi_fitted:.4f})",
        f"Recovered I / N peak  : {rec.peak_intensity_nm:.1f} / {rec.peak_number_nm:.1f} nm (residual = {rec.residual:.3f})",
        f"Whiteboard Criterion  : {cum.quality_verdict}",
    ]
    ax_card.text(
        0.02,
        0.96,
        "\n".join(summary_lines),
        transform=ax_card.transAxes,
        va="top",
        ha="left",
        fontsize=9.0,
        family="monospace",
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": badge_color,
            "edgecolor": border_color,
            "lw": 1.8,
        },
    )

    fig.suptitle(
        "Dynamic Light Scattering (DLS) Nanoparticle Sizing Simulator",
        fontsize=13.5,
        fontweight="bold",
        y=0.99,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.965))

    if out_path is not None:
        target = Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=dpi)
    return fig


def plot_photon_counts_comparison(
    out_path: str | Path | None = None,
    dpi: int = 200,
) -> plt.Figure:
    """Plot a 3-panel dedicated figure for Photon Counts vs Time I(t) & Siegert link.

    Panel (a): Photon Counts vs Time I(t) on a fixed 2.0 ms window comparing
               20 nm (fast fluctuations) vs 120 nm (slow fluctuations).
    Panel (b): Photon Counts vs Time I(t) comparing monodisperse 50 nm vs
               aggregated 50 nm (alpha_agg = 0.25) with slow cluster bursts.
    Panel (c): Empirical autocorrelation computed directly from the simulated
               Photon Counts trace I(t) overlaid on the analytical Siegert curve.
    """
    small_out = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=20.0,
            size_std_rel=0.08,
            aggregation=0.0,
            temperature_c=25.0,
            rng_seed=11,
        )
    )
    large_out = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=120.0,
            size_std_rel=0.08,
            aggregation=0.0,
            temperature_c=25.0,
            rng_seed=22,
        )
    )
    mono_50 = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=50.0,
            size_std_rel=0.10,
            aggregation=0.0,
            temperature_c=25.0,
            rng_seed=33,
        )
    )
    agg_50 = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=50.0,
            size_std_rel=0.10,
            aggregation=0.25,
            temperature_c=25.0,
            rng_seed=33,
        )
    )

    # Generate fixed-window 2.0 ms traces for direct visual speed comparison
    n_pts = 450
    t_fixed_ms = np.linspace(0.0, 2.0, n_pts)
    dt_s = 2.0e-3 / (n_pts - 1)
    rng_s = np.random.default_rng(101)
    rng_l = np.random.default_rng(202)
    e_s = _ou_complex_field(
        small_out.cumulants.gamma_bar_s_inv, dt_s, n_pts, rng_s
    )
    e_l = _ou_complex_field(
        large_out.cumulants.gamma_bar_s_inv, dt_s, n_pts, rng_l
    )
    i_s = 200.0 * (np.abs(e_s) ** 2) / max(float(np.mean(np.abs(e_s) ** 2)), 1e-9)
    i_l = 200.0 * (np.abs(e_l) ** 2) / max(float(np.mean(np.abs(e_l) ** 2)), 1e-9)

    fig, axes = plt.subplots(1, 3, figsize=(15.2, 4.7), dpi=dpi)
    ax0, ax1, ax2 = axes[0], axes[1], axes[2]

    # Panel (a): Fast vs slow photon count fluctuations on identical time axis
    ax0.plot(
        t_fixed_ms,
        i_s,
        color="#0284c7",
        lw=1.3,
        alpha=0.9,
        label=(
            f"Smaller: 20 nm ($\\tau_c = "
            f"{1e3 / small_out.cumulants.gamma_bar_s_inv:.3f}$ ms)"
        ),
    )
    ax0.plot(
        t_fixed_ms,
        i_l,
        color="#dc2626",
        lw=2.0,
        label=(
            f"Larger: 120 nm ($\\tau_c = "
            f"{1e3 / large_out.cumulants.gamma_bar_s_inv:.3f}$ ms)"
        ),
    )
    ax0.set_title(
        "(a) Photon Counts vs Time: 20 nm vs 120 nm",
        fontsize=10.8,
        fontweight="bold",
    )
    ax0.set_xlabel("Time $t$ (ms) [common 2.0 ms window]")
    ax0.set_ylabel("Photon Count Rate $I(t)$ (kcps)")
    ax0.grid(True, alpha=0.28)
    ax0.legend(loc="upper right", fontsize=8.0)

    # Panel (b): Monodisperse vs Aggregated 50 nm photon count trace
    ax1.plot(
        mono_50.autocorrelation.time_trace_ms,
        mono_50.autocorrelation.photon_counts_kcps,
        color="#16a34a",
        lw=1.35,
        alpha=0.85,
        label="Monodisperse 50 nm ($\\alpha_{\\mathrm{agg}} = 0$)",
    )
    ax1.plot(
        agg_50.autocorrelation.time_trace_ms,
        agg_50.autocorrelation.photon_counts_kcps,
        color="#9333ea",
        lw=1.6,
        label="Aggregated 50 nm ($\\alpha_{\\mathrm{agg}} = 0.25$)",
    )
    ax1.set_title(
        "(b) Photon Counts vs Time: Aggregation Effect",
        fontsize=10.8,
        fontweight="bold",
    )
    ax1.set_xlabel("Time $t$ (ms)")
    ax1.set_ylabel("Photon Count Rate $I(t)$ (kcps)")
    ax1.grid(True, alpha=0.28)
    ax1.legend(loc="upper right", fontsize=8.0)

    # Panel (c): Empirical time-average of I(t)I(t+tau) vs analytical Siegert curve
    tau_emp, g2_emp = empirical_autocorrelation_from_trace(
        gamma_eff_s_inv=mono_50.cumulants.gamma_bar_s_inv,
        intercept_beta=mono_50.inputs.intercept_beta,
        agg_fraction=0.0,
        n_steps=120_000,
        rng_seed=42,
    )
    ax2.semilogx(
        mono_50.autocorrelation.tau_s,
        mono_50.autocorrelation.g2_minus_1,
        color="#0f172a",
        lw=2.2,
        label="Analytical Siegert $\\beta |g_1(\\tau)|^2$",
    )
    ax2.semilogx(
        tau_emp,
        g2_emp,
        "o",
        color="#0284c7",
        ms=4.2,
        alpha=0.85,
        label="Time-averaged $\\langle I(t)I(t+\\tau)\\rangle / \\langle I\\rangle^2 - 1$",
    )
    ax2.set_title(
        "(c) From Photon Trace $I(t)$ to $g_2(\\tau)-1$",
        fontsize=10.8,
        fontweight="bold",
    )
    ax2.set_xlabel("Lag Time $\\tau$ (s) [log scale]")
    ax2.set_ylabel("$g_2(\\tau) - 1$")
    ax2.set_ylim(-0.05, 0.98)
    ax2.grid(True, which="both", alpha=0.28)
    ax2.legend(loc="upper right", fontsize=8.0)

    fig.tight_layout()
    if out_path is not None:
        target = Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=dpi)
    return fig


def plot_whiteboard_comparison(
    out_path: str | Path | None = None,
    dpi: int = 200,
) -> plt.Figure:
    """Reproduce the instructor's whiteboard comparison curves in 3 panels."""
    small_out = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=20.0,
            size_std_rel=0.10,
            aggregation=0.0,
            temperature_c=25.0,
        )
    )
    large_out = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=120.0,
            size_std_rel=0.10,
            aggregation=0.0,
            temperature_c=25.0,
        )
    )
    agg_out = simulate_dls(
        DLSInputs(
            solvent="water",
            particle_ri=1.59,
            size_nm=120.0,
            size_std_rel=0.12,
            aggregation=0.25,
            temperature_c=25.0,
        )
    )
    eth_out = simulate_dls(
        DLSInputs(
            solvent="ethanol",
            particle_ri=1.59,
            size_nm=120.0,
            size_std_rel=0.10,
            aggregation=0.0,
            temperature_c=25.0,
        )
    )

    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.8), dpi=dpi)
    ax0, ax1, ax2 = axes[0], axes[1], axes[2]

    ax0.semilogx(
        small_out.autocorrelation.tau_s,
        small_out.autocorrelation.g2_minus_1,
        color="#0284c7",
        lw=2.2,
        label=f"Smaller particles (20 nm, PDI={small_out.cumulants.pdi:.3f})",
    )
    ax0.semilogx(
        large_out.autocorrelation.tau_s,
        large_out.autocorrelation.g2_minus_1,
        color="#16a34a",
        lw=2.2,
        label=f"Larger particles (120 nm, PDI={large_out.cumulants.pdi:.3f})",
    )
    ax0.semilogx(
        agg_out.autocorrelation.tau_s,
        agg_out.autocorrelation.g2_minus_1,
        color="#dc2626",
        lw=2.2,
        ls="-.",
        label=f"120 nm + Aggregation (alpha=0.25, PDI={agg_out.cumulants.pdi:.3f})",
    )
    ax0.set_title(
        "(a) Auto-Correlation vs Size & Aggregation",
        fontsize=11,
        fontweight="bold",
    )
    ax0.set_xlabel("Lag Time $\\tau$ (s) [log scale]")
    ax0.set_ylabel("$g_2(\\tau) - 1$")
    ax0.grid(True, which="both", alpha=0.28)
    ax0.legend(loc="upper right", fontsize=8.0)

    d_grid = agg_out.distribution.diameter_nm
    ax1.semilogx(
        d_grid,
        agg_out.distribution.number_dist * 100.0,
        color="#16a34a",
        lw=2.2,
        label="Number distribution $p_N(d)$",
    )
    ax1.fill_between(
        d_grid, 0.0, agg_out.distribution.number_dist * 100.0,
        color="#16a34a", alpha=0.18,
    )
    ax1.semilogx(
        d_grid,
        agg_out.distribution.intensity_dist * 100.0,
        color="#9333ea",
        lw=2.2,
        label="Intensity distribution $p_I(d) \\propto d^6 P(q,d)$",
    )
    ax1.fill_between(
        d_grid, 0.0, agg_out.distribution.intensity_dist * 100.0,
        color="#9333ea", alpha=0.18,
    )
    ax1.set_title(
        "(b) Number vs Intensity Distribution (Log Axis)",
        fontsize=11,
        fontweight="bold",
    )
    ax1.set_xlabel("Particle Diameter $d$ (nm) [log scale]")
    ax1.set_ylabel("Normalized Probability (%)")
    ax1.grid(True, which="both", alpha=0.28)
    ax1.legend(loc="upper right", fontsize=8.0)

    ax2.semilogx(
        large_out.autocorrelation.tau_s,
        large_out.autocorrelation.g2_minus_1,
        color="#2563eb",
        lw=2.2,
        label=(
            f"Water (eta={large_out.viscosity_mpa_s:.3f} mPa*s, "
            f"n={large_out.solvent_ri:.3f})"
        ),
    )
    ax2.semilogx(
        eth_out.autocorrelation.tau_s,
        eth_out.autocorrelation.g2_minus_1,
        color="#ea580c",
        lw=2.2,
        ls="--",
        label=(
            f"Ethanol (eta={eth_out.viscosity_mpa_s:.3f} mPa*s, "
            f"n={eth_out.solvent_ri:.3f})"
        ),
    )
    ax2.set_title(
        "(c) Solvent Selection: Water vs Ethanol (120 nm)",
        fontsize=11,
        fontweight="bold",
    )
    ax2.set_xlabel("Lag Time $\\tau$ (s) [log scale]")
    ax2.set_ylabel("$g_2(\\tau) - 1$")
    ax2.grid(True, which="both", alpha=0.28)
    ax2.legend(loc="upper right", fontsize=8.0)

    fig.tight_layout()
    if out_path is not None:
        target = Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, dpi=dpi)
    return fig
