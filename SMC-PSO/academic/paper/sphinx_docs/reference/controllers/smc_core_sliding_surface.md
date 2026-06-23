# controllers.smc.core.sliding_surface

**Source:** `src\controllers\smc\core\sliding_surface.py`

## Module Overview

Sliding Surface Calculations for SMC Controllers.

Provides unified sliding surface computation that can be shared across all SMC types.
Implements both linear and nonlinear sliding surface formulations with proper
mathematical foundations.

Mathematical Background:
- Linear sliding surface: s = c₁e₁ + c₂e₂ + λ₁ė₁ + λ₂ė₂
- Where e₁, e₂ are tracking errors and ė₁, ė₂ are error derivatives
- Coefficients c₁, c₂, λ₁, λ₂ must be positive for stability (Hurwitz requirement)


## Mathematical Foundation

### Sliding Mode Control Theory

Sliding mode control forces system trajectories onto a **sliding surface** where desired dynamics are exhibited.

```{math}
s(\vec{x}, t) = 0
```

Where $s: \mathbb{R}^n \times \mathbb{R}_+ \to \mathbb{R}^m$ is the sliding surface function.

### Linear Sliding Surface for DIP

For the double-inverted pendulum with state $\vec{x} = [x, \dot{x}, \theta_1, \dot{\theta}_1, \theta_2, \dot{\theta}_2]^T$:

```{math}
s = \lambda_1 \dot{\theta}_1 + c_1 \theta_1 + \lambda_2 \dot{\theta}_2 + c_2 \theta_2
```

**Physical Interpretation:**
- $\theta_1, \theta_2$: Angular errors (desired = 0 for stabilization)
- $\dot{\theta}_1, \dot{\theta}_2$: Angular velocity errors
- $c_1, c_2 > 0$: Position feedback gains
- $\lambda_1, \lambda_2 > 0$: Velocity feedback gains

### Hurwitz Stability Criterion

For the sliding surface to ensure exponential convergence when $s = 0$:

```{math}
\dot{s} = 0 \quad \Rightarrow \quad \lambda_i \ddot{\theta}_i + c_i \dot{\theta}_i = 0, \quad i = 1, 2
```

This gives characteristic polynomial:

```{math}
p(r) = r + \frac{c_i}{\lambda_i}
```

**Hurwitz criterion** requires all roots to have negative real parts:

```{math}
\frac{c_i}{\lambda_i} > 0 \quad \Rightarrow \quad c_i, \lambda_i > 0
```

This ensures **exponential convergence** to zero:

```{math}
\theta_i(t) = \theta_i(0) e^{-\frac{c_i}{\lambda_i} t}
```

### Lyapunov Stability

**Lyapunov function:**

```{math}
V(s) = \frac{1}{2} s^2
```

**Sliding condition** (Lyapunov stability):

```{math}
\dot{V} = s \dot{s} < 0 \quad \text{for} \quad s \neq 0
```

This ensures trajectories are attracted to the sliding surface and remain there.

### Reaching Condition

**Finite-time reaching** requires:

```{math}
s \dot{s} \leq -\eta |s|, \quad \eta > 0
```

**Reaching time bound:**

```{math}
t_{reach} \leq \frac{|s(0)|}{\eta}
```

### Sliding Surface Design Guidelines

1. **Hurwitz requirement:** All gains $c_i, \lambda_i > 0$
2. **Convergence rate:** Larger $c_i/\lambda_i$ → faster convergence
3. **Overshoot control:** Smaller $c_i/\lambda_i$ → less overshoot
4. **Typical range:** $c_i/\lambda_i \in [0.5, 5.0]$ rad/s

### Higher-Order Sliding Surfaces

**Super-Twisting (2nd order):**

```{math}
s = \sigma, \quad \dot{\sigma} = \lambda_1 \dot{\theta}_1 + c_1 \theta_1 + \lambda_2 \dot{\theta}_2 + c_2 \theta_2
```

Provides **finite-time convergence** and **continuous control** (no chattering).

### Computational Complexity

- **Linear surface evaluation:** $O(n)$ multiply-adds
- **Surface derivative:** $O(n^2)$ if Jacobian needed
- **Memory:** $O(n)$ for gains and state

## Architecture Diagram

```{mermaid}
graph TD
    A[State Vector x] --> B[Extract Errors: θ₁, θ₂, θ̇₁, θ̇₂]
    B --> C[Compute s = λ₁θ̇₁ + c₁θ₁ + λ₂θ̇₂ + c₂θ₂]
    C --> D{|s| < ε?}
    D -->|Yes| E[On Sliding Surface]
    D -->|No| F[Off Sliding Surface]
    E --> G[Sliding Mode Reached]
    F --> H[Reaching Phase]

    B --> I[Validate Gains: c₁, c₂, λ₁, λ₂ > 0]
    I -->|Invalid| J[Raise ValueError]
    I -->|Valid| C

    style C fill:#9cf
    style E fill:#9f9
    style F fill:#ff9
    style J fill:#f99
```

## Usage Examples

### Example 1: Basic Linear Sliding Surface

```python
from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
import numpy as np

# Define gains (c1, c2, λ1, λ2)
gains = [10.0, 8.0, 15.0, 12.0]
surface = LinearSlidingSurface(gains)

# Compute surface value for state
state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])  # [x, ẋ, θ₁, θ̇₁, θ₂, θ̇₂]
s = surface.compute(state)
print(f"Sliding surface value: {s:.4f}")
```

## Example 2: Surface Derivative Computation

```python
# Compute surface derivative ds/dt
state_dot = np.array([0.0, 0.0, 0.1, -0.5, 0.05, -0.3])
s_dot = surface.compute_derivative(state, state_dot)
print(f"Surface derivative: {s_dot:.4f}")

# Check sliding condition
if abs(s) < 0.01 and s * s_dot < 0:
    print("Sliding mode reached and maintained")
```

