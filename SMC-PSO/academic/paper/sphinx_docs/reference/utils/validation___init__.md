# utils.validation.__init__

**Source:** `src\utils\validation\__init__.py`

## Module Overview Parameter

validation utilities for control engineering

. This package provides validation functions for control system


parameters, ensuring stability and proper behavior. ## Complete Source Code ```{literalinclude} ../../../src/utils/validation/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from .parameter_validators import require_positive, require_finite`
- `from .range_validators import require_in_range, require_probability` ## Advanced Mathematical Theory ### Parameter Validation Theory Parameter validation ensures control system stability through mathematical constraint checking. #### Range Validation **Closed interval check:**
$$
x \in [x_{\min}, x_{\max}] \Leftrightarrow x_{\min} \leq x \leq x_{\max}
$$ **Open interval check:**
$$
x \in (x_{\min}, x_{\max}) \Leftrightarrow x_{\min} < x < x_{\max}
$$ **Half-open interval:**
$$
x \in [x_{\min}, x_{\max}) \Leftrightarrow x_{\min} \leq x < x_{\max}
$$ #### Positivity Constraints **Strictly positive:**
$$
x > 0
$$ Required for: masses, lengths, inertias, spring constants **Non-negative:**
$$
x \geq 0
$$ Required for: friction coefficients, damping terms **Positive definite matrix:**
$$
M \succ 0 \Leftrightarrow x^T M x > 0 \quad \forall x \neq 0
$$ #### Probability Constraints **Valid probability:**
$$
p \in [0, 1]
$$ **Probability distribution:**
$$
\sum_{i=1}^n p_i = 1 \wedge p_i \geq 0 \quad \forall i
$$ #### Physical Constraint Satisfaction **Inequality constraints:**
$$
g_i(x) \leq 0, \quad i = 1, \ldots, m
$$ **Equality constraints:**
$$
h_j(x) = 0, \quad j = 1, \ldots, p
$$ **Constraint violation measure:**
$$
V(x) = \sum_{i=1}^m \max(0, g_i(x))^2 + \sum_{j=1}^p h_j(x)^2
$$ Feasible if $V(x) = 0$. ## Architecture Diagram ```{mermaid}
graph TD A[Validation System] --> B[Range Validators] A --> C[Parameter Validators] A --> D[Constraint Validators] B --> E{Check Range} E -->|x ∈ _a,b_| F[Valid] E -->|x ∉ _a,b_| G[ValueError] C --> H{Check Positivity} H -->|x > 0| I[Valid] H -->|x ≤ 0| J[ValueError] D --> K{Check Constraints} K -->|g_i_x_ ≤ 0| L[Feasible] K -->|g_i_x_ > 0| M[Infeasible] F --> N[Return Value] I --> N L --> N G --> O[Raise Exception] J --> O M --> O style E fill:#fff4e1 style H fill:#fff4e1 style K fill:#fff4e1 style N fill:#e8f5e9 style O fill:#ffebee
``` ## Usage Examples ### Example 1: Basic Range Validation ```python

from src.utils.validation import require_in_range def set_control_gain(gain: float): # Validate gain is in acceptable range validated_gain = require_in_range( gain, min_val=0.1, max_val=100.0, name="control_gain" ) return validated_gain # Valid gain
k = set_control_gain(10.0) # ✓ Returns 10.0 # Invalid gain
try: k = set_control_gain(150.0) # ValueError: out of range
except ValueError as e: print(f"Validation failed: {e}")
``` ### Example 2: Positivity Validation ```python
from src.utils.validation import require_positive def configure_pendulum(mass: float, length: float): # Physical parameters must be positive m = require_positive(mass, name="mass") L = require_positive(length, name="length") # Compute inertia I = m * L**2 return I # Valid parameters
I = configure_pendulum(1.0, 0.5) # ✓ Returns 0.25 # Invalid parameters
try: I = configure_pendulum(-1.0, 0.5) # ValueError: must be positive
except ValueError as e: print(f"Invalid mass: {e}")
``` ### Example 3: Probability Validation ```python

from src.utils.validation import require_probability def set_confidence_level(alpha: float): # Validate probability constraint validated_alpha = require_probability( alpha, name="confidence_level" ) return validated_alpha # Valid probability
alpha = set_confidence_level(0.95) # ✓ Returns 0.95 # Invalid probability
try: alpha = set_confidence_level(1.5) # ValueError: not in [0,1]
except ValueError as e: print(f"Invalid confidence: {e}")
``` ### Example 4: Constraint Validation ```python
from src.utils.validation import require_in_range, require_positive
import numpy as np def validate_controller_parameters(params: dict): # Multiple constraint validation validated = {} # Gains must be positive for gain_name in ['k1', 'k2', 'k3']: validated[gain_name] = require_positive( params[gain_name], name=gain_name ) # Max force in specific range validated['max_force'] = require_in_range( params['max_force'], min_val=10.0, max_val=200.0, name="max_force" ) # Boundary layer must be small positive validated['boundary_layer'] = require_in_range( params['boundary_layer'], min_val=0.0, max_val=1.0, name="boundary_layer" ) return validated # Validate complete parameter set
params = { 'k1': 10.0, 'k2': 8.0, 'k3': 15.0, 'max_force': 100.0, 'boundary_layer': 0.01
}
valid_params = validate_controller_parameters(params) # ✓ All pass
``` ### Example 5: Batch Parameter Validation ```python

from src.utils.validation import require_positive, require_in_range
import numpy as np def validate_gains_array(gains: np.ndarray): \"\"\"Validate array of controller gains.\"\"\" # Check array dimensions if gains.shape[0] != 6: raise ValueError(f"Expected 6 gains, got {gains.shape[0]}") # Validate each gain individually for i, gain in enumerate(gains): if i < 5: # First 5 gains must be positive require_positive(gain, name=f"gain[{i}]") else: # Last gain can be zero or positive require_in_range(gain, min_val=0.0, max_val=100.0, name=f"gain[{i}]") return gains # Valid gains
gains = np.array([10.0, 8.0, 15.0, 12.0, 50.0, 5.0])
validated_gains = validate_gains_array(gains) # ✓ Pass # Invalid gains
try: bad_gains = np.array([10.0, -8.0, 15.0, 12.0, 50.0, 5.0]) validate_gains_array(bad_gains) # ValueError: negative gain
except ValueError as e: print(f"Validation error: {e}")
```
