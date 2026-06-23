# optimization.algorithms.evolutionary.genetic

**Source:** `src\optimization\algorithms\evolutionary\genetic.py`

## Module Overview

Genetic Algorithm implementation for control parameter optimization.



## Advanced Mathematical Theory

### Genetic Algorithm (GA)

**Population evolution:**

```{math}
\mathcal{P}^{t+1} = \text{Mutate}(\text{Crossover}(\text{Select}(\mathcal{P}^t)))
```

### Selection Operators

**Roulette wheel selection:**

```{math}
P(\vec{x}_i \text{ selected}) = \frac{f(\vec{x}_i)}{\sum_j f(\vec{x}_j)}
```

**Tournament selection:**

```{math}
\vec{x}_{winner} = \arg\max_{\vec{x} \in \text{Tournament}} f(\vec{x})
```

**Rank-based selection:**

```{math}
P(\vec{x}_i) = \frac{N - \text{rank}(\vec{x}_i) + 1}{\sum_j (N - \text{rank}(\vec{x}_j) + 1)}
```

### Crossover Operators

**Single-point crossover:**

```{math}
\begin{align}
\text{Child}_1[1:k] &= \text{Parent}_1[1:k], \quad \text{Child}_1[k+1:n] = \text{Parent}_2[k+1:n] \\
\text{Child}_2[1:k] &= \text{Parent}_2[1:k], \quad \text{Child}_2[k+1:n] = \text{Parent}_1[k+1:n]
\end{align}
```

**Uniform crossover:**

```{math}
\text{Child}_i[j] = \begin{cases}
\text{Parent}_1[j], & r_j < 0.5 \\
\text{Parent}_2[j], & r_j \geq 0.5
\end{cases}
```

### Mutation Operators

**Bit-flip mutation** (binary encoding):

```{math}
x_i' = \begin{cases}
1 - x_i, & r < p_m \\
x_i, & r \geq p_m
\end{cases}
```

**Gaussian mutation** (real encoding):

```{math}
x_i' = x_i + \mathcal{N}(0, \sigma^2)
```

### Schema Theorem

**Holland's Schema Theorem:**

```{math}
E[m(H, t+1)] \geq m(H, t) \cdot \frac{f(H)}{\bar{f}} \cdot \left[1 - p_c \delta(H) - o(H)p_m\right]
```

Where:
- $m(H, t)$: Number of schema $H$ instances at generation $t$
- $f(H)$: Average fitness of schema
- $\delta(H)$: Defining length
- $o(H)$: Order (number of fixed positions)

**Implication:** Short, low-order, above-average schemata grow exponentially.

## Architecture Diagram

```{mermaid}
graph TD
    A[Initialize Population] --> B[Evaluate Fitness]
    B --> C[Selection]

    C --> D{Selection Type}
    D -->|Roulette| E[Fitness Proportional]
    D -->|Tournament| F[Best of K]
    D -->|Rank| G[Rank-Based]

    E --> H[Crossover]
    F --> H
    G --> H

    H --> I{Crossover Type}
    I -->|Single-Point| J[Single Cut]
    I -->|Two-Point| K[Two Cuts]
    I -->|Uniform| L[Random Mix]

    J --> M[Mutation]
    K --> M
    L --> M

    M --> N[New Population]
    N --> O[Convergence Check]

    O --> P{Converged?}
    P -->|No| B
    P -->|Yes| Q[Return Best]

    style D fill:#ff9
    style I fill:#9cf
    style Q fill:#9f9
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

```{literalinclude} ../../../src/optimization/algorithms/evolutionary/genetic.py
:language: python
:linenos:
```



## Classes

### `GeneticAlgorithmConfig`

Configuration for Genetic Algorithm.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/evolutionary/genetic.py
:language: python
:pyobject: GeneticAlgorithmConfig
:linenos:
```



### `Individual`

Individual in the genetic algorithm population.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/evolutionary/genetic.py
:language: python
:pyobject: Individual
:linenos:
```

#### Methods (3)

##### `__init__(self, genes, fitness)`

[View full source →](#method-individual-__init__)

##### `copy(self)`

Create a copy of the individual.

[View full source →](#method-individual-copy)

##### `__str__(self)`

[View full source →](#method-individual-__str__)



### `GeneticAlgorithm`

**Inherits from:** `OptimizationAlgorithm`

Genetic Algorithm for parameter optimization.

A population-based evolutionary algorithm that uses selection, crossover,
and mutation operators to evolve a population of candidate solutions.

Features:
- Multiple selection methods (tournament, roulette, rank)
- Various crossover operators (uniform, single-point, arithmetic)
- Adaptive mutation strategies
- Elitist preservation
- Diversity maintenance
- Parallel fitness evaluation

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/evolutionary/genetic.py
:language: python
:pyobject: GeneticAlgorithm
:linenos:
```