## Example 3: Gain Validation

```python
from src.controllers.smc.core.sliding_surface import validate_sliding_surface_gains

# Valid gains (all positive)
gains_valid = [10.0, 8.0, 15.0, 12.0]
is_valid = validate_sliding_surface_gains(gains_valid)
print(f"Valid gains: {is_valid}")  # True

# Invalid gains (c2 negative)
gains_invalid = [10.0, -8.0, 15.0, 12.0]
try:
    surface_bad = LinearSlidingSurface(gains_invalid)
except ValueError as e:
    print(f"Validation error: {e}")
```

## Example 4: Frequency Analysis

```python
# example-metadata:
# runnable: false

# Compute characteristic frequencies
c1, c2, lambda1, lambda2 = gains
omega_n1 = np.sqrt(c1 / lambda1)  # rad/s
omega_n2 = np.sqrt(c2 / lambda2)  # rad/s

print(f"Natural frequency 1: {omega_n1:.2f} rad/s")
print(f"Natural frequency 2: {omega_n2:.2f} rad/s")

# Check Nyquist criterion

(sampling frequency 100 Hz)
omega_s = 2 * np.pi * 100  # rad/s
if omega_n1 < omega_s / 5 and omega_n2 < omega_s / 5:
    print("Frequencies safe for 100 Hz sampling")
```

## Example 5: Higher-Order Surface (Super-Twisting)

```python
from src.controllers.smc.core.sliding_surface import HigherOrderSlidingSurface

# Define 6 gains

for 2nd order surface
gains_ho = [25.0, 10.0, 15.0, 12.0, 20.0, 15.0]
surface_ho = HigherOrderSlidingSurface(gains_ho)

# Compute surface and its derivative
s_ho = surface_ho.compute(state)
s_dot_ho = surface_ho.compute_derivative(state, state_dot)

print(f"Higher-order surface: s={s_ho:.4f}, ṡ={s_dot_ho:.4f}")
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/core/sliding_surface.py
:language: python
:linenos:
```



## Classes

### `SlidingSurface`

**Inherits from:** `ABC`

Abstract base class for sliding surface calculations.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/sliding_surface.py
:language: python
:pyobject: SlidingSurface
:linenos:
```

#### Methods (4)

##### `__init__(self, gains)`

[View full source →](#method-slidingsurface-__init__)

##### `_validate_gains(self)`

Validate gains for this specific sliding surface type.

[View full source →](#method-slidingsurface-_validate_gains)

##### `compute(self, state)`

Compute sliding surface value for given state.

[View full source →](#method-slidingsurface-compute)

##### `compute_derivative(self, state, state_dot)`

Compute sliding surface derivative ds/dt.

[View full source →](#method-slidingsurface-compute_derivative)



### `LinearSlidingSurface`

**Inherits from:** `SlidingSurface`

Linear sliding surface for conventional SMC.

Implements: s = λ₁ė₁ + c₁e₁ + λ₂ė₂ + c₂e₂

For double-inverted pendulum:
- e₁ = θ₁ (joint 1 angle error)
- e₂ = θ₂ (joint 2 angle error)
- ė₁ = θ̇₁ (joint 1 velocity error)
- ė₂ = θ̇₂ (joint 2 velocity error)

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/sliding_surface.py
:language: python
:pyobject: LinearSlidingSurface
:linenos:
```

#### Methods (6)

##### `__init__(self, gains)`

Initialize linear sliding surface.

[View full source →](#method-linearslidingsurface-__init__)

##### `_validate_gains(self)`

Validate that surface gains satisfy stability requirements.

[View full source →](#method-linearslidingsurface-_validate_gains)

##### `compute(self, state)`

Compute linear sliding surface value.

[View full source →](#method-linearslidingsurface-compute)

##### `compute_surface(self, state)`

Compatibility method for test interface - alias for compute().

[View full source →](#method-linearslidingsurface-compute_surface)

##### `compute_derivative(self, state, state_dot)`

Compute sliding surface derivative ds/dt.

[View full source →](#method-linearslidingsurface-compute_derivative)

##### `get_coefficients(self)`

Return surface coefficients for analysis.

[View full source →](#method-linearslidingsurface-get_coefficients)



### `HigherOrderSlidingSurface`

**Inherits from:** `SlidingSurface`

Higher-order sliding surface for Super-Twisting and advanced SMC.

Implements surfaces that include higher-order derivatives for
finite-time convergence and better disturbance rejection.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/sliding_surface.py
:language: python
:pyobject: HigherOrderSlidingSurface
:linenos:
```

#### Methods (4)

##### `__init__(self, gains, order)`

Initialize higher-order sliding surface.

[View full source →](#method-higherorderslidingsurface-__init__)

##### `_validate_gains(self)`

Validate gains for higher-order stability.

[View full source →](#method-higherorderslidingsurface-_validate_gains)

##### `compute(self, state)`

Compute higher-order sliding surface (simplified implementation).

[View full source →](#method-higherorderslidingsurface-compute)

##### `compute_derivative(self, state, state_dot)`

Compute higher-order surface derivative.

[View full source →](#method-higherorderslidingsurface-compute_derivative)



## Functions

### `create_sliding_surface(surface_type, gains)`

Factory function for creating sliding surfaces.

Args:
    surface_type: "linear" or "higher_order"
    gains: Gain vector

Returns:
    Appropriate sliding surface instance

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/sliding_surface.py
:language: python
:pyobject: create_sliding_surface
:linenos:
```



## Dependencies

This module imports:

- `from typing import List, Optional, Union, Sequence`
- `import numpy as np`
- `from abc import ABC, abstractmethod`
