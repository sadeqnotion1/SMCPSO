# controllers.base.control_primitives

**Source:** `src\controllers\base\control_primitives.py`

## Module Overview

*No module docstring available.*


## Mathematical Foundation

### Control Law Composition

**Primitive:** Atomic control operation that can be composed into complex laws.

```{math}
u = \mathcal{C}(u_1, u_2, \ldots, u_n)
```

Where $\mathcal{C}$ is composition operator (sum, max, switching, etc.).

### Additive Composition

**Superposition principle** for linear systems:

```{math}
u = u_{ff} + u_{fb} + u_{robust}
```

Where:
- $u_{ff}$: Feedforward control (model-based)
- $u_{fb}$: Feedback control (error-driven)
- $u_{robust}$: Robustness term (disturbance rejection)

**SMC example:**

```{math}
u = u_{eq} + u_{sw}
```

### Saturation Primitive

**Input saturation** enforces actuator limits:

```{math}
\text{sat}(u, u_{max}) = \begin{cases}
u_{max}, & u > u_{max} \\
u, & |u| \leq u_{max} \\
-u_{max}, & u < -u_{max}
\end{cases}
```

**Properties:**
- Non-linear (breaks superposition)
- Lipschitz continuous: $|\text{sat}(u) - \text{sat}(v)| \leq |u - v|$
- Monotonic: $u > v \Rightarrow \text{sat}(u) \geq \text{sat}(v)$

### Deadband Primitive

**Deadband** ignores small errors (avoid actuator noise):

```{math}
\text{deadband}(e, \delta) = \begin{cases}
e - \delta, & e > \delta \\
0, & |e| \leq \delta \\
e + \delta, & e < -\delta
\end{cases}
```

**Typical:** $\delta = 3 \sigma_{noise}$

### Rate Limiter Primitive

**Rate limiting** prevents actuator slew violations:

```{math}
u_k = \text{clip}(u_k^{desired}, u_{k-1} - \dot{u}_{max} \Delta t, u_{k-1} + \dot{u}_{max} \Delta t)
```

**Example:** $\dot{u}_{max} = 1000$ N/s for hydraulic actuator

### Low-Pass Filter Primitive

**First-order filter** reduces high-frequency content:

```{math}
u_f = \frac{\omega_c}{s + \omega_c} u
```

**Discrete implementation:**

```{math}
u_f[k] = \alpha u[k] + (1 - \alpha) u_f[k-1], \quad \alpha = \frac{\Delta t}{\Delta t + \tau}
```

Where $\tau = 1/\omega_c$ is filter time constant.

### Gain Scheduling Primitive

**Non-linear gain** varies with operating point:

```{math}
K(\vec{x}) = K_0 + \sum_{i=1}^{n} K_i \phi_i(\vec{x})
```

Where $\phi_i$ are basis functions (e.g., RBF, polynomial).

**Linear interpolation example:**

```{math}
K(\theta) = \begin{cases}
K_{low}, & \theta < \theta_{low} \\
K_{low} + \frac{K_{high} - K_{low}}{\theta_{high} - \theta_{low}} (\theta - \theta_{low}), & \theta_{low} \leq \theta \leq \theta_{high} \\
K_{high}, & \theta > \theta_{high}
\end{cases}
```

### Anti-Windup Primitive

**Problem:** Integral windup when saturation active.

**Solution:** Conditional integration:

```{math}
\dot{I} = \begin{cases}
e, & u_{raw} = u_{sat} \quad \text{(no saturation)} \\
0, & \text{otherwise}
\end{cases}
```

Or **back-calculation:**

```{math}
\dot{I} = e + \frac{1}{T_i} (u_{sat} - u_{raw})
```

### Observer Primitive

**State estimation** from measurements:

```{math}
\dot{\hat{x}} = A \hat{x} + B u + L(y - C \hat{x})
```

Where $L$ is observer gain matrix.

**Separation principle:** Design observer and controller independently (for linear systems).

### Composition Algebra

**Commutative:** $u_1 + u_2 = u_2 + u_1$ (for linear)

