# Brief intake checklist

What to do, in order, the moment the assignment 2 brief arrives. Every step names the file
it changes, so nothing is left as an intention.

## 1. Capture the brief, verbatim

- Paste the graded statement into `TASK.md` section 2.1 without correcting spelling,
  numbering or units. Assignment 1 kept "you are expected the followings" and
  "methyleneblue" for a reason: the quote is evidence.
- Paste the instrument sketch into 2.2, and the class notes into 2.3, each with its
  provenance line (where it came from, when).
- List every weight exactly as printed, show the sum, and mark any arithmetic repair as
  **Inference**.

## 2. Fill section 1

Name which source grades the work and which defines what the simulator must do, and which
one wins where they disagree. Assignment 1's rule was: the announcement grades, the board
defines.

## 3. Turn each graded clause into an `R<n>` block

For each requirement, in `TASK.md` section 3:

| ask | current artifact | status |
| --- | --- | --- |

The artifact column names files, never intentions. If a requirement needs something the
simulator does not do yet, say so in the status column rather than inventing an artifact.

## 4. Check the sample list

- Do the named samples exist in `xrdsim/samples.py`?
- If not, add each one with `uv run python -m tools.phase_from_cif <COD id> --expect hkl:2theta`,
  and only paste the block if the tool accepts the published line. Then add the row to
  `data/SOURCES.md` and to the `KNOWN_STRONGEST` test.
- If the brief gives a measured pattern rather than a structure, the tool does not apply:
  the data goes in `data/raw/` with its provenance.

## 5. Decide what the figures must show

Map each `R<n>` to a figure in `report/make_figures.py`. The four that exist
(instrument, phase panel, Scherrer, doublet) already cover the standard asks; anything new
goes in the same module so it regenerates with one command.

## 6. Re-read the submission rules

Copy them into `TASK.md` section 6 verbatim: file type, single-file rule, naming, deadline,
code appendix, reference rules. Then check `report/check_pdf.py` still enforces what the
brief requires, and add a check if it does not.

## 7. Rewrite the report sections

`report/generate_pdf_report.py` currently carries the instrument, the model, the phase
table, four figures and the verification. The graded questions replace the draft framing:
one section per `R<n>`, each with its figure and the numbers that support it.

## 8. Close out

- Every number in the report must appear in `report/tables.md` or be computed by the same
  code path; add it if not.
- Re-run: `uv run pytest`, `uv run python -m report.make_figures`,
  `uv run python -m report.tables`, `uv run python -m report.generate_pdf_report`,
  `uv run python -m report.check_pdf`.
- Tick the boxes in `TASK.md` section 8 only when the artifact exists.

## Open questions the brief has to answer

1. Which samples or phases are required, and in what form (formula, mineral, structure)?
2. Which questions are graded, with what weights?
3. Does "screen shot" mean a simulator output written to an image, as in assignment 1, or a
   capture of an interactive window?
4. Is a code appendix required, and does the single-PDF rule apply as it did in assignment 1?
5. Is the report to be submitted by the same pair, with the same title-page conventions?
