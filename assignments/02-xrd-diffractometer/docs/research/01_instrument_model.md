# Assignment 2 — instrument model for an X-ray powder diffractometer (XRD)

**Deliverable A of the Assignment 2 research pack**
Compiled 2026-10-22 on the Blackwall outpost (CT 180, host `agent`) for
`assignments/02-xrd-diffractometer/`. Nothing here is copied into the repository;
this file is a design/specification document.

Scope: a laboratory Bragg–Brentano (theta/2theta) powder diffractometer, modelled
well enough to implement as a simulator with a handful of user settings, in the
same spirit as `plsim` in Assignment 1.

**How to read the confidence marks.** Every quantitative statement carries one of:

| mark | meaning |
| --- | --- |
| **[S]** sourced | taken from a cited primary/secondary source or a NIST certificate, and the number was read from that source in this session |
| **[D]** derived | arithmetic done here from **[S]** numbers; the working is shown or is one line of algebra |
| **[I]** inference / design choice | our modelling decision, stated as such, not a measured fact |
| **[U]** unsourced | plausible and used by the simulator, but **not** verified against a primary source in this session — the report must not present it as literature |

Unit conventions: wavelength in angstrom (1 Å = 0.1 nm); angles in degrees of 2θ
unless marked rad; μ in cm⁻¹ and μ/ρ in cm² g⁻¹; energies in keV.

---

## 0. Summary of the model

A Bragg–Brentano diffractometer has one geometric idea behind everything: the
sample, the X-ray source focus and the detector slit all sit **on the same
focusing circle**, so that a divergent incident beam converges again at the
receiving slit. The sample is flat. That single constraint produces the
theta/2theta coupling, the flat-plate absorption factor, the low-angle
illumination problem and most of the peak-shape asymmetry that a simulator has to
reproduce.

The simulated observable is

    I(2θ) = B(2θ) + T · Σ_hkl [ w_hkl · P_hkl(2θ) ] * R_inst(2θ)      (counts)

where `B` is background (bremsstrahlung + fluorescence + air scatter), `T` the
dwell time in seconds, `w_hkl` the integrated intensity of one reflection
(structure factor, multiplicity, Lorentz–polarisation, absorption, preferred
orientation), `P_hkl` its normalised profile (pseudo-Voigt, with Kα1/Kα2 as
separate components), `R_inst` the instrumental resolution function, and `*`
convolution. Poisson noise is applied last, per point.

Sections 1–5 give the physics behind each factor; §6 lists the user settings,
§7 the package layout, §8 the numbers a grader can check.

---

## 1. Geometry

### 1.1 The optical chain

| element | what it does | what the simulator needs from it |
| --- | --- | --- |
| X-ray tube, **line focus** | electron beam on a water-cooled anode; the focal spot is a line, typically 0.04 mm × 12 mm, and the long axis is parallel to the goniometer axis | a source of finite width in the diffraction plane; the *projected* width is set by the take-off angle (see §2.4) |
| **divergence slit** (slit 1) | defines the angular spread α of the incident beam, typically 0.25°–2° | α, and hence the illuminated length on the sample (§1.4) |
| **Soller slits** (both arms) | stack of thin parallel foils that limits *axial* divergence (the component along the goniometer axis), typically 2.5°–5° total | axial divergence → low-angle peak asymmetry and a small 2θ shift; can be modelled as an extra asymmetry term |
| **sample**, flat plate | the powder, held so that its surface contains the goniometer axis | μ, thickness, particle size, preferred orientation, displacement |
| **receiving slit** (slit 2) | defines the angular acceptance of the detector arm, typically 0.1–0.3 mm at radius R | angular acceptance w/R, and the "resolution vs intensity" trade |
| **monochromator** (optional, after the sample) | a curved graphite (002) crystal, 2d = 6.708 Å, selects the Kα band and rejects Kβ, Compton and sample fluorescence | a flag: on/off, with its own reflectivity curve and a small extra broadening |
| **detector** | point (scintillation + PMT, or proportional counter) or position-sensitive | §5 |

The order matters: monochromator *after* the sample is the usual laboratory
arrangement ("diffracted-beam monochromator") because it also removes the
sample's own fluorescence, which a monochromator before the sample cannot do.
**[I]** for the specific instrument; **[S]** that a diffracted-beam monochromator
is the standard way to remove Kβ and fluorescence is in Jenkins & Snyder [1].

### 1.2 theta/2theta coupling, and which angle is which

- The **Bragg angle θ** is the glancing angle between the incident beam and the
  *sample surface* (equivalently, between the diffracted beam and the surface,
  by symmetry). The lattice planes are parallel to the surface in the
  Bragg–Brentano parafocusing condition.
- The **scattering angle 2θ** is the angle between the incident beam direction
  and the diffracted beam direction. This is the angle the detector arm sweeps,
  measured from the straight-through direction.
- In a **theta/2theta scan** the sample rotates at ω = θ while the detector arm
  rotates at 2θ, i.e. the arm turns at exactly twice the sample's angular rate.
  When the sample is at θ and the detector at 2θ, the detector sits on the
  extension of the beam reflected from the surface planes.

**What the instrument actually measures.** The goniometer encodes the *arm*
angle, and a DAC/encoder reports 2θ. The sample angle is never measured
independently in a coupled scan; it is assumed to be 2θ/2. Every sample-position
error therefore appears as a 2θ error, not as an ω error. This is why sample
displacement and zero offset are the two dominant systematic errors in
Bragg–Brentano data, and why the simulator must expose them as separate knobs
(§1.6).

Two practical consequences for the model:

- When a scan is described as "from 20° to 80°", those are **2θ** values. "Peak at
  28.44°" means 2θ = 28.44°, i.e. θ = 14.22°.
- A `theta/2theta` scan is not the same as an `omega` scan (rocking curve) or a
  `2theta` scan at fixed ω; only the first is modelled here.

### 1.3 The parafocusing condition and why the geometry is "focused"

Source focus S, sample surface point and receiving slit D lie on a circle of
radius R/2 (the focusing circle) when the sample is at the Bragg condition. S and
D are fixed at distance R from the goniometer axis O; the sample surface passes
through O. Because all rays leaving S at angles within α converge to D, the
diffractometer collects a large solid angle while keeping the detector slit
narrow. The price is that the condition holds exactly only for one θ at a time,
and that a **flat** sample deviates from the ideal focusing circle, giving the
characteristic low-angle asymmetry. **[S]** [1, ch. 3], [2, ch. 4].

