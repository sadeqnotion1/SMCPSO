# utils.control.saturation

**Source:** `src\utils\control\saturation.py`

## Module Overview

Saturation functions for sliding mode control.

Provides continuous approximations of the sign function to reduce chattering
in sliding mode controllers.

## Complete Source Code

```{literalinclude} ../../../src/utils/control/saturation.py
:language: python
:linenos:
```



## Functions

### `saturate(sigma, epsilon, method, slope)`

Continuous approximation of sign(sigma) within a boundary layer.

Args:
    sigma: Sliding surface value(s).
    epsilon: Boundary-layer half-width in σ-space (must be > 0).
    method: "tanh" (default) uses tanh((slope * sigma)/epsilon);
            "linear" uses clip(sigma/epsilon, -1, 1).
    slope: Slope parameter for tanh switching (default: 3.0).
           Lower values (2-5) provide smoother transitions and better
           chattering reduction. Original implicit steep slopes (10+)
           behaved like discontinuous sign function.
Returns:
    Same shape as `sigma`.

Notes
-----
The boundary layer width ``epsilon`` should be chosen based on the
expected amplitude of measurement noise and the desired steady‑state
accuracy. A larger ``epsilon`` reduces chattering but introduces
a finite steady‑state error; conversely, a smaller ``epsilon`` reduces
error but may increase high‑frequency switching.

The slope parameter (default 3.0) was optimized for Issue #12 chattering
reduction. Lower slope values provide smoother control signals at the cost
of slightly reduced tracking accuracy near the sliding surface.

Raises:
    ValueError
        If ``epsilon <= 0`` or an unknown ``method`` is provided.

#### Source Code

```{literalinclude} ../../../src/utils/control/saturation.py
:language: python
:pyobject: saturate
:linenos:
```



### `smooth_sign(x, epsilon)`

Smooth approximation of the sign function using tanh.

Args:
    x: Input value(s).
    epsilon: Smoothing parameter.

Returns:
    Smooth sign approximation.

#### Source Code

```{literalinclude} ../../../src/utils/control/saturation.py
:language: python
:pyobject: smooth_sign
:linenos:
```



### `dead_zone(x, threshold)`

Apply dead zone to input signal.

Args:
    x: Input signal.
    threshold: Dead zone threshold (must be positive).

Returns:
    Signal with dead zone applied.

#### Source Code

