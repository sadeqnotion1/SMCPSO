# optimization.algorithms.gradient_based.nelder_mead

**Source:** `src\optimization\algorithms\gradient_based\nelder_mead.py`

## Module Overview

Nelder-Mead simplex optimization algorithm.



## Advanced Mathematical Theory

### Nelder-Mead Simplex Method

**Simplex:** Set of $n+1$ vertices in $\mathbb{R}^n$:

```{math}
S = \{\vec{x}_1, \ldots, \vec{x}_{n+1}\}
```

**Centroid** of best $n$ vertices:

```{math}
\bar{\vec{x}} = \frac{1}{n} \sum_{i=1}^{n} \vec{x}_i \quad (\text{excluding worst})
```

### Simplex Operations

**Reflection:**

```{math}
\vec{x}_r = \bar{\vec{x}} + \alpha (\bar{\vec{x}} - \vec{x}_{n+1}), \quad \alpha = 1
```

**Expansion:**

```{math}
\vec{x}_e = \bar{\vec{x}} + \gamma (\vec{x}_r - \bar{\vec{x}}), \quad \gamma = 2
```

**Contraction (outside):**

```{math}
\vec{x}_c = \bar{\vec{x}} + \rho (\vec{x}_r - \bar{\vec{x}}), \quad \rho = 0.5
```

**Contraction (inside):**

```{math}
\vec{x}_{cc} = \bar{\vec{x}} - \rho (\bar{\vec{x}} - \vec{x}_{n+1}), \quad \rho = 0.5
```

**Shrink:**

```{math}
\vec{x}_i = \vec{x}_1 + \sigma (\vec{x}_i - \vec{x}_1), \quad \sigma = 0.5, \, i = 2, \ldots, n+1
```

### Algorithm Flow

```
1. Sort: f(x_1) ≤ f(x_2) ≤ ... ≤ f(x_{n+1})
2. Reflect: x_r = centroid + α(centroid - x_{worst})
3. If f(x_1) ≤ f(x_r) < f(x_n): Accept reflection
4. If f(x_r) < f(x_1): Try expansion
5. If f(x_r) ≥ f(x_n): Try contraction
6. If contraction fails: Shrink simplex
```

### Convergence Properties

**Theorem (Lagarias et al. 1998):** For strictly convex $f$ with bounded level sets:

```{math}
\lim_{k \to \infty} \text{diam}(S_k) = 0
```

**Limitation:** May converge to non-stationary points for non-convex functions.

## Architecture Diagram

```{mermaid}
graph TD
    A[Simplex] --> B[Sort Vertices]
    B --> C[Compute Centroid]
    C --> D[Reflection]

    D --> E{f(x_r) Quality}
    E -->|Best| F[Try Expansion]
    E -->|Good| G[Accept Reflection]
    E -->|Poor| H[Try Contraction]

    F --> I{f(x_e) < f(x_r)?}
    I -->|Yes| J[Accept Expansion]
    I -->|No| G

    H --> K{Outside or Inside?}
    K -->|Outside| L[Contract Outside]
    K -->|Inside| M[Contract Inside]

    L --> N{Accept Contraction?}
    M --> N
    N -->|Yes| O[Update Simplex]
    N -->|No| P[Shrink All]

    G --> O
    J --> O
    P --> O

    O --> Q{Converged?}
    Q -->|No| B
    Q -->|Yes| R[Return Best]

    style E fill:#ff9
    style K fill:#9cf
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

```{literalinclude} ../../../src/optimization/algorithms/gradient_based/nelder_mead.py
:language: python
:linenos:
```



## Classes

### `NelderMeadConfig`

Configuration for Nelder-Mead algorithm.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/gradient_based/nelder_mead.py
:language: python
:pyobject: NelderMeadConfig
:linenos:
```



### `NelderMeadSimplex`

