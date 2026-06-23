# simulation.integrators.adaptive.error_control

**Source:** `src\simulation\integrators\adaptive\error_control.py`

## Module Overview

Error control and step size adaptation for adaptive integration.


## Mathematical Foundation

### Adaptive Error Control

Automatic adjustment of integration step size based on local error estimates.

### Error Metrics

**Absolute Error:**
```{math}
e_{\text{abs}} = |y_{\text{exact}}(t_{n+1}) - y_{n+1}|
```

**Relative Error:**
```{math}
e_{\text{rel}} = \frac{|y_{\text{exact}}(t_{n+1}) - y_{n+1}|}{|y_{\text{exact}}(t_{n+1})|}
```

**Mixed Error (Scaled):**
```{math}
e_{\text{scaled}} = \frac{|\hat{y}_{n+1} - y_{n+1}|}{\text{atol} + |y_{n+1}| \cdot \text{rtol}}
```

### Error Tolerance

**Absolute tolerance (`atol`):** Minimum acceptable accuracy
**Relative tolerance (`rtol`):** Proportional accuracy requirement

**Combined tolerance:**
```{math}
\tau_i = \text{atol} + |y_i| \cdot \text{rtol}
```

**Typical values:**
- High accuracy: `atol=1e-9`, `rtol=1e-6`
- Standard: `atol=1e-6`, `rtol=1e-3`
- Low accuracy: `atol=1e-3`, `rtol=1e-2`

### Step Size Selection Strategies

#### **1. Elementary Controller**

```{math}
\Delta t_{n+1} = \Delta t_n \cdot \left(\frac{\text{tol}}{\text{err}_n}\right)^{1/p}
```

Where $p$ is the lower order of the embedded pair.

#### **2. PI Controller (Industry Standard)**

```{math}
\Delta t_{n+1} = \Delta t_n \cdot \left(\frac{\text{tol}}{\text{err}_n}\right)^{k_P} \cdot \left(\frac{\text{err}_{n-1}}{\text{err}_n}\right)^{k_I}
```

**Advantages:**
- Smoother step size changes
- Better rejection handling
- Reduced oscillations

#### **3. PID Controller (Advanced)**

```{math}
\Delta t_{n+1} = \Delta t_n \cdot \left(\frac{\text{tol}}{\text{err}_n}\right)^{k_P} \cdot \left(\frac{\text{err}_{n-1}}{\text{err}_n}\right)^{k_I} \cdot \left(\frac{\text{err}_{n-1}^2}{\text{err}_n \cdot \text{err}_{n-2}}\right)^{k_D}
```

### Safety Mechanisms

**Safety factor:** Prevent aggressive step size changes
```{math}
\text{fac}_{\text{min}} \leq \frac{\Delta t_{n+1}}{\Delta t_n} \leq \text{fac}_{\text{max}}
```

Typical: $\text{fac}_{\min} = 0.2$, $\text{fac}_{\max} = 10.0$

**Step bounds:**
```{math}
\Delta t_{\min} \leq \Delta t_{n+1} \leq \Delta t_{\max}
```

**Maximum step rejections:** Prevent infinite loops
```{math}
N_{\text{reject}} < N_{\max} \quad (\text{typically } N_{\max} = 10)
```

### Stiffness Detection

**Stiffness ratio:**
```{math}
S = \frac{|\lambda_{\max}|}{|\lambda_{\min}|}
```

**Heuristic stiffness indicator:**
```{math}
\text{Stiff} \Leftrightarrow \frac{\Delta t_{\text{explicit}}}{\Delta t_{\text{implicit}}} > 100
```

### Error Control Algorithm

```python
# example-metadata:
# runnable: false

while t < t_final:
    # Attempt integration step
    y_new, y_hat = integrate_step(t, y, dt)

    # Estimate error
    error = norm((y_new - y_hat) / (atol + abs(y_new) * rtol))

    # Acceptance decision
    if error <= 1.0:
        # Accept step
        t += dt
        y = y_new

        # Increase step size for next step
        dt_new = 0.9 * dt * error**(-1/5)
    else:
        # Reject step
        # Decrease step size and retry
        dt_new = 0.9 * dt * error**(-1/4)

    # Apply safety bounds
    dt = clip(dt_new, dt_min, dt_max)
```

### Performance Metrics

**Efficiency:**
```{math}
\eta = \frac{N_{\text{accepted}}}{N_{\text{accepted}} + N_{\text{rejected}}}
```

Target: $\eta > 0.9$ (90% acceptance rate)

**Work-Precision Diagram:**
Plot accuracy vs computational cost for different tolerances.

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
from src.simulation.integrators import IntegratorsAdaptiveErrorControl

# Initialize
instance = IntegratorsAdaptiveErrorControl()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = IntegratorsAdaptiveErrorControl(config)
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

```{literalinclude} ../../../src/simulation/integrators/adaptive/error_control.py
:language: python
:linenos:
```



## Classes

### `ErrorController`

Basic error controller for adaptive step size methods.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/adaptive/error_control.py
:language: python
:pyobject: ErrorController
:linenos:
```

#### Methods (2)

##### `__init__(self, safety_factor)`

Initialize error controller.

[View full source →](#method-errorcontroller-__init__)

##### `update_step_size(self, error_norm, current_dt, min_dt, max_dt, order)`

Update step size based on error estimate.

[View full source →](#method-errorcontroller-update_step_size)



### `PIController`

**Inherits from:** `ErrorController`

PI (Proportional-Integral) controller for step size adaptation.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/adaptive/error_control.py
:language: python
:pyobject: PIController
:linenos:
```

#### Methods (3)

##### `__init__(self, safety_factor, alpha, beta)`

Initialize PI controller.

[View full source →](#method-picontroller-__init__)

##### `update_step_size(self, error_norm, current_dt, min_dt, max_dt, order)`

Update step size using PI control.

[View full source →](#method-picontroller-update_step_size)

##### `reset(self)`

Reset controller state.

[View full source →](#method-picontroller-reset)



### `DeadBeatController`

**Inherits from:** `ErrorController`

Dead-beat controller for aggressive step size adaptation.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/adaptive/error_control.py
:language: python
:pyobject: DeadBeatController
:linenos:
```

#### Methods (2)

##### `__init__(self, safety_factor, target_error)`

Initialize dead-beat controller.

[View full source →](#method-deadbeatcontroller-__init__)

##### `update_step_size(self, error_norm, current_dt, min_dt, max_dt, order)`

Update step size using dead-beat control.

[View full source →](#method-deadbeatcontroller-update_step_size)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Tuple`
- `import numpy as np`
