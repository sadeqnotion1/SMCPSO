# simulation.safety.constraints

**Source:** `src\simulation\safety\constraints.py`

## Module Overview

Constraint definitions and checking for simulation safety.


## Mathematical Foundation

### Safety Constraints

Hard constraints and violation handling for safe simulation.

### Constraint Types

#### **1. State Constraints**

**Box constraints:**
```{math}
\mathcal{X}_{\text{safe}} = \{\vec{x} \in \mathbb{R}^n : \vec{x}_{\min} \leq \vec{x} \leq \vec{x}_{\max}\}
```

**Nonlinear constraints:**
```{math}
g_i(\vec{x}) \leq 0, \quad i = 1, \ldots, m
```

#### **2. Control Constraints**

**Input saturation:**
```{math}
\mathcal{U}_{\text{safe}} = \{\vec{u} \in \mathbb{R}^m : u_{\min} \leq u \leq u_{\max}\}
```

**Rate limits:**
```{math}
\left|\frac{du}{dt}\right| \leq \dot{u}_{\max}
```

#### **3. Joint Constraints**

**State-control coupling:**
```{math}
h(\vec{x}, \vec{u}) \leq 0
```

**Example: Energy constraint**
```{math}
E(\vec{x}) + \frac{1}{2} u^2 \leq E_{\max}
```

### Control Barrier Functions (CBF)

**Safety certificate:**
```{math}
B(\vec{x}) \geq 0 \Leftrightarrow \vec{x} \in \mathcal{X}_{\text{safe}}
```

**Forward invariance condition:**
```{math}
\dot{B}(\vec{x}) \geq -\alpha(B(\vec{x}))
```

Where $\alpha(\cdot)$ is a class-$\mathcal{K}$ function (e.g., $\alpha(B) = kB$)

**Control law modification:**
```{math}
u^* = \arg\min_{u \in \mathcal{U}} \|u - u_{\text{nom}}\|^2 \quad \text{s.t.} \quad \dot{B}(\vec{x}, u) \geq -\alpha(B)
```

### Constraint Violation Handling

**Soft constraints** (penalties):
```{math}
J = J_{\text{performance}} + \lambda \sum_{i} \max(0, g_i(\vec{x}))^2
```

**Hard constraints** (clipping):
```{math}
\vec{x}_{\text{safe}} = \Pi_{\mathcal{X}_{\text{safe}}}(\vec{x}) = \arg\min_{\tilde{\vec{x}} \in \mathcal{X}_{\text{safe}}} \|\tilde{\vec{x}} - \vec{x}\|
```

**Emergency stop:**
```{math}
\text{Violation}(\vec{x}) \Rightarrow \text{STOP}
```

### Constraint Propagation

**Forward reachability:**
```{math}
\mathcal{R}_{[t_0, t_f]} = \{\vec{x}(t) : \vec{x}_0 \in \mathcal{X}_0, \vec{u}(\cdot) \in \mathcal{U}, t \in [t_0, t_f]\}
```

**Backward reachability (invariant set):**
```{math}
\mathcal{I} = \{\vec{x}_0 : \vec{x}(t) \in \mathcal{X}_{\text{safe}} \quad \forall t \geq 0\}
```

### Penalty Methods

**Quadratic penalty:**
```{math}
p(\vec{x}) = \sum_{i=1}^{m} \rho_i \cdot \max(0, g_i(\vec{x}))^2
```

**Exponential penalty:**
```{math}
p(\vec{x}) = \sum_{i=1}^{m} e^{\kappa g_i(\vec{x})} - 1
```

### Lagrange Multipliers

**KKT conditions for constrained optimization:**
```{math}
\begin{align}
\nabla_u L(\vec{u}^*, \vec{\lambda}^*) &= 0 \\
g_i(\vec{u}^*) &\leq 0 \\
\lambda_i^* &\geq 0 \\
\lambda_i^* g_i(\vec{u}^*) &= 0
\end{align}
```

### Safety Monitoring Dashboard

**Real-time violation metrics:**
- **Constraint violation count:** $N_{\text{violations}}$
- **Severity:** $\max_i |g_i(\vec{x})|$
- **Duration:** Time spent in violation
- **Recovery time:** Time to return to safe set

## Architecture Diagram

```{mermaid}
graph LR
    A[Input] --> B[Safety Processing]
    B --> C[Output]

    style B fill:#9cf
    style C fill:#9f9
```

## Usage Examples

### Example 1: Basic Usage

```python
from src.simulation.safety import SafetyConstraints

# Initialize
instance = SafetyConstraints()

# Execute
result = instance.process(data)
```

## Example 2: Advanced Configuration

```python
# Custom configuration
config = {'parameter': 'value'}
instance = SafetyConstraints(config)
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

```{literalinclude} ../../../src/simulation/safety/constraints.py
:language: python
:linenos:
```



## Classes

### `Constraint`

**Inherits from:** `ABC`

Base class for simulation constraints.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/constraints.py
:language: python
:pyobject: Constraint
:linenos:
```

#### Methods (2)

##### `check(self, value)`

Check if constraint is satisfied.

[View full source →](#method-constraint-check)

##### `get_violation_message(self)`

Get constraint violation message.

[View full source →](#method-constraint-get_violation_message)



### `StateConstraints`

State variable constraints.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/constraints.py
:language: python
:pyobject: StateConstraints
:linenos:
```

#### Methods (2)

##### `__init__(self, lower_bounds, upper_bounds, custom_constraints)`

Initialize state constraints.

[View full source →](#method-stateconstraints-__init__)

##### `check_all(self, state)`

Check all state constraints.

[View full source →](#method-stateconstraints-check_all)



### `ControlConstraints`

Control input constraints.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/constraints.py
:language: python
:pyobject: ControlConstraints
:linenos:
```

#### Methods (2)

##### `__init__(self, min_control, max_control, rate_limit)`

Initialize control constraints.

[View full source →](#method-controlconstraints-__init__)

##### `check_all(self, control, dt)`

Check all control constraints.

[View full source →](#method-controlconstraints-check_all)



### `EnergyConstraints`

System energy constraints.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/constraints.py
:language: python
:pyobject: EnergyConstraints
:linenos:
```

#### Methods (2)

##### `__init__(self, max_kinetic, max_potential, max_total)`

Initialize energy constraints.

[View full source →](#method-energyconstraints-__init__)

##### `check_all(self, kinetic, potential)`

Check energy constraints.

[View full source →](#method-energyconstraints-check_all)



### `ConstraintChecker`

Unified constraint checker for simulation safety.

#### Source Code

```{literalinclude} ../../../src/simulation/safety/constraints.py
:language: python
:pyobject: ConstraintChecker
:linenos:
```

#### Methods (4)

##### `__init__(self, state_constraints, control_constraints, energy_constraints)`

Initialize constraint checker.

[View full source →](#method-constraintchecker-__init__)

##### `check_state(self, state)`

Check state constraints.

[View full source →](#method-constraintchecker-check_state)

##### `check_control(self, control, dt)`

Check control constraints.

[View full source →](#method-constraintchecker-check_control)

##### `check_energy(self, kinetic, potential)`

Check energy constraints.

[View full source →](#method-constraintchecker-check_energy)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, Optional, Tuple`
- `import numpy as np`
