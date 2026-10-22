"""Turn a COD CIF into a `Phase(...)` block, and check it against a published line.

The lesson this tool encodes: a deposited structure is a starting point, not a citation.
Always pass `--expect hkl:2theta` with the published position of the strongest reflection
and let the tool refuse a phase that does not reproduce it.

Usage:

    uv run python -m tools.phase_from_cif 9008214 --expect 101:25.28
    uv run python -m tools.phase_from_cif 9008214 --cif local.cif --expect 101:25.28
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import tempfile

import gemmi

from xrdsim.diffractometer import Instrument, reflections
from xrdsim.samples import Phase, Site

COD_URL = "http://www.crystallography.net/cod/{cid}.cif"


def fetch(cid: str) -> pathlib.Path:
    """Fetch a COD CIF; the host resets connections intermittently, so try both schemes."""
    target = pathlib.Path(tempfile.gettempdir()) / f"cod-{cid}.cif"
    urls = [COD_URL.format(cid=cid), COD_URL.format(cid=cid).replace("http://", "https://")]
    code = "000"
    for url in urls:
        result = subprocess.run(["curl", "-s", "-m", "20", "-o", str(target), "-w", "%{http_code}",
                                 url], capture_output=True, text=True)
        code = result.stdout.strip()
        if code == "200" and target.exists() and target.stat().st_size > 200:
            return target
    raise SystemExit(f"COD {cid} did not return a CIF (last http {code}). Pass --cif if you "
                     "already have the file.")


def phase_from_cif(path: str, key: str, name: str, formula: str, cid: str = "") -> Phase:
    doc = gemmi.cif.read(path)
    structure = gemmi.make_small_structure_from_block(doc.sole_block())
    cell = structure.cell
    sites = tuple(
        Site(site.type_symbol, site.fract.x % 1.0, site.fract.y % 1.0, site.fract.z % 1.0,
             occupancy=site.occ)
        for site in structure.get_all_unit_cell_sites()
    )
    hexagonal = abs(cell.gamma - 120.0) < 0.5
    return Phase(
        key=key, name=name, formula=formula,
        space_group=structure.spacegroup_hm or "unknown",
        a=cell.a, c=cell.c, hexagonal=hexagonal, sites=sites,
        source=f"COD {cid or 'CIF'}; basis expanded by gemmi from the deposited CIF",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="phase_from_cif", description=__doc__)
    parser.add_argument("cid", help="COD id, for example 9008214")
    parser.add_argument("--key", default=None, help="phase key, defaults to cod-<id>")
    parser.add_argument("--name", default=None, help="display name, defaults to the formula")
    parser.add_argument("--formula", default=None, help="chemical formula")
    parser.add_argument("--cif", default=None, help="read this CIF instead of fetching")
    parser.add_argument("--expect", default=None, metavar="HKL:2THETA",
                        help="published strongest line, for example 101:25.28")
    args = parser.parse_args(argv)

    source = pathlib.Path(args.cif) if args.cif else fetch(args.cid)
    phase = phase_from_cif(str(source), args.key or f"cod-{args.cid}",
                           args.name or (args.formula or args.cid),
                           args.formula or "?", cid=args.cid if not args.cif else "")
    rows = [row for row in reflections(phase, Instrument()) if row.intensity > 1e-9]
    rows.sort(key=lambda row: -row.intensity)
    print(f"# {phase.name} {phase.space_group} a={phase.a:.4f} c={phase.c or 0:.4f} "
          f"sites={len(phase.sites)}", flush=True)
    print("# strongest predicted lines:")
    for row in rows[:5]:
        print(f"#   {''.join(str(v) for v in row.hkl):>4s} {row.two_theta:7.2f} deg")

    if args.expect:
        hkl_text, angle_text = args.expect.split(":")
        expected_hkl = tuple(int(ch) for ch in hkl_text)
        best = max(rows, key=lambda row: row.intensity)
        if best.hkl != expected_hkl:
            raise SystemExit(f"REFUSED: strongest line is {best.hkl}, expected {expected_hkl}")
        if abs(best.two_theta - float(angle_text)) > 0.1:
            raise SystemExit(f"REFUSED: {hkl_text} sits at {best.two_theta:.2f} deg, "
                             f"published {angle_text} deg")

    print("")
    print(f'    "{phase.key}": Phase(')
    print(f'        key="{phase.key}", name="{phase.name}", formula="{phase.formula}",')
    print(f'        space_group="{phase.space_group}",')
    cell = f"a={phase.a:.4f}" + (f", c={phase.c:.4f}" if phase.c else "")
    if phase.hexagonal:
        cell += ", hexagonal=True"
    print(f"        {cell}, sites=(")
    for site in phase.sites:
        print(f'            Site("{site.element}", {site.x:.4f}, {site.y:.4f}, {site.z:.4f}),')
    print("        ),")
    print(f'        source="{phase.source}"),')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
