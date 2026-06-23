<!--======================================================================================\\\
============== docs/testing/theory/lyapunov_stability_testing.md =====================\\\
=======================================================================================-->

# Lyapunov Stability Testing Theory

**Purpose**: Mathematical foundations and testing methodologies for verifying Lyapunov stability of sliding mode controllers.



## 📐 Theoretical Foundations

### Lyapunov Stability Theorem

For system $\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x}, t)$ with equilibrium $\mathbf{x}_e = \mathbf{0}$:

**Theorem**: If there exists a continuously differentiable function $V(\mathbf{x})$ such that:

1. $V(\mathbf{0}) = 0$
2. $V(\mathbf{x}) > 0$ for $\mathbf{x} \neq \mathbf{0}$ (positive definite)
3. $\dot{V}(\mathbf{x}) \leq 0$ (negative semi-definite)

Then $\mathbf{x} = \mathbf{0}$ is **stable**.

If additionally $\dot{V}(\mathbf{x}) < 0$ for $\mathbf{x} \neq \mathbf{0}$, then **asymptotically stable**.



### Sliding Mode Control Lyapunov Function

**Sliding Surface**: $\sigma = \mathbf{s}^T \mathbf{x}$ where $\mathbf{s}$ is sliding surface vector

**Lyapunov Candidate**: $V = \frac{1}{2}\sigma^2$

**Derivative**:
$$\dot{V} = \sigma \dot{\sigma} = \sigma(\mathbf{s}^T \dot{\mathbf{x}})$$

**Reaching Condition**: $\sigma \dot{\sigma} < -\eta |\sigma|$ for $\eta > 0$

This ensures $\sigma \to 0$ in finite time:
$$t_{\text{reach}} = \frac{|\sigma(0)|}{\eta}$$



## 🧪 Testing Methodologies

### Test 1: Positive Definiteness

```python
import pytest
import numpy as np
from hypothesis import given, strategies as st

@given(state=valid_states())
def test_lyapunov_positive_definite(state):
    """V(x) ≥ 0 for all x, V(0) = 0"""
    V = lyapunov_function(state)

    if np.allclose(state, 0, atol=1e-6):
        assert V < 1e-6, f"V(0) = {V} ≠ 0"
    else:
        assert V > 0, f"V not positive: V({state}) = {V}"
```



### Test 2: Negative Derivative

```python
# example-metadata:
# runnable: false

@given(state=valid_states())
def test_lyapunov_decrease(state):
    """dV/dt ≤ 0 along trajectories"""
    # Compute V at current state
    V_t = lyapunov_function(state)

    # Simulate one time step
    u = controller.compute_control(state)
    state_next = dynamics.step(state, u, dt=0.01)

    V_next = lyapunov_function(state_next)

    # Allow small numerical tolerance
    assert V_next <= V_t + 1e-6, \
        f"V increased: {V_t} → {V_next} (Δ={V_next - V_t})"
```



### Test 3: Finite-Time Reaching

```python
# example-metadata:
# runnable: false

def test_finite_time_reaching():
    """Sliding surface reached in finite time"""
    initial_state = np.array([0.5, -0.3, 1.0, -0.8])
    sigma_0 = sliding_surface(initial_state)

    trajectory = simulate(controller, dynamics, initial_state, duration=5.0)

    # Find first time σ crosses zero
    t_reach = None
    for i, state in enumerate(trajectory):
        sigma = sliding_surface(state)
        if abs(sigma) < 0.01:  # Threshold for "reached"
            t_reach = i * 0.01
            break

    assert t_reach is not None, "Did not reach sliding surface"

    # Verify theoretical bound: t_reach ≤ |σ(0)| / η
    eta = 0.1  # Known reaching constant
    t_theoretical = abs(sigma_0) / eta

    assert t_reach <= t_theoretical * 1.2, \  # Allow 20% tolerance
        f"Took too long: {t_reach}s > {t_theoretical}s"
```



## 🔬 Advanced Validation

### Regional Stability

```python
# example-metadata:
# runnable: false

def test_region_of_attraction():
    """Verify estimated region of attraction"""
    # Sample initial states from estimated ROA
    R = 0.5  # Estimated ROA radius
    test_states = sample_sphere(center=[0,0,0,0], radius=R, n_samples=100)

    for initial_state in test_states:
        trajectory = simulate(controller, dynamics, initial_state, duration=10.0)
        final_state = trajectory[-1]

        # Must converge to equilibrium
        assert np.linalg.norm(final_state) < 0.05, \
            f"Failed to converge from {initial_state}"
```



### Robustness to Disturbances

```python
# example-metadata:
# runnable: false

@given(
    state=valid_states(),
    disturbance=st.floats(min_value=-0.5, max_value=0.5)
)
def test_ISS_property(state, disturbance):
    """Input-to-State Stability (ISS)"""
    # Simulate with disturbance
    u = controller.compute_control(state)
    u_disturbed = u + disturbance

    state_next = dynamics.step(state, u_disturbed, dt=0.01)

    # ISS condition: ||x(t)|| ≤ β(||x(0)||, t) + γ(||d||)
    x_norm = np.linalg.norm(state_next)
    d_norm = abs(disturbance)

    # Simplified check: state bounded by disturbance magnitude
    assert x_norm <= 10 * d_norm + 1.0, \
        f"Not ISS: ||x||={x_norm} vs ||d||={d_norm}"
```



## 📊 Practical Considerations

### Numerical Issues

**Problem**: Finite precision can make $\dot{V} > 0$ numerically

**Solution**:
```python
TOLERANCE = 1e-6

def test_lyapunov_with_tolerance(state):
    V_next = lyapunov_function(next_state)
    V_current = lyapunov_function(state)

    # Use relative tolerance for small V values
    if V_current < 1e-3:
        assert V_next <= V_current + TOLERANCE
    else:
        assert V_next <= V_current * (1 + TOLERANCE)
```



### Chattering Effects

**Issue**: High-frequency switching can increase $V$ temporarily

**Mitigation**:
```python
# example-metadata:
# runnable: false

def test_lyapunov_averaged_decrease(state):
    """Check V decreases on average over window"""
    window_size = 10  # Average over 10 steps

    V_values = []
    for _ in range(window_size):
        V = lyapunov_function(state)
        V_values.append(V)

        u = controller.compute_control(state)
        state = dynamics.step(state, u, dt=0.01)

    # Moving average should decrease
    avg_first_half = np.mean(V_values[:5])
    avg_second_half = np.mean(V_values[5:])

    assert avg_second_half < avg_first_half
```



## 📚 Related Documentation

- [SMC Validation Mathematics](smc_validation_mathematics.md)
- [Property-Based Testing](../guides/property_based_testing.md)
- [Control Systems Unit Testing](../guides/control_systems_unit_testing.md)



## 🔗 Navigation

[⬅️ Back to Theory](../theory/) | [🏠 Testing Home](../README.md) | [➡️ SMC Validation Math](smc_validation_mathematics.md)



**Last Updated**: September 30, 2025
**Mathematical Reviewer**: Control Theory Team
**Implementation**: Testing Infrastructure