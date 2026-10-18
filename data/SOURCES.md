# PL spectrometer simulator - reference data pack: sources and confidence

Compiled 2026-10-15 on the Blackwall outpost (CT 180, `agent`) for
`/home/oboda/Projects/Nano capsule/quantum physics/pl-spectrometer-simulator`.
Companion file: `reference_spectra.json` (same directory).

Nothing here is invented. Where no citable value existed I report nothing rather than a guess; in the end every field in
`reference_spectra.json` did get a citable source, but several are ranges, and the confidence column below says which
numbers are firm and which are conventions.

Source kinds used below:
- **vendor datasheet** - published specification sheet from the dye vendor (Cytiva/Amersham, Thermo Fisher, Lumiprobe, Interchim). Authoritative for the commercial dye, but vendor quantum yields are often measured on conjugates.
- **spectral database** - curated, published spectral database (PhotochemCAD 3 = Taniguchi & Lindsey 2018; FPbase).
- **measured data set** - tabulated raw measurement published by a lab (OMLC/Prahl).
- **peer-reviewed paper** - journal article; noted whether I could read the full text, the abstract only, or only the indexed PDF text via a search snippet.

Raw downloaded files are kept in **this repository** under `data/raw/`, so every
digitized curve can be re-derived rather than trusted. The full inventory, with what
each file is for, is at the end of this document (`## Inventory of data/raw/`).

---

## 0. How the reported FWHM numbers were obtained

For every material, `absorption_fwhm_nm` and `emission_fwhm_nm` were measured **on the exact digitized curve shipped in
`reference_spectra.json`** at half of that curve's maximum, taking the **outermost** half-maximum crossings (so a vibronic
shoulder sitting above 50 % counts as part of the band) and interpolating linearly between the 1 nm samples.
This is stated in every `notes` field. It is a reproducible rule, not a literature value: the same dye reported by a
different instrument or with the shoulder treated as a separate band gives a different number. Where the shoulder is
clearly separable I give the main-band-only width as well.

Main-band-only (shoulder excluded) widths, for comparison:
- Cy3 absorption, main band only (dip at ~529 nm to red crossing): **~36 nm**; envelope: 45.0 nm.
- Cy3 absorption, methanol PhotochemCAD record: main band ~39 nm; envelope: 53.9 nm.
- Cy5 absorption, main band only (dip near 631 nm to red crossing): **~34 nm**; envelope: 37.7 nm.
- Methylene blue absorption: the 609 nm dimer shoulder is below 50 % of the 664 nm peak, so 55.9 nm is already the
  monomer band plus its shoulder and there is no clean separation.

---

## 1. Cy3

Reported values (see `reference_spectra.json` for the authoritative copy):

