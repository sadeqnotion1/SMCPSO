# optimization.algorithms.gradient_based.bfgs

**Source:** `src\optimization\algorithms\gradient_based\bfgs.py`

## Module Overview

BFGS quasi-Newton optimization algorithm with numerical gradients.



## Advanced Mathematical Theory

### BFGS Quasi-Newton Method

**Quasi-Newton update:**

```{math}
\vec{x}^{t+1} = \vec{x}^t - \alpha_t B_k^{-1} \nabla f(\vec{x}^t)
```

Where $B_k$ approximates Hessian $\nabla^2 f$.

### Hessian Approximation

**BFGS update formula:**

```{math}
B_{k+1} = B_k + \frac{y_k y_k^T}{y_k^T s_k} - \frac{B_k s_k s_k^T B_k}{s_k^T B_k s_k}
```

Where:
- $s_k = \vec{x}^{k+1} - \vec{x}^k$: Step
- $y_k = \nabla f(\vec{x}^{k+1}) - \nabla f(\vec{x}^k)$: Gradient change

**Inverse Hessian update** (more efficient):

```{math}
H_{k+1} = \left(I - \frac{s_k y_k^T}{y_k^T s_k}\right) H_k \left(I - \frac{y_k s_k^T}{y_k^T s_k}\right) + \frac{s_k s_k^T}{y_k^T s_k}
```

### Line Search

**Wolfe conditions** for step size $\alpha$:

```{math}
\begin{align}
f(\vec{x}^k + \alpha \vec{p}_k) &\leq f(\vec{x}^k) + c_1 \alpha \nabla f(\vec{x}^k)^T \vec{p}_k \quad \text{(Armijo)} \\
\nabla f(\vec{x}^k + \alpha \vec{p}_k)^T \vec{p}_k &\geq c_2 \nabla f(\vec{x}^k)^T \vec{p}_k \quad \text{(Curvature)}
\end{align}
```

Typical: $c_1 = 10^{-4}, c_2 = 0.9$.

### Convergence Analysis

**Theorem (Dennis & Moré):** If $\nabla^2 f$ is Lipschitz continuous and $\nabla^2 f(\vec{x}^*)$ positive definite:

```{math}
\|\vec{x}^{k+1} - \vec{x}^*\| = O(\|\vec{x}^k - \vec{x}^*\|^{1+\mu})
```

**Superlinear convergence** with $\mu \in (0, 1]$.

### Limited-Memory BFGS (L-BFGS)

**Store only last $m$ updates:**

```{math}
M_{storage} = O(m \cdot n) \quad \text{vs} \quad O(n^2) \text{ for full BFGS}
```

Typical: $m = 5$ to $20$.

## Architecture Diagram

```{mermaid}
graph TD
    A[Current Point x] --> B[Compute Gradient]
    B --> C[Compute Search Direction]
    C --> D[p = -H * grad_f]

    D --> E[Line Search]
    E --> F{Wolfe Conditions}
    F -->|Not Met| G[Reduce Step Size]
    F -->|Met| H[Update x]

    G --> E
    H --> I[Compute s and y]
    I --> J[Update Hessian Approx]

    J --> K{BFGS Update}
    K -->|Full| L[Update n×n H]
    K -->|L-BFGS| M[Store m vectors]

    L --> N[Convergence Check]
    M --> N

    N --> O{||grad_f|| < ε?}
    O -->|No| B
    O -->|Yes| P[Return x]

    style F fill:#ff9
    style K fill:#9cf
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

```{literalinclude} ../../../src/optimization/algorithms/gradient_based/bfgs.py
:language: python
:linenos:
```



## Classes

### `BFGSConfig`

Configuration for BFGS algorithm.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/gradient_based/bfgs.py
:language: python
:pyobject: BFGSConfig
:linenos:
```



### `BFGSOptimizer`

**Inherits from:** `OptimizationAlgorithm`

BFGS quasi-Newton optimization algorithm.

The BFGS (Broyden-Fletcher-Goldfarb-Shanno) algorithm is a quasi-Newton
method that approximates the Hessian matrix using gradient information.
It builds up curvature information iteratively to achieve superlinear
convergence near the optimum.

Features:
- Numerical gradient computation (forward, backward, central differences)
- Line search with Wolfe conditions
- Hessian approximation updates
- Boundary constraint handling
- Robust convergence criteria

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/gradient_based/bfgs.py
:language: python
:pyobject: BFGSOptimizer
:linenos:
```

#### Methods (16)

##### `__init__(self, config)`

Initialize BFGS algorithm.

[View full source →](#method-bfgsoptimizer-__init__)

##### `optimize(self, problem, parameter_space, initial_guess)`

Run BFGS optimization.

[View full source →](#method-bfgsoptimizer-optimize)

##### `_initialize_optimization(self, initial_guess)`

Initialize optimization state.

[View full source →](#method-bfgsoptimizer-_initialize_optimization)

##### `_perform_iteration(self)`

Perform one BFGS iteration.

[View full source →](#method-bfgsoptimizer-_perform_iteration)

##### `_compute_numerical_gradient(self, x)`

Compute numerical gradient using finite differences.

[View full source →](#method-bfgsoptimizer-_compute_numerical_gradient)

##### `_update_hessian_inverse(self, x_old, x_new, grad_old, grad_new)`

Update inverse Hessian approximation using BFGS formula.

[View full source →](#method-bfgsoptimizer-_update_hessian_inverse)

##### `_line_search(self, x, f, gradient, direction)`

Line search with Wolfe conditions.

[View full source →](#method-bfgsoptimizer-_line_search)

##### `_safe_evaluate(self, x)`

Safely evaluate objective function.

[View full source →](#method-bfgsoptimizer-_safe_evaluate)

##### `_check_termination(self)`

Check termination conditions.

[View full source →](#method-bfgsoptimizer-_check_termination)

##### `_create_result(self)`

Create optimization result.

[View full source →](#method-bfgsoptimizer-_create_result)

##### `_compute_hessian_condition_number(self)`

Compute condition number of Hessian approximation.

[View full source →](#method-bfgsoptimizer-_compute_hessian_condition_number)

##### `get_optimization_info(self)`

Get detailed optimization information.

[View full source →](#method-bfgsoptimizer-get_optimization_info)

##### `_estimate_convergence_rate(self)`

Estimate convergence rate from function value history.

[View full source →](#method-bfgsoptimizer-_estimate_convergence_rate)

##### `reset_hessian(self)`

Reset Hessian approximation to identity.

[View full source →](#method-bfgsoptimizer-reset_hessian)

##### `get_hessian_eigenvalues(self)`

Get eigenvalues of current Hessian approximation.

[View full source →](#method-bfgsoptimizer-get_hessian_eigenvalues)

##### `get_search_direction(self)`

Get current search direction.

[View full source →](#method-bfgsoptimizer-get_search_direction)



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
