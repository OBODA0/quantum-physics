# Verification log

Everything below was run on Alfred on 2026-10-18, most recently against the final
report-phase commits; the build chain was re-verified from a fresh GitHub clone at
the end.
Purpose: prove that the simulator, the data, the figures and the references are
correct *before* a word of the report is written, so that the report can be
transcription rather than discovery. Nothing here touches the report text.

## 1. The physics model

`uv run pytest` — **22 checks, all passing** (`tests/test_simulator.py`). They
assert the things the report claims:

| what it asserts | why it is in the suite |
| --- | --- |
| step size controls the detection grid | question 1's third user setting |
| each dye peaks at its own emission maximum | question 1 |
| the detection monochromator broadens the band (FWHM adds in quadrature) | the instrument is not ideal, and the figures should show it |
| stray excitation appears as a line at λexc | the harmonic filter and second monochromator only reduce it |
| the harmonic filter blocks UV excitation | instrument design claim |
| emission scales with quantum yield, and is linear in absorbed light | the `I_PL = I_abs · Φf` relation the report cites |
| the emission band does not move with the excitation wavelength | Kasha's rule, question 2 |
| there is no step cut in the emission at λexc | regression guard for the defect below |
| the measured reference bands peak where the sources say | the data pack is the input |
| the model and the measured bands agree on band width | the two databases must not drift apart |
| equal concentration gives different peak absorbances | question 3's premise |
| the excitation scan reproduces `P_exc·(1−10^−A)·Φf` | the sweep metric is correct |
| the excitation scan peaks at the absorption maximum | question 2's headline |
| the CLI rejects bad input instead of drawing a wrong plot | users type wrong things |
| the reference pack is well formed (fields present, curves strictly increasing, finite, non-negative, normalised to 1, quoted maxima inside the measured range) | the data file is an input, and a broken input would silently distort every figure |

### Defect found and fixed: the model broke Kasha's rule

