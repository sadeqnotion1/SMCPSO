# Sliding Surface Mathematical Properties and Stability Analysis

This document provides rigorous mathematical analysis of the sliding surface implementations and their stability properties for the double-inverted pendulum sliding mode control system.

## 1. Mathematical Foundation

### 1.1 Linear Sliding Surface Definition

For the double-inverted pendulum system, the linear sliding surface is defined as:

```
s = λ₁ė₁ + c₁e₁ + λ₂ė₂ + c₂e₂
```

Where:
- `e₁ = θ₁ - θ₁ᵈ` (joint 1 angle error)
- `e₂ = θ₂ - θ₂ᵈ` (joint 2 angle error)
- `ė₁ = θ̇₁ - θ̇₁ᵈ` (joint 1 velocity error)
- `ė₂ = θ̇₂ - θ̇₂ᵈ` (joint 2 velocity error)
- `λ₁, λ₂ > 0` (velocity coefficients)
- `c₁, c₂ > 0` (position coefficients)

For the upright equilibrium task: `θ₁ᵈ = θ₂ᵈ = 0` and `θ̇₁ᵈ = θ̇₂ᵈ = 0`.

### 1.2 Surface Derivative

The sliding surface derivative is:

```
ṡ = λ₁ë₁ + c₁ė₁ + λ₂ë₂ + c₂ė₂
ṡ = λ₁θ̈₁ + c₁θ̇₁ + λ₂θ̈₂ + c₂θ̇₂
```

This derivative is crucial for equivalent control computation and convergence analysis.

## 2. Stability Analysis

### 2.1 Hurwitz Stability Requirement

The coefficients [c₁, c₂, λ₁, λ₂] must satisfy the Hurwitz stability condition for the sliding dynamics to be stable.

For the 2×2 error dynamics system, the characteristic polynomial is:

```
P(s) = det(sI - A)
```

Where the sliding dynamics matrix A has the form:

```
A = [0   1   0   0 ]
    [-c₁ -λ₁ 0   0 ]
    [0   0   0   1 ]
    [0   0  -c₂ -λ₂]
```

**Stability Conditions:**
1. All gains must be positive: `c₁, c₂, λ₁, λ₂ > 0`
2. The poles of each 2×2 subsystem must be in the left half-plane
3. Each subsystem: `s² + λᵢs + cᵢ = 0` has roots with negative real parts

### 2.2 Convergence Analysis

Once the system reaches the sliding surface (s = 0), the error dynamics become:

```
λ₁ė₁ + c₁e₁ = 0  →  ë₁ + (λ₁/c₁)ė₁ + (1/c₁)e₁ = 0
λ₂ė₂ + c₂e₂ = 0  →  ë₂ + (λ₂/c₂)ė₂ + (1/c₂)e₂ = 0
```

These are second-order linear systems with:
- Natural frequency: `ωₙᵢ = √(1/cᵢ)`
- Damping ratio: `ζᵢ = λᵢ/(2√cᵢ)`

**Design Guidelines:**
- For critically damped response: `ζᵢ = 1` → `λᵢ = 2√cᵢ`
- For overdamped response: `ζᵢ > 1` → `λᵢ > 2√cᵢ`
- For underdamped response: `ζᵢ < 1` → `λᵢ < 2√cᵢ`

## 3. Implementation Corrections

### 3.1 Gain Validation Fix

**Problem:** Previous implementation allowed zero or negative gains, violating stability requirements.

**Solution:** Implemented strict validation in `ClassicalSMCConfig`:

```python
# example-metadata:
# runnable: false

def _validate_gains(self) -> None:
    """Validate gain vector according to SMC theory."""
    if len(self.gains) != 6:
        raise ValueError("Classical SMC requires exactly 6 gains: [k1, k2, lam1, lam2, K, kd]")

    k1, k2, lam1, lam2, K, kd = self.gains

    # Surface gains must be positive for Hurwitz stability
    if any(g <= 0 for g in [k1, k2, lam1, lam2]):
        raise ValueError("Surface gains [k1, k2, λ1, λ2] must be positive for stability")

    # Switching gain must be positive for reaching condition
    if K <= 0:
        raise ValueError("Switching gain K must be positive")

    # Derivative gain must be non-negative
    if kd < 0:
        raise ValueError("Derivative gain kd must be non-negative")
```

### 3.2 Surface Computation Consistency

**Problem:** Inconsistent surface computation could lead to control discontinuities.

**Solution:** Unified surface computation in `LinearSlidingSurface` class:

```python
# example-metadata:
# runnable: false

def compute(self, state: np.ndarray) -> float:
    """
    Compute linear sliding surface value.

    Args:
        state: [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]

    Returns:
        Sliding surface value: s = lam1*theta1_dot + k1*theta1 + lam2*theta2_dot + k2*theta2
    """
    if len(state) < 6:
        raise ValueError("State must have at least 6 elements for double-inverted pendulum")

    # Extract joint angles and velocities (reference is upright: theta=0)
    theta1 = state[2]      # Joint 1 angle error
    theta1_dot = state[3]  # Joint 1 velocity error
    theta2 = state[4]      # Joint 2 angle error
    theta2_dot = state[5]  # Joint 2 velocity error

    # Linear sliding surface: s = λ₁ė₁ + c₁e₁ + λ₂ė₂ + c₂e₂
    s = (self.lam1 * theta1_dot + self.k1 * theta1 +
         self.lam2 * theta2_dot + self.k2 * theta2)

    return float(s)
```