**Not commutative:** $\text{sat}(u_1 + u_2) \neq \text{sat}(u_1) + \text{sat}(u_2)$

**Associative:** $(u_1 + u_2) + u_3 = u_1 + (u_2 + u_3)$

**Distributive (partial):** For some operators

## Architecture Diagram

```{mermaid}
graph TD
    A[Raw Control u_raw] --> B[Anti-Windup]
    B --> C[Rate Limiter]
    C --> D[Saturation]
    D --> E[Low-Pass Filter]
    E --> F[Deadband]
    F --> G[Final Control u]

    B --> H[Check: Saturation Active?]
    H -->|Yes| I[Halt Integration]
    H -->|No| J[Continue Integration]

    C --> K[Check: |u̇| ≤ u̇_max?]
    K -->|No| L[Clip Rate]
    K -->|Yes| C

    D --> M[Check: |u| ≤ u_max?]
    M -->|No| N[Saturate]
    M -->|Yes| D

    style A fill:#9cf
    style G fill:#9f9
    style I fill:#f99
    style L fill:#ff9
    style N fill:#ff9
```

## Usage Examples

### Example 1: Saturation Primitive

```python
from src.controllers.base.control_primitives import saturate

# Apply saturation to control signal
u_raw = 150.0  # Exceeds actuator limit
u_max = 100.0

u = saturate(u_raw, u_max)
print(f"Saturated control: {u:.1f} N")  # 100.0 N

# Vectorized saturation
u_raw_array = np.array([150.0, 50.0, -120.0, 30.0])
u_array = saturate(u_raw_array, u_max)
print(f"Saturated controls: {u_array}")  # [100, 50, -100, 30]
```

## Example 2: Rate Limiter

```python
from src.controllers.base.control_primitives import rate_limit

# Current and previous control
u_current = 80.0
u_previous = 40.0
dt = 0.01  # Time step
u_dot_max = 1000.0  # N/s

# Apply rate limiting
u_limited = rate_limit(u_current, u_previous, u_dot_max, dt)

# Maximum allowed change:

1000 * 0.01 = 10 N
# Requested change: 80

- 40 = 40 N
# Limited change: 10 N
print(f"Rate-limited control: {u_limited:.1f} N")  # 50.0 N
```

## Example 3: Anti-Windup

```python
from src.controllers.base.control_primitives import anti_windup_back_calculation

# PID-like controller with integral term
integral = 5.0  # Accumulated integral error
u_raw = 150.0   # Requested control
u_max = 100.0

# Saturated control
u_sat = saturate(u_raw, u_max)  # 100.0 N

# Back-calculation anti-windup
T_i = 1.0  # Integration time constant
integral_correction = (u_sat - u_raw) / T_i  # Negative (reduces integral)

integral_new = integral + integral_correction * dt
print(f"Integral before: {integral:.3f}")
print(f"Integral after:  {integral_new:.3f}")  # Reduced
```

## Example 4: Low-Pass Filter

```python
from src.controllers.base.control_primitives import low_pass_filter

# Noisy control signal
u_noisy = 50.0 + 5.0 * np.random.randn()

# Filter parameters
omega_c = 20.0  # Cutoff frequency (rad/s)
dt = 0.01
tau = 1.0 / omega_c  # Time constant

# Apply filter
u_filtered_prev = 48.0  # Previous filtered value
u_filtered = low_pass_filter(u_noisy, u_filtered_prev, tau, dt)

print(f"Noisy control:    {u_noisy:.2f} N")
print(f"Filtered control: {u_filtered:.2f} N")
```

## Example 5: Complete Control Pipeline

