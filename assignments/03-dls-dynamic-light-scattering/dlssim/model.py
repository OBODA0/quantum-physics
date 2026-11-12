"""The complete DLS model: inputs in, correlation curve and size distribution out."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .aggregation import Aggregation, build_population
from .brownian import (
    decay_rate,
    diameter_from_decay_rate,
    diffusion_coefficient,
    scattering_vector,
)
from .constants import DEFAULT_ANGLE_DEG, DEFAULT_WAVELENGTH_M, K_B
from .correlation import (
    CumulantResult,
    analytic_cumulants,
    cumulant_fit,
    field_correlation,
    intensity_correlation,
)
from .detector import DetectorConfig, measured_correlation, photon_trace
from .inversion import InversionResult, decay_rates_for_grid, diameter_grid, invert
from .materials import MATERIALS, Material
from .population import Population
from .scattering import contrast_factor, particle_mass, sphere_form_factor
from .sizes import SizeDistribution
from .solvents import SOLVENTS, Solvent


@dataclass
class DLSModel:
    """A DLS measurement on one sample.

    All lengths in metres, temperatures in degrees Celsius.
    """

    diameter_m: float = 100e-9
    geometric_sd: float = 1.0
    solvent_name: str = "water"
    material_name: str = "polystyrene"
    temperature_c: float = 25.0
    aggregation_fraction: float = 0.0
    aggregation_number: int = 10
    fractal_dimension: float = 1.8
    wavelength_m: float = DEFAULT_WAVELENGTH_M
    angle_deg: float = DEFAULT_ANGLE_DEG
    beta: float = 0.9
    grid_points: int = 161

    def __post_init__(self) -> None:
        if self.diameter_m <= 0:
            raise ValueError("diameter must be positive")
        if self.geometric_sd < 1.0:
            raise ValueError("geometric standard deviation must be >= 1")
        if self.solvent_name not in SOLVENTS:
            raise ValueError(f"unknown solvent {self.solvent_name!r}; choose from {sorted(SOLVENTS)}")
        if self.material_name not in MATERIALS:
            raise ValueError(
                f"unknown material {self.material_name!r}; choose from {sorted(MATERIALS)}"
            )
        if not 0.0 < self.beta <= 1.0:
            raise ValueError("beta must lie in (0, 1]")

    # --- fixed properties -------------------------------------------------

    @property
    def solvent(self) -> Solvent:
        return SOLVENTS[self.solvent_name]

    @property
    def material(self) -> Material:
        return MATERIALS[self.material_name]

    @property
    def refractive_index(self) -> float:
        return self.solvent.refractive_index(self.wavelength_m, self.temperature_c)

    @property
    def viscosity(self) -> float:
        return self.solvent.viscosity(self.temperature_c)

    @property
    def q(self) -> float:
        return scattering_vector(self.refractive_index, self.wavelength_m, self.angle_deg)

    @property
    def contrast(self) -> float:
        return contrast_factor(self.material.refractive_index, self.refractive_index)

    @property
    def aggregation(self) -> Aggregation:
        return Aggregation(
            fraction=self.aggregation_fraction,
            number=self.aggregation_number,
            fractal_dimension=self.fractal_dimension,
        )

    @property
    def size_distribution(self) -> SizeDistribution:
        return SizeDistribution.lognormal(
            self.diameter_m, self.geometric_sd, points=self.grid_points
        )

    @property
    def population(self) -> Population:
        return build_population(self.size_distribution, self.aggregation, self.q, self.material)

    # --- derived quantities ----------------------------------------------

    def decay_rates(self) -> tuple[np.ndarray, np.ndarray]:
        """Decay rate and normalised intensity weight for each population entry."""
        population = self.population
        temperature_k = self.temperature_c + 273.15
        gammas = (
            K_B * temperature_k * self.q**2
            / (3.0 * np.pi * self.viscosity * population.diameters_m)
        )
        return gammas, population.intensity_weights(self.contrast)

    @property
    def mean_decay_rate(self) -> float:
        gammas, weights = self.decay_rates()
        return float(np.sum(gammas * weights))

    @property
    def correlation_time(self) -> float:
        return 1.0 / self.mean_decay_rate

    @property
    def true_cumulants(self) -> tuple[float, float, float]:
        """Mean decay rate, second cumulant and PDI of the true decay-rate spectrum."""
        gammas, weights = self.decay_rates()
        return analytic_cumulants(gammas, weights)

    @property
    def true_z_average_m(self) -> float:
        gammas, weights = self.decay_rates()
        mean = float(np.sum(gammas * weights))
        return diameter_from_decay_rate(
            mean, self.viscosity, self.temperature_c, self.refractive_index,
            self.wavelength_m, self.angle_deg,
        )

    def diffusion(self, diameter_m: float | None = None) -> float:
        return diffusion_coefficient(
            self.diameter_m if diameter_m is None else diameter_m,
            self.viscosity,
            self.temperature_c,
        )

    # --- curves -----------------------------------------------------------

    def g1(self, tau: np.ndarray) -> np.ndarray:
        gammas, weights = self.decay_rates()
        return field_correlation(tau, gammas, weights)

    def g2(self, tau: np.ndarray, beta: float | None = None) -> np.ndarray:
        gammas, weights = self.decay_rates()
        return intensity_correlation(tau, gammas, weights, self.beta if beta is None else beta)

    def lags(self, points: int = 80, low_factor: float = 1e-3, high_factor: float = 1e2) -> np.ndarray:
        """Log-spaced lag grid around the mean correlation time."""
        return np.geomspace(self.correlation_time * low_factor, self.correlation_time * high_factor, points)

    def measure(
        self, config: DetectorConfig | None = None, seed: int | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Simulated noisy correlation curve."""
        config = config or DetectorConfig(beta=self.beta)
        rng = np.random.default_rng(seed)
        tau = self.lags()
        ideal = self.g2(tau)
        return tau, measured_correlation(tau, ideal, self.beta, config.duration_s, rng)

    def fit(self, tau: np.ndarray, g2: np.ndarray, duration_s: float = 30.0) -> CumulantResult:
        return cumulant_fit(
            tau, g2, self.beta, self.viscosity, self.temperature_c,
            self.refractive_index, self.wavelength_m, self.angle_deg,
            duration_s=duration_s,
        )

    def invert(
        self,
        tau: np.ndarray,
        g2: np.ndarray,
        regularization: float = 1e-6,
        max_diameter_m: float | None = None,
        duration_s: float = 30.0,
        support_fraction: float = 0.01,
    ) -> InversionResult:
        amplitude = np.clip((np.asarray(g2) - 1.0) / self.beta, 0.0, None)
        g1 = np.sqrt(amplitude)
        top = max_diameter_m or max(5e-6, 20.0 * np.max(self.population.diameters_m))
        grid = diameter_grid(1e-9, top)
        return invert(
            tau, g1, grid, self.q, self.viscosity, self.temperature_c,
            self.material.density_kg_m3, regularization,
            duration_s=duration_s, beta=self.beta, support_fraction=support_fraction,
        )

    def photon_trace(self, config: DetectorConfig | None = None, seed: int | None = None) -> np.ndarray:
        config = config or DetectorConfig(beta=self.beta)
        rng = np.random.default_rng(seed)
        return photon_trace(self.g1, self.correlation_time, config, rng)

    def count_rate_cps(self, concentration_per_ml: float = 1e8, calibration_cps: float = 1e5) -> float:
        """Stated count-rate model, calibrated at 100 nm polystyrene in water at 25 C."""
        reference_material = MATERIALS["polystyrene"]
        reference_solvent = SOLVENTS["water"]
        reference_mass = particle_mass(100e-9, reference_material.density_kg_m3)
        reference_index = reference_solvent.refractive_index(DEFAULT_WAVELENGTH_M, 25.0)
        reference_contrast = contrast_factor(reference_material.refractive_index, reference_index)
        # the calibration point is one 100 nm sphere, form factor included
        reference_form = float(
            sphere_form_factor(
                scattering_vector(reference_index, DEFAULT_WAVELENGTH_M, DEFAULT_ANGLE_DEG), 100e-9
            )[0]
        )
        population = self.population
        per_particle = (population.masses_kg / reference_mass) ** 2 * population.form_factors
        mean_intensity = float(np.sum(population.number_weights * per_particle))
        return float(
            calibration_cps
            * (self.contrast / reference_contrast) ** 2
            * (concentration_per_ml / 1e8)
            * mean_intensity
            / reference_form
        )
