"""Crystallite-size study for items 2 and 3: the numbers the report quotes.

Writes report/size_table.md and returns the same rows to the report builder.
"""

from __future__ import annotations

import pathlib

from xrdsim.analysis import find_peaks, scherrer_from_peak
from xrdsim.diffractometer import Instrument, scan
from xrdsim.profile import caglioti_fwhm, size_fwhm
from xrdsim.samples import get_phase

HERE = pathlib.Path(__file__).resolve().parent
TABLE = HERE / "size_table.md"

SIZES_A = [50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0]   # 5 nm to 500 nm
HKLS = [(1, 1, 1), (2, 2, 0), (4, 0, 0)]
STEP = 0.002
BASE = Instrument(
    reference_counts=100_000.0, background_rate=0.0, ka2=False, rng_seed=None
)


def rows() -> list[dict]:
    si = get_phase("si")
    out = []
    for size in SIZES_A:
        result = scan(si, 12.0, 75.0, STEP, BASE, size_a=size)
        peaks = find_peaks(result.two_theta, result.counts)
        by_angle = {round(peak.two_theta, 1): peak for peak in peaks}
        for hkl in HKLS:
            predicted = next(row for row in result.reflections if row.hkl == hkl)
            peak = min(peaks, key=lambda p: abs(p.two_theta - predicted.two_theta))
            instrumental = caglioti_fwhm(peak.two_theta, *BASE.caglioti)
            predicted_size = size_fwhm(size, peak.two_theta, BASE.wavelength)
            try:
                recovered = scherrer_from_peak(peak, instrumental, BASE.wavelength) / 10.0
            except ValueError:
                recovered = float("nan")
            out.append({
                "size_nm": size / 10.0,
                "hkl": "".join(str(v) for v in hkl),
                "two_theta": peak.two_theta,
                "fwhm": peak.fwhm,
                "instrument_fwhm": instrumental,
                "predicted_size_fwhm": predicted_size,
                "height": peak.height,
                "area": peak.area,
                "recovered_nm": recovered,
            })
    return out


def build() -> str:
    data = rows()
    lines = [
        "# Crystallite-size study",
        "",
        "Silicon, Cu K-alpha1 only (the doublet would confuse a width measurement), "
        f"step {STEP} deg, 100 000 counts at the strongest line, no counting noise.",
        "",
        (
            "| D (nm) | hkl | 2theta (deg) | FWHM (deg) | instrument FWHM "
            "| height (counts) | area (counts deg) | Scherrer (nm) |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in data:
        lines.append(
            f"| {row['size_nm']:.0f} | {row['hkl']} | {row['two_theta']:.3f} | "
            f"{row['fwhm']:.4f} | {row['instrument_fwhm']:.4f} | {row['height']:.0f} | "
            f"{row['area']:.0f} | {row['recovered_nm']:.0f} |")
    text = "\n".join(lines) + "\n"
    TABLE.write_text(text, encoding="utf-8")
    print(f"wrote {TABLE} ({len(data)} rows)")
    return text


if __name__ == "__main__":
    build()
