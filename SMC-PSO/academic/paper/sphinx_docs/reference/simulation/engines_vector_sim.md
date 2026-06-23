# simulation.engines.vector_sim

**Source:** `src\simulation\engines\vector_sim.py`

## Module Overview

Unified simulation façade with vectorized safety guards.

This module provides a high‑level ``simulate`` function that accepts either
scalar or batched initial states and control inputs.  It dispatches the
underlying dynamics step through ``src.simulation.engines.simulation_runner.step`` and
invokes safety guards after each step and before returning results.  The
interface maintains shape parity between scalar and batch modes: a single
simulation returns an array of shape ``(H+1, D)`` while a batch of B
simulations returns a tensor of shape ``(B, H+1, D)``.  The initial state is
always included at index ``0`` of the time dimension.

Early stopping is supported via a simple stop callback: if ``stop_fn`` is
provided and returns True given the current state, all remaining steps are
skipped and the output is truncated to the elapsed horizon plus one.  To
preserve uniform batch shapes, the earliest stopping time across batch
elements truncates the entire batch.

## Complete Source Code

```{literalinclude} ../../../src/simulation/engines/vector_sim.py
:language: python
:linenos:
```



## Functions

### `simulate(initial_state, control_inputs, dt, horizon)`

Simulate a dynamical system forward in time.

Parameters
----------
initial_state : array-like
    Initial state of shape ``(D,)`` or ``(B, D)``.  A missing batch
    dimension implies ``B=1``.
control_inputs : array-like
    Control sequence with shape ``(H,)`` or ``(H, U)`` for scalar runs or
    ``(B, H)``/``(B, H, U)`` for batched runs.  The control dimension U
    must be broadcastable to the state dimension.
dt : float
    Timestep between control inputs.
horizon : int, optional
    Number of simulation steps ``H``.  If not provided it is inferred
    from the length of ``control_inputs``.
energy_limits : float, optional
    Maximum allowed total energy.  When provided the energy guard
    compares ``sum(state**2)`` against this limit after each step.
state_bounds : tuple, optional
    Pair ``(lower, upper)`` specifying per‑dimension bounds.  Bounds may
    be scalars or arrays broadcastable to the state shape.  A ``None``
    value disables that side of the bound.
stop_fn : callable, optional
    Optional predicate ``stop_fn(state)``.  If provided and returns
    True, the simulation stops early and the output is truncated.
t0 : float, default 0.0
    Initial simulation time used in bound violation messages.

Returns
-------
numpy.ndarray
    Array of simulated states including the initial state.  Shape is
    ``(H_stop+1, D)`` for scalar runs or ``(B, H_stop+1, D)`` for
    batched runs, where ``H_stop <= horizon`` if early stopping
    occurred.

Examples
--------
Scalar simulation:

>>> import numpy as np
>>> x0 = np.array([1.0, 0.0])
>>> u = np.array([0.1, 0.2])
>>> result = simulate(x0, u, 0.1)
>>> result.shape
(3, 2)
>>> result[0]  # initial state
array([1., 0.])

Batch simulation with early stopping:

>>> x0_batch = np.array([[1.0, 0.0], [2.0, 1.0]])  
>>> u_batch = np.array([[0.1, 0.2], [0.3, 0.4]])
>>> stop_fn = lambda x: np.sum(x**2) > 10.0
>>> result = simulate(x0_batch, u_batch, 0.1, stop_fn=stop_fn)
>>> result.shape[0] == 2  # batch size preserved
True
>>> result.shape[1] <= 3  # may be truncated due to early stop
True

#### Source Code

```{literalinclude} ../../../src/simulation/engines/vector_sim.py
:language: python
:pyobject: simulate
:linenos:
```



### `simulate_system_batch()`

Vectorised batch simulation of multiple controllers.

This function wraps ``run_simulation`` to simultaneously simulate a batch
of controllers with distinct gain vectors (``particles``).  It returns
time, state, control and sliding-surface arrays for the entire batch.
Optional early stopping is available: once the magnitude of the sliding
surface ``sigma`` falls below ``convergence_tol`` for all particles (after
a grace period), integration halts early and the outputs are truncated.

When ``params_list`` is provided, the simulation is repeated for each
element in the list.  The return value is then a list of results, one per
parameter set.  For backward compatibility, the dynamics model is
determined internally by the controller factory; perturbed physics
parameters are ignored and results are replicated across the list.

Parameters
----------
controller_factory : callable
    Factory ``controller_factory(p)`` that returns a controller given a
    gain vector ``p``.  The returned controller must expose a
    ``dynamics_model`` attribute defining the system dynamics.
