# TASK C — Assignment 1 document conventions, and a TASK.md skeleton for Assignment 2

Prepared 2026-10-22 on the Blackwall outpost (CT 180, host `agent`), read-only against
Alfred. Nothing was written into the project repository; this file is the only output.

**What was read** (all of `assignments/01-pl-spectrometer/`):

| file | size | used for |
| --- | --- | --- |
| `TASK.md` | 23,644 B, 8 top-level sections | the conventions themselves |
| `VERIFICATION.md` | 18,848 B | how verification is written |
| `README.md` | 32,396 B | the submitted report (markdown twin of the PDF) |
| `report/README.md` | 2,504 B | the file-status table |
| `data/SOURCES.md` | 21,933 B | source kinds, confidence grading, "could not verify" |
| `report/numbers.md` | 11,469 B | generated number table, section numbering |
| `report/references/AUDIT.md` | 7,296 B | existence/relevance audit format |
| `report/data_provenance.md` | 9,424 B | per-value provenance tables |
| `docs/readme_template.md` | 8,936 B | README generation, `<!-- REPORT -->` placeholder |
| `report/settings.py`, `report/generate_*.py`, `report/check_pdf.py`, `pyproject.toml`, `.gitignore`, `tests/test_simulator.py` | — | generated-vs-handwritten split, gate contents |

Marking used below: **[sourced]** = read directly in those files (section named);
**[inference]** = my reading of them; **[NEW]** = a convention I propose that
Assignment 1 does not have, flagged as new.

---

# 1. The conventions Assignment 1 uses for a TASK.md

## 1.1 Header block

Three elements, in this order **[sourced, TASK.md header block]**:

1. `# TASK.md — Assignment 1: PL spectrometer simulation`
2. `Status: working spec, compiled 2026-10-18. Sources are quoted verbatim; anything`
   `that is our reading rather than the assignment's own words is marked **Inference**.`
3. A course-framing paragraph naming the course, the report title wording, the class-notes
   identifier and date (`W31L2`, `15/10`), and whose words the framing is ("OBODA's words").

The status line is load-bearing: it declares the document a *working spec*, not a finished
document, and it declares the inference marker before any content appears. Dates are
ISO (`2026-10-18`), and every later change is stamped the same way.

## 1.2 Section order

**[sourced]** The eight sections, in this order:

| § | heading | job |
| --- | --- | --- |
| 1 | Where our information comes from | a 2-column table: `source` / `what it gives us`; ends with the precedence rule ("The board and the announcement must both be satisfied. The announcement grades the work; the board defines what the simulator must be able to do.") |
| 2 | The assignment, in its own words | 2.1 announcement, 2.2 whiteboard, 2.3 class notes — each a blockquote, each with a provenance sentence |
| 3 | Requirement-by-requirement, mapped to what exists | one `### R<n> — <short name> (<weight>)` per graded item, each with a mapping table |
| 4 | Sample data the simulator actually uses | the values shipped in the code, with their sources, plus a note where the draft text disagreed with the code |
| 5 | Reference audit | 5.1 existence, 5.2 relevance, 5.3 other findings, 5.4 corrected citation strings, 5.5 text the corrected figures contradict |
| 6 | Submission format | the administrative rules (one PDF, regenerable, gated) |
| 7 | Open questions for the team | numbered, each answerable, no owner column |
| 8 | Definition of done | checkbox list, checked items carry the artifact that proves them |

Sections 1-2 are *input*, 3-5 are *audit*, 6-8 are *closeout*. That order is what makes the
file readable months later: you can stop after §2 and know what was asked.

**[sourced] Quirks in this file that Assignment 2 should not copy:** §5 is ordered
5.1, 5.2, 5.4, 5.5, 5.3 (evidence inserted later without renumbering); §3 refers to a
"Screenshots note above/below" that does not exist anywhere in the file; and the submitted
report jumps from §3 to §3.2 with no §3.1 heading, although the prose opens "**3.1 The
colours come from the absorption bands.**" (a bold run-in, not a heading); and §8's preamble says
"Report-phase items are unchecked" while every item in the list is in fact `[x]`. None of these is
a convention — they are accretion. In Assignment 2, renumber in order and keep the §8 preamble
true.

