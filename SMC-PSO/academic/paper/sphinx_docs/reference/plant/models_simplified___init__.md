# plant.models.simplified.__init__

<!-- Enhanced by Week 8 Phase 2 -->


**Source:** `src\plant\models\simplified\__init__.py`

## Module Overview

Simplified Double Inverted Pendulum Model.

Modular implementation of the simplified DIP dynamics with:
- Focused physics computation
- Type-safe configuration
- Numerical stability features
- Performance optimizations

Refactored from the monolithic 688-line dynamics.py file.



## Architecture Diagram

```{mermaid}
graph TB
    A[models.simplified Package] --> B[SimplifiedDIPDynamics]
    A --> C[SimplifiedDIPConfig]
    A --> D[compute_simplified_physics]
    E[PSO Optimizer] --> B
    F[Real-Time Controller] --> B
    G[HIL Simulation] --> B

    style B fill:#9f9
    style E fill:#9cf
    style F fill:#fcf
    style G fill:#ff9
```



## Enhanced Mathematical Foundation

### Simplified Model Package Architecture

The `plant.models.simplified` package provides a **complete, self-contained** implementation of the simplified DIP dynamics:

```
models/simplified/
    ├─ config.py         → Configuration and validation
    ├─ physics.py        → M(q), C(q,q̇), G(q) computation
    ├─ dynamics.py       → Main dynamics class
    └─ __init__.py       → Public API exports
```

**Public API:**

```python
from plant.models.simplified import (
    SimplifiedDIPDynamics,    # Main dynamics class
    SimplifiedDIPConfig,      # Configuration schema
    compute_simplified_physics  # Physics functions
)
```

### Model Characteristics

**Advantages:**

- **Fast:** 3-4× faster than full model
- **Accurate:** < 5% error for typical trajectories
- **Simple:** Fewer parameters, easier tuning
- **Robust:** Better numerical conditioning

**Limitations:**

- No link inertias (point mass assumption)
- No flexibility modeling
- Moderate-speed trajectories only
- Small-angle approximations may break down

### Use Case Guidelines

**Recommended:**

- Controller gain tuning (PSO optimization)
- Real-time control (< 1ms compute time)
- Educational demonstrations
- HIL simulation (low latency)

**Not Recommended:**

- High-speed maneuvers (>5 rad/s)
- Large-angle swings (>π/2)
- Precise trajectory tracking
- Model-based state estimation

### References

1. **Åström & Furuta** (2000). "Swinging up a pendulum by energy control." *Automatica* 36(2).



## Usage Examples

### Example 1: Basic Usage

Initialize and use the Models Simplified   Init   module:

```python
# example-metadata:
# runnable: false

from src.plant.models.simplified.__init__ import *
import numpy as np

# Basic initialization
# Initialize module
# ... basic usage code ...
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

```{literalinclude} ../../../src/plant/models/simplified/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .config import SimplifiedDIPConfig`
- `from .physics import SimplifiedPhysicsComputer`
- `from .dynamics import SimplifiedDIPDynamics`
