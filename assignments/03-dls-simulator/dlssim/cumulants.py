"""ISO 22412 / Koppel (1972) cumulant analysis and PDI evaluation.

The cumulant expansion of the field correlation is:

    ln |g1(tau)| = -Gamma_bar tau + (mu2 / 2) tau^2 - (mu3 / 6) tau^3 + ...

When fit experimentally as a polynomial in lag time tau:

    ln |g1(tau)| = a0 - a1 tau + a2 tau^2 - ...

the coefficients map to cumulants as:
    a1 = Gamma_bar
    a2 = mu2 / 2   (so mu2 = 2 * a2)

Under both textbook formulations (Koppel 1972, where relative variance is mu2 / Gamma_bar^2)
and international standards (ISO 22412:2025, defining PI = 2 * a2 / a1^2):

    PDI = 2 * a2 / a1^2 = 2 * (mu2 / 2) / Gamma_bar^2 = mu2 / Gamma_bar^2

Both expressions are mathematically identical. When PDI < 0.20, the colloidal
suspension is classified as monodisperse, matching the classroom whiteboard criterion.
"""

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
    pdi: float                  # reported value PDI = mu2 / Gamma_bar^2 = 2 a2 / a1^2
    pdi_exact: float            # from the true decay-rate distribution
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
    """Compute the Z-average diameter and the polydispersity index PDI = mu2 / Gamma_bar^2."""
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

    beta = max(float(intercept_beta), 1.0e-6)
    norm_g2 = np.asarray(g2_minus_1, dtype=float) / beta
    mask = (norm_g2 >= 0.12) & (norm_g2 <= 0.98)
    pdi_fitted = pdi_exact
    if int(np.count_nonzero(mask)) >= 5:
        tau_fit = np.asarray(tau_s, dtype=float)[mask]
        y_fit = 0.5 * np.log(np.clip(norm_g2[mask], 1.0e-12, 1.0))
        weights_fit = np.sqrt(norm_g2[mask])
        # Fit y(tau) = a0 - a1 * tau + a2 * tau^2
        # np.polyfit returns [a2, -a1, a0]
        poly_coeffs = np.polyfit(tau_fit, y_fit, deg=2, w=weights_fit)
        a2_fit = max(float(poly_coeffs[0]), 0.0)
        a1_fit = max(-float(poly_coeffs[1]), 1.0e-12)
        # ISO 22412: PI = 2 * a2 / a1^2; since a2 = mu2/2, PI = mu2 / a1^2
        pdi_fitted = float(2.0 * a2_fit / (a1_fit * a1_fit))

    pdi_reported = float(pdi_fitted)
    pdi_monomer = float(size_std_rel) ** 2
    is_mono = bool(pdi_reported < PDI_MONODISPERSE_LIMIT)
    if is_mono:
        verdict = f"Monodisperse (PDI = {pdi_reported:.3f} < 0.20)"
    else:
        verdict = f"Polydisperse / Aggregated (PDI = {pdi_reported:.3f} >= 0.20)"

    return CumulantResult(
        z_average_nm=z_average_nm,
        pdi=pdi_reported,
        pdi_exact=float(pdi_exact),
        pdi_fitted=float(pdi_fitted),
        pdi_monomer_intrinsic=pdi_monomer,
        gamma_bar_s_inv=gamma_bar,
        mu2_s_inv2=mu2,
        z_avg_diffusion_m2_s=d_z_m2_s,
        is_monodisperse=is_mono,
        quality_verdict=verdict,
    )
