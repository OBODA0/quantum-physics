# TASK.md — Assignment 1: PL spectrometer simulation

Status: working spec, compiled 2026-10-18. Sources are quoted verbatim; anything
that is our reading rather than the assignment's own words is marked **Inference**.

Course framing: "Nanotechnology & Quantum Physics" (report title page) / the nano
capsule class, quantum physics section (OBODA's words). Class notes are headed
`W31L2` and dated `15/10`.

---

## 1. Where our information comes from

| source | what it gives us |
| --- | --- |
| Whiteboard photo (in-class task statement) | the simulator specification: source, user settings, output, sample database |
| Handwritten class notes photo (`W31L2 15/10`) | the instrument chain the design must model, plus the PL taxonomy |
| Announcement text (pasted by OBODA) | the graded deliverables, weights and the two PS rules |

**The board and the announcement must both be satisfied.** The announcement grades
the work; the board defines what the simulator must be able to do.

---

## 2. The assignment, in its own words

### 2.1 Announcement (verbatim)

> In this assignment, you are expected the followings:
> 1. Design a PL spectrometer system using an AI tool. (the part we had started in the class). Show using screen shots that your PL spectrometer can simulate the spectra of the dyes Cy3, Cy5, and methyleneblue. Add your code as appendix. (25%)
>
> 2. Pick one of these three dyes and then change the excitation wavelength from 400 nm to 700 nm. What do you observe (add your screen shots)? Do your observations fit with the results in the literature? Comment on the reasons of your observations in the light of literature. Make sure to give references. (50%)
>
> 3. Plot the emission spectra of these three dyes on the same graph as you set the excitation wavelength as 450, 550, and 650 nm. The peaks should not be the same if the dye concentrations in the samples are the same. Why? (25)
>
> PS: If your references turn out to be hallucinated or irrelevant, you will get 0 from the whole assignment.
>
> PS2: Upload a single pdf file.

Note on the weights: items are marked `25%`, `50%`, `(25)` — item 3's marker is
missing its percent sign, so the three weights sum to 100±. **Inference:** item 3
is worth 25%.

### 2.2 Whiteboard (verbatim transcription)

> Design a PL spectrometer simulator, such that   (PL)
> • uses Xenon lamp at the excitation end,
> • User settings: λexc → excitation wavelength
>   λmin – λmax → PL detection range
>   Δλ → step-size for PL detection
> • at the output → detect the PL spectrum of a sample.
> • Sample database → organic dyes: Cy3 & Cy5
>   → Methylene blue

The board's right margin also carries two small sketches, one arrow-like and one
wave-like; they are not labelled and are not part of any requirement we can
identify. **Inference:** they are a doodle of an excitation arrow and an emission
wave, not a specification.

### 2.3 Class notes (verbatim transcription, with the drawing read left to right)

> `W31L2  15/10`
> • Photoluminescence { electro, chemo, bio }
> • Photoluminescence Spectroscopy (excitation)
>
> white emitter → monochromator → (λ) → optical filter → λexc → SAMPLE
> "sample is excited by λexc & photoluminescence occurs" → monochromator → photodetector → computer
>
> "optical filter: block harmonics"
> "monochromator: splits individual wavelengths s.t. the light received by the photodetector has single wavelength"
> "responsibility (λ)"  (i.e. responsivity; written as a function of wavelength)
> the relation written next to the photodetector/computer is transcribed as `P(λ) = R(λ) I`
> read as: detected signal = responsivity(λ) × incident intensity. This is the least
> certain item on the page — the symbol after `P(λ) =` could be `R(λ)·I`, `R(λ)/I` or a
> two-line expression. **Verify against the lecture before quoting it in the report.**

Note the one conflict between the two images: the notes start from a **white
emitter / monochromator**, the board requires a **xenon lamp at the excitation
end**. The board wins for the simulator; the notes' chain (harmonic filter,
second monochromator, photodetector with spectral responsivity) is what the
design must reproduce after the lamp.

---

## 3. Requirement-by-requirement, mapped to what exists

### R1 — design + screenshots of the three dyes (25%)

Verbatim asks: *"Design a PL spectrometer system using an AI tool"*, *"Show using
screen shots that your PL spectrometer can simulate the spectra of the dyes Cy3,
Cy5, and methyleneblue"*, *"Add your code as appendix"*.

