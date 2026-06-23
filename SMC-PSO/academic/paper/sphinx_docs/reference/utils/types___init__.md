# utils.types.__init__

**Source:** `src\utils\types\__init__.py`

## Module Overview

Type definitions and structured return types for control engineering.

This package provides type-safe structured return types for controllers
and other components, ensuring clear interfaces and reducing errors.

## Complete Source Code

```{literalinclude} ../../../src/utils/types/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .control_outputs import ClassicalSMCOutput, AdaptiveSMCOutput, STAOutput, HybridSTAOutput`


## Advanced Mathematical Theory

### Type System Theory

Type systems provide mathematical foundations for ensuring program correctness through static and runtime checks.

#### Algebraic Data Types

**Product Types** (tuples, records):
$$
T_{\text{product}} = T_1 \times T_2 \times \cdots \times T_n
$$

**Example:** `ClassicalSMCOutput = (u, state_vars, history)`

**Sum Types** (unions, tagged unions):
$$
T_{\text{sum}} = T_1 + T_2 + \cdots + T_n
$$

**Type Constructor:**
$$
\text{NamedTuple}: (name_1: T_1, \ldots, name_n: T_n) \rightarrow T_{\text{output}}
$$

#### Type Safety Guarantees

**Static Type Checking:**
$$
\Gamma \vdash e : T
$$

where $\Gamma$ is type environment, $e$ is expression, $T$ is type.

**Runtime Type Validation:**
$$
\text{isinstance}(x, T) \rightarrow \text{bool}
$$

**Immutability Guarantee:**
$$
x_{\text{tuple}} = \text{frozen} \Rightarrow \forall t: x(t) = x(0)
$$

#### Interface Contract Theory

**Preconditions** (caller must ensure):
$$
P_{\text{pre}}(x) = \text{True} \Rightarrow \text{function can execute}
$$

**Postconditions** (function guarantees):
$$
P_{\text{pre}}(x) \wedge \text{function}(x) \Rightarrow P_{\text{post}}(\text{result})
$$

**Invariants** (always hold):
$$
I(state) = \text{True} \quad \forall \text{ valid states}
$$

**Example for control output:**
- Precondition: $x \in \mathbb{R}^n$
- Postcondition: $u \in [-u_{\max}, u_{\max}]$
- Invariant: Output is NamedTuple with fixed fields

## Architecture Diagram

```{mermaid}
graph TD
    A[Type System] --> B[Product Types]
    A --> C[Sum Types]
    A --> D[Type Constructors]

    B --> E[NamedTuple]
    E --> F[ClassicalSMCOutput]
    E --> G[AdaptiveSMCOutput]
    E --> H[STAOutput]
    E --> I[HybridSTAOutput]

    D --> J{Type Checking}
    J -->|Static| K[mypy Validation]
    J -->|Runtime| L[isinstance Check]

    F --> M[Contract Enforcement]
    G --> M
    H --> M
    I --> M

    M --> N{Preconditions}
    N -->|Valid| O[Execute]
    N -->|Invalid| P[Type Error]

    O --> Q{Postconditions}
    Q -->|Satisfied| R[Return Output]
    Q -->|Violated| S[Contract Violation]

    style J fill:#fff4e1
    style M fill:#e1f5ff
    style R fill:#e8f5e9
```

## Usage Examples

### Example 1: Basic Type-Safe Controller Output

```python
from src.utils.types import ClassicalSMCOutput
import numpy as np

# Controller computation returns structured output
def compute_control(x):
    u = np.array([10.0])
    state_vars = {'sliding_surface': 0.5}
    history = np.array([[0.0]])

    # Type-safe return with named fields
    return ClassicalSMCOutput(u, state_vars, history)

# Client code uses descriptive names
output = compute_control(x)
control = output.u
surface = output.state_vars['sliding_surface']
past_controls = output.history
```

## Example 2: Type Checking and Validation

```python
from src.utils.types import ClassicalSMCOutput, AdaptiveSMCOutput
import numpy as np

def validate_output(output):
    # Runtime type checking
    if isinstance(output, ClassicalSMCOutput):
        print("Classical SMC output detected")
        assert hasattr(output, 'u')
        assert hasattr(output, 'state_vars')
        assert hasattr(output, 'history')
    elif isinstance(output, AdaptiveSMCOutput):
        print("Adaptive SMC output detected")
        assert hasattr(output, 'adaptive_gains')
    else:
        raise TypeError(f"Unknown output type: {type(output)}")

# Validate outputs
classical_output = ClassicalSMCOutput(u, state_vars, history)
validate_output(classical_output)  # ✓ Pass
```

## Example 3: Immutability and Contract Enforcement

```python
from src.utils.types import STAOutput

# Create immutable output
sta_output = STAOutput(u, state_vars, history)

# Attempt modification (will

fail - NamedTuple is frozen)
try:
    sta_output.u = np.array([20.0])  # AttributeError
except AttributeError:
    print("Immutability enforced - cannot modify output")

# Correct approach: Create new output
modified_output = STAOutput(
    u=np.array([20.0]),
    state_vars=sta_output.state_vars,
    history=sta_output.history
)
```

## Example 4: Integration with Type Hints

```python
from src.utils.types import HybridSTAOutput
from typing import Tuple
import numpy as np

def hybrid_controller(
    x: np.ndarray,
    state_vars: dict,
    history: np.ndarray
) -> HybridSTAOutput:
    \"\"\"Type-annotated controller with structured output.\"\"\"
    u = compute_hybrid_control(x)
    updated_vars = update_state_vars(state_vars, x)
    updated_history = np.vstack([history, u])

    return HybridSTAOutput(u, updated_vars, updated_history)

# Static type checker (mypy) validates this
output: HybridSTAOutput = hybrid_controller(x, state_vars, history)
```

## Example 5: Batch

Processing with Type Safety

```python
from src.utils.types import ClassicalSMCOutput
import numpy as np
from typing import List

def batch_control(states: List[np.ndarray]) -> List[ClassicalSMCOutput]:
    \"\"\"Process multiple states with type-safe outputs.\"\"\"
    outputs = []

    for x in states:
        u = controller.compute_control(x, state_vars, history)
        # u is already ClassicalSMCOutput
        outputs.append(u)

    return outputs

# Type-safe batch processing
states = [x1, x2, x3]
outputs = batch_control(states)

# Extract all controls (type-safe field access)
controls = np.array([out.u for out in outputs])
surfaces = [out.state_vars['sliding_surface'] for out in outputs]
```
