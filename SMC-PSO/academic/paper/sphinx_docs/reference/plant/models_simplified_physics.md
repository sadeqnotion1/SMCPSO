# plant.models.simplified.physics

<!-- Enhanced by Week 8 Phase 2 -->


**Source:** `src\plant\models\simplified\physics.py`

## Module Overview

Simplified Physics Computation for DIP.

Focused physics computation module extracted from the monolithic
dynamics implementation. Provides optimized matrix computation
with numerical stability features.



## Architecture Diagram

```{mermaid}
graph TD
    A[q, q̇, params] --> B[Compute Trig Terms]
    B --> C[Build M_q_]
    B --> D[Compute Christoffel]
    D --> E[Build C_q,q̇_]
    B --> F[Compute Potential Grad]
    F --> G[Build G_q_]
    C --> H[Return M, C, G]
    E --> H
    G --> H

    style C fill:#9cf
    style E fill:#fcf
    style G fill:#ff9
```



## Enhanced Mathematical Foundation

### Kinetic Energy Derivation

**Link 1 Kinetic Energy:**

Position of link 1 center of mass:

$$
\begin{aligned}
x_1 &= x + \frac{l_1}{2}\sin\theta_1 \\
y_1 &= \frac{l_1}{2}\cos\theta_1
\end{aligned}
$$

Velocities:

$$
\begin{aligned}
\dot{x}_1 &= \dot{x} + \frac{l_1}{2}\dot{\theta}_1 \cos\theta_1 \\
\dot{y}_1 &= -\frac{l_1}{2}\dot{\theta}_1 \sin\theta_1
\end{aligned}
$$

Kinetic energy:

$$
T_1 = \frac{1}{2}m_1(\dot{x}_1^2 + \dot{y}_1^2) = \frac{1}{2}m_1\left[\dot{x}^2 + l_1 \dot{x}\dot{\theta}_1\cos\theta_1 + \left(\frac{l_1}{2}\right)^2 \dot{\theta}_1^2\right]
$$

**Link 2 Kinetic Energy:**

Similar derivation yields:

$$
T_2 = \frac{1}{2}m_2\left[\dot{x}^2 + 2\dot{x}(l_1\dot{\theta}_1\cos\theta_1 + \frac{l_2}{2}\dot{\theta}_2\cos\theta_2) + \ldots\right]
$$

**Total Kinetic Energy:**

$$
T = \frac{1}{2}m_0\dot{x}^2 + T_1 + T_2
$$

### Potential Energy Derivation

$$
V = m_1 g y_1 + m_2 g y_2 = m_1 g \frac{l_1}{2}\cos\theta_1 + m_2 g \left(l_1\cos\theta_1 + \frac{l_2}{2}\cos\theta_2\right)
$$

### Coriolis Terms Derivation

Using Christoffel symbols:

$$
C_{ij} = \sum_{k=1}^{3} c_{ijk} \dot{q}_k, \quad c_{ijk} = \frac{1}{2}\left(\frac{\partial M_{ij}}{\partial q_k} + \frac{\partial M_{ik}}{\partial q_j} - \frac{\partial M_{jk}}{\partial q_i}\right)
$$

**Example (C₁₂ term):**

$$
C_{12} = -\frac{1}{2}\frac{\partial M_{11}}{\partial \theta_1}\dot{\theta}_1 + \frac{1}{2}\frac{\partial M_{22}}{\partial x}\dot{x} + \ldots
$$

### References

1. **Goldstein** (2002). *Classical Mechanics* (3rd ed.). Addison Wesley. Chapter 1.



## Usage Examples

### Example 1: Basic Usage

Initialize and use the Models Simplified Physics module:

