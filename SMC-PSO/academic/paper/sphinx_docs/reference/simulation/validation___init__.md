# simulation.validation.__init__

**Source:** `src\simulation\validation\__init__.py`

## Module Overview

Testing and validation framework for simulation components.
This module provides validation tools for simulation accuracy,
convergence analysis, and regression testing for simulation engines.

## Complete Source Code

```{literalinclude} ../../../src/simulation/validation/__init__.py
:language: python
:linenos:
```





## Advanced Mathematical Theory

### Numerical Validation

**Energy conservation (Hamiltonian systems):**

```{math}
E(t) = \frac{1}{2}\dot{\vec{q}}^T M \dot{\vec{q}} + V(\vec{q}) = \text{const}
```

**Relative energy drift:**

```{math}
\text{Drift} = \frac{|E(t) - E(t_0)|}{|E(t_0)|} < \epsilon_{\text{tol}}
```

**Order of accuracy validation (Richardson extrapolation):**

If method has order $p$, then:

```{math}
\|\vec{x}(T) - \vec{x}_h(T)\| \approx Ch^p
```

Verify: $\log\|e_h\| - \log\|e_{h/2}\| \approx p\log 2$

### Statistical Validation

**Hypothesis testing (t-test):**

```{math}
t = \frac{\bar{x}_1 - \bar{x}_2}{s_p\sqrt{\frac{1}{n_1} + \frac{1}{n_2}}}
```

where $s_p$ is pooled standard deviation.

**Distribution fitting (Kolmogorov-Smirnov):**

```{math}
D_n = \sup_x |F_n(x) - F_0(x)|
```

**Convergence diagnostics (Gelman-Rubin):**

```{math}
\hat{R} = \sqrt{\frac{\text{Var}_+(\theta)}{W}}
```

where $\text{Var}_+(\theta)$ is weighted variance, $W$ is within-chain variance.

**Acceptance criterion:** $\hat{R} < 1.1$ indicates convergence.

## Architecture Diagram

```{mermaid}
graph TD
    A[Simulation Results] --> B{Validation Type}

    B -->|Numerical| C[Energy Conservation]
    B -->|Numerical| D[Order of Accuracy]
    B -->|Statistical| E[Hypothesis Testing]
    B -->|Statistical| F[Distribution Fitting]

    C --> G[Relative Drift < ε]
    D --> H[Richardson Extrapolation]
    E --> I[t-test, ANOVA]
    F --> J[KS Test]

    G --> K{Pass?}
    H --> K
    I --> K
    J --> K

    K -->|Yes| L[Validated]
    K -->|No| M[Report Failure]

    L --> N[Convergence Diagnostics]
    N --> O[Gelman-Rubin R-hat]

    style L fill:#9f9
    style M fill:#f99
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
