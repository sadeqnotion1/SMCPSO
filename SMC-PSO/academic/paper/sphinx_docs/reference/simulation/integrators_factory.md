# simulation.integrators.factory

**Source:** `src\simulation\integrators\factory.py`

## Module Overview

Integrator Factory for creating numerical integration instances.

This module provides a factory pattern for instantiating different types
of numerical integrators with proper configuration and parameter management.


## Mathematical Foundation

### Integrator Factory Pattern

Centralized creation and configuration of numerical integrators.

### Factory Method Pattern

**Intent:** Define an interface for creating integrators without specifying concrete classes.

```{math}
\text{Factory}: (\text{method\_name}, \text{config}) \mapsto \text{Integrator}
```

### Supported Integration Methods

**1. Euler (1st order)**
```{math}
x_{n+1} = x_n + \Delta t \cdot f(x_n, u_n, t_n)
```

**2. Midpoint (RK2, 2nd order)**
```{math}
\begin{align}
k_1 &= f(x_n, u_n, t_n) \\
x_{n+1} &= x_n + \Delta t \cdot f(x_n + \tfrac{\Delta t}{2} k_1, u_n, t_n + \tfrac{\Delta t}{2})
\end{align}
```

**3. RK4 (4th order)**
```{math}
x_{n+1} = x_n + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)
```

**4. RK45 (Dormand-Prince, adaptive 5th order)**
Embedded 4(5) pair with automatic error control

**5. Custom Methods**
User-defined integrators via registration

### Configuration Schema

```python
IntegratorConfig = {
    'method': str,           # 'euler', 'rk2', 'rk4', 'rk45'
    'dt': float,             # Fixed step size (for fixed-step methods)
    'rtol': float,           # Relative tolerance (adaptive only)
    'atol': float,           # Absolute tolerance (adaptive only)
    'min_step': float,       # Minimum step size (adaptive only)
    'max_step': float,       # Maximum step size (adaptive only)
    'safety_factor': float,  # Step size safety factor (adaptive only)
}
```

### Method Selection Criteria

**Accuracy Requirements:**
- Low (research prototyping): Euler
- Medium (standard simulations): RK4
- High (scientific validation): RK45

**Computational Budget:**
- Real-time: Euler, RK2
- Offline: RK4, RK45

**Stiffness:**
- Non-stiff: Explicit methods (Euler, RK2, RK4, RK45)
- Stiff: Implicit methods (not implemented in standard factory)

### Factory Implementation Pattern

```python
# example-metadata:
# runnable: false

class IntegratorFactory:
    _registry = {}

    @classmethod
    def register(cls, name, integrator_class):
        cls._registry[name] = integrator_class

    @classmethod
    def create(cls, method_name, config):
        if method_name not in cls._registry:
            raise ValueError(f"Unknown integrator: {method_name}")
        return cls._registry[method_name](config)
```

## Extensibility

**Adding custom integrators:**

1. Inherit from `BaseIntegrator`
2. Implement required methods
3. Register with factory

```python
factory.register('my_method', MyCustomIntegrator)
integrator = factory.create('my_method', config)
```

### Performance Comparison

| Method | Order | Cost/Step | Accuracy | Adaptive | Best For |
|--------|-------|-----------|----------|----------|----------|
| Euler  | 1     | 1×        | Low      | No       | Real-time |
| RK2    | 2     | 2×        | Medium   | No       | Fast sims |
| RK4    | 4     | 4×        | High     | No       | Standard |
| RK45   | 5     | ~6×       | Very High | Yes     | Scientific |

## Architecture Diagram

```{mermaid}
graph LR
    A[Input] --> B[Integrators Processing]
    B --> C[Output]

    style B fill:#9cf
    style C fill:#9f9
```

## Usage Examples

### Example 1: Basic Usage

```python
from src.simulation.integrators import IntegratorsFactory

# Initialize
instance = IntegratorsFactory()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = IntegratorsFactory(config)
result = instance.process(data)
```

## Example 3: Error Handling

```python
try:
    result = instance.process(data)
except Exception as e:
    print(f"Error: {e}")
```

### Example 4: Performance Profiling

```python
import time
start = time.time()
result = instance.process(data)
elapsed = time.time() - start
print(f"Execution time: {elapsed:.4f} s")
```

### Example 5: Integration with Other Components

```python
# Combine with other simulation components
result = orchestrator.execute(instance.process(data))
```

## Complete Source Code

```{literalinclude} ../../../src/simulation/integrators/factory.py
:language: python
:linenos:
```



## Classes

### `IntegratorFactory`

Factory for creating numerical integrator instances.

Provides centralized creation and management of integrators
with validation and consistency checking.

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/factory.py
:language: python
:pyobject: IntegratorFactory
:linenos:
```

#### Methods (5)

##### `create_integrator(cls, integrator_type, dt)`

Create an integrator instance of the specified type.

[View full source →](#method-integratorfactory-create_integrator)

##### `list_available_integrators(cls)`

Get list of available integrator types.

[View full source →](#method-integratorfactory-list_available_integrators)

##### `get_integrator_info(cls, integrator_type)`

Get information about an integrator type.

[View full source →](#method-integratorfactory-get_integrator_info)

##### `register_integrator(cls, name, integrator_class)`

Register a custom integrator class.

[View full source →](#method-integratorfactory-register_integrator)

##### `create_default_integrator(cls, dt)`

Create a default integrator instance.

[View full source →](#method-integratorfactory-create_default_integrator)



## Functions

### `create_integrator(integrator_type, dt)`

Create integrator instance (convenience function).

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/factory.py
:language: python
:pyobject: create_integrator
:linenos:
```



### `get_available_integrators()`

Get available integrator types (convenience function).

#### Source Code

```{literalinclude} ../../../src/simulation/integrators/factory.py
:language: python
:pyobject: get_available_integrators
:linenos:
```



## Dependencies

This module imports:

- `from typing import Dict, Type, Any, Optional, Union`
- `import logging`
- `from .base import BaseIntegrator`
- `from .fixed_step.euler import ForwardEuler, BackwardEuler`
- `from .fixed_step.runge_kutta import RungeKutta4, RungeKutta2`
- `from .adaptive.runge_kutta import AdaptiveRungeKutta, DormandPrince45`
- `from .discrete.zero_order_hold import ZeroOrderHold`
