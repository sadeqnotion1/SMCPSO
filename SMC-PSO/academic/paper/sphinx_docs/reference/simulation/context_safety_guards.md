# simulation.context.safety_guards

**Source:** `src\simulation\context\safety_guards.py`

## Module Overview

Vectorized safety guard functions for simulation.

These helpers implement pure checks on state tensors.  They operate on
scalars, vectors or batched vectors (any shape with the last axis as the state
dimension) and raise informative RuntimeError exceptions when invariants are
violated.  The error messages contain frozen substrings which are matched
exactly in the acceptance tests; do not modify the substrings.

## Complete Source Code

```{literalinclude} ../../../src/simulation/context/safety_guards.py
:language: python
:linenos:
```



## Functions

### `_guard_no_nan(state, step_idx)`

Raise if ``state`` contains any non‑finite values.

Parameters
----------
state : array-like
    State array of shape ``(..., D)``.  Can be scalar or batched.
step_idx : int
    Index of the current step (for reporting purposes).

Raises
------
RuntimeError
    If any element of ``state`` is NaN or infinite.  The message
    contains the frozen substring ``"NaN detected in state at step <i>"``
    followed by the actual step index.

#### Source Code

```{literalinclude} ../../../src/simulation/context/safety_guards.py
:language: python
:pyobject: _guard_no_nan
:linenos:
```



### `_guard_energy(state, limits)`

Check that the total energy of ``state`` does not exceed a maximum.

Energy is defined as the sum of squares of the state variables
``sum(state**2, axis=-1)``.  When any batch element exceeds the
configured maximum, a RuntimeError is raised.  The message contains
the frozen substring ``"Energy check failed: total_energy=<val> exceeds <max>"``.

Parameters
----------
state : array-like
    State array of shape ``(..., D)``.  Scalars and batches are allowed.
limits : dict or None
    Must contain the key ``"max"`` specifying the maximum allowed total
    energy.  If ``limits`` is ``None`` or missing the key, this check
    silently returns.

#### Source Code

```{literalinclude} ../../../src/simulation/context/safety_guards.py
:language: python
:pyobject: _guard_energy
:linenos:
```



### `_guard_bounds(state, bounds, t)`

Check that ``state`` lies within elementwise bounds.

Parameters
----------
state : array-like
    State array of shape ``(..., D)``.
bounds : tuple or None
    A pair ``(lower, upper)`` specifying inclusive bounds.  Each may be
    a scalar, an array broadcastable to ``state``, or ``None`` to
    disable that side of the bound.
t : float
    Simulation time (for error reporting).

Raises
------
RuntimeError
    If any element of ``state`` falls outside the specified bounds.
    The message contains the frozen substring ``"State bounds violated at t=<t>"``.

#### Source Code

```{literalinclude} ../../../src/simulation/context/safety_guards.py
:language: python
:pyobject: _guard_bounds
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `from typing import Any, Tuple, Optional, Dict`


## Advanced Mathematical Theory

### Real-Time Constraints

**Deadline constraint:**

```{math}
t_{\text{compute}} \leq t_{\text{deadline}}, \quad \forall \, \text{steps}
```

**Weakly-hard constraints (m, k):**

Out of any $k$ consecutive deadlines, at most $m$ can be missed.

```{math}
\sum_{i=n-k+1}^{n} \mathbb{1}_{\text{miss}}(i) \leq m
```

### Safety Validators

**State bounds validation:**

```{math}
\vec{x}_{\min} \leq \vec{x}_n \leq \vec{x}_{\max}, \quad \forall \, n
```

**Control saturation:**

```{math}
|u_n| \leq u_{\max}, \quad \forall \, n
```

### Numerical Stability Monitoring

**Condition number check:**

```{math}
\kappa(M) = \|M\| \cdot \|M^{-1}\| < \kappa_{\max}
```

**Energy conservation (for Hamiltonian systems):**

```{math}
\left|\frac{E(t) - E(t_0)}{E(t_0)}\right| < \epsilon_{\text{energy}}
```

### Graceful Degradation

**Safety hierarchy:**

```{math}
\text{Safety} = \begin{cases}
\text{Normal Operation} & \text{if all checks pass} \\
\text{Degraded Mode} & \text{if soft violations} \\
\text{Emergency Stop} & \text{if hard violations}
\end{cases}
```

## Architecture Diagram

```{mermaid}
graph TD
    A[Simulation Step] --> B[Pre-Step Validation]

    B --> C[State Bounds Check]
    B --> D[Control Saturation Check]
    B --> E[Numerical Stability Check]

    C --> F{Valid?}
    D --> F
    E --> F

    F -->|Yes| G[Execute Step]
    F -->|No| H[Violation Handler]

    H --> I{Severity}
    I -->|Soft| J[Degraded Mode]
    I -->|Hard| K[Emergency Stop]

    G --> L[Post-Step Validation]
    L --> M[Energy Check]
    L --> N[Deadline Check]

    M --> O{Valid?}
    N --> O

    O -->|Yes| P[Continue]
    O -->|No| Q[Safety Event Log]

    J --> P
    K --> R[Simulation Abort]

    style G fill:#9cf
    style P fill:#9f9
    style K fill:#f99
    style R fill:#f00
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
