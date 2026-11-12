"""Particle size distributions: Number, Volume, and Intensity weighting with aggregation.

Implements the inputs from the in-class whiteboard specification:
- size of the particle (mean monomer hydrodynamic diameter d0 in nm)
- size distribution of the particle (fractional width sigma_rel = sigma / d0, shape)
- aggregation parameter (alpha_agg in [0, 1], controlling aggregate population)
- refractive index of the particle & solvent (via optical scattering weights)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .mie import scattering_cross_section_weight, scattering_wavevector_nm_inv


@dataclass(frozen=True)
class SizeDistribution:
    """Normalized Number, Volume, and Intensity particle size distributions."""

    diameter_nm: np.ndarray            # logarithmic diameter grid (nm)
    number_dist: np.ndarray            # p_N(d), normalized so sum(p_N) = 1
    volume_dist: np.ndarray            # p_V(d) ~ p_N(d) * d^3
    intensity_dist: np.ndarray         # p_I(d) ~ p_N(d) * d^6 * P(qR)
    monomer_intensity_dist: np.ndarray # monomer-only intensity distribution
    number_mean_nm: float
    number_std_nm: float
    intensity_mean_nm: float
    intensity_std_nm: float
    monomer_intensity_frac: float
    aggregate_intensity_frac: float
    aggregate_diameter_nm: float


def build_size_distribution(
    mean_size_nm: float,
    rel_width: float,
    aggregation_param: float = 0.0,
    particle_ri: float = 1.59,
    solvent_ri: float = 1.3325,
    wavelength_nm: float = 632.8,
    angle_deg: float = 173.0,
    dist_shape: str = "lognormal",
    agg_size_factor: float = 5.5,
    n_bins: int = 300,
    d_min_nm: float = 0.5,
    d_max_nm: float = 10000.0,
) -> SizeDistribution:
    """Construct Number, Volume, and Intensity distributions on a log size axis.

    Because scattered intensity scales as d^6, even a tiny number fraction of
    aggregates produces a strong secondary peak in the Intensity distribution
    and a slow-decay tail in the autocorrelation function g2(tau).
    """
    if mean_size_nm <= 0:
        raise ValueError("mean_size_nm must be positive")
    if rel_width <= 0:
        raise ValueError("rel_width must be positive")
    if not (0.0 <= aggregation_param < 1.0):
        raise ValueError("aggregation_param must be in [0.0, 1.0)")

    d = np.geomspace(d_min_nm, d_max_nm, n_bins)
    s_rel = max(float(rel_width), 0.01)

    if dist_shape.lower() == "gaussian":
        sigma_nm = s_rel * mean_size_nm
        p_mono_n = np.exp(-0.5 * ((d - mean_size_nm) / sigma_nm) ** 2)
    else:
        sigma_ln = math.sqrt(math.log(1.0 + s_rel * s_rel))
        mu_ln = math.log(mean_size_nm) - 0.5 * sigma_ln * sigma_ln
        p_mono_n = (1.0 / d) * np.exp(
            -0.5 * ((np.log(d) - mu_ln) / sigma_ln) ** 2
        )

    p_mono_n = p_mono_n / max(float(np.sum(p_mono_n)), 1e-30)

    d_agg = min(mean_size_nm * agg_size_factor, d_max_nm * 0.45)
    sigma_agg_ln = math.sqrt(math.log(1.0 + max(s_rel * 1.25, 0.18) ** 2))
    mu_agg_ln = math.log(d_agg) - 0.5 * sigma_agg_ln * sigma_agg_ln
    p_agg_n = (1.0 / d) * np.exp(
        -0.5 * ((np.log(d) - mu_agg_ln) / sigma_agg_ln) ** 2
    )
    p_agg_n = p_agg_n / max(float(np.sum(p_agg_n)), 1e-30)

    q_nm_inv = scattering_wavevector_nm_inv(wavelength_nm, solvent_ri, angle_deg)
    scat_w = scattering_cross_section_weight(d, particle_ri, solvent_ri, q_nm_inv)
    if np.all(scat_w <= 1e-30):
        scat_w = d ** 6

    mono_scat_avg = float(np.sum(p_mono_n * scat_w))
    agg_scat_avg = float(np.sum(p_agg_n * scat_w))

    if aggregation_param <= 0.0 or agg_scat_avg <= 0.0:
        f_num_agg = 0.0
    else:
        ratio = (aggregation_param / (1.0 - aggregation_param)) * (
            mono_scat_avg / agg_scat_avg
        )
        f_num_agg = ratio / (1.0 + ratio)

    p_n = (1.0 - f_num_agg) * p_mono_n + f_num_agg * p_agg_n
    p_n = p_n / float(np.sum(p_n))

    p_v = p_n * (d ** 3)
    p_v = p_v / float(np.sum(p_v))

    p_i_mono_only = p_mono_n * scat_w
    p_i_mono_only = p_i_mono_only / max(float(np.sum(p_i_mono_only)), 1e-30)

    p_i_mono = (1.0 - f_num_agg) * p_mono_n * scat_w
    p_i_agg = f_num_agg * p_agg_n * scat_w
    total_i = float(np.sum(p_i_mono + p_i_agg))
    p_i = (p_i_mono + p_i_agg) / max(total_i, 1e-30)

    num_mean = float(np.sum(p_n * d))
    num_std = math.sqrt(max(float(np.sum(p_n * ((d - num_mean) ** 2))), 0.0))
    int_mean = float(np.sum(p_i * d))
    int_std = math.sqrt(max(float(np.sum(p_i * ((d - int_mean) ** 2))), 0.0))

    mono_frac = float(np.sum(p_i_mono) / max(total_i, 1e-30))
    agg_frac = float(np.sum(p_i_agg) / max(total_i, 1e-30))

    return SizeDistribution(
        diameter_nm=d,
        number_dist=p_n,
        volume_dist=p_v,
        intensity_dist=p_i,
        monomer_intensity_dist=p_i_mono_only,
        number_mean_nm=num_mean,
        number_std_nm=num_std,
        intensity_mean_nm=int_mean,
        intensity_std_nm=int_std,
        monomer_intensity_frac=mono_frac,
        aggregate_intensity_frac=agg_frac,
        aggregate_diameter_nm=d_agg,
    )
