# Control Primitives Reference **Double-Inverted Pendulum Sliding Mode Control**

**Reference for Control Utilities and Primitives**

---

## Table of Contents 1. [Overview](#overview)

2. [Saturation Functions](#saturation-functions)
3. [Control Output Structures](#control-output-structures)
4. [Parameter Validation](#parameter-validation)
5. [Numerical Stability](#numerical-stability)
6. [Usage Patterns](#usage-patterns)
7. [Best Practices](#best-practices)

---

## 1. Overview ### 1.1 Purpose Control primitives provide foundational utilities for implementing robust sliding mode controllers: - **Saturation Functions**: Continuous approximations of sign function for chattering reduction

- **Control Outputs**: Structured return types for controller interfaces
- **Parameter Validation**: Type-safe parameter checking for stability
- **Numerical Stability**: Safe mathematical operations with epsilon protection ### 1.2 Module Organization ```
src/utils/
├── control/
│ ├── saturation.py # Saturation and smoothing functions
│ └── __init__.py
├── types/
│ ├── control_outputs.py # Structured output types
│ └── __init__.py
├── validation/
│ ├── parameter_validators.py # Parameter checking
│ └── __init__.py
└── numerical_stability/ ├── safe_operations.py # Numerically stable math └── __init__.py
```

---

## 2. Saturation Functions ### 2.1 Core Saturation Function **Location:** `src/utils/control/saturation.py` ```python
# example-metadata:
# runnable: false def saturate( sigma: Union[float, np.ndarray], epsilon: float, method: Literal["tanh", "linear"] = "tanh", slope: float = 3.0
) -> Union[float, np.ndarray]: """Continuous approximation of sign(sigma) within a boundary layer. Args: sigma: Sliding surface value(s) epsilon: Boundary-layer half-width (must be > 0) method: "tanh" (default) or "linear" slope: Slope parameter for tanh switching (default: 3.0) Returns: Continuous switching signal """
``` **Mathematical Foundation:** **Tanh Method (Recommended):**

```
sat(σ) = tanh(σ / (ε · slope)) where:
- ε: Boundary layer width
- slope: Transition smoothness (lower = smoother)
- Range: sat(σ) ∈ [-1, 1]
``` **Linear Method (Piecewise):**

```
sat(σ) = clip(σ/ε, -1, 1) = { -1 if σ < -ε σ/ε if -ε ≤ σ ≤ ε 1 if σ > ε
}
``` **Usage Example:** ```python

from src.utils.control import saturate # Classical SMC control law
sigma = lambda1 * theta1 + lambda2 * theta2 + k1 * dtheta1 + k2 * dtheta2
u_switch = -K * saturate(sigma, epsilon=0.01, method='tanh', slope=3.0)
u_damping = -kd * saturate(sigma, epsilon=0.01, method='tanh', slope=3.0)
u = u_switch + u_damping
``` **Slope Parameter Tuning:** | Slope Value | Transition | Chattering | Tracking Accuracy |
|-------------|------------|------------|-------------------|
| 1.0 - 2.0 | Very smooth | Minimal | Moderate |
| 3.0 (default) | Balanced | Low | Good |
| 5.0 - 10.0 | Steep | Higher | | **Design Note (Issue #12 Fix):**
- Original implementation used implicit steep slope (≈10), behaving like discontinuous sign function
- Enhanced version uses configurable slope (default: 3.0) for better chattering reduction
- Lower slope values provide gentler transitions at cost of slightly reduced tracking accuracy ### 2.2 Smooth Sign Function ```python
def smooth_sign( x: Union[float, np.ndarray], epsilon: float = 0.01
) -> Union[float, np.ndarray]: """Smooth approximation of the sign function using tanh. Convenience wrapper for saturate() with tanh method. """
``` **Mathematical Definition:**

```
smooth_sign(x) = tanh(x/ε) Limits:
- smooth_sign(x) → 1 as x → +∞
- smooth_sign(x) → -1 as x → -∞
- smooth_sign(0) = 0
``` **Usage:** ```python

from src.utils.control import smooth_sign # Continuous sign approximation
sigma = compute_sliding_surface(state)
switch_signal = -K * smooth_sign(sigma, epsilon=0.02)
``` ### 2.3 Dead Zone Function ```python
# example-metadata:
# runnable: false def dead_zone( x: Union[float, np.ndarray], threshold: float
) -> Union[float, np.ndarray]: """Apply dead zone to input signal. Args: x: Input signal threshold: Dead zone threshold (must be positive) Returns: Signal with dead zone applied """
``` **Mathematical Definition:**

```
dead_zone(x, τ) = { 0 if |x| ≤ τ x - τ·sign(x) if |x| > τ
} where τ is the dead zone threshold.
``` **Purpose:**

- **Adaptive SMC**: Freeze gain adaptation inside dead zone to prevent drift
- **Integral Control**: Prevent integral windup near equilibrium
- **Chattering Reduction**: Disable switching inside small neighborhood **Usage Example (Adaptive SMC):** ```python
from src.utils.control import dead_zone # Adaptive gain update with dead zone
sigma = compute_sliding_surface(state) if abs(sigma) <= self.dead_zone: dK = 0.0 # Freeze adaptation
else: sigma_active = dead_zone(sigma, self.dead_zone) dK = self.gamma * abs(sigma_active) - self.leak_rate * (K - K_init)
```

---

## 3. Control Output Structures **Location:** `src/utils/types/control_outputs.py` ### 3.1 Overview All controllers return **NamedTuple** instances instead of bare tuples for: - **Type safety**: Explicit attribute names prevent misuse
- **Backwards compatibility**: NamedTuple inherits from tuple
- **Documentation**: Clear contracts between caller and callee
- **IDE support**: Autocomplete and type checking ### 3.2 Classical SMC Output ```python
# example-metadata:
# runnable: false class ClassicalSMCOutput(NamedTuple): """Return type for ClassicalSMC.compute_control(). Attributes: u: Saturated control input (N) state: Internal controller state (empty tuple for stateless) history: History dictionary for debugging/plotting """ u: float state: Tuple[Any, ...] history: Dict[str, Any]
``` **Usage:** ```python

from src.controllers.smc.classic_smc import ClassicalSMC controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5], max_force=100, boundary_layer=0.01)
result = controller.compute_control(state, (), {}) # Access via attributes
control_input = result.u
controller_state = result.state
debug_info = result.history # Backwards-compatible tuple unpacking
u, state, history = result
``` ### 3.3 Adaptive SMC Output ```python
# example-metadata:
# runnable: false class AdaptiveSMCOutput(NamedTuple): """Return type for AdaptiveSMC.compute_control(). Attributes: u: Saturated control input (N) state: Updated adaptation states (e.g., K_adaptive) history: History dictionary sigma: Current sliding surface value """ u: float state: Tuple[float, ...] history: Dict[str, Any] sigma: float
``` **Key Feature:** Exposes `sigma` to monitor sliding mode convergence without re-computation. **Usage:** ```python

from src.controllers.adaptive_smc import AdaptiveSMC controller = AdaptiveSMC(gains=[25, 18, 15, 10, 4], dt=0.01, max_force=100)
result = controller.compute_control(state, (), {}) # Monitor sliding surface convergence
if abs(result.sigma) < 0.01: print("Reached sliding surface")
``` ### 3.4 Super-Twisting SMC Output ```python
# example-metadata:
# runnable: false class STAOutput(NamedTuple): """Return type for SuperTwistingSMC.compute_control(). Attributes: u: Bounded control input (N) state: Auxiliary integrator states (z, sigma) history: History dictionary """ u: float state: Tuple[float, ...] history: Dict[str, Any]
``` **State Management:** ```python

from src.controllers.sta_smc import SuperTwistingSMC controller = SuperTwistingSMC(gains=[25, 15, 20, 12, 8, 6], dt=0.01, max_force=100) # Initialize state
z_prev, sigma_prev = 0.0, 0.0 for t, state in simulation_loop: result = controller.compute_control(state, (z_prev, sigma_prev), {}) u = result.u z_prev, sigma_prev = result.state # Update auxiliary states
``` ### 3.5 Hybrid Adaptive-STA SMC Output ```python
# example-metadata:
# runnable: false class HybridSTAOutput(NamedTuple): """Return type for HybridAdaptiveSTASMC.compute_control(). Attributes: u: Saturated control input (N) state: Adaptive gains and integral state (k1, k2, u_int) history: History dictionary sigma: Current sliding surface value """ u: float state: Tuple[float, ...] history: Dict[str, Any] sigma: float
``` **Usage:** ```python

from src.controllers.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC controller = HybridAdaptiveSTASMC( gains=[18, 12, 10, 8], dt=0.01, max_force=100, k1_init=5.0, k2_init=3.0
) # Initialize adaptive state
k1, k2, u_int = controller.k1_init, controller.k2_init, 0.0 for t, state in simulation_loop: result = controller.compute_control(state, (k1, k2, u_int), {}) u = result.u k1, k2, u_int = result.state # Update adaptive gains
```

---

## 4. Parameter Validation **Location:** `src/utils/validation/parameter_validators.py` ### 4.1 Positive Parameter Validation ```python
# example-metadata:
# runnable: false def require_positive( value: Union[float, int, None], name: str, *, allow_zero: bool = False
) -> float: """Validate that a numeric value is positive (or non-negative). Args: value: The numeric quantity to validate name: Parameter name (used in error message) allow_zero: When True, value of exactly zero is allowed Returns: Validated value cast to float Raises: ValueError: If value is None, not finite, or not positive """
``` **Usage:** ```python

from src.utils.validation import require_positive class ClassicalSMC: def __init__(self, gains, max_force, boundary_layer): # Validate stability-critical parameters self.max_force = require_positive(max_force, "max_force") self.boundary_layer = require_positive(boundary_layer, "boundary_layer") # Validate gains for i, gain in enumerate(gains): gains[i] = require_positive(gain, f"gains[{i}]", allow_zero=False)
``` **Benefits:**
- **Early error detection**: Fail fast with clear messages
- **Stability guarantee**: Many SMC gains must be > 0 for stability
- **Type safety**: Ensures finite numbers (rejects NaN, Inf) ### 4.2 Finite Value Validation ```python
# example-metadata:
# runnable: false def require_finite( value: Union[float, int, None], name: str
) -> float: """Validate that a value is finite. Args: value: The numeric quantity to validate name: Parameter name Returns: Validated value cast to float Raises: ValueError: If value is None, infinity, or NaN """
``` **Usage:** ```python

