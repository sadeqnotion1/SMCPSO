# plant.core.state_validation

<!-- Enhanced by Week 8 Phase 2 --> **Source:** `src\plant\core\state_validation.py` ## Module Overview State Vector Validation for Plant Dynamics. Provides validation and sanitization of system states:
- State vector format validation
- Physical bounds checking
- Numerical validity verification
- Constraint enforcement Ensures robust dynamics computation by catching invalid states early. ## Architecture Diagram ```{mermaid}
graph TD A[State x] --> B{NaN/Inf Check} B -->|Found| Z[INVALID] B -->|Pass| C{Position Bounds} C -->|Violated| Z C -->|Pass| D{Velocity Bounds} D -->|Violated| Z D -->|Pass| E{Energy Conservation} E -->|Violated| W[WARNING] E -->|Pass| V[VALID] Z --> X[Log Violation] W --> Y[Log Warning] V --> O[Return ValidationResult] X --> O Y --> O style Z fill:#f99 style W fill:#ff9 style V fill:#9f9
``` ## Enhanced Mathematical Foundation ### Physical Constraint Theory **State Space Definition:** The admissible state space $\mathcal{X}$ is defined by physical constraints: $$
\mathcal{X} = \{x \in \mathbb{R}^6 : h_i(x) \leq 0, \forall i \in \mathcal{I}\}
$$ where $h_i(x)$ are inequality constraint functions. **Constraint Types:** 1. **Position Bounds:** $|x| \leq x_{\max}$, $|\theta_i| \leq \theta_{\max}$
2. **Velocity Bounds:** $|\dot{x}| \leq v_{\max}$, $|\dot{\theta}_i| \leq \omega_{\max}$
3. **Energy Bounds:** $E(x) \leq E_{\max}$
4. **Configuration Constraints:** Joint limits, workspace boundaries ### Energy Conservation Validation **Total Energy:** $$
E(x) = T(x) + V(x) = \frac{1}{2}\dot{q}^T M(q) \dot{q} + V(q)
$$ **Numerical Drift Detection:** $$
\Delta E(t) = |E(x(t)) - E(x_0)| / E(x_0)
$$ **Acceptance Criterion:** $$
\Delta E(t) < \epsilon_{\text{tol}} \quad \text{(typical: } \epsilon_{\text{tol}} = 0.05\text{)}
$$ Violations indicate:
- Excessive integration timestep
- Numerical instability
- Non-conservative external forces ### NaN/Inf Detection **IEEE 754 Special Values:** - **NaN (Not-a-Number):** Result of undefined operations (e.g., 0/0, ∞ - ∞)
- **Inf (Infinity):** Result of overflow or division by zero **Detection Strategy:** $$
\text{is\_valid}(x) = \neg \left(\bigvee_{i=1}^{6} \text{isnan}(x_i) \lor \text{isinf}(x_i)\right)
$$ **Common Causes in DIP:** 1. Matrix inversion with near-singular $M(q)$
2. Trigonometric overflow for large angles
3. Timestep too large causing blow-up ### Runtime Verification **Temporal Logic Specification:** Safety property: "State always remains in valid region" $$
\square (x(t) \in \mathcal{X})
$$ where $\square$ is the "always" temporal operator. **Monitor Implementation:** ```python
def runtime_monitor(x, t): if not is_valid(x): raise StateValidationError(f"State violation at t={t}") if energy_drift(x) > threshold: warn(f"Energy drift detected: {energy_drift(x):.2%}")
``` ### Constraint Violation Handling **Violation Severity:** $$

\text{severity}(x) = \max_i \left(\frac{|h_i(x)|}{h_{i,\text{max}}}\right)
$$ **Response Strategy:** 1. **Minor (severity < 0.1):** Log warning, continue
2. **Moderate (0.1 ≤ severity < 0.5):** Clip state to bounds
3. **Severe (severity ≥ 0.5):** Terminate simulation, raise exception **State Clipping:** $$
x_{\text{clipped}} = \text{proj}_{\mathcal{X}}(x) = \arg\min_{y \in \mathcal{X}} \|y - x\|_2
$$ For box constraints: $$
x_{i,\text{clipped}} = \text{clip}(x_i, x_{i,\min}, x_{i,\max})
$$ ### References 1. **Betts** (2010). *Practical Methods for Optimal Control*. SIAM. Chapter 2 (Constraints).
2. **Khalil** (2002). *Nonlinear Systems* (3rd ed.). Prentice Hall. Section 4.6.
3. **Leucker & Schallhart** (2009). "A brief account of runtime verification." *J. Log. Algebr. Program.* 78(5). ## Usage Examples ### Example 1: Basic Usage Initialize and use the Core State Validation module: ```python
from src.plant.core.state_validation import *
import numpy as np # Basic initialization
# Validate state and detect violations

from src.plant.core.state_validation import StateValidator, ValidationResult validator = StateValidator()
state = np.array([0.0, 0.1, 0.05, 0.0, 0.5, 0.3]) result: ValidationResult = validator.validate(state)
if result.is_valid: print("State is physically valid")
else: print(f"Violations: {result.violations}")
``` ### Example 2: Advanced Configuration Configure with custom parameters: ```python
from src.plant.core.state_validation import ValidationConfig # Custom validation constraints
validation_config = ValidationConfig( max_position=2.0, # ±2m cart position max_angle=np.pi/2, # ±90° joint angles max_velocity=5.0, # 5 m/s cart velocity max_angular_velocity=10.0, # 10 rad/s joint velocities energy_conservation_tol=0.05 # 5% energy drift tolerance
) validator = StateValidator(validation_config)
``` ### Example 3: Error Handling Robust error handling and recovery: ```python

