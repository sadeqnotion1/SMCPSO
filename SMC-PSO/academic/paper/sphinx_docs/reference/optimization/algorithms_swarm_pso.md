# optimization.algorithms.swarm.pso

**Source:** `src\optimization\algorithms\swarm\pso.py`

## Module Overview

Enhanced Particle Swarm Optimization with framework integration.



## Advanced Mathematical Theory

### Particle Swarm Optimization (PSO)

**Core PSO equations** for particle $i$ in dimension $d$:

**Velocity update:**

```{math}
v_{i,d}^{t+1} = w v_{i,d}^t + c_1 r_1 (p_{i,d} - x_{i,d}^t) + c_2 r_2 (g_d - x_{i,d}^t)
```

**Position update:**

```{math}
x_{i,d}^{t+1} = x_{i,d}^t + v_{i,d}^{t+1}
```

Where:
- $w$: Inertia weight
- $c_1, c_2$: Cognitive and social coefficients
- $r_1, r_2 \sim U(0,1)$: Random numbers
- $p_{i,d}$: Personal best position
- $g_d$: Global best position

### Inertia Weight Strategies

**Linear decrease:**

```{math}
w(t) = w_{max} - \frac{w_{max} - w_{min}}{T_{max}} \cdot t
```

**Adaptive (Clerc):**

```{math}
w(t) = w_{min} + (w_{max} - w_{min}) \cdot \frac{f_{avg} - f_i}{f_{max} - f_{avg}}
```

**Chaotic:**

```{math}
w(t) = w_{min} + (w_{max} - w_{min}) \cdot \frac{4 z_t (1 - z_t)}{1}, \quad z_{t+1} = 4 z_t (1 - z_t)
```

### Constriction Factor

**Clerc and Kennedy constriction:**

```{math}
\chi = \frac{2}{\left| 2 - \phi - \sqrt{\phi^2 - 4\phi} \right|}, \quad \phi = c_1 + c_2 > 4
```

**Modified velocity update:**

```{math}
v_{i,d}^{t+1} = \chi \left[ v_{i,d}^t + c_1 r_1 (p_{i,d} - x_{i,d}^t) + c_2 r_2 (g_d - x_{i,d}^t) \right]
```

**Ensures convergence** with $\chi \approx 0.729, \phi = 4.1$.

### Velocity Clamping

**Component-wise clamping:**

```{math}
v_{i,d}^{t+1} = \begin{cases}
v_{max,d}, & v_{i,d}^{t+1} > v_{max,d} \\
v_{min,d}, & v_{i,d}^{t+1} < v_{min,d} \\
v_{i,d}^{t+1}, & \text{otherwise}
\end{cases}
```

Typical: $v_{max,d} = 0.2(u_d - l_d)$

### Boundary Handling

**Reflecting boundary:**

```{math}
x_{i,d}^{t+1} = \begin{cases}
2l_d - x_{i,d}^{t+1}, & x_{i,d}^{t+1} < l_d \\
2u_d - x_{i,d}^{t+1}, & x_{i,d}^{t+1} > u_d \\
x_{i,d}^{t+1}, & \text{otherwise}
\end{cases}
```

**Absorbing boundary:**

```{math}
x_{i,d}^{t+1} = \max(l_d, \min(u_d, x_{i,d}^{t+1})), \quad v_{i,d}^{t+1} = 0
```

### Convergence Criteria

**Diversity-based:**

```{math}
\text{Diversity} = \frac{1}{N} \sum_{i=1}^{N} \|\vec{x}_i - \bar{\vec{x}}\| < \epsilon_d
```

**Fitness-based:**

```{math}
|f(\vec{g}^{t+1}) - f(\vec{g}^t)| < \epsilon_f
```

## Architecture Diagram

```{mermaid}
graph TD
    A[Initialize Swarm] --> B[Evaluate Fitness]
    B --> C[Update Personal Best]
    C --> D[Update Global Best]
    D --> E[Update Velocities]

    E --> F{Velocity Clamping}
    F -->|Exceed Max| G[Clamp Velocity]
    F -->|Within Bounds| H[Update Positions]
    G --> H

    H --> I{Boundary Check}
    I -->|Out of Bounds| J[Reflect/Absorb]
    I -->|Within Bounds| K[Convergence Check]
    J --> K

    K --> L{Converged?}
    L -->|No| B
    L -->|Yes| M[Return Best Particle]

    style E fill:#9cf
    style K fill:#ff9
    style M fill:#9f9
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

```{literalinclude} ../../../src/optimization/algorithms/swarm/pso.py
:language: python
:linenos:
```



## Classes

### `ParticleSwarmOptimizer`

**Inherits from:** `PopulationBasedOptimizer`

Professional Particle Swarm Optimization algorithm.

This implementation provides a modern, framework-integrated PSO algorithm
with advanced features for control engineering applications.

#### Source Code

```{literalinclude} ../../../src/optimization/algorithms/swarm/pso.py
:language: python
:pyobject: ParticleSwarmOptimizer
:linenos:
```

#### Methods (15)

##### `__init__(self, parameter_space, population_size, inertia_weight, cognitive_weight, social_weight, max_iterations, tolerance, adaptive_weights, velocity_clamping)`

Initialize PSO optimizer.

[View full source →](#method-particleswarmoptimizer-__init__)

##### `algorithm_name(self)`

Algorithm name.

[View full source →](#method-particleswarmoptimizer-algorithm_name)

##### `supports_constraints(self)`

PSO can handle constraints through penalty methods.

[View full source →](#method-particleswarmoptimizer-supports_constraints)

##### `supports_bounds(self)`

PSO naturally supports parameter bounds.

[View full source →](#method-particleswarmoptimizer-supports_bounds)

##### `optimize(self, problem)`

Perform PSO optimization.

[View full source →](#method-particleswarmoptimizer-optimize)

##### `initialize_population(self, rng)`

Initialize particle positions and velocities.

[View full source →](#method-particleswarmoptimizer-initialize_population)

##### `update_population(self, population, fitness)`

Update population (used by base class interface).

[View full source →](#method-particleswarmoptimizer-update_population)

##### `_update_velocities(self, rng)`

Update particle velocities.

[View full source →](#method-particleswarmoptimizer-_update_velocities)

##### `_update_positions(self)`

Update particle positions.

[View full source →](#method-particleswarmoptimizer-_update_positions)

##### `_update_personal_bests(self, fitness)`

Update personal best positions and fitness.

[View full source →](#method-particleswarmoptimizer-_update_personal_bests)

##### `_update_global_best(self)`

Update global best position and fitness.

[View full source →](#method-particleswarmoptimizer-_update_global_best)

##### `_update_adaptive_parameters(self, iteration, max_iterations)`

Update PSO parameters adaptively.

[View full source →](#method-particleswarmoptimizer-_update_adaptive_parameters)

##### `_calculate_diversity(self)`

Calculate swarm diversity.

[View full source →](#method-particleswarmoptimizer-_calculate_diversity)

##### `_apply_constraint_penalties(self, fitness, problem)`

Apply constraint penalties to fitness values.

[View full source →](#method-particleswarmoptimizer-_apply_constraint_penalties)

##### `get_swarm_statistics(self)`

Get detailed swarm statistics.

[View full source →](#method-particleswarmoptimizer-get_swarm_statistics)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `from typing import Any, Callable, Dict, Optional, Tuple`
- `import logging`
- `from ...core.interfaces import PopulationBasedOptimizer, OptimizationProblem, OptimizationResult, ConvergenceStatus, ParameterSpace`
