# controllers.smc.algorithms.adaptive.adaptation_law

**Source:** `src\controllers\smc\algorithms\adaptive\adaptation_law.py`

## Module Overview

Adaptive Gain Update Laws for Adaptive SMC.

Implements online gain adaptation algorithms based on sliding mode theory.
The adaptation law adjusts switching gain K(t) to handle unknown uncertainties.

Mathematical Background:
- Adaptation law: K̇ = γ|s| - σK (with leakage)
- Lyapunov stability: V̇ = sṡ + (K̃/γ)K̇ ≤ 0
- Bounded adaptation: K_min ≤ K(t) ≤ K_max


## Advanced Mathematical Theory

### Lyapunov-Based Adaptation

**Adaptation law with leakage:**

```{math}
\dot{K} = \gamma |s| - \sigma K
```

Where:
- $\gamma > 0$: Adaptation rate
- $\sigma \geq 0$: Leakage coefficient (prevents unbounded growth)

### Lyapunov Stability Analysis

**Candidate Lyapunov function:**

```{math}
V(s, \tilde{K}) = \frac{1}{2} s^2 + \frac{1}{2\gamma} \tilde{K}^2
```

Where $\tilde{K} = K - K^*$ is gain error.

**Time derivative:**

```{math}
\dot{V} = s \dot{s} + \frac{1}{\gamma} \tilde{K} \dot{K}
```

With control $u = -K \, \text{sign}(s)$ and adaptation law:

```{math}
\dot{V} \leq -\eta |s| - \frac{\sigma}{\gamma} \tilde{K}^2 < 0
```

Ensures **asymptotic stability**.

### Parameter Update Laws

**Gradient adaptation:**

```{math}
\dot{\vec{K}} = -\Gamma \frac{\partial V}{\partial \vec{K}} = \Gamma \vec{\phi}(\vec{x}) |s|
```

Where $\vec{\phi}$ is regressor vector.

**Sigma modification:**

```{math}
\dot{K} = \gamma |s| - \sigma K - \mu (K - K_0)
```

Adds centering term to prevent drift.

### Bounded Adaptation

**Hard limits:**

```{math}
K_{min} \leq K(t) \leq K_{max}
```

**Rate limiting:**

```{math}
|\dot{K}| \leq \dot{K}_{max}
```

### Dead Zone

Avoid adaptation in small-$|s|$ region:

```{math}
\dot{K} = \begin{cases}
\gamma |s| - \sigma K, & |s| > \delta \\
-\sigma K, & |s| \leq \delta
\end{cases}
```

### Convergence Analysis

**Barbalat's Lemma:** If $V$ is bounded below, $\dot{V} \leq 0$, and $\ddot{V}$ bounded, then $\dot{V} \to 0$.

**Conclusion:** $s \to 0$ and $\tilde{K} \to 0$ as $t \to \infty$.

## Architecture Diagram

```{mermaid}
graph TD
    A[Sliding Surface |s|] --> B[Adaptation: K̇ = γ|s| - σK]
    B --> C[Integrate]
    C --> D{K Bounds}
    D -->|K < K_min| E[Clip to K_min]
    D -->|K > K_max| F[Clip to K_max]
    D -->|K_min ≤ K ≤ K_max| G[Updated Gain K]

    E --> G
    F --> G
    G --> H[To Controller]

    style B fill:#9cf
    style G fill:#9f9
```

## Usage Examples

### Example 1: Basic Initialization

```python
from src.controllers.smc.algorithms.adaptive import *

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

```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/adaptation_law.py
:language: python
:linenos:
```



## Classes

### `AdaptationLaw`

Online gain adaptation for Adaptive SMC.

Implements adaptive laws that adjust switching gains based on
sliding surface behavior to handle uncertain disturbances.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/adaptation_law.py
:language: python
:pyobject: AdaptationLaw
:linenos:
```

#### Methods (9)

##### `__init__(self, adaptation_rate, uncertainty_bound, leak_rate, rate_limit, bounds, dead_zone)`

Initialize adaptation law.

[View full source →](#method-adaptationlaw-__init__)

##### `update_gain(self, surface_value, dt, uncertainty_estimate)`

Update adaptive gain using adaptation law.

[View full source →](#method-adaptationlaw-update_gain)

##### `get_current_gain(self)`

Get current adaptive gain value.

[View full source →](#method-adaptationlaw-get_current_gain)

##### `reset_gain(self, initial_gain)`

Reset adaptive gain to initial value.

[View full source →](#method-adaptationlaw-reset_gain)

##### `is_adaptation_active(self, surface_value)`

Check if adaptation is currently active.

[View full source →](#method-adaptationlaw-is_adaptation_active)

##### `get_adaptation_rate(self, surface_value)`

Get current adaptation rate K̇.

[View full source →](#method-adaptationlaw-get_adaptation_rate)

##### `analyze_adaptation_performance(self)`

Analyze adaptation performance from history.

[View full source →](#method-adaptationlaw-analyze_adaptation_performance)

##### `set_adaptation_parameters(self, gamma, sigma, rate_limit)`

Update adaptation parameters during runtime.

[View full source →](#method-adaptationlaw-set_adaptation_parameters)

##### `get_lyapunov_derivative(self, surface_value, surface_derivative)`

Compute Lyapunov function derivative for stability analysis.

[View full source →](#method-adaptationlaw-get_lyapunov_derivative)



### `ModifiedAdaptationLaw`

**Inherits from:** `AdaptationLaw`

Modified adaptation law with additional robustness features.

Includes projection operator and improved stability properties.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/adaptation_law.py
:language: python
:pyobject: ModifiedAdaptationLaw
:linenos:
```

#### Methods (3)

##### `__init__(self)`

Initialize modified adaptation law.

[View full source →](#method-modifiedadaptationlaw-__init__)

##### `update_gain(self, surface_value, dt, uncertainty_estimate)`

Update gain with projection operator.

[View full source →](#method-modifiedadaptationlaw-update_gain)

##### `_is_projection_active(self, K_dot)`

Check if projection operator is currently active.

[View full source →](#method-modifiedadaptationlaw-_is_projection_active)



## Dependencies

This module imports:

- `from typing import Optional, Union`
- `import numpy as np`