| Quantity | Value reported | Source | Confidence |
|---|---|---|---|
| absorption max | **550 nm** | Cytiva/Amersham Cy3 Mono-Reactive Dye Pack PA23001 (vendor datasheet; the PDF copy kept here was corrupt and has been removed - the values are corroborated by the readable Cytiva Cy3 documents, Lumiprobe, Interchim and Thermo) | High for the commercial Cy3 in buffer. Spread across sources: 544.25 (methanol, PhotochemCAD K10), 548 (sulfo-Cy3), 550 (Cytiva), 554 (Thermo guide, FPbase), 555 (Lumiprobe, Interchim non-sulfonated) |
| emission max | **570 nm** | Cytiva Cy3 documentation PA23001 (vendor datasheet; see the note on the removed copy) | High. Spread: 563 (sulfo-Cy3), 566 (Thermo, FPbase), 570 (Cytiva, Lumiprobe, Interchim); methanol PhotochemCAD record gives 557 |
| absorption FWHM | **45.0 nm** | measured on the FPbase Cy3 absorption curve shipped here | Medium (provenance of the FPbase record is not stated). PhotochemCAD methanol record: 53.9 nm envelope / ~39 nm main band |
| emission FWHM | **28.6 nm** | measured on the FPbase Cy3 emission curve shipped here | Medium. PhotochemCAD methanol record: 40.7 nm. Emission FWHM is instrument-bandwidth dependent |
| quantum yield | **0.04 in PBS, pH 7.4** (free dye) | PMC13210223 full text ("Cy3 in PBS buffer: 0.04"); J. Fluoresc. 2023 abstract (Cy3 = 0.04 in non-viscous aqueous solution); original measurement attributed to Stennett et al. 2015 | Medium-high for the *free dye in buffer*; the original 2015 paper itself is paywalled and was not read directly |
| quantum yield, other conditions | 0.07 (methanol, PhotochemCAD K10, measured); >0.15 (Cytiva, labelled protein at D/P = 2); 0.10 (sulfo-Cy3, Lumiprobe) and 0.15 (di-sulfo-Cy3, Interchim; Lumiprobe QY table also gives 0.15); 0.31 (non-sulfonated Cy3 NHS ester: Lumiprobe, Interchim) | vendor datasheets + PhotochemCAD | High as a qualitative statement: Cy3 quantum yield is strongly environment dependent |
| extinction coefficient | **150,000 M-1cm-1** | Cytiva Cy3 documents PA23001 and the readable instruction sheets in this directory, which use 150,000 at 552 nm inside their labelling formula; Lumiprobe; Interchim | High. Variants: 162,000 (sulfo-Cy3: Lumiprobe, Interchim, PMC11721635), 136,000 (FPbase), 133,000 (parent indocarbocyanine in methanol, PhotochemCAD K10, scaled to Sims 1974) |
| Stokes shift | **20 nm** | computed from the two reported maxima | High (trivially derived); 14 nm if computed from the FPbase curve peaks (554/568) |
| pH dependence | pH-insensitive over about pH 4-10 | GoldBio product page (vendor claim only) | Low - vendor marketing claim, not independently verified |

Digitized curves: `digitized_absorption` = FPbase "Cy3" absorption record (450-590 nm, peak 554 nm);
`digitized_emission` = FPbase "Cy3" emission record (514-670 nm, peak 568 nm). Both normalized to their own maximum = 1.0.
FPbase states no manufacturer or reference for these two dye records, so treat the curve *shape* as a good, conventional
Cy3 shape rather than as a traceable measurement. Documented alternative with absolute units, in methanol:
`raw/016-abs.txt` / `raw/016-ems.txt` (PhotochemCAD 2.1a record K10, also republished at omlc.org as record 016).

## 2. Cy5

| Quantity | Value reported | Source | Confidence |
|---|---|---|---|
| absorption max | **649 nm** | Cytiva/Amersham Cy5 Maleimide spec sheet 28954683 (vendor datasheet) | High. Spread: 637.5 (methanol, PhotochemCAD K11), 641-647 (free/sulfonated dye in PBS, Fan et al. 2023), 644 (FPbase), 646 (Lumiprobe, Interchim), 647 (Thermo guide); FPbase's own absorption curve peaks at 652 nm |
| emission max | **670 nm** | Cytiva spec sheet 28954683 | High. Spread: 662 (Lumiprobe, Interchim), 665 (Thermo), 666 (Tocris), 668 (FPbase curve), 670 (Cytiva); methanol PhotochemCAD record gives 657 |
| absorption FWHM | **37.7 nm** | measured on the FPbase Cy5 absorption curve shipped here | Medium. PhotochemCAD methanol record: 39.2 nm |
| emission FWHM | **33.5 nm** | measured on the FPbase Cy5 emission curve shipped here | Medium. PhotochemCAD methanol record: 38.5 nm |
| quantum yield | **0.28** | PMC13560888 (peer-reviewed, open access) states 'Cy5 ... 0.28 in aqueous solution', quoting Klehs et al., ChemPhysChem 2014, 15, 637; Interchim cyanine datasheet gives 0.28 for Cy5 derivatives | Medium. Honest range 0.19-0.30: 0.30 in J. Fluoresc. 2023 (aqueous) and FPbase; 0.27 Lumiprobe QY table; 0.20 Tocris Cyanine 5 SE and Lumiprobe Cy5 NHS ester; 0.19 measured in water (PMC12402892). In methanol PhotochemCAD K11 lists 0.4 for the parent dye, which conflicts with an absolute integrating-sphere value of 0.17 (PMC13386540) |
| extinction coefficient | **250,000 M-1cm-1** | Cytiva spec sheet 28954683 (also used at 650 nm in their D/P formula); Lumiprobe; Interchim; FPbase | High. Variants: 271,000 (sulfo-Cy5: Lumiprobe, Interchim, PMC11721635), 200,000 (parent indodicarbocyanine in methanol, PhotochemCAD K11, scaled to Waggoner 1989) |
| Stokes shift | **21 nm** | computed from the two reported maxima | High (derived) |
| salt / solvent effect | ~1 nm bathochromic shift and slightly higher extinction with added NaCl or DMSO | PMC11721635 (peer-reviewed, open access, read in full) | Medium-high |

