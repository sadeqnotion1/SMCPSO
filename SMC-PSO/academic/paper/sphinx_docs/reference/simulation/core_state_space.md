# simulation.core.state_space

**Source:** `src\simulation\core\state_space.py`

## Module Overview

State-space representation utilities for simulation framework.

## Complete Source Code

```{literalinclude} ../../../src/simulation/core/state_space.py
:language: python
:linenos:
```



## Classes

### `StateSpaceUtilities`

Utilities for state-space system representations and manipulations.

#### Source Code

```{literalinclude} ../../../src/simulation/core/state_space.py
:language: python
:pyobject: StateSpaceUtilities
:linenos:
```

#### Methods (6)

##### `validate_state_dimensions(state, expected_dim)`

Validate state vector dimensions.

[View full source →](#method-statespaceutilities-validate_state_dimensions)

##### `normalize_state_batch(states)`

Normalize state array to consistent batch format.

[View full source →](#method-statespaceutilities-normalize_state_batch)

##### `extract_state_components(state, indices)`

Extract named state components from state vector.

[View full source →](#method-statespaceutilities-extract_state_components)

##### `compute_state_bounds(states, percentile)`

Compute state bounds from trajectory data.

[View full source →](#method-statespaceutilities-compute_state_bounds)

##### `compute_energy(state, mass_matrix)`

Compute system energy from state vector.

[View full source →](#method-statespaceutilities-compute_energy)

##### `linearize_about_equilibrium(dynamics_fn, equilibrium_state, equilibrium_control, epsilon)`

Linearize dynamics about an equilibrium point.

[View full source →](#method-statespaceutilities-linearize_about_equilibrium)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, List, Optional, Tuple, Union`
- `import numpy as np`


## Advanced Mathematical Theory

### Linear State Space Representation

**Continuous-time linear system:**

```{math}
\begin{align}
\dot{\vec{x}} &= A\vec{x} + B\vec{u} \\
\vec{y} &= C\vec{x} + D\vec{u}
\end{align}
```

where:
- $\vec{x} \in \mathbb{R}^n$ is state vector
- $\vec{u} \in \mathbb{R}^m$ is input vector
- $\vec{y} \in \mathbb{R}^p$ is output vector
- $A, B, C, D$ are system matrices

### Nonlinear State Space

**General nonlinear system:**

```{math}
\begin{align}
\dot{\vec{x}} &= \vec{f}(\vec{x}, \vec{u}, t) \\
\vec{y} &= \vec{h}(\vec{x}, \vec{u}, t)
\end{align}
```

### State Transition Matrix

**Solution for linear systems:**

```{math}
\vec{x}(t) = \Phi(t, t_0)\vec{x}(t_0) + \int_{t_0}^t \Phi(t, \tau)B\vec{u}(\tau)d\tau
```

where $\Phi(t, t_0) = e^{A(t-t_0)}$ is the state transition matrix.

### Equilibrium Points

**Equilibrium condition:**

```{math}
\vec{f}(\vec{x}_{eq}, \vec{u}_{eq}, t) = \vec{0}
```

**Linearization about equilibrium:**

```{math}
A = \frac{\partial \vec{f}}{\partial \vec{x}}\bigg|_{\vec{x}_{eq}, \vec{u}_{eq}}, \quad B = \frac{\partial \vec{f}}{\partial \vec{u}}\bigg|_{\vec{x}_{eq}, \vec{u}_{eq}}
```

## Architecture Diagram

```{mermaid}
graph TD
    A[State Vector x] --> B[Dynamics f_x, u, t_]
    C[Control Input u] --> B
    D[Time t] --> B

    B --> E{System Type}
    E -->|Linear| F[A·x + B·u]
    E -->|Nonlinear| G[f_x, u, t_]

    F --> H[State Derivative ẋ]
    G --> H

    H --> I[Integrator]
    I --> J[x_n+1_]

    J --> K[Output Map]
    K --> L[y = h_x, u_]

    J --> M{Equilibrium?}
    M -->|Yes| N[Linearization]
    M -->|No| O[Continue Evolution]

    style B fill:#9cf
    style I fill:#ff9
    style J fill:#9f9
```

## Usage Examples

### Example 1: Basic Simulation

```python
from src.simulation.core import SimulationEngine
from src.simulation.engines import SimulationRunner

# Initialize simulation engine
runner = SimulationRunner(
    controller=controller,
    dynamics=dynamics,
    integrator='rk4',
    dt=0.01
)

# Run simulation
results = runner.simulate(
    x0=initial_state,
    duration=5.0
)

# Extract trajectories
t = results.time
x = results.states
u = results.controls
```

## Example 2: Adaptive Integration

```python
from src.simulation.integrators.adaptive import AdaptiveRK45Integrator

# Create adaptive integrator
integrator = AdaptiveRK45Integrator(
    rtol=1e-6,
    atol=1e-8,
    max_step=0.1,
    min_step=1e-6
)

# Simulate with automatic step size control
results = runner.simulate(
    x0=initial_state,
    duration=5.0,
    integrator=integrator
)

# Check step size history
print(f"Steps taken: {len(results.time)}")
print(f"Average dt: {np.mean(np.diff(results.time)):.6f}")
```

## Example 3: Batch Simulation (Numba)

```python
from src.simulation.engines import run_batch_simulation

# Define batch of initial conditions
x0_batch = np.random.randn(100, 6)  # 100 initial states

# Vectorized batch simulation
results_batch = run_batch_simulation(
    controller=controller,
    dynamics=dynamics,
    x0_batch=x0_batch,
    duration=5.0,
    dt=0.01
)

# Compute batch statistics
mean_trajectory = np.mean(results_batch.states, axis=0)
std_trajectory = np.std(results_batch.states, axis=0)
```

## Example 4: Safety Guards

```python
from src.simulation.context import SimulationContext
from src.simulation.safety import SafetyGuards

# Configure safety constraints
safety = SafetyGuards(
    state_bounds=(-10, 10),
    control_bounds=(-100, 100),
    deadline_ms=10.0,
    max_condition_number=1e6
)

# Simulation with safety monitoring
with SimulationContext(controller, dynamics, safety) as ctx:
    results = ctx.simulate(x0, duration=5.0)

    # Check safety violations
    violations = ctx.get_safety_violations()
    if violations:
        print(f"Warning: {len(violations)} safety events detected")
```

### Example 5: Performance Profiling

```python
import time
from src.simulation.engines import SimulationRunner

# Profile different integrators
integrators = ['euler', 'rk4', 'rk45']
times = {}

for method in integrators:
    runner = SimulationRunner(
        controller=controller,
        dynamics=dynamics,
        integrator=method,
        dt=0.01
    )

    start = time.perf_counter()
    results = runner.simulate(x0, duration=10.0)
    elapsed = time.perf_counter() - start

    times[method] = elapsed
    print(f"{method}: {elapsed:.4f}s ({len(results.time)} steps)")

# Compare speedup
print(f"\nRK4 vs Euler speedup: {times['euler']/times['rk4']:.2f}x")
```
