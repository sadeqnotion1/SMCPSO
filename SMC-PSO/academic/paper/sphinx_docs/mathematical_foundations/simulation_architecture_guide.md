# Simulation Architecture Guide

**High-Performance Simulation System: Vector Engine, Safety Guards & Orchestration**



## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Vector Simulation Engine](#vector-simulation-engine)
4. [Simulation Runner](#simulation-runner)
5. [Simulation Context](#simulation-context)
6. [Orchestrators](#orchestrators)
7. [Safety System](#safety-system)
8. [Performance Optimization](#performance-optimization)
9. [Best Practices](#best-practices)



## Introduction

The DIP-SMC-PSO simulation architecture provides a high-performance, production-grade simulation framework for nonlinear dynamical systems. It supports both scalar and vectorized batch execution with integrated safety guards, multiple orchestration strategies, and adaptive time-stepping.

### Design Principles

1. **Shape Parity:** Scalar and batch modes use consistent array shapes
2. **Safety First:** Integrated safety guards prevent numerical instabilities
3. **Performance:** Vectorized operations for 20-30x speedup
4. **Flexibility:** Multiple dynamics models, integrators, and orchestrators
5. **Production Ready:** Early stopping, error recovery, graceful degradation

### Key Features

- **Vectorized Execution:** Batch simulation of 30+ particles simultaneously
- **Multiple Dynamics Models:** Simplified, full nonlinear, low-rank approximations
- **Adaptive Integration:** Error-controlled RK45, RK23 integrators
- **Safety Guards:** Energy limits, state bounds, NaN detection
- **Orchestration Strategies:** Batch, sequential, parallel, real-time
- **Memory Efficient:** View-based operations, zero-copy when possible



## Architecture Overview

### Component Hierarchy

```
┌───────────────────────────────────────────────────────────┐
│              User Interface (CLI, Streamlit)               │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│          Simulation Context (Configuration Layer)          │
├────────────────────────────────────────────────────────────┤
│  • Configuration loading & validation                      │
│  • Dynamics model selection                                │
│  • Controller creation                                     │
│  • FDI system initialization                               │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│          Orchestrators (Execution Strategy Layer)          │
├────────────────────────────────────────────────────────────┤
│  • BatchOrchestrator (vectorized)                          │
│  • SequentialOrchestrator (single-threaded)                │
│  • ParallelOrchestrator (multi-process)                    │
│  • RealTimeOrchestrator (hardware-in-loop)                 │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│          Vector Simulation Engine (Core Layer)             │
├────────────────────────────────────────────────────────────┤
│  • simulate() - unified façade                             │
│  • Batch dimension handling                                │
│  • Early stopping support                                  │
│  • Safety guard integration                                │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│        Simulation Runner (Dispatch Layer)                  │
├────────────────────────────────────────────────────────────┤
│  • step() - dynamics dispatch                              │
│  • run_simulation() - trajectory generation                │
│  • Model selection (full vs simplified)                    │
│  • Latency monitoring                                      │
└─────────────────────┬─────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼────────┐         ┌────────▼─────────┐
│ Dynamics Models │         │   Integrators    │
├────────────────┤         ├──────────────────┤
│ • Simplified   │         │ • Fixed-step     │
│ • Full         │         │   - Euler        │
│ • Low-rank     │         │   - RK4          │
└────────────────┘         │ • Adaptive       │
                           │   - RK45         │
                           │   - RK23         │
                           └──────────────────┘
```

### Data Flow

**Scalar Simulation:**
```
Initial state (D,) → simulate() → Safety guards → states (H+1, D)
```

**Batch Simulation:**
```
Initial states (B, D) → simulate() → Vectorized dynamics → states (B, H+1, D)
```



## Vector Simulation Engine

### simulate() Function

**Location:** `src/simulation/engines/vector_sim.py`

The `simulate()` function is the unified entry point for all simulations, handling both scalar and batch modes transparently.

#### Signature

```python
# example-metadata:
# runnable: false

def simulate(
    initial_state: Any,
    control_inputs: Any,
    dt: float,
    horizon: Optional[int] = None,
    *,
    energy_limits: Optional[float | dict] = None,
    state_bounds: Optional[Tuple[Any, Any]] = None,
    stop_fn: Optional[Callable[[np.ndarray], bool]] = None,
    t0: float = 0.0,
) -> np.ndarray
```

## Shape Conventions

| Mode | Initial State | Control Inputs | Output States |
|------|--------------|----------------|---------------|
| Scalar | `(D,)` | `(H,)` or `(H, U)` | `(H+1, D)` |
| Batch | `(B, D)` | `(B, H)` or `(B, H, U)` | `(B, H+1, D)` |

**Key principle:** Output always includes initial state at index 0

### Usage Examples

**Scalar Simulation:**

```python
from src.simulation.engines.vector_sim import simulate
import numpy as np

# Single pendulum simulation
x0 = np.array([0.0, 0.1, -0.05, 0.0, 0.0, 0.0])  # [x, θ1, θ2, ẋ, θ̇1, θ̇2]
u = np.zeros(100)  # No control input
dt = 0.01  # 10 ms timestep

states = simulate(x0, u, dt)

print(f"State shape: {states.shape}")  # (101, 6) - includes initial state
print(f"Initial state: {states[0]}")   # Same as x0
print(f"Final state: {states[-1]}")
```

**Batch Simulation (PSO Use Case):**

```python
# example-metadata:
# runnable: false

# Simulate 30 particles with different initial conditions
n_particles = 30
x0_batch = np.random.randn(n_particles, 6) * 0.1  # (30, 6)
u_batch = np.zeros((n_particles, 100))            # (30, 100)

states_batch = simulate(x0_batch, u_batch, dt)

print(f"Batch shape: {states_batch.shape}")  # (30, 101, 6)

# Analyze each particle
for i in range(n_particles):
    final_energy = np.sum(states_batch[i, -1, :]**2)
    print(f"Particle {i}: final energy = {final_energy:.4f}")
```

**Early Stopping:**

```python
# Stop when pendulum falls (|θ1| > π/2)
def stop_condition(state):
    return abs(state[1]) > np.pi / 2

x0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
u = np.random.randn(1000) * 0.1  # Large disturbance

states = simulate(x0, u, dt, stop_fn=stop_condition)

print(f"Simulation stopped at step {len(states)-1}")  # May be < 1000
```

## Safety Guards Integration

The vector engine integrates three safety guards automatically:

**1. NaN Detection:**
```python
def _guard_no_nan(state: np.ndarray, t: float, dt: float) -> None:
    """Detect and raise error for NaN values."""
    if not np.all(np.isfinite(state)):
        raise ValueError(f"NaN/Inf detected at t={t:.3f}")
```

**2. Energy Limits:**
```python
def _guard_energy(state: np.ndarray, energy_limit: float, t: float) -> None:
    """Check total energy against limit."""
    total_energy = np.sum(state**2)
    if total_energy > energy_limit:
        raise ValueError(
            f"Energy violation at t={t:.3f}: "
            f"{total_energy:.2f} > {energy_limit:.2f}"
        )
```

**3. State Bounds:**
```python
def _guard_bounds(state: np.ndarray, lower: Any, upper: Any, t: float) -> None:
    """Check state bounds."""
    if lower is not None and np.any(state < lower):
        raise ValueError(f"Lower bound violation at t={t:.3f}")
    if upper is not None and np.any(state > upper):
        raise ValueError(f"Upper bound violation at t={t:.3f}")
```

**Usage with Safety Guards:**

```python
from src.simulation.engines.vector_sim import simulate

# Pendulum with energy limit
states = simulate(
    x0,
    u,
    dt,
    energy_limits=100.0,  # Total energy < 100
    state_bounds=(
        [-10.0, -np.pi, -np.pi, -50.0, -50.0, -50.0],  # Lower bounds
        [ 10.0,  np.pi,  np.pi,  50.0,  50.0,  50.0]   # Upper bounds
    )
)
```



## Simulation Runner

### step() Function

**Location:** `src/simulation/engines/simulation_runner.py`

The `step()` function dispatches between dynamics models based on configuration.

#### Dynamics Model Selection

```python
from src.simulation.engines.simulation_runner import step, get_step_fn

# Automatic dispatch based on config
# config.simulation.use_full_dynamics = True/False

x_next = step(x_current, u, dt)

# Manual selection
full_step_fn = _load_full_step()      # Full nonlinear model
lowrank_step_fn = _load_lowrank_step()  # Low-rank approximation

x_next_full = full_step_fn(x, u, dt)
x_next_lr = lowrank_step_fn(x, u, dt)
```

## run_simulation() Function

High-level trajectory generation with controller integration.

### Signature

```python
# example-metadata:
# runnable: false

def run_simulation(
    *,
    controller: Any,
    dynamics_model: Any,
    sim_time: float,
    dt: float,
    initial_state: Any,
    u_max: Optional[float] = None,
    seed: Optional[int] = None,
    rng: Optional[np.random.Generator] = None,
    latency_margin: Optional[float] = None,
    fallback_controller: Optional[Callable[[float, np.ndarray], float]] = None,
    **_kwargs: Any,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]
```

## Features

1. **Controller State Management:** Calls `initialize_state()` and `initialize_history()` if available
2. **Control Saturation:** Respects `u_max` or `controller.max_force`
3. **Latency Monitoring:** Switches to fallback if control computation exceeds `dt`
4. **Graceful Degradation:** Truncates output on dynamics failure

### Usage Example

```python
from src.simulation.engines.simulation_runner import run_simulation
from src.controllers.factory import create_controller
from src.plant.models.dynamics import DoubleInvertedPendulum

# Create controller and dynamics
controller = create_controller('classical_smc', config=config, gains=[10, 5, 8, 3, 15, 2])
dynamics = DoubleInvertedPendulum(config.physics)

# Run simulation
t, states, controls = run_simulation(
    controller=controller,
    dynamics_model=dynamics,
    sim_time=10.0,
    dt=0.01,
    initial_state=np.array([0.0, 0.1, -0.05, 0.0, 0.0, 0.0]),
    u_max=100.0,
    seed=42
)

print(f"Time points: {len(t)}")       # 1001
print(f"States shape: {states.shape}")  # (1001, 6)
print(f"Controls shape: {controls.shape}")  # (1000,)
```



## Simulation Context

### SimulationContext Class

**Location:** `src/simulation/context/simulation_context.py`

Centralizes configuration loading, dynamics selection, and controller creation.

#### Architecture

```python
# example-metadata:
# runnable: false

class SimulationContext:
    """Simulation setup and configuration management."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path, allow_unknown=True)
        self.dynamics_model = self._initialize_dynamics_model()

    def _initialize_dynamics_model(self):
        """Select dynamics model based on config flag."""
        if self.config.simulation.use_full_dynamics:
            return FullDIPDynamics(self.config.physics)
        else:
            return DoubleInvertedPendulum(self.config.physics)

    def get_dynamics_model(self):
        """Return initialized dynamics model."""
        return self.dynamics_model

    def create_controller(self, name=None, gains=None):
        """Create controller using factory."""
        # Uses default gains from config if not provided
        return create_controller(name or "classical_smc", config=self.config, gains=gains)
```

#### Usage Pattern

```python
from src.simulation.context.simulation_context import SimulationContext

# Initialize simulation context
ctx = SimulationContext("config.yaml")

# Access components
dynamics = ctx.get_dynamics_model()
config = ctx.get_config()

# Create controller with defaults from config
controller = ctx.create_controller("classical_smc")

# Create controller with custom gains
adaptive_ctrl = ctx.create_controller("adaptive_smc", gains=[10, 5, 8, 3, 2.0])

# Run simulation
t, states, controls = run_simulation(
    controller=controller,
    dynamics_model=dynamics,
    sim_time=config.simulation.duration,
    dt=config.simulation.dt,
    initial_state=config.simulation.initial_state
)
```



## Orchestrators

### Orchestrator Types

The simulation framework provides four orchestration strategies:

| Orchestrator | Use Case | Performance | Complexity |
|-------------|----------|-------------|------------|
| `BatchOrchestrator` | PSO, Monte Carlo | **Fastest** (vectorized) | Low |
| `SequentialOrchestrator` | Single trajectory | Fast | Lowest |
| `ParallelOrchestrator` | CPU-intensive tasks | Medium (multiprocess) | Medium |
| `RealTimeOrchestrator` | HIL, real-time control | Deterministic latency | High |

### BatchOrchestrator

**Location:** `src/simulation/orchestrators/batch.py`

Vectorized execution of multiple simulations simultaneously.

#### Features

- **Vectorized Operations:** Batch dynamics evaluation
- **Early Stopping:** Per-simulation stop conditions
- **Active Mask Tracking:** Skip completed simulations
- **Result Aggregation:** Unified result container

#### Usage Example

```python
from src.simulation.orchestrators.batch import BatchOrchestrator
import numpy as np

orchestrator = BatchOrchestrator()

# Batch initial conditions (Monte Carlo)
n_runs = 100
x0_batch = np.random.randn(n_runs, 6) * 0.1
u_batch = np.zeros((n_runs, 1000))

result = orchestrator.execute(
    initial_state=x0_batch,
    control_inputs=u_batch,
    dt=0.01,
    horizon=1000,
    safety_guards=True,
    stop_fn=lambda x: abs(x[1]) > np.pi/2
)

# Access results
print(f"Batch size: {result.batch_size}")
print(f"Successful runs: {result.success_count}")
print(f"Execution time: {result.execution_time:.3f}s")
```

## Performance Comparison

**Benchmark:** 30 simulations, 1000 timesteps each

| Method | Time (s) | Speedup |
|--------|----------|---------|
| Sequential (loop) | 45.2 | 1.0x |
| Batch (vectorized) | 1.8 | **25.1x** |
| Parallel (4 cores) | 12.3 | 3.7x |

**Conclusion:** Batch orchestration is optimal for homogeneous workloads (PSO, parameter sweeps)



## Safety System

### Safety Guard Architecture

```
┌────────────────────────────────────────┐
│     Simulation Step (t → t + dt)       │
└────────────┬───────────────────────────┘
             │
             ├─► Pre-step guards (optional)
             │   └─ Input validation
             │
             ├─► Dynamics evaluation
             │   └─ x(t+dt) = f(x(t), u(t), dt)
             │
             ├─► Post-step guards (mandatory)
             │   ├─ NaN detection
             │   ├─ Energy limits
             │   └─ State bounds
             │
             └─► Early stop check
                 └─ user-defined stop_fn
```

### Guard Configuration

**In config.yaml:**

```yaml
simulation:
  safety:
    energy:
      max: 100.0
    bounds:
      lower: [-10.0, -3.14, -3.14, -50.0, -50.0, -50.0]
      upper: [ 10.0,  3.14,  3.14,  50.0,  50.0,  50.0]
```

**Programmatic Override:**

```python
# Override config defaults
states = simulate(
    x0, u, dt,
    energy_limits=200.0,  # More permissive than config
    state_bounds=(None, None)  # Disable bounds checking
)
```

## Custom Safety Guards

```python
from src.simulation.context.safety_guards import _guard_no_nan

def custom_guard_angular_velocity(state, t, threshold=100.0):
    """Custom guard for excessive angular velocities."""
    theta1_dot = state[4]
    theta2_dot = state[5]

    if abs(theta1_dot) > threshold or abs(theta2_dot) > threshold:
        raise ValueError(
            f"Angular velocity limit exceeded at t={t:.3f}: "
            f"θ̇1={theta1_dot:.2f}, θ̇2={theta2_dot:.2f}"
        )

# Integrate custom guard into simulation loop
for i in range(horizon):
    x_next = step(x_current, u[i], dt)
    _guard_no_nan(x_next, t, dt)
    custom_guard_angular_velocity(x_next, t, threshold=50.0)
    x_current = x_next
    t += dt
```



## Performance Optimization

### Memory Optimization Techniques

**1. View-Based Operations:**

```python
# GOOD: Creates view (zero-copy)
x_array = np.asarray(x, dtype=float)  # If x is already float64 ndarray

# BAD: Creates copy
x_array = np.array(x, dtype=float)  # Always creates new array
```

**2. Pre-allocation:**

```python
# example-metadata:
# runnable: false

# GOOD: Pre-allocate result array
states = np.zeros((batch_size, horizon + 1, state_dim), dtype=float)
states[:, 0, :] = initial_state

for i in range(horizon):
    states[:, i+1, :] = dynamics_step(states[:, i, :], u[:, i], dt)

# BAD: Append to list
states = [initial_state]
for i in range(horizon):
    states.append(dynamics_step(states[-1], u[i], dt))
states = np.array(states)  # Expensive conversion at end
```

**3. Broadcasting:**

```python
# GOOD: Broadcasting avoids explicit loops
n_particles = 30
control_input = np.array([1.0])  # Single value
u_batch = np.broadcast_to(control_input, (n_particles,))  # Efficient view

# BAD: Explicit replication
u_batch = np.array([control_input[0] for _ in range(n_particles)])
```

## Computational Optimization

**Numba JIT Compilation:**

```python
import numba

@numba.jit(nopython=True, cache=True)
def fast_dynamics_step(state, control, dt, params):
    """JIT-compiled dynamics for 100x speedup."""
    # Pure NumPy operations only
    M = compute_mass_matrix(state, params)
    C = compute_coriolis(state, params)
    G = compute_gravity(state, params)

    qdd = np.linalg.solve(M, control - C @ state[3:] - G)
    return state + dt * np.concatenate([state[3:], qdd])

# First call: ~100 ms (compilation)
# Subsequent calls: ~0.1 ms (compiled code)
```

## Profiling Guidelines

```python
import time
import cProfile

# Time measurement
start = time.perf_counter()
states = simulate(x0, u, dt)
elapsed = time.perf_counter() - start
print(f"Simulation time: {elapsed*1000:.2f} ms")

# Detailed profiling
profiler = cProfile.Profile()
profiler.enable()

for _ in range(100):
    states = simulate(x0, u, dt)

profiler.disable()
profiler.print_stats(sort='cumtime')

# Expected hot spots:
# 1. np.linalg.solve (30-40%)
# 2. dynamics evaluation (20-30%)
# 3. safety guards (5-10%)
# 4. array operations (10-20%)
```



## Best Practices

### 1. Choose the Right Orchestrator

```python
# example-metadata:
# runnable: false

# Single trajectory → SequentialOrchestrator
# PSO (30 particles) → BatchOrchestrator (25x faster)
# Monte Carlo (1000 runs) → ParallelOrchestrator (4 cores)
# HIL testing → RealTimeOrchestrator
```

## 2. Validate Inputs Early

```python
from src.simulation.engines.vector_sim import simulate

# Add input validation before simulation
assert x0.shape == (6,), f"Expected state dim 6, got {x0.shape}"
assert len(u) == horizon, f"Control length {len(u)} != horizon {horizon}"
assert dt > 0, "Time step must be positive"

states = simulate(x0, u, dt, horizon=horizon)
```

## 3. Use Safety Guards in Production

```python
# example-metadata:
# runnable: false

# Development: Permissive limits for debugging
states_dev = simulate(x0, u, dt, energy_limits=1e6, state_bounds=(None, None))

# Production: Strict limits for safety
states_prod = simulate(
    x0, u, dt,
    energy_limits=100.0,
    state_bounds=(
        [-10.0, -np.pi, -np.pi, -50.0, -50.0, -50.0],
        [ 10.0,  np.pi,  np.pi,  50.0,  50.0,  50.0]
    )
)
```

## 4. Handle Early Stopping Gracefully

```python
# example-metadata:
# runnable: false

# Wrap simulation in try-except for safety guard violations
try:
    states = simulate(x0, u, dt, energy_limits=100.0)
    success = True
except ValueError as e:
    # Safety guard triggered
    print(f"Simulation failed: {e}")
    success = False

# Use early stopping instead of throwing errors
def soft_stop(state):
    """Return True when unstable, but don't raise error."""
    return abs(state[1]) > np.pi/2 or np.sum(state**2) > 100.0

states = simulate(x0, u, dt, stop_fn=soft_stop)
# states.shape[0] may be < horizon + 1
```

## 5. uses Vectorization

```python
# example-metadata:
# runnable: false

# PSO fitness evaluation (30 particles)

# BAD: Sequential loop (slow)
def fitness_sequential(particles):
    costs = []
    for gains in particles:
        controller = create_controller('classical_smc', gains=gains)
        _, states, _ = run_simulation(controller, dynamics, 10.0, 0.01, x0)
        costs.append(compute_cost(states))
    return np.array(costs)

# GOOD: Vectorized batch (25x faster)
def fitness_vectorized(particles):
    x0_batch = np.tile(x0, (len(particles), 1))  # (30, 6)
    u_batch = np.zeros((len(particles), 1000))

    # Create controllers in batch
    controllers = [create_controller('classical_smc', gains=g) for g in particles]

    # Simulate all at once
    states_batch = simulate(x0_batch, u_batch, 0.01)  # (30, 1001, 6)

    # Vectorized cost computation
    costs = np.sum(states_batch[:, :, :3]**2 * dt, axis=(1, 2))
    return costs
```



## References

1. **Vector Simulation:** `src/simulation/engines/vector_sim.py`
2. **Simulation Runner:** `src/simulation/engines/simulation_runner.py`
3. **Simulation Context:** `src/simulation/context/simulation_context.py`
4. **Batch Orchestrator:** `src/simulation/orchestrators/batch.py`
5. **Safety Guards:** `src/simulation/context/safety_guards.py`



**File Location:** `docs/mathematical_foundations/simulation_architecture_guide.md`
**Lines:** 647
**Coverage:** Vector engine, simulation runner, context management, orchestrators, safety system, performance optimization
**Cross-references:**
- Vector simulation: `src/simulation/engines/vector_sim.py`
- Simulation runner: `src/simulation/engines/simulation_runner.py`
- Simulation context: `src/simulation/context/simulation_context.py`
- Orchestrators: `src/simulation/orchestrators/`
- Safety guards: `src/simulation/context/safety_guards.py`
