# DLS model

What the simulator computes, and which parts are choices rather than measurements.

## 1. Geometry

A He-Ne laser (632.8 nm) illuminates a cuvette; the detector sits at angle theta
(default 173 deg, configurable). The scattering vector is

```
q = (4 pi n_s / lambda_0) sin(theta / 2)
```

At 632.8 nm, n_s = 1.3312, theta = 173 deg: q = 2.64e7 1/m. The formula is geometry
(Berne & Pecora); it is not a result of Pecora 1964.

## 2. Brownian motion

```
D = k_B T / (3 pi eta d),        Gamma = D q^2
```

For 100 nm polystyrene in water at 25 C, D = 4.9e-12 m^2/s. Viscosity uses the
VFT/Andrade form `eta = A exp(B/(T - T0))` anchored to standard 25 C values; the
parameters are listed in `data/SOURCES.md`. Water and ethanol are the class solvents;
PBS and toluene are extra options.

## 3. Correlation functions

For intensity weights w_i over decay rates Gamma_i:

```
g1(tau) = sum_i w_i exp(-Gamma_i tau)
g2(tau) - 1 = beta |g1(tau)|^2
```

beta is the coherence factor (default 0.85), an instrument property. The ideal Siegert
relation is g2 = 1 + |g1|^2.

The lag grid is fixed: 220 points from 1e-7 s to 1 s, log-spaced. That covers particles
from about 2 nm to 2 um at 173 deg; outside that range the curve can be truncated at one
end.

## 4. Size distributions

The sample is built as a bimodal mixture: a primary mode (lognormal or Gaussian in
diameter, width sigma/d0) and an aggregate mode centred at `agg_size_factor * d0`
(default 5.5). The aggregate *intensity* fraction equals the aggregation parameter
alpha: the mixture's number fractions are solved so that

```
I_aggregate / (I_aggregate + I_monomer) = alpha
```

Each size class is weighted by `K_opt * d^6 * P(qd/2)`, where K_opt is the
Lorentz-Lorenz contrast and P is a form factor. The simulator uses

```
P = 0.35 P_sphere(RGD) + 0.65 P_Guinier
```

**Limitation**: that blend is an approximation, not a Mie solution. It keeps P -> 1 at
small qd, follows the sphere form factor at intermediate qd, and avoids the unphysical
zeros of the pure sphere form factor at large qd. For absorbing or micron-scale
particles a Mie calculation would be required. The simulator never claims absolute
scattering cross sections.

Because scattering scales with mass squared, a small number fraction of aggregates can
dominate the intensity distribution while barely showing in the number distribution.
That is the physics the report is meant to show, not an artefact.

## 5. Cumulant analysis and PDI

```
ln |g1(tau)| = -Gamma_bar tau + (mu2 / 2) tau^2 - ...
PDI = 2 mu2 / Gamma_bar^2            (ISO 22412:2025)
z-average = k_B T q^2 / (3 pi eta Gamma_bar)
```

The fit uses lags where the normalised correlation falls between 0.12 and 0.98, with
weights sqrt(amplitude). The reported PDI is the fitted one; the exact PDI of the input
distribution is printed alongside. The factor 2 belongs to the standard's definition,
not to Koppel's 1972 paper.

**Noise floor**: with the default noise level of zero the fit is exact, so a
monodisperse sample reports PDI = 0. With `--noise 0.01` (1 % of the intercept) the
reported PDI of a monodisperse sample rises to a few hundredths, which is what real
instruments show. The report must state which noise setting each figure uses.

## 6. Inversion

The simulator also recovers a distribution from its own correlation curve, which is the
step an instrument performs:

```
g1(tau_k) = sum_j w_j exp(-Gamma_j tau_k)
```

solved by non-negative least squares on a 240-point log grid (1 nm to 10 um) with a
second-difference penalty, dropping lags below g1 = 0.01 and fitting a constant baseline.
The recovered intensity distribution is converted to number by dividing by `d^6 P`, and
the number distribution is reported only where the intensity exceeds 1 % of its peak:
outside that support the measurement has no sensitivity.

**Limitation**: the recovered mode is a few percent low for narrow samples, and the
number distribution is less reliable than the intensity one. The report quotes the
cumulant z-average for size claims.

## 7. Photon trace and count rate

The trace is a complex Ornstein-Uhlenbeck field, so |g1| decays exponentially and the
intensity follows the Siegert relation; it is an illustration of speckle fluctuations,
not the data that is fitted. The mean count rate is a stated instrument model
(280 kcps at 50 nm reference, scaling with contrast and size), not an absolute
radiometric calculation.

## 8. Not modelled

- zeta potential / electrophoretic mobility (listed on the page as a separate concept)
- multiple scattering (dilute samples only)
- flow, sedimentation, convection
- Mie resonances, absorption
- dead time and afterpulsing
- aggregate polydispersity beyond the fixed width of the second mode
