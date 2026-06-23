# optimization.objectives.control.robustness

**Source:** `src\optimization\objectives\control\robustness.py`

## Module Overview Robustness

objective functions for control optimization

.

## Complete Source Code ```

{literalinclude}

../../../src/optimization/objectives/control/robustness.py


:language: python
:linenos:
```

---

## Classes

### `RobustnessObjective`

**Inherits from:** `SimulationBasedObjective` Objective function for optimizing control robustness. This objective evaluates controller performance under various
uncertainties and disturbances including:
- Parameter variations (mass, length, damping)
- Measurement noise
- External disturbances
- Model uncertainties #### Source Code ```{literalinclude} ../../../src/optimization/objectives/control/robustness.py
:language: python
:pyobject: RobustnessObjective
:linenos:
``` #### Methods (13) ##### `__init__(self, simulation_config, controller_factory, robustness_metric, n_variations, parameter_uncertainty, noise_level, disturbance_magnitude, reference_trajectory)` Initialize robustness objective. [View full source →](#method-robustnessobjective-__init__) ##### `_compute_objective_from_simulation(self, times, states, controls)` Compute robustness objective. [View full source →](#method-robustnessobjective-_compute_objective_from_simulation) ##### `_compute_robustness_from_results(self, times, states, controls)` Compute robustness metric from single simulation results. [View full source →](#method-robustnessobjective-_compute_robustness_from_results) ##### `_compute_monte_carlo_robustness(self, controller_params)` Compute Monte Carlo robustness analysis. [View full source →](#method-robustnessobjective-_compute_monte_carlo_robustness) ##### `_compute_worst_case_robustness(self, controller_params)` Compute worst-case robustness analysis. [View full source →](#method-robustnessobjective-_compute_worst_case_robustness) ##### `_compute_sensitivity_robustness(self, controller_params)` Compute sensitivity-based robustness analysis. [View full source →](#method-robustnessobjective-_compute_sensitivity_robustness) ##### `_compute_h_infinity_robustness(self, controller_params, times, states, controls)` Compute H-infinity norm approximation for robustness. [View full source →](#method-robustnessobjective-_compute_h_infinity_robustness) ##### `_compute_composite_robustness(self, controller_params, times, states, controls)` Compute composite robustness metric. [View full source →](#method-robustnessobjective-_compute_composite_robustness) ##### `_generate_parameter_variations(self)` Generate random parameter variations for Monte Carlo analysis. [View full source →](#method-robustnessobjective-_generate_parameter_variations) ##### `_generate_extreme_variations(self)` Generate extreme parameter variations for worst-case analysis. [View full source →](#method-robustnessobjective-_generate_extreme_variations) ##### `_simulate_with_variation(self, controller_params, parameter_variation)` Simulate system with parameter variations and return performance metric. [View full source →](#method-robustnessobjective-_simulate_with_variation) ##### `_estimate_settling_speed(self, times, states)` Estimate settling speed from trajectory. [View full source →](#method-robustnessobjective-_estimate_settling_speed) ##### `get_robustness_analysis(self, controller_params)` Get robustness analysis. [View full source →](#method-robustnessobjective-get_robustness_analysis)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Any, Dict, Optional, Union, Callable, List`
- `import numpy as np`
- `from concurrent.futures import ThreadPoolExecutor`
- `import warnings`
- `from ..base import SimulationBasedObjective`
- `from src.utils.numerical_stability import EPSILON_DIV`
