# simulation.strategies.monte_carlo

**Source:** `src\simulation\strategies\monte_carlo.py`

## Module Overview

Monte Carlo simulation strategy for statistical analysis.

## Complete Source Code

```{literalinclude} ../../../src/simulation/strategies/monte_carlo.py
:language: python
:linenos:
```



## Classes

### `MonteCarloStrategy`

**Inherits from:** `SimulationStrategy`

Monte Carlo simulation strategy for statistical analysis.

#### Source Code

```{literalinclude} ../../../src/simulation/strategies/monte_carlo.py
:language: python
:pyobject: MonteCarloStrategy
:linenos:
```

#### Methods (7)

##### `__init__(self, n_samples, parallel, max_workers)`

Initialize Monte Carlo strategy.

[View full source →](#method-montecarlostrategy-__init__)

##### `analyze(self, simulation_fn, parameters)`

Perform Monte Carlo analysis.

[View full source →](#method-montecarlostrategy-analyze)

##### `_generate_samples(self, distributions)`

Generate Monte Carlo parameter samples.

[View full source →](#method-montecarlostrategy-_generate_samples)

##### `_run_parallel_simulations(self, simulation_fn, samples, fixed_params)`

Run simulations in parallel.

[View full source →](#method-montecarlostrategy-_run_parallel_simulations)

##### `_run_sequential_simulations(self, simulation_fn, samples, fixed_params)`

Run simulations sequentially.

[View full source →](#method-montecarlostrategy-_run_sequential_simulations)

##### `_analyze_results(self, results, samples)`

Analyze Monte Carlo results.

[View full source →](#method-montecarlostrategy-_analyze_results)

##### `_extract_metrics(self, results)`

Extract metrics from simulation results.

[View full source →](#method-montecarlostrategy-_extract_metrics)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Callable, Dict, List, Optional`
- `import numpy as np`
- `from ..core.interfaces import SimulationStrategy`
- `from ..orchestrators.parallel import ParallelOrchestrator`


## Advanced Mathematical Theory

### Monte Carlo Sampling

**Parameter sampling from distributions:**

```{math}
\theta_i \sim p(\theta), \quad i = 1, \ldots, N
```

**Latin Hypercube Sampling (LHS) for variance reduction:**

Stratified sampling ensures better coverage:

```{math}
\theta_i^{(j)} = F_j^{-1}\left(\frac{\pi_i(j) - U_i}{N}\right)
```

where $F_j^{-1}$ is the inverse CDF of dimension $j$, $\pi_i$ is a random permutation, and $U_i \sim \text{Uniform}(0, 1)$.

**Quasi-random sequences (Sobol, Halton):**

Low-discrepancy sequences for better uniform coverage than pseudo-random.

### Monte Carlo Convergence

**Monte Carlo error:**

```{math}
\epsilon_{\text{MC}} = \frac{\sigma}{\sqrt{N}}
```

where $\sigma$ is the standard deviation of the estimator.

**Confidence intervals:**

```{math}
\mu \pm z_{\alpha/2} \frac{\sigma}{\sqrt{N}}
```

for $(1-\alpha)100\%$ confidence (e.g., $z_{0.025} = 1.96$ for 95% CI).

**Sample size determination:**

To achieve error $\epsilon$ with confidence $1-\alpha$:

```{math}
N = \left(\frac{z_{\alpha/2} \sigma}{\epsilon}\right)^2
```

### Parallel Monte Carlo

**Speedup with $P$ processors:**

```{math}
S(P) = \frac{T(1)}{T(P)} \approx \frac{1}{(1 - p) + \frac{p}{P}}
```

where $p$ is the parallelizable fraction (Amdahl's Law).

**For embarrassingly parallel Monte Carlo:** $p \approx 1$, so $S(P) \approx P$ (ideal scaling).

**Load balancing:**

Distribute $N$ samples evenly: $N_i = \lfloor N/P \rfloor$ or $\lceil N/P \rceil$.

## Architecture Diagram

```{mermaid}
graph TD
    A[Parameter Distributions] --> B[Sampling Strategy]

    B --> C{Method}
    C -->|Random| D[Pseudo-Random]
    C -->|LHS| E[Latin Hypercube]
    C -->|Quasi| F[Sobol/Halton]

    D --> G[Sample θ_1, ..., θ_N]
    E --> G
    F --> G

    G --> H{Parallel?}
    H -->|Yes| I[Distribute to Workers]
    H -->|No| J[Sequential Execution]

    I --> K[Worker 1: θ_1:n_1_]
    I --> L[Worker P: θ_n_P-1:N_]

    K --> M[Gather Results]
    L --> M
    J --> M

    M --> N[Statistical Analysis]
    N --> O[μ, σ, CI, percentiles]

    style G fill:#9cf
    style O fill:#9f9
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