```python
# example-metadata:
# runnable: false

from src.plant.models.simplified.physics import *
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

```{literalinclude} ../../../src/plant/models/simplified/physics.py
:language: python
:linenos:
```



## Classes

### `SimplifiedPhysicsComputer`

Simplified physics computation for DIP dynamics.

Optimized for computational efficiency while maintaining essential
dynamics characteristics. Uses adaptive regularization for numerical
stability and supports both full and simplified matrix computation.

#### Source Code

```{literalinclude} ../../../src/plant/models/simplified/physics.py
:language: python
:pyobject: SimplifiedPhysicsComputer
:linenos:
```

#### Methods (16)

##### `__init__(self, config)`

Initialize simplified physics computer.

[View full source →](#method-simplifiedphysicscomputer-__init__)

##### `compute_dynamics_rhs(self, state, control_input)`

Compute right-hand side of dynamics equation.

[View full source →](#method-simplifiedphysicscomputer-compute_dynamics_rhs)

##### `get_physics_matrices(self, state)`

Get physics matrices M, C, G for current state.

[View full source →](#method-simplifiedphysicscomputer-get_physics_matrices)

##### `compute_inertia_matrix(self, state)`

Compute inertia matrix M(q).

[View full source →](#method-simplifiedphysicscomputer-compute_inertia_matrix)

##### `compute_coriolis_matrix(self, state)`

Compute Coriolis matrix C(q, q̇).

[View full source →](#method-simplifiedphysicscomputer-compute_coriolis_matrix)

##### `compute_gravity_vector(self, state)`

Compute gravity vector G(q).

[View full source →](#method-simplifiedphysicscomputer-compute_gravity_vector)

##### `compute_total_energy(self, state)`

Compute total energy of the system.

[View full source →](#method-simplifiedphysicscomputer-compute_total_energy)

##### `compute_kinetic_energy(self, state)`

Compute kinetic energy T = (1/2) q̇ᵀ M q̇.

[View full source →](#method-simplifiedphysicscomputer-compute_kinetic_energy)

##### `compute_potential_energy(self, state)`

Compute potential energy V.

[View full source →](#method-simplifiedphysicscomputer-compute_potential_energy)

##### `_compute_kinetic_energy(self, state)`

Internal kinetic energy computation.

[View full source →](#method-simplifiedphysicscomputer-_compute_kinetic_energy)

##### `_compute_potential_energy(self, state)`

Internal potential energy computation.

[View full source →](#method-simplifiedphysicscomputer-_compute_potential_energy)

##### `enable_matrix_caching(self, enable)`

Enable/disable matrix caching for repeated calculations.

[View full source →](#method-simplifiedphysicscomputer-enable_matrix_caching)

##### `clear_matrix_cache(self)`

Clear matrix cache.

[View full source →](#method-simplifiedphysicscomputer-clear_matrix_cache)

##### `set_simplified_inertia(self, use_simplified)`

Enable/disable simplified inertia matrix computation.

[View full source →](#method-simplifiedphysicscomputer-set_simplified_inertia)

##### `get_matrix_conditioning(self, state)`

Get condition number of inertia matrix.

[View full source →](#method-simplifiedphysicscomputer-get_matrix_conditioning)

##### `check_numerical_stability(self, state)`

Check if current state leads to numerically stable computation.

[View full source →](#method-simplifiedphysicscomputer-check_numerical_stability)



## Functions

### `compute_simplified_dynamics_numba(state, control_force, m0, m1, m2, L1, L2, Lc1, Lc2, I1, I2, g, c0, c1, c2, reg_alpha, min_reg)`

**Decorators:** `@njit`

JIT-compiled simplified dynamics computation.

Ultra-fast dynamics computation for performance-critical applications.
Uses simplified physics with minimal overhead.

Args:
    state: System state vector
    control_force: Applied control force
    m0, m1, m2: Masses
    L1, L2, Lc1, Lc2: Lengths and COM distances
    I1, I2: Inertias
    g: Gravity
    c0, c1, c2: Friction coefficients
    reg_alpha, min_reg: Regularization parameters

Returns:
    State derivative vector

#### Source Code

```{literalinclude} ../../../src/plant/models/simplified/physics.py
:language: python
:pyobject: compute_simplified_dynamics_numba
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Tuple, Any`
- `import numpy as np`
- `from ...core import DIPPhysicsMatrices, SimplifiedDIPPhysicsMatrices, AdaptiveRegularizer, MatrixInverter, NumericalInstabilityError`
- `from .config import SimplifiedDIPConfig`
