# Research notes

Three notes were produced on 2026-10-22 by separate research workers, before the
assignment brief arrived. They are kept verbatim so that a later reader can see what was
known, and what was wrong, at the time.

| file | what it is | how it was used |
| --- | --- | --- |
| `01_instrument_model.md` | the Bragg-Brentano chain, Cu tube lines, absorption, peak shapes, detector, and a module split | shaped `xrdsim/` and `TASK.md` section 9 |
| `02_analysis_and_materials.md` | d-spacings, indexing, absences, the intensity expression, Scherrer/Williamson-Hall, reference materials, COD/AFLOW access | shaped `structure.py`, `analysis.py` and the phase table |
| `03_document_conventions.md` | the conventions of assignment 1's `TASK.md` and report, and a skeleton for this one | `TASK.md` was written from this skeleton |

## Corrections applied after checking

These notes are not authority. Each item below was tested against the simulator or a
published value before it was used:

| claim in the notes | what was found | where it is recorded |
| --- | --- | --- |
| tetragonal (211) has multiplicity 8 | the point group has 16 operations and (211) is a general position, so 16 | `tests/test_structure_samples.py` |
| rutile a = 4.616, c = 2.977 A (COD 9004143) | puts 110 at 27.30 deg instead of the published 27.45; conventional 4.5937 / 2.9587 A used | `data/SOURCES.md` |
| Al, Cu, NaCl, MgO primitive-to-conventional conversions | each conversion shifts the strongest line by up to 0.4 deg; conventional room-temperature values used instead | `data/SOURCES.md` |
| anatase basis (not in the notes; written by hand) | produced a forbidden 001 line at 9.27 deg; replaced with the COD CIF expanded by gemmi | `VERIFICATION.md` section 3 |
| Cu K-alpha wavelengths | still provisional: no primary table could be read from this host | `data/SOURCES.md` section 1 |

## What is still only in these notes

The notes contain material the simulator does not yet use: Williamson-Hall and microstrain,
peak-profile fitting practice with uncertainties, indexing for tetragonal cells, the full
intensity prefactor, and the COD/AFLOW/AMCSD access map. It stays here for the report and
for whatever the brief turns out to ask.