#### Methods (30)

##### `__init__(self, config)`

Initialize Genetic Algorithm.

[View full source →](#method-geneticalgorithm-__init__)

##### `optimize(self, problem, parameter_space)`

Run genetic algorithm optimization.

[View full source →](#method-geneticalgorithm-optimize)

##### `_initialize_population(self)`

Initialize the population randomly.

[View full source →](#method-geneticalgorithm-_initialize_population)

##### `_evaluate_population(self)`

Evaluate fitness for all individuals in population.

[View full source →](#method-geneticalgorithm-_evaluate_population)

##### `_evaluate_population_serial(self)`

Evaluate population serially.

[View full source →](#method-geneticalgorithm-_evaluate_population_serial)

##### `_evaluate_population_parallel(self)`

Evaluate population in parallel.

[View full source →](#method-geneticalgorithm-_evaluate_population_parallel)

##### `_safe_evaluate(self, genes)`

Safe evaluation wrapper for parallel processing.

[View full source →](#method-geneticalgorithm-_safe_evaluate)

##### `_create_new_generation(self)`

Create new generation using selection, crossover, and mutation.

[View full source →](#method-geneticalgorithm-_create_new_generation)

##### `_select_elite(self, count)`

Select elite individuals (best fitness).

[View full source →](#method-geneticalgorithm-_select_elite)

##### `_select_individual(self)`

Select individual based on selection method.

[View full source →](#method-geneticalgorithm-_select_individual)

##### `_tournament_selection(self)`

Tournament selection.

[View full source →](#method-geneticalgorithm-_tournament_selection)

##### `_roulette_selection(self)`

Roulette wheel selection.

[View full source →](#method-geneticalgorithm-_roulette_selection)

##### `_rank_selection(self)`

Rank-based selection.

[View full source →](#method-geneticalgorithm-_rank_selection)

##### `_crossover(self, parent1, parent2)`

Perform crossover between two parents.

[View full source →](#method-geneticalgorithm-_crossover)

##### `_uniform_crossover(self, parent1, parent2)`

Uniform crossover - each gene has 50% chance of coming from either parent.

[View full source →](#method-geneticalgorithm-_uniform_crossover)

##### `_single_point_crossover(self, parent1, parent2)`

Single-point crossover.

[View full source →](#method-geneticalgorithm-_single_point_crossover)

##### `_arithmetic_crossover(self, parent1, parent2)`

Arithmetic crossover - weighted average of parents.

[View full source →](#method-geneticalgorithm-_arithmetic_crossover)

##### `_mutate(self, individual)`

Mutate an individual.

[View full source →](#method-geneticalgorithm-_mutate)

##### `_gaussian_mutation(self, individual)`

Gaussian mutation - add normally distributed noise.

[View full source →](#method-geneticalgorithm-_gaussian_mutation)

##### `_uniform_mutation(self, individual)`

Uniform mutation - replace with random value in range.

[View full source →](#method-geneticalgorithm-_uniform_mutation)

##### `_polynomial_mutation(self, individual)`

Polynomial mutation.

[View full source →](#method-geneticalgorithm-_polynomial_mutation)

##### `_update_algorithm_state(self)`

Update algorithm state after each generation.

[View full source →](#method-geneticalgorithm-_update_algorithm_state)

##### `_update_best_individual(self)`

Update the best individual found so far.

[View full source →](#method-geneticalgorithm-_update_best_individual)

##### `_calculate_diversity(self)`

Calculate population diversity.

[View full source →](#method-geneticalgorithm-_calculate_diversity)

##### `_update_adaptive_parameters(self)`

Update adaptive algorithm parameters.

[View full source →](#method-geneticalgorithm-_update_adaptive_parameters)

##### `_check_convergence(self)`

Check if algorithm has converged.

[View full source →](#method-geneticalgorithm-_check_convergence)

##### `_create_result(self)`

Create optimization result.

[View full source →](#method-geneticalgorithm-_create_result)

##### `get_population_statistics(self)`

Get statistics about current population.

[View full source →](#method-geneticalgorithm-get_population_statistics)

##### `_estimate_convergence_rate(self)`

Estimate convergence rate from fitness history.

[View full source →](#method-geneticalgorithm-_estimate_convergence_rate)

##### `_calculate_selection_pressure(self)`

Calculate selection pressure in population.

[View full source →](#method-geneticalgorithm-_calculate_selection_pressure)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, List, Optional, Callable, Tuple, Union`
- `import numpy as np`
- `import warnings`
- `from dataclasses import dataclass`
- `from concurrent.futures import ProcessPoolExecutor`
- `import multiprocessing as mp`
- `from ..base import OptimizationAlgorithm`
- `from ...core.interfaces import OptimizationProblem, ParameterSpace, OptimizationResult`
- `from ...core.parameters import ContinuousParameterSpace`

*... and 1 more*