from src.plant.exceptions import ( NumericalInstabilityError, StateValidationError, ConfigurationError
) try: # Risky operation state_dot = dynamics.step(state, control, t) except NumericalInstabilityError as e: print(f"Numerical instability detected: {e}") # Fallback: reduce timestep, increase regularization dynamics.reset_numerical_params(stronger_regularization=True) except StateValidationError as e: print(f"Invalid state: {e}") # Fallback: clip state to valid bounds state = validator.clip_to_valid(state) except ConfigurationError as e: print(f"Configuration error: {e}") # Fallback: use default configuration config = get_default_config()
``` ### Example 4: Performance Optimization Optimize for computational efficiency: ```python
# example-metadata:
# runnable: false # Performance optimization
import cProfile
import pstats # Profile critical code path
profiler = cProfile.Profile()
profiler.enable() # ... run intensive operations ... profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10) # Top 10 time consumers
``` ### Example 5: Integration with Controllers Integrate with control systems: ```python

from src.controllers import ClassicalSMC
from src.core.simulation_runner import SimulationRunner # Create dynamics model
dynamics = SimplifiedDIPDynamics(config) # Create controller
controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01
) # Run closed-loop simulation
runner = SimulationRunner( controller=controller, dynamics=dynamics, duration=5.0, dt=0.01
) result = runner.run( initial_state=np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])
) print(f"Final state: {result.states[-1]}")
print(f"Settling time: {result.settling_time:.2f}s")
print(f"Control effort: {result.control_effort:.2f}")
``` ## Complete Source Code ```{literalinclude} ../../../src/plant/core/state_validation.py
:language: python
:linenos:
```

---

## Classes

### `StateValidationError`

**Inherits from:** `ValueError` Raised when state vector validation fails.

#### Source Code ```

{literalinclude} ../../../src/plant/core/state_validation.py

:language: python
:pyobject: StateValidationError
:linenos:
```

### `StateValidator`

**Inherits from:** `Protocol` Protocol for state validation strategies.

#### Source Code ```

{literalinclude} ../../../src/plant/core/state_validation.py
:language: python
:pyobject: StateValidator
:linenos:
``` #### Methods (2) ##### `validate_state(self, state)` Validate state vector. [View full source →](#method-statevalidator-validate_state) ##### `sanitize_state(self, state)` Sanitize and correct state vector if possible. [View full source →](#method-statevalidator-sanitize_state)

### `DIPStateValidator`

Double Inverted Pendulum state vector validation. Validates state vectors for the DIP system ensuring:

- Correct dimensionality (6-element vectors)
- Physical bounds on positions and velocities
- Numerical validity (no NaN/inf values)
- Angular wrapping and constraint enforcement #### Source Code ```{literalinclude} ../../../src/plant/core/state_validation.py
:language: python
:pyobject: DIPStateValidator
:linenos:
``` #### Methods (14) ##### `__init__(self, position_bounds, angle_bounds, velocity_bounds, angular_velocity_bounds, wrap_angles, strict_validation)` Initialize DIP state validator. [View full source →](#method-dipstatevalidator-__init__) ##### `validate_state(self, state)` Validate complete state vector. [View full source →](#method-dipstatevalidator-validate_state) ##### `sanitize_state(self, state)` Sanitize state vector to ensure validity. [View full source →](#method-dipstatevalidator-sanitize_state) ##### `get_state_info(self, state)` Get detailed information about state vector. [View full source →](#method-dipstatevalidator-get_state_info) ##### `reset_statistics(self)` Reset validation statistics. [View full source →](#method-dipstatevalidator-reset_statistics) ##### `get_statistics(self)` Get validation statistics. [View full source →](#method-dipstatevalidator-get_statistics) ##### `_check_state_structure(self, state)` Check if state has correct structure. [View full source →](#method-dipstatevalidator-_check_state_structure) ##### `_check_numerical_validity(self, state)` Check if state contains valid numerical values. [View full source →](#method-dipstatevalidator-_check_numerical_validity) ##### `_check_physical_bounds(self, state)` Check if state is within physical bounds. [View full source →](#method-dipstatevalidator-_check_physical_bounds) ##### `_fix_numerical_issues(self, state)` Fix numerical issues in state vector. [View full source →](#method-dipstatevalidator-_fix_numerical_issues) ##### `_apply_physical_bounds(self, state)` Apply physical bounds to state vector. [View full source →](#method-dipstatevalidator-_apply_physical_bounds) ##### `_wrap_angles(self, angles)` Wrap angles to [-π, π] range. [View full source →](#method-dipstatevalidator-_wrap_angles) ##### `_estimate_energy(self, state)` Estimate total system energy (rough approximation). [View full source →](#method-dipstatevalidator-_estimate_energy) ##### `_estimate_angular_momentum(self, state)` Estimate total angular momentum (rough approximation). [View full source →](#method-dipstatevalidator-_estimate_angular_momentum)

---

### `MinimalStateValidator`

Minimal state validator for performance-critical applications. Provides only essential validation with minimal overhead.

#### Source Code ```

{literalinclude} ../../../src/plant/core/state_validation.py
:language: python
:pyobject: MinimalStateValidator
:linenos:
``` #### Methods (2) ##### `validate_state(self, state)` Fast basic validation. [View full source →](#method-minimalstatevalidator-validate_state) ##### `sanitize_state(self, state)` Minimal sanitization. [View full source →](#method-minimalstatevalidator-sanitize_state)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Tuple, Optional, Protocol, Dict, Any`
- `import numpy as np`
- `import warnings`
