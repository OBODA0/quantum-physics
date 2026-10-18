# Source and confidence behind every dye value in this report

Read this next to section 4 of the report. Every value the model uses is listed here with the source
it came from and how firm that source is. Where the sources disagree, the range is stated. Where
nothing citable could be found, that is said rather than filled in with a plausible number.

Four kinds of source appear below:

- **vendor datasheet** - the dye supplier's specification sheet. Authoritative for the commercial
  dye, but a vendor quantum yield is often measured on a labelled conjugate, not on the free dye.
- **spectral database** - a curated, published collection: PhotochemCAD 3 (Taniguchi & Lindsey 2018)
  and FPbase.
- **measured data set** - raw measured spectra published by a laboratory (OMLC / Prahl).
- **peer-reviewed paper** - a journal article, read in full or in part as noted.

Every digitized curve was re-derived from the raw file it came from and reproduces that source to
rounding (the FPbase records to 3e-8, the PhotochemCAD PSW009 record to 5e-6).

## How the bandwidths quoted in the report were measured

Absorption and emission FWHM are measured on the exact digitized curve shipped in
`data/reference_spectra.json`, at half of that curve's maximum, taking the outermost half-maximum
crossings and interpolating linearly between the 1 nm samples. This is a reproducible rule, not a
literature value: a different instrument, or treating the vibronic shoulder as a separate band,
gives a different number. Where the shoulder is clearly separable, the main-band-only width is given
for comparison.

## Cy3 - sulfoindocyanine, the sulphonated form of the indocarbocyanine chromophore

| quantity | value used | source | confidence |
| --- | --- | --- | --- |
| absorption maximum | 550 nm | Cytiva Cy3 instruction sheet | high; 544-555 nm across suppliers |
| emission maximum | 570 nm | Cytiva Cy3 instruction sheet | high; 563-570 nm across suppliers |
| absorption FWHM | 45.0 nm | measured here on the FPbase curve | medium; methanol record 53.9 nm |
| emission FWHM | 28.6 nm | measured here on the FPbase curve | medium; methanol record about 40 nm |
| quantum yield | 0.04, free dye in PBS | peer-reviewed free-dye measurement | medium-high; conjugates 0.10-0.31 |
| extinction coefficient | 150,000 at 552 nm | Cytiva Cy3 sheets; Lumiprobe | high; sulfo form 162,000 |
| Stokes shift | 20 nm | derived from the two maxima above | high; 14 nm between the curve peaks |
| pH dependence | flat over pH 4-10 | supplier product page | low; a supplier claim, not measured here |

The record carries three strips of the same dye: a corrected excitation strip (400-649 nm,
250 points), an emission strip (514-670 nm) and the absorbance strip (450-590 nm) that this report's
band is digitized from. The excitation strip is not spliced onto the band, because the two differ by
2.9 % of full scale on average where they overlap; it is reported instead in section 3.3 of the
generated number table, which gives what each curve holds at the band edges.

Digitized curves: absorption 450-590 nm (curve peak 554 nm), emission 514-670 nm (curve peak
568 nm), each normalized to its own maximum. FPbase states no manufacturer and no reference for
these two records, so the curve shape is a conventional Cy3 shape rather than a traceable
measurement. The fully documented alternative for the same chromophore, in absolute units but in
methanol, is the PhotochemCAD record 016 kept in `data/raw/`.

## Cy5 - pentamethine sulfoindocyanine

| quantity | value used | source | confidence |
| --- | --- | --- | --- |
| absorption maximum | 649 nm | Cytiva 28954683 datasheet | high; 637-652 nm across suppliers |
| emission maximum | 670 nm | Cytiva 28954683 datasheet | high; 662-670 nm across suppliers |
| absorption FWHM | 37.7 nm | measured here on the FPbase curve | medium; methanol record 39.2 nm |
| emission FWHM | 33.4 nm | measured here on the FPbase curve | medium; methanol record 38.5 nm |
| quantum yield | 0.28 in water | peer-reviewed, quoting the aqueous value | medium; individual results 0.19-0.30 |
| extinction coefficient | 250,000 at 650 nm | Cytiva 28954683; Lumiprobe | high; sulfo form 271,000 |
| Stokes shift | 21 nm | derived from the two maxima above | high |
| salt / solvent effect | about 1 nm red shift | peer-reviewed, read in full | medium-high |

Digitized curves: absorption 430-734 nm (curve peak 652 nm), emission 622-734 nm (curve peak
668 nm). FPbase again states no provenance; that record's own absorption peak (652 nm) sits 8 nm red
of its stated excitation maximum (644 nm) and of the 646-649 nm vendor consensus, which is why the
report quotes the vendor maxima and uses the curve for its shape. The documented alternative in
methanol is the PhotochemCAD record 017 in `data/raw/`.