from src.utils.validation import require_finite def compute_control_law(state, gains): # Validate intermediate computations sigma = compute_sliding_surface(state) sigma = require_finite(sigma, "sliding_surface") u = -gains[4] * saturate(sigma, epsilon=0.01) u = require_finite(u, "control_input") return u
```

---

## 5. Numerical Stability **Location:** `src/utils/numerical_stability/safe_operations.py` ### 5.1 Safe Division ```python
# example-metadata:
# runnable: false def safe_divide( numerator: NumericType, denominator: NumericType, epsilon: float = 1e-12, fallback: float = 0.0, warn: bool = False,
) -> NumericType: """Safe division with epsilon threshold protection against zero division. Mathematical Definition: safe_divide(a, b) = a / max(|b|, ε) * sign(b) Args: numerator: Dividend (scalar or array) denominator: Divisor (scalar or array) epsilon: Minimum safe denominator magnitude (default: 1e-12) fallback: Value to return if denominator is exactly zero (default: 0.0) warn: Issue warning when epsilon protection triggers (default: False) """
``` **Usage (Classical SMC with Dynamics Model):** ```python

from src.utils.numerical_stability import safe_divide # Compute inertia matrix inverse safely
det_M = np.linalg.det(M)
inv_M = safe_divide(1.0, det_M, epsilon=1e-12, fallback=0.0) # Safe derivative computation
velocity = safe_divide(position - prev_position, dt, epsilon=1e-12)
``` ### 5.2 Safe Reciprocal ```python
def safe_reciprocal( x: NumericType, epsilon: float = 1e-12, fallback: float = 0.0, warn: bool = False,
) -> NumericType: """Safe reciprocal (1/x) with epsilon protection. Convenience wrapper for safe_divide(1.0, x). """
``` ### 5.3 Safe Square Root ```python
# example-metadata:

