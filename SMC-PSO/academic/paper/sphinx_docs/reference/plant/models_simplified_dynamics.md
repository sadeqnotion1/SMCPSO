# plant.models.simplified.dynamics

<!-- Enhanced by Week 8 Phase 2 --> **Source:** `src\plant\models\simplified\dynamics.py` ## Module Overview Simplified DIP Dynamics Model. Main dynamics model implementation combining all simplified DIP components.
Provides a clean, modular interface for the simplified double inverted
pendulum dynamics with numerical stability and performance optimizations. ## Architecture Diagram ```{mermaid}
graph TD A[State x, Control u] --> B[Mass Matrix M_q_] A --> C[Coriolis Matrix C_q,q̇_] A --> D[Gravity Vector G_q_] A --> E[Input Matrix B] B --> F[Invert M] C --> G[Compute Forces] D --> G E --> G F --> H[M^-1_] G --> I[Total Force F] H --> J[Solve: ẍ = M^-1__F-Cq̇-G_+Bu_] I --> J J --> K[State Derivative ẋ] K --> L[Return: θ̈_1_, θ̈_2_, ẍ] style B fill:#9cf style C fill:#fcf style D fill:#ff9 style J fill:#f9f style L fill:#9f9
``` **Data Flow:**
1. Extract generalized coordinates q = [x, θ₁, θ₂]
2. Compute configuration-dependent matrices M, C, G
3. Apply control input u via input matrix B
4. Solve second-order dynamics: Mq̈ + Cq̇ + G = Bu
5. Return accelerations [ẍ, θ̈₁, θ̈₂] for integration ## Mathematical Foundation ### Double-Inverted Pendulum Dynamics Lagrangian formulation: ```{math}
\vec{M}(\vec{q})\ddot{\vec{q}} + \vec{C}(\vec{q},\dot{\vec{q}})\dot{\vec{q}} + \vec{G}(\vec{q}) = \vec{B}\vec{u}
``` Where:

- $\vec{q} = [x, \theta_1, \theta_2]^T$: Generalized coordinates
- $\vec{M}(\vec{q})$: Mass matrix (configuration-dependent)
- $\vec{C}$: Coriolis/centrifugal matrix
- $\vec{G}$: Gravitational vector
- $\vec{B}$: Input matrix **See:** {doc}`../../../plant/complete_dynamics_derivation` ## Complete Source Code ```{literalinclude} ../../../src/plant/models/simplified/dynamics.py
:language: python
:linenos:
```

---

## Classes

### `SimplifiedDIPDynamics`

**Inherits from:** `BaseDynamicsModel` Simplified Double Inverted Pendulum Dynamics Model. Modular implementation of simplified DIP dynamics featuring:
- Type-safe configuration with validation
- Numerical stability monitoring and recovery
- Performance optimizations with JIT compilation
- Clean separation of physics computation
- state validation #### Source Code ```{literalinclude} ../../../src/plant/models/simplified/dynamics.py
:language: python
:pyobject: SimplifiedDIPDynamics
:linenos:
``` #### Methods (17) ##### `__init__(self, config, enable_fast_mode, enable_monitoring)` Initialize simplified DIP dynamics. [View full source →](#method-simplifieddipdynamics-__init__) ##### `_filter_config_for_simplified(self, config_dict)` Filter configuration dictionary to only include fields accepted by SimplifiedDIPConfig. [View full source →](#method-simplifieddipdynamics-_filter_config_for_simplified) ##### `compute_dynamics(self, state, control_input, time)` Compute simplified DIP dynamics. [View full source →](#method-simplifieddipdynamics-compute_dynamics) ##### `get_physics_matrices(self, state)` Get physics matrices M, C, G at current state. [View full source →](#method-simplifieddipdynamics-get_physics_matrices) ##### `compute_total_energy(self, state)` Compute total system energy. [View full source →](#method-simplifieddipdynamics-compute_total_energy) ##### `compute_linearization(self, equilibrium_state, equilibrium_input)` Compute linearization around equilibrium point. [View full source →](#method-simplifieddipdynamics-compute_linearization) ##### `get_equilibrium_states(self)` Get standard equilibrium states for the DIP system. [View full source →](#method-simplifieddipdynamics-get_equilibrium_states) ##### `_setup_validation(self)` Setup state validation for simplified DIP. [View full source →](#method-simplifieddipdynamics-_setup_validation) ##### `_compute_standard_dynamics(self, state, control_input)` Compute dynamics using standard (modular) approach. [View full source →](#method-simplifieddipdynamics-_compute_standard_dynamics) ##### `_compute_fast_dynamics(self, state, control_input)` Compute dynamics using fast JIT-compiled approach. [View full source →](#method-simplifieddipdynamics-_compute_fast_dynamics) ##### `_validate_control_input(self, control_input)` Validate control input vector. [View full source →](#method-simplifieddipdynamics-_validate_control_input) ##### `_validate_state_derivative(self, state_derivative)` Validate computed state derivative. [View full source →](#method-simplifieddipdynamics-_validate_state_derivative) ##### `_compute_linearization_matrices(self, eq_state, eq_input)` Compute linearization matrices A, B. [View full source →](#method-simplifieddipdynamics-_compute_linearization_matrices) ##### `_record_successful_computation(self, state)` Record successful computation for monitoring. [View full source →](#method-simplifieddipdynamics-_record_successful_computation) ##### `_record_numerical_instability(self, state)` Record numerical instability for monitoring. [View full source →](#method-simplifieddipdynamics-_record_numerical_instability) ##### `_record_computation_failure(self, state)` Record general computation failure for monitoring. [View full source →](#method-simplifieddipdynamics-_record_computation_failure) ##### `_rhs_core(self, state, u)` Compatibility method for legacy code expecting _rhs_core. [View full source →](#method-simplifieddipdynamics-_rhs_core)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Tuple, Optional, Dict, Any, Union`
- `import numpy as np`
- `import warnings`
- `from ..base import BaseDynamicsModel, DynamicsResult`
- `from ...core import DIPStateValidator, NumericalInstabilityError, NumericalStabilityMonitor`
- `from .config import SimplifiedDIPConfig`
- `from .physics import SimplifiedPhysicsComputer, compute_simplified_dynamics_numba` ## Usage Examples ### Model Instantiation & Configuration ```python
from src.plant.models.simplified import SimplifiedDynamics
from src.plant.models.full import FullDynamics
from src.plant.configurations import DIPPhysicsConfig # Simplified dynamics (fast, linearized friction)
simplified = SimplifiedDynamics( cart_mass=1.0, pole1_mass=0.1, pole2_mass=0.05, pole1_length=0.5, pole2_length=0.25, friction_cart=0.1
) # Full nonlinear dynamics (high fidelity)
full = FullDynamics( config=DIPPhysicsConfig( cart_mass=1.0, pole1_mass=0.1, pole2_mass=0.05, pole1_length=0.5, pole2_length=0.25, friction_cart=0.1, friction_pole1=0.01, friction_pole2=0.01 )
) # Compute dynamics at a state
state = [0.1, 0.2, 0.1, 0, 0, 0] # [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
control = 10.0 state_derivative = simplified.compute_dynamics(state, control, t=0)
print(f"Accelerations: {state_derivative[3:]}") # [ẍ, θ̈₁, θ̈₂]
``` ### Energy Analysis & Conservation ```python
import numpy as np
import matplotlib.pyplot as plt # Simulate and track energy
dynamics = SimplifiedDynamics()
states = [initial_state]
energies = [] for t in np.arange(0, 10, 0.01): state = states[-1] u = controller.compute_control(state, t) # Compute energy before step E = dynamics.compute_total_energy(state) energies.append(E) # Integrate x_dot = dynamics.compute_dynamics(state, u, t) next_state = state + 0.01 * x_dot states.append(next_state) # Plot energy conservation
plt.plot(energies)
plt.xlabel('Time step')
plt.ylabel('Total Energy (J)')
plt.title('Energy Conservation Analysis')
plt.grid(True)
plt.show() energy_drift = abs(energies[-1] - energies[0]) / energies[0] * 100
print(f"Energy drift: {energy_drift:.2f}%")
``` ### Linearization at Equilibrium ```python
# example-metadata:

