# Audit Report — Account 1
## SMC Algorithms + Plant/Dynamics
**Files reviewed:** 55
**Scope:** `src\controllers\smc\`, `src\core\`, `src\plant\`

---

## Critical Issues Summary

### BROKEN (6 files — must fix before anything runs correctly)

| File | Issue |
|---|---|
| `src\controllers\smc\algorithms\super_twisting\controller.py` | `_estimate_surface_derivative` called with wrong args — runtime crash |
| `src\controllers\smc\algorithms\conditional_hybrid\controller.py` | Output key mismatch with adaptive controller — silently outputs 0.0 |
| `src\controllers\smc\core\equivalent_control.py` | Disconnected from active plant API — u_eq collapses to 0.0 |
| `src\core\dynamics.py` | Numba `@njit` rejects `DIPParams` objects — hard crash in core stepping |
| `src\core\dynamics_full.py` | Inherits same Numba crash from dynamics.py |
| `src\plant\configurations\unified_config.py` | Central config factory broken — preset registry violations |

### NEEDS WORK (10 files)

| File | Issue |
|---|---|
| `src\controllers\smc\algorithms\classical\config.py` | `create_default(**kwargs)` silently drops overrides |
| `src\controllers\smc\algorithms\classical\controller.py` | State indexing conflicts with docstring — integration error risk |
| `src\controllers\smc\algorithms\adaptive\controller.py` | Non-deterministic return type breaks callers |
| `src\controllers\smc\algorithms\adaptive\parameter_estimation.py` | `CombinedEstimator` kwargs incompatible across subcomponents |
| `src\controllers\smc\algorithms\hybrid\config.py` | `from_dict` wrong signature — fails at runtime on load |
| `src\controllers\smc\algorithms\hybrid\controller.py` | Legacy facade nonfunctional for intended use |
| `src\controllers\smc\algorithms\hybrid\switching_logic.py` | Hysteresis margin config ignored — hardcoded 0.6 threshold |
| `src\controllers\smc\core\sliding_surface.py` | Missing state length check — potential index error |
| `src\controllers\smc\core\switching_functions.py` | Derivative formulas diverge from actual switching implementation |
| `src\plant\configurations\validation.py` | Strict mode not actually enforced |

### CLEAN (39 files — no issues found)

---

## Full File-by-File Report

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\classical\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports resolve and match module contents
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\classical\boundary_layer.py
- CORRECTNESS:  [PASS] boundary-layer switching and chattering metrics are internally consistent
- AI SLOP:      [PASS] no dead stubs found
- ARCHITECTURE: [PASS] wiring to SwitchingFunction is correct
- SAFETY:       [PASS] strong finite checks and divide-by-zero guards present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\classical\config.py
- CORRECTNESS:  [ISSUE] create_default(..., **kwargs) ignores kwargs, so caller overrides are silently dropped
- AI SLOP:      [ISSUE] unused kwargs parameter in factory method
- ARCHITECTURE: [PASS] class interfaces otherwise consistent
- SAFETY:       [PASS] validation coverage is strong
- VERDICT:      [NEEDS WORK]
- NOTES:        factory API is misleading and can cause misconfigured controllers

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\classical\controller.py
- CORRECTNESS:  [ISSUE] state-order docstrings conflict with implementation indexing, increasing integration error risk
- AI SLOP:      [ISSUE] mixed/contradictory state-format comments
- ARCHITECTURE: [ISSUE] depends on EquivalentControl path that is nonfunctional with current plant model interfaces
- SAFETY:       [PASS] saturation and error fallback are present
- VERDICT:      [NEEDS WORK]
- NOTES:        equivalent-control branch is effectively inactive in current stack

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\adaptive\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports match available classes
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\adaptive\adaptation_law.py
- CORRECTNESS:  [PASS] adaptation and projection logic are coherent
- AI SLOP:      [PASS] no dead code affecting behavior
- ARCHITECTURE: [PASS] interface aligns with adaptive controller usage
- SAFETY:       [PASS] clipping/bounds protections are present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\adaptive\config.py
- CORRECTNESS:  [PASS] gain/schema validation behaves as expected
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] properties align with controller expectations
- SAFETY:       [PASS] numeric checks are comprehensive
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\adaptive\controller.py
- CORRECTNESS:  [ISSUE] return-type switching on state_vars/history can unexpectedly return arrays in default calls
- AI SLOP:      [ISSUE] inconsistent state-format documentation
- ARCHITECTURE: [ISSUE] ambiguous interface mode can break callers expecting deterministic return type
- SAFETY:       [PASS] safe fallback behavior exists
- VERDICT:      [NEEDS WORK]
- NOTES:        interface contract should be made explicit and stable

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\adaptive\parameter_estimation.py
- CORRECTNESS:  [ISSUE] CombinedEstimator forwards **kwargs to ParameterIdentifier, which rejects many uncertainty-estimator args
- AI SLOP:      [ISSUE] constructor argument fan-out is not type-compatible across subcomponents
- ARCHITECTURE: [ISSUE] combined wrapper has brittle wiring
- SAFETY:       [PASS] numeric operations include basic safeguards
- VERDICT:      [NEEDS WORK]
- NOTES:        combined estimator can fail at construction for common kwargs

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\super_twisting\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are consistent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\super_twisting\config.py
- CORRECTNESS:  [PASS] STA gain constraints and parameter validation are correct
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] config API matches controller consumption
- SAFETY:       [PASS] robust validation present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\super_twisting\controller.py
- CORRECTNESS:  [FAIL] compute_control calls _estimate_surface_derivative(state, surface_value) but method accepts only state; runtime exception observed
- AI SLOP:      [ISSUE] initialized _switching component is unused
- ARCHITECTURE: [FAIL] core compute path is broken; downstream hybrid modes inherit degraded behavior
- SAFETY:       [ISSUE] silent safe-mode fallback can mask total loss of STA authority
- VERDICT:      [BROKEN]
- NOTES:        critical runtime defect in primary control path

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\super_twisting\twisting_algorithm.py
- CORRECTNESS:  [PASS] algorithm implementation is coherent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] integrates cleanly with controller config
- SAFETY:       [PASS] anti-windup and regularization handling present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\hybrid\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are valid
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\hybrid\config.py
- CORRECTNESS:  [ISSUE] from_dict calls AdaptiveSMCConfig.from_dict(..., dynamics_model) with wrong signature
- AI SLOP:      [ISSUE] deserialization path assumes inconsistent config APIs
- ARCHITECTURE: [ISSUE] mixed config constructor conventions are not normalized
- SAFETY:       [PASS] validation logic is generally strong
- VERDICT:      [NEEDS WORK]
- NOTES:        loading hybrid configs from dict can fail at runtime

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\hybrid\controller.py
- CORRECTNESS:  [ISSUE] legacy HybridSMC facade cannot instantiate required sub-configs for most modes (raises ValueError)
- AI SLOP:      [ISSUE] controller-specific key extraction expects fields not produced by source controllers
- ARCHITECTURE: [ISSUE] backward-compat wrapper is not wired to required config graph
- SAFETY:       [PASS] fallback handling avoids crashes
- VERDICT:      [NEEDS WORK]
- NOTES:        facade path is effectively nonfunctional for intended use

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\hybrid\switching_logic.py
- CORRECTNESS:  [ISSUE] hysteresis behavior ignores configured hysteresis margin and hardcodes confidence > 0.6
- AI SLOP:      [ISSUE] config parameter exists but is not used in switching gate
- ARCHITECTURE: [ISSUE] runtime behavior diverges from config contract
- SAFETY:       [PASS] conservative checks prevent frequent invalid switches
- VERDICT:      [NEEDS WORK]
- NOTES:        switching policy is partly hardcoded despite configurable API

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\conditional_hybrid\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are correct
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\conditional_hybrid\config.py
- CORRECTNESS:  [PASS] config validation for thresholds/weights is valid
- AI SLOP:      [ISSUE] unused import (Optional)
- ARCHITECTURE: [PASS] fields align with controller use
- SAFETY:       [PASS] bounds checks are present
- VERDICT:      [NEEDS WORK]
- NOTES:        minor code hygiene issue

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\conditional_hybrid\controller.py
- CORRECTNESS:  [FAIL] reads adaptive output via control_signal key, but adaptive controller returns u; with history={} this path outputs 0.0 (verified)
- AI SLOP:      [ISSUE] reset logic comments acknowledge missing true reset for adaptive baseline
- ARCHITECTURE: [FAIL] interface mismatch between conditional-hybrid and adaptive controller outputs
- SAFETY:       [ISSUE] can silently drop baseline control to zero depending on call signature
- VERDICT:      [BROKEN]
- NOTES:        critical cross-module output-key mismatch

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\algorithms\conditional_hybrid\safety_checker.py
- CORRECTNESS:  [ISSUE] equivalent-gain formula reuses lambda2 twice, likely collapsing an intended independent term
- AI SLOP:      [ISSUE] header path references regional_hybrid, inconsistent with module location
- ARCHITECTURE: [PASS] callable interface is consistent
- SAFETY:       [PASS] safety checks are explicit and compositional
- VERDICT:      [NEEDS WORK]
- NOTES:        physics formula should be re-verified against derivation

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\core\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports map correctly
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\core\equivalent_control.py
- CORRECTNESS:  [FAIL] bundled dynamics models expose compute_dynamics/DynamicsResult, not get_dynamics; u_eq path collapses to 0.0 in practice (verified)
- AI SLOP:      [ISSUE] claims model-based equivalent control but current adapter coverage misses primary model APIs
- ARCHITECTURE: [FAIL] interface contract mismatch with plant model implementations
- SAFETY:       [PASS] fails safe to zero control
- VERDICT:      [BROKEN]
- NOTES:        equivalent-control component is effectively disconnected from active plant stack

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\core\gain_validation.py
- CORRECTNESS:  [PASS] validation logic is coherent
- AI SLOP:      [PASS] no dead stubs affecting behavior
- ARCHITECTURE: [PASS] utility interfaces are consistent
- SAFETY:       [PASS] catches non-finite inputs and stability violations
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\core\sliding_surface.py
- CORRECTNESS:  [ISSUE] compute_derivative checks state_dot length but not state length before indexing
- AI SLOP:      [PASS] abstract pass blocks are expected, not dead runtime logic
- ARCHITECTURE: [PASS] interface and factory wiring are valid
- SAFETY:       [ISSUE] potential index error for malformed state input
- VERDICT:      [NEEDS WORK]
- NOTES:        add symmetric input validation in derivative path

### D:\Projects\main\code_only_lean_20260217_161712\src\controllers\smc\core\switching_functions.py
- CORRECTNESS:  [ISSUE] get_derivative formulas do not match active slope parameters used by compute for tanh/sigmoid
- AI SLOP:      [ISSUE] analysis derivative path diverges from implemented switching law
- ARCHITECTURE: [PASS] function registry and method dispatch are correct
- SAFETY:       [PASS] finite checks and saturation are in place
- VERDICT:      [NEEDS WORK]
- NOTES:        derivative APIs can mislead adaptation/analysis tools

### D:\Projects\main\code_only_lean_20260217_161712\src\core\__init__.py
- CORRECTNESS:  [PASS] compatibility exports are valid
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] legacy aliases are coherent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\core\dynamics.py
- CORRECTNESS:  [FAIL] @njit functions require typed params but accept Python objects; rhs_numba/step_* raise TypingError with DIPParams (verified)
- AI SLOP:      [ISSUE] advertised numba-optimized compatibility path is not executable as documented
- ARCHITECTURE: [ISSUE] API contract (params object) conflicts with nopython constraints
- SAFETY:       [FAIL] runtime hard failure in core dynamics stepping path
- VERDICT:      [BROKEN]
- NOTES:        critical incompatibility between function signature and JIT mode

### D:\Projects\main\code_only_lean_20260217_161712\src\core\dynamics_full.py
- CORRECTNESS:  [FAIL] re-exported step_*_numba path inherits the same TypingError failure with FullDIPParams (verified)
- AI SLOP:      [ISSUE] module-level import order issue (E402) and fragile compatibility layering
- ARCHITECTURE: [ISSUE] compatibility wrapper exposes broken lower-layer APIs
- SAFETY:       [ISSUE] failure manifests at runtime in integration functions
- VERDICT:      [BROKEN]
- NOTES:        full-dynamics compatibility stepping is not operational with current parameter objects

### D:\Projects\main\code_only_lean_20260217_161712\src\core\safety_guards.py
- CORRECTNESS:  [PASS] re-exports resolve
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compatibility intent is clear and functional
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\core\simulation_context.py
- CORRECTNESS:  [PASS] re-export is valid
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compatibility wiring is correct
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\core\simulation_runner.py
- CORRECTNESS:  [PASS] re-exports are valid
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compatibility layer is correct
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\core\vector_sim.py
- CORRECTNESS:  [PASS] exported symbols resolve
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] compatibility import path works
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\__init__.py
- CORRECTNESS:  [PASS] package exports are coherent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] model/core/config integration points are exposed correctly
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\core\__init__.py
- CORRECTNESS:  [PASS] exports are valid
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] module boundary is clean
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\core\dynamics.py
- CORRECTNESS:  [ISSUE] broad star-import compatibility module can silently provide partial API
- AI SLOP:      [ISSUE] multiple try/except ImportError: pass blocks hide missing dependencies
- ARCHITECTURE: [ISSUE] wildcard re-export strategy reduces interface determinism
- SAFETY:       [PASS] no direct numeric hazards
- VERDICT:      [NEEDS WORK]
- NOTES:        missing imports can be masked instead of surfaced

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\core\numerical_stability.py
- CORRECTNESS:  [PASS] regularization/inversion logic is internally consistent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] reusable abstractions are coherent
- SAFETY:       [PASS] strong instability detection and fallback behavior
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\core\physics_matrices.py
- CORRECTNESS:  [PASS] matrix constructions are coherent for intended model level
- AI SLOP:      [PASS] no dead logic affecting execution
- ARCHITECTURE: [PASS] interfaces integrate with model physics computers
- SAFETY:       [PASS] deterministic matrix outputs and no unsafe mutation patterns
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\core\state_validation.py
- CORRECTNESS:  [PASS] validation/sanitization workflow is correct
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] validator interfaces are consistent
- SAFETY:       [PASS] robust finite checks and bounds clipping
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\simplified\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are correct
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\simplified\config.py
- CORRECTNESS:  [PASS] parameter validation and factory presets are coherent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] config API aligns with simplified model
- SAFETY:       [PASS] strong physical and numerical bounds checks
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\simplified\dynamics.py
- CORRECTNESS:  [PASS] dynamics path and compatibility methods are coherent
- AI SLOP:      [PASS] no dead stubs affecting runtime
- ARCHITECTURE: [PASS] integrates correctly with simplified physics/config
- SAFETY:       [PASS] failure paths and validation checks are present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\simplified\physics.py
- CORRECTNESS:  [PASS] simplified RHS and energy calculations are internally consistent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] matrix/inverter integration is clean
- SAFETY:       [PASS] condition/stability checks are available
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\full\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are valid
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\full\config.py
- CORRECTNESS:  [PASS] full-model parameter schema and checks are coherent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] mapping and constructors align with model use
- SAFETY:       [PASS] strong validation for advanced numerical settings
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\full\dynamics.py
- CORRECTNESS:  [ISSUE] _rhs_core is defined twice; later definition silently overrides earlier one
- AI SLOP:      [ISSUE] duplicate method indicates merge/regeneration artifact
- ARCHITECTURE: [ISSUE] duplicate symbol weakens maintainability and auditability
- SAFETY:       [PASS] compute path itself has robust failure handling
- VERDICT:      [NEEDS WORK]
- NOTES:        duplicate method should be removed to avoid drift

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\full\physics.py
- CORRECTNESS:  [PASS] full-physics compute pipeline is coherent
- AI SLOP:      [PASS] no dead stubs impacting behavior
- ARCHITECTURE: [PASS] integrates with full dynamics/config as expected
- SAFETY:       [PASS] guarded solve path with instability exception handling
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\lowrank\__init__.py
- CORRECTNESS:  [PASS] none found
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] exports are consistent
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\lowrank\config.py
- CORRECTNESS:  [PASS] low-rank config behavior is coherent
- AI SLOP:      [PASS] no dead logic affecting runtime
- ARCHITECTURE: [PASS] aligns with low-rank dynamics and base config use
- SAFETY:       [PASS] validation covers core physical consistency
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\lowrank\dynamics.py
- CORRECTNESS:  [PASS] compute path and linearized path behave consistently
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] wiring to low-rank physics/config is correct
- SAFETY:       [PASS] validation and failure fallback are present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\models\lowrank\physics.py
- CORRECTNESS:  [PASS] simplified model equations are internally consistent
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] clear contract with low-rank dynamics
- SAFETY:       [PASS] computation validator catches non-finite/unstable derivatives
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\configurations\__init__.py
- CORRECTNESS:  [PASS] exports are valid
- AI SLOP:      [PASS] none found
- ARCHITECTURE: [PASS] namespace composition is correct
- SAFETY:       [PASS] none found
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\configurations\base_config.py
- CORRECTNESS:  [PASS] base validation and scale utilities are coherent
- AI SLOP:      [PASS] abstract pass usage is expected
- ARCHITECTURE: [PASS] base interfaces are usable by derived configs
- SAFETY:       [PASS] consistency checks are present
- VERDICT:      [CLEAN]
- NOTES:        none

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\configurations\unified_config.py
- CORRECTNESS:  [FAIL] multiple verified breakages: string create_preset_config fails, presets miss required fields, and validate_configuration assumes methods absent on registered simplified/full configs
- AI SLOP:      [FAIL] fallback controller config and preset registry contain inconsistent contract assumptions
- ARCHITECTURE: [FAIL] factory registry type contract (BaseDIPConfig) is violated by registered config classes
- SAFETY:       [ISSUE] configuration validation can silently be bypassed/misreported via incompatible config classes
- VERDICT:      [BROKEN]
- NOTES:        central configuration factory is not reliable for major code paths

### D:\Projects\main\code_only_lean_20260217_161712\src\plant\configurations\validation.py
- CORRECTNESS:  [ISSUE] strict_mode cannot escalate warnings because code catches ConfigurationWarning exceptions, but warnings are emitted via warnings.warn
- AI SLOP:      [ISSUE] warning/error control flow is inconsistent with Python warnings model
- ARCHITECTURE: [ISSUE] strict-validation contract is not actually enforced
- SAFETY:       [PASS] parameter bound checks are otherwise strong
- VERDICT:      [NEEDS WORK]
- NOTES:        strict mode behavior is currently misleading and incomplete
