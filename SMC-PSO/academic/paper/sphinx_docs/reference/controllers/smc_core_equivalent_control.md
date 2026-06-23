# controllers.smc.core.equivalent_control

**Source:** `src\controllers\smc\core\equivalent_control.py`

## Module Overview

Equivalent Control Computation for SMC Controllers.

Implements model-based equivalent control (u_eq) that drives the system along
the sliding surface. This is the feedforward component of SMC that provides
nominal performance when the model is accurate.

Mathematical Background:
- Equivalent control: u_eq = -(LM^{-1}B)^{-1} * LM^{-1}F
- Where: M = inertia matrix, F = nonlinear forces, L = surface gradient, B = input matrix
- Requires dynamics model and assumes controllability: |LM^{-1}B| > threshold


## Mathematical Foundation

### Equivalent Control Method

The **equivalent control** $u_{eq}$ maintains motion on the sliding surface $s = 0$ when reached.

```{math}
\frac{d}{dt} s(\vec{x}, t) = 0 \quad \text{when} \quad s = 0
```

### Derivation for DIP

For sliding surface:

```{math}
s = \lambda_1 \dot{\theta}_1 + c_1 \theta_1 + \lambda_2 \dot{\theta}_2 + c_2 \theta_2
```

Differentiate:

```{math}
\dot{s} = \lambda_1 \ddot{\theta}_1 + c_1 \dot{\theta}_1 + \lambda_2 \ddot{\theta}_2 + c_2 \dot{\theta}_2
```

### Manipulator Equation

DIP dynamics (manipulator form):

```{math}
\mathbf{M}(\vec{q}) \ddot{\vec{q}} + \mathbf{C}(\vec{q}, \dot{\vec{q}}) \dot{\vec{q}} + \mathbf{G}(\vec{q}) = \mathbf{B} u
```

Where:
- $\mathbf{M}$: Mass/inertia matrix (3×3)
- $\mathbf{C}$: Coriolis/centrifugal matrix
- $\mathbf{G}$: Gravity vector
- $\mathbf{B}$: Control input matrix (maps force to generalized coords)

### Solving for Equivalent Control

From $\dot{s} = 0$ on sliding surface:

```{math}
\lambda_1 \ddot{\theta}_1 + \lambda_2 \ddot{\theta}_2 = -(c_1 \dot{\theta}_1 + c_2 \dot{\theta}_2)
```

Express $\ddot{\vec{q}}$ from manipulator equation:

```{math}
\ddot{\vec{q}} = \mathbf{M}^{-1} (\mathbf{B} u - \mathbf{C} \dot{\vec{q}} - \mathbf{G})
```

Substitute into $\dot{s} = 0$ and solve for $u$:

```{math}
u_{eq} = (\mathbf{\Lambda} \mathbf{M}^{-1} \mathbf{B})^{-1} \left[ -\mathbf{\Lambda} \mathbf{M}^{-1} (\mathbf{C} \dot{\vec{q}} + \mathbf{G}) - \mathbf{C}_s \dot{\vec{\theta}} \right]
```

Where:
- $\mathbf{\Lambda} = [\lambda_1, \lambda_2]$: Surface derivative gains
- $\mathbf{C}_s = [c_1, c_2]$: Surface position gains

### Matrix Inversion Considerations

**Challenge:** $\mathbf{M}$ can be **ill-conditioned** near singularities.

**Regularization:** Use **Tikhonov regularization** for numerical stability:

```{math}
\mathbf{M}^{-1} \approx (\mathbf{M}^T \mathbf{M} + \alpha \mathbf{I})^{-1} \mathbf{M}^T
```

**Typical $\alpha$:** $10^{-6}$ to $10^{-4}$ depending on conditioning.

### Model-Based vs Model-Free

**Model-Based (Equivalent Control):**
- ✅ Accurate on sliding surface
- ✅ Smooth control
- ❌ Requires accurate model
- ❌ Computational cost $O(n^3)$ for inversion

**Model-Free (Pure Switching):**
- ✅ Robust to model uncertainty
- ✅ Low computational cost
- ❌ High-frequency chattering
- ❌ Actuator wear

### Hybrid Approach

Combine both for practical SMC:

```{math}
u = u_{eq} + u_{sw}
```

Where:
- $u_{eq}$: Model-based equivalent control (nominal performance)
- $u_{sw} = -K \, \text{sign}(s)$: Switching term (robustness)

### Computational Complexity

- **Matrix multiplication:** $O(n^3)$
- **Matrix inversion:** $O(n^3)$ (dominant cost)
- **Total:** $O(n^3)$ per control cycle
- **For DIP:** $n = 3$, so ~27 multiply-adds

### Numerical Stability

**Condition number check:**

```{math}
\kappa(\mathbf{M}) = \frac{\sigma_{max}(\mathbf{M})}{\sigma_{min}(\mathbf{M})}
```

**Rule of thumb:**
- $\kappa < 10^3$: Well-conditioned
- $10^3 \leq \kappa < 10^6$: Moderate conditioning
- $\kappa \geq 10^6$: Ill-conditioned (increase regularization)

## Architecture Diagram

