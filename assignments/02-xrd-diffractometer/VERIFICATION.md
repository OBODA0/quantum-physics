# VERIFICATION.md - Assignment 2 (XRD diffractometer simulator)

Checked on 2026-10-26 on Alfred, at `main` = 28d67cf (45-page PDF, 8 figures, 18 tables, 16
references, 121 tests). Every item states what was run and what it proves. Nothing here is
reported from intent.

## 0. The three graded items

| item | artifact | checked how |
| --- | --- | --- |
| 1. design and screenshots (25%) | Figure 1 (the chain), Figure 2 (in-class specification cases and the Windows Terminal screenshot), Figure 3 (`phase_panel.png`, nine phases), Figure 4 (`size_series.png`, seven sizes), Appendix A of the PDF | every plot regenerates from `report/make_figures.py` (`class_spec_figure()` draws Figure 2(a)-(c)); `terminal_screenshot.png` is a real capture and is checked in; Appendix A carries all 14 `xrdsim/` modules and the three report scripts |
| 2. what changes with domain size (25%) | Table 4 and `report/size_table.md` (21 rows), Figure 5 (`size_laws.png`), Figure 6 (`fwhm_vs_angle.png`) | the table is produced by `report/size_study.py`; the nine headline numbers quoted in the PDF are gated by `report/check_numbers.py` |
| 3. the signals explanation (25%) | report section 5, Figures 7 and 8 (`convolution.png`, `laue.png`), Table 7 (the exact K_N), 16 references | every reference resolved against Crossref, the DOI handle registry, COD or OpenLibrary on 2026-10-22 and 2026-10-26 (`report/references/AUDIT.md`) |

Measured behaviour in the size study (silicon, Cu K-alpha1, step 0.002 deg): the 111 width
goes from 0.0550 deg at 500 nm to 1.6388 deg at 5 nm; the height from 2869 to 96 counts; the
integrated area of 111 stays at 196 counts deg from 10 nm to 500 nm and 195 at 5 nm, where
the +-4 FWHM window starts to overlap 220; the position stays at 28.441 deg for every size.
The Scherrer inversion recovers the input size at every point, 5 to 500 nm.

## 1. Test suite

`cd assignments/02-xrd-diffractometer && uv run pytest -q` -> **121 passed** in 1.6 s (2026-10-26).

What the suite covers, by file:

| file | what it proves |
| --- | --- |
| `tests/test_lattice.py` | d-spacings and Bragg angles against NIST SRM 640d silicon values; cubic refinement recovers the cell to 1e-6; unreachable reflections raise |
| `tests/test_profile_detector.py` | profiles integrate to 1, their FWHM is the declared width, Caglioti follows the polynomial, Scherrer inverts exactly, Poisson mean and spread, dead-time compression |
| `tests/test_geometry_sources.py` | footprint clipping, attenuation, penetration depth, the K-alpha doublet and its weighted mean |
| `tests/test_structure_samples.py` | f0(0) = Z, the Debye-Waller limit, 24 multiplicity cases, FCC/BCC/diamond absences, rocksalt 111 weak, and every phase against its published strongest line |
| `tests/test_diffractometer.py` | silicon peaks at the certified angles, 222 absent, doublet changes the width, size broadens the peaks, Poisson reproducibility, dead time, one reflection per family, intensity ratios 100/58/30/6 |
| `tests/test_analysis.py` | peak finding on synthetic Gaussians, quadrature width subtraction, cubic indexing, the lattice hint, phase identification, Scherrer recovering a 20 nm crystallite within 15 %, Williamson-Hall recovering a synthetic size and strain to 2 % and 5 % |
| `tests/test_structure_samples.py` (end to end) | every phase, simulated and re-measured: each predicted reflection above 5 % is found within 0.1 deg |
| `tests/test_cli.py` | `--list-phases`, `--table`, PNG output, and the missing-phase error |

## 2. Independent numeric checks