# runnable: false #

Linearize around upright equilibrium

equilibrium_state = [0, 0, 0, 0, 0, 0] # Upright, stationary
equilibrium_control = 0.0 A, B = dynamics.compute_linearization(equilibrium_state, equilibrium_control) print("A matrix (state dynamics):")
print(A)
print("
B matrix (control influence):")
print(B) # Analyze stability of linearized system
eigenvalues = np.linalg.eigvals(A)
print(f"
Eigenvalues: {eigenvalues}")
print(f"Unstable modes: {sum(np.real(eigenvalues) > 0)}")
``` ### Model Comparison Study ```python
from src.plant.models import SimplifiedDynamics, FullDynamics, LowRankDynamics models = { 'Simplified': SimplifiedDynamics(), 'Full': FullDynamics(), 'LowRank': LowRankDynamics()
} # Compare computational cost
import time
state = [0.1, 0.2, 0.1, 0, 0, 0]
control = 10.0 for name, model in models.items(): start = time.perf_counter() for _ in range(10000): model.compute_dynamics(state, control, 0) elapsed = time.perf_counter() - start print(f"{name}: {elapsed*1000:.2f}ms for 10k evaluations") print(f" → {elapsed/10000*1e6:.2f}µs per call")
``` **See:** {doc}`../../../plant/dynamics_comparison_study` 