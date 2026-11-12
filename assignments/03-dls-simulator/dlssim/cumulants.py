"""ISO 22412 / Koppel (1972) cumulant analysis and PDI evaluation."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .autocorrelation import BOLTZMANN_K

PDI_MONODISPERSE_LIMIT: float = 0.20


@dataclass(frozen=True)
class CumulantResult:
    """Cumulant analysis outputs including Z-average size and PDI."""

    z_average_nm: float
    pdi: float
    pdi_fitted: float
    pdi_monomer_intrinsic: float
    gamma_bar_s_inv: float
    mu2_s_inv2: float
    z_avg_diffusion_m2_s: float
    is_monodisperse: bool
    quality_verdict: str


def compute_cumulants(
    tau_s: np.ndarray,
    g2_minus_1: np.ndarray,
    gamma_dist_s_inv: np.ndarray,
    intensity_dist: np.ndarray,
    temperature_k: float,
    viscosity_pa_s: float,
    q_m_inv: float,
    intercept_beta: float,
    size_std_rel: float,
) -> CumulantResult:
    """Compute Z-average hydrodynamic diameter D_z and Polydispersity Index (PDI).

    Under ISO 22412:2017 and Koppel (J. Chem. Phys. 57, 4814, 1972):
      - First cumulant:  Gamma_bar = sum_i p_I(d_i) Gamma_i
      - Second cumulant: mu_2      = sum_i p_I(d_i) (Gamma_i - Gamma_bar)^2
      - Polydispersity:  PDI       = mu_2 / Gamma_bar^2
      - Z-avg diffusion: D_z       = Gamma_bar / q^2
      - Z-avg diameter:  D_z_nm    = k_B T / (3 pi eta D_z) * 1e9

    Also performs a weighted quadratic polynomial fit of ln|g_1(tau)| over the
    initial decay window (0.10 <= g_2(tau)-1 <= 0.98 * beta) to report the
    experimental cumulant-fit PDI alongside the exact distribution cumulant PDI.
    """
    w = np.asarray(intensity_dist, dtype=float)
    w = w / max(float(np.sum(w)), 1.0e-30)
    gamma = np.asarray(gamma_dist_s_inv, dtype=float)

    gamma_bar = float(np.sum(w * gamma))
    mu2 = float(np.sum(w * ((gamma - gamma_bar) ** 2)))
    pdi_exact = float(mu2 / max(gamma_bar * gamma_bar, 1.0e-30))

    d_z_m2_s = gamma_bar / max(float(q_m_inv) ** 2, 1.0e-30)
    z_avg_m = BOLTZMANN_K * float(temperature_k) / (
        3.0 * math.pi * float(viscosity_pa_s) * max(d_z_m2_s, 1.0e-30)
    )
    z_average_nm = float(z_avg_m * 1.0e9)

    # Quadratic cumulant fit on the upper part of the decay curve (ISO 22412)
    beta = max(float(intercept_beta), 1.0e-6)
    norm_g2 = np.asarray(g2_minus_1, dtype=float) / beta
    mask = (norm_g2 >= 0.12) & (norm_g2 <= 0.98)
    if int(np.count_nonzero(mask)) >= 5:
        tau_fit = np.asarray(tau_s, dtype=float)[mask]
        y_fit = 0.5 * np.log(np.clip(norm_g2[mask], 1.0e-12, 1.0))
        weights_fit = norm_g2[mask]
        # Fit y(tau) = c0 - gamma_fit * tau + 0.5 * mu2_fit * tau^2
        poly_coeffs = np.polyfit(tau_fit, y_fit, deg=2, w=weights_fit)
        mu2_fit = max(2.0 * float(poly_coeffs[0]), 0.0)
        gamma_fit = max(-float(poly_coeffs[1]), 1.0e-12)
        pdi_fitted = float(mu2_fit / (gamma_fit * gamma_fit))
    else:
        pdi_fitted = pdi_exact

    pdi_monomer = float(size_std_rel) ** 2
    is_mono = bool(pdi_exact < PDI_MONODISPERSE_LIMIT)
    if is_mono:
        verdict = f"Monodisperse (PDI = {pdi_exact:.3f} < 0.20)"
    else:
        verdict = f"Polydisperse / Aggregated (PDI = {pdi_exact:.3f} >= 0.20)"

    return CumulantResult(
        z_average_nm=z_average_nm,
        pdi=pdi_exact,
        pdi_fitted=pdi_fitted,
        pdi_monomer_intrinsic=pdi_monomer,
        gamma_bar_s_inv=gamma_bar,
        mu2_s_inv2=mu2,
        z_avg_diffusion_m2_s=d_z_m2_s,
        is_monodisperse=is_mono,
        quality_verdict=verdict,
    )
