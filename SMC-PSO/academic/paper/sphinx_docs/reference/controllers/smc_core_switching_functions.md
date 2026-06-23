# controllers.smc.core.switching_functions

**Source:** `src\controllers\smc\core\switching_functions.py`

## Module Overview

Switching Functions for SMC Chattering Reduction.

Provides continuous approximations to the discontinuous sign function used in SMC.
These functions reduce chattering while maintaining the robustness properties of SMC.

Mathematical Background:
- Sign function: sign(s) = {+1 if s>0, -1 if s<0, 0 if s=0}
- Continuous approximations smooth the switching to reduce high-frequency oscillations
- Trade-off: smoother switching reduces chattering but may increase steady-state error


## Mathematical Foundation

### Chattering Reduction in SMC

**Chattering** is high-frequency oscillation around the sliding surface caused by discontinuous control.

### Sign Function (Ideal SMC)

```{math}
u_{sw} = -K \, \text{sign}(s)
```

**Problems:**
- Infinite switching frequency (theory)
- Actuator wear and heat (practice)
- Excites unmodeled dynamics
- Measurement noise amplification

### Boundary Layer Method

Replace sign with continuous approximation within layer $\epsilon > 0$:

```{math}
\text{sat}(s/\epsilon) = \begin{cases}
1, & s > \epsilon \\
s/\epsilon, & |s| \leq \epsilon \\
-1, & s < -\epsilon
\end{cases}
```