## 1.3 Quoting the brief verbatim

**[sourced]** Rules the file follows:

- The brief is reproduced as a markdown blockquote, whole, with its own numbering and its own
  errors: "you are expected the followings", "methyleneblue", "Why? (25)" without a percent
  sign. Nothing is corrected, nothing is paraphrased, nothing is omitted.
- Each quoted source gets a provenance line above or below it: what the source physically is
  ("Whiteboard photo (in-class task statement)", "Handwritten class notes photo (`W31L2 15/10`)",
  "Announcement text (pasted by OBODA)").
- Handwriting is transcribed with visible uncertainty, not smoothed: "the relation written next
  to the photodetector/computer is transcribed as `P(λ) = R(λ) I` … This is the least certain
  item on the page — the symbol after `P(λ) =` could be `R(λ)·I`, `R(λ)/I` or a two-line
  expression. **Verify against the lecture before quoting it in the report.**"
- Where a page has marks that are not requirements, they are named and dismissed in one
  sentence, marked inference: "**Inference:** they are a doodle of an excitation arrow and an
  emission wave, not a specification."
- Where two sources conflict, the conflict is stated and a precedence rule is chosen, not
  hidden: "the notes start from a white emitter / monochromator, the board requires a xenon
  lamp … The board wins for the simulator."
- Arithmetic on the brief's own numbers is shown: "items are marked `25%`, `50%`, `(25)` —
  item 3's marker is missing its percent sign, so the three weights sum to 100±.
  **Inference:** item 3 is worth 25%."
- Where the brief is ambiguous, both readings are implemented rather than argued:
  "**Ambiguity, deliberately covered both ways:** … one graph per excitation wavelength, or all
  curves on a single canvas. The team produced both … **Inference:** keeping both is the safe
  move."

## 1.4 Marking inference

**[sourced]** One mechanism, used everywhere: the bold token **Inference** followed by a colon,
inside the sentence or paragraph it qualifies. It appears in the header, in §2.2 (the doodle), in
§2.1 (the missing weight), and in §3/R3 (covering an ambiguity). It is never a footnote and never
a trailing "(assumed)".

Three neighbouring devices, all distinct:

| device | when it is used | example |
| --- | --- | --- |
| **Inference:** | our reading of the brief or an image | missing percent sign |
| "transcribed as … could be …" + "**Verify against the lecture**" | a glyph or symbol is genuinely uncertain | `P(λ) = R(λ) I` |
| "**gap**", "**must fix**", "**must be stated or changed**" | a requirement is unmet or a claim is unsupported | "using an AI tool \| not stated anywhere in the report \| **gap — name the tool and how it was used**" |

**[inference]** The distinction is: Inference = the brief does not say it, we do; gap = the
brief says it, we have not done it. Keeping them separate is what makes §3 usable as a worklist.

## 1.5 Mapping a requirement to evidence

**[sourced]** Each `### R<n>` block has, in this order:

