# plant.models.base.dynamics_interface

<!-- Enhanced by Week 8 Phase 2 -->


**Source:** `src\plant\models\base\dynamics_interface.py`

## Module Overview

Common interface for plant dynamics models.

Defines abstract base classes and protocols that ensure consistency
across different dynamics implementations (simplified, full, low-rank).



## Architecture Diagram

```{mermaid}
graph TB
    A[DynamicsInterface_ABC_] --> B[SimplifiedDIPDynamics]
    A --> C[FullNonlinearDIPDynamics]
    A --> D[LowRankDIPDynamics]
    E[Controller] --> A
    F[SimulationRunner] --> A

    style A fill:#f9f
    style E fill:#9cf
    style F fill:#fcf
```



## Enhanced Mathematical Foundation

### Abstract Base Class Pattern

The `DynamicsInterface` defines the **contract** that all dynamics models must satisfy:

$$
\text{DynamicsInterface} : (x, u, t) \mapsto \dot{x}
$$

**Required Methods:**

```python
class DynamicsInterface(ABC):
    @abstractmethod
    def step(self, x: np.ndarray, u: np.ndarray, t: float) -> np.ndarray:
        """Compute state derivative dx/dt = f(x, u, t)."""
        pass

    @abstractmethod
    def get_linearization(self, x_eq: np.ndarray, u_eq: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute Jacobian matrices A, B at equilibrium."""
        pass
```

### Polymorphism Benefits

**1. Controller Independence:**

Controllers depend on interface, not concrete implementations:

```python
class SMCController:
    def __init__(self, dynamics: DynamicsInterface):
        self.dynamics = dynamics  # Works with any implementation
```

**2. Model Swapping:**

Easy switching between simplified/full/lowrank models:

```python
# Simplified for development
dynamics = SimplifiedDIPDynamics(config)

# Full for validation
dynamics = FullNonlinearDIPDynamics(config)

# Controller code unchanged!
controller.set_dynamics(dynamics)
```

**3. Testing with Mocks:**

Mock dynamics for unit tests:

```python
class MockDynamics(DynamicsInterface):
    def step(self, x, u, t):
        return np.zeros_like(x)  # Trivial for testing
```

## Linearization Theory

**Jacobian Matrices:**

Compute local linear approximation:

$$
\delta \dot{x} \approx A \delta x + B \delta u
$$

where:

$$
A = \left.\frac{\partial f}{\partial x}\right|_{(x_{eq}, u_{eq})}, \quad B = \left.\frac{\partial f}{\partial u}\right|_{(x_{eq}, u_{eq})}
$$

**Equilibrium Point:**

$$
f(x_{eq}, u_{eq}) = 0 \quad \Rightarrow \quad \dot{x} = 0
$$

For inverted pendulum: $x_{eq} = [0, 0, 0, 0, 0, 0]^T$ (upright).

### References

1. **Gamma et al.** (1994). *Design Patterns*. Addison-Wesley. (Template Method Pattern)
2. **Khalil** (2002). *Nonlinear Systems*. Prentice Hall. Section 2.7 (Linearization).



## Usage Examples

### Example 1: Basic Usage

Initialize and use the Models Base Dynamics Interface module:

```python
# example-metadata:
# runnable: false

from src.plant.models.base.dynamics_interface import *
import numpy as np

# Basic initialization
# Initialize module
# ... basic usage code ...
```

## Example 2: Advanced Configuration

Configure with custom parameters:

```python
from src.plant.models.simplified import SimplifiedDIPDynamics

# Enable numerical stability features
dynamics = SimplifiedDIPDynamics(
    config=config,
    enable_energy_monitoring=True,
    numerical_tolerance=1e-8,
    use_numba=True  # JIT compilation for performance
)

# Configure integration parameters
dynamics.set_integration_params(
    method='rk45',
    atol=1e-8,
    rtol=1e-6
)
```

## Example 3: Error Handling

Robust error handling and recovery:

