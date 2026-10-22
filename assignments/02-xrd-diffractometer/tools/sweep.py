"""Robustness sweep: every phase across ranges, crystallite sizes and options.

    uv run python -m tools.sweep

Counts the scans that raise, so the claim in VERIFICATION.md section 2.3 can be reproduced.
"""

from __future__ import annotations

import time

from xrdsim.diffractometer import Instrument, scan
from xrdsim.samples import PHASES

RANGES = [(20, 90, 0.02), (10, 150, 0.05), (60, 61, 0.001)]
SIZES = [None, 10.0, 100_000.0]
OPTIONS = [dict(), dict(ka2=False), dict(monochromator_two_theta=26.6),
           dict(sample_displacement_mm=1.0), dict(dead_time_s=1e-4),
           dict(rng_seed=3), dict(background_rate=0.0)]


def main() -> int:
    cases = [(key, low, high, step, size, options)
             for key in PHASES for low, high, step in RANGES for size in SIZES
             for options in OPTIONS]
    failures = []
    start = time.time()
    for key, low, high, step, size, options in cases:
        try:
            result = scan(PHASES[key], low, high, step, Instrument(**options), size_a=size)
            assert len(result.counts) == len(result.two_theta)
            assert all(count >= 0 for count in result.counts)
        except Exception as error:                      # noqa: BLE001 - the point is to catch any
            failures.append((key, low, high, step, size, options, repr(error)))
    print(f"{len(cases)} scans in {time.time() - start:.1f} s, {len(failures)} failures")
    for failure in failures[:5]:
        print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
