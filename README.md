# PL spectrometer simulator

Simulator for a photoluminescence (PL) spectrometer, written for the quantum
physics section of the nano capsule class.

It models the instrument from the lab notes:

```
xenon lamp -> monochromator (lambda_exc) -> harmonic filter -> sample
                                                               |
                     photodetector <- monochromator (scan) <---+
```

## User settings

| setting | flag | meaning |
| --- | --- | --- |
| `lambda_exc` | `--lambda-exc` | excitation wavelength selected from the xenon lamp |
| `lambda_min`, `lambda_max` | `--range` | PL detection range |
| `delta lambda` | `--dlambda` | step size of the detection scan |
| sample | `--sample` | dye from the sample database |

## Sample database

| key | dye | absorption | emission | quantum yield | molar extinction |
| --- | --- | --- | --- | --- | --- |
| `cy3` | Cy3 | 550 nm | 570 nm | 0.04 (free dye in PBS) | 150,000 |
| `cy5` | Cy5 | 649 nm | 670 nm | 0.28 (aqueous) | 250,000 |
| `methylene-blue` | Methylene blue | 664 nm | 685 nm | 0.02 (water) | 67,000 |

The quantum yields are the honest ones for the stated solvent, and they matter:
the same Cy3 chromophore is reported at 0.10-0.31 when it is conjugated or in a
low-polarity environment, and methylene blue is 0.04 in ethanol but 0.02 in
water. Always quote the number together with the solvent.

Two databases are available:

- `--database reference` (default): measured absorption and emission bands from
  `data/reference_spectra.json` — digitized vendor/database/paper curves, so the
  simulated spectrum has the real band shape, including the cyanine vibronic
  shoulder.
- `--database model`: Gaussian bands with the same centres, widths and quantum
  yields (the compact model used in `plsim/samples.py`).

## Install and run

```
uv sync
uv run python -m plsim --list-samples
uv run python -m plsim --sample cy5 --lambda-exc 649 --range 600 780 --dlambda 0.5
uv run python -m plsim --sample methylene-blue --lambda-exc 664 --range 550 800 --ideal
uv run python -m plsim --sample cy5 --database model --lambda-exc 649 --range 600 780
```

The figure is written to `out/` unless `--show` is given. `--ideal` removes the
stray excitation light, so only the PL spectrum is left.

The absorbance the model uses is `A_peak = epsilon * c * l`. `--concentration`
(mol/L) with `--path-length` (cm) sets it from the dye's extinction coefficient;
`--peak-absorbance` sets it directly. Equal concentration is *not* equal
absorbance: at 1 umol/L in a 1 cm cuvette the three dyes sit at A = 0.150, 0.250
and 0.067, which is why the third question has a non-trivial answer.

## Experiments

```
uv run python report/generate_assignment_figures.py                  # all three questions
uv run python report/generate_assignment_figures.py --only part2     # the Cy3 sweep
uv run python report/generate_numbers.py                             # rewrite report/numbers.md
```

`report/report_figures/` holds the spectra the assignment asks for, and they are
the screenshots the report needs: one per dye for question 1, the sweep for
question 2, the three-dye comparison for question 3. `report/numbers.md` is
generated from the code and the reference pack, so the report never retypes a
number by hand and the text cannot drift away from the code.

## What is modelled, and how real it is

- **Xenon lamp**: smooth approximation of the arc continuum plus the strongest
  xenon lines. A shape model, not a measured lamp spectrum.
- **Monochromator**: Gaussian passband, given bandwidth and throughput. The
  excitation monochromator is 5 nm, the detection monochromator 2 nm.
- **Harmonic filter**: passes wavelengths above 400 nm and blocks what is below,
  which is where the second-order (harmonic) grating output lands.
- **Sample**: one absorption band and one emission band per dye, taken from the
  measured reference pack by default. Absorbed fraction from the Beer-Lambert
  law, so the PL intensity is `P_exc * (1 - 10^-A(lambda_exc)) * QY`.
  The emission band does **not** depend on the excitation wavelength: a molecule
  that has absorbed a photon relaxes to the bottom of S1 before it emits, so
  sweeping `lambda_exc` changes only how much light is absorbed, never the shape
  or position of the spectrum (Kasha's rule, the subject of question 2).
  Anti-Stokes emission is deliberately not modelled: it is weak, and adding a
  Boltzmann factor on top of a measured band would double-count the vibronic
  envelope that is already in the measured band shape.
- **Photodetector**: silicon responsivity shape, weak in the UV, peaking near
  880 nm, cut off past about 1100 nm. Photocurrent `I = R(lambda) * P`.
- **Stray excitation light**: a small fraction of the excitation beam (1 % by
  default) reaches the detector. When `lambda_exc` lies inside the detection
  range it appears as a sharp line on top of the PL spectrum, which is what the
  filter and the second monochromator are there to suppress.

All powers and currents are in relative units: the model gives spectra and
relative intensities, not absolute radiometric values.

## Reference data and sources

`data/reference_spectra.json` holds the measured reference pack for the three
dyes: absorption and emission maxima, band FWHMs measured on the shipped curves,
quantum yields with their solvent, molar extinction coefficients, Stokes shifts,
notes and, for each dye, a digitized absorption and emission curve at 1 nm.
`data/SOURCES.md` gives a source and a confidence for every number, plus the
list of what could not be verified; `data/raw/` keeps the raw source data so
every digitized curve can be re-derived.

Where the sources disagree, the pack says so instead of hiding it. The main
open points:

- Cy3 and Cy5 curves come from FPbase, which does not state the provenance of
  its dye records; the fully documented curves for the same chromophores are
  PhotochemCAD records in methanol, kept in `data/raw/`.
- No digitized Cy3/Cy5 curve in aqueous buffer was obtainable (vendor
  SpectraViewer and several publishers block automated access), so the aqueous
  numbers are vendor values.
- Emission FWHM is instrument-limited: the PhotochemCAD emission curve was
  recorded with a 4.25 nm bandwidth.
- Methylene blue's widely quoted extinction coefficient of 95,000 had no
  citable primary source and was left out.
- Cy5 in methanol is reported at 0.4 by PhotochemCAD, while an integrating-sphere
  measurement gives 0.17.

## Layout

```
plsim/bands.py          Gaussian and tabulated band shapes
plsim/sources.py        xenon lamp, monochromator, harmonic filter
plsim/samples.py        dye database, concentration, absorbance
plsim/reference.py      loader for the measured reference pack
plsim/detector.py       silicon photodiode
plsim/spectrometer.py   the instrument, producing a PL scan
plsim/analysis.py       excitation scans and their model checks
plsim/plot.py           matplotlib rendering
plsim/cli.py            command line interface
data/                   measured reference pack + sources + raw source data
report/                 assignment figures, numbers, and the report itself
tests/                  the physics the report claims (uv run pytest)
TASK.md                 the assignment, its requirements and the open items
```