```python
from src.plant.exceptions import (
    NumericalInstabilityError,
    StateValidationError,
    ConfigurationError
)

try:
    # Risky operation
    state_dot = dynamics.step(state, control, t)

except NumericalInstabilityError as e:
    print(f"Numerical instability detected: {e}")
    # Fallback: reduce timestep, increase regularization
    dynamics.reset_numerical_params(stronger_regularization=True)

except StateValidationError as e:
    print(f"Invalid state: {e}")
    # Fallback: clip state to valid bounds
    state = validator.clip_to_valid(state)

except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Fallback: use default configuration
    config = get_default_config()
```

### Example 4: Performance Optimization

Optimize for computational efficiency:

```python
import time
from numba import njit

# Enable Numba JIT

compilation for hot loops
@njit
def batch_dynamics_step(states, controls, params):
    """Vectorized dynamics computation."""
    N = states.shape[0]
    state_dots = np.zeros_like(states)
    for i in range(N):
        state_dots[i] = dynamics_core_numba(states[i], controls[i], params)
    return state_dots

# Benchmark
N = 1000
states = np.random.randn(N, 6)
controls = np.random.randn(N, 1)

start = time.perf_counter()
results = batch_dynamics_step(states, controls, params)
elapsed = time.perf_counter() - start

print(f"Processed {N} states in {elapsed*1000:.2f}ms")
print(f"Throughput: {N/elapsed:.0f} states/sec")
```

## Example 5: Integration with Controllers

Integrate with control systems:

```python
from src.controllers import ClassicalSMC
from src.core.simulation_runner import SimulationRunner

# Create dynamics model
dynamics = SimplifiedDIPDynamics(config)

# Create controller
controller = ClassicalSMC(
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
    max_force=100.0,
    boundary_layer=0.01
)

# Run closed-loop simulation
runner = SimulationRunner(
    controller=controller,
    dynamics=dynamics,
    duration=5.0,
    dt=0.01
)

result = runner.run(
    initial_state=np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])
)

print(f"Final state: {result.states[-1]}")
print(f"Settling time: {result.settling_time:.2f}s")
print(f"Control effort: {result.control_effort:.2f}")
```


## Complete Source Code

```{literalinclude} ../../../src/plant/models/base/dynamics_interface.py
:language: python
:linenos:
```



## Classes

### `IntegrationMethod`

**Inherits from:** `Enum`

Available integration methods for dynamics.

#### Source Code

```{literalinclude} ../../../src/plant/models/base/dynamics_interface.py
:language: python
:pyobject: IntegrationMethod
:linenos:
```



### `DynamicsResult`

**Inherits from:** `NamedTuple`

Result of dynamics computation.

Contains state derivatives and optional diagnostic information
for debugging and analysis.

#### Source Code

```{literalinclude} ../../../src/plant/models/base/dynamics_interface.py
:language: python
:pyobject: DynamicsResult
:linenos:
```

#### Methods (2)

##### `success_result(cls, state_derivative)`

Create successful dynamics result.

