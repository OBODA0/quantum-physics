# Brief intake - Assignment 3 (DLS)

Source: in-class debrief, OBODA's notebook photo (page marked `W7 L2 12/10`), supplied
2026-11-12. No digital version exists on Canvas yet: course 741 lists only Assignment 1
(960) and Assignment 2 (1384); the newest announcement is the 5th lab session (DLS,
10 Nov). A digital debrief is expected on Canvas later and must be reconciled with this
transcription when it appears.

## Verbatim transcription of the debrief

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

Readings that are *not* certain from the photo, flagged per the house rule (never present
my reading as the brief's words):

| item | transcription | status |
| --- | --- | --- |
| detector angle | `178 deg` | **uncertain**: could be 173 or 179. Backscatter DLS is normally 173 deg (Malvern Zetasizer) or 175 deg. Default taken as 178 deg because that is what the page shows; configurable. |
| autocorrelation x axis | `(x axis log)` | **uncertain**: the parenthesis is cramped; could read `size axis log`. In DLS the correlation x axis is delay time, normally log-spaced, so log time is the physical reading. |
| waveform annotation | `include photon count/t` | **uncertain**: reads like "Mattn count/t"; photon counts vs t is the trace drawn on the page, so that is the reading. |
| PDI threshold | `if PDI < 0.2` | transcribed as written. ISO 22412 calls < 0.05 monodisperse and < 0.2 the usual acceptability limit. |
| zeta potential | separate bullet | the page lists zeta potential as a concept (surface charge), not as a simulator output. Not built unless the digital brief asks. |

## Requirement map (provisional until the digital brief)

| # | ask (source) | artifact | how it is checked |
| --- | --- | --- | --- |
| R1 | design a DLS simulator (debrief) | `dlssim/` package, one module per stage, CLI | `uv run python -m dlssim --help`, tests |
| R2 | inputs: solvent, aggregation, particle refractive index, size, temperature (debrief) | `dlssim/solvents.py`, `aggregation.py`, `materials.py`, `sizes.py` | input sweep tables, tests per input |
| R3 | outputs: autocorrelation + photon trace, number/intensity distribution, PDI (debrief) | `dlssim/correlation.py`, `detector.py`, `inversion.py`, `analysis.py` | figures + `check_numbers` |
| R4 | screenshots for varying structure/parameters + code appendix (**expected**: pattern of assignments 1 and 2) | `report/make_figures.py`, generated Appendix A | `check_pdf` |
| R5 | explanation of what the outputs mean and how size maps to correlation decay (**expected**) | report sections 3-4 | prose + numbers gate |

Items R4 and R5 are **Inference** from assignments 1 and 2; they must be confirmed against
the digital brief before the report is finalised.

## Constraints carried from the course

- PS1: a hallucinated or irrelevant reference scores 0 for the whole assignment. Every
  citation resolves before it ships; `report/references/AUDIT.md` records the check.
- PS2: one PDF, everything inside it (figures, tables, references, code appendix).
