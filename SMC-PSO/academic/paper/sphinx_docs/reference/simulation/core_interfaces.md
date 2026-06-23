# simulation.core.interfaces

**Source:** `src\simulation\core\interfaces.py`

## Module Overview

Abstract base classes defining simulation framework interfaces.

## Complete Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:linenos:
```



## Classes

### `SimulationEngine`

**Inherits from:** `ABC`

Base interface for all simulation engines.

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: SimulationEngine
:linenos:
```

#### Methods (1)

##### `step(self, state, control, dt)`

Execute a single simulation step.

[View full source →](#method-simulationengine-step)



### `Integrator`

**Inherits from:** `ABC`

Base interface for numerical integration methods.

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: Integrator
:linenos:
```

#### Methods (3)

##### `integrate(self, dynamics_fn, state, control, dt)`

Integrate dynamics forward by one time step.

[View full source →](#method-integrator-integrate)

##### `order(self)`

Integration method order.

[View full source →](#method-integrator-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-integrator-adaptive)



### `Orchestrator`

**Inherits from:** `ABC`

Base interface for simulation execution strategies.

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: Orchestrator
:linenos:
```

#### Methods (1)

##### `execute(self, initial_state, control_inputs, dt, horizon)`

Execute simulation with specified strategy.

[View full source →](#method-orchestrator-execute)



### `SimulationStrategy`

**Inherits from:** `ABC`

Base interface for simulation analysis strategies (Monte Carlo, sensitivity, etc.).

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: SimulationStrategy
:linenos:
```

#### Methods (1)

##### `analyze(self, simulation_fn, parameters)`

Perform strategy-specific analysis.

[View full source →](#method-simulationstrategy-analyze)



### `SafetyGuard`

**Inherits from:** `ABC`

Base interface for safety monitoring and constraints.

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: SafetyGuard
:linenos:
```

#### Methods (2)

##### `check(self, state, step_idx)`

Check safety conditions.

[View full source →](#method-safetyguard-check)

##### `get_violation_message(self)`

Get description of last safety violation.

[View full source →](#method-safetyguard-get_violation_message)



### `ResultContainer`

**Inherits from:** `ABC`

Base interface for simulation result containers.

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: ResultContainer
:linenos:
```

#### Methods (4)

##### `add_trajectory(self, states, times)`

Add a simulation trajectory to results.

[View full source →](#method-resultcontainer-add_trajectory)

##### `get_states(self)`

Get state trajectories.

[View full source →](#method-resultcontainer-get_states)

##### `get_times(self)`

Get time vectors.

[View full source →](#method-resultcontainer-get_times)

##### `export(self, format_type, filepath)`

Export results to specified format.

[View full source →](#method-resultcontainer-export)



### `DataLogger`

**Inherits from:** `ABC`

Base interface for simulation data logging.

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: DataLogger
:linenos:
```

#### Methods (2)

##### `log_step(self, step_data)`

Log data from a simulation step.

[View full source →](#method-datalogger-log_step)

##### `finalize(self)`

Finalize logging and cleanup resources.

[View full source →](#method-datalogger-finalize)



### `PerformanceMonitor`

**Inherits from:** `ABC`

Base interface for performance monitoring.

#### Source Code

```{literalinclude} ../../../src/simulation/core/interfaces.py
:language: python
:pyobject: PerformanceMonitor
:linenos:
```

#### Methods (3)

##### `start_timing(self, operation)`

Start timing an operation.

[View full source →](#method-performancemonitor-start_timing)

##### `end_timing(self, operation)`

End timing and return elapsed time.

[View full source →](#method-performancemonitor-end_timing)

##### `get_statistics(self)`

Get performance statistics.

[View full source →](#method-performancemonitor-get_statistics)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, List, Optional, Tuple, Union, Callable`
- `import numpy as np`


## Advanced Mathematical Theory

### Simulation Engine Architecture

**Abstract interface design:**

```{math}
\text{SimulationEngine} = \{\text{step}, \text{reset}, \text{validate}\}
```

### Numerical Integration Interface

**Integration step contract:**

```{math}
\vec{x}_{n+1} = \vec{x}_n + h \cdot \text{integrator}(\vec{f}, \vec{x}_n, t_n, h, u_n)
```

where:
- $\vec{x}_n$ is state at time $t_n$
- $h$ is time step
- $\vec{f}(\vec{x}, u, t)$ is dynamics function
- $u_n$ is control input

### State Evolution Protocol

**Continuous-time dynamics:**

```{math}
\frac{d\vec{x}}{dt} = \vec{f}(\vec{x}, u, t)
```

**Discrete-time approximation:**

```{math}
\vec{x}_{n+1} \approx \vec{x}_n + h \cdot \Phi(\vec{f}, \vec{x}_n, t_n, h)
```

where $\Phi$ is the numerical method (Euler, RK4, etc.).

### Error Propagation

**Local truncation error:**

```{math}
\tau_n = \vec{x}(t_{n+1}) - \vec{x}_{n+1} = O(h^{p+1})
```

**Global error accumulation:**

```{math}
e_n = \vec{x}(t_n) - \vec{x}_n = O(h^p)
```

where $p$ is the order of the method.

## Architecture Diagram

```{mermaid}
graph TD
    A[Simulation Request] --> B{Engine Type}

    B -->|Fixed-Step| C[Fixed-Step Engine]
    B -->|Adaptive| D[Adaptive Engine]
    B -->|Discrete| E[Discrete Engine]

    C --> F[Integrator Interface]
    D --> F
    E --> G[Discrete Dynamics]

    F --> H[Euler]
    F --> I[RK4]
    F --> J[RK45]

    H --> K[State Update]
    I --> K
    J --> K
    G --> K

    K --> L[Validation]
    L --> M{Valid?}
    M -->|Yes| N[Next Step]
    M -->|No| O[Error Handler]

    style F fill:#9cf
    style K fill:#9f9
    style O fill:#f99
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
