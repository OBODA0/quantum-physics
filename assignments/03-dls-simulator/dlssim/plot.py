"""Publication-quality Matplotlib figures for the DLS simulator."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .simulator import DLSInputs, DLSOutputs, simulate_dls


def plot_dls_dashboard(
    outputs: DLSOutputs,
    out_path: str | Path | None = None,
    dpi: int = 200,
) -> plt.Figure:
    """Plot a 4-panel DLS simulator dashboard matching the whiteboard layout."""
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.6), dpi=dpi)
    ax_trace, ax_corr = axes[0, 0], axes[0, 1]
    ax_dist, ax_card = axes[1, 0], axes[1, 1]

    inp = outputs.inputs
    ac = outputs.autocorrelation
    dist = outputs.distribution
    cum = outputs.cumulants

    # Panel (a): Photon Counts vs t (Whiteboard 1 top-middle)
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
        label=f"Mean $\\langle I \\rangle = {outputs.mean_count_rate_kcps:.1f}$ kcps",
    )
    ax_trace.set_title(
        "(a) Brownian Speckle Fluctuations: Photon Counts vs $t$",
        fontsize=11,
        fontweight="bold",
    )
    ax_trace.set_xlabel("Time $t$ (ms)")
    ax_trace.set_ylabel("Photon Count Rate (kcps)")
    ax_trace.grid(True, alpha=0.28)
    ax_trace.legend(loc="upper right", fontsize=8.5)

    # Panel (b): Auto-correlation function on log axis (Whiteboard Output 1)
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
        # Highlight aggregation shoulder region
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
        "(b) Auto-Correlation Function $g_2(\\tau) - 1$ (Log Time Axis)",
        fontsize=11,
        fontweight="bold",
    )
    ax_corr.set_xlabel("Lag Time $\\tau$ (s) [log scale]")
    ax_corr.set_ylabel("$g_2(\\tau) - 1$")
    ax_corr.set_ylim(-0.04, max(inp.intercept_beta + 0.10, 0.95))
    ax_corr.grid(True, which="both", alpha=0.28)
    ax_corr.legend(loc="upper right", fontsize=8.5)

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
        "(c) Size Distribution [Number, Intensity] (Log Size Axis)",
        fontsize=11,
        fontweight="bold",
    )
    ax_dist.set_xlabel("Hydrodynamic Diameter $d$ (nm) [log scale]")
    ax_dist.set_ylabel("Normalized Weight (%)")
    ax_dist.grid(True, which="both", alpha=0.28)
    ax_dist.legend(loc="upper right", fontsize=8.5)

    # Panel (d): Parameter & PDI Summary Card
    ax_card.axis("off")
    badge_color = "#dcfce7" if cum.is_monodisperse else "#fee2e2"
    border_color = "#15803d" if cum.is_monodisperse else "#b91c1c"

    summary_lines = [
        "DLS SIMULATOR — INPUTS & CUMULANT OUTPUTS",
        "------------------------------------------------------------",
        f"1. Solvent            : {outputs.solvent_model.label}",
        f"   Viscosity eta(T)   : {outputs.viscosity_mpa_s:.3f} mPa*s",
        f"   Solvent RI n_s(T)  : {outputs.solvent_ri:.4f}",
        f"2. Particle RI n_p    : {inp.particle_ri:.4f} "
        f"(contrast K = {outputs.optical_contrast:.4f})",
        f"3. Primary Size d_0   : {inp.size_nm:.1f} nm",
        f"4. Size Width sigma/d : {inp.size_std_rel:.3f} ({inp.dist_shape})",
        f"5. Aggregation alpha  : {inp.aggregation:.3f} "
        f"(cluster ~ {inp.agg_size_factor * inp.size_nm:.0f} nm)",
        f"6. Temperature T      : {inp.temperature_c:.1f} C "
        f"({outputs.temperature_k:.2f} K)",
        "------------------------------------------------------------",
        f"Scattering Vector q   : {outputs.q_nm_inv:.4f} nm^-1 "
        f"(lambda={inp.wavelength_nm:.1f} nm, theta={inp.angle_deg:.0f} deg)",
        f"Diffusion Coeff D_z   : {cum.z_avg_diffusion_m2_s * 1e12:.3f} um^2/s",
        f"Number Mean Size      : {dist.number_mean_nm:.2f} nm",
        f"Intensity Mean Size   : {dist.intensity_mean_nm:.2f} nm",
        f"Z-Average Size D_z    : {cum.z_average_nm:.2f} nm",
        f"Polydispersity (PDI)  : {cum.pdi:.4f} "
        f"(exact {cum.pdi_exact:.4f}, input var {cum.pdi_monomer_intrinsic:.4f})",
        f"Recovered I / N peak  : {rec.peak_intensity_nm:.1f} / {rec.peak_number_nm:.1f} nm",
        f"Inversion residual    : {rec.residual:.3f}",
        f"Whiteboard Criterion  : {cum.quality_verdict}",
    ]
    ax_card.text(
        0.03,
        0.96,
        "\n".join(summary_lines),
        transform=ax_card.transAxes,
        va="top",
        ha="left",
        fontsize=9.2,
        family="monospace",
        bbox={
            "boxstyle": "round,pad=0.6",
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


def plot_whiteboard_comparison(
    out_path: str | Path | None = None,
    dpi: int = 200,
) -> plt.Figure:
    """Reproduce the instructor's whiteboard comparison curves in 3 panels.

    Panel (a): Smaller particles vs Larger particles vs Aggregation on log-tau.
    Panel (b): Number vs Intensity size distribution on log-size axis.
    Panel (c): Water vs Ethanol solvent comparison at fixed particle size.
    """
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

    # Panel (a): Whiteboard 1 autocorrelation comparison
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

    # Panel (b): Number vs Intensity distribution for the aggregated sample
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

    # Panel (c): Water vs Ethanol solvent comparison
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