Nelder-Mead simplex data structure.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/gradient_based/nelder_mead.py
:language: python
:pyobject: NelderMeadSimplex
:linenos:
```

#### Methods (12)

##### `__init__(self, vertices, function_values)`

[View full source →](#method-neldermeadsimplex-__init__)

##### `_sort_vertices(self)`

Sort vertices by function value (best first).

[View full source →](#method-neldermeadsimplex-_sort_vertices)

##### `best_vertex(self)`

Get the best vertex.

[View full source →](#method-neldermeadsimplex-best_vertex)

##### `best_value(self)`

Get the best function value.

[View full source →](#method-neldermeadsimplex-best_value)

##### `worst_vertex(self)`

Get the worst vertex.

[View full source →](#method-neldermeadsimplex-worst_vertex)

##### `worst_value(self)`

Get the worst function value.

[View full source →](#method-neldermeadsimplex-worst_value)

##### `second_worst_vertex(self)`

Get the second worst vertex.

[View full source →](#method-neldermeadsimplex-second_worst_vertex)

##### `second_worst_value(self)`

Get the second worst function value.

[View full source →](#method-neldermeadsimplex-second_worst_value)

##### `centroid(self, exclude_worst)`

Calculate centroid of simplex.

[View full source →](#method-neldermeadsimplex-centroid)

##### `replace_worst(self, new_vertex, new_value)`

Replace worst vertex with new vertex.

[View full source →](#method-neldermeadsimplex-replace_worst)

##### `shrink_simplex(self, shrinkage_coeff)`

Shrink simplex towards best vertex.

[View full source →](#method-neldermeadsimplex-shrink_simplex)

##### `volume(self)`

Calculate simplex volume.

[View full source →](#method-neldermeadsimplex-volume)



### `NelderMead`

**Inherits from:** `OptimizationAlgorithm`

Nelder-Mead simplex optimization algorithm.

The Nelder-Mead algorithm is a direct search method that uses a simplex
(n+1 vertices in n dimensions) to navigate the parameter space. It uses
reflection, expansion, contraction, and shrinkage operations to adapt
the simplex shape and converge to the optimum.

Features:
- Derivative-free optimization
- Adaptive simplex operations
- Boundary constraint handling
- Convergence detection
- Robust parameter adaptation

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/gradient_based/nelder_mead.py
:language: python
:pyobject: NelderMead
:linenos:
```

#### Methods (17)

##### `__init__(self, config)`

Initialize Nelder-Mead algorithm.

[View full source →](#method-neldermead-__init__)

##### `optimize(self, problem, parameter_space, initial_guess)`

Run Nelder-Mead optimization.

[View full source →](#method-neldermead-optimize)

##### `_initialize_simplex(self, initial_guess)`

Initialize the simplex.

[View full source →](#method-neldermead-_initialize_simplex)

##### `_perform_iteration(self)`

Perform one iteration of Nelder-Mead algorithm.

[View full source →](#method-neldermead-_perform_iteration)

##### `_reflect(self, centroid, worst_vertex)`

Perform reflection operation.

[View full source →](#method-neldermead-_reflect)

##### `_expand(self, centroid, reflected_point)`

Perform expansion operation.

[View full source →](#method-neldermead-_expand)

##### `_contract_outside(self, centroid, reflected_point)`

Perform outside contraction.

[View full source →](#method-neldermead-_contract_outside)

##### `_contract_inside(self, centroid, worst_vertex)`

Perform inside contraction.

[View full source →](#method-neldermead-_contract_inside)

##### `_shrink_simplex(self)`

Shrink the entire simplex.

[View full source →](#method-neldermead-_shrink_simplex)

##### `_apply_bounds(self, point)`

Apply parameter bounds to a point.

[View full source →](#method-neldermead-_apply_bounds)

##### `_safe_evaluate(self, point)`

Safely evaluate objective function.

[View full source →](#method-neldermead-_safe_evaluate)

##### `_update_adaptive_parameters(self)`

Update adaptive algorithm parameters.

[View full source →](#method-neldermead-_update_adaptive_parameters)

##### `_check_termination(self)`

Check termination conditions.

[View full source →](#method-neldermead-_check_termination)

##### `_create_result(self)`

Create optimization result.

[View full source →](#method-neldermead-_create_result)

##### `get_simplex_info(self)`

Get information about current simplex.

[View full source →](#method-neldermead-get_simplex_info)

##### `_estimate_convergence_rate(self)`

Estimate convergence rate.

[View full source →](#method-neldermead-_estimate_convergence_rate)

##### `restart_simplex(self, perturbation_factor)`

Restart simplex with perturbation.

[View full source →](#method-neldermead-restart_simplex)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, List, Optional, Callable, Tuple`
- `import numpy as np`
- `import warnings`
- `from dataclasses import dataclass`
- `from ..base import OptimizationAlgorithm`
- `from ...core.interfaces import OptimizationProblem, ParameterSpace, OptimizationResult`
- `from ...core.parameters import ContinuousParameterSpace`
