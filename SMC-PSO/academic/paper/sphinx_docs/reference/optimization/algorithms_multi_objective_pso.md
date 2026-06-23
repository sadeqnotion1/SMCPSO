# optimization.algorithms.multi_objective_pso

**Source:** `src\optimization\algorithms\multi_objective_pso.py`

## Module Overview

Multi-Objective Particle Swarm Optimization (MOPSO) for Controller Tuning.



## Advanced Mathematical Theory

### Multi-Objective PSO (MOPSO)

**Multi-objective optimization problem:**

```{math}
\min_{\vec{x} \in \mathcal{X}} \vec{F}(\vec{x}) = [f_1(\vec{x}), \ldots, f_k(\vec{x})]^T
```

**Pareto dominance:**

```{math}
\vec{x} \prec \vec{y} \iff f_i(\vec{x}) \leq f_i(\vec{y}) \, \forall i \land \exists j: f_j(\vec{x}) < f_j(\vec{y})
```

### Non-Dominated Sorting

**Pareto rank assignment:**

```{math}
\begin{align}
\text{Rank}(\vec{x}) &= 1 + |\{\vec{y} : \vec{y} \prec \vec{x}\}| \\
\mathcal{P}_1 &= \{\vec{x} : \text{Rank}(\vec{x}) = 1\} \\
\mathcal{P}_i &= \{\vec{x} : \text{Rank}(\vec{x}) = i\}
\end{align}
```

**Complexity:** $O(M N^2 k)$ for $M$ objectives, $N$ solutions.

### Archive Maintenance

**Bounded external archive** $\mathcal{A}$ with max size $A_{max}$:

```{math}
\mathcal{A}^{t+1} = \text{Prune}(\mathcal{A}^t \cup \{\text{non-dominated from iteration } t\}, A_{max})
```

### Crowding Distance

**Diversity metric** for archive pruning:

```{math}
CD_i = \sum_{m=1}^{M} \frac{f_m(\vec{x}_{i+1}) - f_m(\vec{x}_{i-1})}{f_m^{max} - f_m^{min}}
```

**Pruning strategy:** Remove solutions with smallest crowding distance.

### Leader Selection

**Roulette wheel selection** based on crowding distance:

```{math}
P(\vec{x}_i \text{ selected as leader}) = \frac{CD_i}{\sum_j CD_j}
```

Favors less crowded regions for better diversity.

### MOPSO Velocity Update

**Modified velocity update** with archive leader:

```{math}
v_{i,d}^{t+1} = w v_{i,d}^t + c_1 r_1 (p_{i,d} - x_{i,d}^t) + c_2 r_2 (l_d - x_{i,d}^t)
```

Where $\vec{l}$ is leader selected from archive $\mathcal{A}$.

## Architecture Diagram

```{mermaid}
graph TD
    A[Initialize Swarm] --> B[Evaluate Objectives]
    B --> C[Non-Dominated Sorting]
    C --> D[Update Archive]

    D --> E{Archive Size}
    E -->|< Max| F[Add All]
    E -->|> Max| G[Prune by Crowding]

    F --> H[Compute Crowding Distance]
    G --> H

    H --> I[Select Leaders]
    I --> J[Update Velocities]
    J --> K[Update Positions]

    K --> L[Convergence Check]
    L --> M{Converged?}
    M -->|No| B
    M -->|Yes| N[Return Pareto Front]

    style C fill:#9cf
    style H fill:#ff9
    style N fill:#9f9
```

## Usage Examples

### Example 1: Basic Initialization

```python
from src.optimization.algorithms import *

# Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
```

## Example 2: Performance Tuning

```python
# Adjust parameters for better performance
optimized_params = tune_parameters(instance, target_performance)
```

## Example 3: Integration with Optimization

```python
# Use in complete optimization loop
optimizer = create_optimizer(opt_type, config)
result = optimize(optimizer, problem, max_iter=100)
```

## Example 4: Edge Case Handling

```python
try:
    output = instance.compute(parameters)
except ValueError as e:
    handle_edge_case(e)
```

### Example 5: Performance Analysis

```python
# Analyze metrics
metrics = compute_metrics(result)
print(f"Best fitness: {metrics.best_fitness:.3f}")
```

This module implements a production-ready multi-objective PSO algorithm specifically
designed for control system parameter optimization. It provides Pareto front discovery,
convergence analysis, and advanced optimization features.

Features:
- NSGA-II style non-dominated sorting
- Crowding distance calculation for diversity maintenance
- Archive-based Pareto front management
- Hypervolume indicator for convergence assessment
- Real-time convergence monitoring
- Statistical validation and benchmarking

References:
- Coello, C.A.C., et al. "MOPSO: A proposal for multiple objective particle swarm optimization."
  IEEE Congress on Evolutionary Computation, 2002.
