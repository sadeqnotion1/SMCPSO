# plant.core.__init__

<!-- Enhanced by Week 8 Phase 2 -->


**Source:** `src\plant\core\__init__.py`

## Module Overview

Core Plant Components - Shared utilities for plant dynamics.

Provides fundamental building blocks for plant dynamics computation:
- Physics matrix computation (M, C, G matrices)
- Numerical stability and regularization
- State validation and sanitization
- Integration utilities

These components are designed for reuse across different plant models
while maintaining mathematical correctness and numerical robustness.



## Architecture Diagram

```{mermaid}
graph TB
    A[plant.core Package] --> B[physics_matrices]
    A --> C[numerical_stability]
    A --> D[state_validation]
    A --> E[dynamics_compatibility_]
    B --> F[compute_mass_matrix]
    B --> G[compute_coriolis_matrix]
    B --> H[compute_gravity_vector]
    C --> I[robust_inverse]
    C --> J[analyze_conditioning]
    D --> K[StateValidator]
    D --> L[validate_state]
    E --> M[Re-export for tests]

    style B fill:#9cf
    style C fill:#fcf
    style D fill:#ff9
```



## Enhanced Mathematical Foundation

### Core Module Architecture

The `plant.core` module provides the **foundational components** for double inverted pendulum dynamics computation. It serves as the abstraction layer between:

1. **Physics Models** (Lagrangian mechanics, matrix computation)
2. **Numerical Methods** (integration, linear algebra)
3. **Controllers** (SMC, MPC, adaptive control)

**Separation of Concerns:**

$$
\text{Dynamics} = \underbrace{\text{Physics}}_\text{core.physics\_matrices} \circ \underbrace{\text{Numerical}}_\text{core.numerical\_stability} \circ \underbrace{\text{Validation}}_\text{core.state\_validation}
$$

### Module Responsibilities

**Physics Computation (`physics_matrices`):**
- Mass matrix $M(q)$ computation
- Coriolis matrix $C(q, \dot{q})$ computation
- Gravity vector $G(q)$ computation
- Christoffel symbol calculation

**Numerical Stability (`numerical_stability`):**
- Matrix conditioning analysis ($\kappa(M)$)
- Tikhonov regularization ($\lambda$ selection)
- SVD pseudo-inverse fallback
- Error bound monitoring

**State Validation (`state_validation`):**
- Physical constraint checking
- Energy conservation monitoring
- NaN/Inf detection
- Runtime verification

**Dynamics Interface (`dynamics`):**
- Backward compatibility layer
- Unified API for test modules
- Re-exports from implementation modules

### Design Principles

**1. Modularity:**

Each component has **single responsibility** and clear interfaces:

```python
# Clean separation
M = compute_mass_matrix(q, params)        # Physics
M_inv = robust_inverse(M)                 # Numerical
is_valid = validate_state(x)              # Validation
```

**2. Composability:**

Components combine to form complete dynamics:

```python
# example-metadata:
# runnable: false

def dynamics_step(x, u, params):
    q, q_dot = extract_coordinates(x)
    M = compute_mass_matrix(q, params)
    C = compute_coriolis_matrix(q, q_dot, params)
    G = compute_gravity_vector(q, params)
    M_inv = robust_inverse(M)
    q_ddot = M_inv @ (B @ u - C @ q_dot - G)
    x_dot = assemble_state_derivative(q_dot, q_ddot)
    validate_state(x_dot)
    return x_dot
```

**3. Performance:**

Numba JIT compilation for critical paths:

```python
# example-metadata:
# runnable: false

@njit(cache=True, fastmath=True)
def compute_physics_matrices_numba(q, q_dot, params):
    # Hot loop - compiled to machine code
    ...
```

### References

1. **Martin** (2017). *Clean Architecture*. Prentice Hall. Chapter 7 (SRP).
2. **Murray et al.** (1994). *Robotic Manipulation*. CRC Press. Chapter 4.



## Usage Examples

### Example 1: Basic Usage

Initialize and use the Core   Init   module:

```python
# example-metadata:
# runnable: false

from src.plant.core.__init__ import *
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

```{literalinclude} ../../../src/plant/core/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .physics_matrices import PhysicsMatrixComputer, DIPPhysicsMatrices, SimplifiedDIPPhysicsMatrices`
- `from .numerical_stability import NumericalInstabilityError, MatrixRegularizer, AdaptiveRegularizer, MatrixInverter, fast_condition_estimate, NumericalStabilityMonitor`
- `from .state_validation import StateValidationError, StateValidator, DIPStateValidator, MinimalStateValidator`