Digitized curves: `digitized_absorption` = FPbase "Cy5" absorption record (430-734 nm, peak 652 nm, shoulder near 610 nm);
`digitized_emission` = FPbase "Cy5" emission record (622-734 nm, peak 668 nm). Normalized to each maximum = 1.0.
Provenance not stated by FPbase; note that this record's absorption peak (652 nm) is 8 nm red of its own stated
excitation maximum (644 nm) and of the 646-649 nm vendor consensus. Documented alternative in methanol:
`raw/017-abs.txt` / `raw/017-ems.txt` (PhotochemCAD 2.1a record K11 / OMLC 017).

## 3. Methylene blue

| Quantity | Value reported | Source | Confidence |
|---|---|---|---|
| absorption max | **664 nm** (water) | PhotochemCAD 3 record PSW009 "Methylene Blue [in H2O]", absorption wavelength 664 nm, reference DOI 10.1021/jacsau.5c01463 (spectral database); independently 664 nm in the OMLC measured data set and in the ACS Omega 2020 monomer deconvolution | High for a dilute aqueous sample. Merck Index (quoted on the OMLC page) says 668 nm + 609 nm; in ethanol the maximum is 656 nm (PhotochemCAD I12) |
| emission max | **685 nm** (water) | PhotochemCAD PSW009 emission data file (measured, Cary Eclipse) | Medium-high. 686 nm is the commonly quoted literature value (1 nm sampling difference); 677 nm in ethanol (PhotochemCAD I12) |
| absorption FWHM | **55.9 nm** | measured on the PSW009 water absorption curve shipped here | Medium - includes the ~609 nm dimer shoulder, present in any real aqueous sample |
| emission FWHM | **48.7 nm** | measured on the PSW009 water emission curve shipped here | Medium |
| quantum yield | **0.02 in water** | PMC12692796 (peer-reviewed, open access): "MB (Phi_F = 2 %)" used as the aqueous reference; J. Fluoresc. 2022 (Tchaikovskaya et al.) uses "the quantum yield of MB fluorescence in water 0.02" | Medium. Measured value in ethanol is 0.04 (PhotochemCAD I12, measured, published in Taniguchi & Lindsey 2018). "About 0.04" is also quoted for MB elsewhere in the photosensitiser literature. **Honest range for water: 0.02-0.04** (up to 0.05 in some reports) |
| extinction coefficient | **67,000 M-1cm-1 at 664 nm** | PhotochemCAD PSW009 record (states "absorption epsilon 67,000" for that measured water spectrum) | Medium - matches the shipped curve, but see the spread below |
| extinction coefficient, alternatives | 74,028 M-1cm-1 at 664 nm (OMLC/Prahl measured 10 microM aqueous data set, computed by me from their tabulated data); 107,800 M-1cm-1 at 664 nm (ACS Omega 2020 deconvoluted **monomer** value, PMC7689667) | measured data set / peer-reviewed paper | The 6.7e4-7.4e4 range is what a real dilute cuvette shows (some dimer present); 1.078e5 is the true monomer value |
| Stokes shift | **21 nm** | computed from the two reported maxima | High (derived) |
| aggregation | dimer at 607 nm, tetramer at 600 nm; higher concentration / ionic strength / lower temperature push intensity to the blue | ACS Omega 2020, Table 2 (read in full) | High |
| dimerisation constant in water | not reported (paper exists: Spectrochim. Acta A 2019, DOI 10.1016/j.saa.2019.03.079, but its full text is paywalled and the abstract contains no numbers) | - | Not verified |

