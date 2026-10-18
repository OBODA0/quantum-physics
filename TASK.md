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
| **screen shots** of the three dyes | `report/report_figures/part1_*.png` + `part1_combined_overview.png` | **gap — these are programmatic plots, not screenshots** |
| code as appendix | appendix in `report/Assignment_1_...Report.pdf`, pages 6–13 | done |
| "using an AI tool" | not stated anywhere in the report | **gap — name the tool and how it was used** |

**Inference:** "screen shots" means captures of the simulator being run (terminal
output, the figure window, the command used), not figures saved by the script.
This is a cheap, real risk: three screenshots of a run per dye would close it.

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
| fit to literature + reasons | §2.2 (Kasha's rule, internal conversion vs ns emission, Stokes shift, excitationspectrum vs absorbance) | mostly done, one wrong claim |
| references | 6 references listed, 2 DOIs broken — see §5 | **must fix** |

The sweep as implemented: detection window 500–750 nm; the "PL peak intensity"
curve is sampled in a fixed **565–575 nm** window.

**Known artifact (must be fixed or explained):** because the model emits nothing
below λexc (Stokes cut), the fixed 565–575 nm window goes dark as soon as
λexc > 570 nm. The intensity curve therefore collapses to zero at 570 nm — that is
the detection window, not the dye's absorption edge. The committed figure's own
right-hand panel shows this: the simulated intensity dies at 570 nm while the
overlaid A(λ) curve continues rising into the 580–600 nm region. The report text
nonetheless claims the excitation spectrum "exactly mirrors" A(λ). Two fixes are
possible: integrate the whole emission band above λexc instead of a fixed window,
and/or normalize by the lamp power at λexc before comparing with A(λ) (the current
curve carries the xenon spectrum as a weight).

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
*absorbance* are different experiments and give different peak heights. The report
currently says "identical peak optical density / concentration", which conflates
the two.

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

## 5. Reference audit (run 2026-10-18 against Crossref / doi.org / OpenLibrary)

PS1 makes this the highest-stakes item in the assignment: hallucinated or
irrelevant references ⇒ 0 for everything.

| # | cited work | cited DOI/ISBN | verdict |
| --- | --- | --- | --- |
| [1] | Kasha 1950, *Discussions of the Faraday Society* 9, 14–19 | 10.1039/DF9500900014 | **verified** — title, author, journal, volume, year all match |
| [2] | Lakowicz 2006, *Principles of Fluorescence Spectroscopy* (3rd ed.) | 10.1007/978-0-387-46312-4; ISBN 978-0-387-31278-1 | **verified** — DOI resolves to the 2006 book; ISBN matches the 3rd edition |
| [3] | Mujumdar et al. 1993, *Bioconjugate Chemistry* 4(2), 105–111 | 10.1021/bc00020a001 | **verified** — title, authors, journal, volume, pages all match |
| [4] | Tuite & Kelly 1993, *J. Photochem. Photobiol. B* 21(2-3), 103–124 | 10.1016/1011-1344(93)80169-M | **DOI DOES NOT EXIST (404)** — the work is real, recorded in Crossref as `10.1016/1011-1344(93)80173-7`, vol 21, pages 103–124, 1993, authors Tuite & Kelly |
| [5] | Albani 2007, *Principles and Applications of Fluorescence Spectroscopy* | 10.1002/9780470691274; ISBN 978-1-4051-3891-8 | **DOI DOES NOT EXIST (404)** — the book is real (ISBN verified), correct DOI `10.1002/9780470692059` |
| [6] | Sauer, Hofkens & Enderlein 2011, *Handbook of Fluorescence Spectroscopy and Imaging* | ISBN 978-3-527-31669-4 | **verified** via OpenLibrary — title and lead author match |

Two fabricated DOIs are enough to look like hallucination even though both works
are genuine. Fix both suffixes before submission.

**Still unchecked: whether each reference supports the exact claim attached to
it.** These need a read, not a lookup:

- "*τf ≈ 0.3–1.0 ns for Cy3 [3]*" — [3] is a dye-labeling chemistry paper; a
  fluorescence lifetime cited to it should be double-checked, or the claim re-cited
  to a lifetime source.
- "*narrowing the HOMO–LUMO energy gap by approximately 0.33 eV … particle-in-a-box
  model [3]*" — [3] does not do that calculation; cite a spectroscopy textbook
  (e.g. [2] or [5]) or drop the number.
- "*rapid intersystem crossing into the triplet state T1, mediated by sulfur
  spin-orbit coupling [4]*" — plausibly supported by [4]; confirm in the text of
  the paper.
- Numbers repeated from our own pack (Φf, ε) should cite `data/SOURCES.md` or the
  primary sources inside it, not a textbook.

---

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

- [ ] R1: three dye spectra + screenshots inside the PDF, code appendix present,
      AI tool named
- [ ] R2: Cy3 sweep 400–700 nm with screenshots, observations, literature comparison,
      corrected references; the 570 nm artifact either fixed or explained in the text
- [ ] R3: both figure forms labelled, "same concentration" premise stated explicitly,
      the "why" answered with the mechanisms the model actually contains
- [ ] Report text and code appendix agree on every number
- [ ] Every DOI/ISBN resolves; every reference supports the sentence it is attached to
- [ ] `reportlab` declared so the PDF rebuilds from a clean `uv sync`
- [ ] One PDF, no external attachments
