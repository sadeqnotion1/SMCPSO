# plant.core.dynamics

<!-- Enhanced by Week 8 Phase 2 --> **Source:** `src\plant\core\dynamics.py` ## Module Overview Plant core dynamics compatibility module. This module provides backward compatibility for test modules that expect
plant dynamics components at src.plant.core.dynamics. All functionality
is re-exported from the actual implementation locations. ## Architecture Diagram ```{mermaid}
graph TD A[State x, Control u] --> B[Extract Coordinates] B --> C[q = x_0:3_] B --> D[q̇ = x_3:6_] C --> E[compute_mass_matrix_q_] C --> F[compute_gravity_vector_q_] D --> G[compute_coriolis_matrix_q, q̇_] E --> H[M_q_] F --> I[G_q_] G --> J[C_q, q̇_] H --> K[robust_inverse_M_] K --> L[M⁻¹] L --> M[Solve: q̈ = M⁻¹_Bu - Cq̇ - G_] J --> M I --> M M --> N[Assemble ẋ = _q̇ᵀ, q̈ᵀ_ᵀ] N --> O[validate_state_ẋ_] O --> P[Return State Derivative] style E fill:#9cf style F fill:#fcf style G fill:#ff9 style K fill:#f9f style M fill:#9f9
``` ## Enhanced Mathematical Foundation ### Lagrangian Mechanics Framework The double inverted pendulum (DIP) dynamics are derived using **Lagrangian mechanics**, a formalism for deriving equations of motion from energy principles. **Lagrangian Definition:** $$
\mathcal{L}(q, \dot{q}) = T(q, \dot{q}) - V(q)
$$ where:
- $T(q, \dot{q})$ is the **kinetic energy** (function of positions and velocities)
- $V(q)$ is the **potential energy** (function of positions only)
- $q = [x, \theta_1, \theta_2]^T$ are the **generalized coordinates** **Euler-Lagrange Equations:** The equations of motion are obtained from the Euler-Lagrange equation: $$
\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}_i}\right) - \frac{\partial \mathcal{L}}{\partial q_i} = \tau_i
$$ for each generalized coordinate $q_i$ and generalized force $\tau_i$. ### Dynamics in Standard Form After applying the Euler-Lagrange equations and symbolic differentiation, the DIP dynamics take the **manipulator equation form**: $$
M(q)\ddot{q} + C(q,\dot{q})\dot{q} + G(q) = \tau
$$ where:
- $M(q) \in \mathbb{R}^{3 \times 3}$ is the **mass (inertia) matrix** (symmetric positive-definite)
- $C(q,\dot{q}) \in \mathbb{R}^{3 \times 3}$ is the **Coriolis matrix**
- $G(q) \in \mathbb{R}^{3}$ is the **gravity vector**
- $\tau \in \mathbb{R}^{3}$ is the **generalized force vector** **Control Input Mapping:** For the DIP with horizontal force input $u$: $$
\tau = B u, \quad B = [1, 0, 0]^T
$$ ### Properties of Physics Matrices **Mass Matrix Properties:** 1. **Symmetric:** $M(q) = M(q)^T$ (follows from kinetic energy symmetry)
2. **Positive-Definite:** $x^T M(q) x > 0$ for all $x \neq 0$ (physical realizability)
3. **Configuration-Dependent:** $M(q)$ varies with joint angles but not velocities
4. **Bounded:** $m_{\min} I \preceq M(q) \preceq m_{\max} I$ for all $q$ **Coriolis Matrix Properties:** 1. **Velocity-Dependent:** $C(q, \dot{q})$ linear in $\dot{q}$
2. **Skew-Symmetry:** $\dot{M}(q) - 2C(q, \dot{q})$ is skew-symmetric
3. **Energy Conservation:** Ensures passivity of the mechanical system **Gravity Vector Properties:** 1. **Conservative:** Derived from potential energy $G(q) = \nabla_q V(q)$
2. **Configuration-Only:** Independent of velocities
3. **Bounded:** $\|G(q)\| \leq g_{\max}$ for all $q$ ### State-Space Representation Convert second-order dynamics to first-order form: $$
\dot{x} = \begin{bmatrix} \dot{q} \\ \ddot{q} \end{bmatrix} = \begin{bmatrix} \dot{q} \\ M(q)^{-1}(Bu - C(q,\dot{q})\dot{q} - G(q)) \end{bmatrix}
$$ with state vector: $$
x = [x, \theta_1, \theta_2, \dot{x}, \dot{\theta}_1, \dot{\theta}_2]^T \in \mathbb{R}^6
$$ ### Energy Conservation (Ideal System) In the absence of control inputs and friction: $$
\frac{d}{dt}E(x) = \frac{d}{dt}\left(\frac{1}{2}\dot{q}^T M(q) \dot{q} + V(q)\right) = 0
$$ This **total energy** $E(x) = T + V$ is conserved, providing a critical validation test for numerical integrators. **Numerical Drift Monitoring:** $$
\Delta E = |E(x(t)) - E(x(0))| / E(x(0)) \ll 1
$$ Typical threshold: $\Delta E < 0.01$ (1% energy drift over simulation duration). ### Computational Workflow 1. **Extract Generalized Coordinates:** $q = x[0:3]$, $\dot{q} = x[3:6]$
2. **Compute Physics Matrices:** $M(q)$, $C(q, \dot{q})$, $G(q)$
3. **Apply Control Input:** $\tau = Bu$
4. **Solve for Accelerations:** $\ddot{q} = M(q)^{-1}(\tau - C(q,\dot{q})\dot{q} - G(q))$
5. **Assemble State Derivative:** $\dot{x} = [\dot{q}^T, \ddot{q}^T]^T$ ### References 1. **Murray, Li, Sastry** (1994). *A Mathematical Introduction to Robotic Manipulation*. CRC Press. Chapter 4.
2. **Spong, Hutchinson, Vidyasagar** (2006). *Robot Modeling and Control*. Wiley. Chapter 7.
3. **Khalil, Dombre** (2004). *Modeling, Identification and Control of Robots*. Taylor & Francis. Chapter 9. ## Usage Examples ### Example 1: Basic Usage Initialize and use the Core Dynamics module: ```python
from src.plant.core.dynamics import *
import numpy as np # Basic initialization
# Create dynamics model with standard parameters
from src.plant.models.simplified import SimplifiedDIPDynamics
from src.plant.configurations import get_default_config config = get_default_config()
dynamics = SimplifiedDIPDynamics(config) # Compute state derivative
state = np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0]) # [x, θ1, θ2, ẋ, θ̇1, θ̇2]
control = np.array([5.0]) # Force in Newtons
state_dot = dynamics.step(state, control, t=0.0)
print(f"State derivative: {state_dot}")
``` ### Example 2: Advanced Configuration Configure with custom parameters: ```python

