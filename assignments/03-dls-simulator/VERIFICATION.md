# Verification - assignment 3 (DLS simulator, report)

What was run on the build host (Alfred, Omarchy; repo at
`/home/oboda/Projects/Nano capsule/quantum-physics/assignments/03-dls-simulator`), what each
check proves, and what it does not.

Build date: 2026-11-15 (clock read on the host, 17:24 +03:00). Python 3.14.9 from the frozen
lock file.

## What was run

| # | command | result |
| --- | --- | --- |
| 1 | `uv run python -m pytest -q` | 18 tests pass (13 physics, 5 end-to-end) |
| 2 | `uv run python -m tools.check_all` | `all steps passed` |
| 3 | `uv run python -m report.check_pdf` | PASS: 66 pages, no embedded files, 12 URI links, 7 DOIs resolve through the handle registry |
| 4 | `uv run python -m report.check_numbers` | PASS: 66 quoted numbers match the model |
| 5 | clean room: `git clone` to `/tmp/q3`, `uv sync --frozen`, `uv run python -m tools.check_all` | `all steps passed`, and `git status --short` empty afterwards |

## What each check proves

- **Tests (18).** Stokes-Einstein at 100 nm in water to 2 %, the inverse-diameter scaling, the
  scattering vector at backscatter, the contrast factor vanishing at index match, the form
  factor limits, the ISO factor of two in the PDI, faster decay for smaller particles, warmer
  solvent shortening the decay, the intensity mean sitting above the number mean, aggregation
  raising both z-average and PDI, the inversion recovering a single 100 nm size, the 0.2
  threshold constant, an unknown solvent refused, and the CLI producing both figures. These
  are physics and plumbing checks; they are not a validation against experiment.
- **`check_pdf`.** The PDF is one self-contained file: the required sections are present in
  the text layer, there are no embedded files, every annotation is a URL (no file launches),
  it is longer than 25 pages, and every DOI printed in the reference list resolves through
  `doi.org/api/handles`. A citation that did not resolve would fail the gate rather than ship.
- **`check_numbers`.** The 66 numbers quoted in the prose and in the tables are recomputed
  from `numbers_source.py` at gate time and searched for in the extracted PDF text. A stale
  build, or an edit that changes a figure without rebuilding, fails here.
- **Clean room.** A fresh clone builds the same PDF from the committed sources alone: the
  figures, the tables, the numbers and the document are all regenerated, and the working tree
  stays clean, which means the committed PDF is byte-identical to the one the build produces
  (reportlab runs with `rl_config.invariant = 1`, and the only image that is not generated is
  the GUI capture, which is committed with the sources).

## What is NOT verified

- **The brief itself.** No Canvas item existed when this was built. The report is written
  against the in-class debrief transcribed in `docs/brief_intake.md`; if the digital brief
  asks for anything else, `report/README.md` and `TASK.md` say which parts would change
  (§6.5 of the report).
- **Experimental validation.** Nothing here is compared with a measured correlation function
  from a real instrument or with published DLS data. The model is checked against its own
  inputs and against the equations it implements; that is consistency, not accuracy.
- **The physics approximations.** The `0.35 P_sphere + 0.65 P_Guinier` blend is not a Mie
  solution, the aggregate population is a second lognormal mode rather than a fractal
  aggregate, the photon trace is illustrative, and the count-rate model is a stated
  instrument model with a 15-2500 kcps clip. Each is declared in the report (Table 10) and in
  `docs/model.md`.
- **The noise model.** Correlation noise is additive on `g2-1` and clipped at zero, which is
  one-sided; the report measures what that does to the inversion (-12.6 to -15.9 %) and to
  the PDI (0.00-0.22 across seeds at 1 % noise) instead of claiming the numbers are
  instrument-grade. A Poisson or multi-tau noise model would need a physics change and a test.
- **The z-average's scatter.** In this model the z-average is computed from the moments of the
  input distribution, so it carries no fitting noise. An instrument would fit it from the
  same noisy curve. This is declared in the report (Table 10) and is a real limitation of the
  verification, not a hidden one.
- **PBS and toluene constants.** They are in the code but their `n` and `eta` values are
  stated handbook numbers without a line-checked source in the audit. They are not used for
  any claim in the report.
- **Zeta potential.** Not modelled, and not claimed anywhere.
- **The GUI screenshot.** It is a real capture of the program running on a virtual X display
  (Xvfb `:97`), not a mock-up, but it is a capture: its pixels are not reproduced by
  `tools.check_all`. The capture script is committed so it can be regenerated.

## Reproduce

```
cd assignments/03-dls-simulator
uv sync --frozen
uv run python -m tools.check_all
```

The only step that needs the network is the DOI resolution inside `check_pdf.py`; add
`--offline` to skip it.