| check | expected | observed |
| --- | --- | --- |
| Si 111 / 220 / 311 / 400 2theta (Cu K-alpha1) | 28.441 / 47.301 / 56.120 / 69.127 (SRM 640f Table 1) | 28.441 / 47.301 / 56.120 / 69.127 |
| Si relative intensities 111 / 220 / 311 / 400 | ~100 / 55 / 30 / 5 (standard pattern) | 100 / 58 / 30 / 6 |
| ZnO 100 / 002 / 101 | 31.77 / 34.42 / 36.25 | 31.77 / 34.44 / 36.26 |
| Al 111 | 38.47 | 38.47 |
| Cu 111 | 43.30 | 43.32 |
| Fe 110 | 44.67 | 44.67 |
| NaCl 200 | 31.69 | 31.70 |
| MgO 200 | 42.92 | 42.92 |
| rutile 110 | 27.45 | 27.44 |
| K-alpha1 - K-alpha2 splitting at Si 422 | 0.275 deg (computed) | 0.28 deg in the scan |

Silicon now matches the NIST SRM 640f certificate table to 0.001 deg. The earlier version
of this file quoted 640d numbers against a 640c lattice parameter and blamed the 1.540598
vs 1.5405929 A wavelength convention, which moves 2theta by about 0.0001 deg at 28 deg -
far too little to explain the 0.002 deg it was invoked for. The cell, the label and the
reference values are now the same certificate.

## 2.1 Intensity agreement

Relative intensities, simulated against published powder patterns. The model uses one
uniform Debye-Waller factor (B = 0.5 A^2), no absorption correction and no texture, so
agreement is expected to be good but not exact.

| phase | reflections | model, integrated area | model, peak height | printed card, I/I0 |
| --- | --- | --- | --- | --- |
| Si | 111 / 220 / 311 / 400 | 100 / 64 / 37 / 10 | 100 / 62 / 35 / 8 | 100 / 55 / 30 / 6 |
| Cu | 111 / 200 / 220 / 311 | 100 / 46 / 24 / 27 | 100 / 45 / 21 / 20 | 100 / 46 / 20 / 17 |
| NaCl | 111 / 200 / 220 | 8 / 100 / 64 | 8 / 62 / 40 | 13 / 100 / 55 |
| ZnO | 100 / 002 / 101 | 52 / 40 / 100 | 52 / 40 / 100 | 57 / 44 / 100 |
| rutile TiO2 | 110 / 101 / 211 | 100 / 45 / 55 | 100 / 45 / 51 | 100 / 50 / 60 |

These are the numbers behind Table 3 of the PDF; the card values are the ICDD PDF entries
named in that table (04-0829, 05-0628, 36-1451, 21-1276, 27-1402) for the phases the
database has, and published patterns otherwise.

The low-angle ratios agree closely; the high-angle ones run high even after the peak-height
column is used (Si 400 at 8 against 6, Cu 311 at 20 against 17, rutile 211 at 51 against 60
in the other direction). Part of that is a definition: the model returns an integrated area
while cards list peak heights, and the instrument width grows with angle. The rest is the
untuned model: no absorption correction, one Debye-Waller factor for every site, a single
2theta-dependent LP factor. This is recorded rather than tuned; fitting B per site would be
fitting, not physics.

## 2.2 Clean-room rebuild

Checked on 2026-10-22: a fresh `git clone` of the repository into `/tmp/clean3`,
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

produced **116 passed** and **PASS**, and `git status` in the clone was **empty**: every
figure, the reflection table and the PDF came out byte-identical to the committed ones.
The PDF is deterministic because `reportlab.rl_config.invariant` fixes its timestamps and
document id.

## 2.3 Robustness sweep

`uv run python -m tools.sweep` reproduces the sweep below: 567 scans, 0 failures, about
12 s. Every phase is covered:

| dimension | values |
| --- | --- |
| range and step | 20-90 at 0.02 deg, 10-150 at 0.05, 60-61 at 0.001 |
| crystallite size | none, 1 nm, 10 um |
| options | default, K-alpha2 off, monochromator at 26.6 deg, 1 mm specimen displacement, dead time 0.1 ms, Poisson seed, no background |

**0 failures**. Every scan returned equal-length arrays and no negative
counts. The command line interface rejects an unknown phase, a reversed range, a zero step
and a negative size with `xrdsim: error: ...` and exit status 2, not a traceback.

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