from src.plant.models.simplified import SimplifiedDIPDynamics # numerical stability features
dynamics = SimplifiedDIPDynamics( config=config, enable_energy_monitoring=True, numerical_tolerance=1e-8, use_numba=True # JIT compilation for performance
) # Configure integration parameters
dynamics.set_integration_params( method='rk45', atol=1e-8, rtol=1e-6
)
``` ### Example 3: Error Handling Robust error handling and recovery: ```python
from src.plant.exceptions import ( NumericalInstabilityError, StateValidationError, ConfigurationError
) try: # Risky operation state_dot = dynamics.step(state, control, t) except NumericalInstabilityError as e: print(f"Numerical instability detected: {e}") # Fallback: reduce timestep, increase regularization dynamics.reset_numerical_params(stronger_regularization=True) except StateValidationError as e: print(f"Invalid state: {e}") # Fallback: clip state to valid bounds state = validator.clip_to_valid(state) except ConfigurationError as e: print(f"Configuration error: {e}") # Fallback: use default configuration config = get_default_config()
``` ### Example 4: Performance Optimization Optimize for computational efficiency: ```python

import time
from numba import njit # Numba JIT compilation for hot loops
@njit
def batch_dynamics_step(states, controls, params): """Vectorized dynamics computation.""" N = states.shape[0] state_dots = np.zeros_like(states) for i in range(N): state_dots[i] = dynamics_core_numba(states[i], controls[i], params) return state_dots # Benchmark
N = 1000
states = np.random.randn(N, 6)
controls = np.random.randn(N, 1) start = time.perf_counter()
results = batch_dynamics_step(states, controls, params)
elapsed = time.perf_counter() - start print(f"Processed {N} states in {elapsed*1000:.2f}ms")
print(f"Throughput: {N/elapsed:.0f} states/sec")
``` ### Example 5: Integration with Controllers Integrate with control systems: ```python
from src.controllers import ClassicalSMC
from src.core.simulation_runner import SimulationRunner # Create dynamics model
dynamics = SimplifiedDIPDynamics(config) # Create controller
controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01
) # Run closed-loop simulation
runner = SimulationRunner( controller=controller, dynamics=dynamics, duration=5.0, dt=0.01
) result = runner.run( initial_state=np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])
) print(f"Final state: {result.states[-1]}")
print(f"Settling time: {result.settling_time:.2f}s")
print(f"Control effort: {result.control_effort:.2f}")
``` ## Complete Source Code ```{literalinclude} ../../../src/plant/core/dynamics.py

:language: python
:linenos:
```

---

## Dependencies This module imports: - `from ...core.dynamics import *`
- `from ..models.dynamics import *`
- `from ...core.dynamics import DIPDynamics, DoubleInvertedPendulum, DIPParams`
