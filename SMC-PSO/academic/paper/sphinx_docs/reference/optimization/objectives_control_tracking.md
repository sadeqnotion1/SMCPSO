# optimization.objectives.control.tracking

**Source:** `src\optimization\objectives\control\tracking.py`

## Module Overview

Tracking performance objective functions for control optimization.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/control/tracking.py
:language: python
:linenos:
```



## Classes

### `TrackingErrorObjective`

**Inherits from:** `SimulationBasedObjective`

Objective function for minimizing tracking error.

This objective computes various tracking error metrics including
ISE (Integral Square Error), IAE (Integral Absolute Error),
and ITAE (Integral Time Absolute Error).

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/control/tracking.py
:language: python
:pyobject: TrackingErrorObjective
:linenos:
```

#### Methods (3)

##### `__init__(self, simulation_config, controller_factory, reference_trajectory, error_metric, state_weights, output_indices)`

Initialize tracking error objective.

[View full source →](#method-trackingerrorobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute tracking error from simulation results.

[View full source →](#method-trackingerrorobjective-_compute_objective_from_simulation)

##### `_compute_error_metric(self, error, times, dt)`

Compute specific error metric.

[View full source →](#method-trackingerrorobjective-_compute_error_metric)



### `StepResponseObjective`

**Inherits from:** `SimulationBasedObjective`

Objective for step response characteristics.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/control/tracking.py
:language: python
:pyobject: StepResponseObjective
:linenos:
```

#### Methods (5)

##### `__init__(self, simulation_config, controller_factory, step_amplitude, output_index, target_settling_time, target_overshoot)`

Initialize step response objective.

[View full source →](#method-stepresponseobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute step response objective.

[View full source →](#method-stepresponseobjective-_compute_objective_from_simulation)

##### `_compute_settling_time(self, times, output, tolerance)`

Compute settling time (2% criterion).

[View full source →](#method-stepresponseobjective-_compute_settling_time)

##### `_compute_overshoot(self, output)`

Compute maximum overshoot percentage.

[View full source →](#method-stepresponseobjective-_compute_overshoot)

##### `_compute_steady_state_error(self, output)`

Compute steady-state error.

[View full source →](#method-stepresponseobjective-_compute_steady_state_error)



### `FrequencyResponseObjective`

**Inherits from:** `SimulationBasedObjective`

Objective based on frequency response characteristics.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/control/tracking.py
:language: python
:pyobject: FrequencyResponseObjective
:linenos:
```

#### Methods (3)

##### `__init__(self, simulation_config, controller_factory, frequency_range, desired_bandwidth, desired_phase_margin, desired_gain_margin)`

Initialize frequency response objective.

[View full source →](#method-frequencyresponseobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute frequency response objective.

[View full source →](#method-frequencyresponseobjective-_compute_objective_from_simulation)

##### `_estimate_bandwidth_from_time_domain(self, states, dt)`

Estimate bandwidth from time-domain response.

[View full source →](#method-frequencyresponseobjective-_estimate_bandwidth_from_time_domain)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, Optional, Union, Callable`
- `import numpy as np`
- `from ..base import SimulationBasedObjective`