## Methylene blue - phenothiazinium dye, the weakest emitter of the three

| quantity | value used | source | confidence |
| --- | --- | --- | --- |
| absorption maximum | 664 nm | PhotochemCAD PSW009 (water) | high for a dilute aqueous sample |
| emission maximum | 685 nm | PhotochemCAD PSW009 emission file | medium-high; 686 nm is quoted in print |
| absorption FWHM | 55.9 nm | measured here on the PSW009 curve | medium; includes the dimer shoulder |
| emission FWHM | 48.6 nm | measured here on the PSW009 curve | medium |
| quantum yield | 0.02 in water | the aqueous reference value in PDT work | medium; 0.04 measured in ethanol |
| extinction coefficient | 67,000 | PhotochemCAD PSW009 (water) | medium; see the alternatives below |
| extinction coefficient, other | 74,028 / 107,800 | OMLC at 10 umol/L | 6.7-7.4e4 is a real cuvette |
| Stokes shift | 21 nm | derived from the two maxima above | high |
| aggregation | dimer at 607 nm | peer-reviewed, table read in full | high |
| dimerisation constant | not reported | the paper is paywalled, abstract has no values | not verified |

Digitized curves: absorption 300-800 nm and emission 625-850 nm, both from the PSW009 water records,
which ship in absolute units. The independent checks on the 664 nm extinction coefficient are the
OMLC measured data set and the deconvoluted monomer value above.

## What could not be verified

1. **A primary source for the extinction coefficient of 95,000 M-1cm-1** that circulates widely for
   methylene blue. It is not used here. The sourced values are 67,000, 74,028 and 107,800.
2. **A primary measurement of the methylene blue quantum yield in water.** 0.02 is the value used
   when methylene blue serves as an aqueous reference in photodynamic therapy; the readable measured
   value, 0.04, is for ethanol. Honest range for water: 0.02-0.04.
3. **Any published emission bandwidth for Cy3.** None was found. The one published bandwidth found
   for either dye is 37.4 nm for an aptamer-Cy5 conjugate, against 33.4 nm measured here.
4. **The provenance of the FPbase Cy3 and Cy5 records** (their source field is empty). The fully
   documented curves for the same chromophores are the PhotochemCAD methanol records in `data/raw/`.
5. **The dimerisation constant of methylene blue in water.** The paper exists but is paywalled and
   its abstract contains no numbers.

Section 3.1 of the generated number table re-runs the 650 nm result at the top and bottom of every
range listed above, and shows that the ranking between the three dyes does not depend on any of it.

## Raw files kept in the repository

Every digitized curve can be re-derived from these rather than trusted:

| file | what it is |
| --- | --- |
| `016_abs.txt`, `016_ems.txt` | PhotochemCAD record 016: the Cy3 chromophore in methanol, 220-700 nm |
| `017_abs.txt`, `017_ems.txt` | PhotochemCAD record 017: the Cy5 chromophore in methanol, same source |
| `PSW009_abs.txt`, `PSW009_ems.txt` | PhotochemCAD record PSW009: methylene blue in water |
| `I12_abs.txt`, `I12_ems.txt` | PhotochemCAD record I12: methylene blue in ethanol, the 0.04 solvent |
| `ombc_mb.txt` | OMLC / Prahl measured methylene blue spectrum in water, 200-800 nm |
| `fpbase_Cy3.json`, `fpbase_Cy5.json` | the FPbase records the shipped Cy3 and Cy5 curves come from |
| `cy5_28954683.pdf` | Cytiva Cy5 maleimide specification sheet: 649 nm, 250,000, 670 nm |
| `cy3_ifu.pdf`, `cy3_maleimide_28954681.pdf` | further Cytiva Cy3 documents used for the Cy3 values |
| `interchim_fpcy.txt` | Interchim (FluoProbes) cyanine data, a second independent supplier |
| `rs_cyanine.txt` | review of cyanine photophysics, used for the conjugate quantum-yield spread |

The readable vendor documents are the ones cited: the Cytiva Cy3 instruction sheet, the Cy3
maleimide specification sheet 28954681 and the Cy5 maleimide sheet 28954683 all print the values used
here, and they agree with Lumiprobe, Interchim and Thermo. The Cytiva Cy3 amine-reactive pack sheet
(PA23001) states the same three Cy3 values; it was read when the data was collected, but the copy kept
in the repository arrived corrupt and was removed, so it is the readable sheets that the report cites.
