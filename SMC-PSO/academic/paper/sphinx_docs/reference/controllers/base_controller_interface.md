# controllers.base.controller_interface

**Source:** `src\controllers\base\controller_interface.py`

## Module Overview

Abstract base controller interface for the double inverted pendulum system.


## Mathematical Foundation

### Protocol-Oriented Design

**Protocols** define abstract interfaces without implementation inheritance.

```{math}
\text{Protocol}: \text{Interface Specification} \to \text{Type Constraints}
```

### Controller Protocol

**Minimal interface** all controllers must implement:

```python
# example-metadata:
# runnable: false

class ControllerProtocol(Protocol):
    def compute_control(
        self,
        state: np.ndarray,
        state_vars: Dict[str, Any],
        history: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any], Dict[str, Any]]:
        ...

    def initialize_history(self) -> Dict[str, Any]:
        ...
```

## Liskov Substitution Principle

**LSP:** Subclasses must be substitutable for base class without breaking program.

```{math}
\forall c \in \text{Controller}: \quad c.\text{compute\_control}(s, v, h) \to (u, v', h')
```

**Guarantees:**
- All controllers return same signature
- All controllers handle same state format
- Simulation engine doesn't care about controller type

### Type Variance

**Contravariant input types:**

```python
# example-metadata:
# runnable: false

class Controller(ABC):
    def compute_control(
        self,
        state: np.ndarray,  # Can accept more general types in subclasses
        ...
    ) -> ...:
        ...
```

**Covariant return types:**

```python
# example-metadata:
# runnable: false

class Controller(ABC):
    def compute_control(...) -> Tuple[float, Dict, Dict]:  # Subclasses can return more specific types
        ...
```

## Abstract Base Class Pattern

```python
class Controller(ABC):
    @abstractmethod
    def compute_control(self, state, state_vars, history):
        """Subclasses MUST implement this."""
        pass

    def reset(self):
        """Default implementation (optional override)."""
        return self.initialize_history()
```

**Enforcement:** Python raises `TypeError` if abstract methods not implemented.

### Duck Typing vs Explicit Protocols

**Duck Typing:** "If it walks like a duck and quacks like a duck, it's a duck."

```python
# No type checking

- relies on runtime behavior
def simulate(controller):
    u = controller.compute_control(state, {}, {})  # Hope it works!
```

**Explicit Protocol:** Type checker validates at compile time.

```python
def simulate(controller: ControllerProtocol):
    u = controller.compute_control(state, {}, {})  # Type-safe!
```

## State Variable Pattern

**Problem:** Controllers need internal state (e.g., integral error, adaptation gains).

**Solution:** Return updated state variables:

```python
# example-metadata:
# runnable: false

def compute_control(
    self,
    state: np.ndarray,
    state_vars: Dict[str, Any],
    history: Dict[str, Any]
) -> Tuple[float, Dict[str, Any], Dict[str, Any]]:
    # Extract previous state
    K = state_vars.get('K', self.K_initial)

    # Update state (e.g., adaptation)
    K_new = K + self.gamma * abs(s) * self.dt

    # Return new state
    return u, {'K': K_new}, history
```

**Benefits:**
- Pure functional style (no hidden state)
- Simulation reproducible (state fully captured)
- Easy to checkpoint and resume

### History Pattern

**Problem:** Controllers may need trajectory history (e.g., for derivative estimation).

**Solution:** Return updated history dict:

```python
def compute_control(self, state, state_vars, history):
    # Append to history
    history['states'].append(state)
    history['times'].append(t)

    # Compute derivative from history
    if len(history['states']) >= 2:
        derivative = (state - history['states'][-2]) / self.dt

    return u, state_vars, history
```

### Polymorphism Depth

**Single-level polymorphism:**

```
Controller (abstract)
├─ ClassicalSMC
├─ AdaptiveSMC
├─ SuperTwistingSMC
└─ HybridAdaptiveSMC
```

**No deep hierarchies:** Avoid fragile base class problem.

### Method Resolution Order

Python uses **C3 linearization** for multiple inheritance:

```python
class HybridAdaptiveSMC(AdaptiveSMC, SuperTwistingSMC):
    pass

# MRO: HybridAdaptiveSMC →

AdaptiveSMC → SuperTwistingSMC → Controller → ABC
```

**Diamond problem:** C3 ensures consistent method resolution.

## Architecture Diagram

```{mermaid}
graph TD
    A[ControllerProtocol_ABC_] --> B[compute_control: Abstract]
    A --> C[initialize_history: Abstract]
    A --> D[reset: Default Implementation]

    B --> E[ClassicalSMC.compute_control]
    B --> F[AdaptiveSMC.compute_control]
    B --> G[SuperTwistingSMC.compute_control]
    B --> H[HybridAdaptiveSMC.compute_control]

    C --> I[ClassicalSMC.initialize_history]
    C --> J[AdaptiveSMC.initialize_history]
    C --> K[SuperTwistingSMC.initialize_history]
    C --> L[HybridAdaptiveSMC.initialize_history]

    E --> M[Return: _u_ state_vars_ history_]
    F --> M
    G --> M
    H --> M

    style A fill:#9cf
    style B fill:#ff9
    style M fill:#9f9
```

## Usage Examples

### Example 1: Basic Controller Protocol Usage

