# Reference audit - assignment 3 (DLS)

Checked 2026-11-12 from the Blackwall outpost. Every identifier below resolves through
Crossref, the DOI handle registry, OpenLibrary or the BSI resolver; the "claim supported"
column says what the source can actually carry. Where a source could not be read in full
it is stated, not glossed over.

| # | citation as it should appear | identifier | resolves | metadata | claim supported | evidence note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A. Einstein, "Uber die von der molekularkinetischen Theorie der Warme geforderte Bewegung von in ruhenden Flussigkeiten suspendierten Teilchen", Ann. Phys. 322(8), 549-560 (1905). | 10.1002/andp.19053220806 | yes | yes: 322(8):549-560, 1905 | partly: derivation in sec. 3; Wiley PDF 403, no OA scan read here | series-4 vol 17 = whole-series 322; modern kT/(6 pi eta a) = Einstein's (RT/N)/(6 pi eta a) |
| 2 | B. J. Berne, R. Pecora, Dynamic Light Scattering: With Applications to Chemistry, Biology, and Physics, Dover (2000), ISBN 978-0-486-41155-2, 376 pp. (reprint of Wiley 1976) | ISBN 978-0-486-41155-2 | yes (OpenLibrary) | yes | yes in substance (g1/g2, Gamma = D q^2); access-restricted, not line-checked | ideal Siegert relation is g2 = 1 + \|g1\|^2; beta is instrumental |
| 3 | D. E. Koppel, "Analysis of Macromolecular Polydispersity in Intensity Correlation Spectroscopy: The Method of Cumulants", J. Chem. Phys. 57(11), 4814-4820 (1972). | 10.1063/1.1678153 | yes | yes: 57(11):4814-4820 | cumulant framework yes (abstract); printed PDI formula not readable | guessed DOI 10.1063/1.1679199 resolves to an unrelated paper |
| 4 | ISO 22412:2025, Particle size analysis - Dynamic light scattering (DLS), 3rd ed., ISO (2025). (2017 2nd ed. withdrawn 2025-09-09.) | BSI 10.3403/30461404 (2025 ed.); 2017: 10.3403/30314231 | yes (BSI) | yes | partly: clause 9.2 is correlation analysis; normative PDI formula paywalled | cite the 2025 edition; do not call 2017 current |
| 5 | R. Pecora, "Doppler Shifts in Light Scattering from Pure Liquids and Polymer Solutions", J. Chem. Phys. 40(6), 1604-1614 (1964). | 10.1063/1.1725368 | yes | yes: 40(6):1604-1614 | partly: Doppler-shift framework; q is geometry, not its result | guessed DOI 10.1063/1.1725603 resolves to an unrelated paper |
| 6 | C. F. Bohren, D. R. Huffman, Absorption and Scattering of Light by Small Particles, Wiley (1983), ISBN 978-0-471-05772-7, 530 pp. | ISBN 978-0-471-05772-7 | yes (OpenLibrary) | yes | yes, read in scanned text: sec. 6.2 eq. (6.13) f(theta) = (3/u^3)(sin u - u cos u), u = 2x sin(theta/2) | the book says "Rayleigh-Gans", not "Rayleigh-Gans-Debye" |
| 7 | S. W. Provencher, "A constrained regularization method for inverting data represented by linear algebraic or integral equations", Comput. Phys. Commun. 27(3), 213-227 (1982). | 10.1016/0010-4655(82)90173-4 | yes | yes | yes: constrained regularised inversion | guessed 10.1016/0010-4655(82)90182-5 is a 404; CONTIN program paper is 27:229-242, 10.1016/0010-4655(82)90174-6 |
| 8 | J. Kestin, M. Sokolov, W. A. Wakeham, "Viscosity of Liquid Water in the Range -8 C to 150 C", J. Phys. Chem. Ref. Data 7(3), 941-948 (1978). | 10.1063/1.555581 | yes | yes | yes: re-analysed standard values with correlation equations | values are ratios plus two correlations anchored at mu(20 C) = 1002.0 uPa s; not a per-degree table |
| 9 | G. M. Hale, M. R. Querry, "Optical Constants of Water in the 200-nm to 200-um Wavelength Region", Appl. Opt. 12(3), 555-563 (1973). | 10.1364/AO.12.000555 | yes | yes | yes for n(lambda) in the visible; tabulated n is 3 decimals at 25 C | n = 1.332 at 0.625 um, 1.331 at 0.65 um, so 633 nm is an interpolation |
| 10 | W. M. Haynes (ed.), CRC Handbook of Chemistry and Physics, 97th ed., CRC Press (2016), ISBN 978-1-4987-5428-6. | ISBN 978-1-4987-5428-6 | yes (OpenLibrary) | yes | not line-verified; the Handbook does carry organic-liquid viscosity tables | pin edition and ISBN when citing; newer editions exist |

## Corrections that change how the report cites things

1. **PDI formula.** Do not hang `PDI = 2 mu2 / Gamma^2` on Koppel. He gives the cumulant
   framework; the factor 2 is the ISO/instrument convention. Attribute the formula to
   ISO 22412 (2025 edition) and describe Koppel as the method.
2. **ISO edition.** ISO 22412:2017 is withdrawn; ISO 22412:2025 is current (published
   2025-09-30, technically revised). Cite 2025, or name the edition explicitly.
3. **Siegert relation.** Berne & Pecora state the ideal `g2 = 1 + |g1|^2`; beta is an
   instrumental factor. Do not present beta as part of the theory.
4. **Scattering vector.** `q = (4 pi n / lambda) sin(theta/2)` is geometry; cite Berne &
   Pecora (or standard texts), not Pecora 1964 as its source.
5. **Water refractive index.** Hale & Querry give three decimals at 25 C. If the report
   needs n(633 nm) to four decimals, either label the value interpolated or cite
   Daimon & Masumura, Appl. Opt. 46, 3811 (2007), DOI 10.1364/AO.46.003811.
6. **Water viscosity.** Kestin et al. is a set of standard values with correlation
   equations, not a printed per-degree table. The simulator's 5-10 K table is an
   interpolation of those values; say so.
7. **Three guessed DOIs were wrong** (Koppel, Pecora, Provencher) and two of the wrong
   ones still resolve, to unrelated papers. A shallow resolution check would have passed
   them. This is exactly the failure mode PS1 punishes.