1. **A heading with the weight in the assignment's own units**: `### R1 — design + screenshots of
   the three dyes (25%)`. Where the brief is inconsistent, the heading uses the inferred weight
   and §2.1 carries the arithmetic.
2. **`Verbatim asks:`** — the brief's clauses, each in italics as a short quotation, comma
   separated, in the order they appear: *"Design a PL spectrometer system using an AI tool"*,
   *"Show using screen shots …"*, *"Add your code as appendix"*. Nothing is added that the brief
   did not say; the weight is not repeated here because it is in the heading.
3. **A three-column table** `| ask | current artifact | status |`. The artifact column names
   **files**, not intentions (`report/report_figures/part1_cy3.png`), and for the PDF names the
   figure numbers it occupies ("all four are embedded in the PDF as Figures 2 and 3").
4. **Status vocabulary is free text, bolded when it is bad**: `done`, `done — <caveat>`,
   `**gap**`, `**must fix**`, `**must be stated or changed**`. A status of `done` is allowed to
   carry a defect that is written out in the same cell.
5. **Resolution blocks appended under the table, dated, in caps or bold**:
   `**Resolved (2026-10-18):**` when a question closed, `**IMPLEMENTED (2026-10-18).**` when code
   changed, `**Artifact found and FIXED (2026-10-18).**` when a measurement defect was found.
   They state what was wrong, what the corrected behaviour is, and which file proves it
   (`plsim/analysis.py`, `VERIFICATION.md` section 1). They are appended, never rewriting the
   history above them.
6. **The honest residue**: statements of what the report must *not* claim ("so the text must not
   claim an exact mirror"), and the premise that had to change ("the model uses equal peak
   optical density, not equal concentration — **must be stated or changed**").

**[inference]** The mapping is ask → artifact → status, never requirement → paragraph of prose.
That is what lets a marker (or a teammate) check the file against the PDF line by line.

## 1.6 How sources are graded

Assignment 1 grades on separate axes. They are not merged.

**(a) Kind of source** **[sourced, `data/SOURCES.md` header]** — a four-item taxonomy with the
weakness of each kind stated: `vendor datasheet` ("authoritative for the commercial dye, but
vendor quantum yields are often measured on conjugates"), `spectral database` (PhotochemCAD 3,
FPbase), `measured data set` (OMLC/Prahl), `peer-reviewed paper` ("noted whether I could read the
full text, the abstract only, or only the indexed PDF text via a search snippet").

**(b) Confidence per value** **[sourced]** — `High` / `Medium-high` / `Medium` / `Low`, each with
the reason in the same cell, plus the spread across sources and the conditions attached to the
number: "0.04 in PBS, pH 7.4 (free dye) … Medium-high for the *free dye in buffer*; the original
2015 paper itself is paywalled and was not read directly". Ranges are given when sources disagree
("150,000 … sulfo form 162,000"; "Cy5 Φf 0.19-0.30"). A number with no citable primary source is
**not used**, and that decision is written down: "No primary source was found for the widely
repeated methylene blue extinction coefficient of 95,000 … so it is not used."
A snippet-only source is labelled and demoted: "listed as supporting evidence only, never as the
sole source of a reported value."

**(c) Reference existence and relevance** **[sourced, `report/references/AUDIT.md`]** — two
separate verdicts. Existence: `VERIFIED` (Crossref + doi.org, with what matched: title, authors,
volume, pages) or `404, does not exist → use <correct DOI>`. Relevance: a four-column table
`claim in the draft | cited to | what the audit found | fix`, where "what the audit found" quotes
the source or says what it does not contain ("its abstract has no lifetime and no time-resolved
data"). Under the assignment's PS1 (fabricated or irrelevant reference ⇒ 0), a broken DOI suffix
is treated as the shape of a hallucination even when the work is real.

**(d) Data-pack self-checks** **[sourced, `SOURCES.md`]** — every digitized curve is re-derived
from the raw file kept in `data/raw/` and must reproduce its source to rounding (FPbase to 3e-8,
PhotochemCAD PSW009 to 5e-6); a "Second opinion" pass re-checks without reusing the team's own
file; the FWHM measurement rule is stated once (§0) so it is reproducible rather than a quoted
literature value.

## 1.7 Definition of done

**[sourced, TASK.md §8]** One line of preamble: "Report-phase items are unchecked; everything the
report depends on is done and verified (`VERIFICATION.md`)." Then a checkbox list where every
checked line names the artifact that proves it:

- `[x] R2's measurement artifact fixed and verified against the model`
- `[x] every reference checked for existence and for relevance (`report/references/AUDIT.md`), with corrections listed in section 5`
- `[x] figures and `report/numbers.md` regenerate byte-identically in a clean room`
- `[x] the PDF carries no external attachments; every DOI printed in it resolves (checked against Crossref on the built file)`

**[inference]** The gate is external and mechanical, not a promise: a checkbox is only ticked if
a named file or command proves it. Two properties are always among the criteria — clean-room
reproducibility, and a check that runs on the *submitted* artifact rather than on the repository.

