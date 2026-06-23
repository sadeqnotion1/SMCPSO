# optimization.objectives.multi.pareto

**Source:** `src\optimization\objectives\multi\pareto.py`

## Module Overview

Pareto-based multi-objective optimization.



## Advanced Mathematical Theory

### Pareto Front Computation

**Pareto set:**

```{math}
\mathcal{P} = \{\vec{x} \in \mathcal{X} : \nexists \vec{y} \in \mathcal{X}, \vec{y} \prec \vec{x}\}
```

**Pareto front:**

```{math}
\mathcal{F} = \{\vec{F}(\vec{x}) : \vec{x} \in \mathcal{P}\}
```

### Fast Non-Dominated Sorting

**Algorithm (Deb et al. 2002):**

1. **Domination count:** $n_p = |\{\vec{q} : \vec{q} \prec \vec{p}\}|$
2. **Dominated set:** $S_p = \{\vec{q} : \vec{p} \prec \vec{q}\}$
3. **Front assignment:**

```{math}
\begin{align}
\mathcal{F}_1 &= \{\vec{p} : n_p = 0\} \\
\mathcal{F}_i &= \{\vec{q} \in S_p : p \in \mathcal{F}_{i-1}, n_q = 1\}
\end{align}
```

**Complexity:** $O(M N^2)$ for $M$ objectives, $N$ solutions.

### Crowding Distance

**Distance metric** for diversity:

```{math}
CD_i = \sum_{m=1}^{M} \frac{f_m^{i+1} - f_m^{i-1}}{f_m^{max} - f_m^{min}}
```

**Boundary solutions:** $CD_1 = CD_N = \infty$

### Hypervolume Indicator

**Quality metric:**

```{math}
HV(\mathcal{S}) = \text{Volume}\left(\bigcup_{\vec{s} \in \mathcal{S}} [\vec{s}, \vec{r}]\right)
```

Where $\vec{r}$ is reference point.

**Properties:**
- Unary indicator (single set)
- Monotonic with Pareto dominance
- Sensitive to spread and convergence

### Reference Point Methods

**Achievement scalarizing function:**

```{math}
\max_{i=1,\ldots,k} w_i (f_i(\vec{x}) - z_i^*) + \rho \sum_{i=1}^{k} w_i (f_i(\vec{x}) - z_i^*)
```

Where $\vec{z}^*$ is reference point, $\rho \ll 1$.

## Architecture Diagram

```{mermaid}
graph TD
    A[Solution Set] --> B[For Each Solution]
    B --> C[Dominance Check]

    C --> D{Compare with Others}
    D --> E[Count Dominated By]
    E --> F[Store Dominates]

    F --> G{Domination Count}
    G -->|0| H[Pareto Front 1]
    G -->|> 0| I[Lower Front]

    H --> J[Compute Crowding Distance]
    I --> J

    J --> K[For Each Objective]
    K --> L[Sort by Objective]
    L --> M[Compute Distance]

    M --> N[Sum Distances]
    N --> O{Archive Pruning?}
    O -->|Yes| P[Remove Min CD]
    O -->|No| Q[Keep All]

    P --> R[Pareto Set]
    Q --> R

    R --> S[Return Non-Dominated]

    style G fill:#ff9
    style O fill:#9cf
    style S fill:#9f9
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
## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/multi/pareto.py
:language: python
:linenos:
```



## Classes

### `ParetoObjective`

**Inherits from:** `SimulationBasedObjective`

Multi-objective optimization using Pareto dominance.

This objective handles true multi-objective optimization by maintaining
a Pareto frontier of non-dominated solutions. Unlike weighted sum approaches,
this can find solutions on non-convex portions of the Pareto frontier.

