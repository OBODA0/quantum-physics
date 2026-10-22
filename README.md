# Quantum physics - nano capsule assignments

Simulators written for the quantum physics section of the nano capsule class
(EE4005, Nanotechnology & Quantum Physics).

Each assignment is self-contained: its own Python package, tests, data pack and report
generator. Assignment 1's PDF is the submitted document; assignment 2's is a draft until its
brief arrives.

| # | assignment | simulator | report |
| --- | --- | --- | --- |
| 1 | PL spectrometer | `plsim` - xenon lamp, two monochromators, dye database, photodiode | [markdown](assignments/01-pl-spectrometer/README.md) - [PDF](assignments/01-pl-spectrometer/report/Assignment_1_PL_Spectroscopy_Simulation_Report.pdf) |
| 2 | XRD diffractometer | `xrdsim` - Bragg-Brentano scan, structure factors, K-alpha doublet, Scherrer | [markdown](assignments/02-xrd-diffractometer/README.md) - [draft PDF](assignments/02-xrd-diffractometer/report/Assignment_2_XRD_Diffractometer_Report.pdf) |

## Layout

```
assignments/
  01-pl-spectrometer/        assignment 1: package, tests, data pack, report
  02-xrd-diffractometer/     assignment 2: XRD diffractometer simulator
```

## Running an assignment

Each assignment has its own environment. From the assignment folder:

```
uv sync
uv run pytest
```

Both assignments have a command line interface:

```
uv run python -m plsim --help
uv run python -m plsim --sample cy5 --lambda-exc 649 --range 600 780
```

```
uv run python -m xrdsim --list-phases
uv run python -m xrdsim --phase si --range 20 100 --out out/si.png
```

The report in each assignment folder is generated from the same source as the
PDF, so the markdown and the PDF cannot drift:

```
uv run python report/generate_readme.py
uv run python report/generate_pdf_report.py
```

## Assignment 1 at a glance

A photoluminescence spectrometer: xenon lamp -> excitation monochromator ->
harmonic filter -> dye sample -> detection monochromator -> silicon photodiode.
It reproduces the measured spectra of Cy3, Cy5 and methylene blue, and checks
Kasha's rule by sweeping the excitation wavelength from 400 nm to 700 nm.

Full report: [assignments/01-pl-spectrometer](assignments/01-pl-spectrometer/README.md).
