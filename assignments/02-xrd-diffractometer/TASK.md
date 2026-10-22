# TASK.md — Assignment 2: XRD diffractometer simulation

Status: working spec, compiled 2026-10-22. The assignment brief has **not been received
yet**; every place that needs it is marked `AWAITING BRIEF` and stays empty until the
brief arrives. Sources are quoted verbatim; anything that is our reading rather than the
assignment's own words is marked **Inference**.

Course framing: "Nanotechnology & Quantum Physics" (report title page) / the nano capsule
class, quantum physics section (OBODA's words). Class notes for this assignment:
`AWAITING BRIEF`.

---

## 1. Where our information comes from

| source | what it gives us |
| --- | --- |
| `AWAITING BRIEF` — the graded statement (Canvas announcement / whiteboard photo / slide / PDF) | the deliverables, their weights and the submission rules |
| `AWAITING BRIEF` — class notes, with heading and date | the diffractometer chain the design must model |
| OBODA, 2026-10-22 | the topic only: "XRD diffractometer simulator", second assignment of the quantum physics section |
| `docs/research/` | three research notes written before the brief: instrument model, analysis and reference data, assignment-1 document conventions. Corrected where they were wrong; see its README |

`AWAITING BRIEF` — one sentence stating which source grades the work and which defines what
the simulator must be able to do, and which one wins where they disagree.
[Assignment 1's rule was: "The announcement grades the work; the board defines what the
simulator must be able to do." Copy that sentence only if the same split is true here.]

---

## 2. The assignment, in its own words

### 2.1 Announcement (verbatim)

> AWAITING BRIEF — paste whole. Keep the brief's own numbering, spelling, units and
> punctuation; do not correct or omit anything.

Note on the weights: `AWAITING BRIEF` — list the weights exactly as printed, show their sum,
and mark any arithmetic repair as **Inference**.

### 2.2 Instrument statement (verbatim transcription)

> AWAITING BRIEF — the whiteboard/slide sketch of the diffractometer: source, optics,
> goniometer, sample, detector.

[Transcribe labels as written. Where a symbol is uncertain, write "transcribed as … could be …
**Verify against the lecture**" and check it before the report quotes it. If the sketch and
the notes conflict, state the conflict and pick a rule.]

### 2.3 Class notes (verbatim transcription, with the drawing read left to right)

> AWAITING BRIEF — note heading and date first, then the chain and any equations written
> beside components.

---

## 3. Requirement-by-requirement, mapped to what exists

### R1 — AWAITING BRIEF (short name, as the brief words it) (AWAITING BRIEF weight)

Verbatim asks: *AWAITING BRIEF*, *AWAITING BRIEF*.

| ask | current artifact | status |
| --- | --- | --- |
| AWAITING BRIEF | AWAITING BRIEF (name files, not intentions) | AWAITING BRIEF |

[A dated Resolution / IMPLEMENTED / Artifact found and FIXED block goes here as defects are
found: what was wrong, what the corrected behaviour is, which file proves it.]

### R2 — AWAITING BRIEF (<weight>%)

Verbatim asks: AWAITING BRIEF.

| ask | current artifact | status |
| --- | --- | --- |
| AWAITING BRIEF | AWAITING BRIEF | AWAITING BRIEF |

[If the brief admits two readings, implement both and say which is which.]

### R3 — AWAITING BRIEF (<weight>%)

Verbatim asks: AWAITING BRIEF.

| ask | current artifact | status |
| --- | --- | --- |
| AWAITING BRIEF | AWAITING BRIEF | AWAITING BRIEF |

### R<n> … repeat until every graded clause and every submission rule has one block.

---

## 4. Sample data the simulator actually uses

`AWAITING BRIEF` — which samples, phases or patterns the brief names, and in what form
(a formula, a mineral name, a measured pattern, a single-crystal structure).

Table to fill once the brief names them; one row per shipped sample:

| sample | space group | lattice parameter(s) | reference pattern | source | confidence |
| --- | --- | --- | --- | --- | --- |
| AWAITING BRIEF | | | | | |

Whatever set of numbers the team settles on, the text and the code must agree; Assignment 1
needed exactly that sentence and it will be needed here.

---

## 5. Reference audit

Run once a draft exists. Five subsections, in this order.

### 5.1 Existence

| # | cited work | DOI in the draft | verdict |
| --- | --- | --- | --- |
| [1] | AWAITING BRIEF | AWAITING BRIEF | verified / **404, does not exist → use …** |

### 5.2 Relevance

| claim in the draft | cited to | what the audit found | fix |
| --- | --- | --- | --- |
| AWAITING BRIEF | AWAITING BRIEF | AWAITING BRIEF | AWAITING BRIEF |

### 5.3 Other audit findings

- AWAITING BRIEF — uncited references, numbers whose stated source is not the repository's
  source, closed-access works that could not be read.

### 5.4 Corrected citation strings, ready to paste

```
AWAITING BRIEF
```

### 5.5 Text in the draft that the corrected figures now contradict

| draft text | what the figures/data show now |
| --- | --- |
| AWAITING BRIEF | AWAITING BRIEF |

---

## 6. Submission format

- `AWAITING BRIEF` — reproduce every administrative rule verbatim: file type, single-file
  rule, naming, deadline, rules about references and code appendix.
- Standing assumption from Assignment 1, to be confirmed against the brief: the report is a
  single PDF that carries its own screenshots, figures, references and code appendix, it is
  regenerable with `uv sync`, and `report/check_pdf.py` gates the built file before upload.

---

## 7. Open questions for the team

1. `AWAITING BRIEF` — every genuine ambiguity in the brief, phrased as a question with two
   answers.
2. `AWAITING BRIEF` — what counts as "using an AI tool" here, and whether prompts are shown.
3. `AWAITING BRIEF` — which model detail is a modelling choice rather than physics
   (Assignment 1's equivalent: measured reference bands vs Gaussian model).
4. What counts as a "screen shot" for this assignment — simulator output written to an image
   file, as in Assignment 1, or a capture of an interactive window?

---

## 8. Definition of done

Report-phase items are unchecked; everything the report depends on is done and verified
(`VERIFICATION.md`).

- [ ] the brief is quoted verbatim in §2 and every weight in it is listed
- [ ] every requirement in §3 has an artifact and a status of done
- [ ] every number the report quotes appears in `report/numbers.md`
- [ ] every shipped datum has a source and a confidence in `data/SOURCES.md`
- [ ] every reference verified for existence and relevance (`report/references/AUDIT.md`)
- [ ] figures audited against their own numbers (`VERIFICATION.md`)
- [ ] clean-room rebuild: figures byte-identical, `numbers.md` identical, PDF builds
- [ ] `report/check_pdf.py` passes on the built PDF
- [ ] §7 questions answered or explicitly declared open

---

## 9. Initial design proposal (not from the brief)

**Inference, not requirement.** This is the design work that does not depend on the missing
brief. It follows Assignment 1's module split so the two assignments read as one course.

### 9.1 Instrument chain

X-ray tube (Cu anode, line focus) → divergence slit → Soller slit → flat sample on a
theta/2theta goniometer → receiving slit → Soller slit → monochromator → detector.
Measured variable: 2theta; the sample sits at theta. Bragg: n·lambda = 2·d·sin(theta).

### 9.2 Fixed instrument constants (Cu K-alpha, to be sourced in `data/SOURCES.md`)

| quantity | value | note |
| --- | --- | --- |
| K-alpha1 | 1.540598 A | primary line |
| K-alpha2 | 1.544426 A | half the K-alpha1 intensity; the doublet |
| K-beta | 1.392250 A | removed by Ni filter or monochromator |
| K-alpha2/K-alpha1 | 0.497 | relative intensity |

### 9.3 User settings (minimal set, mirroring Assignment 1's four)

| setting | meaning |
| --- | --- |
| sample / phase | which structure is in the beam |
| 2theta range | scan start and stop |
| step | scan increment |
| dwell time | counting time per step |
| optional toggles | K-alpha doublet on/off, monochromator on/off, crystallite size D |

### 9.4 Module split (`xrdsim/`)

| file | responsibility |
| --- | --- |
| `lattice.py` | d-spacings for cubic/tetragonal/hexagonal; lattice refinement |
| `atoms.py` | atomic scattering factors, Debye-Waller term |
| `structure.py` | structure factor, multiplicities, systematic absences |
| `sources.py` | tube spectrum, K-alpha doublet, slits |
| `samples.py` | phase database |
| `geometry.py` | theta/2theta, flat-plate absorption, illumination length |
| `profile.py` | pseudo-Voigt, Caglioti resolution function |
| `detector.py` | counting statistics, dead time |
| `diffractometer.py` | the scan that connects them |
| `analysis.py` | peak fitting, Scherrer, indexing |
| `plot.py` | matplotlib rendering |
| `cli.py` | command line interface |

### 9.5 Sanity gates already checked (2026-10-22)

Silicon, a = 5.43102 A, Cu K-alpha1 (computed in the kernel, not copied):

| hkl | d (A) | 2theta K-alpha1 | K-alpha1 - K-alpha2 split |
| --- | --- | --- | --- |
| 111 | 3.1356 | 28.44 | 0.072 |
| 220 | 1.9202 | 47.30 | 0.125 |
| 311 | 1.6375 | 56.12 | 0.152 |
| 400 | 1.3578 | 69.13 | 0.196 |
| 331 | 1.2460 | 76.37 | 0.224 |
| 422 | 1.1086 | 88.03 | 0.275 |

These are the numbers the simulator must reproduce before any figure is made.

### 9.6 Fidelity limits to state in the report

Deliberately not modelled, unless the brief asks for them: Rietveld refinement, anomalous
scattering, texture beyond a simple preferred-orientation factor, K-beta residual, detector
energy discrimination, and absolute intensities (the model is relative, as in Assignment 1).


### 9.7 What exists now (2026-10-22)

The simulator core is written and tested; the report is not. Nothing here depends on the
missing brief, and nothing here is a claim about what the brief will ask for.

| module | state |
| --- | --- |
| `xrdsim/lattice.py` | d-spacings (cubic, tetragonal, hexagonal, orthorhombic), Bragg round trip, cubic lattice refinement |
| `xrdsim/atoms.py` | Waasmaier-Kirfel f0 interpolated from `data/scattering_factors.json`, Debye-Waller term |
| `xrdsim/structure.py` | structure factor from an explicit basis, orbit multiplicities, Lorentz-polarisation |
| `xrdsim/samples.py` | nine phases: Si, Al, Cu, Fe, NaCl, MgO, ZnO, TiO2 rutile and anatase |
| `xrdsim/geom*` | flat-plate footprint, attenuation, penetration depth (`geometry.py`) |
| `xrdsim/sources.py` | Cu K-alpha1/K-alpha2/K-beta lines and the doublet ratio |
| `xrdsim/profile.py` | Gaussian, Lorentzian, pseudo-Voigt, Caglioti FWHM, Scherrer both ways |
| `xrdsim/detector.py` | Poisson counts, noise, dead time |
| `xrdsim/diffractometer.py` | reflection list, the scan, doublet, size broadening, noise |
| `xrdsim/analysis.py` | peak finding with parabolic refinement, FWHM, areas, Scherrer, cubic indexing |
| `xrdsim/plot.py`, `cli.py` | rendering and `python -m xrdsim` with `--list-phases`, `--table`, `--out` |

91 tests pass, including four analytic structure-factor checks and a brute-force orbit count. Every phase reproduces its published strongest line (Si 111 at 28.44, Al 111
38.47, Cu 111 43.30, Fe 110 44.67, NaCl 200 31.69, MgO 200 42.92, ZnO 101 36.25, rutile 110
27.45 deg), and the silicon intensity ratios land at 100 / 58 / 30 / 6 for 111 / 220 / 311 /
400, which is the standard pattern.

### 9.8 Defects found while building, and what fixed them

| defect | symptom | fix |
| --- | --- | --- |
| profile deposited without the step factor | peak areas were 1/step too large; intensities looked right but counts did not scale with the scan step | multiply the unit-area profile by the step |
| every permutation of (hkl) listed as its own reflection | 111 weaker than 220 on silicon, intensities off by integer factors | keep one representative per symmetry family; multiplicities already count the orbit |
| Lorentz-polarisation evaluated at 2theta = 180 deg | a reflection at exactly lambda/2 produced an infinite intensity and every other peak vanished in the normalisation | cap the scan at 150 deg, which is also what a goniometer does |
| hand-written cell constants taken from primitive-cell conversions | rutile 110 at 27.30 instead of 27.45, MgO 111 at 36.57 instead of 36.94 | use conventional room-temperature values and test every phase against its published strongest line |
| hexagonal multiplicity for a general (hk0) reflection | 6 instead of 12; no shipped pattern changed, but any general in-plane family would have been under-weighted | special-position rule (h == 0, k == 0 or h == k gives 6, otherwise 12) | `test_multiplicity_matches_a_brute_force_orbit`, which enumerates the operations independently |
| hand-expanded anatase basis | spurious (001) line at 9.27 deg with 100 % intensity | phase removed until its CIF can be parsed and the basis checked |
| sampled peak heights without sub-bin refinement | heights jittered with the scan step | three-point parabolic refinement of position and height |
