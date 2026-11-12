# Assignment 3 - DLS (dynamic light scattering)

Simulator for the class task: design a DLS instrument, feed it solvent, particle size,
refractive index, temperature and aggregation parameters, and read out the
autocorrelation function, the photon trace, the number and intensity size distributions
and the PDI.

## Run

```
uv sync
uv run python -m dlssim --help
uv run python -m dlssim --diameter 100 --sigma 1.1 --solvent water --temperature 25
uv run python -m pytest -q
```

The CLI writes `out/correlation.csv`, `out/distribution.csv` and `out/dashboard.png`.

## Layout

| path | contents |
| --- | --- |
| `dlssim/` | package: solvents, materials, sizes, scattering, brownian, correlation, detector, inversion, aggregation, model, CLI |
| `tests/` | physics checks: diffusion, q, correlation limits, cumulant recovery, inversion, aggregation, CLI |
| `data/SOURCES.md` | provenance for every constant |
| `docs/model.md` | equations, assumptions and declared limits |
| `docs/brief_intake.md` | the brief as transcribed from the class page |
| `report/` | figures, numbers and the PDF (after the digital brief arrives) |

## Status

Package, tests and documentation complete. The report is on hold until the digital brief
is published on Canvas, because the graded items are not yet in writing.
