# Reference audit (PS1)

The brief says: *"If your references turn out to be hallucinated or irrelevant, you will
get 0 from the whole assignment."* This file records what was checked, how, and when.

Checked 2026-10-22 from the outpost. Tools: Crossref REST (`api.crossref.org`), OpenLibrary
books API (`openlibrary.org/api/books`), and the DOI resolver. No reference is listed that
was not resolved by one of those services.

## The six references in the report

| # | work | identifier | check performed | verdict | used for |
| --- | --- | --- | --- | --- | --- |
| [1] | Patterson, *The Scherrer formula for X-ray particle size determination*, Phys. Rev. 56, 978-982 (1939) | doi:10.1103/PhysRev.56.978 | Crossref record read: title, journal, volume, pages and author match | exists, relevant | the Scherrer relation and the shape constant |
| [2] | Warren, *X-ray Diffraction* (1969; Dover 1990) | ISBN 0-486-66317-5 | OpenLibrary record read: title, author B. E. Warren, 381 pp. | exists, relevant | scattering by a finite lattice, the interference function |
| [3] | Cullity & Stock, *Elements of X-ray Diffraction*, 3rd ed. (2001) | ISBN 0-201-61091-4 | OpenLibrary record read: title, authors B. D. Cullity and S. R. Stock | exists, relevant | instrumental broadening, practical size measurement |
| [4] | Oppenheim & Willsky, *Signals and Systems*, 2nd ed. (1997) | ISBN 0-13-814757-4 | OpenLibrary record read: title, authors Oppenheim and Willsky | exists, relevant | convolution, convolution theorem, frequency response |
| [5] | Bracewell, *The Fourier Transform and Its Applications*, 3rd ed. (2000) | ISBN 0-07-303938-1 | OpenLibrary record read: title, author R. N. Bracewell, 616 pp. | exists, relevant | transform pairs for a rectangle and a finite chain, scaling |
| [6] | Waasmaier & Kirfel, *New analytical scattering-factor functions*, Acta Cryst. A51, 416-431 (1995) | doi:10.1107/S0108767394013292 | Crossref record read: title, journal, volume, pages | exists, relevant | the form factors the simulator uses |

Each DOI was opened through Crossref and returned a record whose title, container and pages
agree with the citation string printed in the report. Each ISBN returned an OpenLibrary
record with the expected title and authors.

## What is *not* in the reference list, and why

- **NIST SRM 640f certificate** and the **COD CIFs** behind the cell constants in Table 1.
  They are the provenance of shipped data, recorded row by row in `data/SOURCES.md` with
  record ids, and the table caption points there. They are not cited as literature because
  the report makes no claim *about* them; they are the inputs.
- **Wikipedia, lecture slides, blog posts.** None is used. No lecture material for this
  assignment was supplied, so nothing is attributed to a lecture.
- **ICDD PDF cards.** Their intensity tables are commercial and were not accessible from the
  build host; the report compares against published peak positions only, and says so.

## Checks on the claims themselves

- The Scherrer constant K = 0.9 is quoted from [1] and [3]; the report uses the same value in
  the code and in the figure annotation.
- The convolution argument is stated for a rectangle window and a finite chain, both of which
  are standard transform pairs in [5]; the reduction to sinc-squared at a Bragg point is in
  [2].
- The statement that the integrated area is preserved by convolution follows from the unit
  area of the normalised response in [4]; the report also demonstrates it numerically in
  Table 2 rather than only asserting it.
