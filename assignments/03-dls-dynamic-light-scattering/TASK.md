# Assignment 3 - DLS simulator (working spec)

Course: EE4005 Nano/Micro-Scale System Design.
Source of the brief: in-class debrief 2026-11-12 (notebook page `W7 L2 12/10`); see
`docs/brief_intake.md` for the transcription and the flagged readings. No Canvas item
exists yet.

## Scope

Build a dynamic light scattering (DLS) simulator. It must take the inputs named in class
and produce the outputs named in class:

Inputs: solvent (water, ethanol), aggregation parameters, particle refractive index,
particle size, temperature.

Outputs: autocorrelation function with a log delay-time axis plus the photon-count trace,
size distribution by number and by intensity, and the polydispersity index (PDI).

## Requirement map

| # | ask | artifact | status |
| --- | --- | --- | --- |
| R1 | DLS simulator design | `dlssim/` package + CLI | in progress |
| R2 | five named inputs | `solvents.py`, `materials.py`, `sizes.py`, `aggregation.py` | in progress |
| R3 | three named outputs | `correlation.py`, `detector.py`, `inversion.py`, `analysis.py` | in progress |
| R4 | screenshots + code appendix | `report/` | pending digital brief |
| R5 | explanation section | `report/` | pending digital brief |

## Model summary

- Scattering vector `q = 4 pi n / lambda * sin(theta/2)`, He-Ne 633 nm, theta = 178 deg.
- Stokes-Einstein `D = k_B T / (3 pi eta d)`, decay rate `Gamma = D q^2`.
- Field correlation `g1(tau) = sum_i w_i exp(-Gamma_i tau)` over the intensity-weighted
  population; measured `g2 = 1 + beta |g1|^2`.
- Cumulant analysis of `ln g1` gives the mean decay rate and the second cumulant;
  `PDI = 2 mu2 / Gamma_mean^2` (ISO 22412 definition).
- Inversion: regularised non-negative least squares on a log-spaced diameter grid.
- Aggregation: fractal clusters of `N` primaries, `Rg = a N^(1/df)`, `Rh = 0.9 Rg`,
  Guinier structure factor for the scattered intensity.

## Inferences (not the brief's words)

- Report structure and the code appendix follow assignments 1 and 2.
- Log axis on the autocorrelation means log delay time.
- PDI uses the ISO 22412 cumulant definition.

## Open questions

1. Digital brief: does it add graded items beyond the five inputs and three outputs?
2. Zeta potential: listed on the page but not as a simulator output; build only if asked.
3. Detection angle: 178 deg as written, or 173 deg as in commercial backscatter instruments?
