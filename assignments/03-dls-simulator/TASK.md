# Assignment 3 - DLS simulator (working spec)

Course: EE4005 Nano/Micro-Scale System Design.
Brief source: in-class debrief 2026-11-12 (notebook page `W7 L2 12/10`), transcribed in
`docs/brief_intake.md`. No Canvas item exists yet.

## Scope

A dynamic light scattering simulator that takes the inputs named in class (solvent,
aggregation, particle refractive index, size, temperature) and produces the outputs named
in class (autocorrelation on a log axis with the photon trace, number and intensity size
distributions, PDI).

## Status

| item | state |
| --- | --- |
| package, CLI, GUI | done |
| physics tests | done |
| inversion of the correlation curve | done |
| provenance and model docs | done |
| report, figures, PDF, gates | pending the digital brief |
| reference audit | done |

## Inferences (not the brief's words)

- Report structure and code appendix follow assignments 1 and 2.
- Log axis on the autocorrelation means log delay time.
- PDI uses the ISO 22412 definition.
- The detector angle is a choice: 173 deg by default, 178 deg as written on the page.

## Open questions

1. Digital brief: does it add graded items beyond the five inputs and three outputs?
2. Zeta potential: listed on the page but not as an output; build only if asked.
3. Angle: 173 or 178 deg in the report's instrument description?
