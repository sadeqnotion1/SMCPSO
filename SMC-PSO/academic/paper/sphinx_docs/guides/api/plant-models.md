# Plant Models API Guide

**Module:** `src.core.dynamics`, `src.plant`

**What This API Does:**
This API provides the physics equations that simulate how the double-inverted pendulum moves. When you run a simulation, these models calculate what happens when the controller applies force to the cart.

**Who This Is For:**
- Researchers modeling physical systems
- Developers building custom simulations
- Anyone wanting to understand the physics behind the system

**Level:** Intermediate to Advanced

**Quick Start:**
```python
# Use the simplified dynamics model
from src.core.dynamics import SimplifiedDynamics
from src.plant.configurations import DefaultPhysicsConfig

dynamics = SimplifiedDynamics(DefaultPhysicsConfig())
state_derivative = dynamics.compute(state, control_force)
```

---

## Table of Contents

- [Overview](#overview)
- [System Overview](#system-overview)
- [Model Types](#model-types)
- [Parameter Configuration](#parameter-configuration)
- [Custom Models](#custom-models)
- [Integration Patterns](#integration-patterns)
- [Troubleshooting](#troubleshooting)



## Overview

The Plant Models API provides physics-based models of the double-inverted pendulum system.

**Key Features:**
- ✅ **Multiple Models:** Simplified and full nonlinear dynamics
- ✅ **Configurable Physics:** Masses, lengths, friction, gravity
- ✅ **State-Space Representation:** Standard 6-dimensional state vector
- ✅ **Extensible:** Custom dynamics implementation support

**Related Documentation:**
- [Tutorial 01: First Simulation](../tutorials/tutorial-01-first-simulation.md)
- [Simulation API Guide](simulation.md)
- [Configuration API Guide](configuration.md)

**Theory & Foundations:**
- [DIP Dynamics Theory](../theory/dip-dynamics.md): Lagrangian derivation, linearization, controllability analysis



## System Overview

### Double-Inverted Pendulum Physics

The double-inverted pendulum consists of:
- **Cart (mass m₀):** Moves horizontally on a frictionless track
- **First Pendulum (mass m₁, length l₁):** Hinged to cart
- **Second Pendulum (mass m₂, length l₂):** Hinged to first pendulum tip

**Control Objective:** Stabilize both pendulums in upright position (θ₁ = θ₂ = 0) by applying horizontal force to cart.

### State Space Representation

All models use the same 6-dimensional state vector:

```python
state = np.array([
    x,        # Cart position (m)
    dx,       # Cart velocity (m/s)
    theta1,   # First pendulum angle (rad, 0 = upright)
    dtheta1,  # First pendulum angular velocity (rad/s)
    theta2,   # Second pendulum angle (rad, 0 = upright)
    dtheta2   # Second pendulum angular velocity (rad/s)
])
```

**Sign Convention:**
- θ > 0: Pendulum tilted right
- θ < 0: Pendulum tilted left
- θ = 0: Pendulum upright (equilibrium)

### Equations of Motion

**Lagrangian Formulation:**

```
L = T - V

where:
T = Kinetic Energy = (1/2)m₀ẋ² + (1/2)m₁(ẋ₁² + ż₁²) + (1/2)m₂(ẋ₂² + ż₂²)
V = Potential Energy = m₁gl₁cos(θ₁) + m₂g(l₁cos(θ₁) + l₂cos(θ₂))

Euler-Lagrange equations:
d/dt(∂L/∂q̇ᵢ) - ∂L/∂qᵢ = Qᵢ

q = [x, θ₁, θ₂]ᵀ (generalized coordinates)
Q = [u, 0, 0]ᵀ (generalized forces)
```

**Matrix Form:**

```
M(q)q̈ + C(q,q̇)q̇ + G(q) = Qu

where:
M(q) = Inertia matrix (configuration-dependent)
C(q,q̇) = Coriolis and centrifugal terms
G(q) = Gravitational terms
Q = Input transformation matrix
u = Control force
```

### Parameter Definitions

| Parameter | Symbol | Unit | Typical Value | Description |
|-----------|--------|------|---------------|-------------|
| Cart mass | m₀ | kg | 1.5 | Mass of cart platform |
| Pendulum 1 mass | m₁ | kg | 0.5 | Mass of first link |
| Pendulum 2 mass | m₂ | kg | 0.75 | Mass of second link |
| Pendulum 1 length | l₁ | m | 0.5 | Length from cart to joint 1 |
| Pendulum 2 length | l₂ | m | 0.75 | Length from joint 1 to tip |
| Pendulum 1 inertia | I₁ | kg⋅m² | (1/3)m₁l₁² | Rotational inertia |
| Pendulum 2 inertia | I₂ | kg⋅m² | (1/3)m₂l₂² | Rotational inertia |
| Cart friction | b₀ | N⋅s/m | 0.1 | Viscous friction |
| Joint 1 friction | b₁ | N⋅m⋅s/rad | 0.01 | Rotational damping |
| Joint 2 friction | b₂ | N⋅m⋅s/rad | 0.01 | Rotational damping |
| Gravity | g | m/s² | 9.81 | Gravitational acceleration |



## Model Types

### Simplified Dynamics

**File:** `src/core/dynamics.py`

**Mathematical Approximations:**
- Small angle assumption: sin(θ) ≈ θ, cos(θ) ≈ 1
- Linearized coupling between pendulums
- Simplified inertia matrix

**Advantages:**
- ✅ Fast computation (~2x faster than full dynamics)
- ✅ Suitable for PSO optimization (many iterations)
- ✅ Valid for small angles (|θ| < 15° ≈ 0.26 rad)
- ✅ Numerically stable

**Limitations:**
- ⚠️ Accuracy degrades for large angles
- ⚠️ Ignores nonlinear coupling effects
- ⚠️ Approximate Coriolis terms

**Usage:**
```python
from src.core.dynamics import SimplifiedDynamics
from src.config import load_config

config = load_config('config.yaml')
config.simulation.use_full_dynamics = False

dynamics = SimplifiedDynamics(config.dip_params)

# Compute state derivatives
state = np.array([0, 0, 0.1, 0, 0.15, 0])
control = 50.0
state_dot = dynamics.compute_dynamics(state, control)
```

**When to Use:**
- PSO optimization (speed critical)
- Controller prototyping
- Small angle stabilization tasks
- Development and debugging

## Full Nonlinear Dynamics

**File:** `src/core/dynamics_full.py`

**Mathematical Accuracy:**
- Exact trigonometric functions: sin(θ), cos(θ)
- Full nonlinear coupling between pendulums
- Complete Coriolis and centrifugal terms
- Configuration-dependent inertia matrix

**Advantages:**
- ✅ Exact physics representation
- ✅ Valid for large angles (|θ| < 180°)
- ✅ Captures all nonlinear effects
- ✅ Suitable for hardware validation

**Limitations:**
- ⚠️ Slower computation (~2x slower)
- ⚠️ May require smaller timesteps for stability

**Usage:**
```python
from src.core.dynamics_full import FullDynamics

config.simulation.use_full_dynamics = True
dynamics = FullDynamics(config.dip_params)

state_dot = dynamics.compute_dynamics(state, control)
```

**When to Use:**
- Final validation
- Large angle scenarios (swing-up control)
- Research publications
- Hardware deployment preparation

### Model Comparison

| Feature | Simplified | Full Nonlinear |
|---------|-----------|----------------|
| **Computation Speed** | Fast | Moderate |
| **Valid Angle Range** | ±15° | ±180° |
| **Accuracy** | Good (small angles) | Exact |
| **Coupling** | Linear approximation | Full nonlinear |
| **Coriolis Terms** | Approximate | Complete |
| **PSO Optimization** | ✅ Recommended | ⚠️ Slow |
| **Final Validation** | ⚠️ Not sufficient | ✅ Required |
| **Swing-Up Control** | ❌ Invalid | ✅ Valid |



## Parameter Configuration

### Loading Parameters from Config

```python
from src.config import load_config

config = load_config('config.yaml')
physics = config.dip_params

print(f"Cart mass: {physics.m0} kg")
print(f"Pendulum lengths: {physics.l1}, {physics.l2} m")
print(f"Gravity: {physics.g} m/s²")
```

### Programmatic Parameter Definition

```python
from src.config.schemas import DIPParams

# Define custom parameters
custom_params = DIPParams(
    m0=2.0,      # Heavier cart
    m1=0.3,      # Lighter first pendulum
    m2=0.5,      # Lighter second pendulum
    l1=0.4,      # Shorter first link
    l2=0.6,      # Shorter second link
    b0=0.2,      # Higher cart friction
    b1=0.02,     # Higher joint friction
    b2=0.02,
    g=9.81
)

# Inertias auto-calculated: I = (1/3) * m * l²
print(f"I1 (auto): {custom_params.I1:.4f} kg⋅m²")
print(f"I2 (auto): {custom_params.I2:.4f} kg⋅m²")
```

## Realistic vs Challenging Parameters

**Realistic (baseline):**
```yaml
dip_params:
  m0: 1.5      # Moderate cart mass
  m1: 0.5      # Balanced pendulums
  m2: 0.75
  l1: 0.5      # Moderate lengths
  l2: 0.75
  b0: 0.1      # Low friction
  b1: 0.01
  b2: 0.01
```

**Challenging (harder control):**
```yaml
dip_params:
  m0: 0.8      # Light cart (less inertia)
  m1: 0.8      # Heavy pendulums
  m2: 1.0
  l1: 0.7      # Longer links (more unstable)
  l2: 1.0
  b0: 0.05     # Very low friction
  b1: 0.005
  b2: 0.005
```

**Research (publication-quality):**
```yaml
dip_params:
  m0: 1.0
  m1: 0.5
  m2: 0.5
  l1: 0.5
  l2: 0.5
  b0: 0.1
  b1: 0.01
  b2: 0.01
  g: 9.81      # Standard gravity
```

### Parameter Sensitivity Analysis

```python
def analyze_mass_sensitivity():
    """Test controller sensitivity to mass variations."""
    base_params = config.dip_params
    m1_values = np.linspace(0.3, 0.8, 20)
    ise_results = []

    for m1 in m1_values:
        # Create modified parameters
        modified_params = DIPParams(
            m0=base_params.m0,
            m1=m1,  # Vary first pendulum mass
            m2=base_params.m2,
            l1=base_params.l1,
            l2=base_params.l2
        )

        # Run simulation
        dynamics = FullDynamics(modified_params)
        runner = SimulationRunner(config, dynamics_model=dynamics)
        result = runner.run(controller)
        ise_results.append(result['metrics']['ise'])

    return m1_values, ise_results

m1_vals, ise_vals = analyze_mass_sensitivity()

import matplotlib.pyplot as plt
plt.plot(m1_vals, ise_vals)
plt.xlabel('First Pendulum Mass m₁ (kg)')
plt.ylabel('ISE')
plt.title('Controller Sensitivity to Mass Variation')
plt.grid(True)
plt.show()
```



## Custom Models

### Implementing Custom Dynamics

**Example: Adding Coulomb friction**

```python
from src.core.dynamics_full import FullDynamics
import numpy as np

class CoulombFrictionDynamics(FullDynamics):
    """Full dynamics with Coulomb friction model."""

    def __init__(self, params, mu_coulomb=0.2):
        """
        Parameters
        # ---------- (RST section marker)
        params : DIPParams
            Physics parameters
        mu_coulomb : float
            Coulomb friction coefficient
        """
        super().__init__(params)
        self.mu_coulomb = mu_coulomb

    def compute_dynamics(self, state, control):
        """Compute state derivatives with Coulomb friction."""
        x, dx, theta1, dtheta1, theta2, dtheta2 = state

        # Coulomb friction force
        F_coulomb = self.mu_coulomb * self.params.m0 * self.params.g * np.sign(dx)

        # Apply Coulomb friction to control input
        effective_control = control - F_coulomb

        # Use parent class dynamics with modified control
        return super().compute_dynamics(state, effective_control)
```

**Example: Adding disturbance**

```python
# example-metadata:
# runnable: false

class DisturbedDynamics(FullDynamics):
    """Dynamics with external disturbance."""

    def __init__(self, params, disturbance_magnitude=10.0):
        super().__init__(params)
        self.disturbance_magnitude = disturbance_magnitude

    def compute_dynamics(self, state, control, time=0.0):
        """Add time-varying disturbance."""
        # Sinusoidal disturbance
        disturbance = self.disturbance_magnitude * np.sin(2 * np.pi * time)

        # Apply to control
        disturbed_control = control + disturbance

        return super().compute_dynamics(state, disturbed_control)
```

### Integration with SimulationRunner

```python
# Create custom dynamics
custom_dynamics = CoulombFrictionDynamics(config.dip_params, mu_coulomb=0.3)

# Use with simulation runner
runner = SimulationRunner(config, dynamics_model=custom_dynamics)
result = runner.run(controller)

print(f"ISE with Coulomb friction: {result['metrics']['ise']:.4f}")
```

## Validation of Custom Models

```python
# example-metadata:
# runnable: false

def validate_custom_dynamics(dynamics):
    """Ensure custom dynamics satisfy basic properties."""
    state = np.array([0, 0, 0.1, 0, 0.15, 0])
    control = 0.0

    # Test 1: State derivative has correct shape
    state_dot = dynamics.compute_dynamics(state, control)
    assert state_dot.shape == (6,), "State derivative shape mismatch"

    # Test 2: No NaN or Inf
    assert np.all(np.isfinite(state_dot)), "Invalid values in state derivative"

    # Test 3: Energy conservation (no control, no friction)
    # ... implement energy check

    print("Custom dynamics validation passed!")

validate_custom_dynamics(custom_dynamics)
```



## Integration Patterns

### Pattern 1: Model Switching

```python
# example-metadata:
# runnable: false

# Optimize with simplified dynamics (fast)
config.simulation.use_full_dynamics = False
dynamics_simple = SimplifiedDynamics(config.dip_params)
runner_simple = SimulationRunner(config, dynamics_model=dynamics_simple)

tuner = PSOTuner(SMCType.CLASSICAL, bounds, config=config)
best_gains, _ = tuner.optimize()

# Validate with full dynamics (accurate)
config.simulation.use_full_dynamics = True
dynamics_full = FullDynamics(config.dip_params)
runner_full = SimulationRunner(config, dynamics_model=dynamics_full)

controller = create_smc_for_pso(SMCType.CLASSICAL, best_gains)
result = runner_full.run(controller)

print(f"Validation ISE: {result['metrics']['ise']:.4f}")
```

## Pattern 2: Model Comparison

```python
# example-metadata:
# runnable: false

# Compare simplified vs full dynamics
results_comparison = {}

for model_name, dynamics in [
    ('Simplified', SimplifiedDynamics(config.dip_params)),
    ('Full', FullDynamics(config.dip_params))
]:
    runner = SimulationRunner(config, dynamics_model=dynamics)
    result = runner.run(controller)
    results_comparison[model_name] = result

# Analyze differences
for model, result in results_comparison.items():
    print(f"{model}: ISE={result['metrics']['ise']:.4f}, "
          f"Settling={result['metrics']['settling_time']:.2f}s")
```



## Troubleshooting

### Problem: Numerical instability with full dynamics

**Solution:**
1. Reduce timestep: `config.simulation.dt = 0.005`
2. Check for singular configurations (θ ≈ ±90°)
3. Reduce controller gains

### Problem: Results differ between models

**Solution:**
Expected for large angles. Simplified model valid only for |θ| < 15°.

### Problem: Energy not conserved

**Solution:**
Check friction parameters and numerical integration timestep.



## Next Steps

- **Learn system physics:** [Tutorial 01: System Introduction](../tutorials/tutorial-01-first-simulation.md)
- **Run simulations:** [Simulation API Guide](simulation.md)
- **Configure parameters:** [Configuration API Guide](configuration.md)
- **Technical details:** [Dynamics Technical Reference](../../reference/core/__init__.md)



**Last Updated:** October 2025
