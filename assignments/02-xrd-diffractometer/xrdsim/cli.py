"""Command line interface: `python -m xrdsim`."""

from __future__ import annotations

import argparse
import pathlib

from . import sources
from .analysis import find_peaks, scherrer_from_peak
from .diffractometer import Instrument, reflections, scan
from .profile import caglioti_fwhm
from .samples import PHASES, get_phase


def _instrument(args) -> Instrument:
    return Instrument(
        ka2=not args.no_ka2,
        monochromator_two_theta=args.monochromator,
        reference_counts=args.counts,
        background_rate=args.background,
        dwell_s=args.dwell,
        rng_seed=None if args.noise == 0 else args.noise,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xrdsim", description=__doc__)
    parser.add_argument("--phase", help="phase key (see --list-phases)")
    parser.add_argument("--range", nargs=2, type=float, metavar=("MIN", "MAX"),
                        default=[20.0, 90.0], help="2theta scan range in degrees")
    parser.add_argument("--step", type=float, default=0.02, help="2theta step in degrees")
    parser.add_argument("--dwell", type=float, default=1.0, help="counting time per step, s")
    parser.add_argument("--counts", type=float, default=20_000.0,
                        help="integrated counts at the strongest reflection")
    parser.add_argument("--background", type=float, default=0.5, help="background, counts/s")
    parser.add_argument("--size", type=float, default=None,
                        help="crystallite size in angstrom (adds size broadening)")
    parser.add_argument("--no-ka2", action="store_true", help="drop the K-alpha2 line")
    parser.add_argument("--monochromator", type=float, default=None,
                        help="monochromator 2theta in degrees")
    parser.add_argument("--noise", type=int, default=0,
                        help="Poisson seed; 0 disables counting noise")
    parser.add_argument("--out", type=pathlib.Path, help="write the scan to this image")
    parser.add_argument("--table", action="store_true", help="print the reflection table")
    parser.add_argument("--list-phases", action="store_true", help="list the phase database")
    args = parser.parse_args(argv)

    if args.list_phases:
        for key, phase in sorted(PHASES.items()):
            print(f"{key:14s} {phase.formula:8s} {phase.space_group:18s} {phase.source}")
        return 0
    if not args.phase:
        parser.error("--phase is required unless --list-phases is given")

    phase = get_phase(args.phase)
    instrument = _instrument(args)
    result = scan(phase, args.range[0], args.range[1], args.step, instrument,
                  size_a=args.size)

    if args.table:
        strongest = max(row.intensity for row in result.reflections)
        print(f"{'hkl':>10s} {'d (A)':>8s} {'2theta':>8s} {'m':>3s} {'I/I0':>7s}")
        for row in result.reflections:
            if row.intensity < 1e-4 * strongest:
                continue
            label = "".join(str(v) for v in row.hkl)
            print(f"{label:>10s} {row.d:8.4f} {row.two_theta:8.3f} {row.multiplicity:3d} "
                  f"{100 * row.intensity / strongest:7.2f}")
        return 0

    peaks = find_peaks(result.two_theta, result.counts)
    print(f"phase      : {phase.name} ({phase.formula}), {phase.space_group}")
    print(f"wavelength : {instrument.wavelength:.6f} A"
          + (" + K-alpha2" if instrument.ka2 else ""))
    print(f"range      : {args.range[0]} - {args.range[1]} deg, step {args.step}")
    print(f"peaks      : {len(peaks)}")
    for peak in peaks[:12]:
        line = f"  {peak.two_theta:8.3f} deg  height {peak.height:9.0f}  FWHM {peak.fwhm:.4f}"
        if args.size:
            try:
                size = scherrer_from_peak(peak, caglioti_fwhm(peak.two_theta, *instrument.caglioti),
                                          instrument.wavelength)
                line += f"  Scherrer {size / 10.0:.1f} nm"
            except ValueError:
                pass
        print(line)

    if args.out:
        from .plot import save_scan
        args.out.parent.mkdir(parents=True, exist_ok=True)
        save_scan(result, args.out, title=f"{phase.name}, Cu K-alpha")
        print(f"wrote {args.out}")
    return 0
