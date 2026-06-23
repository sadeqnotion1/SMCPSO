# Optimization & Simulation Guide

**PSO Optimization and Simulation Infrastructure**

> guide to particle swarm optimization, simulation engines, and the configuration system for the double inverted pendulum control framework.

---

## Table of Contents

1. [Overview](#overview)
2. [PSO Optimization](#pso-optimization)
3. [Simulation Infrastructure](#simulation-infrastructure)
4. [Configuration System](#configuration-system)
5. [Vectorized Batch Simulation](#vectorized-batch-simulation)
6. [Simulation Context](#simulation-context)
7. [Integration Methods](#integration-methods)
8. [Usage Examples](#usage-examples)
9. [Performance Optimization](#performance-optimization)
10. [API Reference](#api-reference)

---

## Overview

The optimization and simulation infrastructure provides:

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **PSO Optimizer** | Controller gain tuning | Vectorized evaluation, uncertainty handling, adaptive penalties |
| **Simulation Runner** | Sequential integration | Explicit Euler, latency monitoring, state management |
| **Vector Simulation** | Batch processing | Safety guards, early stopping, convergence detection |
| **Simulation Context** | Framework integration | Configuration loading, component registration, model selection |
| **Configuration System** | Parameter validation | Pydantic schemas, type safety, physical constraints | ### Architecture Diagram ```
┌─────────────────────────────────────────────────────────────┐
│ Configuration System │
│ (Pydantic Schemas: Physics, Simulation, Controllers, PSO) │
└────────────┬────────────────────────────────────┬───────────┘ │ │ ┌────────▼────────┐ ┌───────▼──────────┐ │ PSO Optimizer │◄─────────────────│ Vector Sim │ │ Cost Function │ batch evaluate │ Safety Guards │ │ Uncertainty │ │ Early Stopping │ └────────┬────────┘ └───────┬──────────┘ │ │ │ ┌───────────────────┐ │ └─────►│ Simulation Runner │◄────────┘ │ Euler Integration│ │ State Management │ └─────────┬─────────┘ │ ┌─────────▼──────────┐ │ Dynamics Models │ │ Simplified / Full │ └────────────────────┘
```

---

## PSO Optimization

### Overview

The PSO (Particle Swarm Optimization) tuner provides high-throughput, vectorized controller gain optimization with robust handling of instabilities and uncertainties.

**Source:** [`src/optimization/algorithms/pso_optimizer.py`](../../src/optimization/algorithms/pso_optimizer.py)

### Key Features

- **Vectorized Evaluation**: Batch simulation of particle swarm for performance
- **Uncertainty Handling**: Robustness evaluation with perturbed physics parameters
- **Adaptive Penalties**: Dynamic instability penalties based on failure severity
- **Cost Normalization**: Baseline-relative normalization for balanced optimization
- **Velocity Clamping**: Particle velocity constraints for convergence stability
- **Inertia Scheduling**: Linearly decreasing inertia for exploration-to-exploitation shift ### Cost Function Design The PSO cost function combines four components: $$
J = w_1 \cdot \frac{ISE}{n_{ISE}} + w_2 \cdot \frac{U^2}{n_U} + w_3 \cdot \frac{(\Delta U)^2}{n_{\Delta U}} + w_4 \cdot \frac{\sigma^2}{n_\sigma} + P_{fail}
$$ Where: 1. **Integral of Squared Error (ISE)** - State tracking performance $$ ISE = \int_0^T \|\mathbf{x}(t)\|^2 dt $$ 2. **Control Effort** - Energy consumption $$ U^2 = \int_0^T u(t)^2 dt $$ 3. **Control Rate** - Actuator stress and chattering $$ (\Delta U)^2 = \int_0^T \left(\frac{du}{dt}\right)^2 dt $$ 4. **Sliding Variable Energy** - SMC stability margin $$ \sigma^2 = \int_0^T \sigma(t)^2 dt $$ 5. **Instability Penalty** - Graded penalty for early failure $$ P_{fail} = w_4 \cdot \frac{T - t_{fail}}{T} \cdot P_{max} $$ **Normalization:** Each component is normalized by baseline performance to ensure balanced contributions regardless of problem scale. **Implementation:** [`src/optimization/algorithms/pso_optimizer.py:393-479`](../../src/optimization/algorithms/pso_optimizer.py#L393-L479) ### Uncertainty Evaluation PSO supports robust optimization under parametric uncertainty: ```python
from src.config import load_config config = load_config("config.yaml") # Configure physics uncertainty
config.physics_uncertainty.n_evals = 5 # Number of perturbed evaluations
config.physics_uncertainty.cart_mass = 0.1 # ±10% variation
config.physics_uncertainty.pendulum1_mass = 0.1
config.physics_uncertainty.pendulum2_mass = 0.1
``` **Uncertainty Sampling:**

- Nominal model evaluated first
- Subsequent draws perturb parameters within ±percent bounds
- Ensures COM remains within pendulum length (safety constraint) **Cost Aggregation:**
$$
J_{robust} = w_{mean} \cdot \text{mean}(J_i) + w_{max} \cdot \text{max}(J_i)
$$ Default weights: $(w_{mean}, w_{max}) = (0.7, 0.3)$ balances average and worst-case performance. **Implementation:** [`src/optimization/algorithms/pso_optimizer.py:348-390`](../../src/optimization/algorithms/pso_optimizer.py#L348-L390) ### PSO Configuration Configuration via `config.yaml`: ```yaml
pso: n_particles: 30 # Swarm size (recommended: 10-50) iters: 100 # Optimization iterations c1: 2.0 # Cognitive coefficient (self-confidence) c2: 2.0 # Social coefficient (swarm influence) w: 0.9 # Inertia weight (exploration vs exploitation) # Advanced features velocity_clamp: [0.1, 0.5] # Velocity limits as fraction of search space w_schedule: [0.9, 0.4] # Linear inertia decrease (exploration → exploitation) # Controller-specific gain bounds bounds: classical_smc: min: [0.1, 0.1, 0.1, 0.1, 1.0, 0.0] # [k1, k2, λ1, λ2, K, K_rate] max: [50.0, 50.0, 50.0, 50.0, 200.0, 50.0] adaptive_smc: min: [0.1, 0.1, 0.1, 0.1, 0.01] # [k1, k2, λ1, λ2, adapt_rate] max: [50.0, 50.0, 50.0, 50.0, 10.0] sta_smc: min: [0.5, 0.5, 0.5, 0.5, 0.1, 0.1] # [k1, k2, λ1, λ2, α, β] max: [100.0, 100.0, 100.0, 100.0, 50.0, 50.0] hybrid_adaptive_sta_smc: min: [0.5, 0.5, 0.5, 0.01] # [λ1, λ2, α, adapt_rate] max: [100.0, 100.0, 50.0, 10.0]
``` **Hyperparameter Guidelines:** | Parameter | Recommended Range | Effect |
|-----------|-------------------|--------|
| `n_particles` | 10-50 | Larger swarms explore better but cost more |
| `iters` | 50-200 | More iterations improve convergence |
| `c1`, `c2` | 1.5-2.5 | Balance personal best vs global best |
| `w` | 0.4-0.9 | Higher values favor exploration |
| `velocity_clamp` | [0.1, 0.5] | Prevents oscillations and divergence | ### Typical PSO Workflow ```python
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.controllers import create_smc_for_pso, SMCType
from src.config import load_config # Load configuration
config = load_config("config.yaml") # Define controller factory
def controller_factory(gains): return create_smc_for_pso(SMCType.CLASSICAL, gains, max_force=100.0) # Initialize PSO tuner
tuner = PSOTuner( controller_factory=controller_factory, config=config, seed=42, # Reproducibility instability_penalty_factor=100.0
) # Run optimization
result = tuner.optimise( iters_override=150, # Override config iterations n_particles_override=40 # Override config swarm size
) # Extract best gains
best_gains = result['best_pos']
best_cost = result['best_cost']
cost_history = result['history']['cost'] print(f"Best gains: {best_gains}")
print(f"Best cost: {best_cost:.4f}")
print(f"Iterations to convergence: {len(cost_history)}")
``` ### PSO Convergence Visualization Interactive convergence plots show optimization progress for different SMC controllers: ```{eval-rst}

.. chartjs:: :type: line :data: ../visualization/data/pso_comparison.json :height: 450 :responsive: :title: PSO Convergence Comparison Across Controllers
``` **Controller-Specific Convergence Analysis:** Classical SMC:
```{eval-rst}

.. chartjs:: :type: line :data: ../visualization/data/pso_classical_smc_convergence.json :height: 350 :responsive: :title: Classical SMC PSO Convergence
``` Adaptive SMC:
```{eval-rst}

.. chartjs:: :type: line :data: ../visualization/data/pso_adaptive_smc_convergence.json :height: 350 :responsive: :title: Adaptive SMC PSO Convergence
``` Hybrid Adaptive-STA SMC:
```{eval-rst}

.. chartjs:: :type: line :data: ../visualization/data/pso_hybrid_adaptive_sta_smc_convergence.json :height: 350 :responsive: :title: Hybrid Adaptive-STA SMC PSO Convergence
``` **Convergence Statistics:** ```{eval-rst}
.. chartjs:: :type: bar :data: ../visualization/data/convergence_statistics.json :height: 300 :responsive: :title: PSO Convergence Statistics Summary
``` **Memory Efficiency:** PSO uses local PRNGs and instance-level attributes to avoid cross-contamination between optimization runs. **Performance:** Vectorized batch simulation achieves **10-100×** speedup over sequential evaluation.

---

## Simulation Infrastructure

### Simulation Runner

The simulation runner provides sequential integration with explicit Euler method and state management.

**Source:** [`src/simulation/engines/simulation_runner.py`](../../src/simulation/engines/simulation_runner.py)

#### Key Features

- **Explicit Euler Integration**: First-order forward integration

- **Controller Interface Flexibility**: Supports both `compute_control` and `__call__`
- **State and History Management**: Automatic initialization and persistence
- **Control Saturation**: Input limits via `u_max` or `controller.max_force`
- **Latency Monitoring**: Optional deadline tracking with fallback controller
- **Early Stopping**: Graceful termination on NaN/Inf or dynamics exceptions #### Integration Algorithm ```
FOR i = 0 TO n_steps-1: t_now = i * dt # Compute control input IF controller has compute_control: u, state_vars, history = controller.compute_control(x_curr, state_vars, history) ELSE: u = controller(t_now, x_curr) # Apply saturation u = clamp(u, -u_max, u_max) # Propagate dynamics (Euler step) x_next = dynamics_model.step(x_curr, u, dt) # Safety check IF not all_finite(x_next): BREAK # Early termination # Update state x_curr = x_next
``` **Time Complexity:** $O(n \cdot d)$ where $n$ is number of steps and $d$ is state dimension. #### Usage Example ```python
from src.simulation.engines.simulation_runner import run_simulation
from src.controllers import ClassicalSMC
from src.plant.models.simplified import SimplifiedDIPDynamics, SimplifiedDIPConfig # Setup dynamics
config = SimplifiedDIPConfig.create_default()
dynamics = SimplifiedDIPDynamics(config) # Setup controller
controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01
) # Initial state
x0 = [0.0, 0.1, -0.05, 0.0, 0.0, 0.0] # Small perturbation from upright # Run simulation
t_arr, x_arr, u_arr = run_simulation( controller=controller, dynamics_model=dynamics, sim_time=5.0, dt=0.01, initial_state=x0
) # Analyze results
print(f"Simulated {len(t_arr)} time steps")
print(f"Final state: {x_arr[-1]}")
print(f"Max control: {np.max(np.abs(u_arr)):.2f} N")
``` #### Latency Monitoring The runner supports real-time deadline monitoring: ```python
# example-metadata:

# runnable: false def fallback_controller(t, x): """Simple PD controller as fallback.""" return -10 * x[0] - 5 * x[3] # Proportional to cart position and velocity t_arr, x_arr, u_arr = run_simulation( controller=main_controller, dynamics_model=dynamics, sim_time=5.0, dt=0.01, initial_state=x0, fallback_controller=fallback_controller # Activated on deadline miss

)
``` When a control computation exceeds `dt`, the fallback controller is used for all subsequent steps.

---

## Vectorized Batch Simulation

### Overview

Vectorized batch simulation enables efficient parallel evaluation of multiple controllers, essential for PSO optimization.

**Source:** [`src/simulation/engines/vector_sim.py`](../../src/simulation/engines/vector_sim.py)

### Key Features

- **Unified Interface**: Supports both scalar and batch modes transparently
- **Safety Guards**: NaN detection, energy limits, state bounds
- **Early Stopping**: Convergence detection and `stop_fn` callback
- **Memory Efficient**: View-based array operations minimize copying

### API: `simulate_system_batch`

```python
# example-metadata:
# runnable: false def simulate_system_batch( *, controller_factory: Callable[[np.ndarray], Any], particles: np.ndarray, # Shape: (B, G) for B particles, G gains sim_time: float, dt: float, u_max: Optional[float] = None, params_list: Optional[List] = None, # Uncertainty evaluation convergence_tol: Optional[float] = None, # Early stopping threshold grace_period: float = 0.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: """ Returns: ------- t : np.ndarray, shape (N+1,) Time vector x_b : np.ndarray, shape (B, N+1, D) State trajectories for B particles u_b : np.ndarray, shape (B, N) Control sequences sigma_b : np.ndarray, shape (B, N) Sliding surface values """
```

## Batch Simulation Example

```python

from src.simulation.engines.vector_sim import simulate_system_batch
from src.controllers import create_smc_for_pso, SMCType
import numpy as np # Define controller factory
def factory(gains): return create_smc_for_pso(SMCType.CLASSICAL, gains, max_force=100.0) # Generate particle swarm (10 particles, 6 gains each)
particles = np.random.uniform( low=[0.1, 0.1, 0.1, 0.1, 1.0, 0.0], high=[50.0, 50.0, 50.0, 50.0, 200.0, 50.0], size=(10, 6)
) # Batch simulate
t, x_batch, u_batch, sigma_batch = simulate_system_batch( controller_factory=factory, particles=particles, sim_time=5.0, dt=0.01, u_max=100.0
) # Analyze batch results
print(f"Batch shape: {x_batch.shape}") # (10, 501, 6)
print(f"Time steps: {len(t)}") # Compute ISE for each particle
ise = np.sum(x_batch[:, :-1, :3]**2 * dt, axis=(1, 2))
best_particle_idx = np.argmin(ise)
print(f"Best particle: {best_particle_idx}, ISE: {ise[best_particle_idx]:.4f}")
``` ### Safety Guards The simulation framework includes automatic safety checks: #### 1. NaN Detection ```python
def _guard_no_nan(state: np.ndarray, step_idx: int) -> None: """Raise error if state contains NaN or Inf values.""" if not np.all(np.isfinite(state)): raise ValueError(f"Non-finite state detected at step {step_idx}")
``` #### 2. Energy Bounds ```python

def _guard_energy(state: np.ndarray, limits: dict) -> None: """Verify total energy within specified limits.""" energy = np.sum(state**2, axis=-1) max_energy = limits.get('max', np.inf) if np.any(energy > max_energy): raise ValueError(f"Energy {energy.max():.2f} exceeds limit {max_energy:.2f}")
``` #### 3. State Bounds ```python
def _guard_bounds(state: np.ndarray, bounds: Tuple, t: float) -> None: """Verify state within per-dimension bounds.""" lower, upper = bounds if lower is not None and np.any(state < lower): raise ValueError(f"State below lower bound at t={t:.3f}") if upper is not None and np.any(state > upper): raise ValueError(f"State above upper bound at t={t:.3f}")
``` ### Early Convergence Detection Batch simulation supports early stopping when convergence is detected: ```python

t, x_batch, u_batch, sigma_batch = simulate_system_batch( controller_factory=factory, particles=particles, sim_time=10.0, dt=0.01, convergence_tol=0.001, # Stop when max(|σ|) < 0.001 grace_period=1.0 # Wait 1 second before checking
) print(f"Converged early: {len(t)} steps < {int(10.0/0.01)} max steps")
``` **Benefits:**
- Reduces PSO computational cost by 30-70% for well-converged controllers
- Avoids wasting computation on settled trajectories
- Ensures minimum settling time via grace period

---

## Configuration System

### Overview

The configuration system uses Pydantic for type-safe, validated parameter management.

**Source:** [`src/config/schemas.py`](../../src/config/schemas.py)

### Architecture

```
ConfigSchema
├── physics: PhysicsConfig
│ ├── Mass parameters (cart, pendulums)
│ ├── Geometric parameters (lengths, COM)
│ ├── Inertia parameters
│ ├── Friction coefficients
│ └── Numerical stability settings
├── simulation: SimulationConfig
│ ├── duration, dt
│ ├── use_full_dynamics
│ ├── latency settings
│ └── real-time mode
├── controller_defaults: Dict[str, ControllerConfig]
│ ├── classical_smc: ClassicalSMCConfig
│ ├── adaptive_smc: AdaptiveSMCConfig
│ ├── sta_smc: STASMCConfig
│ └── hybrid_adaptive_sta_smc: HybridAdaptiveSMCConfig
├── pso: PSOConfig
│ ├── Swarm parameters (n_particles, iters)
│ ├── PSO hyperparameters (c1, c2, w)
│ ├── Gain bounds per controller type
│ └── Advanced features (velocity_clamp, w_schedule)
├── cost_function: CostFunctionConfig
│ ├── weights: (state_error, control_effort, control_rate, stability)
│ ├── norms: Normalization constants
│ └── combine_weights: (mean, max)
└── physics_uncertainty: PhysicsUncertaintySchema ├── n_evals: Number of perturbed evaluations └── Parameter variation percentages
``` ### Type-Safe Configuration Pydantic provides compile-time type safety and runtime validation: ```python

from src.config import load_config # Load and validate configuration
config = load_config("config.yaml") # Access with full IDE autocomplete and type checking
cart_mass: float = config.physics.cart_mass
duration: float = config.simulation.duration
n_particles: int = config.pso.n_particles # Pydantic prevents typos and type errors
try: invalid = config.simulation.durration # AttributeError
except AttributeError: print("Typo caught at runtime!") try: config.physics.cart_mass = "not a number" # ValidationError
except Exception: print("Type error prevented!")
``` ### Physical Constraint Validation The configuration system enforces physical laws: #### 1. Positive Mass Constraint ```python
@field_validator("cart_mass", "pendulum1_mass", "pendulum2_mass")
def _must_be_strictly_positive(cls, v: float, info) -> float: if v <= 0.0: raise ValueError(f"{info.field_name} must be > 0 (conservation of mass)") return v
``` #### 2. Center of Mass Within Length ```python

@model_validator(mode="after")
def _validate_com_within_length(self) -> "PhysicsConfig": if self.pendulum1_com >= self.pendulum1_length: raise ValueError( f"pendulum1_com must be < pendulum1_length (geometric requirement)" ) return self
``` #### 3. Simulation Duration Validity ```python
@model_validator(mode="after")
def _duration_at_least_dt(self): if self.duration < self.dt: raise ValueError("duration must be >= dt (temporal consistency)") return self
``` ### Configuration Loading ```python

from src.config import load_config # Load with unknown field rejection (strict mode)
config = load_config("config.yaml", allow_unknown=False) # Load with unknown field warning (permissive mode)
config = load_config("config.yaml", allow_unknown=True) # Access nested configuration
pso_cfg = config.pso
physics_cfg = config.physics
sim_cfg = config.simulation
``` ### Example: `config.yaml` ```yaml
# Physics parameters
physics: cart_mass: 1.0 pendulum1_mass: 0.1 pendulum2_mass: 0.1 pendulum1_length: 0.5 pendulum2_length: 0.5 pendulum1_com: 0.25 pendulum2_com: 0.25 pendulum1_inertia: 0.00208 pendulum2_inertia: 0.00208 gravity: 9.81 cart_friction: 0.1 joint1_friction: 0.01 joint2_friction: 0.01 regularization: 1.0e-10 det_threshold: 1.0e-12 singularity_cond_threshold: 1.0e8 # Simulation settings
simulation: duration: 5.0 dt: 0.01 use_full_dynamics: false sensor_latency: 0.0 actuator_latency: 0.0 real_time: false # PSO configuration
pso: n_particles: 30 iters: 100 c1: 2.0 c2: 2.0 w: 0.9 velocity_clamp: [0.1, 0.5] w_schedule: [0.9, 0.4] bounds: classical_smc: min: [0.1, 0.1, 0.1, 0.1, 1.0, 0.0] max: [50.0, 50.0, 50.0, 50.0, 200.0, 50.0] # Cost function
cost_function: weights: state_error: 1.0 control_effort: 0.01 control_rate: 0.001 stability: 0.5 norms: state_error: 1.0 control_effort: 1.0 control_rate: 1.0 sliding: 1.0 combine_weights: mean: 0.7 max: 0.3 # Controller defaults
controller_defaults: classical_smc: gains: [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] max_force: 100.0 boundary_layer: 0.01 dt: 0.01
```

---

## Simulation Context

### Overview

The `SimulationContext` class provides centralized management of simulation framework components.

**Source:** [`src/simulation/core/simulation_context.py`](../../src/simulation/core/simulation_context.py)

### Key Responsibilities

1. **Configuration Loading**: Unified config access

2. **Dynamics Model Selection**: Full vs simplified dynamics based on config
3. **Component Registration**: Framework integration (FDI, monitors, analyzers)
4. **Controller Factory**: Simplified controller creation
5. **Simulation Engine Factory**: Sequential, batch, parallel, real-time engines ### Usage Example ```python
from src.simulation.core.simulation_context import SimulationContext # Initialize context with configuration
context = SimulationContext("config.yaml") # Access dynamics model
dynamics = context.get_dynamics_model() # Create controller
controller = context.create_controller(name="classical_smc") # Create simulation engine
engine = context.create_simulation_engine(engine_type="sequential") # Register custom components
from src.utils.monitoring import PerformanceMonitor
monitor = PerformanceMonitor()
context.register_component("performance_monitor", monitor) # Retrieve registered component
monitor = context.get_component("performance_monitor")
``` ### Simulation Engine Types The context supports multiple simulation orchestrators: | Engine Type | Use Case | Features |
|-------------|----------|----------|
| `sequential` | Single-threaded development | Simple, debuggable |
| `batch` | PSO optimization | Vectorized parallel evaluation |
| `parallel` | Multi-core execution | Process-based parallelism |
| `real_time` | HIL experiments | Real-time scheduling, deadline monitoring |

---

## Integration Methods ### Explicit Euler Integration The primary integration method is explicit (forward) Euler: $$
\mathbf{x}_{k+1} = \mathbf{x}_k + \Delta t \cdot \dot{\mathbf{x}}(\mathbf{x}_k, u_k)
$$ **Properties:**
- **Order:** First-order accurate ($O(\Delta t)$)
- **Stability:** Conditionally stable (requires small $\Delta t$)
- **Computational Cost:** Minimal (1 dynamics evaluation per step) **Typical Usage:** $\Delta t = 0.01$ seconds (100 Hz control loop) **Accuracy vs Performance Trade-off:** ```python
# High accuracy (slow)
config.simulation.dt = 0.001 # 1 ms timestep # Balanced (recommended)
config.simulation.dt = 0.01 # 10 ms timestep # Fast prototyping (low accuracy)
config.simulation.dt = 0.05 # 50 ms timestep
``` ### Alternative Integration Methods For research applications requiring higher accuracy, the framework supports: #### Runge-Kutta 4th Order (RK4) Available via `benchmarks/integration/numerical_methods.py`: ```python

from benchmarks.integration import RK4Integrator
from src.plant.models.simplified import SimplifiedDIPDynamics dynamics = SimplifiedDIPDynamics(config)
integrator = RK4Integrator(dynamics) result = integrator.integrate( x0=initial_state, sim_time=5.0, dt=0.01, controller=controller
)
``` **Properties:**
- **Order:** Fourth-order accurate ($O(\Delta t^4)$)
- **Computational Cost:** 4× dynamics evaluations per step
- **Stability:** Better than Euler for stiff systems #### Adaptive RK45 For high-accuracy research simulations: ```python
from benchmarks.integration import AdaptiveRK45Integrator integrator = AdaptiveRK45Integrator(dynamics)
result = integrator.integrate( x0=initial_state, sim_time=5.0, rtol=1e-8, # Relative tolerance atol=1e-10, # Absolute tolerance controller=controller
)
``` **Properties:**

- **Order:** Adaptive 4th/5th order
- **Step Size:** Automatically adjusted for error control
- **Use Case:** Energy conservation validation, benchmark comparisons

---

## Usage Examples

### Example 1: PSO Optimization Workflow

Complete workflow for optimizing classical SMC gains:

```python

from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.controllers import create_smc_for_pso, SMCType
from src.config import load_config
import numpy as np
import json # 1. Load configuration
config = load_config("config.yaml") # 2. Configure PSO for classical SMC
config.pso.n_particles = 40
config.pso.iters = 150
config.pso.bounds.classical_smc.min = [0.1, 0.1, 0.1, 0.1, 1.0, 0.0]
config.pso.bounds.classical_smc.max = [50.0, 50.0, 50.0, 50.0, 200.0, 50.0] # 3. Define controller factory
def controller_factory(gains): return create_smc_for_pso( SMCType.CLASSICAL, gains, max_force=100.0, boundary_layer=0.01, dt=0.01 ) # 4. Initialize PSO tuner
tuner = PSOTuner( controller_factory=controller_factory, config=config, seed=42, instability_penalty_factor=100.0
) # 5. Run optimization
result = tuner.optimise() # 6. Extract and save results
best_gains = result['best_pos']
best_cost = result['best_cost']
cost_history = result['history']['cost'] # 7. Save optimized gains
gains_data = { "controller_type": "classical_smc", "gains": best_gains.tolist(), "cost": float(best_cost), "optimization_iterations": len(cost_history), "config": { "n_particles": config.pso.n_particles, "iters": config.pso.iters, "seed": 42 }
} with open("optimized_gains_classical.json", "w") as f: json.dump(gains_data, f, indent=2) # 8. Validate optimized controller
from src.simulation.engines.simulation_runner import run_simulation
from src.plant.models.simplified import SimplifiedDIPDynamics controller = controller_factory(best_gains)
dynamics = SimplifiedDIPDynamics(config.physics)
x0 = [0.0, 0.1, -0.05, 0.0, 0.0, 0.0] t, x, u = run_simulation( controller=controller, dynamics_model=dynamics, sim_time=5.0, dt=0.01, initial_state=x0
) print(f"Best gains: {best_gains}")
print(f"Best cost: {best_cost:.4f}")
print(f"Final state error: {np.linalg.norm(x[-1][:3]):.4f}")
``` ### Example 2: Batch Controller Comparison Compare multiple controller configurations simultaneously: ```python
from src.simulation.engines.vector_sim import simulate_system_batch
from src.controllers import create_smc_for_pso, SMCType
import numpy as np
import matplotlib.pyplot as plt # Define controller variants
controller_configs = [ {"type": SMCType.CLASSICAL, "gains": [10.0, 8.0, 15.0, 12.0, 50.0, 5.0]}, {"type": SMCType.CLASSICAL, "gains": [20.0, 15.0, 25.0, 20.0, 80.0, 10.0]}, {"type": SMCType.CLASSICAL, "gains": [5.0, 4.0, 10.0, 8.0, 30.0, 2.0]},
] # Create factory for each configuration
def make_factory(cfg): def factory(gains): return create_smc_for_pso(cfg["type"], gains, max_force=100.0) return factory # Prepare particles array
particles = np.array([cfg["gains"] for cfg in controller_configs]) # Batch simulate
factory = make_factory(controller_configs[0])
t, x_batch, u_batch, sigma_batch = simulate_system_batch( controller_factory=factory, particles=particles, sim_time=5.0, dt=0.01, u_max=100.0
) # Compute metrics for each controller
for i, cfg in enumerate(controller_configs): ise = np.sum(x_batch[i, :-1, :3]**2 * 0.01, axis=1).sum() u_rms = np.sqrt(np.mean(u_batch[i]**2)) settling_time = np.argmax(np.all(np.abs(x_batch[i, :, :3]) < 0.01, axis=1)) * 0.01 print(f"Controller {i+1}:") print(f" ISE: {ise:.4f}") print(f" RMS Control: {u_rms:.2f} N") print(f" Settling Time: {settling_time:.2f} s") print() # Plot comparison
fig, axes = plt.subplots(3, 1, figsize=(10, 8))
for i in range(len(controller_configs)): axes[0].plot(t, x_batch[i, :, 1], label=f"Controller {i+1}") axes[1].plot(t, x_batch[i, :, 2]) axes[2].plot(t[:-1], u_batch[i]) axes[0].set_ylabel("θ₁ (rad)")
axes[1].set_ylabel("θ₂ (rad)")
axes[2].set_ylabel("Force (N)")
axes[2].set_xlabel("Time (s)")
axes[0].legend()
axes[0].grid(True)
axes[1].grid(True)
axes[2].grid(True)
plt.tight_layout()
plt.savefig("controller_comparison.png", dpi=150)
``` ### Example 3: Uncertainty Robustness Analysis Evaluate controller performance under parametric uncertainty: ```python

from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config config = load_config("config.yaml") # Configure uncertainty evaluation
config.physics_uncertainty = { "n_evals": 10, # 10 perturbed physics models "cart_mass": 0.15, # ±15% variation "pendulum1_mass": 0.15, "pendulum2_mass": 0.15, "pendulum1_length": 0.05, # ±5% variation "pendulum2_length": 0.05, "gravity": 0.01, # ±1% variation (altitude/latitude) "cart_friction": 0.20, # ±20% variation "joint1_friction": 0.20, "joint2_friction": 0.20,
} # Define controller factory
from src.controllers import create_smc_for_pso, SMCType def controller_factory(gains): return create_smc_for_pso(SMCType.ADAPTIVE, gains, max_force=100.0) # Initialize tuner
tuner = PSOTuner( controller_factory=controller_factory, config=config, seed=42
) # Run robust optimization
result = tuner.optimise() print(f"Robust gains optimized under {config.physics_uncertainty.n_evals} uncertainty scenarios")
print(f"Best robust cost: {result['best_cost']:.4f}")
print(f"Optimized gains: {result['best_pos']}")
```

---

## Performance Optimization

### Memory Efficiency

The simulation infrastructure includes several memory optimizations:

#### 1. View-Based Array Operations

```python
# MEMORY OPTIMIZATION: asarray creates view when input is already ndarray
x = np.asarray(initial_state, dtype=float) # View if already float64 ndarray # Unnecessary defensive copy eliminated
x_curr = x0 # No copy needed, immediately overwritten
```

**Benefit:** Eliminates 423 unnecessary copies in a typical 5-second simulation.

## 2. Broadcast Instead of Copy

```python
# MEMORY OPTIMIZATION: broadcast_to returns view

init_b = np.broadcast_to(init, (B, init.shape[0])) # Only copy when writeable buffer needed
init_b = init_b.copy()
```

**Benefit:** Reduces memory footprint for batch simulations with identical initial conditions.

## Computational Performance

#### 1. Numba JIT Compilation

For maximum performance, use Numba-optimized dynamics:

```python
from src.plant.models.simplified import SimplifiedDIPDynamics dynamics = SimplifiedDIPDynamics( config, enable_fast_mode=True, # Use Numba JIT compilation enable_monitoring=False # Disable diagnostics for speed
)
```

**Speedup:** 10-100× for repeated evaluations (PSO optimization, batch simulation)

**Trade-off:** First call has ~1s compilation overhead

#### 2. Vectorized Batch Simulation

Always use batch simulation for PSO instead of sequential loops:

```python
# example-metadata:

# runnable: false # FAST: Vectorized batch evaluation

t, x_batch, u_batch, sigma_batch = simulate_system_batch( controller_factory=factory, particles=gain_array, sim_time=5.0, dt=0.01
) # SLOW: Sequential loop (10-100× slower)
for i, gains in enumerate(gain_array): controller = factory(gains) t, x, u = run_simulation(controller, dynamics, 5.0, 0.01, x0)
```

## 3. Early Convergence Stopping

convergence detection to reduce PSO computational cost:

```python
t, x_batch, u_batch, sigma_batch = simulate_system_batch( controller_factory=factory, particles=particles, sim_time=10.0, dt=0.01, convergence_tol=0.001, # Stop when converged grace_period=1.0 # Minimum settling time
)
```

**Benefit:** 30-70% reduction in computation time for well-tuned controllers

---

## API Reference

### PSOTuner

**Location:** [`src/optimization/algorithms/pso_optimizer.py`](../../src/optimization/algorithms/pso_optimizer.py)

```python

# example-metadata:

# runnable: false class PSOTuner: """High-throughput, vectorized tuner for sliding-mode controllers.""" def __init__( self, controller_factory: Callable[[np.ndarray], Any], config: Union[ConfigSchema, str, Path], seed: Optional[int] = None, rng: Optional[np.random.Generator] = None, *, instability_penalty_factor: float = 100.0 ): """ Initialize PSO tuner. Parameters ---------- controller_factory : callable Function returning controller given gain vector config : ConfigSchema or path Configuration object or path to YAML seed : int, optional Random seed for reproducibility rng : np.random.Generator, optional External PRNG (overrides seed if provided) instability_penalty_factor : float Scale factor for instability penalties (default: 100.0) """ def optimise( self, *args, iters_override: Optional[int] = None, n_particles_override: Optional[int] = None, options_override: Optional[Dict[str, float]] = None, **kwargs ) -> Dict[str, Any]: """ Run PSO optimization. Parameters ---------- iters_override : int, optional Override config iterations n_particles_override : int, optional Override config swarm size options_override : dict, optional Override PSO hyperparameters (c1, c2, w) Returns ------- dict { "best_cost": float, "best_pos": np.ndarray, "history": {"cost": np.ndarray, "pos": np.ndarray} } """

```

## run_simulation

**Location:** [`src/simulation/engines/simulation_runner.py`](../../src/simulation/engines/simulation_runner.py)

```python
# example-metadata:
# runnable: false def run_simulation( *, controller: Any, dynamics_model: Any, sim_time: float, dt: float, initial_state: Any, u_max: Optional[float] = None, seed: Optional[int] = None, rng: Optional[np.random.Generator] = None, latency_margin: Optional[float] = None, fallback_controller: Optional[Callable[[float, np.ndarray], float]] = None, **kwargs
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: """ Simulate single controller trajectory using Euler integration. Parameters ---------- controller : Any Controller object (compute_control or __call__ interface) dynamics_model : Any Dynamics model with step(state, u, dt) method sim_time : float Total simulation duration (seconds) dt : float Integration timestep (seconds), must be > 0 initial_state : array-like Initial state vector u_max : float, optional Control saturation limit fallback_controller : callable, optional Fallback controller for deadline misses Returns ------- t_arr : np.ndarray, shape (N+1,) Time vector x_arr : np.ndarray, shape (N+1, D) State trajectory u_arr : np.ndarray, shape (N,) Control sequence """
```

## simulate_system_batch

**Location:** [`src/simulation/engines/vector_sim.py`](../../src/simulation/engines/vector_sim.py)

```python
# example-metadata:

# runnable: false def simulate_system_batch( *, controller_factory: Callable[[np.ndarray], Any], particles: np.ndarray, sim_time: float, dt: float, u_max: Optional[float] = None, params_list: Optional[List] = None, convergence_tol: Optional[float] = None, grace_period: float = 0.0, **kwargs

) -> Union[ Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]
]: """ Vectorized batch simulation of multiple controllers. Parameters ---------- controller_factory : callable Factory function: controller = factory(gains) particles : np.ndarray, shape (B, G) Gain vectors for B particles sim_time : float Total simulation duration dt : float Integration timestep u_max : float, optional Control saturation limit params_list : list, optional List of physics parameter objects for uncertainty evaluation convergence_tol : float, optional Early stopping threshold for max(|σ|) grace_period : float Duration before convergence checking begins Returns ------- If params_list is None: (t, x_batch, u_batch, sigma_batch) If params_list is provided: List of (t, x_batch, u_batch, sigma_batch) tuples Notes ----- - t: shape (N+1,) - x_batch: shape (B, N+1, D) - u_batch: shape (B, N) - sigma_batch: shape (B, N) """
```

## SimulationContext

**Location:** [`src/simulation/core/simulation_context.py`](../../src/simulation/core/simulation_context.py)

```python
# example-metadata:
# runnable: false class SimulationContext: """Enhanced simulation context with framework integration.""" def __init__(self, config_path: str = "config.yaml"): """Initialize simulation context.""" def get_dynamics_model(self) -> Any: """Return initialized dynamics model.""" def get_config(self) -> ConfigSchema: """Return validated configuration.""" def create_controller( self, name: Optional[str] = None, gains: Optional[List[float]] = None ) -> Any: """Create controller using configuration.""" def create_simulation_engine( self, engine_type: str = "sequential" ) -> SimulationEngine: """ Create simulation engine. Parameters ---------- engine_type : str Engine type: 'sequential', 'batch', 'parallel', 'real_time' """ def register_component(self, name: str, component: Any) -> None: """Register framework component.""" def get_component(self, name: str) -> Optional[Any]: """Get registered component."""
```

---

## Related Documentation

- [**Controllers Implementation Guide**](../controllers/factory_system_guide.md) - SMC controller details and usage
- [**Plant Models Guide**](../plant/models_guide.md) - Dynamics models and physics computation
- [**Mathematical Foundations**](../mathematical_foundations/index.md) - Control theory and optimization theory
- [**Configuration Reference**](../guides/api/configuration.md) - Complete configuration schema documentation
- [**Performance Benchmarks**](../benchmarks/controller_performance_benchmarks.md) - Integration method comparisons and performance analysis

---

**Version:** Phase 3
**Last Updated:** October 2025
**Status:** Production-Ready ✓