- Deb, K., et al. "A fast and elitist multiobjective genetic algorithm: NSGA-II."
  IEEE Transactions on Evolutionary Computation, 2002.

## Complete Source Code

```{literalinclude} ../../../src/optimization/algorithms/multi_objective_pso.py
:language: python
:linenos:
```



## Classes

### `MOPSOConfig`

Multi-Objective PSO Configuration.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/multi_objective_pso.py
:language: python
:pyobject: MOPSOConfig
:linenos:
```



### `ParetoArchive`

Efficient Pareto archive for non-dominated solutions.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/multi_objective_pso.py
:language: python
:pyobject: ParetoArchive
:linenos:
```

#### Methods (6)

##### `__init__(self, max_size)`

[View full source →](#method-paretoarchive-__init__)

##### `add_solution(self, position, objectives, metadata)`

Add a solution to the archive if it's non-dominated.

[View full source →](#method-paretoarchive-add_solution)

##### `_dominates(self, obj1, obj2)`

Check if obj1 dominates obj2 (minimization assumed).

[View full source →](#method-paretoarchive-_dominates)

##### `_truncate_archive(self)`

Remove solutions with lowest crowding distance.

[View full source →](#method-paretoarchive-_truncate_archive)

##### `_calculate_crowding_distance(self, objectives)`

Calculate crowding distance for diversity maintenance.

[View full source →](#method-paretoarchive-_calculate_crowding_distance)

##### `get_pareto_front(self)`

Get the current Pareto front.

[View full source →](#method-paretoarchive-get_pareto_front)



### `MultiObjectivePSO`

Multi-Objective Particle Swarm Optimization for Controller Tuning.

This implementation provides advanced multi-objective optimization features
with Pareto front discovery and convergence analysis.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/multi_objective_pso.py
:language: python
:pyobject: MultiObjectivePSO
:linenos:
```

#### Methods (10)

##### `__init__(self, bounds, config)`

[View full source →](#method-multiobjectivepso-__init__)

##### `optimize(self, objective_functions, constraints, reference_point)`

Execute multi-objective PSO optimization.

[View full source →](#method-multiobjectivepso-optimize)

##### `_evaluate_population(self, objective_functions, positions)`

Evaluate objective functions for all particles.

[View full source →](#method-multiobjectivepso-_evaluate_population)

##### `_update_leaders(self)`

Update leader particles from archive.

[View full source →](#method-multiobjectivepso-_update_leaders)

##### `_update_swarm(self, iteration)`

Update particle velocities and positions.

[View full source →](#method-multiobjectivepso-_update_swarm)

##### `_update_personal_bests(self, new_objectives)`

Update personal best positions and add to archive.

[View full source →](#method-multiobjectivepso-_update_personal_bests)

##### `_dominates(self, obj1, obj2)`

Check if obj1 dominates obj2.

[View full source →](#method-multiobjectivepso-_dominates)

##### `_calculate_hypervolume(self, objectives, reference_point)`

Calculate hypervolume indicator.

[View full source →](#method-multiobjectivepso-_calculate_hypervolume)

##### `_hypervolume_2d(self, objectives, reference_point)`

Calculate exact hypervolume for 2D case.

[View full source →](#method-multiobjectivepso-_hypervolume_2d)

##### `_hypervolume_monte_carlo(self, objectives, reference_point, n_samples)`

Monte Carlo approximation of hypervolume.

[View full source →](#method-multiobjectivepso-_hypervolume_monte_carlo)



## Functions

### `create_control_objectives(pso_tuner)`

Create multiple objective functions for control system optimization.

Parameters
pso_tuner : PSOTuner
    Single-objective PSO tuner to extract fitness components

Returns
-------
List[Callable]
    List of objective functions for multi-objective optimization

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/multi_objective_pso.py
:language: python
:pyobject: create_control_objectives
:linenos:
```



### `run_multi_objective_pso(controller_factory, config, seed)`

Run multi-objective PSO optimization for controller tuning.

Parameters
----------
controller_factory : Callable
    Factory function to create controllers with given gains
config : ConfigSchema
    Configuration object
seed : int, optional
    Random seed for reproducibility

Returns
-------
Dict[str, Any]
    Multi-objective optimization results

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/multi_objective_pso.py
:language: python
:pyobject: run_multi_objective_pso
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import logging`
- `import numpy as np`
- `from typing import Any, Callable, Dict, List, Optional, Tuple, Union`
- `from dataclasses import dataclass`
- `from concurrent.futures import ThreadPoolExecutor`
- `import threading`
- `from src.optimization.algorithms.pso_optimizer import PSOTuner`
- `from src.config import ConfigSchema`
