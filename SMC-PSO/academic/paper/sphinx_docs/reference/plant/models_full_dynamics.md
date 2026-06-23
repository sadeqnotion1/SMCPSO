# plant.models.full.dynamics

**Source:** `src\plant\models\full\dynamics.py`

## Module Overview Full

Fidelity DIP Dynamics Model

. Complete high-fidelity implementation of the double inverted pendulum


with all nonlinear effects, advanced numerical integration, and
physics modeling. ## Complete Source Code ```{literalinclude} ../../../src/plant/models/full/dynamics.py
:language: python
:linenos:
```

---

## Classes

### `FullDIPDynamics`

**Inherits from:** `BaseDynamicsModel` Full Fidelity Double Inverted Pendulum Dynamics Model. High-fidelity implementation featuring:
- Complete nonlinear dynamics with all coupling effects
- Advanced friction models (viscous + Coulomb)
- Aerodynamic forces and wind effects
- High-precision adaptive integration
- disturbance modeling
- Research-grade numerical accuracy #### Source Code ```{literalinclude} ../../../src/plant/models/full/dynamics.py
:language: python
:pyobject: FullDIPDynamics
:linenos:
``` #### Methods (25) ##### `__init__(self, config, enable_monitoring, enable_validation)` Initialize full-fidelity DIP dynamics. [View full source →](#method-fulldipdynamics-__init__) ##### `compute_dynamics(self, state, control_input, time)` Compute full-fidelity DIP dynamics. [View full source →](#method-fulldipdynamics-compute_dynamics) ##### `get_physics_matrices(self, state)` Get complete physics matrices M, C, G at current state. [View full source →](#method-fulldipdynamics-get_physics_matrices) ##### `compute_energy_analysis(self, state)` Compute energy analysis. [View full source →](#method-fulldipdynamics-compute_energy_analysis) ##### `compute_stability_metrics(self, state)` Compute stability and conditioning metrics. [View full source →](#method-fulldipdynamics-compute_stability_metrics) ##### `set_wind_model(self, wind_function)` Set custom wind velocity function wind_function(time) -> [vx, vy]. [View full source →](#method-fulldipdynamics-set_wind_model) ##### `get_integration_statistics(self)` Get integration performance statistics. [View full source →](#method-fulldipdynamics-get_integration_statistics) ##### `_setup_validation(self)` Setup enhanced state validation for full DIP. [View full source →](#method-fulldipdynamics-_setup_validation) ##### `_validate_inputs(self, state, control_input)` Enhanced input validation for full model. [View full source →](#method-fulldipdynamics-_validate_inputs) ##### `_check_physical_constraints(self, state)` Check physical constraints specific to full model. [View full source →](#method-fulldipdynamics-_check_physical_constraints) ##### `_compute_diagnostics(self, state, state_derivative, time)` Compute diagnostics for full model. [View full source →](#method-fulldipdynamics-_compute_diagnostics) ##### `_compute_force_breakdown(self, state)` Compute breakdown of all forces acting on the system. [View full source →](#method-fulldipdynamics-_compute_force_breakdown) ##### `_update_wind_model(self, time)` Update wind velocity model. [View full source →](#method-fulldipdynamics-_update_wind_model) ##### `_compute_kinetic_energy(self, state)` Compute total kinetic energy. [View full source →](#method-fulldipdynamics-_compute_kinetic_energy) ##### `_compute_potential_energy(self, state)` Compute total potential energy. [View full source →](#method-fulldipdynamics-_compute_potential_energy) ##### `_compute_cart_kinetic_energy(self, state)` Compute kinetic energy of cart. [View full source →](#method-fulldipdynamics-_compute_cart_kinetic_energy) ##### `_compute_pendulum_kinetic_energy(self, state, pendulum_num)` Compute kinetic energy of specified pendulum. [View full source →](#method-fulldipdynamics-_compute_pendulum_kinetic_energy) ##### `_compute_pendulum_potential_energy(self, state, pendulum_num)` Compute potential energy of specified pendulum. [View full source →](#method-fulldipdynamics-_compute_pendulum_potential_energy) ##### `_validate_control_input(self, control_input)` Validate control input for full model. [View full source →](#method-fulldipdynamics-_validate_control_input) ##### `_validate_state_derivative(self, state_derivative)` Enhanced validation of computed state derivative. [View full source →](#method-fulldipdynamics-_validate_state_derivative) ##### `_record_successful_computation(self, state, diagnostics)` Record successful computation with full diagnostics. [View full source →](#method-fulldipdynamics-_record_successful_computation) ##### `_record_numerical_instability(self, state, error_msg)` Record numerical instability with context. [View full source →](#method-fulldipdynamics-_record_numerical_instability) ##### `_rhs_core(self, state, u)` Compatibility method for legacy code expecting _rhs_core. [View full source →](#method-fulldipdynamics-_rhs_core) ##### `_record_computation_failure(self, state, error_msg)` Record general computation failure. [View full source →](#method-fulldipdynamics-_record_computation_failure) ##### `_rhs_core(self, state, u)` Compatibility method for legacy code expecting _rhs_core. [View full source →](#method-fulldipdynamics-_rhs_core)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Tuple, Optional, Dict, Any, Union`
- `import numpy as np`
- `import warnings`
- `from ..base import BaseDynamicsModel, DynamicsResult`
- `from ...core import DIPStateValidator, NumericalInstabilityError, NumericalStabilityMonitor`
- `from .config import FullDIPConfig`
- `from .physics import FullFidelityPhysicsComputer`
- `from src.utils.config_compatibility import AttributeDictionary, ensure_dict_access`
