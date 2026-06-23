# plant.models.lowrank.physics

**Source:** `src\plant\models\lowrank\physics.py`

## Module Overview

Low-rank DIP Physics Computer.

Simplified physics computation optimized for speed and efficiency.
Uses approximations and reduced-order models to maintain essential
dynamics while minimizing computational overhead.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/lowrank/physics.py
:language: python
:linenos:
```



## Classes

### `LowRankPhysicsComputer`

Low-rank Physics Computer for Double Inverted Pendulum.

Implements simplified physics calculations optimized for:
- Fast computation
- Essential dynamics preservation
- Educational clarity
- Prototyping efficiency

#### Source Code

```{literalinclude} ../../../src/plant/models/lowrank/physics.py
:language: python
:pyobject: LowRankPhysicsComputer
:linenos:
```

#### Methods (13)

##### `__init__(self, config)`

Initialize low-rank physics computer.

[View full source →](#method-lowrankphysicscomputer-__init__)

##### `_precompute_constants(self)`

Precompute frequently used constants for efficiency.

[View full source →](#method-lowrankphysicscomputer-_precompute_constants)

##### `compute_simplified_dynamics_rhs(self, state, control_input, time)`

Compute simplified dynamics right-hand side.

[View full source →](#method-lowrankphysicscomputer-compute_simplified_dynamics_rhs)

##### `_compute_linearized_dynamics(self, state, F)`

Compute linearized dynamics (fastest).

[View full source →](#method-lowrankphysicscomputer-_compute_linearized_dynamics)

##### `_compute_small_angle_dynamics(self, state, F)`

Compute dynamics with small angle approximation.

[View full source →](#method-lowrankphysicscomputer-_compute_small_angle_dynamics)

##### `_compute_simplified_nonlinear_dynamics(self, state, F)`

Compute simplified nonlinear dynamics.

[View full source →](#method-lowrankphysicscomputer-_compute_simplified_nonlinear_dynamics)

##### `_compute_dynamics_with_trig(self, state, F, sin_theta1, cos_theta1, sin_theta2, cos_theta2)`

Compute dynamics with given trigonometric values.

[View full source →](#method-lowrankphysicscomputer-_compute_dynamics_with_trig)

##### `compute_simplified_matrices(self, state)`

Compute simplified physics matrices M, C, G.

[View full source →](#method-lowrankphysicscomputer-compute_simplified_matrices)

##### `_compute_diagonal_matrices(self, state)`

Compute diagonal approximation of physics matrices.

[View full source →](#method-lowrankphysicscomputer-_compute_diagonal_matrices)

##### `_compute_coupled_matrices(self, state)`

Compute coupled physics matrices (more accurate).

[View full source →](#method-lowrankphysicscomputer-_compute_coupled_matrices)

##### `compute_energy(self, state)`

Compute simplified energy analysis.

[View full source →](#method-lowrankphysicscomputer-compute_energy)

##### `compute_stability_metrics(self, state)`

Compute simplified stability metrics.

[View full source →](#method-lowrankphysicscomputer-compute_stability_metrics)

##### `validate_computation(self, state, state_derivative)`

Validate physics computation results.

[View full source →](#method-lowrankphysicscomputer-validate_computation)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Optional, Tuple`
- `import numpy as np`
- `from .config import LowRankDIPConfig`
