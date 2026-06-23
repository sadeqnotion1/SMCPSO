# simulation.integrators.adaptive.runge_kutta

**Source:** `src\simulation\integrators\adaptive\runge_kutta.py`

## Module Overview

Adaptive Runge-Kutta integration methods with error control.


## Mathematical Foundation

### Adaptive Runge-Kutta Methods

Embedded RK schemes with automatic step size control:

```{math}
\begin{align}
y_{n+1} &= y_n + \Delta t \sum_{i=1}^{s} b_i k_i \quad \text{($p$-th order)} \\
\hat{y}_{n+1} &= y_n + \Delta t \sum_{i=1}^{s} b^*_i k_i \quad \text{($\hat{p}$-th order, $\hat{p} = p-1$)}
\end{align}
```

### Dormand-Prince 4(5) Method

**Most widely used adaptive RK method:**

**Butcher Tableau (7 stages, 5th order):**
```{math}
\begin{array}{c|ccccccc}
0 \\
1/5 & 1/5 \\
3/10 & 3/40 & 9/40 \\
4/5 & 44/45 & -56/15 & 32/9 \\
8/9 & 19372/6561 & -25360/2187 & 64448/6561 & -212/729 \\
1 & 9017/3168 & -355/33 & 46732/5247 & 49/176 & -5103/18656 \\
1 & 35/384 & 0 & 500/1113 & 125/192 & -2187/6784 & 11/84 \\
\hline
& 35/384 & 0 & 500/1113 & 125/192 & -2187/6784 & 11/84 & 0 \quad \text{(5th)} \\
& 5179/57600 & 0 & 7571/16695 & 393/640 & -92097/339200 & 187/2100 & 1/40 \quad \text{(4th)}
\end{array}
```

**FSAL Property:** First-Same-As-Last - $k_1^{(n+1)} = k_7^{(n)}$

### Error Estimation

**Local error estimate:**
```{math}
\vec{e}_{n+1} = \hat{y}_{n+1} - y_{n+1} = \Delta t \sum_{i=1}^{s} (b^*_i - b_i) k_i
```

**Error norm:**
```{math}
\text{err} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} \left(\frac{e_i}{\text{atol} + |y_i| \cdot \text{rtol}}\right)^2}
```

Where:
- `atol`: Absolute tolerance (e.g., $10^{-8}$)
- `rtol`: Relative tolerance (e.g., $10^{-6}$)

### Step Size Control

**PI Controller (Proportional-Integral):**

```{math}
\Delta t_{n+1} = \Delta t_n \cdot \left(\frac{1}{\text{err}_n}\right)^{k_P} \cdot \left(\frac{\text{err}_{n-1}}{\text{err}_n}\right)^{k_I}
```

Typical values: $k_P = 0.7/p$, $k_I = 0.4/p$ where $p$ is method order

**Safety factor:**
```{math}
\Delta t_{n+1} = 0.9 \cdot \Delta t_n \cdot \text{err}^{-1/5}
```

**Bounds:**
```{math}
\Delta t_{\min} \leq \Delta t_{n+1} \leq \Delta t_{\max}
```

### Step Acceptance

**Accept step if:**
```{math}
\text{err} \leq 1.0
```

**Reject and retry with smaller step if:**
```{math}
\text{err} > 1.0
```

### Adaptive Integration Algorithm

1. **Compute candidate step:** $y_{n+1}$, $\hat{y}_{n+1}$
2. **Estimate error:** $\text{err} = \|e_{n+1}\|$
3. **Check acceptance:**
   - If $\text{err} \leq 1$: Accept, update state, adjust step size
   - If $\text{err} > 1$: Reject, reduce step size, retry
4. **Update step size** using PI controller
5. **Repeat** until final time reached

### Computational Efficiency

**Advantages:**
- Automatic accuracy control
- Efficient use of function evaluations
- Adapts to dynamics (small steps near discontinuities, large steps in smooth regions)

**Typical performance:**
- **DIP system:** $\Delta t$ varies from $10^{-5}$ to $10^{-2}$ s
- **Function evals:** 30-50% fewer than fixed-step RK4 for same accuracy

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
from src.simulation.integrators import IntegratorsAdaptiveRungeKutta

# Initialize
instance = IntegratorsAdaptiveRungeKutta()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = IntegratorsAdaptiveRungeKutta(config)
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

```{literalinclude} ../../../src/simulation/integrators/adaptive/runge_kutta.py
:language: python
:linenos:
```



## Classes

### `AdaptiveRungeKutta`

**Inherits from:** `BaseIntegrator`

Base class for adaptive Runge-Kutta methods.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/adaptive/runge_kutta.py
:language: python
:pyobject: AdaptiveRungeKutta
:linenos:
```

#### Methods (4)

##### `__init__(self, rtol, atol, min_step, max_step, safety_factor)`

Initialize adaptive Runge-Kutta integrator.

[View full source →](#method-adaptiverungekutta-__init__)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-adaptiverungekutta-adaptive)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate dynamics with adaptive step size.

[View full source →](#method-adaptiverungekutta-integrate)

##### `_adaptive_step(self, f, t, y, dt)`

Perform one adaptive integration step.

[View full source →](#method-adaptiverungekutta-_adaptive_step)



### `DormandPrince45`

**Inherits from:** `AdaptiveRungeKutta`

Dormand-Prince 4(5) embedded Runge-Kutta method with adaptive step size.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/adaptive/runge_kutta.py
:language: python
:pyobject: DormandPrince45
:linenos:
```

#### Methods (2)

##### `order(self)`

Integration method order.

[View full source →](#method-dormandprince45-order)

##### `_adaptive_step(self, f, t, y, dt)`

Perform single Dormand-Prince 4(5) step with error control.

[View full source →](#method-dormandprince45-_adaptive_step)



## Functions

### `rk45_step(f, t, y, dt, abs_tol, rel_tol)`

Legacy Dormand-Prince 4(5) step function for backward compatibility.

Parameters
----------
f : callable
    Function computing time derivative dy/dt = f(t, y)
t : float
    Current integration time
y : np.ndarray
    Current state vector
dt : float
    Proposed step size
abs_tol : float
    Absolute tolerance for error control
rel_tol : float
    Relative tolerance for error control

Returns
-------
tuple
    (y_new, dt_new) where y_new is None if step rejected

Notes
-----
This function maintains backward compatibility with the original
adaptive_integrator.py implementation.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/adaptive/runge_kutta.py
:language: python
:pyobject: rk45_step
:linenos:
```



### `_original_rk45_step(f, t, y, dt, abs_tol, rel_tol)`

Original RK45 implementation for fallback.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/adaptive/runge_kutta.py
:language: python
:pyobject: _original_rk45_step
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Callable, Optional, Tuple`
- `import numpy as np`
- `from ..base import BaseIntegrator, IntegrationResult`
- `from .error_control import ErrorController`