### 1.4 Illuminated length on a flat sample (derivation)

This is the single most under-modelled effect in student simulators, so it is
derived here rather than quoted.

Put the goniometer axis at the origin, the sample surface along y = 0, and the
tube focus (the image of the divergence slit) at S = (−R cos θ, R sin θ), i.e. at
distance R from the axis, on the incident side, at height R sin θ. The divergence
slit admits rays at glancing angles φ = θ ± α/2. A ray leaving S in direction
(cos φ, −sin φ) meets the surface y = 0 at

    x(φ) = R [ −cos θ + sin θ · cot φ ]

At φ = θ this gives x = 0 (the centre of the illuminated track). Expanding for
small α/2 gives x(θ ± α/2) = ∓ R α / (2 sin θ), so the illuminated length is

    L(θ) = R α / sin θ            [rad for α; R and L the same unit]      (1)

This is the standard result and it explains the classic statement that the beam
"walks" off the sample at low angle. **[D]** from the geometry above; the same
expression appears in [1, §3.5] and [2, §4.4].

Numbers for R = 240 mm, sample length 20 mm:

| α (deg) | L at 2θ=10° | 2θ=20° | 2θ=40° | 2θ=80° | 2θ=140° | 2θ where L = 20 mm |
| --- | --- | --- | --- | --- | --- | --- |
| 0.5 | 20 (capped) | 12.1 | 6.1 | 3.3 | 2.2 | **12.0°** |
| 1.0 | 20 (capped) | 20 (capped) | 12.2 | 6.5 | 4.5 | **24.2°** |
| 2.0 | 20 (capped) | 20 (capped) | 20 (capped) | 13.0 | 8.9 | **49.5°** |

(mm; **[D]** from eq. 1.) Below the onset angle the beam spills off the specimen
and the measured intensity drops relative to the model, unless the simulator
applies the spillover correction:

    f_spill(θ) = min(1, L_sample / L(θ)) = min(1, L_sample · sin θ / (R α))   (2)

This is a real instrument effect, not a bug: it is why routine scans rarely start
below 2θ = 5°, and why "why does my intensity fall at low angle" is a standard
exam question. **[I]** for using eq. 2 as the correction; it follows directly from
eq. 1 assuming uniform beam intensity across the slit.

### 1.5 Receiving slit and axial (Soller) divergence

The receiving slit of width w at radius R accepts a range of directions
Δ(2θ) = w/R (rad). For w = 0.1 mm, R = 240 mm: Δ2θ = 4.2 × 10⁻⁴ rad = **0.024°**.
This is the geometric floor of the point-detector angular resolution; the
observed FWHM is larger because of the source width, the divergence slit and the
sample. **[D]**

Soller slits limit the axial divergence to a half-angle β (typically 2.5° full
width **[U]**, a common catalogue value we did not verify). Axial divergence
produces (i) a small shift of the centroid toward lower 2θ at low angle and
(ii) an asymmetric tail; it is the standard explanation for why low-angle peaks
are asymmetric even when the sample is perfect. In the simulator, either
(a) add a fixed empirical asymmetry parameter, or (b) implement the exact
axial-divergence integral of Cheary & Coelho's fundamental-parameters approach
[3]. For a teaching simulator, (a) with a documented parameter is the honest
choice; (b) is what NIST does [4].

### 1.6 Sample displacement and zero offset

Two rigid-body errors dominate real peak positions:

    Δ(2θ)_disp = − 2 h cos θ / R        (h = sample surface height above the
                                         goniometer axis; positive = too high)   (3)
    Δ(2θ)_zero = 2θ₀                    (a constant encoder offset)

**[S]** eq. 3 is the standard specimen-displacement relation [1, §3.6], [2, §4.5].
For h = 0.1 mm, R = 240 mm: at 2θ = 30° the shift is −0.046°; at 2θ = 120° it is
−0.024°. The signature is a shift that shrinks with angle — which is exactly how
one distinguishes it from a lattice-parameter error (which grows like tan θ).
**[D]** from eq. 3.

**Design decision [I]:** expose `sample_displacement_mm` and `zero_offset_deg` as
optional settings, default 0, because they are the two knobs that let the report
demonstrate the difference between "the peak moved" and "the cell changed".

---

## 2. Source: the X-ray tube

### 2.1 The line spectrum

A Cu anode produces, above the K absorption edge of Cu (8.979 keV), the K
series:

| line | wavelength (Å) | energy (keV) | relative intensity | status |
| --- | --- | --- | --- | --- |
| Kα1 | 1.5405929 | 8.0478 | 2 | **[S]** wavelength: NIST SRM 640f certificate uses exactly λ = 0.15405929 nm [5]; primary evaluation: Hölzer et al. [6] |
| Kα2 | 1.5444274 | 8.0278 | 1 | **[S]** Hölzer et al. [6]; not listed on the certificate |
| Kβ1,3 | 1.39225 | 8.9053 | ~0.13 (see note) | **[S]** wavelength via Deslattes et al. [7] evaluation; **intensity ratio [U]** |
| Kα weighted mean | 1.541871 | 8.0410 | — | **[D]** (2λ₁ + λ₂)/3 |
| bremsstrahlung | continuum, λ ≥ λ_min | — | — | §2.3 |

**Important convention note.** The brief for this assignment gives Cu Kα1 =
1.540598 Å and Kα2 = 1.544426 Å. The modern evaluated value is 1.5405929 Å (the value NIST uses
to compute the SRM 640f peak positions [5]). The difference is
Δλ/λ = 3.3 × 10⁻⁶, which moves a peak by Δ(2θ) = 2 tan θ · Δλ/λ, i.e. **4.5 ×
10⁻⁴ ° at 2θ = 100°** **[D]** — far below any effect the simulator models. Use one
set consistently and say which; we recommend 1.5405929 / 1.5444274 [6] so that
the SRM 640f check in §8.1 reproduces the certificate to 5 × 10⁻⁴ °.

**Kβ/Kα ratio [U].** The commonly used figure is Kβ ≈ 0.13 of Kα for Cu. We could
not verify it against a primary intensity table in this session (Hölzer et al.
tabulate energies and widths, not intensities; Scofield-type ratios were not
reachable). Treat `kbeta_ratio` as a tunable parameter defaulting to 0.13, and
label it in the report as a typical value, not a measured one.

