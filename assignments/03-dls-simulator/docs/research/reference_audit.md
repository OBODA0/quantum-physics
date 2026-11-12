# Reference audit - assignment 3 (DLS)

Checked 2026-11-12 from the Blackwall outpost. Every identifier resolves through Crossref,
the DOI handle registry, OpenLibrary or the BSI resolver; the "claim supported" column says
what the source can actually carry. Where a source could not be read in full, that is stated.

| # | citation as it should appear | identifier | resolves | metadata | claim supported | evidence note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A. Einstein, Ann. Phys. 322(8), 549-560 (1905). | 10.1002/andp.19053220806 | yes | yes | derivation in sec. 3; PDF 403, no OA scan read here | series-4 vol 17 = whole-series 322 |
| 2 | B. J. Berne, R. Pecora, Dynamic Light Scattering, Dover (2000), ISBN 978-0-486-41155-2. | ISBN 978-0-486-41155-2 | yes | yes | g1/g2, Gamma = D q^2; not line-checked | ideal relation g2 = 1 + \|g1\|^2; beta is instrumental |
| 3 | D. E. Koppel, J. Chem. Phys. 57(11), 4814-4820 (1972). | 10.1063/1.1678153 | yes | yes | cumulant method yes; printed PDI formula not readable | guessed DOI 10.1063/1.1679199 resolves to an unrelated paper |
| 4 | ISO 22412:2025, Particle size analysis - Dynamic light scattering (DLS), 3rd ed. | BSI 10.3403/30461404 | yes | yes | clause 9.2 correlation analysis; PDI formula paywalled | 2017 edition withdrawn 2025-09-09 |
| 5 | R. Pecora, J. Chem. Phys. 40(6), 1604-1614 (1964). | 10.1063/1.1725368 | yes | yes | Doppler-shift framework; q is geometry | guessed DOI 10.1063/1.1725603 resolves elsewhere |
| 6 | C. F. Bohren, D. R. Huffman, Absorption and Scattering of Light by Small Particles, Wiley (1983), ISBN 978-0-471-05772-7. | ISBN 978-0-471-05772-7 | yes | yes | read: sec. 6.2 eq. (6.13) RGD sphere amplitude | book says "Rayleigh-Gans" |
| 7 | S. W. Provencher, Comput. Phys. Commun. 27(3), 213-227 (1982). | 10.1016/0010-4655(82)90173-4 | yes | yes | constrained regularised inversion | guessed ...90182-5 is a 404 |
| 8 | J. Kestin, M. Sokolov, W. A. Wakeham, J. Phys. Chem. Ref. Data 7(3), 941-948 (1978). | 10.1063/1.555581 | yes | yes | standard values + correlation equations | not a per-degree table |
| 9 | G. M. Hale, M. R. Querry, Appl. Opt. 12(3), 555-563 (1973). | 10.1364/AO.12.000555 | yes | yes | n(lambda) in the visible; 3 decimals at 25 C | 633 nm is an interpolation |
| 10 | W. M. Haynes (ed.), CRC Handbook, 97th ed., CRC Press (2016), ISBN 978-1-4987-5428-6. | ISBN 978-1-4987-5428-6 | yes | yes | organic-liquid viscosity tables; not line-verified | pin edition and ISBN |

## Corrections that change how the report cites things

1. Do not attribute `PDI = 2 mu2 / Gamma^2` to Koppel; the factor 2 is the ISO convention.
2. ISO 22412:2017 is withdrawn; cite the 2025 edition or name the edition.
3. beta is instrumental; the ideal Siegert relation has beta = 1.
4. `q` is geometry; cite Berne & Pecora, not Pecora 1964.
5. Hale & Querry give 3 decimals at 25 C; label n(633 nm) as interpolated.
6. Kestin et al. are standard values with correlation equations, not a printed table.
7. Three guessed DOIs were wrong, and two of the wrong ones still resolve to unrelated
   papers. Resolution alone proves nothing - the claim has to be checked.
