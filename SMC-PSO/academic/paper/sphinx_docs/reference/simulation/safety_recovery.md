# simulation.safety.recovery

**Source:** `src\simulation\safety\recovery.py`

## Module Overview

Safety recovery strategies for simulation framework.

## Complete Source Code

```{literalinclude} ../../../src/simulation/safety/recovery.py
:language: python
:linenos:
```



## Classes

### `RecoveryStrategy`

**Inherits from:** `ABC`

Base class for safety recovery strategies.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/recovery.py
:language: python
:pyobject: RecoveryStrategy
:linenos:
```

#### Methods (1)

##### `recover(self, state, control, violation_info)`

Implement recovery strategy.

[View full source →](#method-recoverystrategy-recover)



### `EmergencyStop`

**Inherits from:** `RecoveryStrategy`

Emergency stop recovery strategy.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/recovery.py
:language: python
:pyobject: EmergencyStop
:linenos:
```

#### Methods (1)

##### `recover(self, state, control, violation_info)`

Apply emergency stop - zero control and hold state.

[View full source →](#method-emergencystop-recover)



### `StateLimiter`

**Inherits from:** `RecoveryStrategy`

State limiting recovery strategy.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/recovery.py
:language: python
:pyobject: StateLimiter
:linenos:
```

#### Methods (2)

##### `__init__(self, lower_bounds, upper_bounds)`

Initialize state limiter.

[View full source →](#method-statelimiter-__init__)

##### `recover(self, state, control, violation_info)`

Clip state to bounds and reduce control.

[View full source →](#method-statelimiter-recover)



### `SafetyRecovery`

Safety recovery manager.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/recovery.py
:language: python
:pyobject: SafetyRecovery
:linenos:
```

#### Methods (3)

##### `__init__(self)`

Initialize safety recovery manager.

[View full source →](#method-safetyrecovery-__init__)

##### `register_strategy(self, violation_type, strategy)`

Register recovery strategy for specific violation type.

[View full source →](#method-safetyrecovery-register_strategy)

##### `apply_recovery(self, state, control, violation_info)`

Apply appropriate recovery strategy.

[View full source →](#method-safetyrecovery-apply_recovery)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Optional`
- `import numpy as np`


## Advanced Mathematical Theory

### Constraint Violation Recovery

**Projection onto safe set:**

```{math}
\vec{x}_{\text{safe}} = \text{proj}_{\mathcal{X}}(\vec{x}_{\text{unsafe}}) = \arg\min_{\tilde{\vec{x}} \in \mathcal{X}} \|\vec{x}_{\text{unsafe}} - \tilde{\vec{x}}\|
```

**Box constraints:**

If $\mathcal{X} = \{\vec{x} : \vec{x}_{\min} \leq \vec{x} \leq \vec{x}_{\max}\}$, then:

```{math}
x_i^{\text{safe}} = \max(x_i^{\min}, \min(x_i, x_i^{\max}))
```

### Control Barrier Function Recovery

**Quadratic program (QP) formulation:**

```{math}
\begin{align}
u^* &= \arg\min_{u \in \mathcal{U}} \|u - u_{\text{nom}}\|^2 \\
&\text{subject to: } \dot{B}(\vec{x}, u) \geq -\alpha(B(\vec{x}))
\end{align}
```

where:
- $B(\vec{x}) \geq 0$ is the barrier function (safe if $B \geq 0$)
- $\alpha(\cdot)$ is a class-$\mathcal{K}$ function (e.g., $\alpha(B) = kB$)

**Safety guarantee:**

If $B(\vec{x}_0) \geq 0$ and the QP is feasible, then $B(\vec{x}(t)) \geq 0$ for all $t \geq 0$.

### Graceful Degradation Hierarchy

**Performance degradation modes:**

```{math}
\text{Mode} = \begin{cases}
\text{Normal} & \text{if no violations} \\
\text{Degraded} & \text{if soft violations} \\
\text{Safe Stop} & \text{if hard violations}
\end{cases}
```

**Fallback control law:**

```{math}
u = \begin{cases}
u_{\text{optimal}} & \text{if } B(\vec{x}) > \delta_{\text{high}} \\
\gamma u_{\text{optimal}} + (1-\gamma) u_{\text{safe}} & \text{if } \delta_{\text{low}} < B(\vec{x}) \leq \delta_{\text{high}} \\
u_{\text{safe}} & \text{if } B(\vec{x}) \leq \delta_{\text{low}}
\end{cases}
```

where $\gamma = \frac{B - \delta_{\text{low}}}{\delta_{\text{high}} - \delta_{\text{low}}}$ (linear interpolation).

## Architecture Diagram

```{mermaid}
graph TD
    A[Constraint Violation] --> B{Violation Type}

    B -->|State| C[State Projection]
    B -->|Control| D[Control Saturation]
    B -->|Joint| E[QP Solver]

    C --> F[proj_X__x_unsafe_]
    D --> G[clip_u, u_min, u_max_]
    E --> H[min ||u - u_nom||^2]

    F --> I[Safe State]
    G --> I
    H --> I

    I --> J{Recovery Mode}
    J -->|Normal| K[Resume]
    J -->|Degraded| L[Fallback Controller]
    J -->|Critical| M[Emergency Stop]

    L --> N[Safe Baseline]
    M --> O[Abort Simulation]

    style I fill:#9f9
    style O fill:#f00
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
