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

| key | dye | absorption | emission | quantum yield |
| --- | --- | --- | --- | --- |
| `cy3` | Cy3 | 550 nm | 570 nm | 0.04 |
| `cy5` | Cy5 | 649 nm | 670 nm | 0.28 |
| `methylene-blue` | Methylene blue | 664 nm | 686 nm | 0.04 |

## Install and run

```
uv sync
uv run python -m plsim --list-samples
uv run python -m plsim --sample cy5 --lambda-exc 649 --range 600 780 --dlambda 0.5
uv run python -m plsim --sample methylene-blue --lambda-exc 664 --range 550 800 --ideal
```

The figure is written to `out/` unless `--show` is given. `--ideal` removes the
stray excitation light, so only the PL spectrum is left.

## What is modelled, and how real it is

- **Xenon lamp**: smooth approximation of the arc continuum plus the strongest
  xenon lines. A shape model, not a measured lamp spectrum.
- **Monochromator**: Gaussian passband, given bandwidth and throughput. The
  excitation monochromator is 5 nm, the detection monochromator 2 nm.
- **Harmonic filter**: passes wavelengths above 400 nm and blocks what is below,
  which is where the second-order (harmonic) grating output lands.
- **Sample**: one Gaussian absorption band and one Gaussian emission band per
  dye. Absorbed fraction from the Beer-Lambert law with an absorbance of 1 at the
  peak, so the PL intensity is `P_exc * (1 - 10^-A(lambda_exc)) * QY`. No
  emission is modelled below the excitation wavelength (Stokes shift).
  Band centres and quantum yields are typical literature values for the free
  dye in the given solvent; the real bands are asymmetric, these are Gaussians.
- **Photodetector**: silicon responsivity shape, weak in the UV, peaking near
  880 nm, cut off past about 1100 nm. Photocurrent `I = R(lambda) * P`.
- **Stray excitation light**: a small fraction of the excitation beam (1 % by
  default) reaches the detector. When `lambda_exc` lies inside the detection
  range it appears as a sharp line on top of the PL spectrum, which is what the
  filter and the second monochromator are there to suppress.

All powers and currents are in relative units: the model gives spectra and
relative intensities, not absolute radiometric values.

## Layout

```
plsim/bands.py          Gaussian band shapes
plsim/sources.py        xenon lamp, monochromator, harmonic filter
plsim/samples.py        dye sample database
plsim/detector.py       silicon photodiode
plsim/spectrometer.py   the instrument, producing a PL scan
plsim/plot.py           matplotlib rendering
plsim/cli.py            command line interface
tests/                  sanity checks (uv run pytest)
```
