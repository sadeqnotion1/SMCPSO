# simulation.core.time_domain

**Source:** `src\simulation\core\time_domain.py`

## Module Overview

Time domain management and scheduling utilities for simulation framework.

## Complete Source Code

```{literalinclude} ../../../src/simulation/core/time_domain.py
:language: python
:linenos:
```



## Classes

### `TimeManager`

Manages time-related aspects of simulation execution.

#### Source Code

```{literalinclude} ../../../src/simulation/core/time_domain.py
:language: python
:pyobject: TimeManager
:linenos:
```

#### Methods (12)

##### `__init__(self, dt, total_time, horizon)`

Initialize time manager.

[View full source →](#method-timemanager-__init__)

##### `current_time(self)`

Current simulation time.

[View full source →](#method-timemanager-current_time)

##### `current_step(self)`

Current simulation step.

[View full source →](#method-timemanager-current_step)

##### `progress(self)`

Simulation progress as fraction (0.0 to 1.0).

[View full source →](#method-timemanager-progress)

##### `start_simulation(self)`

Mark simulation start time.

[View full source →](#method-timemanager-start_simulation)

##### `advance_step(self, dt)`

Advance simulation by one time step.

[View full source →](#method-timemanager-advance_step)

##### `is_finished(self)`

Check if simulation is complete.

[View full source →](#method-timemanager-is_finished)

##### `remaining_time(self)`

Get remaining simulation time.

[View full source →](#method-timemanager-remaining_time)

##### `remaining_steps(self)`

Get remaining simulation steps.

[View full source →](#method-timemanager-remaining_steps)

##### `get_time_vector(self)`

Generate time vector for current simulation.

[View full source →](#method-timemanager-get_time_vector)

##### `wall_clock_elapsed(self)`

Get elapsed wall clock time since simulation start.

[View full source →](#method-timemanager-wall_clock_elapsed)

##### `real_time_factor(self)`

Compute real-time factor (simulation_time / wall_clock_time).

[View full source →](#method-timemanager-real_time_factor)



### `RealTimeScheduler`

Scheduler for real-time simulation execution.

#### Source Code

```{literalinclude} ../../../src/simulation/core/time_domain.py
:language: python
:pyobject: RealTimeScheduler
:linenos:
```

#### Methods (5)

##### `__init__(self, target_dt, tolerance)`

Initialize real-time scheduler.

[View full source →](#method-realtimescheduler-__init__)

##### `start_step(self)`

Mark start of a real-time step.

[View full source →](#method-realtimescheduler-start_step)

##### `wait_for_next_step(self)`

Wait until next step deadline.

[View full source →](#method-realtimescheduler-wait_for_next_step)

##### `get_timing_stats(self)`

Get real-time execution statistics.

[View full source →](#method-realtimescheduler-get_timing_stats)

##### `reset(self)`

Reset scheduler state.

[View full source →](#method-realtimescheduler-reset)



### `AdaptiveTimeStep`

Adaptive time step management for integration.

#### Source Code

```{literalinclude} ../../../src/simulation/core/time_domain.py
:language: python
:pyobject: AdaptiveTimeStep
:linenos:
```

#### Methods (3)

##### `__init__(self, initial_dt, min_dt, max_dt, safety_factor, growth_factor, shrink_factor)`

Initialize adaptive time step controller.

[View full source →](#method-adaptivetimestep-__init__)

##### `update_step_size(self, error_estimate, tolerance)`

Update time step based on error estimate.

[View full source →](#method-adaptivetimestep-update_step_size)

##### `get_statistics(self)`

Get adaptive time step statistics.

[View full source →](#method-adaptivetimestep-get_statistics)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import time`
- `from typing import Any, Dict, List, Optional, Tuple, Callable`
- `import numpy as np`


## Advanced Mathematical Theory

### Continuous-Time Evolution

**Initial value problem (IVP):**

```{math}
\begin{cases}
\dot{\vec{x}}(t) = \vec{f}(\vec{x}, u, t) \\
\vec{x}(t_0) = \vec{x}_0
\end{cases}
```

**Existence and uniqueness (Picard-Lindelöf):**

If $\vec{f}$ is Lipschitz continuous:

```{math}
\|\vec{f}(\vec{x}_1, u, t) - \vec{f}(\vec{x}_2, u, t)\| \leq L\|\vec{x}_1 - \vec{x}_2\|
```

then a unique solution exists.

### Discrete-Time Grid

**Uniform time discretization:**

```{math}
t_n = t_0 + n \cdot h, \quad n = 0, 1, 2, \ldots, N
```

**Adaptive time grid:**

```{math}
h_n = h(\epsilon_n, p), \quad t_{n+1} = t_n + h_n
```

where $\epsilon_n$ is local error estimate.

### Time Integration Accuracy

**Consistency:**

```{math}
\lim_{h \to 0} \frac{\Phi(\vec{f}, \vec{x}, t, h) - \vec{f}(\vec{x}, u, t)}{h} = 0
```

**Convergence:**

```{math}
\lim_{h \to 0, \, nh = T} \vec{x}_n = \vec{x}(T)
```

**Stability (A-stability for stiff systems):**

```{math}
|\Phi(\lambda h)| \leq 1, \quad \forall \, \text{Re}(\lambda) < 0
```

## Architecture Diagram

```{mermaid}
graph TD
    A[t_0, x_0] --> B[Time Step Selection]
    B --> C{Adaptive?}

    C -->|Fixed| D[h = const]
    C -->|Adaptive| E[h_n = f_ε, p_]

    D --> F[Integration Step]
    E --> G[Error Estimation]
    G --> H[Step Size Control]
    H --> F

    F --> I[x_n+1 = x_n + h·Φ_·_]
    I --> J[Validation]

    J --> K{Valid?}
    K -->|No| L[Step Rejection]
    L --> M[h_new = h/2]
    M --> F

    K -->|Yes| N[t_n+1, x_n+1_]
    N --> O{t < T?}
    O -->|Yes| B
    O -->|No| P[Final State]

    style F fill:#9cf
    style I fill:#9f9
    style L fill:#f99
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
