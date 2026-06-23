# plant.models.simplified.config

<!-- Enhanced by Week 8 Phase 2 -->


**Source:** `src\plant\models\simplified\config.py`

## Module Overview

Configuration for Simplified DIP Dynamics.

Type-safe configuration with validation for the simplified double
inverted pendulum model. Ensures physical consistency and provides
mathematical constraints based on mechanical engineering principles.



## Architecture Diagram

```{mermaid}
graph TD
    A[SimplifiedDIPConfig] --> B[Validate Masses]
    A --> C[Validate Lengths]
    A --> D[Validate Gravity]
    A --> E[Validate Damping]
    B --> F{All Valid?}
    C --> F
    D --> F
    E --> F
    F -->|Yes| G[Create Config Object]
    F -->|No| H[Raise ValidationError]

    style F fill:#ff9
    style G fill:#9f9
    style H fill:#f99
```



## Enhanced Mathematical Foundation

### Configuration Parameter Space

The simplified DIP model configuration defines the **parameter space** $\Theta$:

$$
\Theta = \{\theta = (m_0, m_1, m_2, l_1, l_2, g, d_0, d_1, d_2) : \theta \in \mathcal{C}\}
$$

where $\mathcal{C}$ is the set of **physically realizable configurations**:

$$
\mathcal{C} = \{\theta : m_i > 0, l_i > 0, g > 0, d_i \geq 0\}
$$

**Parameter Definitions:**

- $m_0$: Cart mass (kg)
- $m_1, m_2$: Link masses (kg)
- $l_1, l_2$: Link lengths (m)
- $g$: Gravitational acceleration (m/s²)
- $d_0, d_1, d_2$: Damping coefficients (N·s/m or N·m·s/rad)

### Validation Constraints

**Physical Feasibility:**

$$
\begin{aligned}
0.1 &\leq m_0 \leq 10.0 \quad \text{(kg)} \\
0.05 &\leq m_1, m_2 \leq 2.0 \quad \text{(kg)} \\
0.1 &\leq l_1, l_2 \leq 1.0 \quad \text{(m)} \\
9.0 &\leq g \leq 10.0 \quad \text{(m/s²)} \\
0.0 &\leq d_i \leq 1.0 \quad \text{(damping)}
\end{aligned}
$$

**Stability Criteria:**

For the inverted equilibrium to be stabilizable:

$$
\frac{m_1 l_1^2 + m_2 (l_1^2 + l_2^2)}{m_0} > \frac{g}{\omega_n^2}
$$

where $\omega_n$ is the desired natural frequency.

### Default Configuration

**Standard Laboratory DIP:**

```python
# example-metadata:
# runnable: false

default_config = SimplifiedDIPConfig(
    m0=1.0,   # 1 kg cart
    m1=0.2,   # 200g link 1
    m2=0.1,   # 100g link 2
    l1=0.3,   # 30cm link 1
    l2=0.2,   # 20cm link 2
    g=9.81,   # Earth gravity
    d0=0.1,   # Light cart damping
    d1=0.01,  # Light joint damping
    d2=0.01
)
```

## References

1. **Block et al.** (2007). "The reaction wheel pendulum." *Synthesis Lectures on Control*. Morgan & Claypool.



## Usage Examples

### Example 1: Basic Usage

Initialize and use the Models Simplified Config module:

```python
from src.plant.models.simplified.config import *
import numpy as np

# Basic initialization
# Load and validate configuration
from src.plant.models.simplified.config import SimplifiedDIPConfig

config = SimplifiedDIPConfig(
    m0=1.5,  # Cart mass (kg)
    m1=0.3,  # Link 1 mass (kg)
    m2=0.2,  # Link 2 mass (kg)
    l1=0.35,  # Link 1 length (m)
    l2=0.25,  # Link 2 length (m)
    g=9.81   # Gravity (m/s²)
)

# Validate physics constraints
if config.is_valid():
    print("Configuration is physically valid")
```

## Example 2: Advanced Configuration

Configure with custom parameters:

```python
# example-metadata:
# runnable: false

# Advanced configuration
# ... custom parameters ...
```

## Example 3: Error Handling

Robust error handling and recovery:

