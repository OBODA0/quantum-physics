"""Command line interface for the DLS simulator."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from .detector import DetectorConfig
from .materials import MATERIALS
from .model import DLSModel
from .solvents import SOLVENTS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dlssim",
        description="Dynamic light scattering simulator: correlation curve, size distribution, PDI.",
    )
    parser.add_argument("--diameter", type=float, default=100.0, help="median diameter in nm")
    parser.add_argument("--sigma", type=float, default=1.0, help="geometric standard deviation (1 = monodisperse)")
    parser.add_argument("--solvent", choices=sorted(SOLVENTS), default="water")
    parser.add_argument("--material", choices=sorted(MATERIALS), default="polystyrene")
    parser.add_argument("--temperature", type=float, default=25.0, help="temperature in C")
    parser.add_argument("--aggregation-fraction", type=float, default=0.0, help="fraction of primaries in aggregates")
    parser.add_argument("--aggregation-number", type=int, default=10, help="primaries per aggregate")
    parser.add_argument("--fractal-dimension", type=float, default=1.8)
    parser.add_argument("--angle", type=float, default=178.0, help="detection angle in degrees")
    parser.add_argument("--wavelength", type=float, default=633.0, help="laser wavelength in nm")
    parser.add_argument("--beta", type=float, default=0.9, help="coherence factor")
    parser.add_argument("--duration", type=float, default=30.0, help="acquisition time in s")
    parser.add_argument("--concentration", type=float, default=1e8, help="particles per mL")
    parser.add_argument("--regularization", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=Path, default=Path("out"), help="output directory")
    parser.add_argument("--no-plot", action="store_true")
    parser.add_argument("--no-csv", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict:
    model = DLSModel(
        diameter_m=args.diameter * 1e-9,
        geometric_sd=args.sigma,
        solvent_name=args.solvent,
        material_name=args.material,
        temperature_c=args.temperature,
        aggregation_fraction=args.aggregation_fraction,
        aggregation_number=args.aggregation_number,
        fractal_dimension=args.fractal_dimension,
        wavelength_m=args.wavelength * 1e-9,
        angle_deg=args.angle,
        beta=args.beta,
    )
    config = DetectorConfig(duration_s=args.duration, beta=args.beta)
    tau, g2 = model.measure(config, seed=args.seed)
    fit = model.fit(tau, g2)
    inversion = model.invert(tau, g2, regularization=args.regularization)
    trace = model.photon_trace(config, seed=args.seed + 1)

    gamma_mean, mu2, pdi_true = model.true_cumulants
    print("DLS simulator")
    print(f"  solvent        {model.solvent.name} at {model.temperature_c:.1f} C: "
          f"n = {model.refractive_index:.4f}, eta = {model.viscosity*1e3:.4f} mPa s")
    print(f"  particle       {model.material.name}: n = {model.material.refractive_index:.4f}, "
          f"median {args.diameter:.1f} nm, sigma {args.sigma:.2f}")
    print(f"  aggregation    {args.aggregation_fraction*100:.0f}% of primaries, "
          f"N = {args.aggregation_number}, df = {args.fractal_dimension:.2f}")
    print(f"  scattering     q = {model.q:.4e} 1/m, angle {args.angle:.0f} deg, "
          f"lambda {args.wavelength:.1f} nm")
    print(f"  diffusion      D = {model.diffusion():.4e} m^2/s, "
          f"tau = {model.correlation_time*1e6:.1f} us")
    print()
    print(f"  true z-average {model.true_z_average_m*1e9:.2f} nm, PDI {pdi_true:.4f}")
    print(f"  measured       {fit.z_average_diameter_m*1e9:.2f} nm, PDI {fit.pdi:.4f} "
          f"({fit.points_used} lags)")
    print(f"  inversion      intensity peak {inversion.peak_intensity_m*1e9:.1f} nm, "
          f"number peak {inversion.peak_number_m*1e9:.1f} nm, residual {inversion.residual:.3f}")
    print(f"  count rate     {model.count_rate_cps(args.concentration):.3e} counts/s "
          f"at {args.concentration:.1e} per mL")

    args.out.mkdir(parents=True, exist_ok=True)
    if not args.no_csv:
        path = args.out / "correlation.csv"
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["tau_s", "g2_ideal", "g2_measured", "g1_measured"])
            g1_measured = np.sqrt(np.clip((g2 - 1.0) / model.beta, 0.0, None))
            for row in zip(tau, model.g2(tau), g2, g1_measured):
                writer.writerow([f"{value:.8e}" for value in row])
        distribution = args.out / "distribution.csv"
        with distribution.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["diameter_nm", "intensity", "number", "volume"])
            for row in zip(
                inversion.diameters_m * 1e9,
                inversion.intensity_weights,
                inversion.number_weights,
                inversion.volume_weights,
            ):
                writer.writerow([f"{value:.8e}" for value in row])
        print(f"  wrote          {path}, {distribution}")

    if not args.no_plot:
        from .plotting import dashboard

        image = args.out / "dashboard.png"
        dashboard(model, tau, g2, fit, inversion, trace=trace, path=image)
        print(f"  wrote          {image}")

    return {
        "model": model,
        "tau": tau,
        "g2_measured": g2,
        "fit": fit,
        "inversion": inversion,
        "true_pdi": pdi_true,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run(args)
    return 0
