# optimization.objectives.multi.weighted_sum

**Source:** `src\optimization\objectives\multi\weighted_sum.py`

## Module Overview

Weighted sum multi-objective optimization.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/multi/weighted_sum.py
:language: python
:linenos:
```



## Classes

### `WeightedSumObjective`

**Inherits from:** `SimulationBasedObjective`

Multi-objective optimization using weighted sum scalarization.

This objective combines multiple objectives into a single scalar objective
using weighted sum: f(x) = Σ(wi * fi(x))

The weighted sum approach is simple but has limitations:
- Cannot find non-convex portions of Pareto frontier
- Weight selection can be difficult
- Scale differences between objectives matter

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/multi/weighted_sum.py
:language: python
:pyobject: WeightedSumObjective
:linenos:
```

#### Methods (8)

##### `__init__(self, simulation_config, controller_factory, objectives, weights, normalization, reference_values, reference_trajectory)`

Initialize weighted sum multi-objective.

[View full source →](#method-weightedsumobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute weighted sum objective from simulation results.

[View full source →](#method-weightedsumobjective-_compute_objective_from_simulation)

##### `_normalize_objectives(self, objective_values)`

Normalize objective values based on selected method.

[View full source →](#method-weightedsumobjective-_normalize_objectives)

##### `evaluate_objectives_separately(self, times, states, controls)`

Evaluate all objectives separately and return detailed results.

[View full source →](#method-weightedsumobjective-evaluate_objectives_separately)

##### `update_weights(self, new_weights)`

Update objective weights.

[View full source →](#method-weightedsumobjective-update_weights)

##### `get_objective_info(self)`

Get information about the multi-objective setup.

[View full source →](#method-weightedsumobjective-get_objective_info)

##### `perform_weight_sensitivity_analysis(self, times, states, controls, n_samples)`

Perform sensitivity analysis for different weight combinations.

[View full source →](#method-weightedsumobjective-perform_weight_sensitivity_analysis)

##### `_analyze_weight_sensitivity(self, results)`

Analyze weight sensitivity results.

[View full source →](#method-weightedsumobjective-_analyze_weight_sensitivity)



### `AdaptiveWeightedSumObjective`

**Inherits from:** `WeightedSumObjective`

Adaptive weighted sum that automatically adjusts weights based on objective performance.

This variant automatically adjusts weights based on:
- Objective value ranges (give more weight to objectives with larger ranges)
- Convergence behavior (reduce weight for objectives that aren't improving)
- Performance trends (adapt based on optimization progress)

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/multi/weighted_sum.py
:language: python
:pyobject: AdaptiveWeightedSumObjective
:linenos:
```

#### Methods (4)

##### `__init__(self)`

Initialize adaptive weighted sum objective.

[View full source →](#method-adaptiveweightedsumobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute weighted sum with adaptive weights.

[View full source →](#method-adaptiveweightedsumobjective-_compute_objective_from_simulation)

##### `_adapt_weights(self)`

Adapt weights based on objective performance.

[View full source →](#method-adaptiveweightedsumobjective-_adapt_weights)

##### `get_adaptation_info(self)`

Get information about weight adaptation.

[View full source →](#method-adaptiveweightedsumobjective-get_adaptation_info)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, List, Optional, Union, Callable`
- `import numpy as np`
- `import warnings`
- `from ..base import SimulationBasedObjective`
- `from ...core.interfaces import ObjectiveFunction`
- `from src.utils.numerical_stability import EPSILON_DIV`
