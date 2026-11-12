# Constants and their provenance

Every number the simulator uses, with where it came from and how sure we are.

| quantity | value used | source | status |
| --- | --- | --- | --- |
| Boltzmann constant | 1.380649e-23 J/K | SI 2019 definition (exact) | exact |
| laser wavelength | 633 nm | He-Ne line | instrument choice |
| detection angle | 178 deg | class debrief page W7 L2 12/10 | **uncertain reading**: 173 deg is the common backscatter angle; configurable |
| water viscosity, 0-60 C | 1.7914 ... 0.4660 mPa s | Kestin, Sokolov & Wakeham (1978) standard values | correlation-based values, tabulated here every 5-10 K and interpolated with PCHIP |
| ethanol viscosity, 0-50 C | 1.773 ... 0.702 mPa s | CRC Handbook (97th ed.) | handbook values, interpolated |
| water n(lambda), 20 C | Cauchy A = 1.323950, B = 0.003101 um^2 | Hale & Querry (1973), interpolated | their table is 3 decimals at 25 C; our fit is anchored on 405-656 nm and residual < 2e-4 |
| ethanol n(lambda), 20 C | Cauchy A = 1.348566, B = 0.004346 um^2 | CRC / Sellmeier data | fit residual < 3e-5 |
| dn/dT, water | -1.0e-4 /K | literature value near 20 C | stated value |
| dn/dT, ethanol | -4.0e-4 /K | literature value near 20 C | stated value |
| polystyrene n (633 nm) | 1.5872 | refractiveindex.info dispersion | stated value |
| silica n (633 nm) | 1.4571 | fused-silica dispersion | stated value |
| PMMA n (633 nm) | 1.4893 | literature dispersion | stated value |
| rutile TiO2 n (633 nm) | 2.614 | literature (ordinary ray) | stated value |
| densities | PS 1050, silica 2000, PMMA 1180, TiO2 4230 kg/m^3 | standard handbook values | stated values |

The reference audit (`docs/research/reference_audit.md`) records which sources were resolved and
which claims they can carry. Two attribution rules come out of it: the PDI factor of 2 belongs to
ISO 22412 (2025 edition), not to Koppel, and the coherence factor beta is an instrument property,
not part of the ideal Siegert relation.