Digitized curves: `digitized_absorption` = PhotochemCAD PSW009 water absorption (300-800 nm, 501 points, already
normalized in the source file: 1.0000 at 664 nm); `digitized_emission` = PSW009 water emission (625-850 nm, 226 points,
maximum at 685 nm). Alternatives kept on disk: `raw/ombc_mb.txt` (OMLC water, absolute extinction units, 200-800 nm),
`raw/I12_abs.txt` + `raw/I12_ems.txt` (ethanol, absolute extinction + quantum yield 0.04).

---

## 4. What I could NOT verify (read this before trusting a number)

1. **The 95,000 M-1cm-1 extinction coefficient for methylene blue** that circulates widely in the literature: I could not
   find a citable primary source for it, so it is *not* reported here. The sourced values are 6.7e4 (PhotochemCAD/JACS Au
   water spectrum), 7.4e4 (OMLC measurement) and 1.078e5 (ACS Omega 2020 monomer deconvolution).
2. **Methylene blue quantum yield in water from a primary measurement.** The 0.02 value comes from the way MB is used as
   a reference standard in the photodynamic-therapy literature (one open-access paper states "MB (Phi_F = 2 %)" and a 2022
   J. Fluoresc. paper uses 0.02 for water). I could not read the classic primary source (Olmsted 1979,
   DOI 10.1021/j100483a006), nor the 2022 J. Fluoresc. full text (publisher blocks this host). The only *measured* value
   I could read end-to-end is 0.04 **in ethanol** (PhotochemCAD I12).
3. **Exact provenance of the FPbase Cy3/Cy5 spectra.** FPbase serves these dye records with an empty manufacturer/URL/part
   field and no reference, so the Cy3/Cy5 digitized curves shipped here are a conventional shape, not a traceable trace.
   The two fully documented curves I do have for the same chromophores are in **methanol** (PhotochemCAD K10/K11).
4. **No Cy3/Cy5 spectrum measured in PBS/aqueous buffer could be obtained.** The Thermo Fisher SpectraViewer
   (which would have been the natural source) serves its data through an Akamai-protected API that refused this host
   (HTTP 403 on `_next` chunks and on the JS bundles). BD Biosciences' spectrum viewer, MDPI and Springer PDF endpoints
   were likewise blocked. Everything for Cy3/Cy5 in aqueous buffer therefore comes from vendor *values* and published
   numbers (peaks, epsilon, quantum yield), not from a digitized aqueous curve.
5. **Cy3/Cy5 FWHM.** No vendor publishes band widths. The FWHM values reported are measured from the FPbase (aqueous-like)
   and PhotochemCAD (methanol) curves; they disagree by 5-12 nm depending on which curve is used and on whether the
   vibronic shoulder is counted.
6. **Emission band widths are instrument-limited.** The PhotochemCAD emission data were recorded with a 4.25 nm emission
   bandwidth (documented in the data headers); the FPbase acquisition conditions are unknown. True emission FWHM is
   therefore a few nm narrower than what is reported.
7. **Thermo Fisher / Invitrogen quantitation.** Thermo's current Cy3/Cy5 pages give only peak excitation/emission
   (554/566 and 647/665 nm) with brightness and photostability scores, no epsilon and no quantum yield; the older
   "Cy3 NHS ester / Cy5 NHS ester" product pages that carried lambda/epsilon/correction-factor values were not
   retrievable in their old form, and I found no Thermo page stating a Cy5 quantum yield. Where Thermo is cited here it
   is only for those peak values. (A widely repeated "Thermo Cy5 quantum yield 0.28" could not be traced to a Thermo
   page, so for Cy5 the 0.28 is credited to the peer-reviewed citation above instead.)
