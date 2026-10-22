# report/

Figures and, later, the PDF report for assignment 2.

## Figures

| file | what it shows | how it is made |
| --- | --- | --- |
| `figures/instrument.png` | the Bragg-Brentano chain the simulator models | `instrument_diagram()` in `make_figures.py` |
| `figures/phase_panel.png` | one simulated pattern for each of the nine phases, 20-90 deg | `phase_panel()` |
| `figures/scherrer.png` | silicon 111 at 5, 20 and 200 nm crystallite size | `scherrer_demo()` |
| `figures/doublet.png` | silicon 422 with and without K-alpha2 | `doublet_demo()` |

Nothing in `figures/` is drawn by hand. Regenerate them all with:

```
uv run python -m report.make_figures
```

The module is run with `-m` so the package `xrdsim` is importable from the assignment
root; a plain `python report/make_figures.py` puts `report/` on `sys.path` instead and
fails to import.

## The PDF

Not built yet. The report follows the brief, which has not been received; `TASK.md`
section 6 records the submission rules to reproduce once it arrives. The generator will
follow assignment 1: a single PDF, built from `reportlab`, gated by `check_pdf.py` before
upload.
