# optimization.core.problem

**Source:** `src\optimization\core\problem.py`

## Module Overview

Optimization problem builders and specialized problem types.



## Advanced Mathematical Theory

### Optimization Problem Formulation

**General constrained optimization problem:**

```{math}
\begin{align}
\min_{\vec{x} \in \mathcal{X}} \quad & f(\vec{x}) \\
\text{subject to} \quad & g_j(\vec{x}) \leq 0, \quad j = 1, \ldots, m \\
& h_k(\vec{x}) = 0, \quad k = 1, \ldots, p
\end{align}
```

Where:
- $f: \mathbb{R}^n \to \mathbb{R}$: Objective function
- $\mathcal{X} \subset \mathbb{R}^n$: Feasible region
- $g_j$: Inequality constraints
- $h_k$: Equality constraints

### Builder Pattern Theory

**Fluent API** for problem construction:

```{math}
\text{Problem} = \text{Builder}()
    .\text{with_objective}(f)
    .\text{with_bounds}(l, u)
    .\text{with_constraint}(g)
    .\text{build}()
```

**Advantages:**
- Immutable problem objects
- Validation at build time
- Type-safe construction

### Multi-Objective Optimization

**Pareto dominance** for objectives $f_1, \ldots, f_k$:

```{math}
\vec{x} \prec \vec{y} \iff f_i(\vec{x}) \leq f_i(\vec{y}) \, \forall i \land \exists j: f_j(\vec{x}) < f_j(\vec{y})
```

**Pareto front:**

```{math}
\mathcal{P} = \{\vec{x} \in \mathcal{X} : \nexists \vec{y} \in \mathcal{X}, \vec{y} \prec \vec{x}\}
```

### Weighted Sum Scalarization

**Convert multi-objective to single objective:**

```{math}
f_{weighted}(\vec{x}) = \sum_{i=1}^{k} w_i f_i(\vec{x}), \quad \sum_{i=1}^{k} w_i = 1, \, w_i \geq 0
```

**Limitations:**
- Cannot find non-convex Pareto points
- Weight selection affects solution
- Requires preference information

### Control Optimization Formulation

**Controller parameter tuning:**

```{math}
\begin{align}
\min_{\vec{\theta} \in \Theta} \quad & J(\vec{\theta}) = w_1 \text{ITAE}(\vec{\theta}) + w_2 \text{ISE}(\vec{\theta}) + w_3 \text{CHAT}(\vec{\theta}) \\
\text{subject to} \quad & \theta_{min,i} \leq \theta_i \leq \theta_{max,i} \\
& |u_{max}(\vec{\theta})| \leq u_{sat}
\end{align}
```

Where $\vec{\theta}$ are controller gains.

## Architecture Diagram

```{mermaid}
graph TD
    A[Problem Builder] --> B[Set Objective]
    B --> C[Set Parameter Space]
    C --> D{Add Constraints?}
    D -->|Yes| E[Add Constraint]
    E --> D
    D -->|No| F[Set Optimization Type]
    F --> G{Minimize or Maximize?}
    G -->|Minimize| H[Build Min Problem]
    G -->|Maximize| I[Build Max Problem]

    H --> J[Validate Problem]
    I --> J

    J --> K{Valid?}
    K -->|Yes| L[Optimization Problem]
    K -->|No| M[Raise Error]

    style D fill:#ff9
    style J fill:#9cf
    style L fill:#9f9
    style M fill:#f99
```

## Usage Examples

### Example 1: Basic Initialization

