# optimization.algorithms.evolutionary.differential

**Source:** `src\optimization\algorithms\evolutionary\differential.py`

## Module Overview

Differential Evolution optimization algorithm.



## Advanced Mathematical Theory

### Differential Evolution (DE)

**Core DE algorithm:**

```{math}
\begin{align}
\text{Mutation: } & \vec{v}_i = \vec{x}_{r1} + F \cdot (\vec{x}_{r2} - \vec{x}_{r3}) \\
\text{Crossover: } & u_{i,j} = \begin{cases} v_{i,j}, & r_j \leq CR \lor j = j_{rand} \\ x_{i,j}, & \text{otherwise} \end{cases} \\
\text{Selection: } & \vec{x}_i^{t+1} = \begin{cases} \vec{u}_i, & f(\vec{u}_i) < f(\vec{x}_i) \\ \vec{x}_i, & \text{otherwise} \end{cases}
\end{align}
```

### Mutation Strategies

**DE/rand/1:**

```{math}
\vec{v}_i = \vec{x}_{r1} + F \cdot (\vec{x}_{r2} - \vec{x}_{r3})
```

**DE/best/1:**

```{math}
\vec{v}_i = \vec{x}_{best} + F \cdot (\vec{x}_{r1} - \vec{x}_{r2})
```

**DE/current-to-best/1:**

```{math}
\vec{v}_i = \vec{x}_i + F \cdot (\vec{x}_{best} - \vec{x}_i) + F \cdot (\vec{x}_{r1} - \vec{x}_{r2})
```

**DE/rand/2:**

```{math}
\vec{v}_i = \vec{x}_{r1} + F \cdot (\vec{x}_{r2} - \vec{x}_{r3}) + F \cdot (\vec{x}_{r4} - \vec{x}_{r5})
```

### Control Parameters

**Scaling factor** $F \in [0, 2]$:
- Typical: $F = 0.5$
- Controls mutation strength
- Lower $F$: Local search
- Higher $F$: Global exploration

**Crossover rate** $CR \in [0, 1]$:
- Typical: $CR = 0.9$
- Controls parameter inheritance
- Higher $CR$: More mutation components

### Adaptive DE

**Self-adaptive parameters:**

```{math}
\begin{align}
F_i &= F_{min} + (F_{max} - F_{min}) \cdot \text{rand}() \\
CR_i &= \text{rand}() \quad \text{or} \quad CR_i \sim \mathcal{N}(0.5, 0.1)
\end{align}
```

### Convergence Properties

**Theorem (Zaharie 2002):** DE converges to global optimum if:

```{math}
F \cdot \sqrt{2} < 1 \quad \text{and} \quad CR \text{ sufficiently large}
```

## Architecture Diagram

```{mermaid}
graph TD
    A[Population] --> B[For Each Individual]
    B --> C[Select r1, r2, r3]

    C --> D{Mutation Strategy}
    D -->|rand/1| E[v = r1 + F(r2-r3)]
    D -->|best/1| F[v = best + F(r1-r2)]
    D -->|current-to-best| G[v = x + F(best-x) + F(r1-r2)]

    E --> H[Crossover]
    F --> H
    G --> H

    H --> I{Binomial CR}
    I -->|Yes| J[Trial Vector u]
    I -->|No| K[Original x]

    J --> L[Selection]
    K --> L

    L --> M{f(u) < f(x)?}
    M -->|Yes| N[Replace with u]
    M -->|No| O[Keep x]

    N --> P[Next Generation]
    O --> P

    P --> Q{Converged?}
    Q -->|No| B
    Q -->|Yes| R[Return Best]

    style D fill:#ff9
    style M fill:#9cf
    style R fill:#9f9
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

```{literalinclude} ../../../src/optimization/algorithms/evolutionary/differential.py
:language: python
:linenos:
```



## Classes

### `DifferentialEvolution`

**Inherits from:** `PopulationBasedOptimizer`

Differential Evolution algorithm for global optimization.

DE is a robust evolutionary algorithm particularly effective for
continuous optimization problems with multimodal landscapes.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/evolutionary/differential.py
:language: python
:pyobject: DifferentialEvolution
:linenos:
```

#### Methods (16)

##### `__init__(self, parameter_space, population_size, mutation_factor, crossover_probability, strategy, max_iterations, tolerance, adaptive_parameters)`

Initialize Differential Evolution optimizer.

[View full source →](#method-differentialevolution-__init__)

##### `algorithm_name(self)`

Algorithm name.

[View full source →](#method-differentialevolution-algorithm_name)

##### `supports_constraints(self)`

DE can handle constraints through penalty methods.

[View full source →](#method-differentialevolution-supports_constraints)

##### `supports_bounds(self)`

DE naturally supports parameter bounds.

[View full source →](#method-differentialevolution-supports_bounds)

##### `optimize(self, problem)`

Perform DE optimization.

[View full source →](#method-differentialevolution-optimize)

##### `initialize_population(self, rng)`

Initialize population randomly within bounds.

[View full source →](#method-differentialevolution-initialize_population)

##### `update_population(self, population, fitness)`

Update population (used by base class interface).

[View full source →](#method-differentialevolution-update_population)

##### `_create_trial_population(self, rng)`

Create trial population using DE mutation and crossover.

[View full source →](#method-differentialevolution-_create_trial_population)

##### `_mutate(self, target_index, rng)`

Apply DE mutation strategy.

[View full source →](#method-differentialevolution-_mutate)

##### `_crossover(self, target, mutant, rng)`

Apply binomial crossover.

[View full source →](#method-differentialevolution-_crossover)

##### `_select_random_indices(self, exclude, count, rng)`

Select random indices excluding the target index.

[View full source →](#method-differentialevolution-_select_random_indices)

##### `_selection(self, trial_population, trial_fitness)`

Selection between current and trial populations.

[View full source →](#method-differentialevolution-_selection)

##### `_update_best(self)`

Update best individual and fitness.

[View full source →](#method-differentialevolution-_update_best)

##### `_adapt_parameters(self, iteration, max_iterations)`

Adapt F and CR parameters during evolution.

[View full source →](#method-differentialevolution-_adapt_parameters)

##### `_apply_constraint_penalties(self, fitness, population, problem)`

Apply constraint penalties to fitness values.

[View full source →](#method-differentialevolution-_apply_constraint_penalties)

##### `get_population_statistics(self)`

Get detailed population statistics.

[View full source →](#method-differentialevolution-get_population_statistics)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `from typing import Any, Dict, Optional, Tuple`
- `import logging`
- `from ...core.interfaces import PopulationBasedOptimizer, OptimizationProblem, OptimizationResult, ConvergenceStatus, ParameterSpace`
