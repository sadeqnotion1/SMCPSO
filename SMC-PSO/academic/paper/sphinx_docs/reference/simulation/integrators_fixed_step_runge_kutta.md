# simulation.integrators.fixed_step.runge_kutta

**Source:** `src\simulation\integrators\fixed_step\runge_kutta.py`

## Module Overview

Fixed step-size Runge-Kutta integration methods.


## Mathematical Foundation

### Runge-Kutta Family

Classical fixed-step Runge-Kutta methods for ODE integration:

```{math}
\dot{\vec{x}} = \vec{f}(\vec{x}, \vec{u}, t)
```

### General s-Stage RK Method

```{math}
\begin{align}
k_i &= \vec{f}\left(\vec{x}_n + \Delta t \sum_{j=1}^{i-1} a_{ij} k_j, \vec{u}, t_n + c_i \Delta t\right), \quad i=1,\ldots,s \\
\vec{x}_{n+1} &= \vec{x}_n + \Delta t \sum_{i=1}^{s} b_i k_i
\end{align}
```

### Butcher Tableau

Compact representation of RK method coefficients:

```{math}
\begin{array}{c|cccc}
c_1 & a_{11} & a_{12} & \cdots & a_{1s} \\
c_2 & a_{21} & a_{22} & \cdots & a_{2s} \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
c_s & a_{s1} & a_{s2} & \cdots & a_{ss} \\
\hline
& b_1 & b_2 & \cdots & b_s
\end{array}
```

### RK2 (Midpoint Method)

**2nd order Runge-Kutta:**

```{math}
\begin{align}
k_1 &= \vec{f}(\vec{x}_n, t_n) \\
k_2 &= \vec{f}\left(\vec{x}_n + \frac{\Delta t}{2} k_1, t_n + \frac{\Delta t}{2}\right) \\
\vec{x}_{n+1} &= \vec{x}_n + \Delta t \cdot k_2
\end{align}
```

**Accuracy:** $O(\Delta t^2)$ local error, $O(\Delta t^2)$ global error

### RK4 (Classical 4th Order)

**Gold standard for fixed-step integration:**

```{math}
\begin{align}
k_1 &= \vec{f}(\vec{x}_n, t_n) \\
k_2 &= \vec{f}\left(\vec{x}_n + \frac{\Delta t}{2} k_1, t_n + \frac{\Delta t}{2}\right) \\
k_3 &= \vec{f}\left(\vec{x}_n + \frac{\Delta t}{2} k_2, t_n + \frac{\Delta t}{2}\right) \\
k_4 &= \vec{f}(\vec{x}_n + \Delta t \cdot k_3, t_n + \Delta t) \\
\vec{x}_{n+1} &= \vec{x}_n + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)
\end{align}
```

**Accuracy:** $O(\Delta t^4)$ local error, $O(\Delta t^4)$ global error

### Stability Regions

**Absolute stability region $S$:** Set of $z = \lambda \Delta t$ where amplification factor $|R(z)| \leq 1$

- **RK2:** Larger than Euler, still conditionally stable
- **RK4:** Significantly larger, allows bigger timesteps

### Order Conditions

For $p$-th order accuracy, RK coefficients must satisfy **order conditions**:

**1st order:**
```{math}
\sum_{i=1}^{s} b_i = 1
```

**2nd order:**
```{math}
\sum_{i=1}^{s} b_i c_i = \frac{1}{2}
```

**4th order:** 8 order conditions (RK4 satisfies all)

### Computational Cost

| Method | Stages | Function Evals | Accuracy | Cost/Step |
|--------|--------|----------------|----------|-----------|
| Euler  | 1      | 1              | $O(\Delta t)$ | $n$ |
| RK2    | 2      | 2              | $O(\Delta t^2)$ | $2n$ |
| RK4    | 4      | 4              | $O(\Delta t^4)$ | $4n$ |

For DIP system ($n=6$), RK4 costs 24 function evaluations per step.

## Architecture Diagram

```{mermaid}
graph TD
    A[Initial State x_n] --> B[Stage 1: k1 = f_x_n_]
    B --> C[Stage 2: k2 = f_x_n_ + Δt/2·k1]
    C --> D[Stage 3: k3 = f_x_n_ + Δt/2·k2]
    D --> E[Stage 4: k4 = f_x_n_ + Δt·k3]
    E --> F[Combine: x_n+1_ = x_n_ + Δt/6_k1+2k2+2k3+k4_]
    F --> G{Continue?}
    G -->|Yes| A
    G -->|No| H[Final State]

    style B fill:#9cf
    style C fill:#9cf
    style D fill:#9cf
    style E fill:#9cf
    style F fill:#ff9
    style H fill:#9f9
```

## Usage Examples

### Example 1: Basic Usage

```python
from src.simulation.integrators import IntegratorsFixedStepRungeKutta

# Initialize
instance = IntegratorsFixedStepRungeKutta()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = IntegratorsFixedStepRungeKutta(config)
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

```{literalinclude} ../../../src/simulation/integrators/fixed_step/runge_kutta.py
:language: python
:linenos:
```



## Classes

### `RungeKutta2`

**Inherits from:** `BaseIntegrator`

Second-order Runge-Kutta method (midpoint rule).

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/fixed_step/runge_kutta.py
:language: python
:pyobject: RungeKutta2
:linenos:
```

#### Methods (3)

##### `order(self)`

Integration method order.

[View full source →](#method-rungekutta2-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-rungekutta2-adaptive)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate using second-order Runge-Kutta (midpoint) method.

[View full source →](#method-rungekutta2-integrate)



### `RungeKutta4`

**Inherits from:** `BaseIntegrator`

Fourth-order Runge-Kutta method (classic RK4).

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/fixed_step/runge_kutta.py
:language: python
:pyobject: RungeKutta4
:linenos:
```

#### Methods (3)

##### `order(self)`

Integration method order.

[View full source →](#method-rungekutta4-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-rungekutta4-adaptive)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate using fourth-order Runge-Kutta method.

[View full source →](#method-rungekutta4-integrate)



### `RungeKutta38`

**Inherits from:** `BaseIntegrator`

Runge-Kutta 3/8 rule (alternative 4th-order method).

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/fixed_step/runge_kutta.py
:language: python
:pyobject: RungeKutta38
:linenos:
```

#### Methods (3)

##### `order(self)`

Integration method order.

[View full source →](#method-rungekutta38-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-rungekutta38-adaptive)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate using Runge-Kutta 3/8 rule.

[View full source →](#method-rungekutta38-integrate)



### `ClassicalRungeKutta`

**Inherits from:** `RungeKutta4`

Alias for standard RK4 method for backward compatibility.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/fixed_step/runge_kutta.py
:language: python
:pyobject: ClassicalRungeKutta
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Callable`
- `import numpy as np`
- `from ..base import BaseIntegrator`
