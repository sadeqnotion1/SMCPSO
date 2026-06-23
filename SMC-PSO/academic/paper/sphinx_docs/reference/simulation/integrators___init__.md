# simulation.integrators.__init__

**Source:** `src\simulation\integrators\__init__.py`

## Module Overview

Numerical integration methods for simulation framework.

## Complete Source Code

```{literalinclude} ../../../src/simulation/integrators/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .base import BaseIntegrator`
- `from .adaptive.runge_kutta import AdaptiveRungeKutta, DormandPrince45`
- `from .fixed_step.euler import ForwardEuler, BackwardEuler`
- `from .fixed_step.runge_kutta import RungeKutta4, RungeKutta2`
- `from .discrete.zero_order_hold import ZeroOrderHold`
- `from .factory import IntegratorFactory, create_integrator, get_available_integrators`


## Advanced Mathematical Theory

### Integrators Module Architecture

**Integrator hierarchy:**

```{math}
\text{Integrator} = \begin{cases}
\text{FixedStep} & \text{(Euler, RK4)} \\
\text{Adaptive} & \text{(RK45, Dormand-Prince)} \\
\text{Discrete} & \text{(ZOH, Tustin)}
\end{cases}
```

### Unified Integration Interface

**Standard API contract:**

```{math}
\vec{x}_{n+1} = \text{integrate}(\vec{f}, \vec{x}_n, u_n, t_n, h)
```

**Properties:**
- **Order:** $p$ (local truncation error $O(h^{p+1})$)
- **Stability:** A-stability, L-stability, or conditional stability
- **Adaptive:** Boolean flag for variable step size support

### Method Selection Criteria

**Computational cost:**

```{math}
C_{\text{total}} = N_{\text{steps}} \cdot C_{\text{step}}
```

where $C_{\text{step}}$ is cost per step (function evaluations $\times$ complexity).

**Accuracy vs. efficiency tradeoff:**

For error tolerance $\epsilon$:
- Euler: $N \approx O(\epsilon^{-1})$
- RK4: $N \approx O(\epsilon^{-1/4})$
- Adaptive RK45: $N \approx O(\epsilon^{-1/5})$ with automatic step control

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
