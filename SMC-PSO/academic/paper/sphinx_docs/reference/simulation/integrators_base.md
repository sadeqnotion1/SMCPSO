# simulation.integrators.base

**Source:** `src\simulation\integrators\base.py`

## Module Overview

Base integrator interface and common utilities.


## Mathematical Foundation

### Numerical Integration Interface

Abstract base class defining the integration protocol for ODE systems.

### ODE Formulation

**Initial Value Problem (IVP):**
```{math}
\begin{cases}
\dot{\vec{x}}(t) = \vec{f}(\vec{x}(t), \vec{u}(t), t) \\
\vec{x}(t_0) = \vec{x}_0
\end{cases}
```

Where:
- $\vec{x} \in \mathbb{R}^n$: State vector
- $\vec{f}: \mathbb{R}^n \times \mathbb{R}^m \times \mathbb{R} \to \mathbb{R}^n$: Dynamics function
- $\vec{u} \in \mathbb{R}^m$: Control input
- $t \in [t_0, t_f]$: Time domain

### Integrator Properties

**1. Order of Accuracy**

Local truncation error: $\tau_n = O(\Delta t^{p+1})$
Global error: $e_N = O(\Delta t^p)$

**2. Stability**

Absolute stability region $S \subseteq \mathbb{C}$:
```{math}
S = \{z \in \mathbb{C} : |R(z)| \leq 1\}
```

Where $R(z)$ is the stability function.

**3. Consistency**

```{math}
\lim_{\Delta t \to 0} \frac{\Phi(x_n, t_n, \Delta t) - x_n}{\Delta t} = f(x_n, t_n)
```

### Integrator Classification

**Fixed-Step Methods:**
- Constant time step $\Delta t$
- Predictable computational cost
- Examples: Euler, RK2, RK4

**Adaptive Methods:**
- Variable time step $\Delta t_n$
- Error-controlled accuracy
- Examples: RK45, Dormand-Prince

**Explicit Methods:**
```{math}
x_{n+1} = x_n + \Delta t \cdot \Phi(x_n, t_n, \Delta t)
```

**Implicit Methods:**
```{math}
x_{n+1} = x_n + \Delta t \cdot \Phi(x_n, x_{n+1}, t_n, \Delta t)
```

### Integration Interface Protocol

**Required Methods:**

1. **integrate(dynamics_fn, state, control, dt, t) → state_new**
   - Single integration step
   - Returns updated state

2. **order() → int**
   - Method accuracy order

3. **adaptive() → bool**
   - Whether step size is adaptive

**Optional Methods:**

4. **reset()**
   - Clear internal state/cache

5. **get_statistics() → dict**
   - Performance metrics (steps, rejections, etc.)

### Convergence Theorem (Lax Equivalence)

For a consistent numerical method applied to a well-posed linear IVP:

**Stability + Consistency ⟹ Convergence**

### Performance Characteristics

| Property | Fixed-Step | Adaptive |
|----------|------------|----------|
| Cost per step | Constant | Variable |
| Accuracy control | Manual | Automatic |
| Stiff systems | Poor | Better |
| Real-time suitability | Excellent | Moderate |

## Architecture Diagram

```{mermaid}
graph LR
    A[Input] --> B[Integrators Processing]
    B --> C[Output]

    style B fill:#9cf
    style C fill:#9f9
```

## Usage Examples

### Example 1: Basic Usage

```python
from src.simulation.integrators import IntegratorsBase

# Initialize
instance = IntegratorsBase()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = IntegratorsBase(config)
result = instance.process(data)
```

## Example 3: Error Handling

```python
try:
    result = instance.process(data)
except Exception as e:
    print(f"Error: {e}")
```

### Example 4: Performance Profiling

```python
import time
start = time.time()
result = instance.process(data)
elapsed = time.time() - start
print(f"Execution time: {elapsed:.4f} s")
```

### Example 5: Integration with Other Components

```python
# Combine with other simulation components
result = orchestrator.execute(instance.process(data))
```

## Complete Source Code

```{literalinclude} ../../../src/simulation/integrators/base.py
:language: python
:linenos:
```



## Classes

### `BaseIntegrator`

**Inherits from:** `Integrator`

Base class for numerical integration methods.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/base.py
:language: python
:pyobject: BaseIntegrator
:linenos:
```

#### Methods (10)

##### `__init__(self, rtol, atol)`

Initialize base integrator.

[View full source →](#method-baseintegrator-__init__)

##### `integrate(self, dynamics_fn, state, control, dt)`

Integrate dynamics forward by one time step.

[View full source →](#method-baseintegrator-integrate)

##### `order(self)`

Integration method order.

[View full source →](#method-baseintegrator-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-baseintegrator-adaptive)

##### `reset_statistics(self)`

Reset integration statistics.

[View full source →](#method-baseintegrator-reset_statistics)

##### `get_statistics(self)`

Get integration statistics.

[View full source →](#method-baseintegrator-get_statistics)

##### `integrate_step(self, dynamics_fn, state, time, dt)`

Integrate dynamics forward by one time step (interface compatibility method).

[View full source →](#method-baseintegrator-integrate_step)

##### `_update_stats(self, accepted, func_evals)`

Update integration statistics.

[View full source →](#method-baseintegrator-_update_stats)

##### `_validate_inputs(self, dynamics_fn, state, control, dt)`

Validate integration inputs.

[View full source →](#method-baseintegrator-_validate_inputs)

##### `_compute_error_norm(self, error, state)`

Compute error norm for adaptive integration.

[View full source →](#method-baseintegrator-_compute_error_norm)



### `IntegrationResult`

Container for integration step results.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/base.py
:language: python
:pyobject: IntegrationResult
:linenos:
```

#### Methods (1)

##### `__init__(self, state, accepted, error_estimate, suggested_dt, function_evaluations)`

Initialize integration result.

[View full source →](#method-integrationresult-__init__)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Callable, Dict, Optional, Tuple`
- `import numpy as np`
- `from ..core.interfaces import Integrator`