8. **Tocris Cyanine 5 SE (quantum yield 0.2).** The page itself blocks this host; the numbers are from the search-result
   snippet, not from the page. It is listed as supporting evidence only, never as the sole source of a reported value.
9. **Cy3/Cy5 pH dependence** rests on vendor marketing text (GoldBio) only; I found no measured pH series.
10. **Methylene blue pH dependence** was not verified at all; the `notes` field deliberately makes no pH claim for MB.
11. **Berlier et al. 2003** (J. Histochem. Cytochem., the classic Alexa-Fluor-vs-Cy comparison) is often cited for Cy3/Cy5
    quantum yields; I did not obtain its full text and therefore did not use it.
12. **Two digitized data sets disagree on quantum yield in methanol.** PhotochemCAD K11 lists 0.4 for the parent
    indodicarbocyanine in methanol; a 2026 absolute integrating-sphere measurement gives 0.17 for unsubstituted Cy5 in
    the same solvent (their extinction coefficients agree, 2.0e5 vs 1.96e5). I report the methanol quantum yield nowhere;
    it is flagged only so that the PhotochemCAD value is not used uncritically.

13. **The class values in the current sample database.** Cy3 550/570/0.04: the peaks survive (they are the vendor values);
    0.04 is correct only for the *free* dye in PBS (conjugates are 0.15-0.31). Cy5 649/670/0.28: the peaks survive;
    0.28 is now backed by both Interchim's datasheet and a peer-reviewed statement that Cy5 is 0.28 in aqueous solution,
    but individual measurements span 0.19-0.30, so treat 0.28 as a central value, not as a measurement of your sample. Methylene blue 664/686/0.04: 664 nm and ~685-686 nm are
    right, but **0.04 is the ethanol value**; for water the literature value is 0.02.



---

## Inventory of `data/raw/`

Every file in this directory, and what it is for. The digitized curves that end up
in `reference_spectra.json` are derived from the tabulated text files here, which is
why they are kept: each curve can be re-derived rather than trusted.

| file | what it is |
| --- | --- |
| `016_abs.txt`, `016_ems.txt` | PhotochemCAD record 016, the Cy3 chromophore (indocarbocyanine) in methanol: absorption and emission, as shipped by OMLC/Prahl. The only absolute emission spectrum obtained for this chromophore. |
| `017_abs.txt`, `017_ems.txt` | PhotochemCAD record 017, the Cy5 chromophore in methanol, same source. |
| `PSW009_abs.txt`, `PSW009_ems.txt` | PhotochemCAD record PSW009, methylene blue in water (the absorption curve that ships in the pack). |
| `I12_abs.txt`, `I12_ems.txt` | PhotochemCAD record I12, methylene blue in ethanol (the solvent of the 0.04 quantum yield). |
| `ombc_mb.txt` | OMLC/Prahl measured methylene blue spectrum in water; the independent check on the 664 nm extinction coefficient (74,028). |
| `fpbase_Cy3.json`, `fpbase_Cy5.json` | The FPbase dye records that the shipped Cy3 and Cy5 curves are digitized from. FPbase does not state the provenance of these records; that is recorded as a limitation. |
| *(removed)* `cy3_monoreactive_28951573.pdf` | The Cytiva Cy3 amine-reactive pack sheet (PA23001) was fetched and read during the verification pass, but the copy that arrived in this repository was corrupt: `pdftotext` returns nothing and `qpdf --check` reports a damaged file with an unrecoverable page tree. It has been deleted rather than kept as unreadable evidence. The values it carries (550 nm, 150,000 M<sup>-1</sup>cm<sup>-1</sup>, 570 nm) are corroborated by the two readable Cytiva Cy3 documents in this directory - which give the 150,000 extinction coefficient at 552 nm - and by the Lumiprobe, Interchim and Thermo pages listed above. |
| `cy5_28954683.pdf` | Cytiva PA25031 spec sheet for Cy5: 649 nm / 250,000 / 670 nm. |
| `cy3_ifu.pdf`, `cy3_maleimide_28954681.pdf` | Further Cytiva Cy3 documents (instructions for use, maleimide derivative), used to check the conjugate quantum yields and the 552 nm extinction value. |
| `rs_cyanine.pdf`, `rs_cyanine.txt` | Review article on cyanine photophysics, used for the sulfo-Cy3/sulfo-Cy5 extinction coefficients and the 0.10-0.31 conjugate quantum-yield spread. |
| `interchim_fpcy.pdf`, `interchim_fpcy.txt` | Interchim (FluoProbes) cyanine data, the second independent vendor source for the same spread. |

