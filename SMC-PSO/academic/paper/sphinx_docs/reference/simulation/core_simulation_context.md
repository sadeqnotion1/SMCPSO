# simulation.core.simulation_context

**Source:** `src\simulation\core\simulation_context.py`

## Module Overview

Enhanced simulation context management with framework integration.

## Complete Source Code

```{literalinclude} ../../../src/simulation/core/simulation_context.py
:language: python
:linenos:
```



## Classes

### `SimulationContext`

Enhanced simulation context with framework integration.

Centralizes simulation setup including configuration loading,
dynamics model selection, and framework component initialization.

#### Source Code

```{literalinclude} ../../../src/simulation/core/simulation_context.py
:language: python
:pyobject: SimulationContext
:linenos:
```

#### Methods (10)

##### `__init__(self, config_path)`

Initialize the simulation context.

[View full source →](#method-simulationcontext-__init__)

##### `_initialize_dynamics_model(self)`

Initialize the dynamics model based on configuration.

[View full source →](#method-simulationcontext-_initialize_dynamics_model)

##### `get_dynamics_model(self)`

Return the initialized dynamics model.

[View full source →](#method-simulationcontext-get_dynamics_model)

##### `get_config(self)`

Return the validated configuration.

[View full source →](#method-simulationcontext-get_config)

##### `create_controller(self, name, gains)`

Create a controller using the configuration.

[View full source →](#method-simulationcontext-create_controller)

##### `create_fdi(self)`

Create FDI system if enabled in configuration.

[View full source →](#method-simulationcontext-create_fdi)

##### `register_component(self, name, component)`

Register a simulation framework component.

[View full source →](#method-simulationcontext-register_component)

##### `get_component(self, name)`

Get a registered component.

[View full source →](#method-simulationcontext-get_component)

##### `create_simulation_engine(self, engine_type)`

Create a simulation engine of specified type.

[View full source →](#method-simulationcontext-create_simulation_engine)

##### `get_simulation_parameters(self)`

Get simulation parameters from configuration.

[View full source →](#method-simulationcontext-get_simulation_parameters)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import logging`
- `from typing import Optional, List, Any, Dict, Union`
- `from src.config import load_config, ConfigSchema`
- `from .interfaces import SimulationEngine`
- `from src.utils.config_compatibility import wrap_physics_config`


## Advanced Mathematical Theory

### Context Management

**Simulation context structure:**

```{math}
\text{Context} = \{\text{Controller}, \text{Dynamics}, \text{Integrator}, \text{Config}, \text{State}\}
```

### Thread-Safe State Isolation

**Context local storage:**

```python
class SimulationContext:
    def __enter__(self):
        # Thread-local context initialization
        return isolated_context

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup and resource release
        pass
```

### Resource Pooling

**Controller/dynamics reuse:**

```{math}
\text{Pool} = \{\text{Resource}_1, \ldots, \text{Resource}_n\}
```

**Allocation strategy:**

```{math}
\text{allocate}(\text{thread}_i) = \begin{cases}
\text{Resource}_k & \text{if available} \\
\text{create\_new}() & \text{if pool full}
\end{cases}
```

### Configuration Validation

**Parameter bounds checking:**

```{math}
\forall \, p \in \text{Config}: \quad p_{\min} \leq p \leq p_{\max}
```

**Physical constraint validation:**

```{math}
\begin{align}
m_i > 0, \quad \ell_i > 0 \quad &\text{(positive mass/length)} \\
g > 0 \quad &\text{(gravity)} \\
I_i > 0 \quad &\text{(positive inertia)}
\end{align}
```

## Architecture Diagram

```{mermaid}
graph TD
    A[Input] --> B[Processing]
    B --> C[Output]

    style B fill:#9cf
    style C fill:#9f9
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