## 1.8 The cross-document contract

**[sourced]** Five documents, each with one job, each referenced by section number from the others:

| file | job | forbidden content |
| --- | --- | --- |
| `TASK.md` | what was asked, mapped to what exists; defects and their resolutions | no report prose |
| `VERIFICATION.md` | proof the simulator, data, figures, references are correct *before* the report is written ("so that the report can be transcription rather than discovery") | its own opening rule, "Nothing here touches the report text" — which Assignment 1 later broke by appending §6 and §8 on the built PDF; the report-phase sections are best read as a second, separate log |
| `data/SOURCES.md` | every shipped datum, its source, its confidence, and what could not be verified | no claims about the report |
| `report/numbers.md` | every number the report quotes, generated | "Do not edit by hand: if a number here is wrong, fix the code or the data, not this file." |
| `report/references/AUDIT.md` | the audit of the draft's references, with a status note saying its findings were applied | not a description of the current list |

Errata handling is uniform: append with a date and a status note at the top, do not rewrite
history. `AUDIT.md` opens with a `> **Status note (added after the report was rewritten).**`
paragraph telling the reader to read the rest as evidence, not as current state. `VERIFICATION.md`
ends with `## 7. Not verified, and therefore not claimed` — an explicit list of what the document
does **not** establish.

---

# 2. Proposed TASK.md skeleton for Assignment 2 (XRD diffractometer simulator)

Written in Assignment 1's numbering and voice. Every place where the assignment's own words,
weights, or named samples must go is marked `AWAITING BRIEF`. Prose in square brackets is
instruction to the author, not text to ship.

````markdown
# TASK.md — Assignment 2: XRD diffractometer simulation

Status: working spec, compiled AWAITING BRIEF. Sources are quoted verbatim; anything
that is our reading rather than the assignment's own words is marked **Inference**.

