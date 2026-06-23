# optimization.core.parameters

**Source:** `src\optimization\core\parameters.py`

## Module Overview

Parameter space definitions and management.



## Advanced Mathematical Theory

### Parameter Space Design

**Continuous parameter space** for $n$ optimization variables:

```{math}
\mathcal{X} = \prod_{i=1}^{n} [l_i, u_i] \subset \mathbb{R}^n
```

Where $l_i, u_i$ are lower and upper bounds for parameter $i$.

### Latin Hypercube Sampling (LHS)

**Stratified sampling** for better space coverage:

```{math}
x_{ij} = \frac{\pi_j(i) - u_{ij}}{N} \cdot (u_j - l_j) + l_j
```

Where:
- $\pi_j$: Random permutation of $\{1, \ldots, N\}$
- $u_{ij} \sim U(0,1)$: Uniform random sample
- $N$: Number of samples

**Advantages:**
- Ensures uniform coverage in each dimension
- Better than pure random sampling for small sample sizes
- $O(N)$ complexity for $N$ samples

### Sobol Sequences

**Quasi-random low-discrepancy sequences:**

```{math}
D_N^* = \sup_{B \in \mathcal{B}} \left| \frac{\#\{x_i \in B\}}{N} - \lambda(B) \right|
```

Where $\lambda(B)$ is Lebesgue measure of box $B$.

**Properties:**
- Discrepancy $D_N^* = O(\frac{(\log N)^n}{N})$
- Better convergence than Monte Carlo
- Deterministic space-filling

### Parameter Scaling

**Normalization to unit hypercube:**

```{math}
x_{norm,i} = \frac{x_i - l_i}{u_i - l_i} \in [0, 1]
```

**Log scaling** for wide-range parameters:

```{math}
x_{log,i} = \log_{10}(x_i), \quad x_i = 10^{x_{log,i}}
```

### Constraint Handling

**Penalty method** for constraints $g_j(\vec{x}) \leq 0$:

```{math}
f_{penalty}(\vec{x}) = f(\vec{x}) + \sum_{j} r_j \max(0, g_j(\vec{x}))^2
```

Where $r_j$ are penalty coefficients.

## Architecture Diagram