[View full source →](#method-dynamicsresult-success_result)

##### `failure_result(cls, reason)`

Create failed dynamics result.

[View full source →](#method-dynamicsresult-failure_result)



### `DynamicsModel`

**Inherits from:** `Protocol`

Protocol for plant dynamics models.

Defines the interface that all dynamics models must implement
for consistent integration with controllers and simulators.

#### Source Code

```{literalinclude} ../../../src/plant/models/base/dynamics_interface.py
:language: python
:pyobject: DynamicsModel
:linenos:
```

#### Methods (5)

##### `compute_dynamics(self, state, control_input, time)`

Compute system dynamics at given state and input.

[View full source →](#method-dynamicsmodel-compute_dynamics)

##### `get_physics_matrices(self, state)`

Get physics matrices M, C, G at current state.

[View full source →](#method-dynamicsmodel-get_physics_matrices)

##### `validate_state(self, state)`

Validate state vector format and bounds.

[View full source →](#method-dynamicsmodel-validate_state)

##### `get_state_dimension(self)`

Get the dimension of the state vector.

[View full source →](#method-dynamicsmodel-get_state_dimension)

##### `get_control_dimension(self)`

Get the dimension of the control input vector.

[View full source →](#method-dynamicsmodel-get_control_dimension)



### `BaseDynamicsModel`

**Inherits from:** `ABC`

Abstract base class for dynamics models.

Provides common functionality and enforces interface compliance
for concrete dynamics implementations.

#### Source Code

```{literalinclude} ../../../src/plant/models/base/dynamics_interface.py
:language: python
:pyobject: BaseDynamicsModel
:linenos:
```

#### Methods (14)

##### `__init__(self, parameters)`

Initialize dynamics model.

[View full source →](#method-basedynamicsmodel-__init__)

##### `compute_dynamics(self, state, control_input, time)`

Compute system dynamics (must be implemented by subclasses).

[View full source →](#method-basedynamicsmodel-compute_dynamics)

##### `get_physics_matrices(self, state)`

Get physics matrices (must be implemented by subclasses).

[View full source →](#method-basedynamicsmodel-get_physics_matrices)

##### `_setup_validation(self)`

Setup state validation (must be implemented by subclasses).

[View full source →](#method-basedynamicsmodel-_setup_validation)

##### `validate_state(self, state)`

Validate state vector using configured validator.

[View full source →](#method-basedynamicsmodel-validate_state)

##### `sanitize_state(self, state)`

Sanitize state vector if validator supports it.

[View full source →](#method-basedynamicsmodel-sanitize_state)

##### `get_state_dimension(self)`

Get state vector dimension (default: 6 for DIP).

[View full source →](#method-basedynamicsmodel-get_state_dimension)

##### `get_control_dimension(self)`

Get control input dimension (default: 1 for DIP).

[View full source →](#method-basedynamicsmodel-get_control_dimension)

##### `reset_monitoring(self)`

Reset monitoring statistics.

[View full source →](#method-basedynamicsmodel-reset_monitoring)

##### `get_monitoring_stats(self)`

Get monitoring statistics.

[View full source →](#method-basedynamicsmodel-get_monitoring_stats)

##### `_setup_monitoring(self)`

Setup default monitoring (can be overridden).

[View full source →](#method-basedynamicsmodel-_setup_monitoring)

##### `_basic_state_validation(self, state)`

Basic state validation fallback.

[View full source →](#method-basedynamicsmodel-_basic_state_validation)

##### `_create_success_result(self, state_derivative)`

Helper to create successful dynamics result.

[View full source →](#method-basedynamicsmodel-_create_success_result)

##### `_create_failure_result(self, reason)`

Helper to create failed dynamics result.

[View full source →](#method-basedynamicsmodel-_create_failure_result)



### `LinearDynamicsModel`

**Inherits from:** `BaseDynamicsModel`

Base class for linear dynamics models.

Provides structure for linear systems of the form:
ẋ = Ax + Bu + f(t)

Where A is the system matrix, B is the input matrix,
and f(t) is an optional time-varying disturbance.

#### Source Code

```{literalinclude} ../../../src/plant/models/base/dynamics_interface.py
:language: python
:pyobject: LinearDynamicsModel
:linenos:
```

#### Methods (6)

##### `__init__(self, A, B, parameters)`

Initialize linear dynamics model.

[View full source →](#method-lineardynamicsmodel-__init__)

##### `compute_dynamics(self, state, control_input, time)`

Compute linear dynamics.

[View full source →](#method-lineardynamicsmodel-compute_dynamics)

##### `get_physics_matrices(self, state)`

Get linear system matrices as M, C, G equivalent.

[View full source →](#method-lineardynamicsmodel-get_physics_matrices)

##### `_setup_validation(self)`

Setup validation for linear systems.

[View full source →](#method-lineardynamicsmodel-_setup_validation)

##### `_validate_matrices(self)`

Validate system matrices.

[View full source →](#method-lineardynamicsmodel-_validate_matrices)

##### `_validate_control_input(self, control_input)`

Validate control input vector.

[View full source →](#method-lineardynamicsmodel-_validate_control_input)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Protocol, Tuple, Optional, Dict, Any, NamedTuple`
- `from abc import ABC, abstractmethod`
- `from enum import Enum`
- `import numpy as np`
