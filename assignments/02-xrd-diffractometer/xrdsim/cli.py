"""Command line interface: `python -m xrdsim`."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib

from . import sources
from .analysis import (find_peaks, identify, index_cubic, lattice_hint,
                       scherrer_from_peak, williamson_hall)
from .diffractometer import Instrument, amorphous_scan, reflections, scan
from .profile import caglioti_fwhm, scherrer_size
from .samples import PHASES, get_phase, simple_cubic


def _instrument(args) -> Instrument:
    return Instrument(
        ka2=not args.no_ka2,
        monochromator_two_theta=args.monochromator,
        reference_counts=args.counts,
        background_rate=args.background,
        dwell_s=args.dwell,
        rng_seed=None if args.noise == 0 else args.noise,
        sample_displacement_mm=args.displacement,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xrdsim", description=__doc__)
    parser.add_argument("--phase", help="phase key (see --list-phases)")
    parser.add_argument("--a", type=float, default=None,
                        help="override lattice constant a in angstrom")
    parser.add_argument("--range", nargs=2, type=float, metavar=("MIN", "MAX"),
                        default=[20.0, 90.0], help="2theta scan range in degrees")
    parser.add_argument("--step", type=float, default=0.02, help="2theta step in degrees")
    parser.add_argument("--dwell", type=float, default=1.0, help="counting time per step, s")
    parser.add_argument("--counts", type=float, default=20_000.0,
                        help="integrated counts at the strongest reflection")
    parser.add_argument("--background", type=float, default=0.5, help="background, counts/s")
    parser.add_argument("--displacement", type=float, default=0.0, metavar="MM",
                        help="sample surface displaced from the goniometer axis")
    parser.add_argument("--size", type=float, default=None,
                        help="crystallite size in angstrom (adds size broadening)")
    parser.add_argument("--size-nm", type=float, default=None,
                        help="crystallite size in nm (adds size broadening)")
    parser.add_argument("--no-ka2", action="store_true", help="drop the K-alpha2 line")
    parser.add_argument("--monochromator", type=float, default=None,
                        help="monochromator 2theta in degrees")
    parser.add_argument("--noise", type=int, default=0,
                        help="Poisson seed; 0 disables counting noise")
    parser.add_argument("--out", type=pathlib.Path, help="write the scan to this image")
    parser.add_argument("--table", action="store_true", help="print the reflection table")
    parser.add_argument("--index", action="store_true",
                        help="index the observed peaks as a cubic pattern")
    parser.add_argument("--scherrer", action="store_true",
                        help="report Scherrer sizes for the observed peaks")
    parser.add_argument("--identify", action="store_true",
                        help="rank the phase database against the simulated pattern")
    parser.add_argument("--list-phases", action="store_true", help="list the phase database")
    args = parser.parse_args(argv)

    if args.list_phases:
        for key, phase in sorted(PHASES.items()):
            print(f"{key:14s} {phase.formula:8s} {phase.space_group:18s} {phase.source}")
        sc = simple_cubic()
        print(f"{'sc':14s} {sc.formula:8s} {sc.space_group:18s} {sc.source}")
        print(f"{'amorphous':14s} {'SiO2':8s} {'non-crystalline':18s} "
              "phenomenological diffuse silica halo at 21.8 deg")
        return 0
    if not args.phase:
        parser.error("--phase is required unless --list-phases is given")

    try:
        return _run(args)
    except (KeyError, ValueError) as error:
        parser.error(str(error).strip('"'))


def _run(args) -> int:
        instrument = _instrument(args)
        if args.phase == "amorphous":
            result = amorphous_scan(args.range[0], args.range[1], args.step, instrument)
            d_eff = scherrer_size(8.8, 21.8, instrument.wavelength) / 10.0
            print("phase      : Amorphous silica (SiO2), non-crystalline")
            print(f"wavelength : {instrument.wavelength:.6f} A")
            print(f"range      : {args.range[0]} - {args.range[1]} deg, step {args.step}")
            print(f"halo       : center 21.800 deg  FWHM 8.8000 deg  D_eff {d_eff:.2f} nm")
            if args.out:
                from .plot import save_scan
                args.out.parent.mkdir(parents=True, exist_ok=True)
                save_scan(result, args.out, title="Amorphous SiO2, diffuse halo")
                print(f"wrote {args.out}")
            return 0

        phase = get_phase(args.phase)
        if args.a is not None:
            if args.a <= 0:
                raise ValueError("lattice constant --a must be positive")
            phase = dataclasses.replace(phase, a=args.a)
        size_a = args.size_nm * 10.0 if args.size_nm is not None else args.size
        result = scan(phase, args.range[0], args.range[1], args.step, instrument,
                      size_a=size_a)

        if args.table:
            strongest = max(row.intensity for row in result.reflections)
            print(f"{'hkl':>10s} {'d (A)':>8s} {'2theta':>8s} {'m':>3s} {'I/I0':>7s}")
            for row in result.reflections:
                if row.intensity < 1e-4 * strongest:
                    continue
                label = "".join(str(v) for v in row.hkl)
                rel_i = 100 * row.intensity / strongest
                print(f"{label:>10s} {row.d:8.4f} {row.two_theta:8.3f} "
                      f"{row.multiplicity:3d} {rel_i:7.2f}")
            return 0

        peaks = find_peaks(result.two_theta, result.counts)
        print(f"phase      : {phase.name} ({phase.formula}), {phase.space_group}, "
              f"a = {phase.a:.4f} A")
        print(f"wavelength : {instrument.wavelength:.6f} A"
              + (" + K-alpha2" if instrument.ka2 else ""))
        print(f"range      : {args.range[0]} - {args.range[1]} deg, step {args.step}")
        print(f"peaks      : {len(peaks)}")
        for peak in peaks[:12]:
            line = (
                f"  {peak.two_theta:8.3f} deg  height {peak.height:9.0f}  "
                f"FWHM {peak.fwhm:.4f}"
            )
            if size_a and not args.scherrer:
                try:
                    inst_w = caglioti_fwhm(peak.two_theta, *instrument.caglioti)
                    size = scherrer_from_peak(peak, inst_w, instrument.wavelength)
                    line += f"  Scherrer {size / 10.0:.1f} nm"
                except ValueError:
                    pass
            print(line)

        if args.index:
            try:
                rows = index_cubic([peak.two_theta for peak in peaks])
            except ValueError as error:
                print(f"indexing failed: {error}")
            else:
                print("indexing   : hkl            2theta")
                for hkl, angle in rows:
                    print(f"             {str(hkl):14s} {angle:7.3f}")
                n_squared = [hkl[0] ** 2 + hkl[1] ** 2 + hkl[2] ** 2 for hkl, _ in rows]
                print(f"lattice    : {lattice_hint(n_squared)}")

        if args.scherrer:
            print("Scherrer   : peak            size (nm)")
            for peak in peaks:
                try:
                    inst_w = caglioti_fwhm(peak.two_theta, *instrument.caglioti)
                    size = scherrer_from_peak(peak, inst_w, instrument.wavelength)
                except ValueError:
                    continue
                print(f"             {peak.two_theta:7.3f}         {size / 10.0:6.1f}")
            try:
                wh_size, wh_strain = williamson_hall(
                    peaks, lambda angle: caglioti_fwhm(angle, *instrument.caglioti),
                    instrument.wavelength)
            except ValueError as error:
                print(f"Williamson-Hall: {error}")
            else:
                note = "" if args.no_ka2 else " (use --no-ka2: shoulders bias the fit)"
                print(
                    f"Williamson-Hall: D = {wh_size / 10.0:.1f} nm, "
                    f"strain = {wh_strain:.5f}{note}"
                )

        if args.identify:
            ranking = identify([peak.two_theta for peak in peaks], PHASES, instrument)
            print("identification: phase          score")
            for key, score in ranking[:5]:
                print(f"                {key:14s} {score:5.2f}")

        if args.out:
            from .plot import save_scan
            args.out.parent.mkdir(parents=True, exist_ok=True)
            save_scan(result, args.out,
                      title=f"{phase.name}, {instrument.wavelength:.4f} A")
            print(f"wrote {args.out}")
        return 0