# runnable: false def safe_sqrt( x: NumericType, min_value: float = 1e-15, warn: bool = False,

) -> NumericType: """Safe square root with negative value protection. Mathematical Definition: safe_sqrt(x) = √(max(x, min_value)) Clips input to [min_value, ∞) before applying sqrt to prevent domain errors from numerical noise producing negative values. """
``` **Usage (Super-Twisting SMC):** ```python
from src.utils.numerical_stability import safe_sqrt # Finite-time STA control law: u = -K1 * sqrt(|σ|) * sign(σ)
u_proportional = -K1 * safe_sqrt(abs(sigma), min_value=1e-15) * smooth_sign(sigma)
``` ### 5.4 Safe Logarithm ```python

def safe_log( x: NumericType, min_value: float = 1e-15, warn: bool = False,
) -> NumericType: """Safe natural logarithm with zero/negative protection. Mathematical Definition: safe_log(x) = ln(max(x, min_value)) """
``` **Usage (Optimization):** ```python
from src.utils.numerical_stability import safe_log # PSO cost function with log penalty
cost = ise + 1000 * safe_log(1 + instability_penalty)
``` ### 5.5 Safe Exponential ```python
# example-metadata:

# runnable: false def safe_exp( x: NumericType, max_value: float = 700.0, warn: bool = False,

) -> NumericType: """Safe exponential with overflow protection. Mathematical Definition: safe_exp(x) = exp(min(x, max_value)) Clips input to (-∞, max_value] to prevent overflow. Default max_value=700 is safe for IEEE 754 double precision. """
``` ### 5.6 Safe Vector Operations **Safe Norm:** ```python
# example-metadata:
# runnable: false def safe_norm( vector: np.ndarray, ord: Optional[Union[int, float, str]] = 2, axis: Optional[int] = None, min_norm: float = 1e-15,
) -> Union[float, np.ndarray]: """Safe vector/matrix norm with zero-norm protection. Mathematical Definition: safe_norm(v) = max(||v||_p, min_norm) """
``` **Safe Normalize:** ```python
# example-metadata:

