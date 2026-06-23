# simulation.safety.monitors

**Source:** `src\simulation\safety\monitors.py`

## Module Overview Performance

and safety monitoring for simulation execution

.

## Complete Source Code ```

{literalinclude}

../../../src/simulation/safety/monitors.py


:language: python
:linenos:
```

---

## Classes

### `SimulationPerformanceMonitor`

**Inherits from:** `PerformanceMonitor` Monitor simulation execution performance.

#### Source Code ```

{literalinclude} ../../../src/simulation/safety/monitors.py
:language: python
:pyobject: SimulationPerformanceMonitor
:linenos:
``` #### Methods (4) ##### `__init__(self)` Initialize performance monitor. [View full source →](#method-simulationperformancemonitor-__init__) ##### `start_timing(self, operation)` Start timing an operation. [View full source →](#method-simulationperformancemonitor-start_timing) ##### `end_timing(self, operation)` End timing and return elapsed time. [View full source →](#method-simulationperformancemonitor-end_timing) ##### `get_statistics(self)` Get performance statistics. [View full source →](#method-simulationperformancemonitor-get_statistics)

---

## `SafetyMonitor`

Monitor safety violations and system health.

### Source Code ```

{literalinclude} ../../../src/simulation/safety/monitors.py

:language: python
:pyobject: SafetyMonitor
:linenos:
``` #### Methods (5) ##### `__init__(self)` Initialize safety monitor. [View full source →](#method-safetymonitor-__init__) ##### `record_violation(self, violation_type, message, step)` Record a safety violation. [View full source →](#method-safetymonitor-record_violation) ##### `record_warning(self, warning_type, message, step)` Record a safety warning. [View full source →](#method-safetymonitor-record_warning) ##### `get_safety_report(self)` Get safety report. [View full source →](#method-safetymonitor-get_safety_report) ##### `_compute_safety_score(self)` Compute overall safety score (0-1, higher is better). [View full source →](#method-safetymonitor-_compute_safety_score)

### `SystemHealthMonitor`

Monitor overall system health and performance.

#### Source Code ```

{literalinclude} ../../../src/simulation/safety/monitors.py
:language: python
:pyobject: SystemHealthMonitor
:linenos:
``` #### Methods (5) ##### `__init__(self, history_length)` Initialize system health monitor. [View full source →](#method-systemhealthmonitor-__init__) ##### `update(self, state, control, metrics)` Update system health with new data. [View full source →](#method-systemhealthmonitor-update) ##### `get_health_status(self)` Get current system health status. [View full source →](#method-systemhealthmonitor-get_health_status) ##### `_analyze_stability(self, states)` Analyze state stability (0-1, higher is more stable). [View full source →](#method-systemhealthmonitor-_analyze_stability) ##### `_analyze_control_effort(self, controls)` Analyze control effort (0-1, higher means more effort). [View full source →](#method-systemhealthmonitor-_analyze_control_effort)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `import time`
- `from typing import Any, Dict, List, Optional`
- `import numpy as np`
- `from ..core.interfaces import PerformanceMonitor` ## Advanced Mathematical Theory ### Real-Time Performance Monitoring **Execution time measurement:** ```{math}
t_{\text{exec}} = t_{\text{end}} - t_{\text{start}}
``` **Deadline monitoring:** ```{math}
\text{Violation} = \begin{cases}
1 & \text{if } t_{\text{exec}} > t_{\text{deadline}} \\
0 & \text{otherwise}
\end{cases}
``` **Throughput:** ```{math}

\lambda = \frac{N_{\text{steps}}}{T_{\text{total}}} \quad \text{[steps/sec]}
``` ### Statistical Performance Metrics **Mean execution time:** ```{math}
\mu = \frac{1}{N}\sum_{i=1}^N t_i
``` **Variance and standard deviation:** ```{math}

