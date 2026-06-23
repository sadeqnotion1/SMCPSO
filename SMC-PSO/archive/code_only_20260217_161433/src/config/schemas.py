#======================================================================================\\\
#=============================== src/config/schemas.py ================================\\\
#======================================================================================\\\

"""Configuration schemas and models for the DIP SMC PSO project."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def redact_value(value: Any) -> str:
    """Redact sensitive values for logging."""
    if isinstance(value, SecretStr):
        return "***"
    if isinstance(value, str) and any(
        keyword in str(value).lower() for keyword in ["password", "secret", "token", "key"]
    ):
        return "***"
    return str(value)

# ------------------------------------------------------------------------------
# Base strict model
# ------------------------------------------------------------------------------
class StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        populate_by_name=True,
        validate_default=True,
        validate_assignment=True,
    )

# ------------------------------------------------------------------------------
# Physics
# ------------------------------------------------------------------------------
class PhysicsConfig(StrictModel):
    cart_mass: float
    pendulum1_mass: float
    pendulum2_mass: float
    pendulum1_length: float
    pendulum2_length: float
    pendulum1_com: float
    pendulum2_com: float
    pendulum1_inertia: float
    pendulum2_inertia: float
    gravity: float
    cart_friction: float = Field(..., ge=0.0)
    joint1_friction: float = Field(..., ge=0.0)
    joint2_friction: float = Field(..., ge=0.0)
    singularity_cond_threshold: float = Field(1.0e8, ge=1e4)
    regularization: float = Field(1e-10, gt=0.0)
    det_threshold: float = Field(1e-12, ge=0.0, le=1e-3)
    # Physics effects for full dynamics model
    include_coriolis_effects: bool = Field(True)
    include_centrifugal_effects: bool = Field(True)
    include_gyroscopic_effects: bool = Field(True)

    @field_validator(
        "cart_mass", "pendulum1_mass", "pendulum2_mass",
        "pendulum1_length", "pendulum2_length",
        "pendulum1_inertia", "pendulum2_inertia",
        "pendulum1_com", "pendulum2_com",
        "gravity"
    )
    @classmethod
    def _must_be_strictly_positive(cls, v: float, info) -> float:
        if v is None or v <= 0.0:
            raise ValueError(f"{info.field_name} must be strictly positive, but got {v}")
        return v

    @model_validator(mode="after")
    def _validate_com_within_length(self) -> "PhysicsConfig":
        if self.pendulum1_com >= self.pendulum1_length:
            raise ValueError(
                f"pendulum1_com ({self.pendulum1_com}) must be less than pendulum1_length ({self.pendulum1_length})"
            )
        if self.pendulum2_com >= self.pendulum2_length:
            raise ValueError(
                f"pendulum2_com ({self.pendulum2_com}) must be less than pendulum2_length ({self.pendulum2_length})"
            )
        return self

class PhysicsUncertaintySchema(StrictModel):
    n_evals: int
    cart_mass: float
    pendulum1_mass: float
    pendulum2_mass: float
    pendulum1_length: float
    pendulum2_length: float
    pendulum1_com: float
    pendulum2_com: float
    pendulum1_inertia: float
    pendulum2_inertia: float
    gravity: float
    cart_friction: float
    joint1_friction: float
    joint2_friction: float

# ------------------------------------------------------------------------------
# Simulation
# ------------------------------------------------------------------------------
class SimulationConfig(StrictModel):
    duration: float
    dt: float = 0.01
    initial_state: Optional[List[float]] = None
    use_full_dynamics: bool = True
    sensor_latency: float = Field(0.0, ge=0.0)
    actuator_latency: float = Field(0.0, ge=0.0)
    real_time: bool = False
    raise_on_warning: bool = False

    @field_validator("dt", "duration")
    @classmethod
    def _must_be_positive(cls, v: float, info):
        if v is None or v <= 0.0:
            raise ValueError(f"{info.field_name} must be > 0")
        return v

    @model_validator(mode="after")
    def _duration_at_least_dt(self):
        if self.duration < self.dt:
            raise ValueError("simulation.duration must be >= simulation.dt")
        return self

    @field_validator("initial_state")
    @classmethod
    def _initial_state_valid(cls, v):
        if v is None:
            return v
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError("initial_state must be a non-empty list of floats")
        if not all(isinstance(x, float) for x in v):
            raise ValueError("initial_state must contain float values (no implicit casts)")
        return v

# ------------------------------------------------------------------------------
# Legacy module-level namespace (best-effort)
# ------------------------------------------------------------------------------
try:
    if "config" not in globals():
        config = SimpleNamespace(
            simulation=SimpleNamespace(
                use_full_dynamics=False,
                safety=None,
            )
        )
except Exception:
    pass

# ------------------------------------------------------------------------------
# Controllers
# ------------------------------------------------------------------------------
class _BaseControllerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gains: List[float] = Field(default_factory=list, min_length=1)

    def __iter__(self):
        for k, v in self.model_dump(exclude_unset=True).items():
            yield k, v

class ControllerConfig(_BaseControllerConfig):
    pass

class ClassicalSMCConfig(_BaseControllerConfig):
    """Configuration for Classical Sliding Mode Controller."""
    max_force: Optional[float] = Field(None, gt=0.0)
    boundary_layer: Optional[float] = Field(None, gt=0.0)
    dt: Optional[float] = Field(None, gt=0.0)
    rate_weight: Optional[float] = Field(None, ge=0.0)
    use_adaptive_boundary: Optional[bool] = None

class STASMCConfig(_BaseControllerConfig):
    """Configuration for Super-Twisting Algorithm Sliding Mode Controller."""
    max_force: Optional[float] = Field(None, gt=0.0)
    damping_gain: Optional[float] = Field(None, ge=0.0)
    dt: Optional[float] = Field(None, gt=0.0)
    boundary_layer: Optional[float] = Field(None, gt=0.0)

class AdaptiveSMCConfig(_BaseControllerConfig):
    """Configuration for Adaptive Sliding Mode Controller."""
    max_force: Optional[float] = Field(None, gt=0.0)
    leak_rate: Optional[float] = Field(None, ge=0.0)
    dead_zone: Optional[float] = Field(None, gt=0.0)
    adapt_rate_limit: Optional[float] = Field(None, gt=0.0)
    K_min: Optional[float] = Field(None, gt=0.0)
    K_max: Optional[float] = Field(None, gt=0.0)
    dt: Optional[float] = Field(None, gt=0.0)
    smooth_switch: Optional[bool] = None
    boundary_layer: Optional[float] = Field(None, gt=0.0)

    @model_validator(mode="after")
    def _validate_adaptive_bounds(self) -> "AdaptiveSMCConfig":
        if self.K_min is not None and self.K_max is not None:
            if self.K_min >= self.K_max:
                raise ValueError(f"K_min ({self.K_min}) must be less than K_max ({self.K_max})")
        return self

class SwingUpSMCConfig(_BaseControllerConfig):
    """Configuration for Swing-Up Sliding Mode Controller."""
    max_force: Optional[float] = Field(None, gt=0.0)
    stabilizing_controller: Optional[str] = None
    energy_gain: Optional[float] = Field(None, gt=0.0)
    switch_energy_factor: Optional[float] = Field(None, gt=0.0, le=1.0)
    switch_angle_tolerance: Optional[float] = Field(None, gt=0.0)
    exit_energy_factor: Optional[float] = Field(None, gt=0.0, le=1.0)
    reentry_angle_tolerance: Optional[float] = Field(None, gt=0.0)

class MPCControllerConfig(_BaseControllerConfig):
    """Configuration for Model Predictive Controller."""
    horizon: Optional[int] = Field(10, gt=0)
    q_x: Optional[float] = Field(1.0, gt=0.0)
    q_theta: Optional[float] = Field(1.0, gt=0.0)
    r_u: Optional[float] = Field(0.1, gt=0.0)
    max_force: Optional[float] = Field(None, gt=0.0)

class HybridAdaptiveSTASMCConfig(_BaseControllerConfig):
    """Configuration for Hybrid Adaptive Super-Twisting Sliding Mode Controller."""
    max_force: Optional[float] = Field(None, gt=0.0)
    dt: Optional[float] = Field(None, gt=0.0)
    k1_init: Optional[float] = Field(None, gt=0.0)
    k2_init: Optional[float] = Field(None, gt=0.0)
    gamma1: Optional[float] = Field(None, gt=0.0)
    gamma2: Optional[float] = Field(None, gt=0.0)
    gain_leak: Optional[float] = Field(None, ge=0.0)
    dead_zone: Optional[float] = Field(None, gt=0.0)
    enable_equivalent: Optional[bool] = None
    damping_gain: Optional[float] = Field(None, ge=0.0)
    adapt_rate_limit: Optional[float] = Field(None, gt=0.0)
    sat_soft_width: Optional[float] = Field(None, gt=0.0)
    cart_gain: Optional[float] = Field(None, ge=0.0)
    cart_lambda: Optional[float] = Field(None, gt=0.0)
    cart_p_gain: Optional[float] = Field(None, ge=0.0)
    cart_p_lambda: Optional[float] = Field(None, gt=0.0)

    @model_validator(mode="after")
    def _validate_hybrid_constraints(self) -> "HybridAdaptiveSTASMCConfig":
        if self.sat_soft_width is not None and self.dead_zone is not None:
            if self.sat_soft_width < self.dead_zone:
                raise ValueError(
                    f"sat_soft_width ({self.sat_soft_width}) must be >= dead_zone ({self.dead_zone})"
                )
        return self

class ConditionalHybridConfig(_BaseControllerConfig):
    """Configuration for Conditional Hybrid SMC Controller."""
    max_force: Optional[float] = Field(None, gt=0.0)
    dt: Optional[float] = Field(None, gt=0.0)
    # Safety thresholds for super-twisting activation
    angle_threshold: Optional[float] = Field(None, gt=0.0)
    surface_threshold: Optional[float] = Field(None, gt=0.0)
    B_eq_threshold: Optional[float] = Field(None, gt=0.0)
    # Blend weights (must sum to 1.0)
    w_angle: Optional[float] = Field(None, gt=0.0, le=1.0)
    w_surface: Optional[float] = Field(None, gt=0.0, le=1.0)
    w_singularity: Optional[float] = Field(None, gt=0.0, le=1.0)
    # Super-twisting gains (regional application)
    gamma1: Optional[float] = Field(None, gt=0.0)
    gamma2: Optional[float] = Field(None, gt=0.0)
    # Adaptive SMC baseline parameters
    epsilon_min: Optional[float] = Field(None, gt=0.0)
    alpha: Optional[float] = Field(None, gt=0.0)

    @model_validator(mode="after")
    def _validate_blend_weights(self) -> "ConditionalHybridConfig":
        if self.w_angle is not None and self.w_surface is not None and self.w_singularity is not None:
            weight_sum = self.w_angle + self.w_surface + self.w_singularity
            if not (0.99 <= weight_sum <= 1.01):
                raise ValueError(
                    f"Blend weights must sum to 1.0, got {weight_sum:.3f}"
                )
        return self

class PermissiveControllerConfig(_BaseControllerConfig):
    model_config = ConfigDict(extra="allow")
    unknown_params: Dict[str, Any] = Field(default_factory=dict)
    allow_unknown: bool = False

    @model_validator(mode="after")
    def _collect_unknown_params(self) -> "PermissiveControllerConfig":
        extra = getattr(self, "model_extra", None)
        if extra:
            unknown = dict(extra)
            object.__setattr__(self, "unknown_params", unknown)
            if not self.__class__.allow_unknown:
                unknown_keys = ", ".join(sorted(unknown.keys()))
                raise ValueError(
                    f"Unknown configuration keys: {unknown_keys}. "
                    "Set allow_unknown=True when calling load_config to accept unknown keys."
                )
        return self

def set_allow_unknown_config(_: bool) -> None:
    """Deprecated - use load_config(..., allow_unknown=True) instead."""
    raise RuntimeError(
        "set_allow_unknown_config() is deprecated; use load_config(..., allow_unknown=True) instead."
    )

class ControllersConfig(StrictModel):
    classical_smc: Optional[ClassicalSMCConfig] = None
    sta_smc: Optional[STASMCConfig] = None
    adaptive_smc: Optional[AdaptiveSMCConfig] = None
    swing_up_smc: Optional[SwingUpSMCConfig] = None
    mpc_controller: Optional[MPCControllerConfig] = None
    hybrid_adaptive_sta_smc: Optional[HybridAdaptiveSTASMCConfig] = None
    conditional_hybrid: Optional[ConditionalHybridConfig] = None

    def keys(self) -> List[str]:
        return [
            name for name in (
                "classical_smc", "sta_smc", "adaptive_smc",
                "swing_up_smc", "hybrid_adaptive_sta_smc", "mpc_controller",
                "conditional_hybrid",
            ) if getattr(self, name) is not None
        ]

    def __iter__(self):
        for name in self.keys():
            yield name

    def items(self):
        for name in self:
            yield (name, getattr(self, name))

    def __getitem__(self, key: str) -> Any:
        canonical = str(key).lower().strip().replace("-", "_").replace(" ", "_")
        if canonical in self.keys():
            val = getattr(self, canonical)
            if val is None:
                raise KeyError(key)
            return val
        raise KeyError(key)

# ------------------------------------------------------------------------------
# PSO
# ------------------------------------------------------------------------------
class PSOBounds(StrictModel):
    min: List[float]
    max: List[float]

class PSOBoundsWithControllers(StrictModel):
    # Default bounds for all controllers
    min: List[float]
    max: List[float]
    # Controller-specific bounds (optional)
    classical_smc: Optional[PSOBounds] = None
    sta_smc: Optional[PSOBounds] = None
    adaptive_smc: Optional[PSOBounds] = None
    hybrid_adaptive_sta_smc: Optional[PSOBounds] = None
    conditional_hybrid: Optional[PSOBounds] = None

class ScenarioDistributionConfig(StrictModel):
    """Distribution of scenario difficulty levels for robust PSO."""
    nominal_fraction: float = Field(0.2, ge=0.0, le=1.0, description="Fraction of scenarios with small perturbations")
    moderate_fraction: float = Field(0.3, ge=0.0, le=1.0, description="Fraction of scenarios with medium perturbations")
    large_fraction: float = Field(0.5, ge=0.0, le=1.0, description="Fraction of scenarios with large perturbations")

    @model_validator(mode='after')
    def validate_fractions_sum(self) -> 'ScenarioDistributionConfig':
        """Ensure fractions sum to 1.0."""
        total = self.nominal_fraction + self.moderate_fraction + self.large_fraction
        if not (0.99 <= total <= 1.01):  # Allow small floating-point tolerance
            raise ValueError(f"Scenario fractions must sum to 1.0, got {total}")
        return self

class RobustnessConfig(StrictModel):
    """Configuration for multi-scenario robust PSO optimization.

    Addresses MT-7 overfitting issue where gains trained on small perturbations
    (±0.05 rad) show 50.4x chattering degradation on realistic perturbations (±0.3 rad).

    Robust fitness: J_robust = mean(costs) + α * max(costs)
    where α = worst_case_weight (default 0.3).
    """
    enabled: bool = Field(False, description="Enable robust multi-scenario optimization")
    n_scenarios: int = Field(15, ge=3, le=100, description="Number of diverse initial conditions to evaluate")
    worst_case_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for worst-case cost (α in robust fitness)")
    scenario_distribution: ScenarioDistributionConfig = Field(
        default_factory=ScenarioDistributionConfig,
        description="Distribution of scenario difficulty levels"
    )
    nominal_range: float = Field(0.05, ge=0.0, description="Perturbation range for nominal scenarios (rad)")
    moderate_range: float = Field(0.15, ge=0.0, description="Perturbation range for moderate scenarios (rad)")
    large_range: float = Field(0.3, ge=0.0, description="Perturbation range for large scenarios (rad)")
    seed: Optional[int] = Field(None, description="Random seed for reproducible scenario generation")

    @model_validator(mode='after')
    def validate_ranges_ordering(self) -> 'RobustnessConfig':
        """Ensure nominal < moderate < large."""
        if not (self.nominal_range < self.moderate_range < self.large_range):
            raise ValueError(
                f"Ranges must satisfy nominal < moderate < large, got "
                f"{self.nominal_range} < {self.moderate_range} < {self.large_range}"
            )
        return self

class PSOConfig(StrictModel):
    n_particles: int = Field(100, ge=1)
    bounds: PSOBoundsWithControllers
    w: float = Field(0.5, ge=0.0)
    c1: float = Field(1.5, ge=0.0)
    c2: float = Field(1.5, ge=0.0)
    iters: int = Field(200, ge=1)
    w_schedule: Optional[Tuple[float, float]] = None
    velocity_clamp: Optional[Tuple[float, float]] = None
    n_processes: Optional[int] = Field(None, ge=1)
    hyper_trials: Optional[int] = None
    hyper_search: Optional[Dict[str, List[float]]] = None
    study_timeout: Optional[int] = None
    seed: Optional[int] = None
    tune: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    robustness: Optional[RobustnessConfig] = Field(
        None,
        description="Multi-scenario robust optimization settings (addresses MT-7 overfitting)"
    )

# ------------------------------------------------------------------------------
# Cost Function
# ------------------------------------------------------------------------------
class CostFunctionWeights(StrictModel):
    state_error: float = Field(50.0, ge=0.0)
    control_effort: float = Field(0.2, ge=0.0)
    control_rate: float = Field(0.1, ge=0.0)
    stability: float = Field(0.1, ge=0.0)

class CombineWeights(StrictModel):
    mean: float = Field(0.7, ge=0.0, le=1.0)
    max: float = Field(0.3, ge=0.0, le=1.0)

class CostFunctionConfig(StrictModel):
    weights: CostFunctionWeights
    baseline: Optional[Dict[str, Any]] = None  # Optional: legacy baseline normalization
    norms: Optional[Dict[str, float]] = None   # Optional: explicit normalization constants
    instability_penalty: float = Field(1000.0, ge=0.0)
    combine_weights: CombineWeights = CombineWeights()
    normalization_threshold: float = Field(1e-12, ge=0.0)

# ------------------------------------------------------------------------------
# Verification
# ------------------------------------------------------------------------------
class VerificationConfig(StrictModel):
    test_conditions: List[Dict[str, Any]]
    integrators: List[str]
    criteria: Dict[str, float]

# ------------------------------------------------------------------------------
# Sensors
# ------------------------------------------------------------------------------
class SensorsConfig(StrictModel):
    angle_noise_std: float = 0.0
    position_noise_std: float = 0.0
    quantization_angle: float = 0.0
    quantization_position: float = 0.0

# ------------------------------------------------------------------------------
# HIL
# ------------------------------------------------------------------------------
class HILConfig(StrictModel):
    plant_ip: str
    plant_port: int
    controller_ip: str
    controller_port: int
    extra_latency_ms: float = 0.0
    sensor_noise_std: float = 0.0

# ------------------------------------------------------------------------------
# FDI
# ------------------------------------------------------------------------------
class FDIConfig(StrictModel):
    enabled: bool = False
    residual_threshold: float = Field(0.5, gt=0)
    persistence_counter: int = Field(10, ge=1)
    residual_states: List[int] = Field(default_factory=lambda: [0, 1, 2])
    residual_weights: Optional[List[float]] = None
    adaptive: bool = False
    window_size: int = Field(50, ge=2)
    threshold_factor: float = Field(3.0, ge=0.0)
    cusum_enabled: bool = False
    cusum_threshold: float = Field(5.0, gt=0.0)

    @field_validator("residual_states")
    @classmethod
    def _validate_residual_states(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("residual_states must not be empty")
        if any(idx < 0 for idx in v):
            raise ValueError("residual_states must contain non-negative indices")
        if any(idx >= 6 for idx in v):
            raise ValueError(
                f"residual_states contains invalid indices {v}; valid state indices are 0-5"
            )
        return v

    @model_validator(mode="after")
    def _validate_weights_length(self) -> "FDIConfig":
        w = getattr(self, "residual_weights", None)
        if w is not None:
            if len(w) != len(self.residual_states):
                raise ValueError(
                    f"residual_weights length {len(w)} does not match residual_states length"
                )
            if any((ww is None or ww < 0.0) for ww in w):
                raise ValueError("residual_weights must contain non-negative numbers")
        return self


# ------------------------------------------------------------------------------
# Stability Monitoring (Issue #1 Resolution)
# ------------------------------------------------------------------------------
class LDRConfig(StrictModel):
    """Lyapunov Decrease Ratio monitoring configuration."""
    threshold: float = Field(0.95, ge=0.0, le=1.0)
    window_ms: float = Field(300.0, gt=0.0)
    transient_time: float = Field(1.0, ge=0.0)


class SaturationConfig(StrictModel):
    """Saturation monitoring configuration."""
    duty_threshold: float = Field(0.2, ge=0.0, le=1.0)
    rate_hit_threshold: float = Field(0.01, ge=0.0, le=1.0)
    max_continuous_ms: float = Field(200.0, gt=0.0)
    window_ms: float = Field(1000.0, gt=0.0)
    transient_time: float = Field(1.0, ge=0.0)


class ConditioningConfig(StrictModel):
    """Dynamics conditioning monitoring configuration."""
    median_threshold: float = Field(1e7, gt=0.0)
    spike_threshold: float = Field(1e9, gt=0.0)
    fallback_threshold: int = Field(3, ge=0)
    window_ms: float = Field(1000.0, gt=0.0)


class DiagnosticsConfig(StrictModel):
    """Diagnostic checklist configuration."""
    auto_classify: bool = True
    store_history: bool = True
    max_history: int = Field(1000, ge=0)


class StabilityMonitoringConfig(StrictModel):
    """Stability monitoring configuration for Issue #1 resolution."""
    enabled: bool = True
    ldr: LDRConfig = Field(default_factory=LDRConfig)
    saturation: SaturationConfig = Field(default_factory=SaturationConfig)
    conditioning: ConditioningConfig = Field(default_factory=ConditioningConfig)
    diagnostics: DiagnosticsConfig = Field(default_factory=DiagnosticsConfig)