### 2.2 The doublet, the Kβ filter, and why the line spectrum is not a nuisance

Kα1 and Kα2 are separate transitions (2p₃/₂ → 1s and 2p₁/₂ → 1s) with a fixed
2:1 statistical weight. A simulator that models them as two lines of equal width
and 2:1 area automatically reproduces:

- the Kα2 shoulder that appears above roughly 2θ = 50° (§8.4);
- the apparent peak asymmetry at high angle;
- the bias in a single-peak fit that ignores Kα2 (which is what the Rachinger
  correction is for).

This is preferable to using the weighted mean wavelength 1.5418 Å, which is only
valid at low angle where the doublet is unresolved.

**Kβ filter, with numbers.** A Ni foil placed after the divergence slit (the
standard Cu-radiation filter) removes Kβ by differential absorption, because the
Ni K edge (8.333 keV) lies between Kα (8.048 keV) and Kβ (8.905 keV). Using the
NIST XCOM values μ/ρ(Ni) = 48.7 cm²/g at Kα and 279.1 cm²/g at Kβ [9], and
ρ(Ni) = 8.908 g/cm³:

| Ni thickness | T(Kα) | T(Kβ) | Kβ/Kα after filter (before = 0.13) |
| --- | --- | --- | --- |
| 15 µm | 0.52 | 0.024 | 0.0060 |
| 20 µm | 0.42 | 0.0069 | 0.0021 |
| 50 µm | 0.11 | 0.000004 | 0.0000045 |

**[D]** from exp(−μρ·ρ·t). The filter halves the Kα, so it costs roughly a factor
2 in count rate — which is why an instrument with a diffracted-beam monochromator
usually has none, and vice versa.

### 2.3 Bremsstrahlung and the Duane–Hunt limit

The continuous spectrum has a sharp short-wavelength limit set by the tube
voltage:

    λ_min = hc / (e V) = 12.3984 / V(kV)   Å      → 0.310 Å at 40 kV      (4)

**[S]** Duane–Hunt limit; the constant hc = 12.39842 keV·Å is exact to the digits
shown.

Kramers' law gives the spectral shape of the continuum (per unit wavelength,
thin target, thick-target correction aside):

    I(λ) ∝ (λ / λ_min − 1) / λ²       for λ ≥ λ_min,  zero below      (5)

**[S]** Kramers 1923 [8]. The absolute scaling is not predicted by eq. 5; the
simulator uses it shape-only and normalises to the Kα intensity through a
user-settable `brems_fraction` **[I]**.

Physics that matters for the model:

- The continuum is **not** removed by a Kβ filter; it is the main reason a
  point-detector scan has a sloping background, largest at low 2θ (where
  Compton- and air-scattered short-λ photons are most efficiently detected).
- With a diffracted-beam monochromator the continuum is largely rejected,
  because only λ near the Kα band satisfies the graphite (002) Bragg condition.
  The simulator should therefore reduce `brems_fraction` by a large factor when
  `monochromator=True` **[I]**.

### 2.4 Tube voltage and current

- **kV sets which lines exist and how they sit on the continuum.** The Cu K edge
  is 8.979 keV **[D]** (λ_K = 1.3806 Å from hc/E). Below ~9 kV there is no Cu K
  radiation at all. The Kα/Kβ/continuum ratio changes with kV because the
  continuum grows roughly as (V − V_K)² while the line intensity grows as
  (V/V_K − 1)^1.6 (empirical); the optimum for a Cu tube is usually 40–50 kV,
  i.e. 4–5 × V_K. **[U]** for the 1.6 exponent — it is a widely used empirical
  form (Green & Cosslett), not verified here.
- **mA sets intensity linearly**, until the anode's power limit is reached
  (typically ~2.2 kW for a long fine-focus Cu tube **[U]**). For the simulator,
  counts scale exactly with mA × dwell time.
- **Take-off angle** (3°–6° typical) determines the *apparent* source size seen
  by the divergence slit: apparent width = focal width × sin(take-off). A 0.04 mm
  × 12 mm focus seen at 6° presents ~0.04 mm × 1.3 mm. This is why the tube is
  run at a low take-off angle: it sharpens the source in the diffraction plane at
  the cost of intensity. **[S]** for the geometry, **[U]** for the typical values.

**Simulator consequence [I]:** do not model kV/mA as free physical parameters if
the goal is a clean teaching tool. Model them as (a) a Kα intensity scale
`tube_current_mA`, and (b) a validity switch that raises an error if
`tube_voltage_kV < 9.0` for a Cu anode. That keeps the physics honest without
pretending to a tube-yield model we cannot source.

---

## 3. The sample

### 3.1 Absorption and the infinite-thickness assumption

For a flat, thick specimen in symmetric reflection, the path length of the
incident beam to depth z is z/sin θ and the diffracted beam travels the same
distance out again. The intensity from depth z is therefore attenuated by
exp(−2 μ z / sin θ), and

    I_total = I₀ ∫₀^∞ exp(−2 μ z / sin θ) dz = I₀ · sin θ / (2 μ)          (6)

**[S]** [1, §5.2], [2, §4.3]. Two consequences that the simulator must encode:

1. The collected intensity is proportional to **1/(2μ)**, independent of θ. This
   is the "infinite thickness" result, and it is why the absorption correction in
   a powder pattern is a constant, not a curve.
2. The **effective penetration depth** is sin θ/(2μ); with the 99 % criterion
   (1 − e^{−2μt/sinθ} = 0.99) the required thickness is

       t₉₉ = 2.303 · sin θ / μ                                            (7)

   **[D]** from eq. 6.

Mass attenuation coefficients were taken from the NIST XCOM tables [9] (elemental
tables fetched and log–log interpolated to 8.0478 keV in this session; additivity
over the formula unit, which is the standard mixture rule [9]). **[S]** for μ/ρ of
the elements; **[D]** for the compounds.

