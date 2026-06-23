# Plant Models Guide

**Double Inverted Pendulum Dynamics Models**

> A guide to the physics models, mathematical foundations, and implementation architecture for the double inverted pendulum plant system.

## Table of Contents

1. [Overview](#overview)
2. [Physical System Description](#physical-system-description)
3. [Model Architecture](#model-architecture)
4. [Model Types](#model-types)
5. [Configuration System](#configuration-system)
6. [Physics Computation](#physics-computation)
7. [Numerical Stability](#numerical-stability)
8. [Mathematical Foundations](#mathematical-foundations)
9. [Usage Examples](#usage-examples)
10. [Performance Optimization](#performance-optimization)
11. [API Reference](#api-reference)

---

## Overview {#overview}

The plant module provides three dynamics models for the double inverted pendulum (DIP) system, each optimized for different use cases:

| Model Type | Fidelity | Speed | Use Case |
|------------|----------|-------|----------|
| **Simplified** | Medium | Fast | Controller development, PSO optimization |
| **Full** | High | Moderate | Research-grade analysis, studies |
| **Low-Rank** | Low | Very Fast | Educational demonstrations, rapid prototyping |

### Key Features

- **Modular Architecture**: Clean separation of dynamics, physics, and configuration
- **Type-Safe Configuration**: Dataclass-based validation with physical constraints
- **Numerical Stability**: Adaptive regularization for matrix conditioning
- **Performance Optimization**: Numba JIT compilation and matrix caching
- **Protocol-Based Design**: Consistent interfaces across all model types
- **Monitoring**: Energy conservation tracking and diagnostics

---

## Physical System Description {#physical-system-description}

The double inverted pendulum consists of:

1. **Cart** (mass $m_0$): Moves horizontally on a track with position $x$
2. **Pendulum 1** (mass $m_1$, length $L_1$): Attached to cart at angle $\theta_1$
3. **Pendulum 2** (mass $m_2$, length $L_2$): Attached to pendulum 1 at angle $\theta_2$

### State Vector

The system state is represented by a 6-dimensional vector:

$$
\mathbf{q} = \begin{bmatrix} x & \theta_1 & \theta_2 & \dot{x} & \dot{\theta}_1 & \dot{\theta}_2 \end{bmatrix}^T
$$

Where:

- $x$ - Cart position (m)
- $\theta_1$ - Pendulum 1 angle from upright (rad)
- $\theta_2$ - Pendulum 2 angle from upright (rad)
- $\dot{x}$ - Cart velocity (m/s)
- $\dot{\theta}_1$ - Pendulum 1 angular velocity (rad/s)
- $\dot{\theta}_2$ - Pendulum 2 angular velocity (rad/s)

### Control Input

The control input is a scalar force applied to the cart:

$$
u = F \quad \text{(N)}
$$

### Equations of Motion

The system dynamics follow the Euler-Lagrange equations:

$$
M(\mathbf{q}) \ddot{\mathbf{q}} + C(\mathbf{q}, \dot{\mathbf{q}}) \dot{\mathbf{q}} + G(\mathbf{q}) = \mathbf{u} + \mathbf{d}
$$

Where:

- $M(\mathbf{q})$ - Configuration-dependent inertia matrix (3×3)
- $C(\mathbf{q}, \dot{\mathbf{q}})$ - Coriolis and centrifugal forces matrix
- $G(\mathbf{q})$ - Gravity vector
- $\mathbf{u}$ - Control input vector $[F, 0, 0]^T$
- $\mathbf{d}$ - Disturbance vector (friction, aerodynamics)

---

## Model Architecture {#model-architecture}

The plant module uses a layered architecture with clear separation of concerns:

```
src/plant/models/
├── base/ # Abstract interfaces
│ └── dynamics_interface.py # Protocol and base classes
├── simplified/ # Simplified model implementation
│ ├── config.py # Type-safe configuration
│ ├── dynamics.py # Main dynamics class
│ └── physics.py # Physics computation
├── full/ # Full-fidelity model
│ ├── config.py
│ ├── dynamics.py
│ └── physics.py
└── lowrank/ # Low-rank model
    ├── config.py
    ├── dynamics.py
    └── physics.py
```

### Design Principles

1. **Protocol-Based Interfaces**: All models implement `DynamicsModel` protocol
2. **Composition Over Inheritance**: Physics computation delegated to separate classes
3. **Dependency Injection**: Configuration passed at initialization
4. **Single Responsibility**: Each module has one clear purpose
5. **Type Safety**: type hints for compile-time error detection

### Base Interface: DynamicsModel Protocol

All dynamics models must implement this protocol:

```python
# example-metadata:
# runnable: false

from typing import Protocol, Tuple
import numpy as np

class DynamicsModel(Protocol):
    """Protocol for plant dynamics models."""

    def compute_dynamics(
        self,
        state: np.ndarray,
        control_input: np.ndarray,
        time: float = 0.0,
        **kwargs
    ) -> DynamicsResult:
        """Compute system dynamics at given state and input."""
        ...

    def get_physics_matrices(
        self,
        state: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get M, C, G matrices at current state."""
        ...

    def validate_state(self, state: np.ndarray) -> bool:
        """Validate state vector format and bounds."""
        ...
```

**Implementation:** [`src/plant/models/base/dynamics_interface.py:65-128`](../../src/plant/models/base/dynamics_interface.py#L65-L128)

### DynamicsResult Structure

Dynamics computations return a structured result:

```python
from typing import NamedTuple, Dict, Any

class DynamicsResult(NamedTuple):
    """Result of dynamics computation."""
    state_derivative: np.ndarray  # dx/dt vector
    success: bool  # Computation succeeded
    info: Dict[str, Any]  # Diagnostics and metadata
```

This provides:

- **Type Safety**: Named fields prevent field ordering errors
- **Diagnostics**: Rich metadata for debugging and analysis
- **Error Handling**: Explicit success/failure indication

---

## Model Types {#model-types}

### Simplified DIP Dynamics

**Purpose**: Balanced speed and accuracy for controller development and PSO optimization.

**Features**:

- Moderate computational complexity
- Essential nonlinear dynamics captured
- Optional Numba JIT compilation for speed
- Adaptive numerical regularization
- Energy conservation tracking

**Source:** [`src/plant/models/simplified/dynamics.py`](../../src/plant/models/simplified/dynamics.py)

**Typical Usage**:

```python
from src.plant.models.simplified import SimplifiedDIPDynamics, SimplifiedDIPConfig

# Create configuration
config = SimplifiedDIPConfig.create_default()

# Initialize dynamics model
dynamics = SimplifiedDIPDynamics(
    config=config,
    enable_fast_mode=True,  # Use Numba JIT compilation
    enable_monitoring=True  # Track performance metrics
)

# Compute dynamics
state = np.array([0.1, 0.05, -0.03, 0.0, 0.0, 0.0])
control = np.array([5.0])
result = dynamics.compute_dynamics(state, control)

if result.success:
    state_derivative = result.state_derivative
    energy = result.info['total_energy']
    print(f"Energy: {energy:.4f} J")
else:
    print(f"Error: {result.info['failure_reason']}")
```

### Full-Fidelity DIP Dynamics

**Purpose**: Research-grade high-fidelity simulation with all nonlinear effects.

**Features**:

- Complete nonlinear dynamics
- Advanced friction models (viscous + Coulomb)
- Aerodynamic forces and wind effects
- energy analysis
- Integration quality metrics
- Detailed diagnostics

**Source:** [`src/plant/models/full/dynamics.py`](../../src/plant/models/full/dynamics.py)

**Typical Usage**:

```python
from src.plant.models.full import FullDIPDynamics, FullDIPConfig

# Create high-fidelity configuration
config = FullDIPConfig.create_default()

# Initialize with monitoring
dynamics = FullDIPDynamics(
    config=config,
    enable_monitoring=True,
    enable_validation=True
)

# Compute dynamics with wind effects
wind_velocity = np.array([0.5, 0.0])  # 0.5 m/s horizontal wind
result = dynamics.compute_dynamics(
    state, control, time=1.5, wind_velocity=wind_velocity
)

# Access detailed diagnostics
if result.success:
    print(f"Total energy: {result.info['total_energy']:.4f} J")
    print(f"Cart kinetic: {result.info['kinetic_cart']:.4f} J")
    print(f"Friction forces: {result.info['friction_forces']}")
    print(f"Aerodynamic forces: {result.info['aerodynamic_forces']}")
```

### Low-Rank DIP Dynamics

**Purpose**: Fast prototyping, educational demonstrations, real-time applications.

**Features**:

- Simplified computational complexity
- Optional linearization for stability analysis
- Small-angle approximations available
- Minimal dependencies
- Educational clarity

**Source:** [`src/plant/models/lowrank/dynamics.py`](../../src/plant/models/lowrank/dynamics.py)

**Typical Usage**:

```python
from src.plant.models.lowrank import LowRankDIPDynamics, LowRankDIPConfig

# Create lightweight configuration
config = LowRankDIPConfig.create_default()

# Initialize for fast computation
dynamics = LowRankDIPDynamics(
    config=config,
    enable_monitoring=False,  # Disable for maximum speed
    enable_validation=True
)

# Use linearized dynamics for control design
A, B = dynamics.get_linearized_system(equilibrium_point="upright")

# Or compute full nonlinear dynamics
result = dynamics.compute_dynamics(state, control)

# Simple Euler integration step
next_state = dynamics.step(state, control, dt=0.01)
```

---

## Configuration System {#configuration-system}

Each model uses a type-safe dataclass-based configuration with validation.

### SimplifiedDIPConfig

**Source:** [`src/plant/models/simplified/config.py`](../../src/plant/models/simplified/config.py)

```python
# example-metadata:
# runnable: false

@dataclass(frozen=True)
class SimplifiedDIPConfig:
    """Type-safe configuration for simplified DIP."""

    # Physical parameters - masses (kg)
    cart_mass: float
    pendulum1_mass: float
    pendulum2_mass: float

    # Lengths (m)
    pendulum1_length: float
    pendulum2_length: float
    pendulum1_com: float  # Center of mass distance
    pendulum2_com: float

    # Inertias (kg⋅m²)
    pendulum1_inertia: float
    pendulum2_inertia: float

    # Environmental
    gravity: float = 9.81

    # Friction (N⋅s/m or N⋅m⋅s/rad)
    cart_friction: float = 0.1
    joint1_friction: float = 0.01
    joint2_friction: float = 0.01

    # Numerical stability
    regularization_alpha: float = 1e-4
    max_condition_number: float = 1e14
    min_regularization: float = 1e-10
```

### Physical Constraint Validation

The configuration enforces physical laws:

1. **Mass Positivity**: All masses must be $> 0$ (conservation of mass)
2. **Length Positivity**: All lengths must be $> 0$ (geometric requirement)
3. **Inertia Bounds**: Inertias constrained by parallel axis theorem
4. **Center of Mass**: $L_{c,i} \leq L_i$ (COM within pendulum length)
5. **Friction Non-negativity**: Friction coefficients $\geq 0$ (energy dissipation)

**Inertia bounds** based on physics:

$$
m_i \cdot L_{c,i}^2 \leq I_i \leq \frac{1}{3} m_i L_i^2
$$

Where:

- Lower bound: Point mass at COM
- Upper bound: Uniform rod about end point

**Implementation:** [`src/plant/models/simplified/config.py:145-183`](../../src/plant/models/simplified/config.py#L145-L183)

### Factory Methods

Configurations provide convenient factory methods:

```python
# example-metadata:
# runnable: false

# Default parameters (balanced for general use)
config = SimplifiedDIPConfig.create_default()

# Benchmark parameters (standardized for comparisons)
config = SimplifiedDIPConfig.create_benchmark()

# Lightweight parameters (optimized for speed)
config = SimplifiedDIPConfig.create_lightweight()

# Custom parameters
config = SimplifiedDIPConfig(
    cart_mass=1.2,
    pendulum1_mass=0.15,
    pendulum2_mass=0.15,
    # ... all required fields
)
```

### Characteristic Scales

Configurations compute characteristic scales:

```python
# Total system mass
total_mass = config.get_total_mass()

# Characteristic length (max pendulum length)
L_char = config.get_characteristic_length()

# Characteristic time (natural period)
T_char = config.get_characteristic_time()  # sqrt(L/g)

# Natural frequency estimate
omega_n = config.estimate_natural_frequency()  # 1/T_char
```

---

## Physics Computation {#physics-computation}

Physics computation is delegated to specialized classes for modularity and testability.

### Simplified Physics Computer

**Source:** [`src/plant/models/simplified/physics.py`](../../src/plant/models/simplified/physics.py)

The simplified physics computer handles matrix computation with numerical stability:

```python
# example-metadata:
# runnable: false

class SimplifiedPhysicsComputer:
    """Simplified physics computation for DIP."""

    def __init__(self, config: SimplifiedDIPConfig):
        self.config = config

        # Physics matrix computers
        self.full_matrices = DIPPhysicsMatrices(config)
        self.simplified_matrices = SimplifiedDIPPhysicsMatrices(config)

        # Numerical stability
        self.regularizer = AdaptiveRegularizer(config)
        self.matrix_inverter = MatrixInverter(self.regularizer)

        # Performance flags
        self.use_simplified_inertia = True
        self.cache_matrices = False
```

### Matrix Computation Pipeline

The dynamics equation solution involves:

1. **Matrix Computation**: $M(\mathbf{q})$, $C(\mathbf{q}, \dot{\mathbf{q}})$, $G(\mathbf{q})$
2. **Forcing Term**: $\mathbf{f} = \mathbf{u} - C \dot{\mathbf{q}} - G$
3. **Linear System Solution**: $M \ddot{\mathbf{q}} = \mathbf{f}$
4. **State Derivative**: $\frac{d\mathbf{q}}{dt} = [\dot{\mathbf{q}}, \ddot{\mathbf{q}}]^T$

**Implementation:**

```python
# example-metadata:
# runnable: false

def compute_dynamics_rhs(
    self,
    state: np.ndarray,
    control_input: np.ndarray
) -> np.ndarray:
    """Compute ẍ = M⁻¹(u - C·ẋ - G)."""

    # Extract state components
    position = state[:3]  # [x, theta1, theta2]
    velocity = state[3:]  # [x_dot, theta1_dot, theta2_dot]

    # Compute physics matrices
    M, C, G = self.get_physics_matrices(state)

    # Control vector (force on cart only)
    u = np.array([control_input[0], 0.0, 0.0])

    # Forcing term
    forcing = u - C @ velocity - G

    # Solve for accelerations: M·q̈ = forcing
    accelerations = self.matrix_inverter.solve_linear_system(M, forcing)

    # Construct state derivative
    return np.concatenate([velocity, accelerations])
```

**Source:** [`src/plant/models/simplified/physics.py:71-117`](../../src/plant/models/simplified/physics.py#L71-L117)

### Numba Optimization

For maximum performance, a JIT-compiled version is available:

```python
# example-metadata:
# runnable: false

from numba import njit

@njit
def compute_simplified_dynamics_numba(
    state, u,
    m0, m1, m2,  # Masses
    L1, L2, Lc1, Lc2,  # Lengths
    I1, I2,  # Inertias
    g, c0, c1, c2,  # Gravity and friction
    reg_alpha, min_reg  # Regularization
):
    """JIT-compiled dynamics computation."""
    # Inline matrix computation and solution
    # ... optimized implementation ...
    return state_derivative
```

This provides **10-100×** speedup for repeated evaluations (PSO optimization, batch simulation).

---

## Numerical Stability {#numerical-stability}

Numerical stability is critical for robust simulation of the DIP system, which can exhibit singular configurations.

### Adaptive Regularization

The system uses adaptive Tikhonov regularization:

$$
M_{\text{reg}} = M + \alpha_{\text{adaptive}} \cdot I
$$

Where $\alpha_{\text{adaptive}}$ is computed based on matrix conditioning:

```python
# example-metadata:
# runnable: false

class AdaptiveRegularizer:
    """Adaptive regularization for matrix conditioning."""

    def compute_regularization(self, matrix: np.ndarray) -> float:
        """Compute adaptive regularization parameter."""

        # Compute condition number
        cond_num = np.linalg.cond(matrix)

        if cond_num > self.max_condition_number:
            # Adaptive regularization scaled by condition number
            alpha = self.regularization_alpha * (cond_num / self.max_condition_number)
            return max(alpha, self.min_regularization)
        else:
            # Use fixed minimal regularization
            return self.min_regularization
```

### Matrix Inversion with Recovery

The matrix inverter provides robust inversion with error recovery:

```python
# example-metadata:
# runnable: false

class MatrixInverter:
    """Robust matrix inversion with regularization."""

    def solve_linear_system(
        self,
        A: np.ndarray,
        b: np.ndarray
    ) -> np.ndarray:
        """Solve Ax = b with adaptive regularization."""
        try:
            # Attempt direct solution
            return np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            # Apply adaptive regularization
            alpha = self.regularizer.compute_regularization(A)
            A_reg = A + alpha * np.eye(A.shape[0])
            try:
                return np.linalg.solve(A_reg, b)
            except np.linalg.LinAlgError:
                # Use pseudo-inverse as last resort
                return np.linalg.lstsq(A_reg, b, rcond=None)[0]
```

### Conditioning Monitoring

Numerical stability is tracked for diagnostics:

```python
# example-metadata:
# runnable: false

class NumericalStabilityMonitor:
    """Monitor numerical stability statistics."""

    def record_inversion(
        self,
        condition_number: float,
        was_regularized: bool,
        failed: bool
    ) -> None:
        """Record matrix inversion event."""
        self.condition_numbers.append(condition_number)
        self.regularization_count += int(was_regularized)
        self.failure_count += int(failed)
```

Statistics accessible via:

```python
stats = dynamics.get_monitoring_stats()
print(f"Average condition number: {stats['avg_condition_number']:.2e}")
print(f"Regularization rate: {stats['regularization_rate']:.2%}")
print(f"Failure rate: {stats['failure_rate']:.2%}")
```

---

## Mathematical Foundations {#mathematical-foundations}

### Lagrangian Mechanics

The DIP system is derived using Lagrangian mechanics.

The Lagrangian $\mathcal{L} = T - V$ where:

**Kinetic Energy** ($T$):

$$
T = \frac{1}{2} m_0 \dot{x}^2 + \frac{1}{2} m_1 (\dot{x}_1^2 + \dot{y}_1^2) + \frac{1}{2} I_1 \dot{\theta}_1^2 + \frac{1}{2} m_2 (\dot{x}_2^2 + \dot{y}_2^2) + \frac{1}{2} I_2 \dot{\theta}_2^2
$$

Where pendulum tip positions are:

$$
\begin{aligned}
x_1 &= x + L_{c1} \sin(\theta_1) \\
y_1 &= L_{c1} \cos(\theta_1) \\
x_2 &= x + L_1 \sin(\theta_1) + L_{c2} \sin(\theta_2) \\
y_2 &= L_1 \cos(\theta_1) + L_{c2} \cos(\theta_2)
\end{aligned}
$$

**Potential Energy** ($V$):

$$
V = m_1 g L_{c1} (1 - \cos\theta_1) + m_2 g [L_1(1 - \cos\theta_1) + L_{c2}(1 - \cos\theta_2)]
$$

**Euler-Lagrange Equations**:

$$
\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}_i}\right) - \frac{\partial \mathcal{L}}{\partial q_i} = Q_i
$$

Where $Q_i$ are generalized forces (control input, friction, disturbances).

**For full derivations:** See [`docs/mathematical_foundations/dynamics_derivations.md`](../mathematical_foundations/dynamics_derivations.md)

### Inertia Matrix Structure

The inertia matrix $M(\mathbf{q})$ is symmetric positive definite with structure:

$$
M(\mathbf{q}) = \begin{bmatrix}
m_{total} & m_{12} \cos\theta_1 & m_{13} \cos\theta_2 \\
m_{12} \cos\theta_1 & I_{11} & m_{23} \cos(\theta_1 - \theta_2) \\
m_{13} \cos\theta_2 & m_{23} \cos(\theta_1 - \theta_2) & I_{22}
\end{bmatrix}
$$

Where:

- $m_{total} = m_0 + m_1 + m_2$ (total system mass)
- Coupling terms depend on configuration via $\cos(\theta_i)$
- Diagonal dominance ensures positive definiteness

### Energy Conservation

For the unforced, frictionless system, total energy is conserved:

$$
E_{total} = T + V = \text{constant}
$$

This provides a validation criterion:

```python
# Compute energy at initial and current states
E_initial = dynamics.compute_total_energy(state_initial)
E_current = dynamics.compute_total_energy(state_current)

# Energy conservation error
energy_drift = abs(E_current - E_initial) / E_initial

# Validation threshold (accounts for numerical integration error)
assert energy_drift < tolerance, f"Energy drift: {energy_drift:.2%}"
```

**For energy conservation theory:** See [`docs/mathematical_foundations/numerical_integration_theory.md`](../mathematical_foundations/numerical_integration_theory.md)

---

## Usage Examples {#usage-examples}

### Example 1: Basic Simulation

```python
import numpy as np
from src.plant.models.simplified import SimplifiedDIPDynamics, SimplifiedDIPConfig

# Setup
config = SimplifiedDIPConfig.create_default()
dynamics = SimplifiedDIPDynamics(config, enable_fast_mode=True)

# Initial state (small perturbation from upright)
state = np.array([0.0, 0.1, -0.05, 0.0, 0.0, 0.0])

# Control input
control = np.array([5.0])  # 5 N force on cart

# Compute dynamics
result = dynamics.compute_dynamics(state, control, time=0.0)

if result.success:
    print(f"State derivative: {result.state_derivative}")
    print(f"Total energy: {result.info['total_energy']:.4f} J")
else:
    print(f"Computation failed: {result.info['failure_reason']}")
```

### Example 2: Energy Conservation Validation

```python
from scipy.integrate import solve_ivp

def dynamics_ode(t, state):
    """ODE right-hand side for scipy integration."""
    control = np.array([0.0])  # No control input
    result = dynamics.compute_dynamics(state, control, time=t)
    return result.state_derivative if result.success else np.zeros(6)

# Initial state with energy
state0 = np.array([0.0, 0.2, -0.15, 0.0, 0.1, -0.05])
E0 = dynamics.compute_total_energy(state0)

# Integrate for 5 seconds
sol = solve_ivp(dynamics_ode, t_span=[0, 5], y0=state0, method='RK45', rtol=1e-8)

# Check energy conservation
E_final = dynamics.compute_total_energy(sol.y[:, -1])
energy_drift = abs(E_final - E0) / E0

print(f"Initial energy: {E0:.6f} J")
print(f"Final energy: {E_final:.6f} J")
print(f"Energy drift: {energy_drift:.2e} ({energy_drift*100:.4f}%)")
```

### Example 3: Linearization for Control Design

```python
from src.plant.models.lowrank import LowRankDIPDynamics, LowRankDIPConfig

# Use low-rank model for fast linearization
config = LowRankDIPConfig.create_default()
dynamics = LowRankDIPDynamics(config)

# Get linearized system around upright equilibrium
A, B = dynamics.get_linearized_system(equilibrium_point="upright")

# Analyze controllability
from scipy.linalg import ctrb
C = ctrb(A, B)
rank = np.linalg.matrix_rank(C)

if rank == A.shape[0]:
    print("System is controllable ✓")
else:
    print(f"System rank deficient: {rank}/{A.shape[0]}")

# Compute eigenvalues
eigenvalues = np.linalg.eigvals(A)
print(f"Open-loop poles: {eigenvalues}")

# Check for unstable modes
unstable = np.any(np.real(eigenvalues) > 0)
print(f"Unstable: {unstable}")
```

### Example 4: Model Comparison

```python
# example-metadata:
# runnable: false

from src.plant.models.simplified import SimplifiedDIPDynamics
from src.plant.models.full import FullDIPDynamics
from src.plant.models.lowrank import LowRankDIPDynamics
import time

# Create all three models with same configuration
config_dict = {
    'cart_mass': 1.0,
    'pendulum1_mass': 0.1,
    'pendulum2_mass': 0.1,
    # ... (same parameters for all)
}

simplified = SimplifiedDIPDynamics(config_dict, enable_fast_mode=True)
full = FullDIPDynamics(config_dict)
lowrank = LowRankDIPDynamics(config_dict)

# Test state
state = np.array([0.0, 0.1, -0.05, 0.0, 0.0, 0.0])
control = np.array([5.0])

# Benchmark computation time
models = [('Simplified', simplified), ('Full', full), ('Low-Rank', lowrank)]

for name, model in models:
    start = time.perf_counter()
    for _ in range(1000):
        result = model.compute_dynamics(state, control)
    elapsed = time.perf_counter() - start
    print(f"{name:12s}: {elapsed*1000:.2f} ms (1000 evaluations)")
    print(f"             Energy: {result.info.get('total_energy', 0.0):.6f} J")
```

---

## Performance Optimization {#performance-optimization}

### Numba JIT Compilation

Fast mode for **10-100× speedup** in repeated evaluations:

```python
dynamics = SimplifiedDIPDynamics(
    config,
    enable_fast_mode=True,  # Use Numba JIT compilation
    enable_monitoring=False  # Disable monitoring for maximum speed
)
```

**When to use**:

- PSO optimization (thousands of dynamics evaluations)
- Monte Carlo validation (large batch simulations)
- Real-time applications (strict timing constraints)

**Trade-offs**:

- First call has compilation overhead (~1 second)
- Reduced diagnostic information
- No monitoring statistics

### Matrix Caching

matrix caching for repeated evaluations at similar states:

```python
physics = dynamics.physics
physics.enable_matrix_caching(True)
```

**Benefit**: Avoids recomputing $M$, $C$, $G$ for identical positions.

**When to use**:

- Fixed-point iterations
- Trajectory optimization with line search
- Iterative control algorithms

**Memory cost**: $O(n)$ where $n$ is number of unique position vectors.

### Simplified Inertia Matrix

Use simplified inertia computation:

```python
physics.set_simplified_inertia(True)
```

**Trade-off**: 2-5% accuracy reduction for 30-50% speed improvement.

**Recommended for**:

- Initial controller prototyping
- Preliminary PSO parameter tuning
- Educational demonstrations

---

## API Reference {#api-reference}

### SimplifiedDIPDynamics

**Location:** [`src/plant/models/simplified/dynamics.py`](../../src/plant/models/simplified/dynamics.py)

```python
# example-metadata:
# runnable: false

class SimplifiedDIPDynamics(BaseDynamicsModel):
    """Simplified DIP dynamics with balanced speed and accuracy."""

    def __init__(
        self,
        config: Union[SimplifiedDIPConfig, Dict[str, Any]],
        enable_fast_mode: bool = False,
        enable_monitoring: bool = True
    ):
        """
        Initialize simplified DIP dynamics.

        Args:
            config: Configuration or dictionary
            enable_fast_mode: Use Numba JIT compilation
            enable_monitoring: performance monitoring
        """

    def compute_dynamics(
        self,
        state: np.ndarray,
        control_input: np.ndarray,
        time: float = 0.0,
        **kwargs
    ) -> DynamicsResult:
        """Compute simplified DIP dynamics."""

    def get_physics_matrices(
        self,
        state: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get M, C, G matrices."""

    def compute_total_energy(self, state: np.ndarray) -> float:
        """Compute total system energy."""

    def compute_linearization(
        self,
        equilibrium_state: np.ndarray,
        equilibrium_input: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute linearization matrices A, B."""
```

### FullDIPDynamics

**Location:** [`src/plant/models/full/dynamics.py`](../../src/plant/models/full/dynamics.py)

```python
# example-metadata:
# runnable: false

class FullDIPDynamics(BaseDynamicsModel):
    """Full-fidelity DIP dynamics with physics."""

    def __init__(
        self,
        config: Union[FullDIPConfig, Dict[str, Any]],
        enable_monitoring: bool = True,
        enable_validation: bool = True
    ):
        """Initialize full-fidelity dynamics."""

    def compute_energy_analysis(
        self,
        state: np.ndarray
    ) -> Dict[str, float]:
        """Compute energy breakdown."""

    def compute_stability_metrics(
        self,
        state: np.ndarray
    ) -> Dict[str, float]:
        """Compute stability and conditioning metrics."""

    def set_wind_model(self, wind_function):
        """Set custom wind velocity function."""

    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration performance statistics."""
```

### LowRankDIPDynamics

**Location:** [`src/plant/models/lowrank/dynamics.py`](../../src/plant/models/lowrank/dynamics.py)

```python
# example-metadata:
# runnable: false

class LowRankDIPDynamics(BaseDynamicsModel):
    """Low-rank DIP dynamics for fast prototyping."""

    def __init__(
        self,
        config: Union[LowRankDIPConfig, Dict[str, Any]],
        enable_monitoring: bool = False,
        enable_validation: bool = True
    ):
        """Initialize low-rank dynamics."""

    def get_linearized_system(
        self,
        equilibrium_point: str = "upright",
        force_recompute: bool = False
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Get linearized system matrices."""

    def compute_linearized_dynamics(
        self,
        state: np.ndarray,
        control_input: np.ndarray,
        equilibrium_point: str = "upright"
    ) -> np.ndarray:
        """Compute dynamics using linearized model."""

    def step(
        self,
        state: np.ndarray,
        control_input: np.ndarray,
        dt: float
    ) -> np.ndarray:
        """Simple Euler integration step."""
```

---

## Related Documentation

- [**Dynamics Derivations**](../mathematical_foundations/dynamics_derivations.md) - Complete Lagrangian mechanics derivation
- [**Numerical Integration Theory**](../mathematical_foundations/numerical_integration_theory.md) - Integration methods and energy conservation
- [**Plant Configurations Reference**](../reference/plant/configurations_base_config.md) - Configuration system details
- [**State Validation Reference**](../reference/plant/core_state_validation.md) - State validation and sanitization
- [**Controller Integration**](../controllers/index.md) - Using models with SMC controllers

---

**Version:** Phase 3
**Last Updated:** October 2025
**Status:** Production-Ready ✓