```{mermaid}
graph TD
    A[Parameter Definition] --> B{Parameter Type}
    B -->|Continuous| C[Continuous Space]
    B -->|Discrete| D[Discrete Space]
    B -->|Mixed| E[Mixed Space]

    C --> F[Sampling Strategy]
    F -->|Random| G[Uniform Sampling]
    F -->|LHS| H[Latin Hypercube]
    F -->|Quasi-Random| I[Sobol Sequence]

    G --> J[Validation]
    H --> J
    I --> J

    J --> K{Valid?}
    K -->|Yes| L[Sample Output]
    K -->|No| M[Clip to Bounds]
    M --> L

    style B fill:#ff9
    style J fill:#9cf
    style L fill:#9f9
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


## Advanced Mathematical Theory

### Parameter Space Design

**Continuous parameter space** for $n$ optimization variables:

```{math}
\mathcal{X} = \prod_{i=1}^{n} [l_i, u_i] \subset \mathbb{R}^n
```

Where $l_i, u_i$ are lower and upper bounds for parameter $i$.

### Latin Hypercube Sampling (LHS)

**Stratified sampling** for better space coverage:

```{math}
x_{ij} = \frac{\pi_j(i) - u_{ij}}{N} \cdot (u_j - l_j) + l_j
```

Where:
- $\pi_j$: Random permutation of $\{1, \ldots, N\}$
- $u_{ij} \sim U(0,1)$: Uniform random sample
- $N$: Number of samples

**Advantages:**
- Ensures uniform coverage in each dimension
- Better than pure random sampling for small sample sizes
- $O(N)$ complexity for $N$ samples

### Sobol Sequences

**Quasi-random low-discrepancy sequences:**

```{math}
D_N^* = \sup_{B \in \mathcal{B}} \left| \frac{\#\{x_i \in B\}}{N} - \lambda(B) \right|
```

Where $\lambda(B)$ is Lebesgue measure of box $B$.

**Properties:**
- Discrepancy $D_N^* = O(\frac{(\log N)^n}{N})$
- Better convergence than Monte Carlo
- Deterministic space-filling

### Parameter Scaling

**Normalization to unit hypercube:**

```{math}
x_{norm,i} = \frac{x_i - l_i}{u_i - l_i} \in [0, 1]
```

**Log scaling** for wide-range parameters:

```{math}
x_{log,i} = \log_{10}(x_i), \quad x_i = 10^{x_{log,i}}
```

### Constraint Handling

**Penalty method** for constraints $g_j(\vec{x}) \leq 0$:

```{math}
f_{penalty}(\vec{x}) = f(\vec{x}) + \sum_{j} r_j \max(0, g_j(\vec{x}))^2
```

Where $r_j$ are penalty coefficients.

## Architecture Diagram

```{mermaid}
graph TD
    A[Parameter Definition] --> B{Parameter Type}
    B -->|Continuous| C[Continuous Space]
    B -->|Discrete| D[Discrete Space]
    B -->|Mixed| E[Mixed Space]

    C --> F[Sampling Strategy]
    F -->|Random| G[Uniform Sampling]
    F -->|LHS| H[Latin Hypercube]
    F -->|Quasi-Random| I[Sobol Sequence]

    G --> J[Validation]
    H --> J
    I --> J

    J --> K{Valid?}
    K -->|Yes| L[Sample Output]
    K -->|No| M[Clip to Bounds]
    M --> L

    style B fill:#ff9
    style J fill:#9cf
    style L fill:#9f9
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

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:linenos:
```



## Classes

### `Parameter`

**Inherits from:** `ABC`

Abstract base class for optimization parameters.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: Parameter
:linenos:
```

#### Methods (5)

##### `__init__(self, name, description)`

Initialize parameter.

[View full source →](#method-parameter-__init__)

##### `sample(self, n_samples, rng)`

Sample values from parameter domain.

[View full source →](#method-parameter-sample)

##### `validate(self, value)`

Validate parameter value(s).

[View full source →](#method-parameter-validate)

##### `clip(self, value)`

Clip value(s) to valid range.

[View full source →](#method-parameter-clip)

##### `bounds(self)`

Parameter bounds (lower, upper).

[View full source →](#method-parameter-bounds)



### `ContinuousParameter`

**Inherits from:** `Parameter`

Continuous real-valued parameter.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: ContinuousParameter
:linenos:
```

#### Methods (5)

##### `__init__(self, name, lower, upper, description, log_scale)`

Initialize continuous parameter.

[View full source →](#method-continuousparameter-__init__)

##### `sample(self, n_samples, rng)`

Sample from uniform distribution.

[View full source →](#method-continuousparameter-sample)

##### `validate(self, value)`

Check if value is within bounds.

[View full source →](#method-continuousparameter-validate)

##### `clip(self, value)`

Clip to bounds.

[View full source →](#method-continuousparameter-clip)

##### `bounds(self)`

Parameter bounds.

[View full source →](#method-continuousparameter-bounds)



### `DiscreteParameter`

**Inherits from:** `Parameter`

Discrete parameter with finite set of values.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: DiscreteParameter
:linenos:
```

#### Methods (6)

##### `__init__(self, name, values, description)`

Initialize discrete parameter.

[View full source →](#method-discreteparameter-__init__)

##### `sample(self, n_samples, rng)`

Sample from discrete values.

[View full source →](#method-discreteparameter-sample)

##### `validate(self, value)`

Check if value is in allowed set.

[View full source →](#method-discreteparameter-validate)

##### `clip(self, value)`

Find closest valid value.

[View full source →](#method-discreteparameter-clip)

##### `_find_closest(self, value)`

Find closest valid value.

[View full source →](#method-discreteparameter-_find_closest)

##### `bounds(self)`

Bounds for discrete parameter (min and max values).

[View full source →](#method-discreteparameter-bounds)



### `ContinuousParameterSpace`

**Inherits from:** `ParameterSpace`

Continuous parameter space with box constraints.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: ContinuousParameterSpace
:linenos:
```

#### Methods (7)

##### `__init__(self, lower_bounds, upper_bounds, names)`

Initialize continuous parameter space.

[View full source →](#method-continuousparameterspace-__init__)

##### `sample(self, n_samples, rng)`

Sample uniformly from parameter space.

[View full source →](#method-continuousparameterspace-sample)

##### `validate(self, parameters)`

Check if parameters are within bounds.

[View full source →](#method-continuousparameterspace-validate)

##### `clip(self, parameters)`

Clip parameters to bounds.

[View full source →](#method-continuousparameterspace-clip)

##### `dimensions(self)`

Number of parameters.

[View full source →](#method-continuousparameterspace-dimensions)

##### `bounds(self)`

Parameter bounds.

[View full source →](#method-continuousparameterspace-bounds)

##### `get_parameter_info(self)`

Get information about each parameter.

[View full source →](#method-continuousparameterspace-get_parameter_info)



### `MixedParameterSpace`

**Inherits from:** `ParameterSpace`

Mixed parameter space with continuous and discrete parameters.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: MixedParameterSpace
:linenos:
```

#### Methods (6)

##### `__init__(self, parameters)`

Initialize mixed parameter space.

[View full source →](#method-mixedparameterspace-__init__)

##### `sample(self, n_samples, rng)`

Sample from mixed parameter space.

[View full source →](#method-mixedparameterspace-sample)

##### `validate(self, parameters)`

Validate mixed parameters.

[View full source →](#method-mixedparameterspace-validate)

##### `clip(self, parameters)`

Clip mixed parameters.

[View full source →](#method-mixedparameterspace-clip)

##### `dimensions(self)`

Number of parameters.

[View full source →](#method-mixedparameterspace-dimensions)

##### `bounds(self)`

Parameter bounds.

[View full source →](#method-mixedparameterspace-bounds)



### `ParameterBounds`

Helper class for parameter bounds management.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: ParameterBounds
:linenos:
```

#### Methods (4)

##### `__init__(self, lower, upper, names)`

Initialize parameter bounds.

[View full source →](#method-parameterbounds-__init__)

##### `to_parameter_space(self)`

Convert to continuous parameter space.

[View full source →](#method-parameterbounds-to_parameter_space)

##### `scale_to_unit(self, parameters)`

Scale parameters to unit cube [0,1]^n.

[View full source →](#method-parameterbounds-scale_to_unit)

##### `scale_from_unit(self, unit_parameters)`

Scale parameters from unit cube to original bounds.

[View full source →](#method-parameterbounds-scale_from_unit)



### `ParameterMapping`

Maps between different parameter representations.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: ParameterMapping
:linenos:
```

#### Methods (3)

##### `__init__(self, parameter_space)`

Initialize parameter mapping.

[View full source →](#method-parametermapping-__init__)

##### `to_dict(self, parameters)`

Convert parameter array to dictionary.

[View full source →](#method-parametermapping-to_dict)

##### `from_dict(self, param_dict)`

Convert parameter dictionary to array.

[View full source →](#method-parametermapping-from_dict)



### `ParameterValidator`

Validates optimization parameters.

#### Source Code

```{literalinclude} ../../../src/optimization/core/parameters.py
:language: python
:pyobject: ParameterValidator
:linenos:
```

#### Methods (3)

##### `__init__(self, parameter_space)`

Initialize parameter validator.

[View full source →](#method-parametervalidator-__init__)

##### `validate_single(self, parameters)`

Validate single parameter vector.

[View full source →](#method-parametervalidator-validate_single)

##### `validate_batch(self, parameters)`

Validate batch of parameter vectors.

[View full source →](#method-parametervalidator-validate_batch)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, List, Optional, Tuple, Union`
- `import numpy as np`
- `from .interfaces import ParameterSpace`