---

## Second opinion (2026-10-18)

An independent pass re-checked every number in `reference_spectra.json` against
primary sources, without reusing this file. Verdict: **all six digitized curves
reproduce their sources to rounding** (FPbase records to 3e-8, PhotochemCAD
PSW009 to 5e-6), and the shipped maxima, quantum yields and extinction
coefficients agree:

- **Cy3**: Cytiva PA23001 gives 550 nm / 150,000 / 570 nm (read during that pass; the copy kept in this repository arrived corrupt and was removed); Lumiprobe
  gives 555 nm / 150,000 / 570 nm / QY 0.31 for the NHS ester and 548 / 162,000 /
  563 / 0.10 for sulfo-Cy3. 0.04 is confirmed as the *free dye in buffer* value,
  quoted in the peer-reviewed literature, not a vendor number. Firm.
- **Cy5**: Cytiva PA25031 (28954683) gives 649 nm / 250,000 / 670 nm. Quantum
  yield 0.28 is a cited central value; individual measurements spread 0.18-0.30.
  Report it as a range if the sentence allows.
- **Methylene blue**: PhotochemCAD PSW009 states 664 nm with epsilon 67,000
  (Cary 50, referencing JACS Au); OMLC/Prahl re-parsed gives 74,028 at 664 nm;
  ACS Omega 2020 gives 107,800 for the deconvoluted monomer. The often-quoted
  95,000 traced no further than repetition, which is why it is not shipped.

### Five numbers the report must not repeat from the earlier draft

| drafted | what the sources support |
| --- | --- |
| methylene blue epsilon "~80,000" | no source; use 67,000, 74,028 or 107,800 and say which |
| methylene blue emission "686 nm" | 685.0 nm on the shipped curve; 686 nm appears in published work on the same band |
| Cy3 emission FWHM "~32 nm" | not published anywhere found; measured on the curve: 28.6 nm (outermost crossings) or 30.0 nm (linear interpolation) |
| "Cy3 absorbs ~90 % at 550 nm" | true only at A = 1.0, about 6.7 umol/L; at 1 umol/L Cy3 absorbs 28 % |
| Cy3 Stokes shift "20 nm / 638 cm-1" | arithmetic correct for the 550/570 pair; the digitized peaks (554/568) give 14 nm / 445 cm-1 |

### Still unverified after both passes

- a primary source for the methylene blue extinction coefficient of 95,000
- a primary measurement of the methylene blue quantum yield in water (0.02 is the
  value used in photodynamic-therapy work; the readable measurement is 0.04 in
  ethanol, and the classic source is paywalled)
- any published Cy3 or Cy5 emission bandwidth
- the provenance of the FPbase dye records (their source field is empty)
- whether Cy5 in water is 0.18, 0.20 or 0.28

### Absorbance at the three assigned excitation wavelengths

The digitized curves are defined only inside the measured range (Cy3 absorption
450-590 nm, Cy5 430-734 nm, methylene blue 300-800 nm); outside it the model
reads zero, so Cy3 shows 0.00 % at 450 nm where the independent check puts it
near 0.6 %. That does not change the conclusion at 450 nm, where all three dyes
are transparent, but the report should say "negligible" rather than "exactly zero".
