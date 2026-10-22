"""The numbers the report quotes, computed once.

Both the PDF builder and the gate import this module, so a figure in the text cannot
disagree with the model that produced it.
"""

from __future__ import annotations

from xrdsim.analysis import find_peaks, scherrer_from_peak
from xrdsim.diffractometer import Instrument, reflections, scan
from xrdsim.profile import caglioti_fwhm
from xrdsim.samples import get_phase

SI_HKLS = [(1, 1, 1), (2, 2, 0), (3, 1, 1), (4, 0, 0)]
# the configuration the report's Scherrer sentence refers to
SCHERRER_SIZE_A = 300.0
SCHERRER_STEP = 0.01


def quoted_numbers() -> dict[str, str]:
    si = get_phase("si")
    instrument = Instrument(rng_seed=None)
    rows = {row.hkl: row for row in reflections(si, instrument)}
    top = rows[(1, 1, 1)].intensity

    result = scan(si, 20.0, 90.0, SCHERRER_STEP,
                  Instrument(ka2=False, background_rate=0.0, rng_seed=None),
                  size_a=SCHERRER_SIZE_A)
    sizes = []
    for peak in find_peaks(result.two_theta, result.counts):
        try:
            sizes.append(scherrer_from_peak(
                peak, caglioti_fwhm(peak.two_theta, *instrument.caglioti),
                instrument.wavelength) / 10.0)
        except ValueError:
            continue

    return {
        "si_positions": "/".join(f"{rows[hkl].two_theta:.3f}" for hkl in SI_HKLS),
        "si_ratios": "/".join(f"{100 * rows[hkl].intensity / top:.0f}" for hkl in SI_HKLS),
        "scherrer_range": f"{min(sizes):.1f}-{max(sizes):.1f}",
    }
