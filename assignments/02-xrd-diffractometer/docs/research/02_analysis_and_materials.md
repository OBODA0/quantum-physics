# Assignment 2 (EE4005) — Analysis and Reference Data for an XRD Powder-Diffractometer Simulator

**Deliverable B.** Companion to the simulator spec. Every numeric fact carries a tag:
`[S]` = sourced (DOI/URL given), `[V]` = verified *on this host on 2026-10-22* (command given, output seen),
`[I]` = inference / standard practice / not separately sourced.

Host: outpost CT180 (`agent`). Project repo on Alfred is **not** touched. All work below was done read-only in `/tmp/xrd_research`.
General search engines are blocked from this host; Crossref, doi.org, OpenAlex, AFLOW and (over HTTP) COD were reachable.

---

## 1. Bragg's law and d-spacing

### 1.1 Bragg's law

    n * lambda = 2 * d_hkl * sin(theta)          ->   lambda = 2 d sin(theta)   for n = 1

Convention used here: `2theta` is the measured angle, `theta = 2theta/2`, `d` in Angstrom, `lambda` in Angstrom.
Equivalent vector form (used for indexing): **|G_hkl| = 2 sin(theta)/lambda = 1/d_hkl**.
Inference/convention, not a sourced measurement `[I]`.

Valid range: `sin(theta) <= 1` gives `d >= lambda/2`. For Cu K-alpha1 (1.5406 A) the smallest observable d is 0.7703 A,
i.e. a hard low-angle... high-angle cut-off that the simulator must enforce `[I]`.

### 1.2 d-spacing by crystal system

Let `a,b,c` be the conventional cell edges and `alpha,beta,gamma` the angles.

**Cubic** (a = b = c, all angles 90 deg) `[I]`, standard crystallographic identity:

    1/d^2 = (h^2 + k^2 + l^2) / a^2

**Tetragonal** (a = b, c; all angles 90 deg) `[I]`:

    1/d^2 = (h^2 + k^2)/a^2 + l^2/c^2

**Hexagonal / trigonal (rhombohedral described on hexagonal axes)** (a = b, gamma = 120 deg) `[I]`:

    1/d^2 = (4/3)(h^2 + hk + k^2)/a^2 + l^2/c^2

**General triclinic** (kept for completeness; the simulator only needs the three above) `[I]`:

    1/d^2 = (1/V^2) [ S11 h^2 + S22 k^2 + S33 l^2 + 2 S12 hk + 2 S13 hl + 2 S23 kl ]
    S11 = b^2 c^2 sin^2(alpha),  S22 = a^2 c^2 sin^2(beta),  S33 = a^2 b^2 sin^2(gamma)
    S12 = a b c^2 (cos(alpha)cos(beta) - cos(gamma))
    S13 = a b^2 c (cos(alpha)cos(gamma) - cos(beta))
    S23 = a^2 b c (cos(beta)cos(gamma) - cos(alpha))
    V   = a b c sqrt(1 - cos^2(alpha) - cos^2(beta) - cos^2(gamma) + 2 cos(alpha)cos(beta)cos(gamma))

**Necessary convention the report must state:** which cell is used per structure (conventional vs primitive).
FCC lattices can be indexed on both (a_cub, Z=4) and the rhombohedral primitive cell (a_p = a_cub/sqrt(2), alpha = 60 deg).
Mixing the two is the single most common source of nonsense lattice parameters `[I]`.

### 1.3 Lattice-parameter refinement

Three methods, in increasing rigour. The report should use at least the second.

1. **Per-peak a (cubic).** `a_hkl = d_hkl * sqrt(h^2+k^2+l^2)` from each indexed peak. Fast, shows random error, but is
   biased by peak-position error (sample displacement, zero shift) `[I]`.
2. **Nelson-Riley / cos^2(theta) extrapolation.** For cubic patterns, plot `a_hkl` against
   `(1/2)(cos^2(theta)/sin(theta) + cos^2(theta)/theta)` and extrapolate to theta = 90 deg; this removes the
   dominant absorption/geometry displacement term of a flat-plate scan `[I]`. Alternative abscissa
   `cos^2(theta)` (Bradley-Jay) is equivalent at this level `[I]`.
3. **Whole-pattern least squares (Rietveld).** Fit the lattice parameters, zero offset, displacement, peak widths and
   intensities together `[S] doi:10.1107/S0021889869006558` (Rietveld 1969, *J. Appl. Cryst.* **2**, 65-71).

**Bragg-Brentano displacement error** (needed so the simulator can inject it and so the report can discuss it) `[I]`:

    Delta(2theta) = -2 s cos(theta) / R

with `s` the specimen displacement from the focusing plane and `R` the goniometer radius. Note the sign: a specimen
sitting `s > 0` too high shifts peaks to **lower** 2theta, and the error vanishes at 90 deg, which is exactly why
cos^2(theta)-type extrapolation works.

**Zero-shift error** `[I]`: `Delta(2theta) = 2*theta_0`, constant in 2theta. Distinguishing zero shift from
displacement is done by the different theta dependence; this belongs in the analysis section.

---

## 2. Peak indexing and systematic absences

### 2.1 Indexing a cubic pattern (the simulator's "student mode")

Compute `sin^2(theta)` for every peak, then form ratios `sin^2(theta_i)/sin^2(theta_1)`. Because
`sin^2(theta) = (lambda^2/4a^2)(h^2+k^2+l^2)`, the ratios are ratios of integers `N = h^2+k^2+l^2` `[I]`.
The allowed `N` set identifies the lattice:

