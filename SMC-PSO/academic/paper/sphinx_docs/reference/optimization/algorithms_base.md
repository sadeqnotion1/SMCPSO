# optimization.algorithms.base

**Source:** `src\optimization\algorithms\base.py`

## Module Overview

Base classes for optimization algorithms.



## Advanced Mathematical Theory

### Base Algorithm Structure

**Iterative optimization template:**

```{math}
\begin{align}
& \text{Initialize: } \vec{x}^0 \in \mathcal{X} \\
& \text{Repeat until convergence:} \\
& \quad \vec{x}^{t+1} = \mathcal{U}(\vec{x}^t, \nabla f(\vec{x}^t), \ldots) \\
& \quad \text{Check: } \|\vec{x}^{t+1} - \vec{x}^t\| < \epsilon
\end{align}
```

Where $\mathcal{U}$ is algorithm-specific update rule.

### Population-Based vs Gradient-Based

**Population-based:**
- Derivative-free
- Global search capability
- Parallel evaluation
- No gradient information needed

**Gradient-based:**
- Local convergence guarantees
- Fast convergence near optimum
- Requires differentiability
- Sequential evaluation

### Convergence Analysis

**Deterministic convergence:**

```{math}
\lim_{t \to \infty} \|\vec{x}^t - \vec{x}^*\| = 0
```

**Stochastic convergence (in probability):**

```{math}
\lim_{t \to \infty} P(\|\vec{x}^t - \vec{x}^*\| > \epsilon) = 0
```

### Exploration vs Exploitation

**Diversity metric** for population $\vec{X}$:

```{math}
D(\vec{X}) = \frac{1}{N(N-1)} \sum_{i=1}^{N} \sum_{j \neq i}^{N} \|\vec{x}_i - \vec{x}_j\|
```

**Exploitation ratio:**

```{math}
R_{exploit} = \frac{\text{Iterations near } \vec{x}_{best}}{\text{Total iterations}}
```

### Performance Metrics

**Convergence rate:**

```{math}
\rho = \frac{\log(f^t - f^*) - \log(f^{t+1} - f^*)}{1}
```

- $\rho > 1$: Superlinear
- $\rho = 1$: Linear
- $\rho < 1$: Sublinear

## Architecture Diagram

```{mermaid}
graph TD
    A[Initialize Population] --> B[Evaluate Fitness]
    B --> C[Update Personal Best]
    C --> D[Update Global Best]
    D --> E[Update Population]
    E --> F[Convergence Check]

    F --> G{Converged?}
    G -->|No| B
    G -->|Yes| H[Return Result]

    F --> I{Max Iterations?}
    I -->|Yes| H
    I -->|No| J{Stagnation?}
    J -->|Yes| K[Diversity Injection]
    K --> B
    J -->|No| B

    style F fill:#ff9
    style G fill:#9cf
    style H fill:#9f9
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

```{literalinclude} ../../../src/optimization/algorithms/base.py
:language: python
:linenos:
```



## Classes

### `OptimizationAlgorithm`

**Inherits from:** `ABC`

Abstract base class for optimization algorithms.

This class defines the common interface that all optimization algorithms
must implement. It provides a standard structure for algorithm initialization,
execution, and result reporting.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/base.py
:language: python
:pyobject: OptimizationAlgorithm
:linenos:
```

#### Methods (7)

##### `__init__(self)`

Initialize the optimization algorithm.

[View full source →](#method-optimizationalgorithm-__init__)

##### `optimize(self, problem, parameter_space)`

Run the optimization algorithm.

[View full source →](#method-optimizationalgorithm-optimize)

##### `get_algorithm_info(self)`

Get information about the algorithm.

[View full source →](#method-optimizationalgorithm-get_algorithm_info)

##### `reset(self)`

Reset the algorithm to initial state.

[View full source →](#method-optimizationalgorithm-reset)

##### `supports_constraints(self)`

Check if algorithm supports constraints.

[View full source →](#method-optimizationalgorithm-supports_constraints)

##### `supports_parallel_evaluation(self)`

Check if algorithm supports parallel function evaluation.

[View full source →](#method-optimizationalgorithm-supports_parallel_evaluation)

##### `get_default_parameters(self)`

Get default algorithm parameters.

[View full source →](#method-optimizationalgorithm-get_default_parameters)



### `PopulationBasedAlgorithm`

**Inherits from:** `OptimizationAlgorithm`

Base class for population-based optimization algorithms.

This class extends OptimizationAlgorithm with common functionality
for algorithms that maintain a population of candidate solutions.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/base.py
:language: python
:pyobject: PopulationBasedAlgorithm
:linenos:
```

#### Methods (4)

##### `__init__(self, population_size)`

Initialize population-based algorithm.

[View full source →](#method-populationbasedalgorithm-__init__)

##### `get_algorithm_info(self)`

Get algorithm information including population details.

[View full source →](#method-populationbasedalgorithm-get_algorithm_info)

##### `reset(self)`

Reset the algorithm including population.

[View full source →](#method-populationbasedalgorithm-reset)

##### `supports_parallel_evaluation(self)`

Population-based algorithms typically support parallel evaluation.

[View full source →](#method-populationbasedalgorithm-supports_parallel_evaluation)



### `GradientBasedAlgorithm`

**Inherits from:** `OptimizationAlgorithm`

Base class for gradient-based optimization algorithms.

This class extends OptimizationAlgorithm with common functionality
for algorithms that use gradient information.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/base.py
:language: python
:pyobject: GradientBasedAlgorithm
:linenos:
```

#### Methods (4)

##### `__init__(self, gradient_tolerance)`

Initialize gradient-based algorithm.

[View full source →](#method-gradientbasedalgorithm-__init__)

##### `get_algorithm_info(self)`

Get algorithm information including gradient details.

[View full source →](#method-gradientbasedalgorithm-get_algorithm_info)

##### `reset(self)`

Reset the algorithm including gradient information.

[View full source →](#method-gradientbasedalgorithm-reset)

##### `requires_gradients(self)`

Check if algorithm requires analytical gradients.

[View full source →](#method-gradientbasedalgorithm-requires_gradients)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, Optional`
- `from ..core.interfaces import OptimizationProblem, ParameterSpace, OptimizationResult`
