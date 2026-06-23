<!--======================================================================================\\\
================ docs/testing/guides/property_based_testing.md =======================\\\
=======================================================================================-->

# Property-Based Testing for Control Systems

**Purpose**: Guide for implementing property-based tests using Hypothesis to validate control system invariants, stability properties, and robustness.



## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Control System Properties](#control-system-properties)
3. [Hypothesis Strategies](#hypothesis-strategies)
4. [Implementation Patterns](#implementation-patterns)
5. [Real-World Examples](#real-world-examples)



## 🎯 Introduction

### What is Property-Based Testing?

Traditional unit tests check specific input/output pairs:
```python
def test_smc_zero_error():
    """Test SMC with zero error"""
    state = [0, 0, 0, 0]  # Specific case
    control = smc.compute_control(state)
    assert control == 0
```

Property-based tests verify universal properties across input ranges:
```python
@given(state=states())
def test_smc_bounded_output(state):
    """Test SMC output always bounded"""
    control = smc.compute_control(state)
    assert -MAX_TORQUE <= control <= MAX_TORQUE  # For ALL states
```



### Why for Control Systems?

Control systems have **mathematical invariants** that must hold universally:

1. **Lyapunov Stability**: $V(\mathbf{x}) \geq 0$, $\dot{V}(\mathbf{x}) \leq 0$
2. **Control Bounds**: $|\mathbf{u}| \leq u_{\text{max}}$
3. **Sliding Surface**: $\sigma(\mathbf{x}, t) \to 0$ as $t \to \infty$
4. **Robustness**: Performance maintained under parameter variations

Property-based testing naturally expresses these invariants.



## 🔬 Control System Properties

### Category 1: Safety Properties

**Definition**: "Bad things never happen"

```python
from hypothesis import given, strategies as st

@given(
    theta1=st.floats(min_value=-π, max_value=π),
    theta2=st.floats(min_value=-π, max_value=π),
    velocity=st.floats(min_value=-10, max_value=10)
)
def test_control_never_exceeds_limits(theta1, theta2, velocity):
    """Control output must NEVER exceed actuator limits"""
    state = construct_state(theta1, theta2, velocity)
    u = controller.compute_control(state)

    assert -MAX_TORQUE <= u <= MAX_TORQUE, \
        f"Control {u} exceeded limits for state {state}"
```



### Category 2: Stability Properties

**Definition**: System energy decreases or remains bounded

```python
# example-metadata:
# runnable: false

@given(state=valid_states())
def test_lyapunov_decrease(state):
    """Lyapunov function decreases along trajectories"""
    # Compute V(x) at current state
    V_current = lyapunov_function(state)

    # Simulate one timestep
    u = controller.compute_control(state)
    next_state = dynamics.step(state, u, dt=0.01)
    V_next = lyapunov_function(next_state)

    # V must decrease (or stay same if at equilibrium)
    assert V_next <= V_current + 1e-6, \
        f"Lyapunov increased: {V_current} -> {V_next}"
```



### Category 3: Continuity Properties

**Definition**: Small state changes → small control changes

```python
# example-metadata:
# runnable: false

@given(
    state=valid_states(),
    perturbation=st.floats(min_value=-0.01, max_value=0.01)
)
def test_control_continuity(state, perturbation):
    """Control law is Lipschitz continuous"""
    u1 = controller.compute_control(state)

    perturbed_state = state + perturbation
    u2 = controller.compute_control(perturbed_state)

    # Control change bounded by Lipschitz constant
    L = 100  # Known Lipschitz constant
    assert abs(u2 - u1) <= L * abs(perturbation), \
        f"Discontinuity detected: Δu={u2-u1}, Δx={perturbation}"
```



### Category 4: Robustness Properties

**Definition**: Performance maintained under uncertainties

```python
# example-metadata:
# runnable: false

@given(
    mass_error=st.floats(min_value=0.8, max_value=1.2),  # ±20%
    friction_error=st.floats(min_value=0.5, max_value=1.5),  # ±50%
    initial_state=valid_states()
)
def test_robust_stabilization(mass_error, friction_error, initial_state):
    """Controller stabilizes despite parameter uncertainties"""
    # Create perturbed dynamics
    perturbed_dynamics = DoublePendulum(
        m1=M1 * mass_error,
        m2=M2 * mass_error,
        b=FRICTION * friction_error
    )

    # Simulate closed-loop
    trajectory = simulate(
        controller, perturbed_dynamics,
        initial_state, duration=5.0
    )

    # Check final state near equilibrium
    final_state = trajectory[-1]
    assert np.linalg.norm(final_state) < 0.1, \
        "Failed to stabilize with parameter errors"
```



## 🎲 Hypothesis Strategies

### Strategy 1: State Space Strategies

```python
from hypothesis import strategies as st

def valid_states(
    theta_max=π,
    velocity_max=10,
    constrain_to_basin=False
):
    """Generate valid state vectors"""
    if constrain_to_basin:
        # Only generate states in region of attraction
        theta_strategy = st.floats(min_value=-0.5, max_value=0.5)
    else:
        # Full state space
        theta_strategy = st.floats(
            min_value=-theta_max,
            max_value=theta_max,
            allow_nan=False,
            allow_infinity=False
        )

    velocity_strategy = st.floats(
        min_value=-velocity_max,
        max_value=velocity_max,
        allow_nan=False
    )

    return st.tuples(
        theta_strategy,  # theta1
        theta_strategy,  # theta2
        velocity_strategy,  # dtheta1
        velocity_strategy   # dtheta2
    )
```



### Strategy 2: Gain Strategies

```python
# example-metadata:
# runnable: false

def positive_gains(min_value=0.1, max_value=100):
    """Generate valid controller gains"""
    return st.floats(
        min_value=min_value,
        max_value=max_value,
        allow_nan=False,
        allow_infinity=False,
        exclude_min=True  # Must be strictly positive
    )

@given(
    k1=positive_gains(),
    k2=positive_gains(),
    k3=positive_gains()
)
def test_smc_with_random_gains(k1, k2, k3):
    """SMC must remain stable for any positive gains"""
    controller = ClassicalSMC(gains=[k1, k2, k3])
    # Test stability property
    ...
```



### Strategy 3: Trajectory Strategies

```python
def trajectories(duration=5.0, dt=0.01):
    """Generate state trajectories"""
    return st.lists(
        valid_states(),
        min_size=int(duration / dt),
        max_size=int(duration / dt)
    )
```



## 💻 Implementation Patterns

### Pattern 1: Invariant Testing

```python
from hypothesis import given, assume, settings
import hypothesis.strategies as st

@given(state=valid_states())
@settings(max_examples=1000)  # Run 1000 random tests
def test_invariant_holds(state):
    """Template for testing control invariants"""
    # Optionally filter invalid cases
    assume(is_physically_realizable(state))

    # Compute control
    u = controller.compute_control(state)

    # Check invariant
    assert invariant_check(u, state), \
        f"Invariant violated for state={state}, control={u}"
```



### Pattern 2: Metamorphic Testing

Test relationships between inputs/outputs:

```python
@given(state=valid_states(), scale=st.floats(min_value=0.1, max_value=10))
def test_control_scaling_property(state, scale):
    """If error scales, control should scale proportionally"""
    u1 = controller.compute_control(state)
    scaled_state = state * scale
    u2 = controller.compute_control(scaled_state)

    # Check proportionality (for linear controllers)
    assert abs(u2 / u1 - scale) < 0.01, \
        "Control does not scale with state"
```



### Pattern 3: Regression Property Testing

```python
# example-metadata:
# runnable: false

@given(state=valid_states())
def test_no_regression_from_baseline(state):
    """Current controller performs at least as well as baseline"""
    # Baseline controller (e.g., from v1.0)
    u_baseline = baseline_controller.compute_control(state)
    cost_baseline = evaluate_performance(state, u_baseline)

    # Current controller
    u_current = current_controller.compute_control(state)
    cost_current = evaluate_performance(state, u_current)

    assert cost_current <= cost_baseline * 1.05, \  # Allow 5% tolerance
        f"Performance regression detected: {cost_current} > {cost_baseline}"
```



## 🏗️ Real-World Examples

### Example 1: Sliding Surface Property

```python
# example-metadata:
# runnable: false

@given(state=valid_states())
def test_sliding_surface_attractivity(state):
    """Sliding surface must be attractive from any state"""
    sigma_values = []

    for t in range(100):  # 1 second simulation
        sigma = sliding_surface(state)
        sigma_values.append(abs(sigma))

        u = controller.compute_control(state)
        state = dynamics.step(state, u, dt=0.01)

    # Σ must decrease on average
    initial_sigma = sigma_values[0]
    final_sigma = sigma_values[-1]

    assert final_sigma < initial_sigma or initial_sigma < 0.01, \
        f"Sliding surface not attractive: {initial_sigma} -> {final_sigma}"
```



### Example 2: Chattering Bound

```python
# example-metadata:
# runnable: false

@given(
    state=valid_states(),
    boundary_layer=st.floats(min_value=0.01, max_value=1.0)
)
def test_chattering_bounded_by_boundary_layer(state, boundary_layer):
    """Chattering frequency inversely related to boundary layer"""
    controller.set_boundary_layer(boundary_layer)

    control_sequence = []
    for _ in range(100):
        u = controller.compute_control(state)
        control_sequence.append(u)
        state = dynamics.step(state, u, dt=0.01)

    # Count sign changes (chattering indicator)
    sign_changes = count_sign_changes(control_sequence)

    # Larger boundary layer → fewer sign changes
    assert sign_changes < 50 / boundary_layer, \
        f"Excessive chattering: {sign_changes} switches with ϕ={boundary_layer}"
```



## 🛠️ Best Practices

### 1. Use `assume()` for Preconditions

```python
# example-metadata:
# runnable: false

@given(state=valid_states())
def test_property(state):
    # Filter out uninteresting cases
    assume(np.linalg.norm(state) > 0.01)  # Skip near-equilibrium
    ...
```



### 2. Shrink Examples Automatically

Hypothesis automatically finds minimal failing examples:

```text
Falsifying example:
  state = [0.0001, 0.0, 0.0, 0.0]  # Hypothesis shrunk from complex case
```



### 3. Use Composite Strategies

```python
@st.composite
def controller_with_valid_gains(draw):
    """Generate controller with constraint: k1 > k2 > k3"""
    k3 = draw(st.floats(min_value=1, max_value=10))
    k2 = draw(st.floats(min_value=k3 + 1, max_value=50))
    k1 = draw(st.floats(min_value=k2 + 1, max_value=100))
    return ClassicalSMC(gains=[k1, k2, k3])
```



### 4. Profile with `settings`

```python
# example-metadata:
# runnable: false

from hypothesis import settings, HealthCheck

@given(state=valid_states())
@settings(
    max_examples=10000,  # Exhaustive testing
    deadline=None,       # No timeout
    suppress_health_check=[HealthCheck.too_slow]
)
def test_critical_property(state):
    ...
```



## 📚 Related Documentation

- [Control Systems Unit Testing](control_systems_unit_testing.md)
- [Integration Workflows](integration_workflows.md)
- [SMC Validation Mathematics](../theory/smc_validation_mathematics.md)



## 🔗 Navigation

[⬅️ Back to Guides](../guides/) | [🏠 Testing Home](../README.md) | [➡️ Performance Benchmarking](performance_benchmarking.md)



**Last Updated**: September 30, 2025
**Maintainer**: Testing Infrastructure Team
**Coverage**: Property-based testing, Hypothesis, control system invariants