| ask | current artifact | status |
| --- | --- | --- |
| design of the system | `plsim/` (lamp → monochromator → harmonic filter → sample → monochromator → photodiode) | done |
| the three dye spectra | `report/report_figures/part1_cy3.png`, `part1_cy5.png`, `part1_methylene-blue.png` + `part1_combined_overview.png` | done — these figures are the "screenshots" (see the note below); the PDF currently embeds only the overview, the three individual panels can be added |
| code as appendix | `report/Assignment_1_...Report.pdf`, appendix listing 13 files: every `plsim` module, the figure and number generators, and the test suite | done (paths now resolve against the repository root; a missing file is an error rather than a shorter appendix) |
| "using an AI tool" | not stated anywhere in the report | **gap — name the tool and how it was used** |

**Resolved (2026-10-18):** "screen shots" means the graphs themselves — see the
"Screenshots" note above. Six captures of the simulator were built and thrown
away; a terminal photograph shows a command, not a spectrum.

### R2 — excitation sweep 400 → 700 nm on one dye (50%)

Verbatim asks: *"Pick one of these three dyes and then change the excitation
wavelength from 400 nm to 700 nm"*, *"What do you observe (add your screen
shots)?"*, *"Do your observations fit with the results in the literature?"*,
*"Comment on the reasons of your observations in the light of literature"*,
*"Make sure to give references"*.

