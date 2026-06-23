# optimization.objectives.control.energy

**Source:** `src\optimization\objectives\control\energy.py`

## Module Overview

Energy consumption objective functions for control optimization.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/control/energy.py
:language: python
:linenos:
```



## Classes

### `EnergyConsumptionObjective`

**Inherits from:** `SimulationBasedObjective`

Objective function for minimizing control energy consumption.

This objective computes various energy consumption metrics to optimize
control efficiency while maintaining performance requirements.

Energy metrics include:
- Total energy: ∫ u²(t) dt
- RMS control effort: √(∫ u²(t) dt / T)
- Peak control effort: max|u(t)|
- Weighted energy with control rate penalty

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/control/energy.py
:language: python
:pyobject: EnergyConsumptionObjective
:linenos:
```

#### Methods (4)

##### `__init__(self, simulation_config, controller_factory, energy_metric, control_rate_weight, control_penalty_weight, max_control_threshold, reference_trajectory)`

Initialize energy consumption objective.

[View full source →](#method-energyconsumptionobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute energy consumption objective from simulation results.

[View full source →](#method-energyconsumptionobjective-_compute_objective_from_simulation)

##### `get_energy_breakdown(self, times, controls)`

Get detailed breakdown of energy components.

[View full source →](#method-energyconsumptionobjective-get_energy_breakdown)

##### `evaluate_energy_efficiency(self, times, states, controls, tracking_error)`

Evaluate energy efficiency considering performance trade-offs.

[View full source →](#method-energyconsumptionobjective-evaluate_energy_efficiency)



### `ControlEffortObjective`

**Inherits from:** `EnergyConsumptionObjective`

Specialized objective for minimizing control effort with saturation handling.

This is a specialized version of EnergyConsumptionObjective that includes
specific handling for control saturation and actuator limitations.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/control/energy.py
:language: python
:pyobject: ControlEffortObjective
:linenos:
```

#### Methods (2)

##### `__init__(self, simulation_config, controller_factory, max_control_force, saturation_penalty, smoothness_weight)`

Initialize control effort objective.

[View full source →](#method-controleffortobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute control effort objective with saturation penalties.

[View full source →](#method-controleffortobjective-_compute_objective_from_simulation)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, Optional, Union, Callable`
- `import numpy as np`
- `from ..base import SimulationBasedObjective`
- `from src.utils.numerical_stability import EPSILON_DIV`
