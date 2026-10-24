# Reference audit (PS1)

The brief says: *"If your references turn out to be hallucinated or irrelevant, you will
get 0 from the whole assignment."* This file records what was checked, how, and when.

Checked 2026-10-22 from the outpost. Tools: Crossref REST (`api.crossref.org`), the DOI
handle registry (`doi.org/api/handles/`), OpenLibrary (`openlibrary.org/api/books`), and the
GDZ digitisation for the one source without a DOI. No reference is listed that was not
resolved by one of those services.

## The ten references in the report

| # | work | identifier | check performed | verdict | used for |
| --- | --- | --- | --- | --- | --- |
| [1] | Patterson, *The Scherrer formula for X-ray particle size determination*, Phys. Rev. 56, 978-982 (1939) | doi:10.1103/PhysRev.56.978 | Crossref record: title, journal, volume, pages, author | exists, relevant | the Scherrer relation |
| [2] | Warren, *X-ray Diffraction* (1969; Dover 1990) | ISBN 0-486-66317-5 | OpenLibrary: title, author, 381 pp. | exists, relevant | scattering by a finite lattice; Warren-Averbach |
| [3] | Cullity & Stock, *Elements of X-ray Diffraction*, 3rd ed. (2001) | ISBN 0-201-61091-4 | OpenLibrary: title, authors | exists, relevant | instrumental broadening; K = 0.9 |
| [4] | Oppenheim & Willsky, *Signals and Systems*, 2nd ed. (1997) | ISBN 0-13-814757-4 | OpenLibrary: title, authors | exists, relevant | convolution, convolution theorem |
| [5] | Bracewell, *The Fourier Transform and Its Applications*, 3rd ed. (2000) | ISBN 0-07-303938-1 | OpenLibrary: title, author, 616 pp. | exists, relevant | transform pairs for rectangles and finite chains |
| [6] | Waasmaier & Kirfel, *New analytical scattering-factor functions*, Acta Cryst. A51, 416-431 (1995) | doi:10.1107/S0108767394013292 | Crossref: title, journal, volume, pages | exists, relevant | the form factors |
| [7] | Langford & Wilson, *Scherrer after sixty years*, J. Appl. Cryst. 11, 102-113 (1978) | doi:10.1107/S0021889878012844 | Crossref + handle registry | exists, relevant | K depends on shape, hkl and breadth definition |
| [8] | Stokes & Wilson, *A method of calculating the integral breadths of Debye-Scherrer lines*, Proc. Camb. Phil. Soc. 38, 313-322 (1942) | doi:10.1017/S0305004100021988 | Crossref + handle registry | exists, relevant | integral-breadth convention |
| [9] | Bertaut, *Raies de Debye-Scherrer et repartition des dimensions des domaines de Bragg dans les poudres polycristallines*, Acta Cryst. 3, 14-18 (1950) | doi:10.1107/S0365110X50000045 | Crossref + handle registry | exists, relevant | the breadth gives a mean dimension; the distribution needs higher coefficients |
| [10] | Scherrer, *Bestimmung der Groesse und der inneren Struktur von Kolloidteilchen mittels Roentgenstrahlen*, Nachr. Ges. Wiss. Goettingen, Math.-Phys. Kl. 1918, 98-100 | no DOI; GDZ PPN002505045 | GDZ digitisation located; the page image was read | exists, relevant | the original size relation, and its K = 0.94 for a cube |

## What was rejected, and why

- **Ungar, *Microstructure parameters from line profile analysis*** — no record in Crossref or
  OpenAlex, and no such chapter in *Diffraction Analysis of the Microstructure of Materials*
  (Springer 2004). The Ungar chapter that does resolve is about dislocation/strain
  broadening, which is not the claim here. Rejected rather than cited loosely.
- **Wikipedia, lecture slides, blog posts** — none used. No lecture material was supplied, so
  nothing is attributed to a lecture.
- **ICDD PDF cards** — commercial and not reachable from the build host; the report compares
  against published peak positions only and says so.

## Checks on the claims themselves

- **K.** The report states K = 0.9 as the conventional value [3], notes that Scherrer's own
  1918 paper used 0.94 for a cube [10] (read from the page image by the reference audit),
  that K depends on shape, reflection and breadth definition [7], [8], and that the pure
  finite-chain value computed in this report is 0.8859. Using 0.9 against 0.8859 returns a
  size 1.6 per cent large, which is stated in section 5.3.
- **Convolution and bandwidth.** Standard in [4]; the rectangle and finite-chain transform
  pairs are in [5]; the reduction to sinc-squared at a Bragg point is in [2].
- **Area conservation.** Follows from the unit area of a normalised response in [4] and is
  also measured numerically in Table 3 rather than only asserted.
- **1/cos(theta).** Derived in the report from q = 4 pi sin(theta)/lambda; the same relation
  is the one behind the Scherrer formula in [1] and [3].
