# DLS model

Everything below is what the simulator computes. Each assumption that is a choice
rather than a measurement is marked **assumption**.

## 1. Geometry and scattering vector

A He-Ne laser (633 nm) illuminates a cuvette; the detector sits at angle theta from the
forward direction, 178 deg by default (the value written on the class page). In a medium
of refractive index n the scattering vector is

```
q = (4 pi n / lambda) sin(theta / 2)
```

At 633 nm, n = 1.3317, theta = 178 deg: q = 2.6423e7 1/m. The formula is geometry (Berne &
Pecora); it is not a result of Pecora 1964.

## 2. Brownian motion

A sphere of diameter d in a liquid of viscosity eta at temperature T diffuses with

```
D = k_B T / (3 pi eta d)
```

This is the Stokes-Einstein relation (Einstein 1905, using Stokes drag; see
`docs/research/reference_audit.md` for what was verified). For 100 nm
polystyrene in water at 25 C: D = 4.907e-12 m^2/s. Viscosity is interpolated from
measured tables; see `data/SOURCES.md`.

## 3. Correlation functions

Each particle size contributes a decaying exponential with rate

```
Gamma = D q^2
```

A population with intensity weights w_i gives

```
g1(tau) = sum_i w_i exp(-Gamma_i tau)
g2(tau) = 1 + beta |g1(tau)|^2
```

`beta` is the coherence factor of the optics (**assumption**: 0.9 by default, a typical
value for a well-aligned benchtop instrument). The ideal relation is g2 = 1 + |g1|^2; beta is
an instrument property, not part of the theory. For a single size, g1 decays with time
constant 1/Gamma, so a larger particle has a longer correlation time: the class note's
"larger -> slower, smaller -> faster".

## 4. Which particles dominate: number versus intensity

A particle scatters in proportion to its mass squared (Rayleigh), so intensity weights
grow as d^6. The intensity distribution is therefore shifted to large sizes relative to
the number distribution. This is not a bug to be corrected: it is why DLS reports
intensity-weighted sizes by default, and why a trace amount of aggregates can dominate
the signal.

A form factor P(q, d) reduces the weight of particles whose size is comparable to
1/q. Solid spheres use the Rayleigh-Gans-Debye form factor

```
P(q) = [3 (sin x - x cos x) / x^3]^2,   x = q d / 2
```

**Limitation**: RGD is exact for small particles and approximate when the particle is
large or optically dense (|m - 1| not small). For polystyrene in water (m = 1.19) and
sizes up to a few hundred nm it is acceptable; a Mie calculation would be needed for
metallic or micron-scale particles. The simulator never claims absolute scattering
cross-sections, only relative weights.

## 5. Cumulant analysis and PDI

Expanding ln g1:

```
ln g1(tau) = -Gamma_mean tau + (mu2 / 2) tau^2 - ...
```

A weighted quadratic fit gives Gamma_mean and mu2, and

```
PDI = 2 mu2 / Gamma_mean^2          (ISO 22412:2025; the factor 2 is the standard convention,
                                     not part of Koppel's original paper)
z-average diameter = k_B T q^2 / (3 pi eta Gamma_mean)
```

The fit uses lags up to 1.5 mean decay times, weighted by the inverse variance of ln g1
implied by the correlator noise model. Without those weights the second cumulant is
dominated by the noisiest long lags.

**Noise floor**: a finite acquisition makes a monodisperse sample report a small positive
PDI. With the default 30 s acquisition the floor is about 0.02-0.05, which matches the
values commercial instruments report for narrow standards. The floor falls as 1/sqrt(T)
and grows with particle size at fixed T, because a large particle has fewer independent
correlation times in the same acquisition window.

## 6. Inversion to a size distribution

On a log-spaced diameter grid the field correlation is linear in the intensity weights:

```
g1(tau_k) = sum_j w_j exp(-Gamma_j tau_k)
```

The simulator solves a non-negative least-squares problem with a second-difference
penalty on w (Tikhonov regularisation; Provencher's CONTIN is the standard alternative).
Lags where g1 has fallen below 0.01 are dropped, and each lag is weighted by the inverse
of the correlator noise. A constant baseline is fitted alongside the weights: the square
root used to obtain g1 from g2 is concave, so noise at long lags leaves a small positive
offset, and without a baseline term that offset is explained by spurious mass at the
largest grid sizes.

The mode of the recovered distribution is coarser than the z-average: it is limited by
the grid spacing and by the noise-driven broadening, and it comes out a few percent low
for narrow samples. The report quotes the cumulant z-average for size claims and uses
the distribution to show shape and the number/intensity difference.

The solution is an intensity distribution. The number distribution divides by the
intensity scattered per particle (proportional to d^6 P(q)) and is reported only where
the intensity distribution exceeds 1 % of its peak. Outside that support the measurement
has no sensitivity: many tiny particles and one large particle can scatter the same
light, so the data cannot distinguish them. Number distributions from DLS are
correspondingly less reliable than the z-average, and the report says so.

## 7. Aggregation

A fraction f of primary particles forms fractal aggregates of N primaries:

```
Rg = (d_primary / 2) N^(1/df)
Rh = 0.9 Rg                        (**assumption**: Rh/Rg = 0.9 for clusters)
```

The aggregate is treated as a scattering object of mass N m_primary with the Debye
structure factor of a Gaussian chain,

```
S(q) = 2 (exp(-x) - 1 + x) / x^2,  x = q^2 Rg^2
```

Aggregation therefore raises the mean size, widens the decay-rate distribution (PDI) and
moves the intensity distribution towards the aggregate peak while the number
distribution stays dominated by primaries. This coarse model does not resolve cluster
shape, polydispersity of N, or restructuring.

## 8. Detection

The photon trace is generated from a complex Gaussian field whose intensity covariance is
exactly beta |g1|^2, then Poisson sampled, so the trace is non-negative and has the right
fluctuation statistics. Its sample interval is one tenth of the correlation time, so the
plotted trace shows the fluctuation envelope; it is an illustration, not the data that is
fitted. The measured correlation curve adds correlator noise with
standard deviation sqrt(2 tau / T) (1 + beta |g1|^2). The correlation is fitted, never
drawn: every reported number comes from the noisy curve.

The count rate is a stated instrument model, calibrated so that 100 nm polystyrene in
water at 25 C and 1e8 particles/mL gives 1e5 counts/s; it scales with concentration,
contrast squared and particle mass squared. It is not an absolute radiometric
calculation.

## 9. Not modelled

- zeta potential and electrophoretic mobility (listed on the class page as a separate
  concept, not as a simulator output)
- multiple scattering (valid only for dilute samples)
- flow, sedimentation and convection
- particle-size-dependent viscosity or hindered diffusion
- Mie resonances for large or absorbing particles
- dead time and afterpulsing (a dead-time parameter exists but is off by default)