```python
from src.controllers.base.control_primitives import (
    saturate, rate_limit, low_pass_filter, deadband
)

# Control pipeline
class ControlPipeline:
    def __init__(self, u_max, u_dot_max, tau_filter, deadband_threshold):
        self.u_max = u_max
        self.u_dot_max = u_dot_max
        self.tau = tau_filter
        self.deadband = deadband_threshold
        self.u_prev = 0.0
        self.u_filtered_prev = 0.0

    def process(self, u_raw, dt):
        # 1. Deadband (ignore small errors)
        u1 = deadband(u_raw, self.deadband)

        # 2. Rate limiting (prevent slew violations)
        u2 = rate_limit(u1, self.u_prev, self.u_dot_max, dt)

        # 3. Saturation (enforce actuator limits)
        u3 = saturate(u2, self.u_max)

        # 4. Low-pass filter (reduce high-frequency content)
        u4 = low_pass_filter(u3, self.u_filtered_prev, self.tau, dt)

        # Update history
        self.u_prev = u3  # Before filtering for rate limiting
        self.u_filtered_prev = u4

        return u4

# Usage
pipeline = ControlPipeline(
    u_max=100.0,
    u_dot_max=1000.0,
    tau_filter=0.05,
    deadband_threshold=0.5
)

u_raw = -75.0  # Raw controller output
u_final = pipeline.process(u_raw, dt=0.01)
print(f"Final control: {u_final:.2f} N")
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/base/control_primitives.py
:language: python
:linenos:
```



## Functions

### `require_positive(value, name)`

Validate that a numeric value is positive (or non‑negative).

Parameters
----------
value : float or int or None
    The numeric quantity to validate.
name : str
    The name of the parameter (used in the error message).
allow_zero : bool, optional
    When True, a value of exactly zero is allowed; otherwise values must
    be strictly greater than zero.

Returns
-------
float
    The validated value cast to ``float``.

Raises
------
ValueError
    If ``value`` is ``None``, not a finite number, or does not satisfy
    the positivity requirement.

Notes
-----
Many control gains and time constants must be positive to ensure
stability in sliding‑mode and adaptive control laws【462167782799487†L186-L195】.
Centralising positivity checks via this helper reduces duplicated logic
across controllers and configuration validators.  Callers may still
choose to perform their own validation before construction, but using
this helper ensures consistent error messages and thresholds.

#### Source Code

```{literalinclude} ../../../src/controllers/base/control_primitives.py
:language: python
:pyobject: require_positive
:linenos:
```



### `require_in_range(value, name)`

Validate that a numeric value lies within a closed or open interval.

Parameters
----------
value : float or int or None
    The numeric quantity to validate.
name : str
    The name of the parameter (used in the error message).
minimum : float
    Lower bound of the allowed interval.
maximum : float
    Upper bound of the allowed interval.
allow_equal : bool, optional
    If True (default) the bounds are inclusive; if False the value
    must satisfy ``minimum < value < maximum``.

Returns
-------
float
    The validated value cast to ``float``.

Raises
------
ValueError
    If ``value`` is ``None``, not finite, or lies outside the
    specified interval.

Notes
-----
Range constraints arise frequently in control law design; for
example, a controllability threshold should be positive but small,
whereas adaptation gains must lie within finite bounds to ensure
stability【462167782799487†L186-L195】.  Centralising range checks
avoids duplicating logic across the project and produces uniform
error messages.

#### Source Code

```{literalinclude} ../../../src/controllers/base/control_primitives.py
:language: python
:pyobject: require_in_range
:linenos:
```



### `saturate(sigma, epsilon, method)`

Continuous approximation of sign(sigma) within a boundary layer.

Args:
    sigma: Sliding surface value(s).
    epsilon: Boundary-layer half-width in σ-space (must be > 0).  # ε is the half-width in σ-space.
    method: "tanh" (default) uses tanh(sigma/epsilon);
            "linear" uses clip(sigma/epsilon, -1, 1).
Returns:
    Same shape as `sigma`.

Notes
-----
The boundary layer width ``epsilon`` should be chosen based on the
expected amplitude of measurement noise and the desired steady‑state
accuracy.  A larger ``epsilon`` reduces chattering but introduces
a finite steady‑state error; conversely, a smaller ``epsilon`` reduces
error but may increase high‑frequency switching【538884328193976†L412-L423】.

Raises:
    ValueError
        If ``epsilon <= 0`` or an unknown ``method`` is provided.

#### Source Code

```{literalinclude} ../../../src/controllers/base/control_primitives.py
:language: python
:pyobject: saturate
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import math`
- `import numpy as np`
- `from typing import Literal`