```{mermaid}
graph TD
    A[State x, Dynamics Model] --> B[Compute M_x_]
    B --> C[Compute C_x_ẋ_]
    C --> D[Compute G_x_]
    D --> E[Compute B Matrix]
    E --> F[Assemble: Λ M⁻¹ B]
    F --> G{Condition Number < 10⁶?}
    G -->|Yes| H[Invert: _Λ M⁻¹ B_⁻¹]
    G -->|No| I[Apply Tikhonov Regularization]
    I --> H
    H --> J[Compute u_eq = _Λ M⁻¹ B_⁻¹ _-Λ M⁻¹_Cẋ + G_ - C_s θ̇_]
    J --> K[Return u_eq]

    style F fill:#9cf
    style H fill:#ff9
    style I fill:#f99
    style K fill:#9f9
```

## Usage Examples

### Example 1: Basic Equivalent Control Computation

```python
from src.controllers.smc.core.equivalent_control import EquivalentControl
from src.plant.models.simplified import SimplifiedDIPDynamics

# Initialize dynamics model
dynamics = SimplifiedDIPDynamics()

# Initialize equivalent control module
eq_control = EquivalentControl(
    dynamics_model=dynamics,
    surface_gains=[10.0, 8.0, 15.0, 12.0]  # λ1, c1, λ2, c2
)

# Compute equivalent control for current state
state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])
u_eq = eq_control.compute(state)
print(f"Equivalent control: {u_eq:.2f} N")
```

## Example 2: Matrix Conditioning Check

```python
# Check matrix conditioning before inversion
M = dynamics.compute_mass_matrix(state)
cond_number = np.linalg.cond(M)

print(f"Condition number of M: {cond_number:.2e}")

if cond_number > 1e6:
    print("Warning: Ill-conditioned matrix, increasing regularization")
    eq_control.set_regularization(alpha=1e-4)
else:
    print("Matrix well-conditioned")
```

## Example 3: Regularization Adjustment

```python
# example-metadata:
# runnable: false

# Adaptive regularization based on conditioning
def adaptive_regularization(cond_number):
    if cond_number < 1e3:
        return 1e-6  # Minimal regularization
    elif cond_number < 1e6:
        return 1e-5  # Moderate regularization
    else:
        return 1e-4  # Strong regularization

alpha = adaptive_regularization(cond_number)
eq_control.set_regularization(alpha=alpha)
print(f"Using regularization: α={alpha:.2e}")
```

## Example 4: Hybrid

Control (Equivalent + Switching)

```python
from src.utils.control.saturation import saturate

# Compute equivalent control (model-based)
u_eq = eq_control.compute(state)

# Compute sliding surface
s = surface.compute(state)

# Compute switching control (robustness)
K_sw = 50.0  # Switching gain
epsilon = 0.01  # Boundary layer
u_sw = -K_sw * saturate(s, epsilon, method='tanh')

# Total control
u_total = u_eq + u_sw

# Apply actuator limits
u_max = 100.0
u = np.clip(u_total, -u_max, u_max)

print(f"u_eq={u_eq:.2f}, u_sw={u_sw:.2f}, u_total={u:.2f}")
```

## Example 5: Performance Profiling

```python
import time

# Benchmark equivalent control computation
n_iterations = 1000
start = time.time()

for _ in range(n_iterations):
    u_eq = eq_control.compute(state)

elapsed = time.time() - start
time_per_call = (elapsed / n_iterations) * 1e6  # microseconds

print(f"Equivalent control time: {time_per_call:.2f} μs per call")
print(f"Can achieve ~{1e6 / time_per_call:.0f} Hz control rate")
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/core/equivalent_control.py
:language: python
:linenos:
```



## Classes

### `EquivalentControl`

Model-based equivalent control computation for SMC.

Computes the control input that would maintain the system exactly on the
sliding surface if the model were perfect and no disturbances were present.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/equivalent_control.py
:language: python
:pyobject: EquivalentControl
:linenos:
```

#### Methods (7)

##### `__init__(self, dynamics_model, regularization, regularization_alpha, min_regularization, max_condition_number, use_fixed_regularization, controllability_threshold)`

Initialize equivalent control computation.

[View full source →](#method-equivalentcontrol-__init__)

##### `compute(self, state, sliding_surface, surface_derivative)`

Compute equivalent control input.

[View full source →](#method-equivalentcontrol-compute)

##### `_extract_dynamics_matrices(self, state)`

Extract inertia matrix M and force vector F from dynamics model.

[View full source →](#method-equivalentcontrol-_extract_dynamics_matrices)

##### `_get_surface_gradient(self, sliding_surface)`

Get surface gradient L from sliding surface object.

[View full source →](#method-equivalentcontrol-_get_surface_gradient)

##### `check_controllability(self, state, sliding_surface)`

Analyze system controllability at current state.

[View full source →](#method-equivalentcontrol-check_controllability)

##### `set_controllability_threshold(self, threshold)`

Update controllability threshold.

[View full source →](#method-equivalentcontrol-set_controllability_threshold)

##### `get_dynamics_info(self, state)`

Get information about dynamics matrices at current state.

[View full source →](#method-equivalentcontrol-get_dynamics_info)



## Dependencies

This module imports:

- `from typing import Optional, Any, Tuple`
- `import numpy as np`
- `import logging`
- `from abc import ABC, abstractmethod`
- `from src.plant.core.numerical_stability import MatrixInverter, AdaptiveRegularizer`
