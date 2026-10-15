"""Command line entry point for the PL spectrometer simulator."""

from __future__ import annotations

import argparse
import dataclasses
from pathlib import Path

from .samples import SAMPLE_DATABASE, get_sample
from .spectrometer import PLSpectrometer


def build_parser():
    parser = argparse.ArgumentParser(
        prog="plsim",
        description="Photoluminescence spectrometer simulator (xenon lamp, dye samples, photodiode).",
    )
    parser.add_argument("--sample", default="cy3", help="sample from the database (default: %(default)s)")
    parser.add_argument("--list-samples", action="store_true", help="print the sample database and exit")
    parser.add_argument("--lambda-exc", type=float, default=550.0, metavar="NM",
                        help="excitation wavelength (default: %(default)s)")
    parser.add_argument("--range", dest="detection_range", type=float, nargs=2, default=(500.0, 750.0),
                        metavar=("LAMBDA_MIN", "LAMBDA_MAX"),
                        help="PL detection range in nm (default: %(default)s)")
    parser.add_argument("--dlambda", type=float, default=1.0, metavar="NM",
                        help="step size for PL detection (default: %(default)s)")
    parser.add_argument("--peak-absorbance", type=float, default=None, metavar="A",
                        help="sample absorbance at the absorption peak (default: 1.0)")
    parser.add_argument("--scatter", type=float, default=0.01, metavar="FRACTION",
                        help="fraction of excitation light reaching the detector (default: %(default)s)")
    parser.add_argument("--ideal", action="store_true",
                        help="ideal instrument: no stray excitation light")
    parser.add_argument("--out", type=Path, default=None, metavar="PNG",
                        help="output file (default: out/<sample>_<lambda_exc>nm.png)")
    parser.add_argument("--show", action="store_true", help="open a window instead of writing a file")
    return parser


def list_samples():
    """One line per dye in the sample database."""
    lines = []
    for key, dye in SAMPLE_DATABASE.items():
        lines.append(
            "{:<16} {:<14} excitation {:>5.0f} nm  emission {:>5.0f} nm  quantum yield {:g}".format(
                key,
                dye.name,
                dye.absorption.center_nm,
                dye.emission.center_nm,
                dye.quantum_yield,
            )
        )
    return "\n".join(lines)


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.list_samples:
        print(list_samples())
        return 0

    sample = get_sample(args.sample)
    if args.peak_absorbance is not None:
        sample = dataclasses.replace(sample, peak_absorbance=args.peak_absorbance)

    if not args.show:
        import matplotlib
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from .plot import plot_scan

    spectrometer = PLSpectrometer(
        sample=sample,
        scatter_fraction=0.0 if args.ideal else args.scatter,
    )
    scan = spectrometer.acquire(
        lambda_exc_nm=args.lambda_exc,
        lambda_min_nm=args.detection_range[0],
        lambda_max_nm=args.detection_range[1],
        dlambda_nm=args.dlambda,
    )

    print("sample           : {} ({})".format(sample.name, sample.solvent))
    print("quantum yield    : {:g}".format(sample.quantum_yield))
    print(
        "excitation       : {:g} nm, power {:.4g} (relative units)".format(
            scan.lambda_exc_nm, scan.excitation_power
        )
    )
    print(
        "detection range  : {:g} - {:g} nm, step {:g} nm ({} points)".format(
            scan.wavelengths_nm[0], scan.wavelengths_nm[-1], args.dlambda, scan.wavelengths_nm.size
        )
    )
    print("absorbed fraction: {:.3f} of the excitation light".format(sample.absorbed_fraction(scan.lambda_exc_nm)))
    print("PL peak          : {:.1f} nm".format(scan.emission_peak_nm))
    if scan.excitation_power < 1e-6:
        print("note             : the harmonic filter blocks this excitation wavelength")
    if scan.scatter_inside_range:
        print("note             : stray excitation light shows up at {:g} nm".format(scan.lambda_exc_nm))

    out_path = args.out
    if out_path is None and not args.show:
        slug = sample.name.lower().replace(" ", "-")
        out_path = Path("out") / "{}_{:g}nm.png".format(slug, scan.lambda_exc_nm)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    figure = plot_scan(scan, path=out_path, show=args.show)
    plt.close(figure)
    if out_path is not None:
        print("figure           : {}".format(out_path))
    return 0
