#=====================================================================================
#============================ src/controllers/__init__.py ============================
#=====================================================================================
"""Controllers package (beta).

M5 Slice 1: classical SMC ported (flat `classical_smc.py`).
M5 Slice 2: super-twisting SMC ported (flat `sta_smc.py`, class `SuperTwistingSMC`).
M5 Slice 3: adaptive SMC ported (flat `adaptive_smc.py`, from source
`smc/adaptive_smc.py`, class `AdaptiveSMC`).
M5 Slice 4: hybrid adaptive super-twisting SMC ported (flat
`hybrid_adaptive_sta_smc.py`, class `HybridAdaptiveSTASMC`; modular twin
`smc/algorithms/hybrid/*` dropped, its HybridSMCConfig deferred to S5).
M5 Slice 5: clean beta-native controller factory landed (flat `factory.py`).
This __init__ is now widened to re-export the factory surface used by the
active call sites (simulate.py, streamlit_app.py, src/optimization/*).

base.py (M4 S1) provides the abstract ControllerInterface + shared
validators/saturate.

NOTE - two controller interfaces coexist (unification DEFERRED):
  * `ControllerInterface` (base.py): `compute_control(state, reference=None)
    -> float`, plus `reset()`, `step()`, `parameters`.
  * the four flat monoliths: `compute_control(state, state_vars, history) ->
    <structured *Output>`, plus `initialize_state()`, `initialize_history()`,
    `reset()`.
The M5 factory targets the monolith interface and deliberately does NOT force
the monoliths to inherit `ControllerInterface`. Unifying the two interfaces
(and reconciling the Trap A state-ordering boundary between controllers and the
yet-to-be-ported plant) is tracked as a later-milestone task.
"""
from .base import (
    ControllerInterface,
    require_positive,
    require_in_range,
    saturate,
)
from .classical_smc import ClassicalSMC
from .sta_smc import SuperTwistingSMC
from .adaptive_smc import AdaptiveSMC
from .hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC
from .factory import (
    SMCType,
    SMCConfig,
    SMCFactory,
    CONTROLLER_REGISTRY,
    CONTROLLER_ALIASES,
    canonicalize_controller_type,
    get_controller_info,
    list_available_controllers,
    get_default_gains,
    get_gain_bounds,
    validate_controller_type,
    get_expected_gain_count,
    ValidationResult,
    validate_controller_gains,
    validate_smc_gains,
    validate_state_vector,
    validate_control_output,
    create_controller,
    create_smc_for_pso,
    create_pso_controller_factory,
    get_gain_bounds_for_pso,
    PSOControllerWrapper,
    create_all_smc_controllers,
    get_all_gain_bounds,
)

__all__ = [
    # base interface + shared helpers
    "ControllerInterface",
    "require_positive",
    "require_in_range",
    "saturate",
    # flat monoliths
    "ClassicalSMC",
    "SuperTwistingSMC",
    "AdaptiveSMC",
    "HybridAdaptiveSTASMC",
    # factory: types + config
    "SMCType",
    "SMCConfig",
    "SMCFactory",
    # factory: registry
    "CONTROLLER_REGISTRY",
    "CONTROLLER_ALIASES",
    "canonicalize_controller_type",
    "get_controller_info",
    "list_available_controllers",
    "get_default_gains",
    "get_gain_bounds",
    "validate_controller_type",
    "get_expected_gain_count",
    # factory: validation
    "ValidationResult",
    "validate_controller_gains",
    "validate_smc_gains",
    "validate_state_vector",
    "validate_control_output",
    # factory: construction + PSO surface
    "create_controller",
    "create_smc_for_pso",
    "create_pso_controller_factory",
    "get_gain_bounds_for_pso",
    "PSOControllerWrapper",
    "create_all_smc_controllers",
    "get_all_gain_bounds",
]
