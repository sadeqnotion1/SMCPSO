# simulation.integrators.discrete.zero_order_hold

**Source:** `src\simulation\integrators\discrete\zero_order_hold.py`

## Module Overview

Zero-order hold discretization for discrete-time simulation.

## Complete Source Code

```{literalinclude} ../../../src/simulation/integrators/discrete/zero_order_hold.py
:language: python
:linenos:
```



## Classes

### `ZeroOrderHold`

**Inherits from:** `BaseIntegrator`

Zero-order hold discretization for linear and linearized systems.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/discrete/zero_order_hold.py
:language: python
:pyobject: ZeroOrderHold
:linenos:
```

#### Methods (9)

##### `__init__(self, A, B, dt)`

Initialize ZOH discretization.

[View full source →](#method-zeroorderhold-__init__)

##### `order(self)`

Integration method order (exact for linear systems).

[View full source →](#method-zeroorderhold-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-zeroorderhold-adaptive)

##### `set_linear_system(self, A, B, dt)`

Set linear system matrices and compute discrete-time equivalent.

[View full source →](#method-zeroorderhold-set_linear_system)

##### `_compute_discrete_matrices(self)`

Compute discrete-time matrices using matrix exponential.

[View full source →](#method-zeroorderhold-_compute_discrete_matrices)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate using zero-order hold discretization.

[View full source →](#method-zeroorderhold-integrate)

##### `_integrate_nonlinear(self, dynamics_fn, state, control, dt, t)`

Integrate nonlinear system with ZOH control approximation.

[View full source →](#method-zeroorderhold-_integrate_nonlinear)

##### `get_discrete_matrices(self)`

Get computed discrete-time matrices.

[View full source →](#method-zeroorderhold-get_discrete_matrices)

##### `simulate_discrete_sequence(self, initial_state, control_sequence, horizon)`

Simulate discrete-time system for multiple steps.

[View full source →](#method-zeroorderhold-simulate_discrete_sequence)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Callable, Optional`
- `import numpy as np`
- `from scipy.linalg import expm`
- `from ..base import BaseIntegrator`


## Advanced Mathematical Theory

### Zero-Order Hold (ZOH) Discretization

**Exact discretization for linear time-invariant systems:**

```{math}
\dot{\vec{x}}(t) = A\vec{x}(t) + B\vec{u}(t)
```

**Discrete-time equivalent (ZOH):**

```{math}
\vec{x}_{k+1} = A_d \vec{x}_k + B_d \vec{u}_k
```

where:

```{math}
\begin{align}
A_d &= e^{A\Delta t} \\
B_d &= \left(\int_0^{\Delta t} e^{A\tau}d\tau\right) B = A^{-1}(A_d - I)B
\end{align}
```

### Matrix Exponential Computation

**Padé approximation:**

```{math}
e^{A\Delta t} \approx \left(I - \frac{A\Delta t}{2}\right)^{-1}\left(I + \frac{A\Delta t}{2}\right)
```

**Eigenvalue decomposition (if $A$ diagonalizable):**

```{math}
A = V\Lambda V^{-1} \quad \Rightarrow \quad e^{A\Delta t} = Ve^{\Lambda\Delta t}V^{-1}
```

**Series expansion (small $\Delta t$):**

```{math}
e^{A\Delta t} = I + A\Delta t + \frac{(A\Delta t)^2}{2!} + \frac{(A\Delta t)^3}{3!} + \cdots
```

### Numerical Stability

**Condition number:**

```{math}
\kappa(A_d) = \|A_d\| \cdot \|A_d^{-1}\|
```

For well-conditioned $A$, ZOH is numerically stable. For ill-conditioned systems, use scaling and squaring method.

## Architecture Diagram

```{mermaid}
graph TD
    A[Linear System A, B, dt] --> B[Matrix Exponential]
    B --> C[Compute A_d = exp_A·dt_]

    C --> D[Integral Computation]
    D --> E[B_d = A^-1_·_A_d - I_·B]

    E --> F[ZOH Discrete System]
    F --> G[State Update]

    G --> H[x_k+1 = A_d·x_k + B_d·u_k]

    H --> I{Nonlinear?}
    I -->|Yes| J[Jacobian Linearization]
    I -->|No| K[Exact Discretization]

    J --> L[Re-compute A_d, B_d]
    L --> G

    K --> M[Next Step]

    style C fill:#9cf
    style E fill:#ff9
    style H fill:#9f9
```

## Usage Examples

### Example 1: Basic Integration

```python
from src.simulation.integrators import create_integrator

# Create integrator
integrator = create_integrator('rk4', dt=0.01)

# Integrate one step
x_next = integrator.integrate(dynamics_fn, x, u, dt)
```

## Example 2: Zero-Order Hold Discretization

```python
from src.simulation.integrators.discrete import ZeroOrderHold

# Linear system matrices
A = np.array([[0, 1], [-2, -3]])
B = np.array([[0], [1]])

# Create ZOH integrator
zoh = ZeroOrderHold(A, B, dt=0.01)

# Discrete-time evolution
x_next = zoh.integrate(None, x, u, dt)

# Access discrete matrices
A_d = zoh.A_d
B_d = zoh.B_d
```

## Example 3: Real-Time Monitoring

```python
from src.simulation.safety import SimulationPerformanceMonitor

# Create monitor
monitor = SimulationPerformanceMonitor()

# Simulation loop with monitoring
for i in range(N_steps):
    monitor.start_timing('step')

    u = controller.compute(x)
    x = integrator.integrate(dynamics, x, u, dt)

    elapsed = monitor.end_timing('step')

    if elapsed > deadline:
        print(f"Deadline violation at step {i}: {elapsed:.4f}s")

# Get statistics
stats = monitor.get_statistics()
print(f"Mean: {stats['mean']:.4f}s")
print(f"95th percentile: {stats['p95']:.4f}s")
```

## Example 4: Monte Carlo Simulation

```python
from src.simulation.strategies import MonteCarloStrategy

# Define parameter distributions
distributions = {
    'mass': ('normal', {'mean': 1.0, 'std': 0.1}),
    'length': ('uniform', {'low': 0.9, 'high': 1.1})
}

# Create Monte Carlo strategy
mc = MonteCarloStrategy(n_samples=1000, parallel=True)

# Run Monte Carlo analysis
results = mc.analyze(
    simulation_fn=run_simulation,
    parameters=distributions
)

# Extract statistics
print(f"Mean ISE: {results['metrics']['ise']['mean']:.4f}")
print(f"95% CI: [{results['metrics']['ise']['ci_lower']:.4f}, "
      f"{results['metrics']['ise']['ci_upper']:.4f}]")
```

## Example 5: Safety Recovery

```python
from src.simulation.safety import SafetyRecovery

# Configure recovery
recovery = SafetyRecovery(
    state_bounds=(-10, 10),
    control_bounds=(-100, 100),
    recovery_mode='qp'  # or 'projection', 'fallback'
)

# Simulation with safety recovery
for i in range(N_steps):
    u = controller.compute(x)

    # Check for violations
    if recovery.check_violation(x, u):
        x_safe, u_safe = recovery.recover(x, u)
        x = integrator.integrate(dynamics, x_safe, u_safe, dt)
    else:
        x = integrator.integrate(dynamics, x, u, dt)
```