| material | μ/ρ (cm²/g) | ρ (g/cm³) | μ (cm⁻¹) | 1/μ (mm) | t₉₉ at 2θ=20° (mm) | t₉₉ at 2θ=60° (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| Fe₂O₃ (hematite) | 213.9 | 5.24 | 1121 | 0.009 | 0.004 | 0.010 |
| TiO₂ (rutile) | 123.9 | 4.23 | 524 | 0.019 | 0.008 | 0.022 |
| LaB₆ | 237.6 | 4.72 | 1121 | 0.009 | 0.004 | 0.010 |
| Si | 63.6 | 2.33 | 148 | 0.068 | 0.027 | 0.078 |
| SiO₂ (quartz) | 35.8 | 2.65 | 94.9 | 0.105 | 0.042 | 0.121 |
| Al₂O₃ (corundum) | 31.6 | 3.99 | 125.9 | 0.079 | 0.032 | 0.091 |
| CaCO₃ (calcite) | 74.0 | 2.71 | 200.6 | 0.050 | 0.020 | 0.057 |
| cellulose C₆H₁₀O₅ | 7.66 | 1.50 | 11.5 | 0.87 | 0.35 | 1.00 |
| PLA C₃H₄O₂ | 7.34 | 1.24 | 9.11 | 1.10 | 0.44 | 1.27 |

Densities are handbook values **[U]** for the density column only; μ/ρ is **[S]**.
The headline for the report: **inorganic powders are "infinitely thick" at a few
tens of micrometres, organic ones need a millimetre.** A 1 mm polymer pellet is
therefore not infinitely thick at high angle; a 20 µm coat on a silicon wafer is,
for Cu radiation, but only just.

**Thin-film / substrate case [I]:** if the modelled layer is thinner than t₉₉, the
simulator must (a) multiply by the finite-thickness factor
[1 − exp(−2μt/sinθ)] and (b) add the substrate's peaks and its amorphous
scattering. Assignment-2 samples ("nano capsules") are plausibly thin coatings,
so this flag is worth having.

### 3.2 Illumination vs 2θ

Already covered in §1.4: L ∝ 1/sin θ with the spillover cap. Two further points:

- With a **fixed** divergence slit, the *volume* illuminated is constant with θ:
  the footprint length grows as 1/sinθ while the beam width at the sample shrinks
  as sinθ, and the penetration depth grows as sinθ. The product is constant **[D]**
  from eq. 1 and eq. 6. This is the usual justification for the 1/(2μ) constant
  in the intensity formula.
- With an **automatic** divergence slit (constant illuminated length), intensity
  instead falls as sinθ. The simulator should state which mode it implements;
  this is a common source of a spurious "background slope" in student models.

### 3.3 Preferred orientation (texture)

Plate-like or needle-like crystallites pack with a preferred orientation, which
scales reflection intensities by a factor that depends on the angle between the
scattering vector and the pressing direction. The March–Dollase model is the
standard one-parameter form:

    P_hkl = (r² cos²α + sin²α / r)^(−3/2)      (8)

with r the March parameter (r = 1 isotropic, r < 1 for platy crystallites aligned
with their plates normal to the pressing direction) and α the angle between the
scattering vector and the texture axis. **[S]** Dollase 1986 [10], after March 1932.

**Simulator design [I]:** one scalar `preferred_orientation_r` per phase plus a
texture-axis direction (usually the sample normal), default 1.0. Anything more
(SHARP, E-WIMV) is out of scope.

### 3.4 Particle statistics

Every reflection samples only the crystallites that happen to be in the Bragg
condition. With N crystallites contributing, the relative standard deviation of
the integrated intensity is approximately

    σ(I)/I ≈ 1/√N_eff ,   N_eff ≈ (illuminated volume × packing fraction) / v_cryst   (9)

**[D]** — this is the counting-statistics argument applied to crystallites rather
than photons; it is the standard "particle statistics" or "granularity" effect
[2, §5.6].

Worked illustration **[D]**: a 10 mm × 0.1 mm footprint with 20 µm effective depth
= 2 × 10⁻² mm³; at 50 % packing with 1 µm cubes (10⁻⁹ mm³ each) that is 10⁷
crystallites, and σ/I ≈ 0.03 %. At 10 µm cubes it is 10⁴ crystallites and
σ/I ≈ 1 %. The practical rule — grind below ~10 µm, or accept percent-level
spikes — falls out of the model rather than being asserted.

### 3.5 Amorphous background and fluorescence

- **Amorphous / nanocrystalline fraction**: a broad hump (FWHM several degrees)
  under the pattern, plus a slowly varying background. Model it as one or two
  broad Gaussians with user-settable position/width/area per sample **[I]**.
  For a "nano capsule" sample this is not optional: the capsule shell is usually
  amorphous, and its halo is part of what the measurement shows.
- **Fluorescence**: with Cu radiation (8.05 keV), any element whose K edge lies
  below 8.05 keV is excited efficiently and emits K radiation that the detector
  cannot resolve from the diffracted beam. That means Z ≈ 24–27 (Cr, Mn, Fe, Co);
  Ni (K edge 8.333 keV) is excited only weakly, by the continuum. Fe in a Cu-Kα experiment is
  the textbook case: Fe Kα at 6.40 keV floods a point detector with a
  featureless background **[S]** for the mechanism [1, §5.7]; the fix is a
  diffracted-beam monochromator or an energy-discriminating detector.
  **Simulator:** a `fluorescence_background` term that switches on when the
  sample contains an element with absorption edge below the source energy, and
  is suppressed when `monochromator=True`.

---

## 4. Peak shape and width

### 4.1 Where the width comes from

Four independent contributions:

1. **Instrument**: source size, divergence slit, receiving slit, Soller slits,
   monochromator, sample transparency, axial divergence.
2. **Crystallite size** (finite coherent domain): broadening ∝ 1/cos θ.
3. **Microstrain** (non-uniform lattice spacing): broadening ∝ tan θ.
4. **Wavelength spread**: the Kα doublet itself, plus the intrinsic line width of
   the emission line (~2 eV, i.e. Δλ/λ ~ 2.5 × 10⁻⁴ → 0.02° at 2θ = 60°) **[D]**.

### 4.2 Profile functions

Normalised to unit area, with x = 2θ − 2θ₀ and w = FWHM:

    Gaussian:    G(x) = (2/w)√(ln2/π) · exp(−4 ln2 (x/w)²)                (10)
    Lorentzian:  L(x) = (2/(πw)) · 1 / (1 + 4(x/w)²)                     (11)
    pseudo-Voigt: PV(x) = η L(x) + (1−η) G(x),  0 ≤ η ≤ 1                 (12)

**[S]** standard forms [1, §4.3], [11]. The pseudo-Voigt is a *functional
approximation* to the true Voigt convolution, not a convolution itself; it is
accurate to about 1 % in FWHM when η is fitted. **[S]** [11].

Rules of thumb worth stating in the report: a Lorentzian has long tails and fits
size-broadened or instrument-dominated peaks; a Gaussian fits strain-broadened
peaks better; real peaks are in between and η typically rises with 2θ. **[I]** for
the last sentence as a generalisation.

### 4.3 Caglioti resolution function

The classical parametrisation of the instrumental FWHM in a constant-wavelength
powder diffractometer is

    FWHM_inst²(θ) = U tan²θ + V tanθ + W          (degrees² if U,V,W in deg²)   (13)

**[S]** Caglioti, Paoletti & Ricci 1958 [12]. U, V and W are fitted **per
instrument and per configuration** (slit widths, monochromator). They are not
universal constants, and a simulator that hard-codes "textbook" values is
inventing data.

For reference, here is one internally consistent illustrative set and the curve
it produces **[I]** — chosen so that FWHM ≈ 0.08° at 2θ = 30° and ≈ 0.15° at
2θ = 140°, which is the right order for a modern laboratory instrument:

U = 0.0025 deg², V = −0.0010 deg², W = 0.0064 deg²

| 2θ (°) | 20 | 30 | 50 | 80 | 100 | 120 | 140 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FWHM (°) | 0.079 | 0.079 | 0.080 | 0.086 | 0.094 | 0.110 | 0.150 |

The **correct way** to get U, V, W for the simulator is to fit eq. 13 to a
measured SRM 640f or SRM 660a pattern. Since we do not have one, the defaults
must be labelled "illustrative" in the code and the report. This is exactly the
kind of assumption Assignment 1's standard requires us to declare.

Note also that eq. 13 gives a *symmetric* width. It says nothing about
asymmetry; adding asymmetry needs either a split pseudo-Voigt or the axial
divergence model.

### 4.4 Sample broadening

**Size (Scherrer).**

    β_size(2θ) = K λ / (D cos θ)      [radians of 2θ; D = coherent domain size]  (14)

with K ≈ 0.9 for spherical crystallites of narrow size distribution, and the
exact value depending on shape and on whether β is FWHM or integral breadth
**[S]** Scherrer 1918; Langford & Wilson 1978 [13] show K spans roughly 0.83–1.15
for common shapes/definitions.

Numbers **[D]**, λ = 1.5405929 Å, K = 0.9:

| D (nm) | β at 2θ = 28.4° (°) | β at 2θ = 100° (°) |
| --- | --- | --- |
| 1 | 8.20 | 12.36 |
| 5 | 1.64 | 2.47 |
| 10 | 0.82 | 1.24 |
| 20 | 0.41 | 0.62 |
| 50 | 0.16 | 0.25 |
| 100 | 0.082 | 0.124 |

So a 100 nm powder is already at the instrument limit: the measured width is
dominated by the instrument, and a naive Scherrer analysis of such data returns
a meaningless size. That is a result the report should state, because it is the
most common student error.

**Strain.** Non-uniform strain ε gives β_strain = 4 ε tan θ (radians) **[S]**
[13]. The θ dependence distinguishes it from size: a Williamson–Hall plot of
β cos θ vs 4 sin θ has slope ε and intercept Kλ/D. **[S]** [13].

### 4.5 Combining instrumental and sample broadening

Exact: convolution. Practical rules, exact only in the limits:

    both Gaussian:     β_obs² = β_inst² + β_sample²                        (15)
    both Lorentzian:   β_obs  = β_inst  + β_sample                         (16)
    mixed:             use a Voigt; FWHM_Voigt ≈ 0.5346 w_L + √(0.2166 w_L² + w_G²)  (17)

**[S]** eq. 17 is Olivero & Longbothum's empirical fit, accurate to ~0.02 % [14].
**[I]** for the recommendation to use eq. 15 for a Gaussian-instrument model.

Consequence to state explicitly: **eqs. 15 and 16 differ.** A 0.08° instrument
convolved with a 0.08° sample gives 0.113° (Gaussian) or 0.16° (Lorentzian).
A simulator that mixes them silently will disagree with a reference by ~40 %.
The code must declare one convention and use it everywhere.

### 4.6 The doublet, quantitatively

Differentiating Bragg's law at fixed d:

    Δ(2θ) = 2 tan θ · (Δλ / λ)        [radians]                            (18)

**[D]**. With λ = 1.5405929 Å and Δλ = 0.0038345 Å (Δλ/λ = 2.489 × 10⁻³):

    Δ(2θ) [°] = 0.2853 · tan θ

| 2θ (°) | 20 | 30 | 40 | 60 | 80 | 100 | 120 | 140 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| splitting (°) | 0.050 | 0.076 | 0.104 | 0.165 | 0.239 | 0.340 | 0.494 | 0.784 |
| FWHM_inst from §4.3 | 0.079 | 0.079 | 0.080 | 0.082 | 0.086 | 0.094 | 0.110 | 0.150 |
| splitting / FWHM | 0.63 | 0.96 | 1.30 | 2.02 | 2.80 | 3.63 | 4.48 | 5.22 |

So with a 0.08° instrument the Kα2 component becomes visually separable at about
2θ ≈ 40° (ratio 1.3) and clearly resolved (two maxima) above about 2θ ≈ 55–60°
(ratio > 2). This is the quantitative version of the familiar statement "the
doublet only shows up at high angle", and it is a ready-made sanity check (§8.4).

---

## 5. Detector and counting

### 5.1 Point detector vs position-sensitive detector

| | point detector + receiving slit | position-sensitive (PSD) |
| --- | --- | --- |
| what it records | counts in one angular window per step; the arm must move | counts in all channels simultaneously; the arm may be static (or move while reading out) |
| angular channel | set by w/R (e.g. 0.024° for 0.1 mm at 240 mm) | set by strip pitch (e.g. 0.004°–0.01° per channel) |
| resolution | divergence-limited; the slit trades intensity for resolution | fixed by the optics, not the readout |
| counting rate | one channel at a time | many channels in parallel → much faster scans |
| defects to model | dead time, dark counts | channel-to-channel gain, flat-field correction, parallax |

**[S]** for the architecture [1, ch. 6]; **[U]** for the example numbers, which are
typical catalogue values.

### 5.2 Dead time

For a non-paralyzable detector with dead time τ, the observed rate m is related
to the true rate n by

    m = n / (1 + n τ)      ⇔      n = m / (1 − m τ)                        (19)

**[S]** standard counting-statistics result, Knoll [15, ch. 4]. With τ = 1 µs and
a measured 10⁵ counts/s, the true rate is 1.11 × 10⁵ (10 % higher); at a measured
5 × 10⁵ the true rate is 1 × 10⁶ (50 % higher). **[D]**

**[I]:** implement dead time as an optional parameter, default 0, and note in the
report that a laboratory point detector saturates somewhere around 10⁶ counts/s.
The effect matters only when the simulator is asked to model a strong peak with a
long dwell — exactly the case where a naive model predicts an impossibly sharp
maximum.

### 5.3 Counting statistics

Photon counting is Poisson: a measurement of N counts has σ = √N, so the relative
error is 1/√N and the signal-to-noise ratio of a peak against a flat background
of B counts is

    SNR ≈ (N_peak − B) / √(N_peak + B)                                     (20)

**[S]** Poisson statistics. For 1 % statistics on the peak, N ≈ 10⁴ counts; for
0.1 %, 10⁶. **[D]**

The simulator should apply noise as `np.random.poisson(expected_counts)` per step
*after* computing the model, never as Gaussian noise on a smooth curve — the
difference is visible on a log-scale plot and is the point of the exercise.

### 5.4 Step size, dwell time, scan time

The Nyquist-ish rule for a peak of FWHM w is at least 5 points across the FWHM,
i.e. step ≤ w/5; 0.01°–0.02° is standard for a 0.08°–0.1° instrument. **[I]** rule
of thumb, consistent with [1, §6.4].

Scan time: (2θ_max − 2θ_min)/step × dwell. For 5°–150° at 0.02°/step and 1 s per
step: 7250 points, **2.0 h** **[D]**. A PSD covering 4° at 0.01°/channel does the
same scan roughly an order of magnitude faster for the same counts per channel
**[D]**.

**Design decision [I]:** expose `step_deg` and `counts_per_step` (or
`dwell_s` + `tube_current_mA`), not `scan_speed_deg_per_min`. The latter hides
where the noise comes from.

---

## 6. User settings the simulator should expose

Assignment 1 exposed `lambda_exc`, `lambda_min`, `lambda_max`, `dlambda` and a
sample. The XRD analogue, kept to seven:

| # | setting | units | default | analogue in `plsim` | why it must be exposed |
| --- | --- | --- | --- | --- | --- |
| 1 | `sample` | name → phase record | required | `sample` | the whole point: phase, a, μ, D, texture |
| 2 | `two_theta_min`, `two_theta_max` | ° | 5, 120 | `lambda_min/max` | sets the observable window |
| 3 | `step_deg` | ° | 0.02 | `dlambda` | sampling; controls peak shape fidelity |
| 4 | `counts_per_step` (or `dwell_s`) | counts | 2000 | — | noise level; the only handle on SNR |
| 5 | `divergence_slit_deg` | ° | 1.0 | (fixed optics) | changes L(θ), spillover, resolution |
| 6 | `crystallite_size_nm`, `microstrain` | nm, — | 100, 0 | (fixed sample model) | the Scherrer/Williamson–Hall demonstrations |
| 7 | `monochromator`, `kbeta_filter` | bool | True, False | harmonic filter | changes background and Kβ content |

Optional extras that cost almost nothing and buy real checks: `tube_voltage_kV`
(validity switch only), `sample_displacement_mm`, `zero_offset_deg`,
`preferred_orientation_r`, `dead_time_us`, `seed`.

**One CLI shape** (mirroring `python -m plsim --sample cy5 ...`):

    uv run python -m xrdsim --sample srm640f --range 20 140 --step 0.02 \
        --counts 5000 --divergence 1.0 --noise --seed 7

and a comparison mode:

    uv run python -m xrdsim --sample srm640f --range 20 140 --check-certificate

which prints the computed positions next to the certificate table (§8.1).

---

## 7. Python package layout (mirroring `plsim/`)

`plsim` has: `__init__ __main__ analysis bands cli detector plot reference samples sources spectrometer`.
The XRD analogue, same granularity (10 modules, ~1000 lines):

```
xrdsim/
  __init__.py        public API: Diffractometer, Phase, Scan; __version__
  __main__.py        python -m xrdsim
  sources.py         XrayTube: K alpha1/alpha2/Kbeta lines, Kramers continuum,
                     Duane-Hunt cutoff, kV validity, take-off projection
  optics.py          DivergenceSlit, SollerSlits, ReceivingSlit, Monochromator;
                     illuminated length (eq. 1), acceptance w/R, spillover (eq. 2)
  geometry.py        theta/2theta kinematics, R, parafocusing check,
                     sample displacement and zero offset (eq. 3)
  phases.py          Phase database: lattice + reflection list (or atoms),
                     structure factors, multiplicities, density, mu/rho table,
                     preferred orientation (eq. 8); the analogue of samples.py
  profiles.py        gaussian/lorentzian/pseudo-Voigt (eqs. 10-12), Caglioti
                     (eq. 13), Scherrer and strain (eq. 14), FWHM combination
                     (eqs. 15-17), convolution helpers
  detector.py        PointDetector / PSD, dead time (eq. 19), Poisson sampling (eq. 20)
  diffractometer.py  Diffractometer.acquire(settings) -> Scan; assembles the
                     intensity sum, applies background, noise; the analogue of
                     spectrometer.py
  analysis.py        peak finding, pseudo-Voigt fitting, Kalpha2 stripping,
                     Scherrer, Williamson-Hall, lattice refinement (Nelson-Riley)
  reference.py       SRM 640f / SRM 660a certified values and peak tables
  plot.py            pattern plot, log-scale plot, peak-fit overlay, W-H plot
  cli.py             argparse front end
```

Dependency direction is one-way: `cli → diffractometer → {sources, optics,
geometry, phases, profiles, detector}`, and `analysis`/`plot` depend only on the
`Scan` dataclass. `reference.py` is imported only by tests and by `--check-certificate`,
never by the physics modules — that keeps the validation data from quietly
becoming part of the model.

Same testing discipline as Assignment 1: one test per check in §8, plus a test
that `Scan` is deterministic under a fixed seed.

---

## 8. Sanity checks a grader will accept

All numbers below were computed in this session from the stated inputs.

### 8.1 Peak positions from Bragg, against the NIST certificate

SRM 640f silicon: a = 0.5431144 nm ± 0.0000008 nm at 22.5 °C **[S]** [5].
Computed with λ = 1.5405929 Å, d = a/√(h²+k²+l²), 2θ = 2 arcsin(λ/2d):

| hkl | computed 2θ (°) | certificate 2θ (°) | difference (°) |
| --- | --- | --- | --- |
| 111 | 28.4412 | 28.441 | +0.0002 |
| 220 | 47.3007 | 47.301 | −0.0003 |
| 311 | 56.1199 | 56.120 | −0.0001 |
| 400 | 69.1268 | 69.127 | −0.0002 |
| 331 | 76.3726 | 76.373 | −0.0004 |
| 422 | 88.0257 | 88.026 | −0.0003 |
| 511 | 94.9475 | 94.947 | +0.0005 |
| 440 | 106.7023 | 106.702 | +0.0003 |
| 531 | 114.0851 | 114.085 | +0.0001 |
| 620 | 127.5352 | 127.535 | +0.0002 |
| 533 | 136.8816 | 136.882 | −0.0004 |

Maximum deviation 5 × 10⁻⁴ °, i.e. at the rounding of the certificate's own
table. **This is the single strongest check in the report**: it simultaneously
validates the Bragg implementation, the lattice constant and the wavelength
convention. A simulator that fails it by 0.01° has a units bug, not a physics
bug.

Second standard, SRM 660a LaB₆, a = 0.41569162 nm ± 0.00000097 nm at 22.5 °C
**[S]** [16] — computed positions **[D]**:

| hkl | 100 | 110 | 111 | 200 | 210 | 211 | 220 | 300 | 310 | 311 | 222 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2θ(Kα1) | 21.358 | 30.385 | 37.442 | 43.506 | 48.957 | 53.989 | 63.218 | 67.547 | 71.745 | 75.844 | 79.870 |

(LaB₆ is primitive cubic, Pm-3m, so **no** reflections are systematically absent
— the B₆ octahedra only modulate intensities. The positions above are geometry
only and do not depend on that. **[S]** for the space group; **[D]** for the
positions.)

### 8.2 Scherrer size

Feed a 10 nm Si-like powder through the model and fit the 111 peak. Expected
β = 0.82° at 2θ = 28.44° (§4.4), to which the instrument adds in quadrature
(Gaussian convention): √(0.82² + 0.079²) = 0.824° **[D]**. A fit should return
D = 10 ± 1 nm. Recovering the input size to 10 % is the acceptance criterion;
recovering it to 1 % is not, because K and the profile convention are not that
well defined.

### 8.3 Instrument-limited regime

Same model with D = 100 nm: β_sample = 0.082°, β_obs = √(0.082² + 0.079²) =
0.114° **[D]**. A Scherrer fit that ignores the instrument returns
D = 100 × (0.082/0.114) = 72 nm, i.e. 28 % too small — a demonstration that the
size is not recoverable without an instrument standard, and that the error is
always toward "smaller". The report should show this rather than hide it.

### 8.4 Doublet splitting at high 2θ

Model Kα1 and Kα2 as two pseudo-Voigts, 2:1 area, separated by eq. 18. Predicted
outcome (§4.6): one peak below 2θ ≈ 40°, a shoulder at 40–55°, two resolved
maxima above ~60°. Quantitative check: the fitted separation at 2θ = 120° should
be 0.494° ± 0.005° **[D]**, and the fitted area ratio 2.0 ± 0.1.

A negative control is worth including: fit the same peak with a single
pseudo-Voigt and show that (a) the residual has a systematic W shape and (b) the
returned FWHM is 10–20 % too large.

### 8.5 Absorption / thickness

For a 5 µm Fe₂O₃ layer: t/t₉₉ at 2θ = 20° is 5/3.6 = 1.4, so the layer is
effectively thick; at 2θ = 60°, t/t₉₉ = 0.49, so the intensity is
1 − e^{−2.303·0.49} = 68 % of the bulk value **[D]**. A model that ignores finite
thickness will therefore over-predict the high-angle intensity by ~1.5 ×. This is
a check a grader can run on the numbers in §3.1 alone.

### 8.6 Counting statistics

With 2000 counts per step, the point-to-point scatter on a flat background must
be √2000 = 45 counts (2.2 %) **[D]**, and the histogram of (I − model)/√model must
be standard normal. Chi-square per degree of freedom ≈ 1.0 ± 0.05 for 10⁴ points.

---

## 9. References

Primary sources are cited with DOI where one exists; books with ISBN. All DOIs
below were resolved through the Crossref REST API in this session and the
volume/page/year match the record returned.

1. R. Jenkins and R. L. Snyder, *Introduction to X-ray Powder Diffractometry*,
   Wiley, 1996. DOI: 10.1002/9781118520994. ISBN 978-0-471-51339-1.
2. B. D. Cullity and S. R. Stock, *Elements of X-ray Diffraction*, 3rd ed.,
   Prentice Hall, 2001. ISBN 0-201-61091-4. *(ISBN as printed; not re-verified
   against a catalogue record in this session.)*
3. R. W. Cheary and A. Coelho, "A fundamental parameters approach to X-ray
   line-profile fitting", *J. Appl. Cryst.* **25** (1992) 109–121.
   DOI: 10.1107/S0021889891010804.
4. J. P. Cline, M. H. Mendenhall, D. Black, D. Windover, A. Henins, "The optics,
   alignment and calibration of laboratory X-ray powder diffraction equipment
   with the use of NIST standard reference materials", *J. Res. NIST* **120**
   (2015) 173–222. (Cited as ref. [3] of the SRM 640f certificate; DOI not
   verified here.)
5. NIST Standard Reference Material 640f, *Line Position and Line Shape Standard
   for Powder Diffraction (Silicon Powder)*, certificate issue date 26 Feb 2019.
   https://tsapps.nist.gov/srmext/certificates/archives/640f.pdf — certified
   a = 0.5431144 nm ± 0.0000008 nm at 22.5 °C; Table 1 peak positions computed
   with λ(Cu Kα1) = 0.15405929 nm.
6. G. Hölzer, M. Fritsch, M. Deutsch, J. Härtwig, "Kα1,2 and Kβ1,3 X-ray emission
   lines of the 3d transition metals", *Phys. Rev. A* **56** (1997) 4554–4568.
   DOI: 10.1103/PhysRevA.56.4554.
7. R. D. Deslattes, E. G. Kessler, P. Indelicato, L. de Billy, E. Lindroth,
   J. Anton, "X-ray transition energies: new approach to a comprehensive
   evaluation", *Rev. Mod. Phys.* **75** (2003) 35–99.
   DOI: 10.1103/RevModPhys.75.35.
8. H. A. Kramers, "On the theory of X-ray absorption and of the continuous X-ray
   spectrum", *Phil. Mag.* **46** (1923) 836–871.
   DOI: 10.1080/14786442308565244.
9. J. H. Hubbell and S. M. Seltzer, *Tables of X-ray Mass Attenuation
   Coefficients and Mass Energy-Absorption Coefficients*, NISTIR 5632 (1995).
   DOI: 10.6028/NIST.IR.5632. Online tables used here:
   https://physics.nist.gov/PhysRefData/XrayMassCoef/
10. W. A. Dollase, "Correction of intensities for preferred orientation in powder
    diffractometry: application of the March model", *J. Appl. Cryst.* **19**
    (1986) 267–272. DOI: 10.1107/S0021889886089458.
11. R. A. Young and D. B. Wiles, "Profile shape functions in Rietveld
    refinements", *J. Appl. Cryst.* **15** (1982) 430–438.
    DOI: 10.1107/S002188988201231X. *(Pseudo-Voigt as a profile function.)*
12. G. Caglioti, A. Paoletti, F. P. Ricci, "Choice of collimators for a crystal
    spectrometer for neutron diffraction", *Nucl. Instrum.* **3** (1958) 223–228.
    DOI: 10.1016/0369-643X(58)90029-X.
13. J. I. Langford and A. J. C. Wilson, "Scherrer after sixty years: a survey and
    some new results in the determination of crystallite size", *J. Appl. Cryst.*
    **11** (1978) 102–113. DOI: 10.1107/S0021889878012844.
14. J. J. Olivero and R. L. Longbothum, "Empirical fits to the Voigt line width:
    a brief review", *J. Quant. Spectrosc. Radiat. Transfer* **17** (1977)
    233–236. DOI: 10.1016/0022-4073(77)90161-3.
15. G. F. Knoll, *Radiation Detection and Measurement*, 4th ed., Wiley, 2010.
    ISBN 978-0-470-13148-0.
16. NIST Standard Reference Material 660a, *Lanthanum Hexaboride Powder — Line
    Position and Line Shape Standard for Powder Diffraction*, certificate.
    https://tsapps.nist.gov/srmext/certificates/archives/660a.pdf — certified
    a = 0.41569162 nm ± 0.00000097 nm at 22.5 °C.
17. H. M. Rietveld, "A profile refinement method for nuclear and magnetic
    structures", *J. Appl. Cryst.* **2** (1969) 65–71.
    DOI: 10.1107/S0021889869006558. *(Cited for the analysis module, not used in
    the forward model.)*
18. H. P. Klug and L. E. Alexander, *X-ray Diffraction Procedures for
    Polycrystalline and Amorphous Materials*, 2nd ed., Wiley, 1974.
    ISBN 0-471-49369-4. *(Standard reference for flat-plate absorption, particle
    statistics and the intensity formula; ISBN as printed, not re-verified.)*
19. B. E. Warren, *X-ray Diffraction*, Addison-Wesley 1969 / Dover 1990.
    ISBN 0-486-66317-5. *(Structure factors, Lorentz–polarisation, line profiles;
    ISBN as printed, not re-verified.)*

---

## Appendix A — constants used

| constant | value | note |
| --- | --- | --- |
| hc | 12.39842 keV·Å | exact to the digits shown **[D]** |
| Cu Kα1 | 1.5405929 Å / 8.0478 keV | [5], [6] |
| Cu Kα2 | 1.5444274 Å / 8.0278 keV | [6] |
| Cu Kβ | 1.39225 Å / 8.9053 keV | [7]; intensity ratio **[U]** |
| Cu K edge | 8.979 keV / 1.3808 Å | **[D]** from the edge energy |
| graphite (002) 2d | 6.708 Å | **[U]** (standard monochromator value) |
| Si SRM 640f a | 5.431144 Å | [5] |
| LaB₆ SRM 660a a | 4.1569162 Å | [16] |

## Appendix B — what is *not* verified

Stated plainly, because Assignment 1's marking rule punishes invented references
and numbers:

1. **Kβ/Kα intensity ratio (0.13)** — typical textbook value; no primary table
   read. Use as a parameter, label as typical.
2. **U, V, W = 0.0025, −0.0010, 0.0064 deg²** — constructed here so the FWHM
   curve is plausible. Not fitted to any instrument. Must be labelled
   "illustrative" in code and report.
3. **Dead time τ, Soller acceptance 2.5°, receiving slit 0.1 mm, take-off 6°,
   focal spot 0.04 × 12 mm, 2.2 kW tube limit** — typical catalogue/instrument
   values, not verified.
4. **Green–Cosslett exponent 1.6** for K-line intensity vs kV — widely quoted,
   not verified here.
5. **Densities** in §3.1 — handbook values from memory, not re-checked against a
   source in this session; the μ/ρ column, which is what the physics uses, is
   verified.
6. **Bremsstrahlung absolute scale** — Kramers' law gives the shape; the
   amplitude is normalised by a user parameter and is not predicted.
7. **ISBNs 2, 18, 19** — as printed; not checked against a catalogue record
   (Crossref has no ISBN for these editions).
8. **Hölzer Kα2 and Kβ digits** — the 640f certificate independently confirms
   Kα1 = 1.5405929 Å; Kα2 and Kβ rest on [6]/[7] as commonly tabulated. The
   Kα2–Kα1 *difference*, which is what the doublet model needs, is 0.0038345 Å.

What is solid: all geometry algebra (§1.4, eqs. 1–3), all absorption numbers
(§3.1, from NIST XCOM tables fetched today), the SRM 640f/660a constants and the
Si peak positions (§8.1, read from the certificates), the Scherrer and splitting
arithmetic, and every DOI in §9.