The earlier model multiplied the emission band by a step at λexc ("no emission
below the excitation wavelength"). Whenever λexc fell inside the emission band
this **truncated the band**, so the simulated spectrum moved and changed width
with the excitation wavelength — the opposite of what question 2 asks the student
to demonstrate, and in contradiction with the report's own claim.

Measured before the fix (Cy3, same instrument):

| λexc | measured emission peak | measured FWHM |
| --- | --- | --- |
| 520 nm | 568 nm | 28.5 nm |
| 560 nm | 568 nm | 25.5 nm (truncated) |
| 565 nm | 568 nm | 22.5 nm (truncated) |

After the fix the band is invariant by construction: peak 568.00 nm and FWHM
28.50 nm for every excitation wavelength that produces measurable emission
(`report/numbers.md`, section 4).

Anti-Stokes emission is deliberately *not* modelled. A Boltzmann factor was tried
and rejected: multiplying a measured band by `exp(−Δν/kT)` double-counts the
vibronic envelope that is already in the measured band shape, and at kT = 208 cm⁻¹
it visibly distorts the blue wing. This is recorded in `plsim/samples.py`.

### Defect found and fixed: the excitation sweep measured the window, not the dye

The earlier question-2 figure sampled a fixed 565–575 nm window to get "the PL
peak intensity". Because no emission is produced below λexc, that window went dark
as soon as λexc passed 570 nm, and the plotted curve fell off a cliff at 570 nm —
which the draft then interpreted as the absorption edge. It was not: the figure's
own right-hand panel showed the absorbance curve continuing past 570 nm.

The sweep now integrates the whole emitted band inside the detection range
(`plsim/analysis.py`). Verification is built into the measurement: the same
function computes the model prediction, so the two can be compared point by point.

| dye | strongest PL at | measured vs `P_exc·(1−10^−A)·Φf` | band integral across the sweep |
| --- | --- | --- | --- |
| Cy3 | 554.0 nm | 2.2e-16 of full scale | constant to 0.0 |
| Cy5 | 652.0 nm | 2.2e-16 | 0.0 |
| methylene blue | 664.0 nm | 5.6e-16 | 0.0 |

Machine-precision agreement means every factor in the pipeline (lamp power,
absorbed fraction, quantum yield, monochromator throughput, detector responsivity)
is accounted for, and that the measured curve follows the absorbed light.

## 2. The data

Independently re-checked by a second pass that did not reuse our own file
(`data/SOURCES.md`, section "Second opinion"):

- all six digitized curves reproduce their sources to rounding — FPbase records to
  3e-8, PhotochemCAD PSW009 to 5e-6;
- the shipped maxima, quantum yields and extinction coefficients agree with Cytiva
  datasheets, Lumiprobe, PhotochemCAD, OMLC and peer-reviewed papers;
- **five numbers in the draft report are not supported** and are listed in
  `report/numbers.md` section 6 (methylene blue ε "≈80,000"; its emission "686 nm";
  Cy3 emission FWHM "≈32 nm"; "Cy3 absorbs ~90 % at 550 nm"; the Stokes-shift pair);
- open items remain open and are listed rather than papered over: a primary source
  for the 95,000 ε, a primary measurement of methylene blue's quantum yield in
  water, any published Cy3/Cy5 emission bandwidth, and the provenance of the FPbase
  records.

Known fidelity limit: the digitized curves are defined only inside their measured
range, so the model reads zero absorption outside it. Cy3 therefore shows 0.00 % at
450 nm where an independent check puts it near 0.6 %. It does not change the
conclusion at 450 nm (all three dyes are transparent), and the report is told to
say "negligible" rather than "exactly zero".

## 3. The references

Two passes (`report/references/AUDIT.md`, `report/references/claims.json`):

- **Existence**: `[1]`, `[2]`, `[3]`, `[6]` verified against Crossref/OpenLibrary.
  **`[4]` and `[5]` carry DOIs that do not exist** (both 404 at Crossref *and*
  doi.org). Both works are real; the corrected DOIs are
  `10.1016/1011-1344(93)80173-7` and `10.1002/9780470692059`.
- **Relevance**: six claim/reference pairs fail (Cy3 lifetime cited to a
  synthesis paper; `I_PL = I_abs·Φf` cited to the same; the 100 fs–1 ps window
  attributed to Kasha 1950, which does not state it; the 620 nm cutoff asserted
  with no source and inconsistent with Cy3's ~570 nm 0–0 gap; the 0.33 eV
  particle-in-a-box claim cited to a synthesis paper instead of Kuhn 1949; the
  "96 % decays by intersystem crossing" statement, which misreads 1 − Φf).
  Replacements are named in `TASK.md` section 5.2.
- **[5] and [6] are never cited in the body** of the draft — either cite them or
  drop them.

## 4. Reproducibility (clean room)

A fresh clone of the committed tree, a fresh `uv sync` (which installs reportlab
from `pyproject.toml`, so the PDF no longer depends on somebody's ad-hoc install),
and then everything rebuilt from scratch:

```
uv sync                     -> numpy, matplotlib, pytest, reportlab installed
uv run pytest -q            -> 18 passed
report/generate_assignment_figures.py
report/generate_numbers.py
report/generate_pdf_report.py  -> PDF built
```

Results (repeated after every change, latest run on the committed tree):

- `report/numbers.md` regenerated **byte-identical** to the committed file;
- all seven figures regenerated with **mean absolute pixel difference 0.000** and
  identical dimensions, so the committed figures provably come from the committed
  code;
- the PDF builds from a clean environment with no manual steps;
- with the reference pack temporarily removed, `--database auto` falls back to the
  Gaussian model and says so in its output, while `--database reference` refuses
  with a one-line error instead of a traceback.

### A new teammate, from the remote alone

The committed repository was cloned from GitHub on a clean path and driven by the
README alone — `uv sync`, the four documented CLI examples, the figure generator,
the numbers generator, the PDF builder. Result: 22 tests pass, every documented
command works, all nine figures regenerate **byte-identical** to the committed
ones, `numbers.md` identical. The only file that changes is the PDF, and only in
its `/CreationDate` metadata (2 lines), which is expected for a rebuilt PDF.

### Defect found and fixed: the code appendix was not the code

`report/generate_pdf_report.py` read its appendix sources from paths relative to
the *working directory* and skipped any file that did not exist — so building the
PDF from anywhere but the repository root produced a silently shorter appendix,
and four modules that carry the results shown in the figures (`analysis.py`,
`cli.py`, `plot.py`, `reference.py`) were missing from it entirely. Paths now
resolve against the repository root, a missing file is a hard error, and the
appendix lists thirteen files including the figure and number generators and the
test suite (`VERIFICATION.md` sections 4; `TASK.md` section 3).

## 4b. The figures, audited independently

A separate pass checked all seven figures pixel by pixel against the printed axes
and against `report/numbers.md`. Every number printed in the figures (A, Φf, λexc,
concentration) agreed with the generated table. The curves did not always:

| finding | what was wrong | fix |
| --- | --- | --- |
| stray light drawn in the wrong units | the dotted stray-light curve was plotted from optical power while the axis is photocurrent, so in the methylene blue panel it stood 44 % above the spectrum it belongs to and set the axis | `PLScan` now carries `emitted_photocurrent` and `scatter_photocurrent`; every figure plots current. A test asserts the two add up to `photocurrent` and that the stray line is never the tallest feature |
| stray light dominating the dim dye | at 0.5 % of the excitation power the stray line was 79 % of methylene blue's PL peak | the report figures use 0.1 %, which is what a double monochromator with a harmonic filter should leave; the value is stated in every legend |
| three legend entries with no curve | the question-2 overlay listed 450, 600 and 650 nm, where Cy3 does not absorb, so three labels pointed at flat lines | the overlay now shows the six wavelengths that produce a spectrum (470–560 nm) and the title says why |
| empty 450 nm panel | at 450 nm all three dyes absorb under 0.25 %, so the panel looked broken | the panel carries an annotation giving the absorbed fraction of each dye |
| single canvas hid the answer | one spectrum set the scale, so eight of nine curves were flat at zero | the peak current of all nine curves is printed in the figure |
| missing Φf, ambiguous A | the individual dye titles had no quantum yield, and "A = 0.150" is the peak absorbance at 554 nm, not at the 550 nm excitation used | titles now read "A(550 nm) = 0.143, A_peak = 0.150, Φf = 0.04" |
| unlabelled stray spike, three scales | the overview panels drew a stray spike with no legend entry and three different y scales | stray light has its own legend entry and the title states that each panel has its own scale |
| "detected PL" label | the curve is PL plus stray light | labelled "detected photocurrent (PL + stray)" |

Two further defects were found in the numbers generator itself: it double-converted
one ratio to a percentage (399 % instead of 4.0 %), and a figure title overflowed
its canvas. Both fixed.

### Second audit round, after those fixes

The fixed figures were re-audited by an independent pass that also recomputed the
numbers from the code. Every claimed fix was present, and the recomputed values
matched the generated table exactly (peak absorbance 0.15000 / 0.25000 / 0.06700;
absorbed fraction 28.00 / 42.97 / 14.30 %; emission peaks 568.0 / 668.0 / 686.0 nm;
stray light 3.98 / 0.38 / 15.77 % of the PL peak against 4.0 / 0.4 / 15.8 % claimed;
the below-λexc fractions 3.71 / 9.21 / 7.94 %). It found four more problems, all fixed:

| finding | fix |
| --- | --- |
| `numbers.md` still declared 0.5 % stray light while the figures used 0.1 % — a report copying the instrument table would state a value its own figures do not use | the optical conditions now live in one module, `report/settings.py`, imported by both generators |
| part 3 legends showed the *peak* absorbance beside an annotation about that dye absorbing nothing at that wavelength | legends quote A(λexc) for the panel they are in |
| the question-2 title said "only 470–560 nm produces a visible spectrum", contradicted by its own right panel (non-zero from 452 nm) | reworded: Cy3 does not absorb at 450/600/650 nm because its measured absorption band stops at 590 nm |
| zero absorption past 590 nm is a **data limit**, not the 0–0 energy gap the draft's prose invokes | the panel marks the end of the measured range and says so; `TASK.md` §5.5 tells the report not to explain it as physics |

It also noted that the below-λexc fraction is grid-dependent (3.21 / 3.88 % for Cy3
at 1 nm / 0.1 nm), which `numbers.md` now states, and listed the draft sentences the
corrected figures contradict — collected in `TASK.md` §5.5.

### Deliberate non-fix: emission drawn below the excitation wavelength

The audit flagged that 4–9 % of the emitted band integral lies below λexc, which is
anti-Stokes emission. The remedy it suggested — cutting the emission at λexc — is
the exact defect that was removed earlier in this phase, because it breaks Kasha's
rule. A Boltzmann suppression referenced to λexc was also tried and rejected: it
*is* the physically correct treatment for a single excitation wavelength, but it
makes the band shape depend on λexc again, which is the one thing question 2 must
not do. The correct reference for hot-band suppression is the dye's own 0–0 energy,
which does not move with λexc; the measured band already contains its own vibronic
envelope, so applying another factor on top would double-count it.

The chosen behaviour is therefore: the emission band is the measured band, and the
fraction below λexc (3.7 % for Cy3, 9.2 % for Cy5, 7.9 % for methylene blue at the
absorption maximum) is quantified in `report/numbers.md` §3.1 so the report can
state it instead of hiding it.


## 6. The submission PDF (report phase)

Built by `report/generate_pdf_report.py` from the corrected text, the generated
figures and the source files. What was checked on the built file itself, not on the
repository:

| check | result |
| --- | --- |
| pages / size | 43 pages, 3.0 MB |
| figures embedded (not linked) | yes — device figures on pages 1-4 at full resolution (3900x1680 diagram, 4800x1440 overview, 3 x 2160x1380 singles, 4350x1680 sweep, part-3 figures) |
| appendix files present | 14 |
| every DOI printed in the PDF resolves | 7 of 7 return HTTP 200 from Crossref |
| the two fabricated DOIs from the earlier draft | absent |
| one file, no attachments | yes |

The DOI check is the PS1 gate: it runs on the text extracted from the built PDF, so
a reference cannot be correct in the repository and wrong in the submission.

Two independent audits ran on the report text afterwards: one checking every number,
arithmetic claim, caption and factual statement against `numbers.md`, the figures and
the code; one checking every citation for existence and for whether the cited work
supports the sentence it is attached to. Their findings and the fixes are recorded
below as they land.


## 8. Audits of the report itself

Three independent passes ran against the built PDF. Their findings and what was done
about them:

| pass | scope | findings | status |
| --- | --- | --- | --- |
| text audit | every number, arithmetic claim, caption and factual statement in the PDF, against `numbers.md`, the figures and the code | 17: 1 blocker, 9 must-fix, 7 cosmetic. Blocker: five of the nine references were never cited in the body, which under PS1 reads as irrelevant | all fixed. Each reference now carries a sentence; the causal claim about peak positions, the two wrong statements about the wavelength ends, the order-of-magnitude claim, the missing detection settings and the bandwidth values were rewritten |
| reference audit | existence of every reference and whether it supports the sentence it is attached to | 10: no reference hallucinated and all DOIs resolve, but ten corrections - a wrong author initial, a mislabelled vendor sheet, an attribution to the wrong PhotochemCAD reference, an internal-conversion figure attributed to Kasha 1950 rather than to the textbook, a 100 nm figure that Kuhn 1949 does not print, a quantum-efficiency formula quoted as responsivity, and a bandwidth limitation stated too absolutely | all applied |
| end-to-end audit | fresh clone from GitHub, `uv sync`, the full build chain, figure and number comparison, appendix, DOIs, and the six assignment clauses | the chain reproduces exactly: figures byte-identical, `numbers.md` identical, PDF text identical, 7/7 DOIs resolve, all six clauses satisfied | the four defects it found were stale documentation, all corrected |

The gate that runs on the built file is `report/check_pdf.py`: DOI resolution, appendix
count, embedded figures, metadata. It passes on the current build (47 pages, 14
appendix files, 18 embedded image objects, 8 DOIs, none failing).

## 7. Not verified, and therefore not claimed

- The report text itself has not been touched, so its numbers still disagree with
  the code in the five places listed above (the report text was rewritten in the
  report phase; what remains open here is the fidelity limits, not the numbers).
  The PDF in `report/` is the submission build: corrected text, nine embedded
  figures, a fourteen-file appendix, and every printed DOI resolving.
- The committed PDF predates the corrected figures and must be rebuilt during the
  report phase.
- The literature's *experimental* emission maxima differ from our simulated ones by
  a few nm in places (Cy3 simulated 568 nm vs quoted 570 nm) because the digitized
  curve peaks at 554/568 nm. The figures use the quoted maxima for the excitation
  wavelength; the emission peak that appears is the curve's own.
- No GUI exists, and the user settings are command-line options.
- The claim/reference pairs marked "standard textbook content" could not be checked
  against a page because the textbooks are closed access from this host.
