# optimization.objectives.base

**Source:** `src\optimization\objectives\base.py`

## Module Overview

Base classes for optimization objective functions.



## Advanced Mathematical Theory

### Objective Function Design

**General form:**

```{math}
f: \mathbb{R}^n \to \mathbb{R}, \quad f(\vec{x}) = g(h_1(\vec{x}), \ldots, h_k(\vec{x}))
```

Where $h_i$ are component functions, $g$ is aggregation.

### Vectorization Strategies

**Batch evaluation:**

```{math}
\vec{F} = f(\mathbf{X}), \quad \mathbf{X} \in \mathbb{R}^{N \times n}, \quad \vec{F} \in \mathbb{R}^N
```

**Computational complexity:** $O(N \cdot C_f)$ vs $N \times O(C_f)$ for loop.

### Gradient Computation

**Finite differences:**

```{math}
\frac{\partial f}{\partial x_i} \approx \frac{f(\vec{x} + h \vec{e}_i) - f(\vec{x})}{h}
```

**Central differences** (higher accuracy):

```{math}
\frac{\partial f}{\partial x_i} \approx \frac{f(\vec{x} + h \vec{e}_i) - f(\vec{x} - h \vec{e}_i)}{2h}
```

**Automatic differentiation** (exact):

```{math}
\nabla f(\vec{x}) = \text{AutoDiff}(f, \vec{x})
```

### Smoothness Analysis

**Lipschitz continuity:**

```{math}
|f(\vec{x}) - f(\vec{y})| \leq L \|\vec{x} - \vec{y}\|
```

**Hessian condition number:**

```{math}
\kappa(\nabla^2 f) = \frac{\lambda_{max}}{\lambda_{min}}
```

High $\kappa$ indicates ill-conditioning.

### Penalty Functions

**Quadratic penalty:**

```{math}
P(\vec{x}) = \sum_{j} r_j \max(0, g_j(\vec{x}))^2
```

**Augmented Lagrangian:**

```{math}
\mathcal{L}_A(\vec{x}, \vec{\lambda}) = f(\vec{x}) + \sum_j \lambda_j g_j(\vec{x}) + \frac{\mu}{2} \sum_j g_j(\vec{x})^2
```

## Architecture Diagram

```{mermaid}
graph TD
    A[Input Parameters] --> B{Vectorized?}
    B -->|Yes| C[Batch Evaluation]
    B -->|No| D[Sequential Evaluation]

    C --> E[Parallel Compute]
    D --> E

    E --> F[Component Functions]
    F --> G[h₁, h₂, ..., hₖ]

    G --> H[Aggregation]
    H --> I{Aggregation Type}
    I -->|Weighted Sum| J[Σ wᵢhᵢ]
    I -->|Max| K[max(hᵢ)]
    I -->|Custom| L[g(h₁,...,hₖ)]

    J --> M[Objective Value]
    K --> M
    L --> M

    M --> N{Gradient Needed?}
    N -->|Yes| O[Compute Gradient]
    N -->|No| P[Return Value]

    O --> Q{Method}
    Q -->|FD| R[Finite Differences]
    Q -->|AD| S[Auto Diff]

    R --> P
    S --> P

    style B fill:#ff9
    style I fill:#9cf
    style P fill:#9f9
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

```{literalinclude} ../../../src/optimization/objectives/base.py
:language: python
:linenos:
```



## Classes

### `SimulationBasedObjective`

**Inherits from:** `ObjectiveFunction`

Base class for objectives that require simulation.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/base.py
:language: python
:pyobject: SimulationBasedObjective
:linenos:
```

#### Methods (6)

##### `__init__(self, simulation_config, controller_factory, reference_trajectory)`

Initialize simulation-based objective.

[View full source →](#method-simulationbasedobjective-__init__)

##### `_compute_objective_from_simulation(self, times, states, controls)`

Compute objective value from simulation results.

[View full source →](#method-simulationbasedobjective-_compute_objective_from_simulation)

##### `evaluate(self, parameters)`

Evaluate objective for single parameter set.

[View full source →](#method-simulationbasedobjective-evaluate)

##### `evaluate_batch(self, parameters)`

Evaluate objective for batch of parameters.

[View full source →](#method-simulationbasedobjective-evaluate_batch)

##### `_run_simulation(self, parameters)`

Run simulation with given parameters.

[View full source →](#method-simulationbasedobjective-_run_simulation)

##### `is_vectorized(self)`

Simulation-based objectives are not inherently vectorized.

[View full source →](#method-simulationbasedobjective-is_vectorized)



### `AnalyticalObjective`

**Inherits from:** `ObjectiveFunction`

Base class for analytical objective functions.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/base.py
:language: python
:pyobject: AnalyticalObjective
:linenos:
```

#### Methods (5)

##### `__init__(self)`

Initialize analytical objective.

[View full source →](#method-analyticalobjective-__init__)

##### `_compute_analytical_objective(self, parameters)`

Compute objective analytically.

[View full source →](#method-analyticalobjective-_compute_analytical_objective)

##### `evaluate(self, parameters)`

Evaluate objective for single parameter set.

[View full source →](#method-analyticalobjective-evaluate)

##### `evaluate_batch(self, parameters)`

Evaluate objective for batch of parameters.

[View full source →](#method-analyticalobjective-evaluate_batch)

##### `is_vectorized(self)`

Analytical objectives can be vectorized.

[View full source →](#method-analyticalobjective-is_vectorized)



### `CompositeObjective`

**Inherits from:** `ObjectiveFunction`

Composite objective combining multiple objectives.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/base.py
:language: python
:pyobject: CompositeObjective
:linenos:
```

#### Methods (6)

##### `__init__(self, objectives, weights, combination_method)`

Initialize composite objective.

[View full source →](#method-compositeobjective-__init__)

##### `evaluate(self, parameters)`

Evaluate composite objective.

[View full source →](#method-compositeobjective-evaluate)

##### `evaluate_batch(self, parameters)`

Evaluate composite objective for batch.

[View full source →](#method-compositeobjective-evaluate_batch)

##### `_combine_objectives(self, values)`

Combine objective values according to method.

[View full source →](#method-compositeobjective-_combine_objectives)

##### `is_vectorized(self)`

Composite objective is vectorized if all components are.

[View full source →](#method-compositeobjective-is_vectorized)

##### `get_individual_evaluations(self, parameters)`

Get individual objective evaluations.

[View full source →](#method-compositeobjective-get_individual_evaluations)



### `PenaltyObjective`

**Inherits from:** `ObjectiveFunction`

Objective with constraint penalties.

#### Source Code

```{literalinclude} ../../../src/optimization/objectives/base.py
:language: python
:pyobject: PenaltyObjective
:linenos:
```

#### Methods (5)

##### `__init__(self, base_objective, constraints, penalty_factor)`

Initialize penalty objective.

[View full source →](#method-penaltyobjective-__init__)

##### `evaluate(self, parameters)`

Evaluate objective with penalties.

[View full source →](#method-penaltyobjective-evaluate)

##### `evaluate_batch(self, parameters)`

Evaluate objective with penalties for batch.

[View full source →](#method-penaltyobjective-evaluate_batch)

##### `_compute_penalty(self, parameters)`

Compute constraint penalty.

[View full source →](#method-penaltyobjective-_compute_penalty)

##### `is_vectorized(self)`

Penalty objective inherits vectorization from base.

[View full source →](#method-penaltyobjective-is_vectorized)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, List, Optional, Union, Callable`
- `import numpy as np`
- `from ..core.interfaces import ObjectiveFunction`
