# simulation.integrators.compatibility

**Source:** `src\simulation\integrators\compatibility.py`

## Module Overview

Integrator compatibility wrapper for simulation engine integration.

This module provides compatibility wrappers to bridge the interface mismatch between
simulation engines that expect dynamics_model.step(x, u, dt) and integrators that
expect dynamics_fn(t, x, u) -> dx/dt. It ensures integration of adaptive
and fixed-step integrators with the simulation framework.

## Complete Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:linenos:
```



## Classes

### `DynamicsCompatibilityWrapper`

Wrapper to make integrators compatible with simulation dynamics interface.

Converts between:
- Simulation interface: dynamics_model.step(state, control, dt) -> next_state
- Integrator interface: dynamics_fn(time, state, control) -> state_derivative

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: DynamicsCompatibilityWrapper
:linenos:
```

#### Methods (3)

##### `__init__(self, integrator, dynamics_fn)`

Initialize compatibility wrapper.

[View full source →](#method-dynamicscompatibilitywrapper-__init__)

##### `step(self, state, control, dt)`

Step the dynamics using the wrapped integrator.

[View full source →](#method-dynamicscompatibilitywrapper-step)

##### `reset_time(self, t)`

Reset the internal time counter.

[View full source →](#method-dynamicscompatibilitywrapper-reset_time)



### `LegacyDynamicsWrapper`

Wrapper to adapt legacy dynamics models to integrator interface.

Converts from:
- Legacy interface: dynamics.step(state, control, dt) -> next_state
To:
- Integrator interface: dynamics_fn(t, x, u) -> dx/dt

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: LegacyDynamicsWrapper
:linenos:
```

#### Methods (2)

##### `__init__(self, legacy_dynamics)`

Initialize legacy wrapper.

[View full source →](#method-legacydynamicswrapper-__init__)

##### `__call__(self, t, state, control)`

Convert legacy step to derivative function.

[View full source →](#method-legacydynamicswrapper-__call__)



### `IntegratorSafetyWrapper`

Safety wrapper for integrators to handle edge cases and errors gracefully.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: IntegratorSafetyWrapper
:linenos:
```

#### Methods (4)

##### `__init__(self, base_integrator, fallback_integrator)`

Initialize safety wrapper.

[View full source →](#method-integratorsafetywrapper-__init__)

##### `integrate(self, dynamics_fn, state, control, dt)`

Safely integrate with automatic fallback on failure.

[View full source →](#method-integratorsafetywrapper-integrate)

##### `_safe_fallback_integrate(self, dynamics_fn, state, control, dt)`

Safely integrate using fallback method.

[View full source →](#method-integratorsafetywrapper-_safe_fallback_integrate)

##### `reset(self)`

Reset the safety wrapper state.

[View full source →](#method-integratorsafetywrapper-reset)



## Functions

### `create_compatible_dynamics(integrator_type, dynamics_fn, legacy_dynamics)`

Create a dynamics model compatible with simulation engines.

Parameters
----------
integrator_type : str
    Type of integrator ('euler', 'rk4', 'rk45', 'dopri45')
dynamics_fn : callable, optional
    Dynamics function with signature (t, x, u) -> dx/dt
legacy_dynamics : object, optional
    Legacy dynamics with step(x, u, dt) method
**integrator_kwargs
    Additional arguments for integrator initialization

Returns
-------
DynamicsCompatibilityWrapper
    Wrapped dynamics model compatible with simulation engines

Examples
--------
>>> def pendulum_dynamics(t, x, u):
...     return np.array([x[1], -np.sin(x[0]) - 0.1*x[1] + u])
>>>
>>> dynamics = create_compatible_dynamics('rk4', pendulum_dynamics)
>>> next_state = dynamics.step(np.array([0.1, 0.0]), 0.5, 0.01)

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: create_compatible_dynamics
:linenos:
```



### `create_safe_integrator(integrator_type)`

Create a safety-wrapped integrator.

Parameters
----------
integrator_type : str
    Type of integrator
**kwargs
    Integrator parameters

Returns
-------
IntegratorSafetyWrapper
    Safety-wrapped integrator

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: create_safe_integrator
:linenos:
```



### `create_robust_euler_dynamics(dynamics_fn)`

Create robust Euler-integrated dynamics.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: create_robust_euler_dynamics
:linenos:
```



### `create_robust_rk4_dynamics(dynamics_fn)`

Create robust RK4-integrated dynamics.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: create_robust_rk4_dynamics
:linenos:
```



### `create_robust_adaptive_dynamics(dynamics_fn, rtol, atol)`

Create robust adaptive-integrated dynamics.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/compatibility.py
:language: python
:pyobject: create_robust_adaptive_dynamics
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Callable, Any, Optional, Union`
- `import numpy as np`
- `from .base import BaseIntegrator`
- `from .fixed_step.euler import ForwardEuler`
- `from .fixed_step.runge_kutta import RungeKutta4`
- `from .adaptive.runge_kutta import DormandPrince45`


## Advanced Mathematical Theory

### Backward Compatibility Layer

**Interface abstraction:**

```python
class CompatibilityIntegrator:
    def integrate(self, dynamics, state, control, dt):
        # Dispatch to appropriate method
        pass
```

**Method dispatch based on features:**

```{math}
\text{Method} = \begin{cases}
\text{Adaptive} & \text{if adaptive supported and requested} \\
\text{FixedStep} & \text{if high accuracy required} \\
\text{Discrete} & \text{if linear system detected}
\end{cases}
```

### Performance Profiling

**Execution time per method:**

```{math}
t_{\text{method}} = \sum_{i=1}^{N} t_i^{\text{step}}
```

**Efficiency ratio:**

```{math}
\eta = \frac{\text{Accuracy}}{\text{Computational Cost}} = \frac{1/\epsilon}{N \cdot C_{\text{step}}}
```

**Optimal method selection:**

```{math}
\text{Method}^* = \arg\max_{\text{Method}} \eta_{\text{Method}}
```

## Architecture Diagram

```{mermaid}
graph TD
    A[Subsystem Input] --> B[Processing Pipeline]
    B --> C[Component 1]
    B --> D[Component 2]

    C --> E[Integration]
    D --> E

    E --> F[Output]

    style E fill:#9cf
    style F fill:#9f9
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