```python
from src.plant.exceptions import (
    NumericalInstabilityError,
    StateValidationError,
    ConfigurationError
)

try:
    # Risky operation
    state_dot = dynamics.step(state, control, t)

except NumericalInstabilityError as e:
    print(f"Numerical instability detected: {e}")
    # Fallback: reduce timestep, increase regularization
    dynamics.reset_numerical_params(stronger_regularization=True)

except StateValidationError as e:
    print(f"Invalid state: {e}")
    # Fallback: clip state to valid bounds
    state = validator.clip_to_valid(state)

except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Fallback: use default configuration
    config = get_default_config()
```

### Example 4: Performance Optimization

Optimize for computational efficiency:

```python
# example-metadata:
# runnable: false

# Performance optimization
import cProfile
import pstats

# Profile critical code path
profiler = cProfile.Profile()
profiler.enable()

# ... run intensive operations ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 time consumers
```

## Example 5: Integration with Controllers

Integrate with control systems:

```python
from src.controllers import ClassicalSMC
from src.core.simulation_runner import SimulationRunner

# Create dynamics model
dynamics = SimplifiedDIPDynamics(config)

# Create controller
controller = ClassicalSMC(
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
    max_force=100.0,
    boundary_layer=0.01
)

# Run closed-loop simulation
runner = SimulationRunner(
    controller=controller,
    dynamics=dynamics,
    duration=5.0,
    dt=0.01
)

result = runner.run(
    initial_state=np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])
)

print(f"Final state: {result.states[-1]}")
print(f"Settling time: {result.settling_time:.2f}s")
print(f"Control effort: {result.control_effort:.2f}")
```


## Complete Source Code

```{literalinclude} ../../../src/plant/models/simplified/config.py
:language: python
:linenos:
```



## Classes

### `SimplifiedDIPConfig`

Type-safe configuration for simplified DIP dynamics.

Physical Parameters:
- All masses must be positive (physical requirement)
- All lengths must be positive (geometric requirement)
- Friction coefficients must be non-negative (energy dissipation)
- Inertias must be positive (rotational mass distribution)

Numerical Parameters:
- Regularization ensures matrix invertibility
- Condition number bounds prevent numerical instability

#### Source Code

```{literalinclude} ../../../src/plant/models/simplified/config.py
:language: python
:pyobject: SimplifiedDIPConfig
:linenos:
```

#### Methods (13)

##### `__post_init__(self)`

Validate configuration after creation.

[View full source →](#method-simplifieddipconfig-__post_init__)

##### `_validate_physical_parameters(self)`

Validate physical parameters for consistency.

[View full source →](#method-simplifieddipconfig-_validate_physical_parameters)

##### `_validate_numerical_parameters(self)`

Validate numerical parameters for stability.

[View full source →](#method-simplifieddipconfig-_validate_numerical_parameters)

##### `_validate_geometric_constraints(self)`

Validate geometric constraints between parameters.

[View full source →](#method-simplifieddipconfig-_validate_geometric_constraints)

##### `create_default(cls)`

Create configuration with sensible default parameters.

[View full source →](#method-simplifieddipconfig-create_default)

##### `create_benchmark(cls)`

Create configuration for benchmark/comparison studies.

[View full source →](#method-simplifieddipconfig-create_benchmark)

##### `create_lightweight(cls)`

Create configuration optimized for computational speed.

[View full source →](#method-simplifieddipconfig-create_lightweight)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-simplifieddipconfig-to_dict)

##### `from_dict(cls, config_dict)`

Create configuration from dictionary.

[View full source →](#method-simplifieddipconfig-from_dict)

##### `get_total_mass(self)`

Get total system mass.

[View full source →](#method-simplifieddipconfig-get_total_mass)

##### `get_characteristic_length(self)`

Get characteristic length scale of the system.

[View full source →](#method-simplifieddipconfig-get_characteristic_length)

##### `get_characteristic_time(self)`

Get characteristic time scale for oscillations.

[View full source →](#method-simplifieddipconfig-get_characteristic_time)

##### `estimate_natural_frequency(self)`

Estimate natural frequency for small oscillations.

[View full source →](#method-simplifieddipconfig-estimate_natural_frequency)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Optional, Dict, Any`
- `from dataclasses import dataclass, field`
- `import numpy as np`
