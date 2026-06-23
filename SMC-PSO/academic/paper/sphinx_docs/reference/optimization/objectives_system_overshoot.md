# optimization.objectives.system.overshoot

**Source:** `src\optimization\objectives\system\overshoot.py`

## Module Overview

Overshoot objective functions for control optimization.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/system/overshoot.py
:language: python
:linenos:
```



## Classes

### `OvershootObjective`

**Inherits from:** `SimulationBasedObjective`

Objective function for minimizing system overshoot.

This objective computes various overshoot metrics:
- Peak overshoot percentage
- Absolute overshoot
- Weighted overshoot for multiple outputs
- Undershoot penalty

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/system/overshoot.py
:language: python
:pyobject: OvershootObjective
:linenos:
```

#### Methods (7)

##### `__init__(self, simulation_config, controller_factory, overshoot_metric, output_weights, output_indices, undershoot_penalty, reference_trajectory)`

Initialize overshoot objective.

[View full source →](#method-overshootobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute overshoot objective from simulation results.

[View full source →](#method-overshootobjective-_compute_objective_from_simulation)

##### `_compute_single_output_overshoot(self, times, output)`

Compute overshoot for a single output signal.

[View full source →](#method-overshootobjective-_compute_single_output_overshoot)

##### `_determine_step_characteristics(self, output)`

Determine initial and final values for step response analysis.

[View full source →](#method-overshootobjective-_determine_step_characteristics)

##### `compute_detailed_overshoot_analysis(self, times, states, controls)`

Compute detailed overshoot analysis for all outputs.

[View full source →](#method-overshootobjective-compute_detailed_overshoot_analysis)

##### `_count_oscillations_before_settling(self, times, output, initial_value, final_value)`

Count number of oscillations around final value before settling.

[View full source →](#method-overshootobjective-_count_oscillations_before_settling)

##### `get_overshoot_characteristics(self, times, output)`

Get overshoot characteristics for a single output.

[View full source →](#method-overshootobjective-get_overshoot_characteristics)



### `UndershootObjective`

**Inherits from:** `OvershootObjective`

Objective function specifically for minimizing undershoot.

This is a specialized version that focuses on undershoot rather than overshoot.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/system/overshoot.py
:language: python
:pyobject: UndershootObjective
:linenos:
```

#### Methods (2)

##### `__init__(self)`

Initialize undershoot objective.

[View full source →](#method-undershootobjective-__init__)

##### `_compute_single_output_overshoot(self, times, output)`

Compute undershoot instead of overshoot.

[View full source →](#method-undershootobjective-_compute_single_output_overshoot)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, Optional, Union, Callable, Tuple`
- `import numpy as np`
- `from ..base import SimulationBasedObjective`
- `from src.utils.numerical_stability import EPSILON_DIV`