```python
from src.optimization.core import *

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

```{literalinclude} ../../../src/optimization/core/problem.py
:language: python
:linenos:
```



## Classes

### `OptimizationProblemBuilder`

Builder for constructing optimization problems.

#### Source Code

```{literalinclude} ../../../src/optimization/core/problem.py
:language: python
:pyobject: OptimizationProblemBuilder
:linenos:
```

#### Methods (9)

##### `__init__(self)`

Initialize problem builder.

[View full source →](#method-optimizationproblembuilder-__init__)

##### `with_objective(self, objective)`

Set objective function.

[View full source →](#method-optimizationproblembuilder-with_objective)

##### `with_parameter_space(self, parameter_space)`

Set parameter space.

[View full source →](#method-optimizationproblembuilder-with_parameter_space)

##### `with_bounds(self, lower, upper)`

Set parameter bounds (creates continuous parameter space).

[View full source →](#method-optimizationproblembuilder-with_bounds)

##### `minimize(self)`

Set optimization type to minimization.

[View full source →](#method-optimizationproblembuilder-minimize)

##### `maximize(self)`

Set optimization type to maximization.

[View full source →](#method-optimizationproblembuilder-maximize)

##### `with_constraint(self, constraint)`

Add constraint.

[View full source →](#method-optimizationproblembuilder-with_constraint)

##### `with_name(self, name)`

Set problem name.

[View full source →](#method-optimizationproblembuilder-with_name)

##### `build(self)`

Build optimization problem.

[View full source →](#method-optimizationproblembuilder-build)



### `ControlOptimizationProblem`

**Inherits from:** `OptimizationProblem`

Specialized optimization problem for control parameter tuning.

#### Source Code

```{literalinclude} ../../../src/optimization/core/problem.py
:language: python
:pyobject: ControlOptimizationProblem
:linenos:
```

#### Methods (3)

##### `__init__(self, objective, parameter_space, controller_factory, simulation_config, optimization_type, constraints, name)`

Initialize control optimization problem.

[View full source →](#method-controloptimizationproblem-__init__)

##### `create_controller(self, parameters)`

Create controller from optimization parameters.

[View full source →](#method-controloptimizationproblem-create_controller)

##### `simulate_controller(self, parameters)`

Simulate controller with given parameters.

[View full source →](#method-controloptimizationproblem-simulate_controller)



### `MultiObjectiveProblem`

**Inherits from:** `OptimizationProblem`

Multi-objective optimization problem.

#### Source Code

```{literalinclude} ../../../src/optimization/core/problem.py
:language: python
:pyobject: MultiObjectiveProblem
:linenos:
```

#### Methods (3)

##### `__init__(self, objectives, parameter_space, weights, optimization_type, constraints, name)`

Initialize multi-objective problem.

[View full source →](#method-multiobjectiveproblem-__init__)

##### `evaluate_objectives(self, parameters)`

Evaluate all individual objectives.

[View full source →](#method-multiobjectiveproblem-evaluate_objectives)

##### `evaluate_objectives_batch(self, parameters)`

Evaluate all objectives for batch of parameters.

[View full source →](#method-multiobjectiveproblem-evaluate_objectives_batch)



### `WeightedSumObjective`

**Inherits from:** `ObjectiveFunction`

Weighted sum of multiple objectives.

#### Source Code

```{literalinclude} ../../../src/optimization/core/problem.py
:language: python
:pyobject: WeightedSumObjective
:linenos:
```

#### Methods (4)

##### `__init__(self, objectives, weights)`

Initialize weighted sum objective.

[View full source →](#method-weightedsumobjective-__init__)

##### `evaluate(self, parameters)`

Evaluate weighted sum of objectives.

[View full source →](#method-weightedsumobjective-evaluate)

##### `evaluate_batch(self, parameters)`

Evaluate weighted sum for batch of parameters.

[View full source →](#method-weightedsumobjective-evaluate_batch)

##### `is_vectorized(self)`

Vectorized if all component objectives are vectorized.

[View full source →](#method-weightedsumobjective-is_vectorized)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, List, Optional, Callable, Union`
- `import numpy as np`
- `from .interfaces import OptimizationProblem, ObjectiveFunction, ParameterSpace, Constraint, OptimizationType`
- `from .parameters import ContinuousParameterSpace`