# runnable: false def safe_normalize( vector: np.ndarray, ord: Optional[Union[int, float, str]] = 2, axis: Optional[int] = None, min_norm: float = 1e-15, fallback: Optional[np.ndarray] = None,

) -> np.ndarray: """Safe vector normalization with zero-norm protection. Mathematical Definition: safe_normalize(v) = v / max(||v||, min_norm) """
``` **Usage:** ```python
from src.utils.numerical_stability import safe_norm, safe_normalize # Gradient descent with safe normalization
gradient = compute_gradient(params)
gradient_norm = safe_norm(gradient, min_norm=1e-10)
unit_gradient = safe_normalize(gradient, min_norm=1e-10) params_new = params - step_size * unit_gradient
```

---

## 6. Usage Patterns ### 6.1 Classical SMC Implementation Pattern ```python

from src.utils.control import saturate
from src.utils.types import ClassicalSMCOutput
from src.utils.validation import require_positive class ClassicalSMC: def __init__(self, gains, max_force, boundary_layer): # Parameter validation self.gains = [require_positive(g, f"gains[{i}]") for i, g in enumerate(gains)] self.max_force = require_positive(max_force, "max_force") self.boundary_layer = require_positive(boundary_layer, "boundary_layer") def compute_control(self, state, state_vars, history): # Extract state x, theta1, theta2, dx, dtheta1, dtheta2 = state # Compute sliding surface k1, k2, lam1, lam2, K, kd = self.gains sigma = lam1 * theta1 + lam2 * theta2 + k1 * dtheta1 + k2 * dtheta2 # Continuous control law with saturation u_switch = -K * saturate(sigma, self.boundary_layer, method='tanh', slope=3.0) u_damping = -kd * saturate(sigma, self.boundary_layer, method='tanh', slope=3.0) u = np.clip(u_switch + u_damping, -self.max_force, self.max_force) # Return structured output return ClassicalSMCOutput(u=u, state=(), history={})
``` ### 6.2 Adaptive SMC with Dead Zone Pattern ```python
from src.utils.control import saturate, dead_zone
from src.utils.types import AdaptiveSMCOutput
from src.utils.numerical_stability import safe_divide class AdaptiveSMC: def __init__(self, gains, dt, max_force, leak_rate, dead_zone_threshold): self.gains = gains self.dt = dt self.max_force = max_force self.leak_rate = leak_rate self.dead_zone = dead_zone_threshold self.K_init = 10.0 def compute_control(self, state, state_vars, history): K_prev = state_vars[0] if state_vars else self.K_init # Compute sliding surface k1, k2, lam1, lam2, gamma = self.gains x, theta1, theta2, dx, dtheta1, dtheta2 = state sigma = lam1 * theta1 + lam2 * theta2 + k1 * dtheta1 + k2 * dtheta2 # Adaptive gain update with dead zone if abs(sigma) <= self.dead_zone: dK = 0.0 # Freeze inside dead zone else: sigma_active = dead_zone(sigma, self.dead_zone) dK = gamma * abs(sigma_active) - self.leak_rate * (K_prev - self.K_init) K_new = K_prev + dK * self.dt K_new = np.clip(K_new, 0.1, 100.0) # Saturation # Control law u = -K_new * saturate(sigma, epsilon=0.01, method='tanh') u = np.clip(u, -self.max_force, self.max_force) return AdaptiveSMCOutput(u=u, state=(K_new,), history={}, sigma=sigma)
``` ### 6.3 Super-Twisting SMC with Safe Operations Pattern ```python