\sigma^2 = \frac{1}{N}\sum_{i=1}^N (t_i - \mu)^2, \quad \sigma = \sqrt{\sigma^2}
``` **Percentiles for deadline guarantees:** ```{math}
p_{95} = \inf\{x : F(x) \geq 0.95\}
``` where $F(x)$ is the empirical CDF. ### Real-Time Scheduling Theory **Weakly-hard (m, k) constraints:** Out of any $k$ consecutive deadlines, at most $m$ can be missed: ```{math}

\sum_{i=n-k+1}^{n} \mathbb{1}_{\text{miss}}(i) \leq m
``` **Average case deadline guarantee:** ```{math}
P(t_{\text{exec}} \leq t_{\text{deadline}}) \geq 1 - \epsilon
``` for some small $\epsilon > 0$ (e.g., $\epsilon = 0.01$ for 99% guarantee). ## Architecture Diagram ```{mermaid}

graph TD A[Simulation Step] --> B[Start Timer] B --> C[Execute Step] C --> D[End Timer] D --> E[t_exec = t_end - t_start] E --> F{Deadline Check} F -->|t_exec > deadline| G[Violation Event] F -->|t_exec ≤ deadline| H[Success] G --> I[Log Violation] I --> J[Update Statistics] H --> J J --> K[Compute μ, σ, percentiles] K --> L{Health Check} L -->|Healthy| M[Continue] L -->|Degraded| N[Warning] style E fill:#9cf style G fill:#f99 style M fill:#9f9
``` ## Usage Examples ### Example 1: Basic Integration ```python
from src.simulation.integrators import create_integrator # Create integrator
integrator = create_integrator('rk4', dt=0.01) # Integrate one step
x_next = integrator.integrate(dynamics_fn, x, u, dt)
``` ### Example 2: Zero-Order Hold Discretization ```python

from src.simulation.integrators.discrete import ZeroOrderHold # Linear system matrices
A = np.array([[0, 1], [-2, -3]])
B = np.array([[0], [1]]) # Create ZOH integrator
zoh = ZeroOrderHold(A, B, dt=0.01) # Discrete-time evolution
x_next = zoh.integrate(None, x, u, dt) # Access discrete matrices
A_d = zoh.A_d
B_d = zoh.B_d
``` ### Example 3: Real-Time Monitoring ```python
from src.simulation.safety import SimulationPerformanceMonitor # Create monitor
monitor = SimulationPerformanceMonitor() # Simulation loop with monitoring
for i in range(N_steps): monitor.start_timing('step') u = controller.compute(x) x = integrator.integrate(dynamics, x, u, dt) elapsed = monitor.end_timing('step') if elapsed > deadline: print(f"Deadline violation at step {i}: {elapsed:.4f}s") # Get statistics
stats = monitor.get_statistics()
print(f"Mean: {stats['mean']:.4f}s")
print(f"95th percentile: {stats['p95']:.4f}s")
``` ### Example 4: Monte Carlo Simulation ```python

from src.simulation.strategies import MonteCarloStrategy # Define parameter distributions
distributions = { 'mass': ('normal', {'mean': 1.0, 'std': 0.1}), 'length': ('uniform', {'low': 0.9, 'high': 1.1})
} # Create Monte Carlo strategy
mc = MonteCarloStrategy(n_samples=1000, parallel=True) # Run Monte Carlo analysis
results = mc.analyze( simulation_fn=run_simulation, parameters=distributions
) # Extract statistics
print(f"Mean ISE: {results['metrics']['ise']['mean']:.4f}")
print(f"95% CI: [{results['metrics']['ise']['ci_lower']:.4f}, " f"{results['metrics']['ise']['ci_upper']:.4f}]")
``` ### Example 5: Safety Recovery ```python
from src.simulation.safety import SafetyRecovery # Configure recovery
recovery = SafetyRecovery( state_bounds=(-10, 10), control_bounds=(-100, 100), recovery_mode='qp' # or 'projection', 'fallback'
) # Simulation with safety recovery
for i in range(N_steps): u = controller.compute(x) # Check for violations if recovery.check_violation(x, u): x_safe, u_safe = recovery.recover(x, u) x = integrator.integrate(dynamics, x_safe, u_safe, dt) else: x = integrator.integrate(dynamics, x, u, dt)
```