```{literalinclude} ../../../src/utils/control/saturation.py
:language: python
:pyobject: dead_zone
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `import warnings`
- `from typing import Literal, Union`


## Advanced Mathematical Theory

### Saturation Functions for Control Systems

Saturation functions limit control outputs to physical actuator constraints while minimizing adverse effects like integrator windup and chattering.

#### Hard Saturation

**Definition:**
$$
\text{sat}(u) = \begin{cases}
u_{\max} & \text{if } u > u_{\max} \\
u & \text{if } u_{\min} \leq u \leq u_{\max} \\
u_{\min} & \text{if } u < u_{\min}
\end{cases}
$$

**Vector form:**
$$
\text{sat}(\vec{u})_i = \max(u_{i,\min}, \min(u_i, u_{i,\max}))
$$

**Properties:**
- Discontinuous at boundaries
- May cause chattering in sliding mode control
- Simple and computationally efficient

#### Smooth Saturation (tanh)

**Definition:**
$$
\text{sat}_{\text{smooth}}(u, u_{\max}) = u_{\max} \tanh\left(\frac{u}{u_{\max}}\right)
$$

**Properties:**
- Continuously differentiable everywhere
- Asymptotically approaches $\pm u_{\max}$
- Derivative: $\frac{d}{du}\text{sat}_{\text{smooth}}(u) = \frac{1}{\cosh^2(u/u_{\max})}$
- Reduces chattering in SMC

#### Dead Zone

**Definition:**
$$
\text{dz}(u, \delta) = \begin{cases}
u - \delta & \text{if } u > \delta \\
0 & \text{if } |u| \leq \delta \\
u + \delta & \text{if } u < -\delta
\end{cases}
$$

**Applications:**
- Noise filtering: Ignore small control signals below threshold
- Anti-windup: Prevent integrator accumulation for small errors
- Robustness: Reject sensor noise and quantization effects

### Saturation Effects on Stability

**Anti-windup compensation:**

For PI controller with saturation:
$$
u = K_P e + K_I \int_0^t e(\tau) d\tau
$$

With anti-windup:
$$
\dot{x}_I = \begin{cases}
e(t) & \text{if not saturated} \\
0 & \text{if saturated}
\end{cases}
$$

## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Control Signal u] --> B{Saturation Type}

    B -->|Hard| C[Hard Saturation]
    B -->|Smooth| D[Smooth tanh]
    B -->|Dead Zone| E[Dead Zone]

    C --> F[max_u_min, min_u, u_max__]
    D --> G[u_max·tanh_u/u_max_]
    E --> H[Remove |u| < δ]

    F --> I[Saturated Control]
    G --> I
    H --> I

    I --> J{Anti-Windup?}
    J -->|Yes| K[Stop Integrator]
    J -->|No| L[Apply to Plant]

    K --> L
    L --> M[Plant Response]

    style B fill:#fff4e1
    style I fill:#e8f5e9
    style K fill:#ffebee
\`\`\`

## Usage Examples

### Example 1: Basic Hard Saturation

\`\`\`python
from src.utils.control import saturate

# Scalar saturation

u = 150.0  # Exceeds limit
u_sat = saturate(u, u_min=-100.0, u_max=100.0)
print(f"Saturated: {u} -> {u_sat}")  # 150.0 -> 100.0

# Vector saturation

u_vec = np.array([50, -120, 80])
u_sat_vec = saturate(u_vec, u_min=-100.0, u_max=100.0)
print(f"Vector saturation: {u_sat_vec}")  # [50, -100, 80]
\`\`\`

## Example 2: Smooth

Saturation for Chattering Reduction

\`\`\`python
from src.utils.control import smooth_sign
import numpy as np

# SMC with smooth saturation

def smc_with_smooth_saturation(x, sliding_surface, K, epsilon=0.1):
    """SMC using smooth sign function (tanh)."""
    s = sliding_surface(x)

    # Smooth sign instead of hard sign
    u = -K * smooth_sign(s, epsilon)

    return u

# Comparison: hard vs smooth

s_values = np.linspace(-1, 1, 100)
hard_sign = np.sign(s_values)
smooth = np.array([smooth_sign(s, 0.1) for s in s_values])

# Plot to show smoothness

import matplotlib.pyplot as plt
plt.plot(s_values, hard_sign, label='Hard sign', linestyle='--')
plt.plot(s_values, smooth, label='Smooth sign (tanh)')
plt.xlabel('Sliding Surface s')
plt.ylabel('Switching Function')
plt.legend()
plt.grid(True)
plt.show()
\`\`\`

## Example 3: Dead

Zone for Noise Filtering

\`\`\`python
from src.utils.control import dead_zone

# Filter small control signals

u_noisy = np.array([0.05, -0.02, 5.0, -3.0, 0.08])
threshold = 0.1

u_filtered = dead_zone(u_noisy, threshold)
print(f"Filtered: {u_filtered}")
# Result: [0, 0,

4.9, -2.9, 0] (small signals removed)

# Application: PD controller with dead zone

def pd_control_with_dead_zone(x, x_ref, Kp, Kd, dead_zone_threshold):
    error = x_ref - x
    error_dot = -np.gradient(x)  # Simplified

    u_pd = Kp * error + Kd * error_dot

    # Apply dead zone to avoid actuator wear from small commands
    u = dead_zone(u_pd, dead_zone_threshold)

    return u
\`\`\`

## Example 4: Anti-Windup with Saturation

\`\`\`python
from src.utils.control import saturate

class PIControllerWithAntiWindup:
    def __init__(self, Kp, Ki, u_min, u_max):
        self.Kp = Kp
        self.Ki = Ki
        self.u_min = u_min
        self.u_max = u_max
        self.integral = 0.0

    def compute(self, error, dt):
        # Proportional term
        u_p = self.Kp * error

        # Integral term
        u_i = self.Ki * self.integral

        # Total control before saturation
        u_total = u_p + u_i

        # Apply saturation
        u_sat = saturate(u_total, self.u_min, self.u_max)

        # Anti-windup: only integrate if not saturated
        if abs(u_total - u_sat) < 1e-6:  # Not saturated
            self.integral += error * dt
        # else: stop integrating (anti-windup)

        return u_sat

# Use PI with anti-windup

controller = PIControllerWithAntiWindup(Kp=10, Ki=5, u_min=-100, u_max=100)

for k in range(100):
    error = x_ref - x
    u = controller.compute(error, dt=0.01)
    # Integral won't wind up during saturation
\`\`\`

## Example 5: Saturation Monitoring

\`\`\`python
from src.utils.control import saturate
import numpy as np

def monitor_saturation(u_desired, u_min, u_max):
    """Monitor saturation frequency and severity."""

    u_actual = saturate(u_desired, u_min, u_max)

    # Saturation indicator
    is_saturated = (np.abs(u_actual - u_desired) > 1e-6)

    # Saturation ratio
    if np.linalg.norm(u_desired) > 0:
        ratio = np.linalg.norm(u_actual) / np.linalg.norm(u_desired)
    else:
        ratio = 1.0

    return {
        'u_actual': u_actual,
        'is_saturated': is_saturated,
        'saturation_ratio': ratio
    }

# Track saturation during simulation

saturation_count = 0
saturation_ratios = []

for k in range(1000):
    u_desired = controller.compute_control(x, state_vars, history)

    sat_info = monitor_saturation(u_desired, u_min=-100, u_max=100)

    if sat_info['is_saturated']:
        saturation_count += 1

    saturation_ratios.append(sat_info['saturation_ratio'])

    u = sat_info['u_actual']
    x = integrator.integrate(dynamics, x, u, t)
    t += dt

print(f"Saturation frequency: {saturation_count/1000:.1%}")
print(f"Mean saturation ratio: {np.mean(saturation_ratios):.3f}")
\`\`\`
