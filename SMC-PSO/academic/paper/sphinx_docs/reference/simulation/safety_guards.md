# simulation.safety.guards

**Source:** `src\simulation\safety\guards.py`

## Module Overview

Enhanced safety guard functions for simulation framework.


## Mathematical Foundation

### Safety Guard Systems

Runtime monitoring and enforcement of safety invariants.

### Safety Invariants

**State space constraints:**
```{math}
\mathcal{S}_{\text{safe}} = \{\vec{x} \in \mathbb{R}^n : h(\vec{x}) \leq 0\}
```

**Invariant preservation:**
```{math}
\vec{x}_0 \in \mathcal{S}_{\text{safe}} \land \dot{\vec{x}} = f(\vec{x}, \vec{u}) \Rightarrow \vec{x}(t) \in \mathcal{S}_{\text{safe}} \quad \forall t
```

### Guard Types

#### **1. NaN Guard**

Detect numerical instabilities:
```{math}
\text{NaN}(x_i) \lor \text{Inf}(x_i) \Rightarrow \text{VIOLATION}
```

**Detection:** `np.isnan(x) or np.isinf(x)`

#### **2. Energy Guard**

Prevent unrealistic energy growth:
```{math}
E(\vec{x}) = \frac{1}{2} m \dot{x}^2 + mgh \leq E_{\max}
```

**Violation condition:**
```{math}
E(\vec{x}_k) > (1 + \epsilon) E_0 \quad \text{where } E_0 = E(\vec{x}_0)
```

Typical: $\epsilon = 5.0$ (500% energy growth threshold)

#### **3. State Bounds Guard**

Enforce physical limits:
```{math}
\vec{x}_{\min} \leq \vec{x}(t) \leq \vec{x}_{\max}
```

**Component-wise constraints:**
```{math}
\begin{align}
|x| &\leq x_{\max} \quad \text{(cart position)} \\
|\theta_1|, |\theta_2| &\leq \pi \quad \text{(pendulum angles)} \\
|\dot{x}|, |\dot{\theta}_1|, |\dot{\theta}_2| &\leq v_{\max} \quad \text{(velocities)}
\end{align}
```

#### **4. Control Saturation Guard**

Verify actuator limits:
```{math}
|u(t)| \leq u_{\max}
```

### Formal Verification

**Runtime assertion checking:**
```{math}
\text{assert}(\phi(\vec{x}_k)) \quad \text{at each step } k
```

**Temporal logic properties:**
```{math}
\square (\vec{x} \in \mathcal{S}_{\text{safe}}) \quad \text{(Always safe)}
```

### Recovery Strategies

**1. State Clamping**
```{math}
\vec{x}_{\text{safe}} = \text{clip}(\vec{x}, \vec{x}_{\min}, \vec{x}_{\max})
```

**2. Simulation Termination**
```{math}
\text{VIOLATION} \Rightarrow \text{STOP}, \text{LOG}, \text{REPORT}
```

**3. Emergency Controller**
```{math}
u_{\text{emergency}} = -K_p \vec{x} - K_d \dot{\vec{x}}
```

### Monitor Composition

**Sequential guards:**
```{math}
\text{GuardChain} = \text{NaN} \to \text{Bounds} \to \text{Energy}
```

**Parallel guards:**
```{math}
\text{Violation} = \bigvee_{i=1}^{N} \text{Guard}_i(\vec{x})
```

### Performance Overhead

**Guard checking cost:**
```{math}
T_{\text{guard}} = \sum_{i=1}^{N} T_{\text{check}}^{(i)}
```

**Typical overhead:** <1% of total simulation time

### Watchdog Timers

**Deadlock detection:**
```{math}
t - t_{\text{last\_update}} > T_{\text{watchdog}} \Rightarrow \text{TIMEOUT}
```

Typical: $T_{\text{watchdog}} = 10 \times \Delta t$

## Architecture Diagram

```{mermaid}
graph TD
    A[State x_k_] --> B{NaN/Inf Check}
    B -->|Pass| C{Bounds Check}
    B -->|Fail| Z[VIOLATION]
    C -->|Pass| D{Energy Check}
    C -->|Fail| Z
    D -->|Pass| E[Safe State]
    D -->|Fail| Z
    Z --> F[Log Error]
    F --> G[Recovery/Terminate]

    style B fill:#9cf
    style C fill:#9cf
    style D fill:#9cf
    style E fill:#9f9
    style Z fill:#f99
```