Course framing: "Nanotechnology & Quantum Physics" (report title page) / the nano
capsule class, quantum physics section (OBODA's words). Class notes are headed
`AWAITING BRIEF` and dated `AWAITING BRIEF`.

---

## 1. Where our information comes from

| source | what it gives us |
| --- | --- |
| AWAITING BRIEF — which artifact states the task (announcement text / whiteboard photo / lecture slide / PDF brief) | AWAITING BRIEF |
| AWAITING BRIEF — class notes, with their heading and date | the diffractometer chain the design must model |
| AWAITING BRIEF — any pasted announcement, with where it was pasted from | the graded deliverables and their weights |

AWAITING BRIEF — one sentence stating which source grades the work and which defines what
the simulator must do, and what happens where they disagree.
[Assignment 1 wrote: "The announcement grades the work; the board defines what the simulator
must be able to do." Copy that sentence only if the same split is true here.]

---

## 2. The assignment, in its own words

### 2.1 Announcement (verbatim)

> AWAITING BRIEF — paste whole. Keep the brief's own numbering, spelling, units and
> punctuation; do not correct or omit anything.

Note on the weights: AWAITING BRIEF — list the weights exactly as printed, show their sum,
and mark any arithmetic repair as **Inference** (Assignment 1: "items are marked `25%`,
`50%`, `(25)` … **Inference:** item 3 is worth 25%").

### 2.2 Instrument statement (verbatim transcription)

> AWAITING BRIEF — the whiteboard/slide sketch of the diffractometer: source, optics,
> goniometer, sample, detector.

[Transcribe labels as written; where a symbol is uncertain write "transcribed as … could be …
**Verify against the lecture** before quoting it in the report." If the sketch and the notes
conflict, state the conflict and pick a rule, as Assignment 1 did with "The board wins for the
simulator."]

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
| AWAITING BRIEF | AWAITING BRIEF | AWAITING BRIEF |

[A Resolution / IMPLEMENTED / Artifact found and FIXED block goes here, dated, as defects are
found: what was wrong, what the corrected behaviour is, which file proves it.]

### R2 — AWAITING BRIEF (<weight>%)

Verbatim asks: AWAITING BRIEF.

| ask | current artifact | status |
| --- | --- | --- |
| AWAITING BRIEF | AWAITING BRIEF | AWAITING BRIEF |

[If the brief admits two readings, implement both and say which is which:
"**Ambiguity, deliberately covered both ways:** … **Inference:** keeping both is the safe move."]

### R3 — AWAITING BRIEF (<weight>%)

Verbatim asks: AWAITING BRIEF.

| ask | current artifact | status |
| --- | --- | --- |
| AWAITING BRIEF | AWAITING BRIEF | AWAITING BRIEF |

### R<n> … (repeat until every graded clause and every PS rule has one block)

---

## 4. Sample data the simulator actually uses

AWAITING BRIEF — which samples/phases the brief names, and in what form (a formula, a
mineral name, a measured pattern, a single crystal structure).

Table to fill, one row per shipped sample, same columns as Assignment 1 plus the
crystallographic ones:

| sample | AWAITING BRIEF (e.g. space group / lattice parameter / reference pattern source) | … | source | confidence |
| --- | --- | --- | --- | --- |

Then the sentence Assignment 1 needed and Assignment 2 will need in some form: which value the
draft text carried wrongly, and what the code actually ships.
[Assignment 1: "The draft body carried pre-source numbers … Whatever set of numbers the team
wants, the text and the code must agree."]

---

## 5. Reference audit

AWAITING BRIEF — run once the draft exists. Keep the five subsections, in this order
(Assignment 1 has them out of order; fix that here).

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

- AWAITING BRIEF — reproduce every administrative rule verbatim (file type, single-file rule,
  naming, deadline, any rule about references). Assignment 1's were: one PDF, nothing attached
  separately, and a gate (`report/check_pdf.py`) run on the built file before upload.
- The PDF is regenerable: `reportlab` and `pypdf` declared in the dev group, `uv sync` installs
  them, and `report/check_pdf.py` gates the built file.

---

## 7. Open questions for the team

1. AWAITING BRIEF — every genuine ambiguity in the brief, phrased as a question with two
   answers, not as a complaint.
2. AWAITING BRIEF — what counts as "using an AI tool" here, and whether prompts are shown.
3. AWAITING BRIEF — which model detail is a modelling choice rather than physics (Assignment 1's
   equivalent: reference bands vs Gaussian model; anti-Stokes emission).

---

## 8. Definition of done

Report-phase items are unchecked; everything the report depends on is done and verified
(`VERIFICATION.md`).

- [ ] every requirement in §3 has a figure or table and a status of done
- [ ] every number the report quotes appears in `report/numbers.md`
- [ ] every shipped datum has a source and a confidence in `data/SOURCES.md`
- [ ] every reference verified for existence and relevance (`report/references/AUDIT.md`)
- [ ] figures audited against their own numbers (`VERIFICATION.md` section 4b)
- [ ] clean-room rebuild: figures byte-identical, `numbers.md` identical, PDF builds
- [ ] `report/check_pdf.py` passes on the built PDF
- [ ] §7 questions answered or explicitly declared open
````

**[NEW] Two additions I propose, not present in Assignment 1** (flagged, and optional):
a `## 9. Fidelity limits` section listing what the simulator deliberately does not model
(Assignment 1 keeps that content scattered across `VERIFICATION.md §7` and the README's
"What is modelled, and how real it is"), and a one-line `Owner:` field on each §7 question.
Both exist to stop the same paragraph being written twice in two documents.

---

# 3. What the Assignment 1 report does that the XRD report must also do

Concrete artifacts and file names. Grouped by the artifact that carries the property.

**Cover and header**
- [ ] Title page with a metadata table (Assignment 1: Simulator / Sample database / Physics /
      Built with / Repository / Source of numbers), the course and both students with IDs.
- [ ] "Built with" names the AI tool and the models, and how it was used — Assignment 1's brief asks
      for it, and R1's status was a **gap** until this row existed.
- [ ] Repository link printed on the title page.

**Figures**
- [ ] Every figure generated by a committed script
      (`report/generate_assignment_figures.py` → `report/report_figures/*.png`), never drawn by
      hand, never screenshotted from a terminal.
- [ ] Numbered captions that state: what is drawn, the conditions (concentration, range, stray
      level, wavelength), and which module produced it ("Every box is a module in the appendix
      code: the lamp spectrum (`sources.py`) …").
- [ ] At least one figure per graded clause, plus the "both readings" figure where the brief is
      ambiguous.
- [ ] Titles carry the numbers a reader would otherwise have to guess
      ("A(550 nm) = 0.143, A_peak = 0.150, Φf = 0.04").
- [ ] Figure audit against printed axes and against `numbers.md` before submission
      (`VERIFICATION.md` §4b, defect table).

**Numbers**
- [ ] `report/numbers.md`, generated by `report/generate_numbers.py`, with a "do not edit by
      hand" header.
- [ ] Every number in the report text traceable to a row of `numbers.md`; no number retyped.
- [ ] One module holding the experimental conditions shared by every figure and table
      (`report/settings.py`) — created because the figures and the table had drifted apart.
- [ ] A section of `numbers.md` titled "Values that are easy to get wrong".

**Data provenance**
- [ ] `data/SOURCES.md`: source kinds, one table per sample with `value | source | confidence`,
      a stated measurement rule for any derived width (FWHM analogue), an inventory of
      `data/raw/`, a "Second opinion" pass, and a "What I could NOT verify" list.
- [ ] `data/raw/` keeps the downloaded files, so every digitized curve can be re-derived.
- [ ] `report/data_provenance.md`: the same information in report-ready prose, appendix item 1.
- [ ] `data/reference_patterns.json` (A2 analogue of `reference_spectra.json`) validated by a
      test: fields present, abscissa strictly increasing, finite, non-negative, normalised,
      quoted maxima inside the measured range.

**References**
- [ ] `report/references/AUDIT.md` with an existence table and a relevance table, plus a status
      note saying the findings were applied.
- [ ] `report/references/claims.json` — machine-readable verdict per claim.
- [ ] Every reference cited in the body at least once; every printed DOI resolves from the
      **built PDF** (`report/check_pdf.py`), not from the repository.
- [ ] A "Declared limitations" paragraph inside the reference section.

**Verification**
- [ ] `VERIFICATION.md` with: model checks mapped to the claims they defend (table), the data
      re-check, the reference re-check, clean-room reproducibility, the figure audit, the PDF
      gate, and a final "Not verified, and therefore not claimed" section.
- [ ] A defect log: before/after numbers for every defect found (`λexc 520/560/565 nm → FWHM
      28.5/25.5/22.5 nm`), the fix, and the test that now guards it.
- [ ] `tests/test_simulator.py` asserting the report's own claims, not just code behaviour.
- [ ] Clean-room result stated as byte-identical figures and `numbers.md`, not "it works".

**Submission**
- [ ] `report/Assignment_2_XRD_Diffractometer_Simulation_Report.pdf`, single file, figures and
      code appendix embedded, no external attachments.
- [ ] Code appendix read from the repository at build time, paths resolved against the
      repository root, a missing file is a hard error.
- [ ] `report/check_pdf.py` gate: DOI resolution, appendix file count, embedded images, page
      count and metadata.
- [ ] `report/README.md` file-status table (`current` / one-off / historical).
- [ ] `README.md` generated from the PDF source via `docs/readme_template.md` +
      `<!-- REPORT -->`, so markdown and PDF cannot drift.
- [ ] `TASK.md` itself, with §8 checked off.

---

# 4. Repository layout Assignment 2 should copy

`[H]` handwritten, `[G]` generated by a committed script, `[D]` data (committed, source files in
`raw/`), `[B]` build output (ignored).

```
quantum-physics/
├── README.md                              [H] course index, links both assignments
├── .gitignore                             [H] .venv/ __pycache__/ .pytest_cache/ out/
└── assignments/
    ├── 01-pl-spectrometer/                (unchanged)
    └── 02-xrd-diffractometer/
        ├── TASK.md                        [H] the skeleton in section 2 of this file
        ├── VERIFICATION.md                [H] evidence log, appended never rewritten
        ├── README.md                      [G] from docs/readme_template.md + PDF source
        ├── pyproject.toml                 [H] numpy, matplotlib; dev: pytest, reportlab, pypdf
        │                                      [tool.uv] package = false
        │                                      [tool.pytest.ini_options] pythonpath = ["."]
        ├── uv.lock                        [G] uv sync
        ├── xrdsim/                        [H] the simulator package (proposed name)
        │   ├── __init__.py                     exports, version
        │   ├── __main__.py                     4 lines: calls cli.main()
        │   ├── cli.py                          argparse; rejects bad input with a message
        │   ├── xray.py                         source emission: Kα1/Kα2, β, take-off
        │   ├── samples.py                      the sample/phase database the brief names
        │   ├── reference.py                    loader/validator for data/reference_patterns.json
        │   ├── instrument.py                   goniometer, slits, monochromator, broadening
        │   ├── detector.py                     detector response (if modelled)
        │   ├── diffractometer.py               the scan that connects them
        │   ├── analysis.py                     peak fitting, positions, widths, derived sizes
        │   └── plot.py                         plotting helpers only
        ├── data/
        │   ├── SOURCES.md                 [H] sources, confidence, what could not be verified
        │   ├── reference_patterns.json    [D] the shipped reference pack
        │   └── raw/                       [D] every downloaded file, kept
        ├── tests/
        │   └── test_simulator.py          [H] one test per claim the report makes
        ├── docs/
        │   └── readme_template.md         [H] README shell with <!-- REPORT -->
        ├── out/                           [B] interactive CLI output (gitignored)
        └── report/
            ├── README.md                  [H] file-status table for this folder
            ├── settings.py                [H] conditions shared by figures and numbers
            ├── generate_assignment_figures.py   [H; output G] → report_figures/*.png
            ├── generate_numbers.py        [H; output G] → numbers.md
            ├── generate_pdf_report.py     [H] reportlab source of record for the text
            ├── generate_readme.py         [H; output G] → ../README.md
            ├── check_pdf.py               [H] gate on the built PDF
            ├── numbers.md                 [G] every quoted number
            ├── data_provenance.md         [H] prose twin of data/SOURCES.md
            ├── references/
            │   ├── AUDIT.md               [H] existence + relevance audit
            │   └── claims.json            [H] machine-readable verdicts
            ├── report_figures/            [G] part1_*.png, part2_*.png, part3_*.png
            ├── cover.pdf                  [D] if the course supplies a cover page
            └── Assignment_2_XRD_Diffractometer_Simulation_Report.pdf   [B] the submission
```

**[inference]** Module names (`xray.py`, `instrument.py`, `diffractometer.py`) follow Assignment
1's split — one module per physical element named in the instrument chain, plus `analysis` for
the measurement metric and `plot` for drawing only — but the exact set should follow the brief's
chain, not this list. If the brief names fewer elements, ship fewer modules; an empty module is
worse than none.

**Files that must never be generated into two places** (learned from Assignment 1):
`report/settings.py` holds the conditions once; `numbers.md` is written only by its generator;
the report prose lives only in `generate_pdf_report.py`, from which both `README.md` and the PDF
are built.

---

# 5. Scope notes and what is *not* in this deliverable

- The Assignment 2 brief was not available on Alfred today (`assignments/02-xrd-diffractometer/`
  contains only a 226-byte placeholder README: "Status: not started"). Every item marked
  `AWAITING BRIEF` is therefore a slot, not a guess at the content. Where I inferred structure
  (module names, figure numbering, the five audit subsections) it is marked **[inference]** or
  **[NEW]**.
- No requirement, weight, sample name, radiation, angular range or sample count is proposed as
  fact anywhere in section 2. Those are the assignment's words to supply.
- Assignment 1's own outstanding items (draft text superseded by corrected figures, five
  unsupported numbers, the two fabricated DOIs) are recorded in its `TASK.md §5` and
  `VERIFICATION.md`; they are not restated here.
