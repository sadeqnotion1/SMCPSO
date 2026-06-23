# simulation.integrators.fixed_step.euler

**Source:** `src\simulation\integrators\fixed_step\euler.py`

## Module Overview

Euler integration methods (explicit and implicit).


## Mathematical Foundation

### Euler Integration Method

The Euler method is the simplest first-order numerical integration scheme:

```{math}
\vec{x}_{k+1} = \vec{x}_k + \Delta t \cdot \vec{f}(\vec{x}_k, \vec{u}_k, t_k)
```

Where:
- $\vec{x}_k \in \mathbb{R}^n$: State vector at step $k$
- $\vec{f}$: Dynamics function (derivatives)
- $\Delta t$: Fixed time step
- $\vec{u}_k$: Control input

### Local Truncation Error

Taylor series expansion shows first-order accuracy:

```{math}
\vec{x}(t_{k+1}) = \vec{x}(t_k) + \Delta t \vec{f}(\vec{x}_k, t_k) + \frac{\Delta t^2}{2} \vec{f}'(\vec{x}_k, t_k) + O(\Delta t^3)
```

**Local truncation error:**
```{math}
\tau_k = \frac{\Delta t^2}{2} \vec{f}'(\vec{x}_k, t_k) = O(\Delta t^2)
```

**Global error:**
```{math}
e_N = O(\Delta t)
```

### Stability Analysis

**Absolute stability region** for test equation $\dot{y} = \lambda y$:

```{math}
y_{k+1} = (1 + \lambda \Delta t) y_k
```

**Stability condition:**
```{math}
|1 + \lambda \Delta t| < 1 \quad \Rightarrow \quad \Delta t < \frac{2}{|\text{Re}(\lambda)|}
```

For the DIP system, characteristic frequencies determine maximum stable timestep.

### Convergence

**Consistency:**
```{math}
\lim_{\Delta t \to 0} \frac{x_{k+1} - x_k}{\Delta t} = f(x_k, t_k)
```

**Stability + Consistency = Convergence** (Lax Equivalence Theorem)

### Computational Complexity

- **Function evaluations per step:** 1
- **Computational cost:** $O(n)$ per step
- **Memory:** $O(n)$ for state vector
- **Total cost for $N$ steps:** $O(Nn)$

### Use Cases

**Suitable for:**
- Simple, non-stiff dynamics
- Fast prototyping
- Real-time applications (low computational cost)

**Not suitable for:**
- Stiff equations (unstable)
- High-accuracy requirements
- Long-time integration (error accumulation)

## Architecture Diagram

```{mermaid}
graph TD
    A[Initial State x_n] --> B[Evaluate f_x_n_u_n_t_n_]
    B --> C[Compute x_n+1_ = x_n_ + Δt·f]
    C --> D{Converged?}
    D -->|No| A
    D -->|Yes| E[Final State x_N_]

    style B fill:#9cf
    style C fill:#ff9
    style E fill:#9f9
```

## Usage Examples

### Example 1: Basic Usage

```python
from src.simulation.integrators import IntegratorsFixedStepEuler

# Initialize
instance = IntegratorsFixedStepEuler()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = IntegratorsFixedStepEuler(config)
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

```{literalinclude} ../../../src/simulation/integrators/fixed_step/euler.py
:language: python
:linenos:
```



## Classes

### `ForwardEuler`

**Inherits from:** `BaseIntegrator`

Forward (explicit) Euler integration method.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/fixed_step/euler.py
:language: python
:pyobject: ForwardEuler
:linenos:
```

#### Methods (3)

##### `order(self)`

Integration method order.

[View full source →](#method-forwardeuler-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-forwardeuler-adaptive)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate using forward Euler method.

[View full source →](#method-forwardeuler-integrate)



### `BackwardEuler`

**Inherits from:** `BaseIntegrator`

Backward (implicit) Euler integration method.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/fixed_step/euler.py
:language: python
:pyobject: BackwardEuler
:linenos:
```

#### Methods (4)

##### `__init__(self, rtol, atol, max_iterations)`

Initialize backward Euler integrator.

[View full source →](#method-backwardeuler-__init__)

##### `order(self)`

Integration method order.

[View full source →](#method-backwardeuler-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-backwardeuler-adaptive)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate using backward Euler method.

[View full source →](#method-backwardeuler-integrate)



### `ModifiedEuler`

**Inherits from:** `BaseIntegrator`

Modified Euler method (Heun's method).

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/fixed_step/euler.py
:language: python
:pyobject: ModifiedEuler
:linenos:
```

#### Methods (3)

##### `order(self)`

Integration method order.

[View full source →](#method-modifiedeuler-order)

##### `adaptive(self)`

Whether integrator supports adaptive step size.

[View full source →](#method-modifiedeuler-adaptive)

##### `integrate(self, dynamics_fn, state, control, dt, t)`

Integrate using modified Euler (Heun's) method.

[View full source →](#method-modifiedeuler-integrate)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Callable`
- `import numpy as np`
- `from scipy.optimize import fsolve`
- `from ..base import BaseIntegrator`