## Usage Examples

### Example 1: Basic Usage

```python
from src.simulation.safety import SafetyGuards

# Initialize
instance = SafetyGuards()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = SafetyGuards(config)
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

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:linenos:
```



## Classes

### `SafetyViolationError`

**Inherits from:** `RuntimeError`

Exception raised when safety constraints are violated.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: SafetyViolationError
:linenos:
```

#### Methods (1)

##### `__init__(self, message, violation_type, step_idx)`

Initialize safety violation error.

[View full source →](#method-safetyviolationerror-__init__)



### `NaNGuard`

**Inherits from:** `SafetyGuard`

Guard against NaN and infinite values in state.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: NaNGuard
:linenos:
```

#### Methods (2)

##### `check(self, state, step_idx)`

Check for NaN/infinite values.

[View full source →](#method-nanguard-check)

##### `get_violation_message(self)`

Get violation message.

[View full source →](#method-nanguard-get_violation_message)



### `EnergyGuard`

**Inherits from:** `SafetyGuard`

Guard against excessive system energy.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: EnergyGuard
:linenos:
```

#### Methods (3)

##### `__init__(self, max_energy)`

Initialize energy guard.

[View full source →](#method-energyguard-__init__)

##### `check(self, state, step_idx)`

Check energy constraint.

[View full source →](#method-energyguard-check)

##### `get_violation_message(self)`

Get violation message.

[View full source →](#method-energyguard-get_violation_message)



### `BoundsGuard`

**Inherits from:** `SafetyGuard`

Guard against state bounds violations.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: BoundsGuard
:linenos:
```

#### Methods (3)

##### `__init__(self, lower_bounds, upper_bounds)`

Initialize bounds guard.

[View full source →](#method-boundsguard-__init__)

##### `check(self, state, step_idx)`

Check bounds constraint.

[View full source →](#method-boundsguard-check)

##### `get_violation_message(self)`

Get violation message.

[View full source →](#method-boundsguard-get_violation_message)



### `SafetyGuardManager`

Manager for multiple safety guards.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: SafetyGuardManager
:linenos:
```

#### Methods (4)

##### `__init__(self)`

Initialize safety guard manager.

[View full source →](#method-safetyguardmanager-__init__)

##### `add_guard(self, guard)`

Add a safety guard.

[View full source →](#method-safetyguardmanager-add_guard)

##### `check_all(self, state, step_idx)`

Check all safety guards.

[View full source →](#method-safetyguardmanager-check_all)

##### `clear_guards(self)`

Clear all safety guards.

[View full source →](#method-safetyguardmanager-clear_guards)



## Functions

### `guard_no_nan(state, step_idx)`

Check for NaN/infinite values (legacy interface).

Parameters
----------
state : array-like
    State array
step_idx : int
    Current step index

Raises
------
SafetyViolationError
    If NaN/infinite values detected

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: guard_no_nan
:linenos:
```



### `guard_energy(state, limits)`

Check energy constraint (legacy interface).

Parameters
----------
state : array-like
    State array
limits : dict or None
    Energy limits with 'max' key

Raises
------
SafetyViolationError
    If energy constraint violated

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: guard_energy
:linenos:
```



### `guard_bounds(state, bounds, t)`

Check bounds constraint (legacy interface).

Parameters
----------
state : array-like
    State array
bounds : tuple or None
    (lower, upper) bounds
t : float
    Current time

Raises
------
SafetyViolationError
    If bounds violated

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: guard_bounds
:linenos:
```



### `apply_safety_guards(state, step_idx, config)`

Apply all configured safety guards.

Parameters
----------
state : np.ndarray
    Current state vector
step_idx : int
    Current simulation step
config : Any
    Configuration object with safety settings

Raises
------
SafetyViolationError
    If any safety guard is violated

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: apply_safety_guards
:linenos:
```



### `create_default_guards(config)`

Create default safety guards from configuration.

Parameters
config : Any
    Configuration object

Returns
-------
SafetyGuardManager
    Configured safety guard manager

#### Source Code

```{literalinclude} ../../../src/simulation/safety/guards.py
:language: python
:pyobject: create_default_guards
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `from typing import Any, Tuple, Optional, Dict, Union`
- `from ..core.interfaces import SafetyGuard`
