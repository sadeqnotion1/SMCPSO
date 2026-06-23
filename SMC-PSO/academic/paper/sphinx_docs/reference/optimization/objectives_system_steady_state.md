# optimization.objectives.system.steady_state

**Source:** `src\optimization\objectives\system\steady_state.py`

## Module Overview Steady-state

error objective functions for control optimization

.

## Complete Source Code ```

{literalinclude}

../../../src/optimization/objectives/system/steady_state.py


:language: python
:linenos:
```

---

## Classes

### `SteadyStateErrorObjective`

**Inherits from:** `SimulationBasedObjective` Objective function for minimizing steady-state tracking error. This objective computes various steady-state error metrics:
- Absolute steady-state error
- Percentage steady-state error
- RMS steady-state error
- Weighted error for multiple outputs #### Source Code ```{literalinclude} ../../../src/optimization/objectives/system/steady_state.py
:language: python
:pyobject: SteadyStateErrorObjective
:linenos:
``` #### Methods (7) ##### `__init__(self, simulation_config, controller_factory, error_metric, steady_state_window, output_weights, output_indices, reference_trajectory)` Initialize steady-state error objective. [View full source →](#method-steadystateerrorobjective-__init__) ##### `_compute_objective_from_simulation(self, times, states, controls)` Compute steady-state error objective from simulation results. [View full source →](#method-steadystateerrorobjective-_compute_objective_from_simulation) ##### `_compute_single_output_steady_state_error(self, times, output, reference)` Compute steady-state error for a single output. [View full source →](#method-steadystateerrorobjective-_compute_single_output_steady_state_error) ##### `_get_reference_values(self, times, n_states)` Get reference trajectory for all states. [View full source →](#method-steadystateerrorobjective-_get_reference_values) ##### `compute_detailed_steady_state_analysis(self, times, states, controls)` Compute detailed steady-state analysis for all outputs. [View full source →](#method-steadystateerrorobjective-compute_detailed_steady_state_analysis) ##### `get_steady_state_convergence(self, times, output, reference, tolerance)` Analyze steady-state convergence characteristics. [View full source →](#method-steadystateerrorobjective-get_steady_state_convergence) ##### `get_error_statistics(self, times, states, reference_values)` Get error statistics. [View full source →](#method-steadystateerrorobjective-get_error_statistics)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Any, Dict, Optional, Union, Callable, Tuple`
- `import numpy as np`
- `from ..base import SimulationBasedObjective`