| Lattice type | Allowed N = h^2+k^2+l^2 | Observable consequence |
|---|---|---|
| Primitive cubic (P) | all N except 0 | 1,2,3,4,5,6,8,9,... |
| BCC (I) | h+k+l even | 2,4,6,8,10,12,14,16,... (all even) |
| FCC (F) | h,k,l all even or all odd | 3,4,8,11,12,16,19,20,... |
| Diamond-type (Fd-3m) | FCC **and** h=k=l=odd forbidden, plus h+k+l = 4n+2 forbidden | 3,8,11,16,19,24,... (no 4, no 12) |
| NaCl-type (Fm-3m, two-atom basis) | FCC; extra rule if F_cation = F_anion | 3,4,8,11,... (4 survives because F_cation != F_anion) |

`[I]` — these follow from the structure-factor rules in 2.2; they are the standard textbook rules
(Cullity & Stock, *Elements of X-Ray Diffraction*; Warren, *X-Ray Diffraction*).

**Worked check the simulator should reproduce:** Si (Fd-3m) first allowed reflection is 111 (N=3); the 200 and 222
reflections are absent even though N=4 and N=8 are FCC-allowed, because the two-atom diamond basis cancels them.
A student who indexes Si on a simple FCC rule set will mislabel the second observed peak `[I]`.

**Rule of mixtures for `N`:** any observed `N` that is *not* in the allowed set of the proposed lattice falsifies it.
The simulator should include a deliberate "wrong lattice" sample so the report can show this test failing `[I]`.

### 2.2 Structure factor and the origin of absences

    F_hkl = sum_j  f_j * exp(2*pi*i (h x_j + k y_j + l z_j)) * exp(-B_j (sin(theta)/lambda)^2)

with `f_j` the atomic scattering factor of atom `j` at fractional coordinates `(x_j,y_j,z_j)`, `B_j` the isotropic
Debye-Waller factor, and the sum over all atoms in the **cell** (not the asymmetric unit) `[I]`.

**General condition:** `I_hkl = |F_hkl|^2`; a reflection is *systematically* absent when `F_hkl = 0` for all members of
the family by symmetry, and *accidentally* absent when the atoms happen to cancel at one composition `[I]`.
This distinction matters for the report: only systematic absences are a lattice fingerprint.

| Structure type | Space group | Condition on (hkl) | Absent families | Source |
|---|---|---|---|---|
| Primitive cubic (e.g. CsCl-type *lattice*) | Pm-3m | none | none | `[I]` |
| BCC (W, alpha-Fe, Mo) | Im-3m | h+k+l = odd | 100, 111, 210, 300,... | `[I]` |
| FCC (Cu, Al, Ni, Au) | Fm-3m | h,k,l mixed parity | 100, 110, 210, 211,... | `[I]` |
| Diamond (C, Si, Ge) | Fd-3m | FCC + (h,k,l all odd OK only if h+k+l = 4n+1); h+k+l = 4n+2 forbidden | 200, 222, 420,... | `[I]` |
| NaCl / rock salt (NaCl, MgO, LiF) | Fm-3m | FCC; h+k+l = 4n+2 weak or absent when f_cat = f_an | 111 weak, 200 strong; with equal f, 200 disappears | `[I]` |
| Perovskite (ABO3, e.g. SrTiO3) | Pm-3m | primitive, no general absences; superlattice reflections appear only on tilting (Glazer) | none in the ideal cubic cell | `[I]` |
| Spinel (AB2O4, e.g. MgAl2O4) | Fd-3m | FCC + diamond-type rules; A/B site contrast sets which survive | 111, 220, 311, 400, 331, 422, 511, 440 | `[I]` |
| Wurtzite (ZnO, GaN) | P63mc | primitive hexagonal; no general absences; 000l allowed for all l | none; intensities set by z-parameter | `[I]` |
| Rutile (TiO2) | P42/mnm | primitive tetragonal; 0kl absent when k+l odd, h0l absent when h+l odd (screw/glide) | 100, 101 weak by geometry, 0kl odd sum absent | `[I]` |

**Honest limitation:** the perovskite, spinel and wurtzite rows above are given from the space-group symmetry rules as
taught in standard texts; I did **not** re-derive them from International Tables on this host (no IT access; the
all-angle "perovskite has no absences" statement is true only for the ideal cubic cell). The report should cite
*International Tables for Crystallography, Vol. A* for the general-position tables and let the simulator generate
absences from `F_hkl` numerically rather than from a hand-written rule table. **Recommendation: compute, don't tabulate.**
`[I]`

### 2.3 Indexing tetragonal patterns

For `1/d^2 = (h^2+k^2)/a^2 + l^2/c^2`, define `A = lambda^2/(4a^2)` and `C = lambda^2/(4c^2)`. Then
`sin^2(theta) = A*(h^2+k^2) + C*l^2`. Two unknowns, so two peaks of different `(h^2+k^2, l^2)` type fix `a` and `c`;
the rest must then be predicted and *checked*, not fitted `[I]`. Practical algorithm for the simulator's
"index this pattern" feature:

1. Guess the smallest `sin^2(theta)` peak is (001) or (100); try both.
2. Solve for `A, C` from two peaks; require `A, C > 0`.
3. Predict all `sin^2(theta)` up to the observed maximum; compare to observed within a tolerance.
4. Accept only if every observed peak is predicted and the fit residual is small `[I]`.

