"""The numbers the report quotes, computed once.

The PDF builder and both gates import this module, so a figure in the text cannot disagree
with the model that produced it. Every value here must appear literally in the built PDF;
``report/check_numbers.py`` refuses a PDF where one of them does not.
"""

from __future__ import annotations

import numpy as np

from .cases import BASE, row, run
from .size_study import rows as size_rows
from .tables import (aggregation_rows, angle_rows, noise_rows, noisy_inversion_rows,
                     polydispersity_rows, refractive_index_rows, solvent_rows)


def _by(rows: list[dict], key: str, value: float) -> dict:
    return next(entry for entry in rows if float(entry[key]) == float(value))


def quoted_numbers() -> dict[str, str]:
    size = {float(entry["size_nm"]): entry for entry in size_rows()}
    pdi = {float(entry["sigma_rel"]): entry for entry in polydispersity_rows()}
    agg = {float(entry["aggregation"]): entry for entry in aggregation_rows()}
    solvent = {(entry["solvent"], float(entry["temperature_c"])): entry
               for entry in solvent_rows()}
    ri = {float(entry["particle_ri"]): entry for entry in refractive_index_rows()}
    angle = {float(entry["angle_deg"]): entry for entry in angle_rows()}
    noise = {float(entry["noise_level"]): entry for entry in noise_rows()}
    noisy = {float(entry["size_nm"]): entry for entry in noisy_inversion_rows()}
    base = row(run(**BASE))

    water_25 = solvent[("water", 25.0)]
    ethanol_25 = solvent[("ethanol", 25.0)]
    eta_ratio = ethanol_25["viscosity_mpas"] / water_25["viscosity_mpas"]
    q_ratio = (water_25["q_nm_inv"] / ethanol_25["q_nm_inv"]) ** 2

    return {
        # ---- the base case (section 3)
        "base_tau_ms": f"{base['tau_c_ms']:.4f}",
        "base_z_nm": f"{base['z_avg_nm']:.2f}",
        "base_pdi": f"{base['pdi']:.4f}",
        "base_kcps": f"{base['count_rate_kcps']:.1f}",
        "base_number_mean_nm": f"{base['number_mean_nm']:.2f}",
        "base_intensity_mean_nm": f"{base['intensity_mean_nm']:.2f}",
        "base_q_nm_inv": f"{base['q_nm_inv']:.5f}",
        "base_diffusion_um2_s": f"{base['diffusion_m2_s'] * 1e12:.3f}",
        # ---- the size sweep (section 5.1)
        "size10_tau_ms": f"{size[10.0]['tau_c_ms']:.4f}",
        "size500_tau_ms": f"{size[500.0]['tau_c_ms']:.4f}",
        "size10_z_nm": f"{size[10.0]['z_avg_nm']:.2f}",
        "size500_z_nm": f"{size[500.0]['z_avg_nm']:.2f}",
        "size10_diffusion_um2_s": f"{size[10.0]['diffusion_m2_s'] * 1e12:.3f}",
        "size500_diffusion_um2_s": f"{size[500.0]['diffusion_m2_s'] * 1e12:.3f}",
        "size_tau_ratio": f"{size[500.0]['tau_c_ms'] / size[10.0]['tau_c_ms']:.1f}",
        "size_z_error_small": f"{size[10.0]['z_error_pct']:.2f}",
        "size_z_error_large": f"{size[500.0]['z_error_pct']:+.2f}",
        "size_recovered_100_nm": f"{size[100.0]['recovered_i_nm']:.0f}",
        "size_recovered_500_nm": f"{size[500.0]['recovered_i_nm']:.0f}",
        # ---- polydispersity (section 5.2)
        "pdi_sigma_002": f"{pdi[0.02]['pdi']:.4f}",
        "pdi_sigma_010": f"{pdi[0.10]['pdi']:.4f}",
        "pdi_sigma_020": f"{pdi[0.20]['pdi']:.4f}",
        "pdi_sigma_030": f"{pdi[0.30]['pdi']:.4f}",
        "width_from_pdi_030": f"{(pdi[0.30]['pdi'] / 2.0) ** 0.5:.3f}",
        "intensity_mean_sigma_030": f"{pdi[0.30]['intensity_mean_nm']:.1f}",
        "z_avg_sigma_030": f"{pdi[0.30]['z_avg_nm']:.2f}",
        # ---- aggregation (section 5.3)
        "agg_pdi_000": f"{agg[0.0]['pdi']:.4f}",
        "agg_pdi_010": f"{agg[0.10]['pdi']:.4f}",
        "agg_pdi_030": f"{agg[0.30]['pdi']:.4f}",
        "agg_z_030": f"{agg[0.30]['z_avg_nm']:.2f}",
        "agg_intensity_mean_030": f"{agg[0.30]['intensity_mean_nm']:.1f}",
        "agg_cluster_nm": f"{agg[0.30]['aggregate_diameter_nm']:.0f}",
        "agg_share_030": f"{1.0 - agg[0.30]['monomer_intensity_frac']:.3f}",
        "agg_exact_pdi_010": f"{agg[0.10]['pdi_exact']:.4f}",
        # ---- solvent and temperature (section 5.4)
        "eta_water_25": f"{water_25['viscosity_mpas']:.3f}",
        "eta_ethanol_25": f"{ethanol_25['viscosity_mpas']:.3f}",
        "eta_ratio": f"{eta_ratio:.3f}",
        "tau_water_10": f"{solvent[('water', 10.0)]['tau_c_ms']:.4f}",
        "tau_water_55": f"{solvent[('water', 55.0)]['tau_c_ms']:.4f}",
        "tau_temp_ratio": f"{solvent[('water', 10.0)]['tau_c_ms'] / solvent[('water', 55.0)]['tau_c_ms']:.2f}",
        "tau_ethanol_25": f"{ethanol_25['tau_c_ms']:.4f}",
        "solvent_tau_ratio": f"{ethanol_25['tau_c_ms'] / water_25['tau_c_ms']:.3f}",
        "q_water_25": f"{water_25['q_nm_inv']:.5f}",
        "q_ethanol_25": f"{ethanol_25['q_nm_inv']:.5f}",
        "solvent_q_factor": f"{q_ratio:.3f}",
        "z_water_10": f"{solvent[('water', 10.0)]['z_avg_nm']:.2f}",
        "z_water_55": f"{solvent[('water', 55.0)]['z_avg_nm']:.2f}",
        # ---- refractive index (section 5.5)
        "contrast_np_140": f"{ri[1.40]['contrast']:.5f}",
        "contrast_np_159": f"{ri[1.59]['contrast']:.5f}",
        "contrast_np_200": f"{ri[2.00]['contrast']:.5f}",
        "kcps_np_134": f"{ri[1.34]['count_rate_kcps']:.1f}",
        "kcps_np_140": f"{ri[1.40]['count_rate_kcps']:.1f}",
        "kcps_np_159": f"{ri[1.59]['count_rate_kcps']:.1f}",
        "kcps_np_200": f"{ri[2.00]['count_rate_kcps']:.1f}",
        # ---- detector angle (section 5.6)
        "q_173": f"{angle[173.0]['q_nm_inv']:.5f}",
        "q_178": f"{angle[178.0]['q_nm_inv']:.5f}",
        "angle_scale_178": f"{abs(angle[178.0]['size_scale_rel_pct']):.3f}",
        "angle_scale_90": f"{abs(angle[90.0]['size_scale_rel_pct']):.1f}",
        # ---- inversion and noise (section 6)
        "inv_i_error_100_noiseless": f"{size[100.0]['recovered_i_error_pct']:.1f}",
        "inv_i_error_100_noisy": f"{noisy[100.0]['i_error_pct']:.1f}",
        "inv_noisy_min_error": f"{min(abs(e['i_error_pct']) for e in noisy.values()):.1f}",
        "inv_residual_noisy": f"{noisy[100.0]['recovered_residual']:.4f}",
        "pdi_noiseless": f"{noise[0.0]['pdi_mean']:.4f}",
        "pdi_noise_1pct_mean": f"{noise[0.010]['pdi_mean']:.4f}",
        "pdi_noise_1pct_min": f"{noise[0.010]['pdi_min']:.4f}",
        "pdi_noise_1pct_max": f"{noise[0.010]['pdi_max']:.4f}",
    }


if __name__ == "__main__":
    for name, value in quoted_numbers().items():
        print(f"{name:28s} {value}")