particles : array-like
    Array of shape ``(B, G)`` where each row contains a gain vector for
    one particle.  A single particle may be provided as shape ``(G,)``.
sim_time : float
    Total simulation duration (seconds).
dt : float
    Timestep for integration (seconds).
u_max : float, optional
    Control saturation limit.  Overrides controller-specific ``max_force``.
seed : int, optional
    Deprecated.  Ignored; retained for signature compatibility.
params_list : iterable, optional
    Optional list of physics parameter objects.  When provided, the
    simulation is repeated for each element.  The current implementation
    ignores these parameters and replicates the base results.
initial_state : array-like, optional
    Initial state(s) for the batch.  If ``None``, a zero state is used.
    If a 1D array of length ``D`` is provided, it is broadcast across all
    particles.  If a 2D array of shape ``(B, D)`` is provided, it is used
    directly.
convergence_tol : float, optional
    Threshold for sliding-surface convergence.  When provided and
    positive, the integration stops once ``max(|sigma|) < convergence_tol``
    across all particles (after the grace period).
grace_period : float, optional
    Duration (seconds) to wait before checking the convergence criterion.
rng : numpy.random.Generator, optional
    Unused in this implementation.  Present for API compatibility.

Returns
-------
If ``params_list`` is not provided, returns a tuple ``(t, x_b, u_b, sigma_b)``:

- ``t``: ndarray of shape ``(N+1,)`` of time points
- ``x_b``: ndarray of shape ``(B, N+1, D)`` of states
- ``u_b``: ndarray of shape ``(B, N)`` of controls
- ``sigma_b``: ndarray of shape ``(B, N)`` of sliding-surface values

If ``params_list`` is provided, returns a list of such tuples (one per
element in ``params_list``).

#### Source Code

```{literalinclude} ../../../src/simulation/engines/vector_sim.py
:language: python
:pyobject: simulate_system_batch
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `from typing import Any, Callable, Optional, Tuple`
- `from .simulation_runner import step as _step_fn`
- `from ..context.safety_guards import _guard_no_nan, _guard_energy, _guard_bounds`


## Advanced Mathematical Theory

### Batch Simulation

**Vectorized state evolution:**

```{math}
\vec{X} = [\vec{x}^{(1)}, \vec{x}^{(2)}, \ldots, \vec{x}^{(B)}]^T \in \mathbb{R}^{B \times n}
```

**Batch integration:**

```{math}
\vec{X}_{k+1} = \vec{X}_k + h \cdot \vec{F}(\vec{X}_k, \vec{U}_k, t_k)
```

where $\vec{F}$ is vectorized dynamics.

### Numba JIT Compilation

**Just-In-Time compilation:**

```python
@numba.jit(nopython=True, parallel=True)
def batch_integrate(X, U, dt, N):
    for i in numba.prange(B):  # Parallel loop
        X[i] = integrate_single(X[i], U[i], dt, N)
    return X
```

**Performance gain:**

```{math}
\text{Speedup} = \frac{T_{\text{Python}}}{T_{\text{Numba}}} \approx 10-100\times
```

### Memory Layout Optimization

**Cache-friendly memory access:**

```{math}
\text{Stride}_1 \text{ (contiguous)} < \text{Stride}_2 \text{ (non-contiguous)}
```

**Optimal array layout:**

```python
# Good: C-contiguous
X = np.ascontiguousarray(X)  # Row-major

# Bad: Non-contiguous views
X_bad = X[:, ::2]  # Strided access
```

## Parallel Efficiency

**Amdahl's Law:**

```{math}
\text{Speedup} = \frac{1}{(1 - P) + \frac{P}{N_{\text{cores}}}}
```

where $P$ is parallelizable fraction.

## Architecture Diagram

```{mermaid}
graph TD
    A[Batch Initial States X_0] --> B[Numba JIT Compilation]

    B --> C[Parallel Thread Pool]
    C --> D[Thread 1: X_1_]
    C --> E[Thread 2: X_2_]
    C --> F[Thread B: X_B_]

    D --> G[Single Integration]
    E --> G
    F --> G

    G --> H[Vectorized Dynamics]
    H --> I[f_X, U, t_]

    I --> J[Batch State Update]
    J --> K[X_n+1 = X_n + h·F_·_]

    K --> L{All Converged?}
    L -->|No| C
    L -->|Yes| M[Gather Results]

    M --> N[Batch Trajectories]
    N --> O[Statistics Computation]

    style B fill:#9cf
    style H fill:#ff9
    style N fill:#9f9
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
