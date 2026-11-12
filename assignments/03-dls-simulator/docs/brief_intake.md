# Brief intake - Assignment 3 (DLS)

Source: in-class debrief, OBODA's notebook page marked `W7 L2 12/10`, supplied
2026-11-12. No Canvas item exists yet: course 741 lists only Assignment 1 (960) and
Assignment 2 (1384); the newest announcement is the 5th lab session (DLS, 10 Nov). A
digital debrief is expected later and must be reconciled with this transcription.

## Verbatim transcription of the page

> 1) DLS : Dynamic Light Scattering
> - to detect the size of nano particles
>
> **Zeta potential**
> - measures the surface charge of nano particles
> - those particles experience "thermal motion" -> Brownian motion
>
> [diagram] Laser source -> cuvette (sample containing particles in a solvent) -> detector
> at 178 deg
>
> [plot] photon counts vs t -> auto-correlation: if particle larger -> slower; if particle
> smaller -> faster
>
> [plot] Number/Intensity vs size -> size distribution -> PDI; if PDI < 0.2
>
> **Simulation task(s): design a DLS simulator**
>
> Inputs:
> - select solvent (water, ethanol)
> - aggregation parameters
> - refractive index of the particle
> - size of the particle
> - temperature
>
> Outputs:
> - auto correlation function (x axis log), include photon count/t
> - size distribution [Number, Intensity]
> - PDI

## Readings that are not certain from the photo

| item | transcription | status |
| --- | --- | --- |
| detector angle | `178 deg` | uncertain: could be 173 or 179. Commercial backscatter instruments use 173 deg. The simulator defaults to 173 deg and the angle is a CLI input; the report must state which was used. |
| autocorrelation x axis | `(x axis log)` | uncertain: could read `size axis log`. In DLS the correlation x axis is delay time, normally log-spaced; that is the physical reading. |
| waveform annotation | `include photon count/t` | uncertain print; photon counts vs t is the trace drawn on the page, so that is the reading. |
| PDI threshold | `if PDI < 0.2` | transcribed as written. ISO 22412 treats < 0.05 as monodisperse and < 0.2 as the usual acceptance limit. |
| zeta potential | separate bullet | listed as a concept (surface charge), not as a simulator output. Not built unless the digital brief asks. |

## Requirement map (provisional)

| # | ask (source) | artifact | status |
| --- | --- | --- | --- |
| R1 | design a DLS simulator (debrief) | `dlssim/` package, CLI, GUI | done |
| R2 | solvent, aggregation, particle RI, size, temperature inputs (debrief) | `solvents.py`, `distribution.py`, `mie.py`, `simulator.py` | done |
| R3 | autocorrelation + photon trace, number/intensity distributions, PDI (debrief) | `autocorrelation.py`, `cumulants.py`, `inversion.py`, `plot.py` | done |
| R4 | screenshots for varying parameters + code appendix (expected, from assignments 1-2) | `report/` | pending digital brief |
| R5 | explanation of what the outputs mean (expected) | report sections | pending digital brief |

R4 and R5 are inference from assignments 1 and 2, not the debrief's words.

## Constraints carried from the course

- PS1: a hallucinated or irrelevant reference scores 0 for the whole assignment. Every
  citation resolves before it ships; see `docs/research/reference_audit.md`.
- PS2: one PDF, with figures, tables, references and the code appendix inside it.
