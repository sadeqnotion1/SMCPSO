# optimization.objectives.system.settling_time

**Source:** `src\optimization\objectives\system\settling_time.py`

## Module Overview

Settling time objective functions for control optimization.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/system/settling_time.py
:language: python
:linenos:
```



## Classes

### `SettlingTimeObjective`

**Inherits from:** `SimulationBasedObjective`

Objective function for minimizing system settling time.

This objective computes settling time based on various criteria:
- 2% settling time (default)
- 5% settling time
- Custom settling tolerance
- Weighted settling time for multiple outputs

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/system/settling_time.py
:language: python
:pyobject: SettlingTimeObjective
:linenos:
```

#### Methods (8)

##### `__init__(self, simulation_config, controller_factory, settling_tolerance, settling_metric, output_weights, output_indices, min_settled_duration, reference_trajectory)`

Initialize settling time objective.

[View full source →](#method-settlingtimeobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute settling time objective from simulation results.

[View full source →](#method-settlingtimeobjective-_compute_objective_from_simulation)

##### `_compute_single_output_settling_time(self, times, output)`

Compute settling time for a single output signal.

[View full source →](#method-settlingtimeobjective-_compute_single_output_settling_time)

##### `_compute_tolerance_band(self, output, reference_values)`

Compute settling tolerance band for the output signal.

[View full source →](#method-settlingtimeobjective-_compute_tolerance_band)

##### `_find_settling_time(self, times, output, reference_values, tolerance_bands)`

Find the settling time based on tolerance criteria.

[View full source →](#method-settlingtimeobjective-_find_settling_time)

##### `compute_detailed_settling_analysis(self, times, states, controls)`

Compute detailed settling time analysis for all outputs.

[View full source →](#method-settlingtimeobjective-compute_detailed_settling_analysis)

##### `_count_zero_crossings(self, signal)`

Count zero crossings in a signal (indicator of oscillations).

[View full source →](#method-settlingtimeobjective-_count_zero_crossings)

##### `get_settling_criteria(self)`

Get the settling criteria used by this objective.

[View full source →](#method-settlingtimeobjective-get_settling_criteria)



### `RiseTimeObjective`

**Inherits from:** `SettlingTimeObjective`

Objective function for minimizing rise time (10%-90% rise time).

Rise time is the time required for the system response to rise from
10% to 90% of its final steady-state value.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/system/settling_time.py
:language: python
:pyobject: RiseTimeObjective
:linenos:
```

#### Methods (2)

##### `__init__(self)`

Initialize rise time objective.

[View full source →](#method-risetimeobjective-__init__)

##### `_compute_single_output_settling_time(self, times, output)`

Compute rise time (10%-90%) instead of settling time.

[View full source →](#method-risetimeobjective-_compute_single_output_settling_time)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, Optional, Union, Callable, Tuple`
- `import numpy as np`
- `from ..base import SimulationBasedObjective`
