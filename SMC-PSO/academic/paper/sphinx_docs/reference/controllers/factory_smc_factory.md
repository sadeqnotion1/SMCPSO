# controllers.factory.smc_factory

**Source:** `src\controllers\factory\smc_factory.py`

## Module Overview

Clean SMC Controller Factory - Focused on 4 Core SMC Controllers

Provides a unified, type-safe interface for creating SMC controllers optimized for:
- PSO parameter tuning
- Research consistency
- Performance benchmarking
- Clean separation of concerns

Design Principles:
- Single responsibility: Only SMC controllers
- Consistent interfaces: Unified parameter handling
- PSO-ready: Array-based parameter injection
- Type-safe: Explicit typing for all controllers
- Minimal: No unnecessary complexity


## Mathematical Foundation

### Factory Design Pattern

The **Factory Pattern** encapsulates object creation logic, providing loose coupling between client code and concrete implementations.

### Gang of Four Definition

**Intent:** Define an interface for creating objects, but let subclasses decide which class to instantiate.

```{math}
\text{Factory}: \text{ProductType} \times \text{Parameters} \to \text{ConcreteProduct}
```

### SMC Controller Hierarchy

```{math}
\begin{align}
\text{SMC} &\to \text{Controller} \quad \text{(abstract base)} \\
&\to \text{ClassicalSMC} \\
&\to \text{AdaptiveSMC} \\
&\to \text{SuperTwistingSMC} \\
&\to \text{HybridAdaptiveSMC}
\end{align}
```

### Enum-Based Type Safety

**Type-safe controller selection:**

```python
class SMCType(Enum):
    CLASSICAL = "classical"
    ADAPTIVE = "adaptive"
    SUPER_TWISTING = "sta"
    HYBRID = "hybrid"
```

**Compile-time validation:** Python type checker (mypy) validates:

```python
# example-metadata:
# runnable: false

def create_controller(ctrl_type: SMCType, ...) -> Controller:
    ...
```

## Registry Pattern

**Dynamic controller registration:**

```{math}
\text{Registry}: \text{SMCType} \to (\text{Parameters} \to \text{Controller})
```

**Benefits:**
1. **Open/Closed Principle:** Add new controllers without modifying factory
2. **Plugin Architecture:** Controllers can be registered at runtime
3. **Testing:** Mock controllers can be injected

### Singleton Registry

**Single global registry** avoids duplication:

```python
_controller_registry: Dict[SMCType, Callable] = {}

def register_controller(ctrl_type: SMCType, factory_fn: Callable):
    _controller_registry[ctrl_type] = factory_fn
```

**Thread safety:** Use locks if multi-threaded:

```python
_registry_lock = threading.Lock()

with _registry_lock:
    _controller_registry[ctrl_type] = factory_fn
```

### Dependency Injection

**Inversion of Control:** Factory receives dependencies rather than creating them:

```python
# example-metadata:
# runnable: false

def create_controller(
    ctrl_type: SMCType,
    gains: List[float],
    dynamics_model: Optional[DynamicsModel] = None,  # Injected
    config: Optional[Config] = None  # Injected
) -> Controller:
    ...
```

**Benefits:**
- Testability: Inject mock dynamics models
- Flexibility: Change models without factory changes
- Loose coupling: Factory doesn't depend on concrete dynamics

## Gain Specification Pattern

**Each controller type specifies gain requirements:**

```{math}
\text{GainSpec} = (n_{gains}, \text{bounds}, \text{names})
```

**Example:**

```python
@dataclass
class GainSpecification:
    n_gains: int
    bounds: List[Tuple[float, float]]
    gain_names: List[str]
    description: str
```

**Runtime validation:**

```python
def validate_gains(ctrl_type: SMCType, gains: List[float]) -> bool:
    spec = get_gain_specification(ctrl_type)
    if len(gains) != spec.n_gains:
        return False
    return all(lb <= g <= ub for g, (lb, ub) in zip(gains, spec.bounds))
```

### Configuration Dataclass Pattern

**Type-safe configuration:**

```python
# example-metadata:
# runnable: false

@dataclass(frozen=True)
class SMCConfig:
    gains: List[float]
    max_force: float
    dt: float
    boundary_layer: float = 0.01

    def __post_init__(self):
        # Validation logic
        if self.max_force <= 0:
            raise ValueError("max_force must be positive")
```

**Benefits:**
- Immutable (frozen=True)
- Type hints enforced
- Validation in `__post_init__`
- Auto-generated `__repr__` and `__eq__`

