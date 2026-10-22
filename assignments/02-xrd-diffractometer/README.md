# XRD diffractometer simulator

Simulator for an X-ray powder diffractometer, written for the quantum physics section of
the nano capsule class (assignment 2).

It models a Bragg-Brentano laboratory instrument:

```
X-ray tube (Cu K-alpha) -> divergence slit -> Soller slit -> flat sample (theta/2theta)
      -> receiving slit -> Soller slit -> monochromator -> detector
```

A scan returns counts against 2theta, built from the structure factor of the phase in the
beam, the Lorentz-polarisation factor, the powder multiplicity, the Debye-Waller term, the
Cu K-alpha1/K-alpha2 doublet, a Caglioti peak width, optional crystallite-size broadening
and Poisson counting statistics.

**Status:** the simulator core is complete and tested; the assignment brief has not been
received, so `TASK.md` carries the spec with its brief slots still marked `AWAITING BRIEF`.

## Running it

```
uv sync
uv run pytest
uv run python -m xrdsim --list-phases
uv run python -m xrdsim --phase si --range 20 100 --step 0.01 --out out/si.png
uv run python -m xrdsim --phase zno --range 25 70 --size 300 --out out/zno.png
uv run python -m xrdsim --phase si --table
```

| setting | flag | meaning |
| --- | --- | --- |
| phase | `--phase` | which sample is in the beam |
| 2theta range | `--range MIN MAX` | scan start and stop |
| step | `--step` | 2theta increment |
| dwell | `--dwell` | counting time per step |
| counts | `--counts` | integrated counts at the strongest reflection |
| size | `--size` | crystallite size in angstrom |
| displacement | `--displacement` | specimen surface off the goniometer axis, mm |
| doublet | `--no-ka2` | drop the K-alpha2 line |
| monochromator | `--monochromator 2THETA` | add the polarisation term |
| noise | `--noise SEED` | Poisson counts (0 disables) |
| table | `--table` | print the reflection table |
| index | `--index` | index the observed peaks, and name the lattice from the n^2 sequence |
| Scherrer | `--scherrer` | size from each peak, corrected for the instrument |

## Phases

| key | formula | space group | cell (A) | strongest line |
| --- | --- | --- | --- | --- |
| `si` | Si | Fd-3m | 5.431144 | 111 at 28.44 |
| `al` | Al | Fm-3m | 4.0495 | 111 at 38.47 |
| `cu` | Cu | Fm-3m | 3.6149 | 111 at 43.30 |
| `fe` | alpha-Fe | Im-3m | 2.8665 | 110 at 44.67 |
| `nacl` | NaCl | Fm-3m | 5.6402 | 200 at 31.69 |
| `mgo` | MgO | Fm-3m | 4.2112 | 200 at 42.92 |
| `zno` | ZnO | P63mc | 3.2494 / 5.2038 | 101 at 36.25 |
| `tio2-rutile` | TiO2 | P42/mnm | 4.5937 / 2.9587 | 110 at 27.45 |
| `tio2-anatase` | TiO2 | I41/amd | 3.7892 / 9.537 | 101 at 25.28 |

Cell constants, their provenance and their confidence are in `data/SOURCES.md`.

## Layout

```
xrdsim/     lattice, atoms, structure, samples, geometry, sources, profile,
            detector, diffractometer, analysis, plot, cli
tests/      one file per module group, 91 tests
data/       scattering_factors.json (generated), SOURCES.md
tools/      build_scattering_factors.py
```

## What is modelled, and what is not

Modelled: Bragg positions, relative intensities, doublet splitting, instrumental and
size broadening, Poisson noise, dead time, flat-plate absorption geometry.

Not modelled: Rietveld refinement, anomalous dispersion, texture, K-beta residual,
absolute intensities, and any measured background.
