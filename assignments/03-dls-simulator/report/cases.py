"""The parameter sets this report uses, in one place.

Figures, tables, the quoted numbers and the PDF all import these, so a figure cannot
disagree with a table about which case it shows.

Every case fixes the detector angle at 173 deg (the choice is argued in section 2 of the
report); the class page says 178 deg. ``run()`` merges an override dict onto the base case.
"""

from __future__ import annotations

from dlssim import DLSInputs, DLSOutputs, simulate_dls

# ---------------------------------------------------------------- fixed choices
ANGLE_DEG: float = 173.0        # detector angle used everywhere in this report
WAVELENGTH_NM: float = 632.8    # He-Ne laser line
INTERCEPT_BETA: float = 0.85    # coherence factor of the modelled instrument
PDI_LIMIT: float = 0.20         # the class page's "if PDI < 0.2" criterion

# ---------------------------------------------------------------- parameter sets
BASE = dict(
    solvent="water",
    particle_ri=1.590,
    size_nm=50.0,
    size_std_rel=0.12,
    aggregation=0.08,
    temperature_c=25.0,
    wavelength_nm=WAVELENGTH_NM,
    angle_deg=ANGLE_DEG,
    intercept_beta=INTERCEPT_BETA,
)

SIZES_NM = (10.0, 20.0, 50.0, 100.0, 200.0, 500.0)
SIZES_FIGURE_NM = (10.0, 50.0, 100.0, 500.0)
SIZES_REPORTED_NM = (10.0, 50.0, 100.0, 500.0)
SIGMA_SWEEP = (0.02, 0.05, 0.10, 0.15, 0.20, 0.30)
SIGMA_FIGURE = (0.02, 0.10, 0.20)
ALPHA_SWEEP = (0.0, 0.02, 0.05, 0.10, 0.20, 0.30)
ALPHA_FIGURE = (0.0, 0.10, 0.30)
SOLVENTS = ("water", "ethanol")
TEMPERATURES_C = (10.0, 25.0, 40.0, 55.0)
RI_SWEEP = (1.34, 1.40, 1.45, 1.50, 1.59, 1.75, 2.00)
ANGLES_DEG = (173.0, 178.0, 90.0)
NOISE_SWEEP = (0.0, 0.005, 0.010, 0.020)
NOISE_SEEDS = (1, 2, 3, 4, 5)


def run(**overrides) -> DLSOutputs:
    """Simulate one case: the base case with the given overrides."""
    kwargs = dict(BASE)
    kwargs.update(overrides)
    return simulate_dls(DLSInputs(**kwargs))


def case(**overrides) -> dict:
    """The full input dict for one case, as it will be reported."""
    kwargs = dict(BASE)
    kwargs.update(overrides)
    return kwargs


def row(outputs: DLSOutputs, **tags) -> dict:
    """Flatten one run into the quantities the tables and figures report.

    Everything here is measured from the same ``DLSOutputs`` the figures plot.
    """
    inp = outputs.inputs
    cum = outputs.cumulants
    dist = outputs.distribution
    rec = outputs.recovered
    row = {
        "solvent": inp.solvent,
        "temperature_c": inp.temperature_c,
        "particle_ri": inp.particle_ri,
        "size_nm": inp.size_nm,
        "sigma_rel": inp.size_std_rel,
        "aggregation": inp.aggregation,
        "viscosity_mpas": outputs.viscosity_mpa_s,
        "solvent_ri": outputs.solvent_ri,
        "q_nm_inv": outputs.q_nm_inv,
        "tau_c_ms": 1.0e3 / max(cum.gamma_bar_s_inv, 1.0e-12),
        "diffusion_m2_s": cum.z_avg_diffusion_m2_s,
        "z_avg_nm": cum.z_average_nm,
        "pdi": cum.pdi,
        "pdi_exact": cum.pdi_exact,
        "pdi_monomer_intrinsic": cum.pdi_monomer_intrinsic,
        "monodisperse": cum.is_monodisperse,
        "number_mean_nm": dist.number_mean_nm,
        "intensity_mean_nm": dist.intensity_mean_nm,
        "monomer_intensity_frac": dist.monomer_intensity_frac,
        "aggregate_diameter_nm": dist.aggregate_diameter_nm,
        "recovered_i_nm": rec.peak_intensity_nm,
        "recovered_n_nm": rec.peak_number_nm,
        "recovered_residual": rec.residual,
        "count_rate_kcps": outputs.mean_count_rate_kcps,
        "contrast": outputs.optical_contrast,
    }
    row.update(tags)
    return row