### Builder Pattern Variant

For complex configurations:

```python
# example-metadata:
# runnable: false

class SMCConfigBuilder:
    def __init__(self):
        self._config = {}

    def with_gains(self, gains: List[float]):
        self._config['gains'] = gains
        return self

    def with_max_force(self, max_force: float):
        self._config['max_force'] = max_force
        return self

    def build(self) -> SMCConfig:
        return SMCConfig(**self._config)
```

**Usage:**

```python
config = (SMCConfigBuilder()
    .with_gains([10, 8, 15, 12, 50, 5])
    .with_max_force(100.0)
    .build())
```

## Performance Considerations

**Factory overhead:**
- Type dispatch: $O(1)$ hash table lookup
- Object construction: $O(n_{params})$
- Validation: $O(n_{gains})$

**Total:** Negligible compared to controller compute time (~$\mu$s vs ms).

## Architecture Diagram

```{mermaid}
graph TD
    A[Client Request: SMCType, gains, config] --> B[Factory.create_controller]
    B --> C{Validate Gains}
    C -->|Invalid| D[Raise ValueError]
    C -->|Valid| E{Type Dispatch}

    E -->|CLASSICAL| F[ClassicalSMC.__init__]
    E -->|ADAPTIVE| G[AdaptiveSMC.__init__]
    E -->|SUPER_TWISTING| H[SuperTwistingSMC.__init__]
    E -->|HYBRID| I[HybridAdaptiveSMC.__init__]

    F --> J[Return Controller Instance]
    G --> J
    H --> J
    I --> J

    J --> K[Client Uses: controller.compute_control]

    style B fill:#9cf
    style E fill:#ff9
    style J fill:#9f9
    style D fill:#f99
```

## Usage Examples

### Example 1: Basic Controller Creation

```python
from src.controllers.factory import SMCType, create_controller

# Create classical SMC controller
controller = create_controller(
    ctrl_type=SMCType.CLASSICAL,
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 0.01],
    max_force=100.0,
    dt=0.01
)

# Use controller
state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])
u, state_vars, history = controller.compute_control(state, {}, {})
print(f"Control output: {u:.2f} N")
```

## Example 2: Type-Safe Factory Usage

```python
from src.controllers.factory import SMCFactory, SMCConfig

# Create configuration dataclass
config = SMCConfig(
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 0.01],
    max_force=100.0,
    dt=0.01,
    boundary_layer=0.01
)

# Factory ensures type safety
controller = SMCFactory.create_controller(SMCType.CLASSICAL, config)

# mypy validates this at compile time!
```

## Example 3: Gain Specification Query

```python
from src.controllers.factory import SMCFactory, SMCType

# Get gain requirements

for each controller type
for ctrl_type in SMCType:
    spec = SMCFactory.get_gain_specification(ctrl_type)
    print(f"\n{ctrl_type.value}:")
    print(f"  Number of gains: {spec.n_gains}")
    print(f"  Gain names:      {spec.gain_names}")
    print(f"  Bounds:          {spec.bounds}")
```

## Example 4: Dynamic Controller Registry

```python
from src.controllers.factory.core.registry import ControllerRegistry

# View registered controllers
registry = ControllerRegistry()
registered_types = registry.list_controllers()

print("Registered Controllers:")
for ctrl_type in registered_types:
    factory_fn = registry.get_factory(ctrl_type)
    print(f"  {ctrl_type.value}: {factory_fn.__name__}")

# Register custom controller (plugin architecture)
def create_custom_smc(config):
    return CustomSMC(**config)

registry.register(SMCType.CUSTOM, create_custom_smc)
```

## Example 5: Batch Controller Creation

```python
from src.controllers.factory import create_all_smc_controllers

# Gains for each controller type
gains_dict = {
    "classical": [10, 8, 15, 12, 50, 0.01],
    "adaptive": [10, 8, 15, 12, 0.5],
    "sta": [25, 10, 15, 12, 20, 15],
    "hybrid": [15, 12, 18, 15]
}

# Create all controllers for comparison
controllers = create_all_smc_controllers(
    gains_dict,
    max_force=100.0,
    dt=0.01
)

# Simulate each controller
results = {}
for ctrl_name, controller in controllers.items():
    result = simulate(controller, duration=5.0)
    results[ctrl_name] = result
    print(f"{ctrl_name}: ITAE={result.itae:.3f}")
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:linenos:
```



