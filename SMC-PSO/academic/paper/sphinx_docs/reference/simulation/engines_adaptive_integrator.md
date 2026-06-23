# simulation.engines.adaptive_integrator

**Source:** `src\simulation\engines\adaptive_integrator.py`

## Module Overview

Adaptive Runge–Kutta integrators for state‑space models.

This module implements a Dormand–Prince 4(5) embedded Runge–Kutta step
with error estimation and adaptive step size control.  Embedded
Runge–Kutta pairs compute two solutions of different orders from the
same function evaluations; the difference between the 4th‑ and 5th‑order
approximations provides an estimate of the local truncation error.  By
comparing this error against user‑supplied absolute and relative
tolerances the integrator can accept or reject a proposed step and
adjust the step size accordingly【313837333132264†L58-L82】.  Adaptive
integrators avoid manual tuning of Courant–Friedrichs–Lewy (CFL)
parameters and automatically reduce the step size when the system
exhibits rapid dynamics or near‑singular mass matrices.

The implementation here focuses on a single step of the Dormand–Prince
method.  A higher‑level loop must call :func:`rk45_step` repeatedly
while updating the integration time and state.  If a step is rejected
the returned state will be ``None`` and the caller should retry the
integration with the suggested smaller ``dt``.  When a step is
accepted the integrator proposes a new step size that can be used for
the next call.

The algorithm is described in many numerical analysis textbooks; see
Section III of Shampine and Reichelt for details【313837333132264†L58-L82】.

## Complete Source Code

```{literalinclude} ../../../src/simulation/engines/adaptive_integrator.py
:language: python
:linenos:
```



## Functions

### `rk45_step(f, t, y, dt, abs_tol, rel_tol)`

Perform a single Dormand–Prince 4(5) integration step.

Parameters
----------
f : Callable[[float, np.ndarray], np.ndarray]
    Function computing the time derivative of the state ``y`` at time
    ``t``.  The derivative must be a one‑dimensional NumPy array.
t : float
    Current integration time.
y : np.ndarray
    Current state vector.
dt : float
    Proposed step size.
abs_tol : float
    Absolute tolerance for local error control.
rel_tol : float
    Relative tolerance for local error control.

Returns
-------
Tuple[Optional[np.ndarray], float]
    A tuple ``(y_new, dt_new)``.  If the step is accepted then
    ``y_new`` contains the 5th‑order solution at ``t + dt`` and
    ``dt_new`` is a suggested step size for the next step.  If the
    step is rejected then ``y_new`` is ``None`` and ``dt_new`` is a
    smaller step size to retry.

Notes
-----
This implementation uses the Dormand–Prince coefficients for the
classic `RK45` method.  The constants are hard‑coded for clarity
rather than generated programmatically.  See the cited reference
for the Butcher tableau【313837333132264†L58-L82】.

#### Source Code

```{literalinclude} ../../../src/simulation/engines/adaptive_integrator.py
:language: python
:pyobject: rk45_step
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Callable, Tuple, Optional`
- `import numpy as np`


## Advanced Mathematical Theory

### Adaptive Step Size Control

**Error estimation (embedded RK pairs):**

```{math}
\epsilon_n = \|\vec{x}_{n+1}^{\text{high}} - \vec{x}_{n+1}^{\text{low}}\|
```

**Step size adaptation:**

```{math}
h_{\text{new}} = h \cdot \min\left(f_{\max}, \max\left(f_{\min}, f \cdot \left(\frac{\text{tol}}{\epsilon}\right)^{1/p}\right)\right)
```

where:
- $p$ is the lower order of the embedded pair
- $f, f_{\min}, f_{\max}$ are safety factors

### Runge-Kutta-Fehlberg (RK45)

**Fourth-order solution:**

```{math}
\vec{x}_{n+1}^{(4)} = \vec{x}_n + h\sum_{i=1}^{6} b_i \vec{k}_i
```

**Fifth-order solution:**

```{math}
\vec{x}_{n+1}^{(5)} = \vec{x}_n + h\sum_{i=1}^{6} b_i^* \vec{k}_i
```

**Butcher tableau coefficients:**

```{math}
\vec{k}_i = \vec{f}\left(t_n + c_i h, \vec{x}_n + h\sum_{j=1}^{i-1} a_{ij}\vec{k}_j\right)
```

### Dormand-Prince Method

**Fifth-order accurate with fourth-order error estimate:**

```{math}
\begin{align}
\text{Solution:} \quad &\vec{x}_{n+1} = \vec{x}_n + h\sum_{i=1}^{7} b_i \vec{k}_i \quad O(h^6) \\
\text{Error Est:} \quad &\epsilon_n = h\sum_{i=1}^{7} (b_i - b_i^*) \vec{k}_i \quad O(h^5)
\end{align}
```

### Step Acceptance Criteria

**Accept step if:**

```{math}
\epsilon_n \leq \text{tol} \cdot \max(\|\vec{x}_n\|, \|\vec{x}_{n+1}\|)
```

**Reject and retry with:**

```{math}
h_{\text{retry}} = h \cdot \max\left(0.1, 0.9\left(\frac{\text{tol}}{\epsilon_n}\right)^{1/p}\right)
```

## Architecture Diagram

```{mermaid}
graph TD
    A[x_n, t_n, h] --> B[Embedded RK Step]

    B --> C[High-Order Solution]
    B --> D[Low-Order Solution]

    C --> E[x_n+1^high_]
    D --> F[x_n+1^low_]

    E --> G[Error Estimate]
    F --> G

    G --> H[ε = ||x^high - x^low||]
    H --> I{ε ≤ tol?}

    I -->|Yes| J[Accept Step]
    I -->|No| K[Reject Step]

    J --> L[Update h_new]
    L --> M[h_new = h·_tol/ε_^1/p]

    K --> N[Reduce h]
    N --> O[h_new = 0.5·h]
    O --> B

    M --> P[x_n+1, t_n+1_]
    P --> Q{t < T?}
    Q -->|Yes| A
    Q -->|No| R[Final Solution]

    style J fill:#9f9
    style K fill:#f99
    style P fill:#9cf
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
