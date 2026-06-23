# controllers.smc.algorithms.super_twisting.twisting_algorithm

**Source:** `src\controllers\smc\algorithms\super_twisting\twisting_algorithm.py`

## Module Overview

Super-Twisting Algorithm Implementation.

Implements the core Super-Twisting sliding mode algorithm for finite-time convergence.
The algorithm provides second-order sliding mode control with chattering reduction.

Mathematical Background:
- Control law: u = u₁ + u₂
- u₁ = -K₁|s|^α sign(s)
- u₂ = -K₂ ∫sign(s)dt
- Stability: K₁ > K₂ > 0 for finite-time convergence


## Advanced Mathematical Theory

### Super-Twisting Control Law

**Two-component structure:**

```{math}
u = u_1 + u_2 = -K_1 |s|^{\alpha} \text{sign}(s) - K_2 \int \text{sign}(s) dt
```

Where:
- $K_1, K_2 > 0$: Gains
- $\alpha \in (0, 1)$: Exponent (typically 0.5)
- $u_1$: Continuous feedback (no chattering)
- $u_2$: Integral term (finite-time convergence)

### Finite-Time Convergence

**Convergence time bound:**

```{math}
t_{conv} \leq \frac{2 |s(0)|^{1-\alpha/2}}{\eta (1 - \alpha/2)}
```

**Sliding variable and its derivative both reach zero:**

```{math}
s = \dot{s} = 0 \quad \text{in finite time}
```

### Gain Selection Criteria

**Sufficient conditions for finite-time stability:**

```{math}
\begin{align}
K_1 &> \frac{L_1}{\lambda_{min}^{1/2}} \\
K_2 &> \frac{K_1 L_1}{\lambda_{min}} + \frac{L_0}{\lambda_{min}}
\end{align}
```

Where:
- $L_0, L_1$: Bounds on disturbance and its derivative
- $\lambda_{min}$: Minimum eigenvalue of system matrix

### Lyapunov Analysis

**Lyapunov function candidate:**

```{math}
V = \zeta^T \mathbf{P} \zeta, \quad \zeta = [|s|^{\alpha} \text{sign}(s), \, \dot{s}]^T
```

Where $\mathbf{P} = \mathbf{P}^T > 0$ is found via LMI.

**Homogeneity property** enables finite-time analysis.

### Second-Order Sliding Mode

**Sliding manifold:**

```{math}
\mathcal{S} = \{(s, \dot{s}) : s = \dot{s} = 0\}
```

Ensures both position and velocity errors converge.

### Continuous Control

**No sign function in control:**

- $u_1$ uses $|s|^{0.5} \text{sign}(s)$ (continuous)
- $u_2$ is integral (smooth)
- **Result:** Continuous control signal (minimal chattering)

## Architecture Diagram

```{mermaid}
graph TD
    A[Sliding Surface s] --> B[Continuous: u₁ = -K₁|s|^α sign_s_]
    A --> C[Integral: u₂ = -K₂ ∫sign_s_dt]

    B --> D[Combiner: u = u₁ + u₂]
    C --> D

    C --> E[Anti-Windup]
    E -->|Saturation Active| F[Halt Integration]
    E -->|No Saturation| G[Continue Integration]

    D --> H[Control Output u]

    style B fill:#9cf
    style C fill:#ff9
    style H fill:#9f9
```

## Usage Examples

### Example 1: Basic Initialization

```python
from src.controllers.smc.algorithms.super_twisting import *

# Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
```

## Example 2: Performance Tuning

```python
# Adjust parameters for better performance
optimized_params = tune_parameters(instance, target_performance)
```

## Example 3: Integration with Controller

```python
# Use in complete control loop
controller = create_controller(ctrl_type, config)
result = simulate(controller, duration=5.0)
```

## Example 4: Edge Case Handling

```python
try:
    output = instance.compute(state)
except ValueError as e:
    handle_edge_case(e)
```

### Example 5: Performance Analysis

```python
# Analyze metrics
metrics = compute_metrics(result)
print(f"ITAE: {metrics.itae:.3f}")
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/super_twisting/twisting_algorithm.py
:language: python
:linenos:
```



## Classes

### `SuperTwistingAlgorithm`

Core Super-Twisting sliding mode algorithm.

Implements second-order sliding mode control with finite-time convergence:
- Continuous control component: u₁ = -K₁|s|^α sign(s)
- Integral component: u₂ = -K₂ ∫sign(s)dt

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/super_twisting/twisting_algorithm.py
:language: python
:pyobject: SuperTwistingAlgorithm
:linenos:
```

#### Methods (11)

##### `__init__(self, K1, K2, alpha, anti_windup_limit, regularization)`

Initialize Super-Twisting algorithm.

[View full source →](#method-supertwistingalgorithm-__init__)

##### `compute_control(self, surface_value, dt, switching_function, boundary_layer)`

Compute Super-Twisting control law.

[View full source →](#method-supertwistingalgorithm-compute_control)

##### `_compute_switching_function(self, s, method, epsilon)`

Compute switching function sign(s) with smooth approximation.

[View full source →](#method-supertwistingalgorithm-_compute_switching_function)

##### `reset_state(self)`

Reset algorithm internal state.

[View full source →](#method-supertwistingalgorithm-reset_state)

##### `set_gains(self, K1, K2)`

Update twisting gains.

[View full source →](#method-supertwistingalgorithm-set_gains)

##### `get_gains(self)`

Get current twisting gains (K1, K2).

[View full source →](#method-supertwistingalgorithm-get_gains)

##### `check_stability_condition(self)`

Check if current gains satisfy stability condition.

[View full source →](#method-supertwistingalgorithm-check_stability_condition)

##### `estimate_convergence_time(self, initial_surface)`

Estimate finite-time convergence time.

[View full source →](#method-supertwistingalgorithm-estimate_convergence_time)

##### `analyze_performance(self, surface_history)`

Analyze Super-Twisting performance from surface history.

[View full source →](#method-supertwistingalgorithm-analyze_performance)

##### `get_lyapunov_function(self, surface_value, surface_derivative)`

Compute Lyapunov function for stability analysis.

[View full source →](#method-supertwistingalgorithm-get_lyapunov_function)

##### `get_state_dict(self)`

Get current algorithm state for logging/debugging.

[View full source →](#method-supertwistingalgorithm-get_state_dict)



## Dependencies

This module imports:

- `from typing import Optional, Dict, Any`
- `import numpy as np`
- `import math`
