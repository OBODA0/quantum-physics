# The model, equation by equation

What the simulator computes, in the order it computes it, with the assumption behind every
term. Symbols: `lambda` (A), `theta` (deg, the Bragg angle), `d` (A), `s = sin(theta)/lambda`
(1/A), `F` (the structure factor, in electrons), `m` (multiplicity).

## 1. Positions

Bragg's law, `2 d sin(theta) = lambda`, with `d` from the cell:

| system | 1/d^2 |
| --- | --- |
| cubic | (h^2 + k^2 + l^2) / a^2 |
| tetragonal | (h^2 + k^2) / a^2 + l^2 / c^2 |
| hexagonal | 4/3 (h^2 + hk + k^2) / a^2 + l^2 / c^2 |
| orthorhombic | h^2/a^2 + k^2/b^2 + l^2/c^2 |

A reflection whose `d < lambda/2` is unreachable and is dropped, not clamped.

## 2. Structure factor

    F(hkl) = sum_j occ_j f0_j(s) exp(-B_j s^2) exp(2 pi i (h x_j + k y_j + l z_j))

`f0` is interpolated from `data/scattering_factors.json`, sampled from the
Waasmaier-Kirfel parameterisation; `f0(0)` reproduces the electron count, which the test
suite checks. Every site ships `B = 0.5 A^2`, a stated assumption, not a measurement.
Anomalous dispersion is neglected. It is not negligible: for Cu K-alpha the real part is of
order -2 electrons, roughly 7 % of f0(0) for a 3d element, so intensities near an absorption
edge would be off by that much. Only the intensity column is affected, not the positions.

Absences are not tabulated. They appear because the phases cancel: the diamond 222, the
FCC 100/110/210 and the BCC 100/111 all come out as zero from the sum.

## 3. Relative intensity

    I(hkl) = |F|^2 * m * LP(2theta)

    LP = (1 + cos^2 2theta) / (sin^2 theta cos theta)              no monochromator
    LP = (1 + cos^2 2theta cos^2 2theta_m) / (sin^2 theta cos theta)   monochromator at 2theta_m

The absolute prefactor of a Bragg-Brentano scan - the classical electron radius, the beam
area, the specimen-to-detector distance, the cell volume - is constant across reflections
and cancels when the pattern is normalised to its strongest line. That is why the model is
relative, exactly as assignment 1's PL model is. The flat-plate absorption factor
`A = 1/(2 mu)` is also independent of angle for an infinitely thick specimen, so it
cancels too; it matters only for thin films, which this simulator does not model.

## 4. Multiplicity

The orbit size of `(hkl)` under the Laue class: cubic `(3!/prod n_i!) 2^(nonzero)`,
tetragonal and hexagonal handled by their own rules. It is computed, not read from a table,
and tested against 24 published cases.

## 5. Profile

Each line is a pseudo-Voigt with unit area:

    pV(x) = eta L(x) + (1 - eta) G(x),  eta = 0.5

The instrumental width is Caglioti, `FWHM^2 = U tan^2 theta + V tan theta + W`, with
`U = 0.004, V = -0.002, W = 0.003` (degrees): plausible defaults, not a fitted instrument.
A crystallite size `D` adds `K lambda / (D cos theta)` with `K = 0.9`, combined in
quadrature. Quadrature is exact for two Gaussians and approximate for the Lorentzian part of
the pseudo-Voigt; that approximation is stated rather than hidden.

## 6. The scan

Counts per step are the sum of the profile areas multiplied by the step, plus a flat
background, then a Poisson draw. The dead time, when enabled, compresses the rate as
`n = m / (1 + m tau)` before the draw. The strongest reflection carries
`reference_counts` integrated counts **of the K-alpha1 line**; the K-alpha2 partner adds
another 49.7 % of that area, and every other line scales by its relative intensity.

The K-alpha doublet puts every reflection twice, at its own Bragg angle, weighted 1 and
0.497, so the shoulder grows with 2theta as it does on a real diffractometer.

A displaced specimen shifts every line by `Delta(2theta) = -2 s cos(theta) / R` with the
goniometer radius `R = 240 mm`; the shift is largest at low angle, so a misplaced sample
shifts the whole pattern, most at low angle: a specimen 0.2 mm off the axis moves 111 from 28.441 to 28.348 deg but 422 by only about 0.05 deg.

## 7. What the analysis reads back

`find_peaks` locates local maxima above a height threshold, refines each with a three-point
parabola, and measures the FWHM by interpolating the half-height crossings. `pure_width`
subtracts the instrumental width in quadrature, and `scherrer_from_peak` turns the result
into a size. On a noiseless 30 nm scan the recovered size is 30.0-30.1 nm across six
reflections, and a Williamson-Hall fit of the same peaks returns 30.0 nm with zero strain.

## 8. Fidelity limits

Not modelled: Rietveld refinement, anomalous dispersion, preferred orientation, K-beta
residual, detector energy discrimination, thin-film absorption, axial-divergence asymmetry,
amorphous background, and absolute intensities. The wavelengths are provisional (see
`data/SOURCES.md`).