## Classes

### `SMCType`

**Inherits from:** `Enum`

Enumeration of the 4 core SMC controller types.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: SMCType
:linenos:
```



### `SMCProtocol`

**Inherits from:** `Protocol`

Protocol defining the unified SMC controller interface.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: SMCProtocol
:linenos:
```

#### Methods (4)

##### `compute_control(self, state, state_vars, history)`

Compute control input for given state.

[View full source →](#method-smcprotocol-compute_control)

##### `initialize_state(self)`

Initialize controller internal state.

[View full source →](#method-smcprotocol-initialize_state)

##### `initialize_history(self)`

Initialize controller history tracking.

[View full source →](#method-smcprotocol-initialize_history)

##### `gains(self)`

Return controller gains.

[View full source →](#method-smcprotocol-gains)



### `PSOControllerWrapper`

PSO-friendly wrapper that simplifies the control interface.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: PSOControllerWrapper
:linenos:
```

#### Methods (3)

##### `__init__(self, controller)`

[View full source →](#method-psocontrollerwrapper-__init__)

##### `compute_control(self, state, state_vars, history)`

Flexible compute_control interface supporting both patterns:

[View full source →](#method-psocontrollerwrapper-compute_control)

##### `gains(self)`

Return controller gains.

[View full source →](#method-psocontrollerwrapper-gains)



### `SMCConfig`

Clean configuration for all SMC controllers.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: SMCConfig
:linenos:
```

#### Methods (1)

##### `__post_init__(self)`

Validate SMC configuration parameters.

[View full source →](#method-smcconfig-__post_init__)



### `SMCGainSpec`

Specification of gain requirements for each SMC type.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: SMCGainSpec
:linenos:
```

#### Methods (1)

##### `gain_bounds(self)`

Default gain bounds for PSO optimization.

[View full source →](#method-smcgainspec-gain_bounds)



### `SMCFactory`

Clean, focused factory for creating SMC controllers.

Optimized for:
- PSO parameter optimization
- Research benchmarking
- Type safety and consistency

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: SMCFactory
:linenos:
```

#### Methods (8)

##### `create_controller(smc_type, config)`

Create an SMC controller with clean, validated configuration.

[View full source →](#method-smcfactory-create_controller)

##### `create_from_gains(smc_type, gains)`

PSO-friendly: Create controller directly from gains array.

[View full source →](#method-smcfactory-create_from_gains)

##### `get_gain_specification(smc_type)`

Get gain specification for an SMC controller type.

[View full source →](#method-smcfactory-get_gain_specification)

##### `list_available_controllers()`

List all available SMC controller types.

[View full source →](#method-smcfactory-list_available_controllers)

##### `_create_classical_smc(config)`

Create Classical SMC with clean parameter mapping.

[View full source →](#method-smcfactory-_create_classical_smc)

##### `_create_adaptive_smc(config)`

Create Adaptive SMC with clean parameter mapping.

[View full source →](#method-smcfactory-_create_adaptive_smc)

##### `_create_super_twisting_smc(config)`

Create Super-Twisting SMC with clean parameter mapping.

[View full source →](#method-smcfactory-_create_super_twisting_smc)

##### `_create_hybrid_smc(config)`

Create Hybrid Adaptive-STA SMC with clean parameter mapping.

[View full source →](#method-smcfactory-_create_hybrid_smc)



## Functions

### `create_smc_for_pso(smc_type, gains, dynamics_model_or_max_force, dt, dynamics_model)`

Convenience function optimized for PSO parameter tuning.

Supports both calling patterns:
1. create_smc_for_pso(smc_type, gains, max_force, dt, dynamics_model)
2. create_smc_for_pso(smc_type, gains, dynamics_model)

Usage:
    # In PSO fitness function
    controller = create_smc_for_pso("classical_smc", pso_params)
    performance = evaluate_controller(controller, test_scenarios)
    return performance

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: create_smc_for_pso
:linenos:
```



### `get_gain_bounds_for_pso(smc_type)`

Get PSO optimization bounds for SMC controller gains.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: get_gain_bounds_for_pso
:linenos:
```



### `validate_smc_gains(smc_type, gains)`

Validate that gains are appropriate for the SMC controller type.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/smc_factory.py
:language: python
:pyobject: validate_smc_gains
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from dataclasses import dataclass`
- `from enum import Enum`
- `from typing import Protocol, Union, List, Optional, Type, Dict, Any, Tuple`
- `import numpy as np`