### 3.3 Derivative Computation Fix

**Problem:** Surface derivative computation was inconsistent or missing.

**Solution:** Explicit derivative computation method:

```python
# example-metadata:
# runnable: false

def compute_derivative(self, state: np.ndarray, state_dot: np.ndarray) -> float:
    """
    Compute sliding surface derivative ds/dt.

    Args:
        state: Current state vector
        state_dot: State derivative vector

    Returns:
        Surface derivative: ṡ = λ₁θ̈₁ + c₁θ̇₁ + λ₂θ̈₂ + c₂θ̇₂
    """
    if len(state_dot) < 6:
        raise ValueError("State derivative must have at least 6 elements")

    # Extract joint accelerations and velocities
    theta1_dot = state[3]     # Joint 1 velocity
    theta1_ddot = state_dot[3] # Joint 1 acceleration
    theta2_dot = state[5]     # Joint 2 velocity
    theta2_ddot = state_dot[5] # Joint 2 acceleration

    # Surface derivative
    s_dot = (self.lam1 * theta1_ddot + self.k1 * theta1_dot +
             self.lam2 * theta2_ddot + self.k2 * theta2_dot)

    return float(s_dot)
```

## 4. Higher-Order Sliding Surfaces

### 4.1 Super-Twisting Surface

For super-twisting and higher-order SMC, the surface can be extended to include higher-order derivatives:

```
s₁ = λ₁ė₁ + c₁e₁ + λ₂ė₂ + c₂e₂         (first-order surface)
s₂ = ṡ₁ = λ₁ë₁ + c₁ė₁ + λ₂ë₂ + c₂ė₂   (second-order surface)
```

The super-twisting algorithm operates on both s₁ and s₂ to achieve finite-time convergence without requiring explicit knowledge of the derivative.

### 4.2 Adaptive Surface Design

For adaptive SMC, the surface gains can be time-varying:

```
s = λ₁(t)ė₁ + c₁(t)e₁ + λ₂(t)ė₂ + c₂(t)e₂
```

Where the gains λᵢ(t) and cᵢ(t) are adapted based on parameter estimation algorithms to maintain stability under parametric uncertainties.

## 5. Lyapunov Stability Analysis

### 5.1 Candidate Lyapunov Function

For sliding mode control, a common Lyapunov function candidate is:

```
V = ½s²
```

### 5.2 Stability Condition

For stability, we require:

```
V̇ = sṡ ≤ -η|s|
```

Where η > 0 is the reaching law parameter. This ensures finite-time convergence to the sliding surface.

### 5.3 Reaching Law Implementation

The reaching law is implemented through the switching control:

```
u_switching = -K·sign(s)
```

Where K > η to satisfy the reaching condition. In practice, the boundary layer method replaces sign(s) with a continuous approximation.

## 6. Performance Metrics

### 6.1 Convergence Time

The time to reach the sliding surface can be estimated from:

```
t_reach ≤ |s(0)|/η
```

Where s(0) is the initial surface value and η is the reaching law parameter.

### 6.2 Tracking Error Bounds

Once on the sliding surface, the tracking error is bounded by the boundary layer thickness:

```
|eᵢ(t)| ≤ ε/min(cᵢ, λᵢ)
```

Where ε is the boundary layer thickness.

## 7. Numerical Considerations

### 7.1 Regularization

To avoid numerical issues with matrix inversion in equivalent control computation, a regularization term is added:

```
(L·M⁻¹·B + ρI)⁻¹
```

Where ρ > 0 is the regularization parameter (typically 1e-10).

### 7.2 Controllability Check

Before computing equivalent control, the controllability matrix is checked:

```
rank([B, AB, A²B, ...]) = n
```

If the system is not controllable, equivalent control is set to zero and only switching control is used.

## 8. Testing and Validation

### 8.1 Mathematical Property Tests

- **Gain Positivity**: Verify all surface gains are positive
- **Stability**: Check that characteristic polynomial has roots in left half-plane
- **Continuity**: Verify surface computation is continuous
- **Differentiability**: Check surface derivative computation

### 8.2 Numerical Validation

- **Finite Values**: Ensure surface values remain finite for all valid states
- **Consistency**: Verify surface computation is consistent across calls
- **Sensitivity**: Test robustness to small parameter changes

### 8.3 Control Performance Tests

- **Convergence**: Verify system reaches sliding surface in finite time
- **Tracking**: Check tracking error remains within theoretical bounds
- **Chattering**: Validate chattering reduction with boundary layer

## References

1. Utkin, V. I. (1992). *Sliding Modes in Control and Optimization*. Springer-Verlag.

2. Edwards, C., & Spurgeon, S. (1998). *Sliding Mode Control: Theory and Applications*. CRC Press.

3. Shtessel, Y., Edwards, C., Fridman, L., & Levant, A. (2014). *Sliding Mode Control and Observation*. Birkhäuser.

4. Khalil, H. K. (2002). *Nonlinear Systems*. Prentice Hall.

5. Levant, A. (2003). Higher-order sliding modes, differentiation and output-feedback control. *International Journal of Control*, 76(9-10), 924-941.