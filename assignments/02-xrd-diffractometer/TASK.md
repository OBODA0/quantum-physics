# TASK.md — Assignment 2: XRD diffractometer simulation

Status: working spec, brief received 2026-10-22 (pasted by OBODA from the course
announcement). Sources are quoted verbatim; anything that is our reading rather than the
assignment's own words is marked **Inference**.

Course framing: "Nanotechnology & Quantum Physics" (report title page) / the nano capsule
class, quantum physics section (OBODA's words). The brief refers back to "the part we had
done in the class"; no sketch or notes from that session were supplied, so the report
describes the standard Bragg-Brentano chain the simulator implements and says so.

---

## 1. Where our information comes from

| source | what it gives us |
| --- | --- |
| Course announcement, pasted verbatim by OBODA on 2026-10-22 | the three graded items, their weights and the two PS rules |
| "The part we had done in the class" (referenced by item 1) | the design the report reproduces; no artefact from that session was supplied |
| `docs/research/` | instrument model, analysis and reference data, and assignment-1 document conventions, written before the brief arrived |
| `data/SOURCES.md` | the provenance of every constant the simulator ships |

The announcement grades the work and defines what must be demonstrated; the simulator's
physics defines what can honestly be claimed. Where the two disagree, the report says which
one it follows.

---

## 2. The assignment, in its own words

### 2.1 Announcement (verbatim)

> In this assignment, you are expected the followings:
> 1. Design a XRD system using an AI tool (the part we had done in the class). Show using screen shots that your XRD system can simulate the diffraction patterns of materials with varying crystal structures and size of the crystalline unit . Add your code as appendix. (25%)
>
> 2. What happens to the XRD data if you change the crystal domain size? (25%)
>
> 3. Explain why your observation in part b occurs using your knowledge in signals and systems. (25)  Feel free to use credible sources in your explanations. 
>
> PS: If your references turn out to be hallucinated or irrelevant, you will get 0 from the whole assignment. 
>
> PS2: Upload a single pdf file.

Note on the weights: items are printed `25%`, `25%` and `(25)`. **Inference:** item 3 is
worth 25% and its percent sign was lost in typing; the three items are equally weighted.
Their printed sum is 75%, which the brief does not explain. Assignment 1's three items summed
to 100%. The report therefore treats each item as worth a quarter of the marked work and does
not claim a total.

**Inference:** "part b" in item 3 is item 2. The brief has no part (a)/(b) labels anywhere
else, and item 2 is the only question about changing the domain size.

**Inference:** "size of the crystalline unit" and "crystal domain size" mean the same thing
in this brief: the size of the coherently diffracting domain, that is the crystallite size
`D` in the Scherrer relation. The report states that reading once and uses one word,
*crystallite size*, from then on.

### 2.2 The design from the class

No sketch, slide or note from the class session was supplied with the brief. The simulator
models the standard laboratory chain and the report presents it as such: Cu K-alpha tube,
divergence slit, Soller slits, flat specimen on a theta/2theta goniometer, receiving slit,
optional monochromator, detector. Nothing here is attributed to the class.

### 2.3 Class notes

None supplied. The design and the physics in the report are documented from the sources in
section 5, not from lecture notes.

---

## 3. Requirement-by-requirement, mapped to what exists

### R1 — design, screenshots, code appendix (25%)

Verbatim ask: *"Design a XRD system using an AI tool (the part we had done in the class).
Show using screen shots that your XRD system can simulate the diffraction patterns of
materials with varying crystal structures and size of the crystalline unit . Add your code
as appendix."*

| ask | artifact | status |
| --- | --- | --- |
| an XRD system, built with an AI tool | `xrdsim/` (12 modules), built in this repository with the AI assistant named on the title page | done |
| screenshots of **varying crystal structures** | `report/figures/structures.png`: nine phases spanning diamond, FCC, BCC, rocksalt, wurtzite, tetragonal and rhombohedral-description cells | to produce |
| screenshots of **varying crystallite size** | `report/figures/size_series.png`: one phase at 5, 10, 25, 50, 100 and 500 nm | to produce |
| code appendix | Appendix A of the PDF: every `xrdsim/` module | done |

### R2 — what changes when the domain size changes (25%)

Verbatim ask: *"What happens to the XRD data if you change the crystal domain size? (25%)"*

| ask | artifact | status |
| --- | --- | --- |
| the observation, quantified | `report/figures/size_fwhm.png` (FWHM against 1/D, log-log) and the size table in section 4 | to produce |
| peak height and area behaviour | same table: height, integrated area and FWHM for each size | to produce |
| angular dependence | `report/figures/fwhm_vs_angle.png`: FWHM against 2theta at a fixed size | to produce |

### R3 — why, in signals-and-systems terms (25%)

Verbatim ask: *"Explain why your observation in part b occurs using your knowledge in
signals and systems. (25) Feel free to use credible sources in your explanations."*

| ask | artifact | status |
| --- | --- | --- |
| an explanation grounded in signals and systems | report section 4.3: the crystal as a finite window on a lattice, the diffraction pattern as the magnitude of a Fourier transform, convolution with the instrument response | to write |
| credible sources | five verified sources: Patterson 1939 (DOI), Warren (ISBN), Cullity & Stock (ISBN), Oppenheim & Willsky (ISBN), Bracewell (ISBN) — every one checked against Crossref or OpenLibrary on 2026-10-22 | done |

### PS rules

- **PS1, references.** Every citation in the report is checked for existence **and**
  relevance before it ships; `report/references/AUDIT.md` records what was checked and how.
  No source is cited that was not opened or resolved.
- **PS2, one PDF.** The report is built as a single PDF that carries its screenshots,
  figures, references and code appendix. `report/check_pdf.py` refuses a file with embedded
  attachments or a missing section.

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

- **PS2: one PDF file.** Everything the marker needs — screenshots, figures, references and
  the code appendix required by item 1 — goes inside that one file. Nothing is attached
  separately.
- The PDF is regenerable: `uv sync`, then `uv run python -m report.generate_pdf_report`;
  `report/check_pdf.py` and `report/check_numbers.py` gate the built file before upload.
- No deadline is printed in the brief. The file name follows Assignment 1's pattern:
  `Assignment_2_XRD_Diffractometer_Report.pdf`.

---

## 7. Open questions for the team

1. **The weights sum to 75%, not 100%.** Items are printed 25%, 25%, (25). Is the assignment
   marked out of 75, is one item worth 50%, or is a fourth item missing?
2. **What counts as a "screen shot"?** The report shows simulator output written straight to
   image files, as Assignment 1 did. If a capture of an interactive window is required, the
   figures have to be re-shot.
3. **What must be attributed to the class session?** Item 1 says "the part we had done in the
   class". No artefact from that session was supplied, so the report presents the design as
   the standard Bragg-Brentano chain and does not claim it reproduces a specific sketch.
4. **Citation style.** The brief only requires credible sources. The report uses numbered
   references with DOI or ISBN for every entry.

---

## 8. Definition of done

- [x] the brief is quoted verbatim in §2 and every weight in it is listed
- [x] every requirement in §3 has an artifact named
- [x] R1 figures exist: `phase_panel.png` (structures), `size_series.png`, and Appendix A in the PDF
- [x] R2 figures and the size table exist, with heights, areas, FWHM and recovered sizes
- [x] R3 explanation is written and every claim in it points at a verified source
- [x] every reference checked for existence and relevance (`report/references/AUDIT.md`)
- [ ] every number quoted in the report is produced by `report/numbers_source.py` or the
      generated tables
- [ ] clean-room rebuild: figures, tables and PDF byte-identical
- [ ] `report/check_pdf.py` and `report/check_numbers.py` pass on the built PDF
- [ ] the PDF carries no external attachments (PS2)

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
| `xrdsim/lattice.py` | d-spacings (cubic, tetragonal, hexagonal, orthorhombic) checked against the metric tensor, Bragg round trip, cubic lattice refinement |
| `xrdsim/atoms.py` | Waasmaier-Kirfel f0 interpolated from `data/scattering_factors.json`, Debye-Waller term |
| `xrdsim/structure.py` | structure factor from an explicit basis, orbit multiplicities, Lorentz-polarisation |
| `xrdsim/samples.py` | nine phases: Si, Al, Cu, alpha-Fe, NaCl, MgO, ZnO, TiO2 rutile and anatase |
| `xrdsim/geometry.py` | flat-plate footprint, attenuation, penetration depth, specimen displacement |
| `xrdsim/sources.py` | Cu K-alpha1/K-alpha2/K-beta lines and the doublet ratio |
| `xrdsim/profile.py` | Gaussian, Lorentzian, pseudo-Voigt (scalar and vectorised), Caglioti FWHM, Scherrer both ways |
| `xrdsim/detector.py` | Poisson counts, noise, dead time |
| `xrdsim/diffractometer.py` | reflection list, the scan, doublet, size broadening, noise, displacement |
| `xrdsim/analysis.py` | peak finding with parabolic refinement, FWHM, areas, Scherrer, Williamson-Hall, cubic indexing with a lattice hint, phase identification |
| `xrdsim/plot.py`, `cli.py` | rendering and `python -m xrdsim` with `--list-phases`, `--table`, `--index`, `--scherrer`, `--identify`, `--out` |

The suite passes, including four analytic structure-factor
checks, a brute-force orbit count and a metric-tensor check. Every phase reproduces its
published strongest line (Si 111 at 28.44, Al 111 38.47, Cu 111 43.30, Fe 110 44.67, NaCl
200 31.69, MgO 200 42.92, ZnO 101 36.25, rutile 110 27.45, anatase 101 25.27 deg), and the
silicon intensity ratios land at 100 / 58 / 30 / 6 for 111 / 220 / 311 / 400, which is the
standard pattern.

### 9.8 Defects found while building, and what fixed them

| defect | symptom | fix |
| --- | --- | --- |
| profile deposited without the step factor | peak areas were 1/step too large; counts did not scale with the scan step | multiply the unit-area profile by the step |
| every permutation of (hkl) listed as its own reflection | 111 weaker than 220 on silicon, intensities off by integer factors | keep one representative per symmetry family |
| Lorentz-polarisation evaluated at 2theta = 180 deg | a reflection at lambda/2 produced an infinite intensity and every other peak vanished in the normalisation | cap the scan at 150 deg, which is also what a goniometer does |
| cell constants taken from primitive-cell conversions | rutile 110 at 27.30 instead of 27.45, MgO 111 at 36.57 instead of 36.94 | conventional room-temperature values, and a test against each phase's published strongest line |
| hexagonal multiplicity for a general (hk0) reflection | 6 instead of 12; any general in-plane family would have been under-weighted | special-position rule: h, k or h == k gives 6, otherwise 12; checked by a brute-force orbit count |
| hand-expanded anatase basis | a forbidden (001) line at 9.27 deg with 100 % intensity | basis taken from the COD CIF and expanded by gemmi; (001) is now zero |
| sampled peak heights | heights jittered with the scan step | three-point parabolic refinement of position and height |
| indexing started its search at n^2 = 3 | a body-centred pattern came back as (111), (211), (300) | search from n^2 = 1 and name the lattice from the sequence |
