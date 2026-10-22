# Reference audit - Assignment 1, PL spectroscopy simulator

> **Status note (added after the report was rewritten).** This audit was run against
> the *earlier draft*. Its findings were applied in the rewrite: the two DOIs that do
> not exist were replaced, the mis-cited claims were re-pointed to sources that carry
> them, and the uncited references were either cited where they belong or dropped.
> What the shipped PDF contains now is listed in `TASK.md` section 5.4 and verified in
> `VERIFICATION.md` section 6. Read the rest of this file as the evidence behind those
> changes, not as a description of the current reference list.

Audited: `report/generate_pdf_report.py` (the PDF's source of record) and `data/SOURCES.md`,
`data/reference_spectra.json` in the assignment repo on Alfred
(`/home/oboda/Projects/Nano capsule/quantum physics/pl-spectrometer-simulator/`).
Audit run 2026-10-18 on the Blackwall outpost (CT 180). No repository was modified.

Tools actually used: Crossref REST, doi.org content negotiation, OpenLibrary books API and
search-inside, PubMed eutils, Europe PMC (search + full-text XML), Unpaywall, OpenAlex,
Internet Archive (metadata, scans). Google/Bing/DuckDuckGo/Brave/HathiTrust are blocked from
this host, so ordinary web pages (publisher landing pages, RSC, ACS, ScienceDirect) were not
reachable; that is the main reason several sources could only be read at abstract level.

## 0. Headline findings

1. **Two DOIs in the reference list do not exist** (both return "DOI Not Found"):
   [4] `10.1016/1011-1344(93)80169-M` and [5] `10.1002/9780470691274`. The correct DOIs are
   given below. Under a rule where a hallucinated reference scores 0, these are the two
   must-fix items.
2. **[3] (Mujumdar 1993) is doing work it cannot do**: it is cited for the Cy3 fluorescence
   lifetime (C3), for Beer-Lambert + the I_PL = I_abs*Phi_f relation (C4), for the pi-pi*
   assignment (C5) and for the free-electron particle-in-a-box model of cyanine chain length
   (C10). It is a dye-synthesis paper. C3, C4 and C10 need different references.
3. **[1] (Kasha 1950) is the correct source for Kasha's rule (C1, direct quotes found) but is
   anachronistic for the "100 fs - 1 ps" number in C2**, which it does not state.
4. **C7 is a deduction, not a citation**, and its threshold contradicts the report's own
   simulator code (which applies no cut-off at lambda_exc; the zero comes from the absorption
   tail dying out).
5. **C8's physics is partly wrong** independently of the citation: methylene blue's
   intersystem-crossing (triplet) yield is about half, not 96%, of the excited molecules.
6. **[5] and [6] are never cited in the body of the report** - they appear only in the
   reference list.
7. The report also cites "[3, 4]" for the sample-database quantum yields, but the repo's own
   `SOURCES.md` attributes those numbers to vendor datasheets, PhotochemCAD and OMLC, not to
   [3] or [4]; and the report body says methylene blue Phi_f = 0.04 while the shipped database
   (`reference_spectra.json`, README) uses 0.02 in water.

## 1. Reference-by-reference

### [1] Kasha 1950, Discuss. Faraday Soc. 9, 14-19, DOI 10.1039/DF9500900014 - VERIFIED
Crossref and doi.org both resolve. Title "Characterization of electronic transitions in complex
molecules", Discussions of the Faraday Society vol. 9 (1950), author Michael Kasha, RSC.
Crossref's page field is "14" (first page only); the cited 14-19 is the standard range.
Full text: read as OCR of the Internet Archive scan `dli.ernet.18779` ("Discussions Of The
Faraday Society (1950)", Digital Library of India). OCR digits and ligatures are noisy
(`10^-x` renders as `10~x`); page headers 14/15/16/17/19 are visible in the OCR.
The publisher's own page (pubs.rsc.org) is behind Cloudflare (HTTP 403) from here.
ISBN/doi.org checks: none needed.

### [2] Lakowicz 2006, Principles of Fluorescence Spectroscopy, 3rd ed., DOI 10.1007/978-0-387-46312-4 - VERIFIED (metadata); TEXT NOT READ
Crossref: book, Springer US, 2006, print ISBN 9780387312781 = 978-0-387-31278-1 as cited,
electronic ISBN 9780387463124. doi.org resolves.
**Not readable from here**: the book is closed access, and the only Lakowicz item on
archive.org (`principlesfluore00lako`) has no OCR text ("No hOCR or Abbyy file present"),
so no page, section or table could be inspected. Every statement below that depends on [2] is
therefore "standard textbook content, page not verifiable from here" and is flagged as such.

### [3] Mujumdar et al. 1993, Bioconjugate Chem. 4(2) 105-111, DOI 10.1021/bc00020a001 - VERIFIED (existence + metadata)
Crossref and doi.org resolve; title, all five authors, journal, volume, issue, pages and year
match exactly. Abstract read in full via PubMed (PMID 7873641). Full text: closed access
(Unpaywall `is_oa=false`), ACS blocks scraping - **full text NOT read**.
Abstract content, verbatim highlights: "synthesis and properties of these reagents ... succinimidyl
ester reactive groups ... water soluble, pH insensitive ... One of the reagents, Cy3, can be
excited with the 488-, 514- and 532-nm laser lines and is optimally excited with the 546-nm
mercury arc line. Another, Cy5, can be excited with the 633-nm HeNe and 647-nm Kr laser lines."

### [4] Tuite & Kelly 1993, J. Photochem. Photobiol. B 21(2-3) 103-124 - WRONG DOI
Cited DOI `10.1016/1011-1344(93)80169-M` **does not exist**: Crossref returns 404 and
doi.org returns "DOI Not Found".
**Correct DOI: 10.1016/1011-1344(93)80173-7** (resolves; Crossref: Tuite E.M., Kelly J.M.,
Journal of Photochemistry and Photobiology B: Biology 21(2-3) 103-124, 1993; PubMed PMID 8301408
gives the full title).
Caveat for whoever re-checks it: Crossref's deposited *title* for the correct DOI is
"New trends in photobiology" (the Elsevier series heading); the article title the report gives,
"Photochemical interactions of methylene blue and analogues with DNA and other biological
substrates", is correct and is confirmed by PubMed.
Abstract read in full (PubMed). Full text: closed access - **NOT read**.
Abstract content: "The light-induced reactions of methylene blue and related phenothiazinium
dyes with biological substrates are described. The properties of the excited states of the
dyes, their reactions with nucleic acids and their photosensitised chemical modifications of
nucleic acid bases are examined."

### [5] Albani 2007, Principles and Applications of Fluorescence Spectroscopy - WRONG DOI
Cited DOI `10.1002/9780470691274` **does not exist** (Crossref 404, doi.org "DOI Not Found").
**Correct DOI: 10.1002/9780470692059** (resolves; Crossref: monograph, Wiley, 2007, Albani,
Jihad Rene; ISBNs 9781405138918 print and 9780470692059 electronic). The print ISBN cited in the
report, 978-1-405-13891-8, is correct and is confirmed in OpenLibrary (OL11650205M, 2007).
The book exists; only the DOI is wrong.

### [6] Sauer, Hofkens & Enderlein 2011, Handbook of Fluorescence Spectroscopy and Imaging, ISBN 978-3-527-31669-4 - VERIFIED (no DOI cited, none needed)
OpenLibrary OL26086213M (Wiley-VCH, 2011, Markus Sauer) confirms the ISBN; Crossref has the
book as DOI 10.1002/9783527633500 with the same print ISBN. No DOI is cited in the report,
which is acceptable. Full text not read. **The reference is never cited in the body.**

## 2. Claim-by-claim

