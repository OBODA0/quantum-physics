# VERIFICATION.md - Assignment 2 (XRD diffractometer simulator)

Checked on 2026-10-22 on Alfred, at commit `c8d2ab7`. Every item states what was run and
what it proves. Nothing here is reported from intent.

## 1. Test suite

`cd assignments/02-xrd-diffractometer && uv run pytest -q` -> **92 passed** (commit `60a57db`).

What the suite covers, by file:

| file | what it proves |
| --- | --- |
| `tests/test_lattice.py` | d-spacings and Bragg angles against NIST SRM 640d silicon values; cubic refinement recovers the cell to 1e-6; unreachable reflections raise |
| `tests/test_profile_detector.py` | profiles integrate to 1, their FWHM is the declared width, Caglioti follows the polynomial, Scherrer inverts exactly, Poisson mean and spread, dead-time compression |
| `tests/test_geometry_sources.py` | footprint clipping, attenuation, penetration depth, the K-alpha doublet and its weighted mean |
| `tests/test_structure_samples.py` | f0(0) = Z, the Debye-Waller limit, 24 multiplicity cases, FCC/BCC/diamond absences, rocksalt 111 weak, and every phase against its published strongest line |
| `tests/test_diffractometer.py` | silicon peaks at the certified angles, 222 absent, doublet changes the width, size broadens the peaks, Poisson reproducibility, dead time, one reflection per family, intensity ratios 100/58/30/6 |
| `tests/test_analysis.py` | peak finding on synthetic Gaussians, quadrature width subtraction, cubic indexing on silicon, Scherrer recovers a 20 nm crystallite within 15 % |
| `tests/test_cli.py` | `--list-phases`, `--table`, PNG output, and the missing-phase error |

## 2. Independent numeric checks

| check | expected | observed |
| --- | --- | --- |
| Si 111 / 220 / 311 / 400 2theta (Cu K-alpha1) | 28.4425 / 47.3034 / 56.1211 / 69.1295 | 28.441 / 47.300 / 56.120 / 69.126 |
| Si relative intensities 111 / 220 / 311 / 400 | ~100 / 55 / 30 / 5 (standard pattern) | 100 / 58 / 30 / 6 |
| ZnO 100 / 002 / 101 | 31.77 / 34.42 / 36.25 | 31.77 / 34.44 / 36.26 |
| Al 111 | 38.47 | 38.47 |
| Cu 111 | 43.30 | 43.32 |
| Fe 110 | 44.67 | 44.67 |
| NaCl 200 | 31.69 | 31.70 |
| MgO 200 | 42.92 | 42.92 |
| rutile 110 | 27.45 | 27.44 |
| K-alpha1 - K-alpha2 splitting at Si 422 | 0.275 deg (computed) | 0.28 deg in the scan |

The 0.002-0.007 deg residuals on silicon come from the wavelength convention: NIST
certificates quote 1.5405929 A, the simulator uses 1.540598 A. That is stated in
`data/SOURCES.md` and is smaller than the peak width.

## 2.1 Intensity agreement

Relative intensities, simulated against published powder patterns. The model uses one
uniform Debye-Waller factor (B = 0.5 A^2), no absorption correction and no texture, so
agreement is expected to be good but not exact.

| phase | reflections | simulated I/I0 | published |
| --- | --- | --- | --- |
| Si | 111 / 220 / 311 / 400 | 100 / 58 / 30 / 6 | 100 / 55 / 30 / 5 |
| Cu | 111 / 200 / 220 / 311 | 100 / 41 / 16 / 15 | 100 / 46 / 20 / 17 |
| NaCl | 111 / 200 / 220 | 6 / 100 / 54 | 13 / 100 / 55 |
| ZnO | 100 / 002 / 101 | 50 / 38 / 100 | 57 / 44 / 100 |
| rutile TiO2 | 110 / 101 / 211 | 100 / 43 / 37 | 100 / 50 / 60 |

The largest deviation is rutile 211 (37 against 60) and NaCl 111 (6 against 13). Both are
weak-line cases where the difference of two form factors is small, so the result is
sensitive to the tabulated f0 and to B. This is recorded rather than tuned: adjusting B per
site to fit published intensities would be fitting, not physics.

## 2.2 Clean-room rebuild

Checked at commit `9104084`: a fresh `git clone` of the repository into `/tmp/clean3`,
then

```
uv sync
uv run pytest
uv run python -m report.make_figures
uv run python -m report.tables
uv run python -m report.generate_pdf_report
uv run python -m report.check_pdf
uv run python -m report.check_numbers
```

produced **92 passed** and **PASS**, and `git status` in the clone was **empty**: every
figure, the reflection table and the PDF came out byte-identical to the committed ones.
The PDF is deterministic because `reportlab.rl_config.invariant` fixes its timestamps and
document id.

## 3. Defects found and fixed during the build

| defect | how it showed up | fix | proof |
| --- | --- | --- | --- |
| unit-area profile deposited without the step factor | peak areas too large by 1/step; counts did not scale with the scan step | multiply by the step | `test_poisson_noise_is_reproducible_and_proportional` |
| every permutation of (hkl) listed separately | Si 111 weaker than 220 | one representative per symmetry family | `test_only_one_member_of_each_family_is_listed`, `test_silicon_relative_intensities_match_the_standard_pattern` |
| LP evaluated at 2theta = 180 deg | infinite intensity, every other peak normalised to zero | cap at 150 deg | scans run; no non-finite counts |
| cell constants taken from primitive-cell conversions | rutile 110 at 27.30, MgO 111 at 36.57 | conventional room-temperature values | `test_every_phase_reproduces_its_published_strongest_line` |
| hexagonal multiplicity for a general (hk0) reflection | 6 instead of 12; no shipped pattern changed, but any general in-plane family would have been under-weighted | special-position rule (h == 0, k == 0 or h == k gives 6, otherwise 12) | `test_multiplicity_matches_a_brute_force_orbit`, which enumerates the operations independently |
| hand-expanded anatase basis | spurious (001) at 9.27 deg with 100 % intensity | basis taken from the COD CIF expanded by gemmi | (001) now zero, 101 at 25.27 deg with 100 %; `test_every_phase_reproduces_its_published_strongest_line` |
| sampled peak heights | heights jittered with the scan step | parabolic refinement | `test_find_peaks_recovers_positions_widths_and_heights` |

## 4. What is NOT verified

- The Cu K-alpha wavelengths are provisional: no primary table could be read from this host.
- The Caglioti U, V, W are plausible defaults, not fitted to a real instrument.
- Every site ships B = 0.5 A^2; no per-site Debye-Waller value was read.
- No simulated pattern has yet been compared with a *measured* scan. Everything above is
  compared with published peak positions and intensity ratios, which is the strongest check
  available without a diffractogram.
- Absolute intensities are not modelled, by design.