| ask | current artifact | status |
| --- | --- | --- |
| pick one dye | Cy3 | done |
| sweep λexc 400 → 700 nm | 8 overlaid spectra (450…610 nm) + 151-point sweep (2 nm steps) in `part2_cy3_excitation_sweep.png` | done, but see the artifact below |
| observations | §2.1 of the report, 4 numbered observations | done |
| screenshots | none, same gap as R1 | **gap** |
| fit to literature + reasons | §2.2 of the draft (Kasha's rule, internal conversion vs ns emission, Stokes shift, excitation spectrum vs absorbance) | substance is there; the "exactly mirrors A(λ)" claim and the 620 nm cutoff reasoning must be rewritten (section 5.2) |
| references | 6 references listed, 2 DOIs broken — see §5 | **must fix** |

The sweep as implemented: detection window 500–750 nm; the "PL peak intensity"
curve is sampled in a fixed **565–575 nm** window.

**Artifact found and FIXED (2026-10-18).** The draft measured the "PL peak
intensity" in a fixed 565–575 nm window. Because no emission is produced below
λexc, that window went dark as soon as λexc passed 570 nm, so the curve fell off a
cliff at 570 nm — the detection window, not the dye's absorption edge. The draft
read that cliff as physics.

The sweep now integrates the whole emitted band inside the detection range
(`plsim/analysis.py`), and the same function computes `P_exc·(1−10^−A)·Φf` beside
it: the two agree to ~1e-16 of full scale for all three dyes, and the band integral
is constant across the sweep (`VERIFICATION.md`, section 1). The remaining honest
nuance to write up: the measured intensity carries the xenon lamp spectrum as a
weight, so it tracks `P_exc(λ)·(1−10^−A(λ))`, which is *close to but not identical
with* A(λ) — the corrected figure shows both curves, so the text must not claim an
exact mirror.

### R3 — three dyes, one graph, at 450 / 550 / 650 nm (25%)

Verbatim: *"Plot the emission spectra of these three dyes on the same graph as you
set the excitation wavelength as 450, 550, and 650 nm. The peaks should not be the
same if the dye concentrations in the samples are the same. Why?"*

**Ambiguity, deliberately covered both ways:** "on the same graph … as you set the
excitation wavelength as 450, 550, and 650" can mean one graph per excitation
wavelength, or all curves on a single canvas. The team produced both:
`part3_three_dyes_comparison.png` (three panels, one per λexc) and
`part3_single_canvas_overlay.png` (single canvas). **Inference:** keeping both is
the safe move; the PDF should say which is which.

| ask | artifact | status |
| --- | --- | --- |
| 3 dyes × 3 excitation wavelengths | both part 3 figures, on shared absolute axes | done |
| "why?" answer | §3 of the report: ε(λexc), Φf, detector responsivity, lamp radiance, chromophore structure | done |
| "same concentrations" premise | the model uses `peak_absorbance = 1.0` for all three dyes, i.e. **equal peak optical density, not equal concentration** | **must be stated or changed** |

That last point matters and is easy to get wrong in front of a marker: with equal
concentration `c` and path length `l`, the peak absorbance differs per dye because
ε differs (150,000 vs 250,000 vs 67,000 M⁻¹cm⁻¹). Equal *concentration* and equal
*absorbance* are different experiments and give different peak heights. The draft
says "identical peak optical density / concentration", which conflates the two.

**IMPLEMENTED (2026-10-18).** `plsim.samples.with_concentration()` sets
`A_peak = ε·c·l`, and every figure now runs at 1 µmol/L in a 1 cm cuvette. The
resulting peak absorbances are 0.150 (Cy3), 0.250 (Cy5) and 0.067 (methylene blue):
same concentration, three different absorbances, which is the answer question 3 is
fishing for. Absorbed fractions at the three assigned wavelengths are in
`report/numbers.md`, section 3.

---

## 4. Sample data the simulator actually uses

Quantum yields and band widths come from `data/SOURCES.md` (39 sources, 34 URLs);
`data/reference_spectra.json` holds digitized measured curves, used by default
(`--database auto`), with the Gaussian model available via `--database model`.

| dye | λabs | λem | QY (solvent) | ε (M⁻¹cm⁻¹) |
| --- | --- | --- | --- | --- |
| Cy3 | 550 nm | 570 nm | 0.04 (free dye, PBS) | 150,000 |
| Cy5 | 649 nm | 670 nm | 0.28 (aqueous; range 0.19–0.30) | 250,000 |
| Methylene blue | 664 nm | 685 nm | 0.02 (water; 0.04 is the ethanol value) | 67,000–107,800 |

The report body still carries the pre-source numbers (MB Φf = 0.04, λem = 686 nm,
Cy3 emission FWHM ≈ 32 nm) while its own code appendix prints 0.02, 685 nm and
28.6 nm. Whatever set of numbers the team wants, the text and the code must agree.

---

## 5. Reference audit

PS1 makes this the highest-stakes item in the assignment: hallucinated or
irrelevant references ⇒ 0 for everything. Two audits were run on 2026-10-18
against Crossref, doi.org, OpenLibrary, PubMed and Europe PMC, and the full
detail is in `report/references/AUDIT.md` with machine-readable verdicts in
`report/references/claims.json`.

### 5.1 Existence: two DOIs in the draft do not exist

| # | cited work | DOI in the draft | verdict |
| --- | --- | --- | --- |
| [1] | Kasha 1950, *Discussions of the Faraday Society* 9, 14–19 | 10.1039/DF9500900014 | **verified** — title, author, journal, volume, year match |
| [2] | Lakowicz 2006, *Principles of Fluorescence Spectroscopy* 3rd ed. | 10.1007/978-0-387-46312-4 | **verified** (ISBN 978-0-387-31278-1 matches; text closed, not read) |
| [3] | Mujumdar et al. 1993, *Bioconjugate Chem.* 4(2), 105–111 | 10.1021/bc00020a001 | **verified** — exact match on title, all five authors, volume, pages |
| [4] | Tuite & Kelly 1993, *J. Photochem. Photobiol. B* 21(2-3), 103–124 | 10.1016/1011-1344(93)80169-M | **404, does not exist** → use `10.1016/1011-1344(93)80173-7` |
| [5] | Albani 2007, *Principles and Applications of Fluorescence Spectroscopy* | 10.1002/9780470691274 | **404, does not exist** → use `10.1002/9780470692059` (ISBN 978-1-4051-3891-8 is correct) |
| [6] | Sauer, Hofkens & Enderlein 2011, *Handbook of Fluorescence Spectroscopy and Imaging* | none (ISBN 978-3-527-31669-4) | **verified** via OpenLibrary; no DOI needed |

Both works behind the broken DOIs are real; only the suffixes are invented. Under
PS1 that is still the shape of a hallucinated reference, so both must be corrected
before submission.

### 5.2 Relevance: six claims sit on references that cannot carry them

| claim in the draft | cited to | what the audit found | fix |
| --- | --- | --- | --- |
| "Kasha's rule: the emission spectrum does not depend on the excitation wavelength" | [1, 2] | the *idea* is verified, but [1] states it in terms of **states** ("the emitting level … is the lowest excited level of that multiplicity", p.14–15) and the word "wavelength" never appears in [1]. The explicit wavelength-independence sentence is [2] §1.3.2, "Emission Spectra Are Typically Independent of the Excitation Wavelength", p.7 | cite [1] for Kasha's rule and [2] §1.3.2 for the wavelength form the assignment asks about |
| Cy3 fluorescence lifetime ≈ 0.3–1.0 ns | [3] | [3] is a dye-synthesis paper; its abstract has no lifetime and no time-resolved data | cite a Cy3 photophysics measurement, e.g. Berrocal-Martin et al., *J. Phys. Chem. B* 2025, DOI 10.1021/acs.jpcb.5c03845 (open access; reports ~0.2 ns free sCy3 and 0.6–1.1 ns components) |
| internal conversion / vibrational relaxation take 100 fs – 1 ps | [1, 2] | [1] p.16 prints only an *upper bound* on IC (~10⁻¹²–10⁻¹³ s, from an intensity ratio, superscript partly unreadable) and puts the real limit at "the time of a vibrational period"; the words "vibrational relaxation" never appear in [1]. The measured 100 fs–1 ps window is [2] §1.4.2 "Timescale of Molecular Processes in Solution", p.12 | keep [1] for the "ultrafast, faster than emission" statement; cite [2] §1.4.2 for the numbers |
| Beer–Lambert + `I_PL = I_abs · Φf` | [3] | textbook fluorescence, not in a dye-synthesis paper | cite [2] (or [5]) |
| `π–π*` assignment for the cyanine S0→S1 band | [3] | [3] names Cy3 and its laser lines (546 nm) but never says 550 nm or `π–π*`; 550 nm is the vendor value | keep [3] for the chromophore, cite [1]/[2] for the assignment, and attribute 550 nm to the Cytiva datasheet |
| emission vanishes at λexc ≥ 620 nm because hν < the 0–0 gap | [1–3] | no source states a Cy3 0–0 gap or a 620 nm cutoff; Cy3's 0–0 is ~570 nm, and the simulator itself does not cut emission at λexc — the signal dies because the absorption tail dies | state it as a consequence of the vanishing absorption, drop the citation |
| ~96 % of excited methylene blue decays non-radiatively, "specifically by intersystem crossing to T1" | [4] | 96 % is the *total* non-radiative share (1 − Φf) and is fine as such, but Φ_ISC for methylene blue is ≈0.50–0.52, not 0.96: roughly half goes to T1 and half returns to S0 by internal conversion (Morgounova, *J. Biomed. Opt.* 2013, 056004; Moreira, InTech 2012, p.395, which names internal conversion *and* triplet formation). [4]'s full text is unreadable by every route tried | reword to the half/half statement and cite one of those sources, not [4] |
| narrow HOMO–LUMO gap by 0.33 eV, "free-electron particle-in-a-box model" | [3] | [3] does no such calculation; the free-electron model of cyanines is Kuhn 1949, 44 years earlier | cite Kuhn, *J. Chem. Phys.* 1949, 17, 1198, DOI 10.1063/1.1747143 (the arithmetic itself is right: 550→649 nm is 0.344 eV) |
| silicon "quantum efficiency scales as λ/1.24 µm" | nothing | the relation is right but misnamed: λ/1.24 is the **responsivity** factor, `R [A/W] = η·λ[µm]/1.24`. The quantum-efficiency form is `QE = [S·1240/λ]·100 %` | reword to responsivity and cite Hamamatsu, *Si photodiodes*, tech. note KSPD9001E04, §2-3 p.6 eq. (2-3); RP Photonics, "Responsivity", DOI 10.61835/xal |
| methylene blue is a "tricyclic phenothiazine with distinct electronic symmetry and selection rules" | [4] | [4]'s abstract does not mention structure, symmetry or selection rules; 18 citing papers use it for DNA binding and photosensitised oxidation | cite a phenothiazinium dye review for the structure, or drop the symmetry clause |

### 5.4 Corrected citation strings, ready to paste

Verified during the audit (existence checked against Crossref/doi.org, and the
supporting passage read where it could be reached):

```
[4] Tuite, E. M.; Kelly, J. M. J. Photochem. Photobiol. B 1993, 21 (2-3), 103-124.
    DOI 10.1016/1011-1344(93)80173-7        (the DOI in the draft, ...80169-M, does not exist)
[5] Albani, J. R. Principles and Applications of Fluorescence Spectroscopy;
    Blackwell: Oxford, 2007. ISBN 978-1-4051-3891-8.
    DOI 10.1002/9780470692059               (the DOI in the draft, ...0691274, does not exist)

For C3 (Cy3 lifetime), replacing [3]:
    Berrocal-Martin, A. et al. J. Phys. Chem. B 2025, 129, 11626-11635. DOI 10.1021/acs.jpcb.5c03845
    Sanborn, M. E. et al. J. Phys. Chem. B 2007. DOI 10.1021/jp072912u
For C8 (methylene blue triplet yield ~0.5):
    Morgounova, E. et al. J. Biomed. Opt. 2013, 18, 056004.
    Moreira, L. M. et al. "Phenothiazinium Dyes as Photosensitizers in PDT", InTech 2012, p. 395.
    DOI 10.5772/48087
For C9 (detector):
    Hamamatsu Photonics, "Si photodiodes", technical note KSPD9001E04, sec. 2-3, eq. (2-3).
    RP Photonics Encyclopedia, "Responsivity". DOI 10.61835/xal
For C10 (cyanine chain length, replacing the particle-in-a-box attribution to [3]):
    Kuhn, H. J. Chem. Phys. 1949, 17, 1198-1212. DOI 10.1063/1.1747143
    Vahdani, A. et al. J. Am. Chem. Soc. 2024, 146, 19756-19767. DOI 10.1021/jacs.4c02171
    Neme, N. et al. Phys. Chem. Chem. Phys. 2024. DOI 10.1039/D3CP05219B
For the sample-database values themselves:
    cite the primary sources listed in data/SOURCES.md (vendor datasheets,
    PhotochemCAD, OMLC, ACS Omega 2020), not [3] or [4].
```

### 5.3 Other audit findings

- **[5] and [6] are never cited in the body**, only listed. Cite them where they
  carry something, or drop them: an uncited reference is exactly what "irrelevant"
  means to a marker.
- **Quantum yields are cited to [3, 4]** while the repository attributes them to
  vendor datasheets, PhotochemCAD and OMLC. Cite `data/SOURCES.md`'s primary
  sources for numbers that come from the data pack.
- **The body says methylene blue Φf = 0.04** while the shipped database says 0.02
  in water. The number in the text, the figures and the code must be the same one.
- **[2] Lakowicz could not be read from anywhere accessible** (closed access, no
  OCR copy). Claims that rest on it should be phrased as standard textbook content,
  and anything more specific needs a readable source.

## 6. Submission format

- **PS2: a single PDF file.** The report is one PDF; everything the marker needs —
  screenshots, figures, references, code appendix — must be inside that file.
  Nothing may be a separate attachment.
- The PDF must be regenerable: `report/generate_pdf_report.py` needs `reportlab`,
  which is currently **not** in `pyproject.toml` and **not** in `.venv`.

---

## 7. Open questions for the team

1. Are the "screen shots" required to be literal screenshots of a run? If yes,
   from which surface — terminal, figure window, editor?
2. Which platform counts as "an AI tool" for R1 — do we name it explicitly, and do
   we show the prompts or the working session?
3. For R3, do we set **equal concentration** (different peak absorbance per dye) or
   keep equal peak absorbance and say so plainly?
4. Do we keep the Gaussian model or move the figures to the measured reference
   bands? Either is defensible; mixing them is not.
5. Who owns the final read-through of the reference list against the claims?

---

## 8. Definition of done

Report-phase items are unchecked; everything the report depends on is done and
verified (`VERIFICATION.md`).

- [x] figures for R1/R2/R3 exist and are the "screenshots" the announcement asks for
- [x] R2's measurement artifact fixed and verified against the model
- [x] R3's equal-concentration premise implemented and stated in the figure titles
- [x] every shipped dye number independently re-checked (`data/SOURCES.md`)
- [x] every reference checked for existence and for relevance
      (`report/references/AUDIT.md`), with corrections listed in section 5
- [x] the seven figures audited independently against their own numbers and against
      the question each belongs to; eight defects found and fixed
      (`VERIFICATION.md` section 4b)
- [x] `reportlab` declared, PDF rebuilds from a clean `uv sync`
- [x] figures and `report/numbers.md` regenerate byte-identically in a clean room
- [ ] **report phase**: correct the five unsupported numbers (section 6 of `numbers.md`)
- [ ] **report phase**: fix the two DOIs and re-point the six mis-cited claims (section 5.2)
- [ ] **report phase**: cite or drop [5] and [6]; say which AI tool designed the system
- [ ] **report phase**: embed the three individual dye panels as well as the
      combined overview (the PDF currently shows only the overview for question 1)
- [ ] **report phase**: rebuild the PDF from the corrected text and figures
- [ ] **report phase**: one PDF, no external attachments, nothing left outside it