```python
# example-metadata:
# runnable: false

from src.controllers.base.controller_interface import ControllerProtocol
import numpy as np

def simulate(controller: ControllerProtocol, duration: float):
    """Simulate with any controller implementing the protocol."""

    # Initialize
    state_vars = {}
    history = controller.initialize_history()

    # Simulation loop
    state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])

    for t in np.arange(0, duration, 0.01):
        u, state_vars, history = controller.compute_control(
            state, state_vars, history
        )
        # ... integrate dynamics

    return history

# Works with ANY controller implementing ControllerProtocol
from src.controllers import ClassicalSMC, AdaptiveSMC

classical = ClassicalSMC(gains=[10, 8, 15, 12, 50, 0.01])
adaptive = AdaptiveSMC(gains=[10, 8, 15, 12, 0.5])

result_classical = simulate(classical, duration=5.0)
result_adaptive = simulate(adaptive, duration=5.0)
```

## Example 2: Duck

Typing vs Explicit Protocol

```python
# example-metadata:
# runnable: false

# Duck typing (no type checking)
def simulate_duck(controller):  # No type hint
    u = controller.compute_control(state, {}, {})  # Hope it works!
    return u

# Explicit protocol (type-safe)
def simulate_protocol(controller: ControllerProtocol):
    u, _, _ = controller.compute_control(state, {}, {})  # mypy validates!
    return u

# mypy catches errors at compile time:
# simulate_protocol(None) # Error:

None doesn't implement ControllerProtocol
# simulate_protocol("foo") # Error:

str doesn't implement ControllerProtocol
```

## Example 3: Liskov Substitution Principle

```python
# Base class behavior
from src.controllers.base import Controller

def reset_controller(controller: Controller):
    """Works with any Controller subclass."""
    history = controller.reset()
    return history

# Works for all subclasses
classical = ClassicalSMC(gains=[10, 8, 15, 12, 50, 0.01])
adaptive = AdaptiveSMC(gains=[10, 8, 15, 12, 0.5])

history_classical = reset_controller(classical)  # Works
history_adaptive = reset_controller(adaptive)    # Works

# Substitutability guaranteed by LSP
```

## Example 4: State Variable Pattern

```python
# example-metadata:
# runnable: false

# Controller with internal state (e.g., adaptation)
class AdaptiveController(Controller):
    def compute_control(self, state, state_vars, history):
        # Extract previous state
        K = state_vars.get('K', self.K_initial)
        integral = state_vars.get('integral', 0.0)

        # Compute control
        s = self.compute_sliding_surface(state)
        K_new = K + self.gamma * abs(s) * self.dt
        integral_new = integral + s * self.dt

        u = -K_new * np.tanh(s / self.epsilon)

        # Return updated state
        return u, {'K': K_new, 'integral': integral_new}, history

# State is fully captured in state_vars
state_vars = {}
for i in range(100):
    u, state_vars, history = controller.compute_control(state, state_vars, history)
    # state_vars contains full controller state for reproducibility
```

### Example 5: Custom Controller Implementation

```python
from src.controllers.base.controller_interface import Controller
from abc import ABC

class MyCustomSMC(Controller):
    """Custom SMC implementation."""

    def __init__(self, gains, max_force):
        self.gains = gains
        self.max_force = max_force

    def compute_control(self, state, state_vars, history):
        # Custom control law
        theta1, theta2 = state[2], state[4]
        theta1_dot, theta2_dot = state[3], state[5]

        # Custom sliding surface
        s = self.gains[0] * theta1 + self.gains[1] * theta1_dot

        # Custom switching law
        u = -self.gains[2] * np.sign(s)
        u = np.clip(u, -self.max_force, self.max_force)

        return u, state_vars, history

    def initialize_history(self):
        return {'states': [], 'times': []}

# Use custom controller

with existing simulation infrastructure
custom_controller = MyCustomSMC(gains=[10.0, 5.0, 50.0], max_force=100.0)
result = simulate(custom_controller, duration=5.0)  # Works!
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/base/controller_interface.py
:language: python
:linenos:
```



## Classes

### `ControllerInterface`

**Inherits from:** `ABC`

Abstract base class for all controllers in the DIP system.

This interface defines the common methods that all controllers must implement,
ensuring consistency and interoperability across different control algorithms.

#### Source Code

```{literalinclude} ../../../src/controllers/base/controller_interface.py
:language: python
:pyobject: ControllerInterface
:linenos:
```

#### Methods (7)

##### `__init__(self, max_force, dt)`

Initialize the base controller.

[View full source →](#method-controllerinterface-__init__)

##### `compute_control(self, state, reference)`

Compute the control action for the given state.

[View full source →](#method-controllerinterface-compute_control)

##### `reset(self)`

Reset the controller internal state.

[View full source →](#method-controllerinterface-reset)

##### `_reset_state(self)`

Reset internal controller state variables.

[View full source →](#method-controllerinterface-_reset_state)

##### `step(self, state, reference)`

Perform one control step.

[View full source →](#method-controllerinterface-step)

##### `parameters(self)`

Get controller parameters as a dictionary.

[View full source →](#method-controllerinterface-parameters)

##### `__repr__(self)`

String representation of the controller.

[View full source →](#method-controllerinterface-__repr__)



## Dependencies

This module imports:

- `from abc import ABC, abstractmethod`
- `from typing import Any, Optional, Tuple, Union`
- `import numpy as np`