from src.utils.control import saturate, smooth_sign
from src.utils.types import STAOutput
from src.utils.numerical_stability import safe_sqrt class SuperTwistingSMC: def __init__(self, gains, dt, max_force): self.gains = gains self.dt = dt self.max_force = max_force def compute_control(self, state, state_vars, history): K1, K2, k1, k2, lam1, lam2 = self.gains z_prev, sigma_prev = state_vars if state_vars else (0.0, 0.0) # Compute sliding surface x, theta1, theta2, dx, dtheta1, dtheta2 = state sigma = lam1 * theta1 + lam2 * theta2 + k1 * dtheta1 + k2 * dtheta2 # Super-twisting algorithm with safe operations u_proportional = -K1 * safe_sqrt(abs(sigma), min_value=1e-15) * smooth_sign(sigma) z_new = z_prev - K2 * smooth_sign(sigma) * self.dt u = u_proportional + z_new # Saturation u = np.clip(u, -self.max_force, self.max_force) return STAOutput(u=u, state=(z_new, sigma), history={})
```

---

## 7. Best Practices ### 7.1 Saturation Function Selection **Use `tanh` method (default) for:**
- Production controllers requiring chattering reduction
- Systems with high-frequency measurement noise
- Applications where smooth control signals are critical **Use `linear` method only for:**
- Legacy code compatibility
- Theoretical analysis requiring explicit boundary layer
- Cases where computational efficiency is critical (tanh slightly slower) **Slope Parameter Guidelines:**
- **slope = 1.0-2.0**: Maximum smoothness, minimal chattering, reduced tracking accuracy
- **slope = 3.0 (recommended)**: Balanced performance
- **slope = 5.0-10.0**: Steeper transition, better tracking, increased chattering ### 7.2 Numerical Stability Guidelines **Always use safe operations when:**
- Dividing by dynamically computed values (e.g., velocities, determinants)
- Computing square roots of quantities that may become negative due to numerical errors
- Implementing optimization cost functions with logarithmic penalties
- Normalizing vectors that may become zero **Choose epsilon values based on:**
- **Control derivatives**: `epsilon=1e-12` (stability margin)
- **Square roots/logarithms**: `epsilon=1e-15` (numerical precision)
- **Division**: `epsilon=1e-12` (prevent instability)
- **Optimization**: `epsilon=1e-10` (convergence criteria) ### 7.3 Parameter Validation Best Practices **Validate at construction time:**
```python

def __init__(self, gains, max_force, dt): # Validate immediately - fail fast self.gains = [require_positive(g, f"gains[{i}]") for i, g in enumerate(gains)] self.max_force = require_positive(max_force, "max_force") self.dt = require_positive(dt, "dt")
``` **Validate critical intermediate values:**
```python

def compute_control(self, state): sigma = compute_sliding_surface(state) # Validate critical quantities in debug builds if __debug__: sigma = require_finite(sigma, "sliding_surface")
``` ### 7.4 Output Structure Best Practices **Use attribute access for clarity:**
```python
# Clear and self-documenting

result = controller.compute_control(state, state_vars, history)
control_input = result.u
sliding_surface = result.sigma # Adaptive/Hybrid SMC only
``` **Use tuple unpacking for backwards compatibility:**
```python
# Backwards-compatible with legacy code

u, state, history = controller.compute_control(state, state_vars, history)
``` **Access sigma directly instead of re-computing:**
```python
# Efficient - no redundant computation

result = controller.compute_control(state, state_vars, history)
if abs(result.sigma) < 0.01: print("On sliding surface") # Inefficient - re-computes sigma
result = controller.compute_control(state, state_vars, history)
sigma = recompute_sliding_surface(state) # Redundant!
```

---

## Conclusion The control primitives provide a robust foundation for implementing production-grade sliding mode controllers. Key takeaways: - **Saturation Functions**: Use `tanh` method with `slope=3.0` for balanced chattering reduction
- **Output Structures**: Prefer NamedTuple for type safety and clarity
- **Parameter Validation**: Validate early, fail fast with clear error messages
- **Numerical Stability**: Always use safe operations for division, square roots, and logarithms For implementation examples, see:
- `src/controllers/smc/classic_smc.py` - Classical SMC using saturate()
- `src/controllers/adaptive_smc.py` - Adaptive SMC using dead_zone()
- `src/controllers/sta_smc.py` - Super-Twisting SMC using safe_sqrt()
- `tests/test_utils/` - test suite for all primitives **Next Steps:**
- Review [Factory System Guide](factory_system_guide.md) for controller creation patterns
- Explore [Classical SMC Technical Guide](classical_smc_technical_guide.md) for detailed implementation
- Study [Numerical Stability Documentation](../numerical_stability/safe_operations_reference.md) for advanced safe operations

---

**Document Version:** 1.0
**Last Updated:** 2025-10-04
**Part of:** Week 2 Controllers Module Documentation
**Related:** Factory System Guide, SMC Technical Guides, Numerical Stability Reference