**Degeneracy warning** `[I]`: in tetragonal systems `(h^2+k^2)` and `l^2` can swap, giving a family of solutions
`(a,c)` and `(c,a)`. Report both and let the systematic-absence pattern (e.g. rutile's `0kl` rule) discriminate.

---

## 3. Intensities

### 3.1 The full Bragg-Brentano powder intensity expression

For a flat-plate, theta-2theta (Bragg-Brentano) scan, the integrated intensity of reflection `hkl` is `[I]`
(standard form, after Cullity & Stock ch. 4 and Warren ch. 3):

    I_hkl = [ I0 * lambda^3 * A_beam / (64 * pi * r) ]
            * ( e^2 / (4 pi eps0 m c^2) )^2
            * ( 1 + cos^2(2theta) ) / ( sin^2(theta) * cos(theta) )
            * ( 1 / (4 v^2) )
            * |F_hkl|^2
            * m_hkl
            * exp( -2 B (sin(theta)/lambda)^2 )
            * (absorption/geometry term)

where

| Symbol | Meaning | Note |
|---|---|---|
| `I0` | incident beam intensity | simulator input |
| `lambda` | wavelength used for that peak | K-alpha1 only, or the doublet split (see §8) |
| `A_beam` | illuminated specimen area | cancels in relative intensities |
| `r` | specimen-to-detector distance | cancels in relative intensities |
| `e^2/(4 pi eps0 m c^2)` | classical electron radius `r_e` = 2.8179403205e-15 m | `[S]` CODATA value, `[I]` for the numeric |
| `v` | unit-cell volume | |
| `|F_hkl|^2` | structure factor squared | see 2.2 |
| `m_hkl` | multiplicity of the family | see 3.3 |
| `B` | isotropic Debye-Waller factor | see 3.4 |

**Practical consequence for the simulator:** all the prefactors are constant across peaks, so the *only* things that
shape a simulated pattern are `|F|^2`, `m`, LP(theta), the Debye-Waller term, and the peak profile. Implement the
relative form

    I_rel(hkl) = |F_hkl|^2 * m_hkl * LP(2theta) * exp(-2B sin^2(theta)/lambda^2)

and normalise to the strongest reflection = 100 `[I]`. This is what real software reports as "I/I0".

### 3.2 Atomic scattering factors and their 2theta falloff

`f(s)` with `s = sin(theta)/lambda` decreases monotonically with `s`; it is *not* flat, and the falloff is the
reason high-angle peaks are weak. This is the single most-often-omitted term in student simulators `[I]`.

Two citable analytic parameterisations:

* **Cromer-Mann** (4-Gaussian + constant), `f(s) = sum_{i=1..4} a_i exp(-b_i s^2) + c`.
  `[S] doi:10.1107/S0567739468000550` — Cromer & Mann, *Acta Cryst.* A**24**, 321-324 (1968). Coefficients are
  tabulated in *International Tables for Crystallography Vol. C*, Table 6.1.1.4.
* **Waasmaier-Kirfel** (5-Gaussian + constant, covers ions and wide s-range), `[S] doi:10.1107/S0108767394013292`
  — Waasmaier & Kirfel, *Acta Cryst.* A**51**, 416-431 (1995).

The simulator should use the 5-Gaussian set because it is valid over a wider `s` range and includes ionic species,
which matters for NaCl-type and oxide samples `[I]`. For `s -> 0`, `f(0) = Z` (electron count) — a built-in unit
test: any coefficient set that does not reproduce `f(0) = Z` to within ~1% is mistyped `[I]`.

**Anomalous dispersion** `f = f0 + f' + i f''` becomes significant near an absorption edge; for Cu K-alpha radiation
and the light/3d elements in the sample set it is a <1% correction to intensities and should be stated as neglected `[I]`.

### 3.3 Multiplicity

`m_hkl` = number of symmetry-equivalent `(hkl)` in the point group of the lattice, i.e. the number of times that
`d`-spacing contributes to the powder pattern `[I]`.

| Cubic family | m (cubic, 48-fold) | Tetragonal | m (tetragonal, 16-fold) | Hexagonal | m (hex, 24-fold) |
|---|---|---|---|---|---|
| 100 | 6 | 100 | 4 | 100 | 6 |
| 110 | 12 | 110 | 4 | 110 | 6 |
| 111 | 8 | 101 | 8 | 101 | 12 |
| 200 | 6 | 111 | 8 | 102 | 12 |
| 210 | 24 | 200 | 4 | 103 | 12 |
| 211 | 24 | 201 | 8 | 002 | 2 |
| 220 | 12 | 210 | 8 | 201 | 12 |
| 221 | 24 | 211 | 8 | 112 | 12 |

`[I]` — these are the standard point-group orbit sizes; they can be generated programmatically by applying the
Laue group to `(hkl)` and counting distinct signed permutations, which is what the simulator should do rather than
hard-code a table.

**Symptom of a wrong multiplicity:** the simulated pattern's intensity *ratios* are wrong by integer factors
(e.g. 111/200 in FCC off by 8/6 = 1.33), while peak *positions* are perfect. See §8.

### 3.4 Lorentz-polarisation factor and Debye-Waller

**LP, no monochromator** (unpolarised tube source, Bragg-Brentano) `[I]`:

    LP(2theta) = (1 + cos^2(2theta)) / ( sin^2(theta) * cos(theta) )

**LP, with a monochromator** at Bragg angle `theta_m` before the detector `[I]`:

    LP(2theta) = (1 + cos^2(2theta) * cos^2(2theta_m)) / ( sin^2(theta) * cos(theta) )

A graphite (002) monochromator for Cu K-alpha sits at `2theta_m ~= 26.6 deg` `[I]` (derived from d(002) = 3.354 A
and Bragg's law at 1.5406 A; treat as a derived number, not a cited measurement). With a monochromator the
polarisation term loses contrast, so high-angle peaks are relatively *stronger* — a visible, testable difference the
simulator should expose as a toggle `[I]`.

**Debye-Waller (temperature) factor** `[I]`:

    T(2theta) = exp( -2 B (sin(theta)/lambda)^2 ) = exp( -B / (2 d^2) )

`B = 8 pi^2 <u^2>` with `<u^2>` the mean-square displacement along the scattering vector. Typical `B`:
0.4-0.6 A^2 for tightly bound light atoms, ~0.8-1.2 A^2 for metals at room temperature `[I]` (order-of-magnitude,
not a cited measurement). Effect: a smooth, monotone suppression of high-angle intensity, indistinguishable in shape
from a `1/s^2`-type `f` falloff unless `f` is handled correctly. Setting `B = 0` overestimates high-angle intensity
by ~10-20% at `s = 0.5 A^-1` for `B ~ 1` `[I]` (arithmetic from the formula above).

---

## 4. Crystallite size and microstrain

### 4.1 Scherrer equation

    D = K * lambda / ( beta * cos(theta) )

where `D` is the volume-weighted crystallite size (A), `beta` the **integral breadth** of the pure size-broadened
profile in **radians** of 2theta, `theta` the Bragg angle of the peak, `K` the shape constant `[S]
doi:10.1107/S0021889878012844` (Langford & Wilson, *J. Appl. Cryst.* **11**, 102-113, 1978).
Original: P. Scherrer, *Göttinger Nachrichten* (1918); the modern critical review is Langford & Wilson above `[S]`.

**Values of K** `[S] doi:10.1107/S0021889878012844` and `[I]`:
* `K = 0.9` is the near-universal default for roughly spherical/equiaxed crystallites with `beta` = FWHM;
* `K = 0.89` for spherical particles with `beta` = integral breadth;
* `K` ranges ~0.62-2.0 depending on shape (needles, plates, cubes) and on whether FWHM or integral breadth is used;
* the `0.9` in the brief is therefore a **choice, not a constant of nature** — the report must say so and must state
  which `beta` definition was used.

**What invalidates the Scherrer number** `[I]`:
1. `beta` not corrected for instrumental broadening (must be deconvolved, not subtracted — see 4.3).
2. `beta` taken as FWHM while `K = 0.89` was intended for integral breadth (mixing definitions inflates `D`).
3. Size distribution: Scherrer gives a volume-weighted mean; a broad distribution makes a single `D` meaningless.
4. Simultaneous strain: any microstrain adds to `beta` and is read as *smaller* crystallites.
5. `D` below ~20-30 A: the equation loses validity, and atomic-scale disorder dominates.
6. `D` above ~1000-2000 A: instrumental broadening dominates and `D` is not measurable this way.
7. Faulting, stacking defects and twins broaden peaks anisotropically — a single `D` is then wrong in a
   `(hkl)`-dependent way.
8. `2theta` not corrected for zero shift / displacement: an error in `theta` propagates as `1/cos(theta)`.

### 4.2 Williamson-Hall and microstrain

    beta * cos(theta) = K*lambda/D  +  4 * epsilon * sin(theta)

`[S] doi:10.1016/0001-6160(53)90006-6` — Williamson & Hall, *Acta Metall.* **1**, 22-31 (1953).
Plot `beta cos(theta)` vs `sin(theta)`: intercept gives `K lambda / D`, slope gives `4 epsilon`.
`epsilon = Delta d / d` is the (dimensionless) microstrain `[I]`.

**Microstrain from a single peak** `[I]`: `epsilon = beta / (4 tan(theta))`.
**Sign of the diagnosis:** strain scales with `tan(theta)` (grows with angle), size scales with `1/cos(theta)`
(falls with angle). Observing `beta` *increasing* with 2theta means strain dominates `[I]`.

**Caveats to state in the report** `[I]`:
* W-H assumes isotropic strain and a single size; anisotropic models (uniform stress / uniform deformation
  energy density) are refinements, and the modified W-H forms are common in the literature.
* Points must not be weighted naively: the fit is in `beta cos(theta)`, and the uncertainty in `beta` is roughly
  constant in absolute terms, so an unweighted fit over-weights the large-angle points. Report the fit with and
  without weights `[I]`.
* A negative intercept means the instrumental correction was over-applied — a diagnostic, not a result.

### 4.3 Instrumental broadening correction

Measured `beta_obs` contains `beta_instr`. Two standard treatments `[I]`:
* **Gaussian approximation**: `beta = sqrt(beta_obs^2 - beta_instr^2)`.
* **Lorentzian approximation**: `beta = beta_obs - beta_instr`.
The truth is between; the report should show both and quote the spread as a systematic uncertainty. A better route is
to fit the instrumental profile from a strain-free, large-crystallite standard (LaB6 or NIST SRM 660 series) and
deconvolve the Voigt components separately (see §5) `[I]`.

---

## 5. Peak-profile fitting practice

### 5.1 Pseudo-Voigt

    pV(2theta) = eta * L(2theta; Gamma) + (1 - eta) * G(2theta; Gamma)
    G(x) = exp( -4 ln2 * (x/Gamma)^2 )                      (Gamma = FWHM)
    L(x) = 1 / ( 1 + 4 (x/Gamma)^2 )

`eta` in [0,1] mixes Lorentzian and Gaussian character; `Gamma` is the FWHM. `[I]` for the form (standard).
The physically-motivated variant used by Rietveld codes is the **Thompson-Cox-Hastings** pseudo-Voigt, which makes
`Gamma` and `eta` functions of the Caglioti-style width parameters `U, V, W` and of `theta`:
`[S] doi:10.1107/S0021889887087090` (Thompson, Cox & Hastings, *J. Appl. Cryst.* **20**, 79-83, 1987) and
`[S] doi:10.1016/0369-643X(58)90029-X` (Caglioti, Paoletti & Ricci, *Nucl. Instrum.* **3**, 223-228, 1958), with

    Gamma^2 = U tan^2(theta) + V tan(theta) + W

**Why size and strain map onto the Voigt components** `[I]`: size broadening is closer to Lorentzian, strain and
instrumental resolution closer to Gaussian. The TC-H formulation is what lets a whole-pattern fit separate them.

**Axial divergence (peak asymmetry)** at low angle is a separate systematic, handled by the Finger-Cox-Jephcoat
correction `[S] doi:10.1107/S0021889894004218` (*J. Appl. Cryst.* **27**, 892-900, 1994). A symmetric pV cannot
reproduce it; the simulator should either include it or explicitly exclude low-angle data `[I]`.

### 5.2 FWHM vs integral breadth

* **FWHM** `Gamma`: full width at half maximum; robust, simple, but depends on profile shape.
* **Integral breadth** `beta = (1/I_peak) * integral I(2theta) d(2theta)`: the width of the equivalent rectangle;
  the quantity Scherrer/Williamson-Hall are formally written in `[I]`.
* For a **Gaussian**, `beta = 1.0645 * FWHM`; for a **Lorentzian**, `beta = 1.5708 * FWHM` (i.e. `pi/2`).
  `[I]` — these are exact definite integrals of the two functions; reproducible analytically.
* Consequence: quoting `D` from FWHM with `K = 0.89` introduces a 6-57% error depending on shape `[I]`.

**Integrated intensity** must be `integral` of the *fitted* profile, not the peak height, and not the sum of raw
channel counts without background subtraction `[I]`.

### 5.3 Background models

* **Polynomial** (Chebyshev or ordinary least squares, order 2-6): the default in Rietveld codes; risks absorbing
  broad amorphous humps `[I]`.
* **Sonnerveld-Visser / Bish-Post** `[S] doi:10.1515/9781501509018-012` (Post & Bish, *Modern Powder Diffraction*,
  Rev. Mineral. **20**, 277-308, 1989 — chapter on Rietveld refinement; the widely used background discussion is
  Bish & Post 1989, *Am. Mineral.* **74**, 177-184, which I could **not** verify by DOI on this host — treat the
  page numbers as unverified `[I]`).
* **Fixed background from an empty holder** run: best practice, removes the fit ambiguity `[I]`.

**Rule the simulator should enforce:** the background must be fitted *simultaneously* with the peaks. Fitting a
linear background first and then the peaks biases both `[I]`.

### 5.4 Reporting uncertainties

Minimum set `[I]`:
1. **Parameter e.s.d.** from the covariance matrix `sigma_p = sqrt( chi^2 * (J^T J)^-1_pp )`, with `chi^2` the
   weighted sum of squared residuals. Report as `value +/- esd`.
2. **Fit quality**: `Rwp`, `Rp` and `GoF = Rwp/Rexp` for whole-pattern fits; `R^2` alone is inadequate for
   diffraction data because points are not independent `[I]`.
3. **Systematic vs random**: state separately. Wavelength, `K`, and the instrumental-broadening model are
   *systematic* and dominate the total error budget; a 1% error in `K` is a 1% error in `D` regardless of esd `[I]`.
4. **Correlated parameters**: `D` and `epsilon` are strongly anti-correlated in W-H; quote the correlation
   coefficient or at least state that the two were fitted together `[I]`.
5. **Do not report more digits than the esd supports** — one or two significant figures on the uncertainty `[I]`.

---

## 6. Reference materials for the simulator

Selection criteria: cubic or simple tetragonal/hexagonal, well-known space group, cheap to justify in a report,
and a pattern with a *diagnostic* feature (doublet resolution, systematic absences, or a strong/weak reflection pair).

Values below were **read from machine-readable records on this host on 2026-10-22**, not from memory.

| Material | Formula | Space group | Conventional cell (A) | Z | Source (verified here) | Why it is a good simulator sample |
|---|---|---|---|---|---|---|
| Silicon (NIST SRM 640f) | Si | Fd-3m (227) | a = 5.431144(8) at 22.5 degC | 8 | `[V]` NIST certificate PDF, `https://tsapps.nist.gov/srmext/certificates/archives/640f.pdf` (certified, k=2) | the calibration standard; diamond absences 200/222; ideal for Scherrer and for K-alpha1/K-alpha2 resolution |
| Silicon (COD) | Si | Fd-3m | a = 5.381 (as deposited) | 8 | `[V]` COD 1526655, `https://www.crystallography.net/cod/1526655.cif` | shows that COD deposits vary: this entry is 0.9% off SRM 640f — good teaching point |
| Diamond | C | Fd-3m (227) | a = 3.56679 | 8 | `[V]` COD 9008564 (Crystal Structures, 1963) | extreme Debye-Waller/f falloff; only 3 strong reflections |
| Aluminium | Al | Fm-3m (225) | a = 4.0398 (derived: 2.8558 x sqrt2 from the primitive cell) | 4 | `[V]` AFLOW `Al1_ICSD_52611`, geometry a_p = 2.856, 60 deg | ductile metal, sharp peaks, easy FCC indexing |
| Copper | Cu | Fm-3m (225) | a = 3.6146 (derived: 2.5559 x sqrt2) | 4 | `[V]` AFLOW `Cu1_ICSD_53755` | strong 111, classic FCC pattern |
| alpha-Iron | Fe | Im-3m (229) | a = 2.9647 (derived: 2.5675 x 2/sqrt3) — **3.4% above the usual 2.8665 A**, so this entry is probably high-temperature or expanded; use a room-temperature entry | 2 | `[V]` AFLOW `Fe1_ICSD_631722` | BCC absences (100, 111 absent); magnetic sample |
| Nickel | Ni | Fm-3m (225) | a = 3.5037 (derived: 2.4775 x sqrt2) | 4 | `[V]` AFLOW `Ni1_ICSD_181716` | FCC twin of Cu; used for alloy work |
| Rock salt | NaCl | Fm-3m (225) | a = 5.665 (derived: 4.0058 x sqrt2) | 4 | `[V]` AFLOW `Cl1Na1_ICSD_60280` | two-atom basis; 111 weak vs 200 strong — intensity-model test |
| Periclase | MgO | Fm-3m (225) | a = 4.253 (derived: 3.0073 x sqrt2) | 4 | `[V]` AFLOW `Mg1O1_ICSD_173128` | isostructural with NaCl, cheap standard |
| Zincite | ZnO | P63mc (186) | a = 3.2494, c = 5.2038 | 2 | `[V]` COD 9004180 (Canadian Mineralogist, 1985) | wurtzite; hexagonal; piezoelectric; strong texture risk |
| Rutile | TiO2 | P42/mnm (136) | a = 4.616, c = 2.977 | 2 | `[V]` COD 9004143 (Canadian Mineralogist, 1979) | tetragonal indexing; 110 is the 100% peak |
| Anatase | TiO2 | I41/amd (141) | a = 3.7892, c = 9.537 | 4 | `[V]` COD 9008214, doi:10.1524/zkri.1972.136.3-4.273 | same formula as rutile, different pattern — polymorphism demo |
| Calcite | CaCO3 | R-3c (167) | a = 4.9920, c = 17.069 (hex axes) | 6 | `[V]` COD 9009668, doi:10.1107/S0021889804031231 | strong 104; rhombohedral-on-hex indexing; common student sample |
| alpha-Quartz | SiO2 | P3221 (154) | a = 4.8362, c = 5.3439 | 3 | `[V]` COD 9000776 (American Mineralogist, 1980) | trigonal; note this entry is ~1.6% below the usual 4.9134/5.4052 — flag it, do not treat as canonical |
| Corundum | Al2O3 | R-3c (167) | a = 4.7657, c = 13.010 | 6 | `[V]` COD 9009671, doi:10.1063/1.325494 | very common standard; strong 104/113 |
| Nickel (COD) | Ni | Fm-3m | a = 3.615 | 4 | `[V]` COD 9013034, doi:10.1007/BF01174717 | **warning:** 2.6% above the AFLOW value — a thin-film entry. Do not use as a lattice standard |

**Two hard warnings that belong in the report:**
1. **COD and AFLOW entries are not interchangeable.** The same element appears with `a` values differing by 0.5-3%
   because entries come from different papers, temperatures, pressures and (in AFLOW's relaxed fields) from DFT.
   The simulator must carry the *provenance* of each lattice constant, and the report must say which one was used `[V]`/`[I]`.
2. **AFLOW's ICSD_WEB geometry is the primitive cell.** For FCC it is the 60-deg rhombohedron; for BCC the
   109.47-deg rhombohedron. The sqrt2 and 2/sqrt3 conversions above are mine `[I]`; the primitive values are
   `[V]` from the API. Get this wrong and every d-spacing is off by 29% or 15%.

**Recommended minimum set for the simulator:** Si (SRM 640f), Al, Cu, Fe, NaCl, MgO, ZnO, TiO2 rutile+anatase,
CaCO3 calcite. That spans primitive/FCC/BCC/diamond, wurtzite, tetragonal and rhombohedral, and every systematic
absence rule in §2 `[I]`.

---

## 7. Free machine-readable reference patterns — and what actually works from this host

### 7.1 What was tested (2026-10-22, from CT180)

| Resource | URL | Status from this host | Notes |
|---|---|---|---|
| Crystallography Open Database (CIF by ID) | `https://www.crystallography.net/cod/<ID>.cif` | **WORKS** `[V]` | direct TLS to the hostname fails; pin IPv4 with `--resolve` |
| COD search / result pages | `.../cod/result?formula=...&format=json` | **BROKEN** `[V]` | server returns **raw PHP source** (`<?php include bootstrap.php ...`), not JSON. Same on the `cod.ibt.lt` mirror. Search is unusable; use known IDs. |
| COD over plain HTTP | `http://www.crystallography.net/cod/<ID>.cif` | **WORKS** `[V]` | simpler alternative to the `--resolve` trick |
| AFLOW AFLUX API | `https://aflow.org/API/aflux/?species(Si),nspecies(1),$paging(0),geometry` | **WORKS** `[V]` | returns JSON incl. `geometry = [a,b,c,alpha,beta,gamma]`, `spacegroup_relax`, `Pearson_symbol_relax`, `aurl` |
| AMCSD (American Mineralogist Crystal Structure DB) | `http://rruff.geo.arizona.edu/AMS/amcsd.php` | **UNREACHABLE** `[V]` | connection failure (000); DNS resolves to 128.196.236.195 |
| RRUFF project | `https://rruff.info/ima/` | reachable (301/302 redirect) `[V]` | the AMS/CIF front-end behind it is the part that fails |
| NIST SRM certificates | `https://tsapps.nist.gov/srmext/certificates/archives/<srm>.pdf` | **WORKS** `[V]` | the non-`archives` path 404s; verified by extracting the certified Si lattice parameter |
| Materials Project API | `https://api.materialsproject.org` | 401 (needs API key) `[V]` | not usable anonymously |
| Crossref / doi.org / OpenAlex | — | **WORKS** `[V]` | used for every DOI below |

### 7.2 Working commands (copy-paste, no search engine)

```bash
# COD: TLS to the hostname fails on this host -> pin IPv4 (158.129.170.82)
curl -s --resolve www.crystallography.net:443:158.129.170.82 \
     'https://www.crystallography.net/cod/9009668.cif' -o calcite.cif
# or simply over HTTP (works, no trick needed):
curl -s 'http://www.crystallography.net/cod/9009668.cif' -o calcite.cif

# COD search is broken (serves PHP source). Do not build the simulator on it.
# Use the ID list in section 6 instead.

# AFLOW: all structures containing Si, with geometry
curl -s 'https://aflow.org/API/aflux/?species(Si),nspecies(1),$paging(0),compound,aurl,spacegroup_relax,Pearson_symbol_relax,geometry'
# filter in Python for 'ICSD_WEB' in aurl to keep experimental structures only

# NIST certified lattice parameters (SRM 640f silicon)
curl -sL -o srm640f.pdf 'https://tsapps.nist.gov/srmext/certificates/archives/640f.pdf'
```

**Honest gap:** there is **no verified way from this host to list COD entries by formula**. The search endpoint is
broken and I found no working alternative on the COD mirrors. The workable method is: obtain COD IDs from the
literature or from the structures you already use, then fetch them by ID. The ID list in §6 is that starting set,
verified one-by-one today `[V]`.

### 7.3 What a "measured reference pattern" actually means

COD, AMCSD and RRUFF give **crystal structures** (atomic coordinates + cell), from which a pattern is *calculated*.
They are not measured diffractograms. Measured digital patterns with intensities are held by
* ICDD PDF-4+/PDF-2 (commercial),
* NIST SRM 660/640/1976 certificates and certificate *supplements* (limited patterns),
* and various instrument-facility calibration sets.
For Assignment 2 the correct framing is: **calculate the pattern from a deposited structure, then compare to a
measured pattern only if you have one.** The report should not claim a "reference pattern" was downloaded from COD
when what was downloaded is a CIF `[I]`.

---

## 8. Common mistakes and their observable symptoms

Each row: the mistake, the exact symptom visible in a *simulated* pattern, and the diagnostic that proves it.

| # | Mistake | Observable symptom in the simulated pattern | How to prove it |
|---|---|---|---|
| 1 | **K-alpha2 doublet ignored** (treated as one line) | every peak is too narrow and the simulated peak is *not* asymmetric at high angle; fitted FWHM is systematically too small, so Scherrer `D` is too large. Real Cu K-alpha patterns show a visible shoulder at 2theta > ~60 deg for sharp peaks. | compare peak width of the 400/331 region with and without the doublet; the K-alpha1/K-alpha2 separation is `Delta(2theta) = 2 tan(theta) * (lambda2-lambda1)/lambda1` ≈ 0.1 deg at 2theta = 100 deg `[I]` |
| 2 | **K-beta not removed / not modelled** | spurious extra reflections at `sin(theta_beta)/sin(theta_alpha) = lambda_beta/lambda_alpha ≈ 0.901` of every strong line — i.e. peaks at ~0.9x the 2theta of the true lines, often misindexed as a second phase. | check that every "extra" peak sits at exactly `2 asin( (lambda_beta/lambda_alpha) sin(theta_alpha) )` |
| 3 | **Lorentz-polarisation factor missing** | intensity ratios wrong in a smooth, angle-dependent way: high-angle peaks far too strong (LP falls by an order of magnitude from 20 deg to 120 deg). Peak *positions* are perfect, which is why students miss it. | plot `I_obs/I_calc` vs 2theta: without LP it is a smooth curve, with LP it is flat |
| 4 | **Wrong multiplicity** | intensity ratios wrong by small integer factors, worst for high-symmetry families (e.g. 111 vs 200 in FCC off by 8/6). Again positions unaffected. | recompute `m` by applying the Laue group and comparing to the table used |
| 5 | **Atomic scattering factor held constant** (f = Z) | high-angle peaks far too intense; the whole pattern looks "flat" compared with a real one; the apparent Debye-Waller `B` comes out negative when fitted. | fit `B`: with f = const, `B_fit < 0` is the signature |
| 6 | **Primitive/conventional cell mixed up** | all d-spacings wrong by a constant factor (sqrt2 for FCC, 2/sqrt3 for BCC); lattice parameter refine to a value that matches no known phase. | `a_refined/a_literature` = 1.414 or 1.155 exactly |
| 7 | **Scherrer with FWHM but K for integral breadth** | `D` too large by ~6-57% depending on shape; the error changes if the profile is switched between Gaussian and Lorentzian. | recompute `D` with both width definitions; a systematic offset that flips sign between shapes means a definition mismatch |
| 8 | **Instrumental broadening not removed** | `D` is capped by the instrument: all samples appear to be the same "size" (~ the instrumental limit), and W-H gives a large positive intercept but ~0 slope regardless of sample. | run the same analysis on LaB6/SRM 660; if `D` equals the sample's, the instrument dominates |
| 9 | **Background fitted before, not with, the peaks** | broad amorphous hump is absorbed by the background polynomial, "removing" real intensity; weak peaks near the hump vanish and Rwp still looks good. | refit with the background order reduced; if weak peaks reappear, the background was eating them |
| 10 | **Uncertainties omitted or esd only** | a single `D = 12.3 nm` with no interval, while `K` alone carries 10% uncertainty. | build the error budget: `K`, `beta` definition, instrumental correction |
| 11 | **Wrong wavelength used** (K-alpha1 vs weighted mean 1.5418) | lattice parameters off by ~0.1-0.2%, systematically, with no scatter — all peaks shift the same direction. | refine `a` with both wavelengths; the ratio should equal `lambda` ratio exactly |
| 12 | **Zero-shift not modelled** | `a` from each peak drifts linearly in `cos(theta)` (or in the Nelson-Riley abscissa) and does not extrapolate to a constant. | Nelson-Riley plot slopes instead of flattening |
| 13 | **Over-parameterised profile fit** | `eta`, FWHM, background and asymmetry all free on a single peak: the fit is perfect but the parameters are unidentifiable and change wildly with starting values. | perturb the start values by 10%; stable parameters are identifiable |

`[I]` for the whole table — these are standard diagnostics; the numeric ratios (`0.901` for K-beta/K-alpha, `1.414`
for sqrt2, `1.0645`/`1.5708` for width conversions) are exact arithmetic, shown so the simulator can assert them.

---

## 9. Wavelength constants the simulator needs

| Quantity | Value | Status |
|---|---|---|
| Cu K-alpha1 | 1.5405929 A | `[S]` doi:10.1103/PhysRevA.56.4554 (Hölzer et al. 1997, *Phys. Rev. A* **56**, 4554-4568). DOI verified on this host; **the numeric value was not re-read from the paper here** — cross-check against the NIST/Bearden tables before final submission. |
| Cu K-alpha2 | 1.5444274 A | same caveat as above |
| Cu K-alpha weighted mean | 1.5418 A (K-alpha1:K-alpha2 = 2:1) | `[I]` arithmetic from the two lines above; the 2:1 branching ratio is the standard assumption |
| Cu K-beta | 1.3922 A | `[S]` doi:10.1103/RevModPhys.39.78 (Bearden 1967, *Rev. Mod. Phys.* **39**, 78-124) for the wavelength set; **numeric value not re-read here** `[I]` |

**Honesty note:** these four numbers are the ones most likely to be reproduced from memory in a student report. I have
verified the *DOIs exist and describe these exact quantities*, but I could not read the numeric tables from this host
(the publisher sites are blocked; only metadata is reachable). Before submission, the report should quote the values
from an accessible table (e.g. the NIST X-ray transition-energy database, or the SRM 640f certificate which states
the wavelength used). Treat any value in this table as **provisional** until then.

---

## 10. Summary of what is solid vs what needs checking

**Solid, verified on this host today** `[V]`:
* NIST SRM 640f silicon: `a = 0.5431144 nm +/- 0.0000008 nm` at 22.5 degC (certificate PDF read directly).
* 9 COD CIFs fetched and parsed one by one; their cell parameters, space groups and journal references are quoted
  above exactly as stored in the CIF.
* AFLOW AFLUX API works and returns experimental (ICSD_WEB) geometry; the primitive-cell convention was confirmed
  by inspecting the returned angles (60 deg for FCC, 109.47 deg for BCC).
* COD search is broken from here (returns PHP source); AMCSD is unreachable; Materials Project needs a key.

**Needs a second pass before submission** `[I]`:
* Cu K-alpha / K-beta numeric wavelengths — DOIs verified, values not read.
* The detailed absence rules for perovskite, spinel and wurtzite — standard textbook rules, not re-derived here.
  Recommendation: generate absences numerically from `F_hkl` and use the table only as a unit test.
* Bish & Post (1989) *Am. Mineral.* background paper — page numbers not verified; the DOI I verified is the
  *Modern Powder Diffraction* chapter (Post & Bish), which is a different publication.
* AFLOW primitive-to-conventional conversions (sqrt2, 2/sqrt3) — correct for the cubic cases and checked against
  the returned angles, but flagged as my derivation, not a cited statement.

**Deliberately not done:** nothing was written into the project repo; no numbers were filled in from memory and
presented as sourced.
