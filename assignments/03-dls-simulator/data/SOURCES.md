# Constants and their provenance

| quantity | value used | source | status |
| --- | --- | --- | --- |
| Boltzmann constant | 1.380649e-23 J/K | SI 2019 definition | exact |
| laser wavelength | 632.8 nm | He-Ne line | instrument choice |
| detection angle | 173 deg default, 178 deg on the class page | class debrief; commercial backscatter practice | **choice**, configurable |
| water: n(25 C), dn/dT | 1.3312, -1.0e-4 /K | Hale & Querry (1973), interpolated to 633 nm | value at 633 nm is an interpolation of a 3-decimal table |
| water: VFT viscosity | A = 0.02414 mPa s, B = 570.58 K, T0 = 140 K | standard values, Kestin, Sokolov & Wakeham (1978) | fit anchored at 0.890 mPa s at 25 C; 0.2 % over 0-60 C |
| ethanol: n(25 C), dn/dT | 1.3594, -4.0e-4 /K | standard dispersion data | stated value |
| ethanol: VFT viscosity | A = 0.00593, B = 1550 K, T0 = 0 K | CRC Handbook values | fit anchored at 1.074 mPa s at 25 C |
| PBS: n, eta | 1.3340, 0.910 mPa s | physiological saline, standard tables | stated value |
| toluene: n, eta | 1.4941, 0.554 mPa s | standard tables | stated value |
| particle refractive index | user input, default 1.590 | polystyrene at 633 nm | user-settable |
| count-rate reference | 280 kcps at 50 nm, scaling with contrast and size | **stated instrument model** | not absolute |

The reference audit (`docs/research/reference_audit.md`) records which sources were
resolved and which claims they can carry.
