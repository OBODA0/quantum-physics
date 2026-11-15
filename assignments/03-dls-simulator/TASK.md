# Assignment 3 - DLS simulator (working spec)

Course: EE4005 Nano/Micro-Scale System Design.
Brief source: in-class debrief 2026-11-12 (notebook page `W7 L2 12/10`), transcribed in
`docs/brief_intake.md`. No Canvas item exists yet.

## Scope

A dynamic light scattering simulator that takes the inputs named in class (solvent,
aggregation, particle refractive index, size, temperature) and produces the outputs named
in class (autocorrelation on a log axis with the photon trace, number and intensity size
distributions, PDI), plus the submission report that presents and measures it.

## Status

| item | state |
| --- | --- |
| package, CLI, GUI | done |
| physics tests (18) | done |
| inversion of the correlation curve | done |
| provenance and model docs | done |
| reference audit (10 entries) | done |
| report pipeline: figures, tables, numbers, PDF | done |
| gates: `check_pdf`, `check_numbers`, `tools/check_all` | done |
| `VERIFICATION.md`, `report/README.md` | done |
| reconcile with the digital brief | pending the brief |

## Inferences (not the brief's words)

- Report structure and code appendix follow assignments 1 and 2 (R4, R5 in
  `docs/brief_intake.md`). The report marks them as inference.
- Log axis on the autocorrelation means log delay time.
- PDI uses the ISO 22412:2025 definition, `PDI = 2 mu2 / Gamma^2`.
- The detector angle is a choice: the report uses 173 deg everywhere and quantifies the
  178 deg reading of the page (0.17 % on every diameter, Table 9 of the report).
- **The width and shape of the size distribution are treated as a sixth input.** The page
  names five inputs; without a width there is no intensity distribution and no non-zero PDI,
  so the width is a derived requirement, listed here rather than attributed to the page.

## Report

`report/Assignment_3_DLS_Simulator_Report.pdf`, 66 pages. Built from the simulator by
`report/make_figures.py`, `report/tables.py`, `report/size_study.py` and
`report/generate_pdf_report.py`; every quoted number comes from `report/numbers_source.py`
and is checked against the built PDF. Page map and rebuild commands: `report/README.md`.
What was verified, and what was not: `VERIFICATION.md`.

## Open questions

1. Digital brief: does it add graded items beyond the five inputs and three outputs? The
   report's section 6.5 lists what would change for each plausible difference.
2. Zeta potential: listed on the page but not as an output; not built. It needs a different
   technique (electrophoretic light scattering), so it is out of scope unless asked.
3. Angle: 173 deg is used in every figure and table; 178 deg is quantified in Table 9. If the
   digital brief states one, change `ANGLE_DEG` in `report/cases.py` and rebuild.
