# plant.models.full.physics

**Source:** `src\plant\models\full\physics.py`

## Module Overview

Full Fidelity Physics Computation for DIP.

Complete high-fidelity physics computation including all nonlinear effects,
advanced friction models, aerodynamic forces, and coupling terms for the
double inverted pendulum system.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/full/physics.py
:language: python
:linenos:
```



## Classes

### `FullFidelityPhysicsComputer`

Full-fidelity physics computation for DIP dynamics.

Implements complete nonlinear dynamics with:
- All coupling terms and nonlinear effects
- Advanced friction modeling (viscous + Coulomb)
- Aerodynamic forces and drag
- Gyroscopic and Coriolis effects
- High-precision matrix computation

#### Source Code

```{literalinclude} ../../../src/plant/models/full/physics.py
:language: python
:pyobject: FullFidelityPhysicsComputer
:linenos:
```

#### Methods (13)

##### `__init__(self, config)`

Initialize full-fidelity physics computer.

[View full source →](#method-fullfidelityphysicscomputer-__init__)

##### `compute_complete_dynamics_rhs(self, state, control_input, time, wind_velocity)`

Compute complete right-hand side of dynamics equation.

[View full source →](#method-fullfidelityphysicscomputer-compute_complete_dynamics_rhs)

##### `_compute_full_inertia_matrix(self, state)`

Compute full inertia matrix with all coupling terms.

[View full source →](#method-fullfidelityphysicscomputer-_compute_full_inertia_matrix)

##### `_compute_full_coriolis_matrix(self, state)`

Compute full Coriolis matrix with all nonlinear terms.

[View full source →](#method-fullfidelityphysicscomputer-_compute_full_coriolis_matrix)

##### `_compute_full_gravity_vector(self, state)`

Compute full gravity vector.

[View full source →](#method-fullfidelityphysicscomputer-_compute_full_gravity_vector)

##### `_compute_friction_forces(self, state)`

Compute advanced friction forces.

[View full source →](#method-fullfidelityphysicscomputer-_compute_friction_forces)

##### `_compute_aerodynamic_forces(self, state, wind_velocity)`

Compute aerodynamic drag forces on pendulums.

[View full source →](#method-fullfidelityphysicscomputer-_compute_aerodynamic_forces)

##### `_compute_disturbance_forces(self, state, time)`

Compute external disturbance forces.

[View full source →](#method-fullfidelityphysicscomputer-_compute_disturbance_forces)

##### `_compute_pendulum_tip_velocity(self, pendulum_num, state, length)`

Compute velocity of pendulum tip in world coordinates.

[View full source →](#method-fullfidelityphysicscomputer-_compute_pendulum_tip_velocity)

##### `_solve_with_refinement(self, A, b)`

Solve linear system with iterative refinement for higher accuracy.

[View full source →](#method-fullfidelityphysicscomputer-_solve_with_refinement)

##### `_setup_cached_parameters(self)`

Setup frequently used parameters for efficiency.

[View full source →](#method-fullfidelityphysicscomputer-_setup_cached_parameters)

##### `_compute_full_inertia_matrix_numba(theta1, theta2, m0, m1, m2, L1, L2, Lc1, Lc2, I1, I2)`

JIT-compiled full inertia matrix computation.

[View full source →](#method-fullfidelityphysicscomputer-_compute_full_inertia_matrix_numba)

##### `_compute_full_coriolis_matrix_numba(theta1, theta2, theta1_dot, theta2_dot, m1, m2, L1, L2, Lc1, Lc2, include_coriolis, include_centrifugal, include_gyroscopic)`

JIT-compiled full Coriolis matrix computation.

[View full source →](#method-fullfidelityphysicscomputer-_compute_full_coriolis_matrix_numba)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Tuple, Any, Optional`
- `import numpy as np`
- `from ...core import DIPPhysicsMatrices, AdaptiveRegularizer, MatrixInverter, NumericalInstabilityError`
- `from .config import FullDIPConfig`
