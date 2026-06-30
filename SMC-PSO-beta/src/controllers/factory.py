#=====================================================================================
#============================ src/controllers/factory.py =============================
#=====================================================================================

"""Controller factory (beta).

Clean, beta-native adapter that builds the four flat SMC monoliths ported in
M5 slices 1-4 (``ClassicalSMC``, ``SuperTwistingSMC``, ``AdaptiveSMC``,
``HybridAdaptiveSTASMC``). It provides the public surface the active code base
imports from ``src.controllers.factory``:

  * ``SMCType`` enum + ``SMCConfig`` lightweight config
  * registry helpers (``CONTROLLER_REGISTRY``, ``canonicalize_controller_type``,
    ``get_controller_info``, ``list_available_controllers``,
    ``get_default_gains``, ``get_gain_bounds``, ``validate_controller_type``,
    ``get_expected_gain_count``)
  * gain validation (``ValidationResult``, ``validate_controller_gains``,
    ``validate_smc_gains``, ``validate_state_vector``,
    ``validate_control_output``)
  * construction (``create_controller``, ``SMCFactory``)
  * PSO surface (``create_smc_for_pso``, ``create_pso_controller_factory``,
    ``get_gain_bounds_for_pso``, ``PSOControllerWrapper``)
  * convenience (``create_all_smc_controllers``, ``get_all_gain_bounds``)

Deliberate adaptations vs the source ``factory/`` package (see APPLY.md):
  * The source registry/base instantiated the *modular twin* controllers via
    typed config objects; those twins were dropped in M5. This factory
    kwargs-instantiates the kept FLAT monoliths instead, following the per-type
    constructor contracts documented below.
  * No ``src.core`` / plant imports (Trap B): ``PSOControllerWrapper`` never
    auto-builds ``DIPDynamics``; it uses only a ``dynamics_model`` already
    attached to the controller (or ``None``). Plant coupling returns in a later
    milestone.
  * Dropped from scope: modular-twin coupling, ``legacy_factory`` sprawl,
    thread-lock machinery, ``conditional_hybrid``, MPC, ``fallback_configs``.

Two controller interfaces coexist (unification deferred, see
``src/controllers/__init__.py``): the abstract ``ControllerInterface`` in
``base.py`` exposes ``compute_control(state, reference=None) -> float`` whereas
the four monoliths expose ``compute_control(state, state_vars, history) ->
<structured output>``. This factory targets the monolith interface; it does NOT
force the monoliths to inherit ``ControllerInterface``.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

from .classical_smc import ClassicalSMC
from .sta_smc import SuperTwistingSMC
from .adaptive_smc import AdaptiveSMC
from .hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC

logger = logging.getLogger(__name__)

__all__ = [
    "SMCType",
    "SMCConfig",
    "SMCFactory",
    "CONTROLLER_REGISTRY",
    "CONTROLLER_ALIASES",
    "canonicalize_controller_type",
    "get_controller_info",
    "list_available_controllers",
    "get_default_gains",
    "get_gain_bounds",
    "validate_controller_type",
    "get_expected_gain_count",
    "ValidationResult",
    "validate_controller_gains",
    "validate_smc_gains",
    "validate_state_vector",
    "validate_control_output",
    "create_controller",
    "create_smc_for_pso",
    "create_pso_controller_factory",
    "get_gain_bounds_for_pso",
    "PSOControllerWrapper",
    "create_all_smc_controllers",
    "get_all_gain_bounds",
]


#=====================================================================================
# SMC type + lightweight config
#=====================================================================================

class SMCType(Enum):
    """Canonical SMC controller types (values match registry keys)."""

    CLASSICAL = "classical_smc"
    ADAPTIVE = "adaptive_smc"
    SUPER_TWISTING = "sta_smc"
    HYBRID = "hybrid_adaptive_sta_smc"


class SMCConfig:
    """Lightweight PSO/config container.

    Mirrors the source ``SMCConfig(gains, max_force=150.0, dt=0.001, **kwargs)``
    contract. Extra keyword arguments are retained in ``params`` and as
    attributes so per-type construction can read overrides.
    """

    def __init__(self, gains: Sequence[float], max_force: float = 150.0,
                 dt: float = 0.001, **kwargs: Any) -> None:
        self.gains = list(gains) if gains is not None else []
        self.max_force = max_force
        self.dt = dt
        self.params: Dict[str, Any] = dict(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


#=====================================================================================
# Registry
#=====================================================================================

CONTROLLER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "classical_smc": {
        "default_gains": [20.0, 15.0, 12.0, 8.0, 35.0, 5.0],
        "gain_count": 6,
        "gain_structure": "[k1, k2, lambda1, lambda2, K, kd]",
        "description": "Classical sliding mode controller with boundary layer",
        "supports_dynamics": True,
        "required_params": ["gains", "max_force", "boundary_layer"],
        "gain_bounds": [(1.0, 50.0), (1.0, 50.0), (1.0, 30.0), (1.0, 30.0), (5.0, 100.0), (0.1, 20.0)],
        "category": "classical",
        "complexity": "medium",
    },
    "sta_smc": {
        "default_gains": [25.0, 15.0, 20.0, 12.0, 8.0, 6.0],
        "gain_count": 6,
        "gain_structure": "[K1, K2, k1, k2, lambda1, lambda2]",
        "description": "Super-twisting sliding mode controller",
        "supports_dynamics": True,
        "required_params": ["gains", "dt"],
        "gain_bounds": [(3.0, 100.0), (2.0, 50.0), (2.0, 50.0), (2.0, 50.0), (1.0, 40.0), (1.0, 40.0)],
        "category": "advanced",
        "complexity": "high",
    },
    "adaptive_smc": {
        "default_gains": [25.0, 18.0, 15.0, 10.0, 4.0],
        "gain_count": 5,
        "gain_structure": "[k1, k2, lambda1, lambda2, gamma]",
        "description": "Adaptive sliding mode controller with parameter estimation",
        "supports_dynamics": True,
        "required_params": ["gains", "dt", "max_force", "leak_rate", "adapt_rate_limit",
                            "K_min", "K_max", "smooth_switch", "boundary_layer", "dead_zone"],
        "gain_bounds": [(2.0, 60.0), (2.0, 60.0), (2.0, 40.0), (2.0, 40.0), (0.5, 15.0)],
        "category": "adaptive",
        "complexity": "high",
    },
    "hybrid_adaptive_sta_smc": {
        "default_gains": [18.0, 12.0, 10.0, 8.0],
        "gain_count": 4,
        "gain_structure": "[c1, lambda1, c2, lambda2]",
        "description": "Hybrid adaptive super-twisting sliding mode controller",
        "supports_dynamics": False,
        "required_params": ["gains", "dt", "max_force", "k1_init", "k2_init",
                            "gamma1", "gamma2", "dead_zone"],
        "gain_bounds": [(2.0, 30.0), (2.0, 30.0), (1.0, 20.0), (1.0, 20.0)],
        "category": "hybrid",
        "complexity": "very_high",
    },
}

CONTROLLER_ALIASES: Dict[str, str] = {
    "classic_smc": "classical_smc",
    "smc_classical": "classical_smc",
    "smc_v1": "classical_smc",
    "super_twisting": "sta_smc",
    "sta": "sta_smc",
    "adaptive": "adaptive_smc",
    "hybrid": "hybrid_adaptive_sta_smc",
    "hybrid_sta": "hybrid_adaptive_sta_smc",
}


def canonicalize_controller_type(name: Any) -> str:
    """Normalise a controller name/enum to its canonical registry key."""
    if hasattr(name, "value"):
        name = name.value
    key = str(name).strip().lower().replace("-", "_").replace(" ", "_")
    return CONTROLLER_ALIASES.get(key, key)


def get_controller_info(controller_type: Any) -> Dict[str, Any]:
    """Return a copy of the registry metadata for a controller type."""
    canonical = canonicalize_controller_type(controller_type)
    if canonical not in CONTROLLER_REGISTRY:
        available = sorted(CONTROLLER_REGISTRY.keys())
        raise ValueError(f"Unknown controller type '{controller_type}'. Available: {available}")
    info = dict(CONTROLLER_REGISTRY[canonical])
    info["name"] = canonical
    return info


def list_available_controllers() -> List[str]:
    """Return the sorted list of registered controller types."""
    return sorted(CONTROLLER_REGISTRY.keys())


def get_default_gains(controller_type: Any) -> List[float]:
    """Return a copy of the default gains for a controller type."""
    return list(get_controller_info(controller_type)["default_gains"])


def get_gain_bounds(controller_type: Any) -> List[Tuple[float, float]]:
    """Return a copy of the (lower, upper) gain bounds for a controller type."""
    return list(get_controller_info(controller_type)["gain_bounds"])


def validate_controller_type(controller_type: Any) -> bool:
    """Return True if the controller type (or alias) is registered."""
    try:
        return canonicalize_controller_type(controller_type) in CONTROLLER_REGISTRY
    except Exception:
        return False


def get_expected_gain_count(smc_type: Any) -> int:
    """Return the expected number of gains for a controller type."""
    return int(get_controller_info(smc_type)["gain_count"])


#=====================================================================================
# Gain validation
#=====================================================================================

class ValidationResult:
    """Structured validation result mirroring the source validation API."""

    def __init__(self) -> None:
        self.valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.info.append(message)

    def has_issues(self) -> bool:
        return bool(self.errors) or bool(self.warnings)

    def get_summary(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        return (f"{status} (errors={len(self.errors)}, "
                f"warnings={len(self.warnings)}, info={len(self.info)})")

    def __bool__(self) -> bool:
        return self.valid

    def __str__(self) -> str:
        parts = [self.get_summary()]
        for e in self.errors:
            parts.append(f"  ERROR: {e}")
        for w in self.warnings:
            parts.append(f"  WARNING: {w}")
        for i in self.info:
            parts.append(f"  INFO: {i}")
        return "\n".join(parts)


def _coerce_float_list(gains: Any) -> Optional[List[float]]:
    """Best-effort conversion of gains to a list of floats; None on failure."""
    try:
        if hasattr(gains, "tolist"):
            gains = gains.tolist()
        return [float(g) for g in gains]
    except Exception:
        return None


def _validate_classical(gains: List[float], result: ValidationResult) -> None:
    k1, k2, lam1, lam2, K, kd = gains
    if K <= 0:
        result.add_error("Classical SMC requires switching gain K > 0")
    if kd < 0:
        result.add_error("Classical SMC requires derivative gain kd >= 0")
    for name, value in (("k1", k1), ("k2", k2), ("lambda1", lam1), ("lambda2", lam2)):
        if value <= 0:
            result.add_error(f"Classical SMC requires sliding-surface gain {name} > 0")


def _validate_sta(gains: List[float], result: ValidationResult) -> None:
    K1, K2 = gains[0], gains[1]
    if K1 <= K2 or K2 <= 0:
        result.add_error("Super-twisting stability requires K1 > K2 > 0")
        return
    for name, value in zip(("k1", "k2", "lambda1", "lambda2"), gains[2:]):
        if value <= 0:
            result.add_error(f"Super-twisting requires surface gain {name} > 0")


def _validate_adaptive(gains: List[float], result: ValidationResult) -> None:
    k1, k2, lam1, lam2, gamma = gains
    if gamma <= 0:
        result.add_error("Adaptive SMC requires adaptation rate gamma > 0")
    for name, value in (("k1", k1), ("k2", k2), ("lambda1", lam1), ("lambda2", lam2)):
        if value <= 0:
            result.add_error(f"Adaptive SMC requires sliding-surface gain {name} > 0")


def _validate_hybrid(gains: List[float], result: ValidationResult) -> None:
    c1, lam1, c2, lam2 = gains
    for name, value in (("c1", c1), ("lambda1", lam1), ("c2", c2), ("lambda2", lam2)):
        if value <= 0:
            result.add_error(f"Hybrid SMC requires surface gain {name} > 0")


_PER_TYPE_VALIDATORS: Dict[str, Callable[[List[float], ValidationResult], None]] = {
    "classical_smc": _validate_classical,
    "sta_smc": _validate_sta,
    "adaptive_smc": _validate_adaptive,
    "hybrid_adaptive_sta_smc": _validate_hybrid,
}


def validate_controller_gains(gains: Any, controller_type: Any,
                              check_bounds: bool = True,
                              check_stability: bool = True) -> ValidationResult:
    """Validate a gain vector for a controller type.

    Always checks count, numeric/finite, and per-type stability constraints
    (e.g. STA requires ``K1 > K2 > 0``). Bounds membership is reported as
    warnings only when ``check_bounds`` is True.
    """
    result = ValidationResult()
    try:
        info = get_controller_info(controller_type)
    except ValueError as exc:
        result.add_error(str(exc))
        return result

    canonical = info["name"]
    result.metadata["controller_type"] = canonical

    coerced = _coerce_float_list(gains)
    if coerced is None:
        result.add_error("Gains must be numeric")
        return result

    expected = int(info["gain_count"])
    if len(coerced) != expected:
        result.add_error(f"{canonical} expects {expected} gains, got {len(coerced)}")
        return result

    if not all(np.isfinite(coerced)):
        result.add_error("Gains must all be finite")
        return result

    if check_stability and canonical in _PER_TYPE_VALIDATORS:
        _PER_TYPE_VALIDATORS[canonical](coerced, result)
    elif canonical == "sta_smc":
        # STA K1>K2>0 is a hard feasibility constraint, enforced even when
        # the optional stability checks are skipped.
        _validate_sta(coerced, result)
    else:
        if any(g <= 0 for g in coerced):
            result.add_error("All SMC gains must be positive")

    if check_bounds:
        for idx, (value, (low, high)) in enumerate(zip(coerced, info["gain_bounds"])):
            if value < low or value > high:
                result.add_warning(
                    f"gain[{idx}]={value:g} outside recommended bounds [{low:g}, {high:g}]")

    return result


def validate_smc_gains(smc_type: Any, gains: Any) -> bool:
    """Boolean gain check used by PSO: correct count + positive finite values."""
    try:
        info = get_controller_info(smc_type)
    except ValueError:
        return False
    coerced = _coerce_float_list(gains)
    if coerced is None:
        return False
    if len(coerced) != int(info["gain_count"]):
        return False
    if not all(np.isfinite(coerced)):
        return False
    return all(g > 0 for g in coerced)


def validate_state_vector(state: Any, expected_dim: int = 6) -> ValidationResult:
    """Validate a DIP state vector (default 6 dimensions)."""
    result = ValidationResult()
    try:
        arr = np.asarray(state, dtype=float)
    except Exception:
        result.add_error("State vector must be numeric")
        return result
    if arr.ndim != 1:
        result.add_error("State vector must be one-dimensional")
        return result
    if arr.shape[0] != expected_dim:
        result.add_error(f"State vector must have {expected_dim} elements, got {arr.shape[0]}")
    if not np.all(np.isfinite(arr)):
        result.add_error("State vector must be finite")
    return result


def validate_control_output(control: Any, max_force: float = 150.0) -> ValidationResult:
    """Validate a scalar control output is finite and within saturation."""
    result = ValidationResult()
    try:
        value = float(np.asarray(control).flatten()[0]) if hasattr(control, "__len__") else float(control)
    except Exception:
        result.add_error("Control output must be a finite scalar")
        return result
    if not np.isfinite(value):
        result.add_error("Control output must be finite")
        return result
    if abs(value) > abs(max_force) + 1e-9:
        result.add_warning(f"Control output {value:g} exceeds max_force {max_force:g}")
    result.metadata["value"] = value
    return result


#=====================================================================================
# Per-type instantiation
#=====================================================================================

_PARAM_KEYS = frozenset({
    "max_force", "dt", "boundary_layer", "damping_gain", "switch_method",
    "regularization", "leak_rate", "adapt_rate_limit", "K_min", "K_max",
    "smooth_switch", "dead_zone", "K_init", "alpha", "k1_init", "k2_init",
    "gamma1", "gamma2", "sat_soft_width", "dynamics_model",
})


def _instantiate_controller(canonical_type: str, gains: List[float],
                            params: Dict[str, Any]):
    """Construct a flat monolith with only signature-valid kwargs per type."""
    p = params
    if canonical_type == "classical_smc":
        return ClassicalSMC(
            gains=gains,
            max_force=p.get("max_force", 150.0),
            boundary_layer=p.get("boundary_layer", 0.02),
            dynamics_model=p.get("dynamics_model"),
            regularization=p.get("regularization", 1e-10),
            switch_method=p.get("switch_method", "tanh"),
        )
    if canonical_type == "sta_smc":
        return SuperTwistingSMC(
            gains=gains,
            dt=p.get("dt", 0.001),
            max_force=p.get("max_force", 150.0),
            damping_gain=p.get("damping_gain", 0.0),
            boundary_layer=p.get("boundary_layer", 0.01),
            dynamics_model=p.get("dynamics_model"),
            switch_method=p.get("switch_method", "linear"),
        )
    if canonical_type == "adaptive_smc":
        return AdaptiveSMC(
            gains=gains,
            dt=p.get("dt", 0.001),
            max_force=p.get("max_force", 150.0),
            leak_rate=p.get("leak_rate", 0.01),
            adapt_rate_limit=p.get("adapt_rate_limit", 10.0),
            K_min=p.get("K_min", 0.1),
            K_max=p.get("K_max", 100.0),
            smooth_switch=p.get("smooth_switch", True),
            boundary_layer=p.get("boundary_layer", 0.01),
            dead_zone=p.get("dead_zone", 0.05),
            K_init=p.get("K_init", 10.0),
            alpha=p.get("alpha", 0.5),
        )
    if canonical_type == "hybrid_adaptive_sta_smc":
        return HybridAdaptiveSTASMC(
            gains=gains,
            dt=p.get("dt", 0.001),
            max_force=p.get("max_force", 150.0),
            k1_init=p.get("k1_init", 4.0),
            k2_init=p.get("k2_init", 0.4),
            gamma1=p.get("gamma1", 0.1),
            gamma2=p.get("gamma2", 0.05),
            dead_zone=p.get("dead_zone", 0.05),
            sat_soft_width=p.get("sat_soft_width", 0.35),
            dynamics_model=p.get("dynamics_model"),
        )
    raise ValueError(f"Cannot instantiate unknown controller type '{canonical_type}'")


def _cfg_to_dict(cfg: Any) -> Dict[str, Any]:
    """Extract a flat dict of params/gains from a config-like object."""
    if cfg is None:
        return {}
    if isinstance(cfg, dict):
        return dict(cfg)
    if hasattr(cfg, "model_dump"):
        try:
            return {k: v for k, v in cfg.model_dump(exclude_none=True).items()}
        except Exception:
            pass
    out: Dict[str, Any] = {}
    for key in list(_PARAM_KEYS) + ["gains"]:
        value = getattr(cfg, key, None)
        if value is not None:
            out[key] = value
    return out


def _resolve_from_config(config: Any, canonical: str) -> Tuple[Dict[str, Any], Optional[List[float]]]:
    """Resolve (params, gains) from a top-level or controller-specific config."""
    if config is None:
        return {}, None
    ctrl_cfg = None
    controllers = getattr(config, "controllers", None)
    if controllers is not None:
        try:
            ctrl_cfg = controllers[canonical]
        except Exception:
            ctrl_cfg = getattr(controllers, canonical, None)
    if ctrl_cfg is None:
        ctrl_cfg = config
    flat = _cfg_to_dict(ctrl_cfg)
    raw_gains = flat.pop("gains", None)
    gains = _coerce_float_list(raw_gains) if raw_gains is not None else None
    params = {k: v for k, v in flat.items() if k in _PARAM_KEYS}
    return params, gains


#=====================================================================================
# Construction
#=====================================================================================

def create_controller(controller_type: Any, config: Any = None,
                       gains: Optional[Sequence[float]] = None):
    """Create a controller instance (primary active-call-site entry point).

    Resolution order for gains: explicit ``gains`` > config-provided gains >
    registry default. Gains are validated (count + per-type feasibility,
    including STA ``K1 > K2 > 0``) before construction.
    """
    canonical = canonicalize_controller_type(controller_type)
    if canonical not in CONTROLLER_REGISTRY:
        available = list_available_controllers()
        raise ValueError(f"Unknown controller type '{controller_type}'. Available: {available}")

    params, cfg_gains = _resolve_from_config(config, canonical)
    resolved = gains if gains is not None else cfg_gains
    if resolved is None:
        resolved = get_default_gains(canonical)
    resolved = _coerce_float_list(resolved)
    if resolved is None:
        raise ValueError(f"Gains for '{canonical}' must be numeric")

    check = validate_controller_gains(resolved, canonical, check_bounds=False, check_stability=False)
    if not check.valid:
        raise ValueError(f"Invalid gains for '{canonical}': {check.errors}")

    params.setdefault("max_force", 150.0)
    params.setdefault("dt", 0.001)
    return _instantiate_controller(canonical, resolved, params)


class SMCFactory:
    """Static factory facade over :func:`create_controller`."""

    @staticmethod
    def create_controller(smc_type: Any, config: SMCConfig):
        canonical = canonicalize_controller_type(smc_type)
        if canonical not in CONTROLLER_REGISTRY:
            available = list_available_controllers()
            raise ValueError(f"Unknown controller type '{smc_type}'. Available: {available}")
        gains = _coerce_float_list(getattr(config, "gains", None))
        if gains is None:
            raise ValueError("SMCConfig.gains must be numeric")
        params = dict(getattr(config, "params", {}) or {})
        params.setdefault("max_force", getattr(config, "max_force", 150.0))
        params.setdefault("dt", getattr(config, "dt", 0.001))
        check = validate_controller_gains(gains, canonical, check_bounds=False, check_stability=False)
        if not check.valid:
            raise ValueError(f"Invalid gains for '{canonical}': {check.errors}")
        return _instantiate_controller(canonical, gains, params)

    @staticmethod
    def list_available_controllers() -> List[str]:
        return list_available_controllers()

    @staticmethod
    def create_from_gains(smc_type: Any, gains: Sequence[float], **kwargs: Any):
        return SMCFactory.create_controller(
            smc_type, SMCConfig(gains=list(gains), **kwargs))


#=====================================================================================
# PSO surface
#=====================================================================================

class PSOControllerWrapper:
    """Adapt a flat monolith to the scalar-array interface PSO expects.

    BETA ADAPTATION: unlike the source wrapper this never auto-constructs a
    ``DIPDynamics`` plant (Trap B; plant not yet ported). It seeds the
    monolith's ``initialize_state``/``initialize_history`` each call and
    extracts the control from the structured output's first field.
    """

    def __init__(self, controller: Any, n_gains: int, controller_type: str) -> None:
        self.controller = controller
        self.n_gains = int(n_gains)
        self.controller_type = controller_type
        self.max_force = float(getattr(controller, "max_force", 150.0))
        self.dynamics_model = getattr(controller, "dynamics_model", None)

    def validate_gains(self, particles: Any) -> np.ndarray:
        """Vectorised per-particle gain validation -> boolean mask."""
        arr = np.asarray(particles, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        mask = np.ones(arr.shape[0], dtype=bool)
        for i in range(arr.shape[0]):
            mask[i] = validate_smc_gains(self.controller_type, arr[i])
        return mask

    @staticmethod
    def _extract_control(result: Any) -> float:
        u = getattr(result, "u", None)
        if u is None:
            if isinstance(result, dict) and "u" in result:
                u = result["u"]
            elif isinstance(result, (tuple, list)) and len(result) > 0:
                u = result[0]
            else:
                u = result
        arr = np.asarray(u, dtype=float).flatten()
        return float(arr[0]) if arr.size else 0.0

    def compute_control(self, state: Any) -> np.ndarray:
        """Return a length-1 saturated control array for a single state."""
        try:
            state = np.asarray(state, dtype=float)
            state_vars = (self.controller.initialize_state()
                          if hasattr(self.controller, "initialize_state") else ())
            history = (self.controller.initialize_history()
                       if hasattr(self.controller, "initialize_history") else {})
            result = self.controller.compute_control(state, state_vars, history)
            u = self._extract_control(result)
            if not np.isfinite(u):
                u = 0.0
            return np.array([float(np.clip(u, -self.max_force, self.max_force))], dtype=float)
        except Exception as exc:  # pragma: no cover - defensive for PSO sweeps
            logger.debug("PSOControllerWrapper.compute_control failed: %s", exc)
            return np.array([0.0], dtype=float)


def create_smc_for_pso(smc_type: Any, gains: Sequence[float],
                       plant_config_or_model: Any = None, **kwargs: Any) -> PSOControllerWrapper:
    """Build a PSO-ready controller wrapper for a gain vector."""
    extra = {k: v for k, v in kwargs.items() if k not in ("max_force", "dt")}
    config = SMCConfig(
        gains=list(gains),
        max_force=kwargs.get("max_force", 150.0),
        dt=kwargs.get("dt", 0.001),
        **extra,
    )
    # Only attach an explicit dynamics model; never auto-build a plant (Trap B).
    if (plant_config_or_model is not None and "dynamics_model" not in kwargs
            and hasattr(plant_config_or_model, "compute_dynamics")):
        config.params["dynamics_model"] = plant_config_or_model
        setattr(config, "dynamics_model", plant_config_or_model)
    controller = SMCFactory.create_controller(smc_type, config)
    canonical = canonicalize_controller_type(smc_type)
    expected = get_expected_gain_count(canonical)
    return PSOControllerWrapper(controller, expected, canonical)


def create_pso_controller_factory(smc_type: Any, plant_config: Any = None,
                                  **kwargs: Any) -> Callable[[Sequence[float]], PSOControllerWrapper]:
    """Return a gains->wrapper factory carrying PSO metadata attributes."""
    canonical = canonicalize_controller_type(smc_type)

    def controller_factory(gains: Sequence[float]) -> PSOControllerWrapper:
        return create_smc_for_pso(smc_type, gains, plant_config, **kwargs)

    controller_factory.n_gains = get_expected_gain_count(canonical)
    controller_factory.controller_type = canonical
    controller_factory.max_force = kwargs.get("max_force", 150.0)
    return controller_factory


def get_gain_bounds_for_pso(controller_type: Any) -> Tuple[List[float], List[float]]:
    """Return ``(lower, upper)`` PSO bound lists for a controller type."""
    bounds = get_gain_bounds(controller_type)
    lower = [float(low) for low, _ in bounds]
    upper = [float(high) for _, high in bounds]
    return lower, upper


#=====================================================================================
# Convenience
#=====================================================================================

def create_all_smc_controllers(gains_map: Optional[Dict[str, Sequence[float]]] = None,
                               **kwargs: Any) -> Dict[str, Any]:
    """Create one controller per registered type (default or supplied gains)."""
    gains_map = gains_map or {}
    out: Dict[str, Any] = {}
    for canonical in list_available_controllers():
        out[canonical] = create_controller(
            canonical, gains=gains_map.get(canonical), **({} if not kwargs else {"config": kwargs}))
    return out


def get_all_gain_bounds() -> Dict[str, Tuple[List[float], List[float]]]:
    """Return ``(lower, upper)`` PSO bounds for every registered type."""
    return {canonical: get_gain_bounds_for_pso(canonical)
            for canonical in list_available_controllers()}
