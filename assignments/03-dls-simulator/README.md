# Assignment 3 — Dynamic Light Scattering (DLS) Nanoparticle Simulator (`dlssim`)

A physics-based **Dynamic Light Scattering (DLS) / Photon Correlation Spectroscopy (PCS)** simulator implemented in Python (`dlssim`), designed around the in-class whiteboard specification:

## In-Class Whiteboard Specification

### Inputs (6 Core Parameters)
1. **Select solvent (`water`, `ethanol`, `pbs`, `toluene`)**:
   - Temperature-dependent dynamic viscosity $\eta(T)$ via the Vogel–Fulcher–Tammann (VFT) / Andrade relation (`water`: $0.890\text{ mPa}\cdot\text{s}$ at $25\,^\circ\text{C}$; `ethanol`: $1.074\text{ mPa}\cdot\text{s}$ at $25\,^\circ\text{C}$).
   - Temperature-dependent solvent refractive index $n_s(T)$.
2. **Refractive index of the particle ($n_p$)**:
   - Controls the Lorentz–Lorenz / Clausius–Mossotti optical contrast factor
     $$K_{\text{opt}}(n_p, n_s) = \left(\frac{m^2 - 1}{m^2 + 2}\right)^2, \qquad m = \frac{n_p}{n_s},$$
     and scales the scattered photon count rate $\langle I(t)\rangle$.
3. **Size of the particle ($d_0$ in nm)**:
   - Mean hydrodynamic diameter of the primary nanoparticle population.
4. **Size distribution of the particle ($\sigma / d_0$, shape)**:
   - Relative standard deviation $\sigma / d_0$ and distribution shape (`lognormal` or `gaussian`).
5. **Aggregation parameter ($\alpha_{\text{agg}} \in [0, 1)$)**:
   - Controls secondary cluster formation ($d_{\text{agg}} \approx 5.5\,d_0$), producing a slow-decay shoulder in $g_2(\tau)-1$ and a secondary peak in the intensity distribution $p_I(d)$.
6. **Temperature ($T$ in $^\circ\text{C}$)**:
   - Enters both the thermal energy $k_B T$ and the solvent viscosity $\eta(T)$ in the Stokes–Einstein relation.

### Outputs (3 Core Outputs + Speckle Trace)
1. **Auto-correlation function on a logarithmic lag-time axis (`tau_s`)**:
   - Translational diffusion coefficient via the Stokes–Einstein equation:
     $$D(d, T) = \frac{k_B T}{3\pi\,\eta(T)\,d}, \qquad \Gamma(d) = D(d)\,q^2, \qquad q = \frac{4\pi n_s(T)}{\lambda_0}\sin\!\left(\frac{\theta}{2}\right).$$
   - Polydisperse field autocorrelation $g_1(\tau) = \sum_i p_I(d_i)\exp(-\Gamma(d_i)\tau)$ and Siegert intensity autocorrelation $g_2(\tau) - 1 = \beta\,|g_1(\tau)|^2$ on a logarithmic axis $\tau \in [10^{-7}, 10^0]\text{ s}$.
   - Stochastic Brownian speckle photon-count trace $I(t)$ (`Photon Counts vs t`).
2. **Size distribution `[Number, Intensity]` on a logarithmic size axis (`diameter_nm`)**:
   - Number distribution $p_N(d)$ and Intensity distribution $p_I(d) \propto p_N(d)\,d^6\,P(qd/2)$ plotted against $\log_{10}(d/\text{nm})$.
3. **Polydispersity Index (`PDI`) & Monodispersity Criterion (`If PDI < 0.2`)**:
   - ISO 22412 / Koppel (1972) cumulant expansion $\ln|g_1(\tau)| \approx -\bar{\Gamma}\tau + \frac{1}{2}\mu_2\tau^2$:
     $$\text{PDI} = \frac{\mu_2}{\bar{\Gamma}^2}, \qquad D_z = \frac{k_B T}{3\pi\,\eta(T)\,(\bar{\Gamma}/q^2)}.$$
   - Evaluates the classroom criterion **`If PDI < 0.2`** (`Monodisperse` vs `Polydisperse / Aggregated`).

---

## Quick Start

### 1. Run the Command-Line Simulator
```bash
cd assignments/03-dls-simulator
python -m dlssim --solvent water --ri 1.59 --size-nm 50 --sigma 0.12 --aggregation 0.08 --temp-c 25 --out out/dls_dashboard.png --compare-out out/dls_whiteboard_comparison.png
```

### 2. Launch the Interactive GUI
```bash
python -m dlssim --gui
```

### 3. Run the Test Suite
```bash
pytest -q
```
