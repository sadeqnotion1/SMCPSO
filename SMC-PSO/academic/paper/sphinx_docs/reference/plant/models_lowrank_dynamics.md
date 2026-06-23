# plant.models.lowrank.dynamics

**Source:** `src\plant\models\lowrank\dynamics.py`

## Module Overview

Low-rank DIP Dynamics Model.

Simplified implementation optimized for computational efficiency while
maintaining essential double inverted pendulum dynamics. Ideal for
fast prototyping, educational purposes, and real-time applications.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/lowrank/dynamics.py
:language: python
:linenos:
```



## Classes

### `LowRankDIPDynamics`

**Inherits from:** `BaseDynamicsModel`

Low-rank Double Inverted Pendulum Dynamics Model.

Simplified implementation featuring:
- Fast computation with reduced complexity
- Essential dynamics preservation
- Optional linearization for stability analysis
- Small-angle approximations for efficiency
- Educational clarity with simplified physics

#### Source Code

```{literalinclude} ../../../src/plant/models/lowrank/dynamics.py
:language: python
:pyobject: LowRankDIPDynamics
:linenos:
```

#### Methods (17)

##### `__init__(self, config, enable_monitoring, enable_validation)`

Initialize low-rank DIP dynamics.

[View full source →](#method-lowrankdipdynamics-__init__)

##### `compute_dynamics(self, state, control_input, time)`

Compute low-rank DIP dynamics.

[View full source →](#method-lowrankdipdynamics-compute_dynamics)

##### `get_physics_matrices(self, state)`

Get simplified physics matrices M, C, G at current state.

[View full source →](#method-lowrankdipdynamics-get_physics_matrices)

##### `get_linearized_system(self, equilibrium_point, force_recompute)`

Get linearized system matrices around equilibrium point.

[View full source →](#method-lowrankdipdynamics-get_linearized_system)

##### `compute_linearized_dynamics(self, state, control_input, equilibrium_point)`

Compute dynamics using linearized model.

[View full source →](#method-lowrankdipdynamics-compute_linearized_dynamics)

##### `compute_energy_analysis(self, state)`

Compute simplified energy analysis.

[View full source →](#method-lowrankdipdynamics-compute_energy_analysis)

##### `compute_stability_metrics(self, state)`

Compute simplified stability metrics.

[View full source →](#method-lowrankdipdynamics-compute_stability_metrics)

##### `get_computation_statistics(self)`

Get computation performance statistics.

[View full source →](#method-lowrankdipdynamics-get_computation_statistics)

##### `step(self, state, control_input, dt)`

Simplified single-step integration (for compatibility).

[View full source →](#method-lowrankdipdynamics-step)

##### `_setup_validation(self)`

Setup simplified state validation for low-rank DIP.

[View full source →](#method-lowrankdipdynamics-_setup_validation)

##### `_validate_inputs(self, state, control_input)`

Basic input validation for low-rank model.

[View full source →](#method-lowrankdipdynamics-_validate_inputs)

##### `_validate_control_input(self, control_input)`

Validate control input.

[View full source →](#method-lowrankdipdynamics-_validate_control_input)

##### `_check_state_bounds(self, state)`

Check if state is within configured bounds.

[View full source →](#method-lowrankdipdynamics-_check_state_bounds)

##### `_compute_diagnostics(self, state, state_derivative, time)`

Compute simplified diagnostics.

[View full source →](#method-lowrankdipdynamics-_compute_diagnostics)

##### `_record_successful_computation(self)`

Record successful computation.

[View full source →](#method-lowrankdipdynamics-_record_successful_computation)

##### `_record_failed_computation(self)`

Record failed computation.

[View full source →](#method-lowrankdipdynamics-_record_failed_computation)

##### `_rhs_core(self, state, u)`

Compatibility method for legacy code expecting _rhs_core.

[View full source →](#method-lowrankdipdynamics-_rhs_core)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Tuple, Optional, Dict, Any, Union`
- `import numpy as np`
- `import warnings`
- `from ..base import BaseDynamicsModel, DynamicsResult`
- `from ...core import DIPStateValidator, NumericalInstabilityError, NumericalStabilityMonitor`
- `from .config import LowRankDIPConfig`
- `from .physics import LowRankPhysicsComputer`
