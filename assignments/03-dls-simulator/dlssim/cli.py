"""Command-line interface for the Task 3 DLS Nanoparticle Simulator."""

from __future__ import annotations

import argparse
from typing import Sequence

import matplotlib.pyplot as plt

from .gui import launch_gui
from .plot import plot_dls_dashboard, plot_whiteboard_comparison
from .simulator import DLSInputs, DLSOutputs, simulate_dls
from .solvents import SOLVENTS, list_solvents


def format_terminal_report(outputs: DLSOutputs) -> str:
    """Format a structured ASCII terminal summary of DLS inputs and outputs."""
    inp = outputs.inputs
    dist = outputs.distribution
    cum = outputs.cumulants
    lines = [
        "======================================================================",
        "  DYNAMIC LIGHT SCATTERING (DLS) NANOPARTICLE SIMULATOR (ISO 22412)   ",
        "======================================================================",
        "  WHITEBOARD INPUTS:",
        f"    1. Solvent                  : {outputs.solvent_model.label}",
        f"       - Dynamic viscosity eta  : {outputs.viscosity_mpa_s:.4f} mPa*s",
        f"       - Solvent RI n_s(T)      : {outputs.solvent_ri:.4f}",
        f"    2. Particle RI n_p          : {inp.particle_ri:.4f} "
        f"(optical contrast K = {outputs.optical_contrast:.4f})",
        f"    3. Primary particle size d0 : {inp.size_nm:.2f} nm",
        f"    4. Size distribution width  : sigma/d0 = {inp.size_std_rel:.3f} "
        f"({inp.dist_shape})",
        f"    5. Aggregation parameter    : alpha_agg = {inp.aggregation:.3f}",
        f"    6. Temperature T            : {inp.temperature_c:.2f} C "
        f"({outputs.temperature_k:.2f} K)",
        "----------------------------------------------------------------------",
        "  OPTICAL & HYDRODYNAMIC PARAMETERS:",
        f"    Laser wavelength lambda_0   : {inp.wavelength_nm:.1f} nm",
        f"    Scattering angle theta      : {inp.angle_deg:.1f} deg",
        f"    Scattering vector q         : {outputs.q_nm_inv:.5f} nm^-1 "
        f"({outputs.q_m_inv:.3e} m^-1)",
        f"    Mean photon count rate <I>  : {outputs.mean_count_rate_kcps:.1f} kcps",
        f"    Mean decay rate Gamma_bar   : {cum.gamma_bar_s_inv:.2f} s^-1 "
        f"(tau_c = {1e3 / max(cum.gamma_bar_s_inv, 1.0):.4f} ms)",
        f"    Z-avg diffusion coeff D_z   : "
        f"{cum.z_avg_diffusion_m2_s * 1e12:.4f} um^2/s",
        "----------------------------------------------------------------------",
        "  WHITEBOARD OUTPUTS:",
        "    1. Auto-correlation g2(tau)-1 : computed on log tau in [1e-7, 1] s",
        f"    2. Size distribution (log d)  : Number mean    = "
        f"{dist.number_mean_nm:.2f} nm (std = {dist.number_std_nm:.2f} nm)",
        f"                                    Intensity mean = "
        f"{dist.intensity_mean_nm:.2f} nm (std = {dist.intensity_std_nm:.2f} nm)",
        f"                                    Z-average D_z  = "
        f"{cum.z_average_nm:.2f} nm",
        f"    3. Polydispersity Index (PDI) : {cum.pdi:.4f} "
        f"(cumulant fit = {cum.pdi_fitted:.4f})",
        f"       Criterion (If PDI < 0.2)   : {cum.quality_verdict}",
        "======================================================================",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for `python -m dlssim`."""
    parser = argparse.ArgumentParser(
        prog="dlssim",
        description=(
            "Simulate Dynamic Light Scattering (DLS) autocorrelation "
            "functions, Number/Intensity size distributions, and PDI."
        ),
    )
    parser.add_argument(
        "--solvent",
        type=str,
        default="water",
        choices=list_solvents(),
        help="Solvent selection (default: water).",
    )
    parser.add_argument(
        "--ri",
        type=float,
        default=1.590,
        help="Refractive index n_p of the nanoparticle (default: 1.590).",
    )
    parser.add_argument(
        "--size-nm",
        type=float,
        default=50.0,
        help="Primary hydrodynamic diameter d_0 in nm (default: 50.0).",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=0.12,
        help="Relative standard deviation sigma/d_0 (default: 0.12).",
    )
    parser.add_argument(
        "--shape",
        type=str,
        default="lognormal",
        choices=["lognormal", "gaussian"],
        help="Primary size distribution shape (default: lognormal).",
    )
    parser.add_argument(
        "--aggregation",
        type=float,
        default=0.08,
        help="Aggregation parameter alpha_agg in [0, 1] (default: 0.08).",
    )
    parser.add_argument(
        "--temp-c",
        type=float,
        default=25.0,
        help="Sample temperature in degrees Celsius (default: 25.0).",
    )
    parser.add_argument(
        "--wavelength",
        type=float,
        default=632.8,
        help="Laser wavelength in nm (default: 632.8 He-Ne).",
    )
    parser.add_argument(
        "--angle",
        type=float,
        default=173.0,
        help="Scattering detection angle in degrees (default: 173.0).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="out/dls_dashboard.png",
        help="Output PNG path for the 4-panel DLS dashboard.",
    )
    parser.add_argument(
        "--compare-out",
        type=str,
        default="",
        help="Optional PNG path for the 3-panel whiteboard comparison figure.",
    )
    parser.add_argument(
        "--list-solvents",
        action="store_true",
        help="List available solvents with viscosity and RI at 25 C and exit.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the interactive Tkinter + Matplotlib GUI.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the DLS CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_solvents:
        print("Available DLS Solvents (at T = 25.0 C / 298.15 K):")
        for key, model in SOLVENTS.items():
            eta = model.viscosity_mpa_s(298.15)
            ri = model.refractive_index(298.15)
            print(f"  - {key:<8s}: {model.label:<26s} eta={eta:.3f} mPa*s, n={ri:.4f}")
        return 0

    if args.gui:
        launch_gui()
        return 0

    inputs = DLSInputs(
        solvent=args.solvent,
        particle_ri=args.ri,
        size_nm=args.size_nm,
        size_std_rel=args.sigma,
        aggregation=args.aggregation,
        temperature_c=args.temp_c,
        dist_shape=args.shape,
        wavelength_nm=args.wavelength,
        angle_deg=args.angle,
    )
    outputs = simulate_dls(inputs)
    print(format_terminal_report(outputs))

    if args.out:
        fig = plot_dls_dashboard(outputs, out_path=args.out)
        plt.close(fig)
        print(f"Saved DLS dashboard figure -> {args.out}")

    if args.compare_out:
        fig_cmp = plot_whiteboard_comparison(out_path=args.compare_out)
        plt.close(fig_cmp)
        print(f"Saved whiteboard comparison figure -> {args.compare_out}")

    return 0