**Properties:**
- Continuous everywhere
- Lipschitz continuous: $|\text{sat}(s/\epsilon) - \text{sat}(s'/\epsilon)| \leq |s - s'|/\epsilon$
- Reduces chattering to bounded oscillation: $|s| \leq \epsilon$

### Tanh Smoothing

```{math}
\text{tanh}\left(\frac{\beta s}{\epsilon}\right)
```

**Advantages:**
- Smooth (infinitely differentiable)
- Slope parameter $\beta$ controls sharpness
- Better frequency response than saturation

**Slope selection:**
- $\beta = 3$ (default): Smooth transition, minimal chattering
- $\beta = 10$: Sharper transition, closer to sign function
- $\beta < 2$: Too smooth, tracking degrades

### Frequency Analysis

**Describing function** for tanh switching:

```{math}
N(A) = \frac{4 \beta}{\pi \epsilon A} \int_0^{\pi/2} \tanh(\beta A \sin \phi) \sin \phi \, d\phi
```

**For small $A \ll \epsilon$:**

```{math}
N(A) \approx \frac{\beta}{\epsilon}
```

**Chattering frequency estimate:**

```{math}
\omega_c \approx \sqrt{\frac{K \beta}{\epsilon m}}
```

Where $m$ is effective inertia.

### Trade-offs

**Larger $\epsilon$:**
- ✅ Less chattering
- ❌ Larger steady-state error: $|e_{ss}| \leq \epsilon \max_i \lambda_i$

**Smaller $\epsilon$:**
- ✅ Better tracking accuracy
- ❌ More chattering

**Typical design:**

```{math}
\epsilon = 3 \sigma_{noise}
```

Where $\sigma_{noise}$ is measurement noise standard deviation.

### Dead Zone

For very small surface values, use dead zone to avoid chattering:

```{math}
u_{sw} = \begin{cases}
-K \, \text{tanh}(s/\epsilon), & |s| > \delta \\
0, & |s| \leq \delta
\end{cases}
```

**Typical:** $\delta = 0.1 \epsilon$

### Higher-Order Approximations

**Sigmoid function:**

```{math}
\frac{2}{1 + e^{-\beta s/\epsilon}} - 1
```

**Properties:**
- Smooth like tanh
- Symmetric around origin
- Computationally similar cost

### Implementation Considerations

**Numerical precision:**
- Avoid $s/\epsilon$ when $\epsilon \to 0$
- Clamp tanh argument: $|\beta s/\epsilon| \leq 20$ (prevents overflow)

**Real-time constraints:**
- tanh: ~10-20 CPU cycles
- saturation: ~5 CPU cycles
- sign: ~1 CPU cycle

### Chattering Index Metric

Quantify chattering via **switching count** in window $T$:

```{math}
I_c = \frac{1}{T} \int_0^T |\dot{u}(t)| dt
```

**Goal:** $I_c < I_{max}$ (e.g., $I_{max} = 100$ N/s for actuator)

## Architecture Diagram

```{mermaid}
graph TD
    A[Sliding Surface s] --> B{Switching Method}
    B -->|sign| C[Discontinuous: sign_s_]
    B -->|saturation| D[Boundary Layer: sat_s/ε_]
    B -->|tanh| E[Smooth: tanh_βs/ε_]

    C --> F[High Chattering]
    D --> G[Reduced Chattering, Bounded |s| ≤ ε]
    E --> H[Minimal Chattering, Smooth]

    E --> I[Check: |βs/ε| < 20]
    I -->|Yes| J[Compute tanh]
    I -->|No| K[Clamp Argument]
    K --> J

    style C fill:#f99
    style D fill:#ff9
    style E fill:#9cf
    style H fill:#9f9
```

## Usage Examples

### Example 1: Tanh Switching Function

```python
from src.utils.control.saturation import saturate
import numpy as np

# Sliding surface value
s = 0.05  # rad

# Boundary layer parameters
epsilon = 0.01  # rad
beta = 3.0  # Slope parameter

# Compute tanh switching
u_sw = saturate(s, epsilon, method='tanh', slope=beta)
print(f"Switching control: {u_sw:.4f}")

# For s >>

epsilon, u_sw → 1.0
# For s <<

-epsilon, u_sw → -1.0
# For |s| < epsilon, smooth transition
```

## Example 2: Chattering Comparison

```python
import matplotlib.pyplot as plt

# Time series
t = np.linspace(0, 5, 5000)
s_trajectory = 0.02 * np.sin(10 * t) + 0.005 * np.random.randn(len(t))

# Different switching methods
u_sign = np.sign(s_trajectory)
u_sat = np.clip(s_trajectory / epsilon, -1, 1)
u_tanh = np.tanh(beta * s_trajectory / epsilon)

# Compute chattering index (control derivative)
chat_sign = np.sum(np.abs(np.diff(u_sign)))
chat_sat = np.sum(np.abs(np.diff(u_sat)))
chat_tanh = np.sum(np.abs(np.diff(u_tanh)))

print(f"Chattering index (sign):  {chat_sign:.1f}")
print(f"Chattering index (sat):   {chat_sat:.1f}")
print(f"Chattering index (tanh):  {chat_tanh:.1f}")  # Lowest
```

## Example 3: Slope Parameter Tuning

```python
# Test different slope parameters
slopes = [1.0, 3.0, 5.0, 10.0, 20.0]

for beta in slopes:
    u = saturate(s, epsilon, method='tanh', slope=beta)

    # Estimate effective switching sharpness
    s_test = np.linspace(-3*epsilon, 3*epsilon, 100)
    u_test = saturate(s_test, epsilon, method='tanh', slope=beta)
    sharpness = np.mean(np.abs(np.diff(u_test))) / (6 * epsilon / 100)

    print(f"β={beta:4.1f}: u={u:6.4f}, sharpness={sharpness:.3f}")
```

### Example 4: Dead Zone Integration

```python
# example-metadata:
# runnable: false

def dead_zone_switching(s, epsilon, delta, K):
    """Switching with dead zone to avoid chattering near origin."""
    if abs(s) < delta:
        return 0.0
    else:
        return -K * saturate(s, epsilon, method='tanh')

# Parameters
delta = 0.1 * epsilon  # Dead zone 10% of boundary layer
K = 50.0

u_sw = dead_zone_switching(s, epsilon, delta, K)
print(f"Switching with dead zone: {u_sw:.2f} N")
```

## Example 5: Frequency Response

```python
from scipy import signal

# Create transfer function for tanh switching
# Approximation: linearize around s=0
# tanh(βs/ε) ≈ (β/ε)s for small s
gain_linear = beta / epsilon

# Frequency response
frequencies = np.logspace(-1, 3, 100)  # 0.1 to 1000 rad/s
w, mag, phase = signal.bode((gain_linear, [1, 0]), frequencies)

# Plot
plt.subplot(2, 1, 1)
plt.semilogx(w, mag)
plt.ylabel('Magnitude (dB)')
plt.title(f'Tanh Switching (β={beta}, ε={epsilon})')

plt.subplot(2, 1, 2)
plt.semilogx(w, phase)
plt.ylabel('Phase (deg)')
plt.xlabel('Frequency (rad/s)')
plt.show()
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:linenos:
```



## Classes

### `SwitchingMethod`

**Inherits from:** `Enum`

Available switching function methods.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:pyobject: SwitchingMethod
:linenos:
```



### `SwitchingFunction`

Continuous switching functions for SMC chattering reduction.

Provides various approximations to the sign function, each with different
smoothness and robustness characteristics.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:pyobject: SwitchingFunction
:linenos:
```

#### Methods (8)

##### `__init__(self, method)`

Initialize switching function.

[View full source →](#method-switchingfunction-__init__)

##### `_get_switching_function(self)`

Get the appropriate switching function implementation.

[View full source →](#method-switchingfunction-_get_switching_function)

##### `compute(self, surface_value, boundary_layer)`

Compute switching function value.

[View full source →](#method-switchingfunction-compute)

##### `_tanh_switching(self, s, epsilon, slope)`

Hyperbolic tangent switching function with configurable slope.

[View full source →](#method-switchingfunction-_tanh_switching)

##### `_linear_switching(self, s, epsilon)`

Piecewise-linear saturation switching function.

[View full source →](#method-switchingfunction-_linear_switching)

##### `_sign_switching(self, s, epsilon)`

Pure sign function (discontinuous).

[View full source →](#method-switchingfunction-_sign_switching)

##### `_sigmoid_switching(self, s, epsilon, slope)`

Sigmoid switching function with configurable slope.

[View full source →](#method-switchingfunction-_sigmoid_switching)

##### `get_derivative(self, surface_value, boundary_layer)`

Compute derivative of switching function.

[View full source →](#method-switchingfunction-get_derivative)



## Functions

### `tanh_switching(s, epsilon, slope)`

Hyperbolic tangent switching function with optimized slope.

Args:
    s: Sliding surface value
    epsilon: Boundary layer thickness
    slope: Slope parameter (default: 3.0 for optimal chattering reduction)

Returns:
    tanh((slope * s)/ε) ∈ [-1, 1]

Note:
    Default slope reduced from steep (10+) to gentle (3.0) for better
    chattering reduction. Use slope=2-5 for smooth control, slope>5
    approaches discontinuous behavior.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:pyobject: tanh_switching
:linenos:
```



### `linear_switching(s, epsilon)`

Linear saturation switching function.

Args:
    s: Sliding surface value
    epsilon: Boundary layer thickness

Returns:
    sat(s/ε) = clip(s/ε, -1, 1)

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:pyobject: linear_switching
:linenos:
```



### `sign_switching(s, epsilon)`

Pure sign function (DEPRECATED - causes severe chattering).

WARNING: Discontinuous switching causes chattering in real systems.
Prefer tanh_switching() or linear_switching() with appropriate boundary layer.

Args:
    s: Sliding surface value
    epsilon: Ignored (kept for interface consistency)

Returns:
    sign(s) ∈ {-1, 0, 1}

Deprecated:
    Use tanh_switching(s, epsilon, slope=3.0) instead for chattering reduction.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:pyobject: sign_switching
:linenos:
```



### `adaptive_boundary_layer(surface_value, surface_derivative, base_epsilon, adaptation_gain)`

Adaptive boundary layer thickness based on surface derivative.

Larger ε when |ṡ| is large (fast surface motion) to increase smoothness.
Smaller ε when |ṡ| is small (near surface) to maintain precision.

Args:
    surface_value: Current sliding surface value
    surface_derivative: Surface time derivative ṡ
    base_epsilon: Base boundary layer thickness
    adaptation_gain: Adaptation coefficient

Returns:
    Adaptive boundary layer thickness

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:pyobject: adaptive_boundary_layer
:linenos:
```



### `power_rate_reaching_law(surface_value, K, alpha, epsilon)`

Power rate reaching law for finite-time convergence.

Formula: -K * |s|^α * sign(s) ≈ -K * |s|^α * tanh(s/ε)

Args:
    surface_value: Sliding surface value s
    K: Reaching law gain (> 0)
    alpha: Power exponent (0 < α < 1 for finite-time)
    epsilon: Boundary layer for sign approximation

Returns:
    Power rate reaching law output

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/switching_functions.py
:language: python
:pyobject: power_rate_reaching_law
:linenos:
```



## Dependencies

This module imports:

- `from typing import Union, Callable`
- `import numpy as np`
- `from enum import Enum`