The objective returns a composite metric but also maintains detailed
Pareto analysis for optimization algorithms that can handle it.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/multi/pareto.py
:language: python
:pyobject: ParetoObjective
:linenos:
```

#### Methods (23)

##### `__init__(self, simulation_config, controller_factory, objectives, scalarization_method, reference_point, normalization, reference_trajectory)`

Initialize Pareto multi-objective.

[View full source →](#method-paretoobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute Pareto-based objective from simulation results.

[View full source →](#method-paretoobjective-_compute_objective_from_simulation)

##### `_update_pareto_frontier(self, parameters, objectives)`

Update the Pareto frontier with new solution.

[View full source →](#method-paretoobjective-_update_pareto_frontier)

##### `_check_dominance(self, obj1, obj2)`

Check dominance relationship between two objective vectors.

[View full source →](#method-paretoobjective-_check_dominance)

##### `_normalize_objectives(self, objective_values)`

Normalize objective values.

[View full source →](#method-paretoobjective-_normalize_objectives)

##### `_scalarize_objectives(self, objectives)`

Convert multi-objective values to scalar.

[View full source →](#method-paretoobjective-_scalarize_objectives)

##### `_compute_hypervolume_contribution(self, objectives)`

Compute hypervolume contribution (approximation).

[View full source →](#method-paretoobjective-_compute_hypervolume_contribution)

##### `_compute_crowding_distance(self, objectives)`

Compute crowding distance metric.

[View full source →](#method-paretoobjective-_compute_crowding_distance)

##### `_compute_epsilon_indicator(self, objectives)`

Compute epsilon indicator metric.

[View full source →](#method-paretoobjective-_compute_epsilon_indicator)

##### `get_pareto_frontier(self)`

Get current Pareto frontier information.

[View full source →](#method-paretoobjective-get_pareto_frontier)

##### `_compute_frontier_metrics(self)`

Compute metrics about the current Pareto frontier.

[View full source →](#method-paretoobjective-_compute_frontier_metrics)

##### `_compute_frontier_hypervolume(self)`

Compute hypervolume of current Pareto frontier.

[View full source →](#method-paretoobjective-_compute_frontier_hypervolume)

##### `_compute_frontier_spread(self, objectives_array)`

Compute spread (diversity) of Pareto frontier.

[View full source →](#method-paretoobjective-_compute_frontier_spread)

##### `_compute_frontier_extent(self, objectives_array)`

Compute extent (range) of Pareto frontier.

[View full source →](#method-paretoobjective-_compute_frontier_extent)

##### `evaluate_solution_quality(self, times, states, controls)`

Evaluate solution quality in multi-objective context.

[View full source →](#method-paretoobjective-evaluate_solution_quality)

##### `_compute_pareto_rank(self, objectives)`

Compute Pareto rank (1 = non-dominated, higher = more dominated).

[View full source →](#method-paretoobjective-_compute_pareto_rank)

##### `_count_dominated_solutions(self, objectives)`

Count how many solutions this one dominates.

[View full source →](#method-paretoobjective-_count_dominated_solutions)

##### `_count_dominating_solutions(self, objectives)`

Count how many solutions dominate this one.

[View full source →](#method-paretoobjective-_count_dominating_solutions)

##### `reset_pareto_frontier(self)`

Reset the Pareto frontier and evaluation history.

[View full source →](#method-paretoobjective-reset_pareto_frontier)

##### `get_optimization_progress(self)`

Get optimization progress information.

[View full source →](#method-paretoobjective-get_optimization_progress)

##### `_compute_convergence_metrics(self)`

Compute convergence metrics for the optimization.

[View full source →](#method-paretoobjective-_compute_convergence_metrics)

##### `_measure_recent_improvement(self, recent_objectives)`

Measure improvement in recent evaluations.

[View full source →](#method-paretoobjective-_measure_recent_improvement)

##### `_measure_frontier_stability(self)`

Measure stability of Pareto frontier.

[View full source →](#method-paretoobjective-_measure_frontier_stability)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, List, Optional, Union, Callable, Tuple`
- `import numpy as np`
- `import warnings`
- `from ..base import SimulationBasedObjective`
- `from ...core.interfaces import ObjectiveFunction`
- `from src.utils.numerical_stability import EPSILON_DIV`
