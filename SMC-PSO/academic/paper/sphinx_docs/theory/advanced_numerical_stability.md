# Advanced Numerical Stability Guide **guide to numerical stability, robustness, and error mitigation in the DIP-SMC-PSO framework.**

## Table of Contents - [Overview](#overview)

- [Common Numerical Issues](#common-numerical-issues)
- [Matrix Conditioning](#matrix-conditioning)
- [Regularization Techniques](#regularization-techniques)
- [Adaptive Parameter Tuning](#adaptive-parameter-tuning)
- [Error Analysis](#error-analysis)
- [Implementation Patterns](#implementation-patterns)
- [Validation and Testing](#validation-and-testing)
- [Best Practices](#best-practices)

## Overview ### Why Numerical Stability Matters In control systems and optimization, numerical instability can cause: - **Simulation divergence** - States explode to infinity

- **Matrix singularity** - `LinAlgError: Singular matrix`
- **Chattering** - High-frequency oscillations in control
- **Optimization failure** - PSO unable to converge
- **Incorrect results** - Silent errors that pass validation ### Affected Components | Component | Numerical Challenge | Impact |
|-----------|-------------------|--------|
| **Dynamics computation** | Matrix inversion, eigenvalues | Simulation crashes |
| **SMC controllers** | Division by zero, saturation | Chattering, instability |
| **PSO optimization** | Fitness landscape ill-conditioning | Poor convergence |
| **Adaptive controllers** | Parameter drift, numerical drift | Unstable adaptation |
| **Integration (RK4)** | Stiff equations, step size | Accuracy loss |

## Common Numerical Issues ### 1. Matrix Singularity **Problem:** Mass matrix `M(θ)` becomes ill-conditioned or singular. **Symptoms:**

```python
LinAlgError: Singular matrix
RuntimeError: Matrix is singular to working precision
``` **Root Causes:**

- Pendulum angles near singular configurations (θ ≈ 0, π)
- High condition number: `cond(M) > 1e12`
- Accumulation of floating-point errors **Example:**
```python
# Problematic code
M_inv = np.linalg.inv(M) # May fail if M is singular
acceleration = M_inv @ forces
``` ### 2. Division by Zero **Problem:** Sliding surface `s` approaches zero, causing division by zero in control law. **Symptoms:**

```python
RuntimeWarning: divide by zero encountered in true_divide
RuntimeWarning: invalid value encountered in multiply
``` **Root Causes:**

```python
# Classical SMC control law
u = -K * sign(s) / |s| # Division by |s| when s ≈ 0
``` ### 3. Floating-Point Overflow **Problem:** State variables or controls grow unbounded. **Symptoms:**

```python
RuntimeWarning: overflow encountered in double_scalars
inf or nan values in simulation results
``` **Root Causes:**

- Unbounded feedback gains
- No saturation limits on control
- Improper initial conditions ### 4. Chattering **Problem:** High-frequency switching in sliding mode control. **Symptoms:**
- Control force oscillates rapidly (>100 Hz)
- Large control effort with minimal state improvement
- Numerical instability in discrete-time implementation **Root Causes:**
```python
# Pure sign function causes chattering
u = -K * np.sign(s) # Discontinuous, causes chattering # Better: boundary layer
u = -K * np.tanh(s / boundary_layer) # Smooth approximation
```

---

## Matrix Conditioning ### Understanding Condition Numbers The **condition number** `κ(M)` measures sensitivity to errors: ```python

import numpy as np M = np.array([[1, 1], [1, 1.0001]])
kappa = np.linalg.cond(M)
print(f"Condition number: {kappa:.2e}")
# Output: Condition number: 4.00e+04 (ill-conditioned)

``` **Interpretation:**
- `κ = 1`: Perfectly conditioned (ideal)
- `κ < 100`: Well-conditioned
- `100 < κ < 1e6`: Moderately ill-conditioned
- `κ > 1e6`: Severely ill-conditioned (expect issues)
- `κ → ∞`: Singular matrix (inversion fails) ### Monitoring Condition Numbers ```python
class DynamicsWithMonitoring: def __init__(self, config, condition_threshold=1e8): self.condition_threshold = condition_threshold self.conditioning_history = [] def compute_dynamics(self, state): M = self.mass_matrix(state) kappa = np.linalg.cond(M) self.conditioning_history.append(kappa) if kappa > self.condition_threshold: print(f"Warning: High condition number {kappa:.2e}") # Use robust inversion M_inv = self.robust_inverse(M, kappa) return M_inv def robust_inverse(self, M, kappa): if kappa < 1e6: # Standard inversion is safe return np.linalg.inv(M) else: # Use regularized pseudo-inverse return self.regularized_inverse(M)
``` ### Causes of Ill-Conditioning 1. **Geometric singularities**: Pendulum configurations where `M` loses rank

2. **Small masses**: Very small `m1` or `m2` relative to `m_cart`
3. **Numerical cancellation**: Subtracting nearly equal large numbers
4. **Accumulation of errors**: Long simulations without re-orthogonalization

---

## Regularization Techniques ### 1. Tikhonov Regularization **Add small diagonal term to stabilize inversion:** ```python

def regularized_inverse(self, M, lambda_reg=1e-10): """ Compute regularized inverse: (M + λI)^-1 Parameters ---------- M : np.ndarray Matrix to invert lambda_reg : float Regularization parameter (default: 1e-10) Returns ------- M_reg_inv : np.ndarray Regularized inverse """ n = M.shape[0] M_reg = M + lambda_reg * np.eye(n) return np.linalg.inv(M_reg)
``` **Adaptive regularization:**
```python

def adaptive_regularization(self, M, base_lambda=1e-12): """Adjust regularization based on condition number.""" kappa = np.linalg.cond(M) if kappa < 1e6: lambda_reg = base_lambda elif kappa < 1e9: lambda_reg = base_lambda * (kappa / 1e6) else: lambda_reg = base_lambda * 1e3 # Strong regularization return self.regularized_inverse(M, lambda_reg)
``` ### 2. SVD-Based Pseudo-Inverse **More robust than direct inversion:** ```python
def svd_pseudo_inverse(self, M, rcond=1e-10): """ Compute pseudo-inverse using SVD with threshold. Parameters ---------- M : np.ndarray Matrix to invert rcond : float Cutoff for small singular values (default: 1e-10) Returns ------- M_pinv : np.ndarray Moore-Penrose pseudo-inverse """ U, s, Vt = np.linalg.svd(M, full_matrices=False) # Threshold small singular values s_inv = np.where(s > rcond * s[0], 1 / s, 0) # Reconstruct inverse return (Vt.T @ np.diag(s_inv) @ U.T)
``` **Benefits:**

- Handles near-singular matrices gracefully
- No `LinAlgError` exceptions
- Controllable accuracy via `rcond` ### 3. Iterative Refinement **Improve solution accuracy through iteration:** ```python
def iterative_inverse(self, M, x0=None, max_iter=5): """ Iteratively refine matrix inversion. Solves M * x = b more accurately by: 1. Initial solve: x_0 = M^-1 * b 2. Residual: r = b - M * x_0 3. Correction: x_1 = x_0 + M^-1 * r 4. Repeat until convergence """ if x0 is None: # Initial approximation M_inv_approx = np.linalg.inv(M + 1e-8 * np.eye(M.shape[0])) else: M_inv_approx = x0 for i in range(max_iter): # Compute residual R = np.eye(M.shape[0]) - M @ M_inv_approx # Check convergence if np.linalg.norm(R, 'fro') < 1e-12: break # Refine approximation M_inv_approx = M_inv_approx + M_inv_approx @ R return M_inv_approx
```

---

## Adaptive Parameter Tuning ### 1. Boundary Layer Adaptation **Dynamically adjust boundary layer to reduce chattering:** ```python
class AdaptiveBoundaryLayer: def __init__(self, initial_delta=0.3, min_delta=0.01, max_delta=1.0): self.delta = initial_delta self.min_delta = min_delta self.max_delta = max_delta self.chattering_threshold = 10.0 # Control rate threshold def update(self, control_history, dt): """ Adapt boundary layer based on chattering detection. Parameters ---------- control_history : list Recent control values (last 50 time steps) dt : float Time step Returns ------- delta : float Updated boundary layer thickness """ if len(control_history) < 10: return self.delta # Compute control rate (derivative approximation) control_rate = np.abs(np.diff(control_history[-10:])) / dt # Detect chattering if np.mean(control_rate) > self.chattering_threshold: # Increase boundary layer self.delta = min(self.delta * 1.1, self.max_delta) else: # Decrease boundary layer for better tracking self.delta = max(self.delta * 0.99, self.min_delta) return self.delta
``` ### 2. Adaptive Gain Scheduling **Adjust controller gains based on system state:** ```python

class AdaptiveGainScheduler: def __init__(self, nominal_gains, gain_bounds): self.nominal_gains = np.array(nominal_gains) self.gains = self.nominal_gains.copy() self.gain_bounds = gain_bounds # (lower, upper) tuples def update_gains(self, state, tracking_error): """ Adjust gains based on tracking performance. Parameters ---------- state : np.ndarray Current state [x, dx, θ1, dθ1, θ2, dθ2] tracking_error : float Magnitude of tracking error Returns ------- gains : np.ndarray Updated controller gains """ # Increase gains if error is large if tracking_error > 0.1: scaling_factor = 1.05 elif tracking_error < 0.01: # Decrease gains to reduce control effort scaling_factor = 0.98 else: scaling_factor = 1.0 # Apply bounds self.gains *= scaling_factor for i, (lower, upper) in enumerate(self.gain_bounds): self.gains[i] = np.clip(self.gains[i], lower, upper) return self.gains
``` ### 3. Adaptive Step Size (Integration) **Adjust time step dynamically for accuracy:** ```python
class AdaptiveRK4: def __init__(self, base_dt=0.01, min_dt=1e-4, max_dt=0.1, tol=1e-6): self.dt = base_dt self.min_dt = min_dt self.max_dt = max_dt self.tolerance = tol def step(self, f, t, y): """ Adaptive RK4 step with error estimation. Uses Richardson extrapolation to estimate error and adjust step size. """ # Full step y_full = self.rk4_step(f, t, y, self.dt) # Two half steps y_half1 = self.rk4_step(f, t, y, self.dt / 2) y_half2 = self.rk4_step(f, t + self.dt / 2, y_half1, self.dt / 2) # Error estimate (Richardson extrapolation) error = np.linalg.norm(y_full - y_half2) / 15.0 # O(h^5) accuracy # Adjust step size if error < self.tolerance / 10: self.dt = min(self.dt * 1.5, self.max_dt) elif error > self.tolerance: self.dt = max(self.dt * 0.5, self.min_dt) # Accept half-step result (more accurate) return t + self.dt, y_half2, error def rk4_step(self, f, t, y, dt): """Standard RK4 step.""" k1 = f(t, y) k2 = f(t + dt / 2, y + dt * k1 / 2) k3 = f(t + dt / 2, y + dt * k2 / 2) k4 = f(t + dt, y + dt * k3) return y + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
```

---

## Error Analysis ### 1. Truncation Error **From finite difference and integration schemes:** ```python

def estimate_truncation_error(state_history, dt): """ Estimate local truncation error using Richardson extrapolation. For RK4: LTE ~ O(dt^5) """ # Compare solution at dt and dt/2 # (Requires re-running simulation with half step size) pass # Implementation depends on simulation setup
``` ### 2. Round-Off Error **Accumulation of floating-point errors:** ```python
def monitor_roundoff_error(): """ Check for catastrophic cancellation. Example: Computing (1 + 1e-16) - 1 may give 0 instead of 1e-16 """ # Use Kahan summation for long sums def kahan_sum(values): total = 0.0 compensation = 0.0 for value in values: y = value - compensation t = total + y compensation = (t - total) - y total = t return total
``` ### 3. Lyapunov Stability Validation **Verify theoretical stability numerically:** ```python

def validate_lyapunov_stability(state_history, V_func): """ Check Lyapunov function V(x) is decreasing. Parameters ---------- state_history : np.ndarray State trajectory (N, 6) V_func : callable Lyapunov candidate function Returns ------- is_stable : bool True if V decreases monotonically """ V_values = [V_func(state) for state in state_history] # Check for monotonic decrease dV = np.diff(V_values) violations = np.sum(dV > 0) if violations == 0: return True, "Lyapunov stability confirmed" else: pct = 100 * violations / len(dV) return False, f"Stability violated in {pct:.1f}% of steps"
```

---

## Implementation Patterns ### Pattern 1: Defensive Matrix Operations ```python
class RobustLinearAlgebra: """Wrapper for numerically stable linear algebra operations.""" @staticmethod def safe_inverse(M, method='auto', rcond=1e-10, reg_lambda=1e-10): """ Robust matrix inversion with automatic method selection. Parameters ---------- M : np.ndarray Matrix to invert method : str 'auto', 'svd', 'regularized', 'standard' rcond : float Threshold for SVD reg_lambda : float Regularization parameter Returns ------- M_inv : np.ndarray Inverse matrix Raises ------ LinAlgError If matrix is too ill-conditioned even with regularization """ kappa = np.linalg.cond(M) if method == 'auto': if kappa < 1e6: method = 'standard' elif kappa < 1e12: method = 'regularized' else: method = 'svd' try: if method == 'standard': return np.linalg.inv(M) elif method == 'regularized': M_reg = M + reg_lambda * np.eye(M.shape[0]) return np.linalg.inv(M_reg) elif method == 'svd': return np.linalg.pinv(M, rcond=rcond) except np.linalg.LinAlgError as e: raise LinAlgError( f"Matrix inversion failed (κ={kappa:.2e}): {e}" ) @staticmethod def safe_solve(A, b, method='auto'): """Robust linear system solve: Ax = b.""" kappa = np.linalg.cond(A) if method == 'auto': if kappa < 1e6: return np.linalg.solve(A, b) else: return np.linalg.lstsq(A, b, rcond=None)[0] elif method == 'lstsq': return np.linalg.lstsq(A, b, rcond=None)[0] elif method == 'standard': return np.linalg.solve(A, b)
``` ### Pattern 2: Saturation with Smooth Transitions ```python

def smooth_saturation(x, x_min, x_max, smoothness=0.1): """ Smooth saturation function using tanh. Parameters ---------- x : float or np.ndarray Input value(s) x_min, x_max : float Saturation limits smoothness : float Transition smoothness (0.01 = sharp, 1.0 = smooth) Returns ------- x_sat : float or np.ndarray Saturated value(s) with smooth transitions """ # Map to [-1, 1] x_normalized = 2 * (x - x_min) / (x_max - x_min) - 1 # Smooth saturation x_sat_normalized = np.tanh(x_normalized / smoothness) # Map back to [x_min, x_max] return (x_sat_normalized + 1) * (x_max - x_min) / 2 + x_min
``` ### Pattern 3: Numerical Derivative with Noise Rejection ```python
class NumericalDerivative: """Robust numerical differentiation with noise filtering.""" def __init__(self, window_size=5): self.window_size = window_size self.history = [] def compute(self, value, dt): """ Compute derivative using Savitzky-Golay filter. More robust than simple finite difference. """ self.history.append(value) if len(self.history) > self.window_size: self.history.pop(0) if len(self.history) < 3: return 0.0 # Not enough data # Fit quadratic polynomial to recent values t = np.arange(len(self.history)) * dt coeffs = np.polyfit(t, self.history, deg=2) # Derivative is linear term return coeffs[1]
```

---

## Validation and Testing ### Test 1: Matrix Conditioning ```python

# tests/test_numerical_stability/test_matrix_conditioning.py def test_mass_matrix_conditioning(): """Verify mass matrix remains well-conditioned.""" dynamics = SimplifiedDynamics(config) # Test various configurations test_configs = [ np.array([0, 0, 0.1, 0, 0.1, 0]), # Small angles np.array([0, 0, np.pi/4, 0, np.pi/4, 0]), # 45 degrees np.array([0, 0, np.pi/2, 0, np.pi/2, 0]), # 90 degrees (potential singularity) ] for state in test_configs: M = dynamics.mass_matrix(state) kappa = np.linalg.cond(M) assert kappa < 1e8, f"Ill-conditioned mass matrix: κ = {kappa:.2e}" assert np.all(np.linalg.eigvals(M) > 0), "Mass matrix not positive definite"

``` ### Test 2: Chattering Detection ```python
def test_no_chattering(): """Verify controller doesn't chatter.""" controller = ClassicalSMC(gains=[...], boundary_layer=0.3) sim = SimulationRunner(controller, dynamics, config) result = sim.run() # Compute control rate control_rate = np.abs(np.diff(result.controls)) / config.simulation.dt # Chattering threshold: max rate < 50 N/s max_rate = np.max(control_rate) assert max_rate < 50, f"Chattering detected: max rate = {max_rate:.1f} N/s"
``` ### Test 3: Long-Term Stability ```python

def test_long_term_stability(): """Verify no numerical drift over long simulations.""" controller = AdaptiveSMC(gains=[...]) config.simulation.duration = 300.0 # 5 minutes sim = SimulationRunner(controller, dynamics, config) result = sim.run() # Check for overflow or NaN assert np.all(np.isfinite(result.states)), "Numerical instability: NaN or Inf" # Check final error final_error = np.linalg.norm(result.states[-1, [0, 2, 4]]) # Position and angles assert final_error < 0.1, f"Steady-state error too large: {final_error:.4f}"
```

---

## Best Practices ### 1. Input Validation ```python
def validate_state(state): """Ensure state vector is numerically sound.""" if not np.all(np.isfinite(state)): raise ValueError(f"Invalid state: {state}") # Check physical bounds x, dx, theta1, dtheta1, theta2, dtheta2 = state if abs(x) > 10: raise ValueError(f"Cart position out of bounds: {x:.2f} m") if abs(dx) > 50: raise ValueError(f"Cart velocity out of bounds: {dx:.2f} m/s")
``` ### 2. Graceful Degradation ```python

try: M_inv = np.linalg.inv(M)
except np.linalg.LinAlgError: # Fall back to regularized inverse M_inv = np.linalg.pinv(M, rcond=1e-8) warnings.warn("Mass matrix ill-conditioned, using pseudo-inverse")
``` ### 3. Logging and Monitoring ```python
class NumericalHealthMonitor: """Monitor numerical health during simulation.""" def __init__(self): self.warnings = [] def check(self, state, control, M_condition): if M_condition > 1e10: self.warnings.append(f"High conditioning: κ={M_condition:.2e}") if abs(control) > 200: self.warnings.append(f"Large control: {control:.1f} N") if np.any(np.abs(state) > 100): self.warnings.append("State values very large") def report(self): if self.warnings: print(f"⚠️ {len(self.warnings)} numerical warnings:") for w in self.warnings[:5]: # Show first 5 print(f" - {w}")
``` ### 4. Configuration Validation ```python

def validate_simulation_config(config): """Ensure config parameters are numerically safe.""" assert 0 < config.simulation.dt < 0.1, "Time step must be in (0, 0.1)" assert config.simulation.duration < 1000, "Duration too long for stability" # Check controller bounds if hasattr(config.controller, 'max_force'): assert config.controller.max_force < 500, "Max force unrealistically high"
```

---

## References - Golub, G. H., & Van Loan, C. F. (2013). *Matrix Computations* (4th ed.). Johns Hopkins University Press.
- Trefethen, L. N., & Bau III, D. (1997). *Numerical Linear Algebra*. SIAM.
- Higham, N. J. (2002). *Accuracy and Stability of Numerical Algorithms* (2nd ed.). SIAM.
- Slotine, J.-J. E., & Li, W. (1991). *Applied Nonlinear Control*. Prentice Hall. (Chattering reduction)

---

**Last Updated:** 2025-10-09
**Maintainer:** DIP-SMC-PSO Team