# ------------------------------------------------------------------------------
# Fault Detection (Issue #18 Resolution - Threshold Calibration)
# ------------------------------------------------------------------------------
class FaultDetectionConfig(StrictModel):
    """Fault Detection and Isolation (FDI) configuration - Issue #18 resolution."""

    residual_threshold: float = Field(
        default=0.150,
        ge=0.0,
        description="Statistically calibrated threshold (P99 percentile)"
    )
    hysteresis_enabled: bool = Field(
        default=True,
        description="Enable hysteresis to prevent threshold oscillation"
    )
    hysteresis_upper: float = Field(
        default=0.165,
        ge=0.0,
        description="Upper bound triggers fault (threshold * 1.1)"
    )
    hysteresis_lower: float = Field(
        default=0.135,
        ge=0.0,
        description="Lower bound for recovery (threshold * 0.9)"
    )
    persistence_counter: int = Field(
        default=10,
        ge=1,
        description="Consecutive violations required to trigger fault"
    )
    adaptive: bool = Field(
        default=False,
        description="Use adaptive threshold (vs fixed)"
    )
    window_size: int = Field(
        default=50,
        ge=1,
        description="Window size for adaptive mode"
    )
    threshold_factor: float = Field(
        default=3.0,
        ge=0.0,
        description="N-sigma rule for adaptive mode"
    )

# ------------------------------------------------------------------------------
# Streamlit UI Configuration (Phase 3 Wave 3: Theme Parity)
# ------------------------------------------------------------------------------
class StreamlitConfig(StrictModel):
    """Streamlit UI configuration for theme injection and UI features."""
    enable_dip_theme: bool = Field(
        default=True,
        description="Enable design token-driven theme injection for visual consistency"
    )
    theme_version: str = Field(
        default="2.0.0",
        description="Design tokens version (v2.0.0: Phase 2 accessibility remediation)"
    )
