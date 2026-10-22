# XRD simulator - sources and confidence

Compiled 2026-10-22 for `assignments/02-xrd-diffractometer/`. This file records where
every shipped number comes from and how firm it is. Nothing here is invented: where no
citable value existed the assumption is named and marked **design choice**.

Confidence column: **firm** = read from a primary record or certificate; **derived** =
computed here from firm values, with the calculation stated; **provisional** = a value in
common use that could not be read from a primary source on this host; **choice** = a
modelling decision, not a measurement.

## 1. Radiation

| quantity | value | confidence | source / note |
| --- | --- | --- | --- |
| Cu K-alpha1 | 1.540598 A | provisional | value in common use; the primary tables (ITC Vol C, Deslattes 2003) could not be read from this host. Crossref-verified reference for the convention: doi:10.1107/S0567739468000550 (Cromer & Mann) is *not* the wavelength source; a primary wavelength citation is still owed. |
| Cu K-alpha2 | 1.544426 A | provisional | same |
| Cu K-beta | 1.392250 A | provisional | same |
| K-alpha2 / K-alpha1 | 0.497 | provisional | standard doublet ratio; not re-measured here |
| K-beta / K-alpha | 0.20 | provisional | used only when K-beta is switched on; not used in shipped figures |
| Ni filter, 15 um | 0.52 (K-alpha) / 0.024 (K-beta) | provisional | from the instrument research note; only used to justify removing K-beta |

These four wavelengths set every peak position. If the course expects a different
wavelength convention (for example the 1.5405929 A printed on some NIST certificates), the
positions move by about 0.002 deg at 30 deg - below the line width, but it should be
stated in the report.

## 2. Scattering factors

| item | value | confidence | source |
| --- | --- | --- | --- |
| f0 parametrisation | Waasmaier-Kirfel 5-Gaussian + constant | firm | doi:10.1107/S0108767394013292, Acta Cryst. A51, 416-431 (1995) |
| table build | `tools/build_scattering_factors.py`, 0 to 0.80 1/A in 0.002 steps | derived | values taken from xraydb 4.5.8, which carries that parametrisation |
| check | f0(0) reproduces Z within 1% for Si, Cu, Fe, O | derived | `tests/test_structure_samples.py` |
| anomalous dispersion f', f'' | neglected | choice | < 1% for Cu K-alpha and the elements shipped; stated as a fidelity limit |

`data/scattering_factors.json` is generated, not hand-edited. Rebuild it with
`uv run python tools/build_scattering_factors.py`; the script is a dev dependency on
xraydb, the simulator itself needs only numpy.

## 3. Phases

| key | formula | space group | cell (A) | confidence | source |
| --- | --- | --- | --- | --- | --- |
| si | Si | Fd-3m | a = 5.431144 | firm | NIST SRM 640f certificate, a = 5.431144(8) A at 22.5 C |
| al | Al | Fm-3m | a = 4.0495 | provisional | room-temperature conventional value. AFLOW `Al1_ICSD_52611` (primitive 2.856 A) converts to 4.0398 A, a different entry; the conventional value reproduces the published 111 line at 38.47 deg. |
| cu | Cu | Fm-3m | a = 3.6149 | provisional | room-temperature conventional value; AFLOW `Cu1_ICSD_53755` converts to 3.6146 A |
| fe | alpha-Fe | Im-3m | a = 2.8665 | provisional | room-temperature conventional value. The AFLOW `Fe1_ICSD_631722` entry reads 2.9647 A (3.4% high, probably expanded or high-temperature) and is deliberately NOT used. |
| nacl | NaCl | Fm-3m | a = 5.6402 | provisional | room-temperature conventional value; AFLOW `Cl1Na1_ICSD_60280` converts to 5.665 A |
| mgo | MgO | Fm-3m | a = 4.2112 | provisional | room-temperature conventional value; AFLOW `Mg1O1_ICSD_173128` converts to 4.253 A |
| zno | ZnO | P63mc | a = 3.2494, c = 5.2038 | firm | COD 9004180; u(O) = 0.3819 |
| tio2-rutile | TiO2 | P42/mnm | a = 4.5937, c = 2.9587 | provisional | room-temperature conventional values; u(O) = 0.3047. The research note listed COD 9004143 as 4.616 / 2.977 A, which puts 110 at 27.30 deg instead of the published 27.45 deg, so the conventional values are used and the COD record has to be re-read before they are called firm. |

| tio2-anatase | TiO2 | I41/amd | a = 3.7892, c = 9.537 | firm | COD 9008214; z(O) = 0.2079; the basis is expanded from the deposited CIF by gemmi, not hand-written |

The COD CIFs were fetched with `curl` on 2026-10-22; Python's urllib hit a TLS reset on the
same host. The expansion of each CIF into a full conventional-cell basis is done by gemmi
(`tools/` carries no build step for this yet: the sites are written into `xrdsim/samples.py`
with the COD id in the source column).

**Every phase is checked against its published strongest reflection** in
`tests/test_structure_samples.py`: Si 111 at 28.44, Al 111 at 38.47, Cu 111 at 43.30,
Fe 110 at 44.67, NaCl 200 at 31.69, MgO 200 at 42.92, ZnO 101 at 36.25, rutile 110 at
27.45, anatase 101 at 25.28 deg. That test is what caught the wrong cell constants above.

**Warning carried from the research pass:** COD and AFLOW entries are not interchangeable.
The same element appears with lattice constants differing by 0.5-3% because the entries come
from different papers, temperatures and pressures, and AFLOW's relaxed fields can come from
DFT. Each row above states which record was used.

**Basis coordinates** are the symmetry-expanded conventional cell for each space group,
written out in `xrdsim/samples.py`. They are textbook Wyckoff positions, not fetched per
site from a CIF; the cell constants are the sourced part.

**Debye-Waller:** every site ships B = 0.5 A^2 as a single stated assumption. No
per-site B was read from the records.

## 4. Instrument model

| item | value | confidence | note |
| --- | --- | --- | --- |
| Caglioti U, V, W | 0.004, -0.002, 0.003 | choice | gives a 0.05-0.07 deg FWHM over 20-90 deg; no diffractometer was measured, so these are plausible defaults, not fitted values |
| pseudo-Voigt eta | 0.5 | choice | half Gaussian, half Lorentzian |
| scan max 2theta | 150 deg | choice | goniometers do not reach 180 deg, and the Lorentz-polarisation factor diverges there |
| dead time | 0 (off by default) | choice | exposed as a control, not calibrated |
| background | flat, counts/s | choice | no measured background was fitted |
| reference counts | integrated counts at the strongest reflection | choice | sets the noise level, not a radiometric calibration |

## 5. Multiplicity and absences

Multiplicities are computed by orbit counting in `xrdsim/structure.py`, not tabulated, and
are tested against the powder-average values for cubic, tetragonal and hexagonal families.
One row in the external research note (tetragonal (211) = 8) is wrong: the point group has
16 operations and (211) is a general position, so the multiplicity is 16. The code and the
test carry 16.

Absences come from the structure factor itself, so the diamond 222, the FCC 100/110/210 and
the BCC 100/111 reflections are zero because the summed phases cancel, not because a table
says so. `tests/test_structure_samples.py` checks all four cases.
