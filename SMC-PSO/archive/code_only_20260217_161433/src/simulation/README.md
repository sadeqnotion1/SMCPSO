# Simulation Module

**Total Files**: 45
**Test Coverage**: 92%
**Status**: Stable

---

## Overview

The simulation module orchestrates closed-loop simulation of the double-inverted pendulum system. It manages the time-stepping loop, integrates controller and plant dynamics, monitors system state, handles safety constraints, and collects results.

---

## Directory Structure

```
src/simulation/                 (45 files total)
├── engines/                    Core simulation runners
│   ├── simulation_runner.py    Single-run simulation [PRIMARY]
│   ├── vector_sim.py           Batch vectorized simulation
│   └── parallel_runner.py      Parallel multi-run execution
│
├── integrators/                Numerical integration schemes
│   ├── rk4.py                  4th-order Runge-Kutta [DEFAULT]
│   ├── rk45.py                 Adaptive RK45
│   └── euler.py                Forward Euler (for testing)
│
├── context/                    Simulation state management
│   ├── simulation_context.py  State container and history
│   └── safety_guards.py        Safety constraint monitoring
│
├── orchestrators/              Multi-run coordination
│   ├── monte_carlo.py          Monte Carlo simulations
│   └── parameter_sweep.py      Parameter space exploration
│
├── results/                    Result collection and processing
│   ├── result_collector.py     Data aggregation
│   └── result_exporter.py      Export to files
│
├── safety/                     Safety monitoring
│   ├── constraint_monitor.py   Real-time constraint checking
│   └── emergency_stop.py       Emergency termination logic
│
├── logging/                    Simulation-specific logging
│   └── sim_logger.py          Structured logging for simulations
│
├── validation/                 Input validation
│   └── sim_validators.py      Validate simulation parameters
│
└── core/                       Core utilities
    └── time_stepper.py         Time-stepping logic
```

---

## Key Difference: simulation/ vs plant/

**Frequent Question**: What's the difference between `simulation/` and `plant/`?

**Answer**:
- **plant/**: Pure physics (state evolution given control input)
  - No time loop
  - No controller interaction
  - Just implements `next_state = f(current_state, control, dt)`

- **simulation/**: Orchestration (runs the closed-loop system)
  - Time-stepping loop
  - Calls controller to get control signal
  - Calls plant to evolve state
  - Monitors safety constraints
  - Logs data

**Analogy**:
- `plant/` is like a physics engine (just computes forces/accelerations)
- `simulation/` is like a game loop (coordinates all components)

---

## Core Components

### 1. Simulation Runner (`engines/simulation_runner.py`) [PRIMARY]

**Purpose**: Main interface for running single closed-loop simulations.

**Example**:
```python
from src.simulation.engines.simulation_runner import SimulationRunner
from src.controllers.smc.classical_smc import ClassicalSMC
from src.plant.models.simplified.simplified_dynamics import SimplifiedDynamics

# Create components
controller = ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])
plant = SimplifiedDynamics()

# Create runner
runner = SimulationRunner(
    controller=controller,
    plant=plant,
    dt=0.01,        # Time step (seconds)
    integrator='rk4'  # Integration scheme
)

# Run simulation
result = runner.run(
    initial_state=[0.1, 0.05, 0.0, 0.0],  # [θ1, θ2, θ̇1, θ̇2]
    t_final=10.0    # Simulation duration (seconds)
)

# Access results
times = result['times']      # (N,) array
states = result['states']    # (N, 4) array
controls = result['controls']  # (N,) array
```

**Result Dictionary**:
```python
result = {
    'times': np.array([0, 0.01, 0.02, ..., 10.0]),  # Time stamps
    'states': np.array([[θ1, θ2, θ̇1, θ̇2], ...]),    # State trajectory
    'controls': np.array([u1, u2, u3, ...]),         # Control history
    'metrics': {                                     # Performance metrics
        'ise': 0.025,           # Integral squared error
        'settling_time': 1.2,   # Time to settle
        'max_overshoot': 0.05,  # Max overshoot
    },
    'converged': True,          # Whether system stabilized
    'exit_reason': 'completed'  # 'completed', 'timeout', 'safety_violation'
}
```

---

### 2. Batch Simulation (`engines/vector_sim.py`)

**Purpose**: Run multiple simulations efficiently using vectorization.

**Use Case**: Monte Carlo studies, parameter sweeps, PSO optimization.

**Example**:
```python
from src.simulation.engines.vector_sim import run_batch_simulation
import numpy as np

# Define 100 initial conditions
np.random.seed(42)
initial_conditions = np.random.uniform(
    low=[-0.2, -0.1, -0.5, -0.5],
    high=[0.2, 0.1, 0.5, 0.5],
    size=(100, 4)  # 100 simulations, 4 states each
)

# Run batch
results = run_batch_simulation(
    controller=controller,
    plant=plant,
    initial_conditions=initial_conditions,
    t_final=5.0,
    dt=0.01
)

# results['states'] shape: (100, 501, 4) - 100 simulations, 501 time steps, 4 states
# results['controls'] shape: (100, 501) - 100 simulations, 501 time steps
```

**Performance**: ~10x faster than running 100 sequential simulations.

---

### 3. Integration Schemes (`integrators/`)

**Available Integrators**:

| Integrator | Accuracy | Speed | Use Case |
|------------|----------|-------|----------|
| `'rk4'` [DEFAULT] | O(dt⁴) | Fast | General purpose |
| `'rk45'` | Adaptive | Medium | Stiff systems |
| `'euler'` | O(dt) | Fastest | Testing only |

**RK4 (Recommended)**:
```python
runner = SimulationRunner(
    controller=controller,
    plant=plant,
    dt=0.01,
    integrator='rk4'  # 4th-order Runge-Kutta
)
```

**Adaptive RK45** (for stiff systems):
```python
runner = SimulationRunner(
    controller=controller,
    plant=plant,
    dt=0.01,  # Initial step size
    integrator='rk45',
    integrator_config={
        'rtol': 1e-6,  # Relative tolerance
        'atol': 1e-8   # Absolute tolerance
    }
)
```

**Note**: Euler is only for testing/debugging (unstable for dt > 0.001).

---

### 4. Safety Guards (`context/safety_guards.py`)

**Purpose**: Monitor system constraints and trigger emergency stops.

**Example**:
```python
from src.simulation.safety.safety_guards import SafetyGuards

# Define constraints
safety = SafetyGuards(
    max_angle_deg=45.0,      # Max pendulum angle
    max_angular_velocity=10.0,  # Max angular velocity (rad/s)
    max_control=60.0,        # Max control signal
    timeout=20.0             # Max simulation time
)

# Use in simulation
runner = SimulationRunner(
    controller=controller,
    plant=plant,
    safety_guards=safety
)

result = runner.run(initial_state=[...], t_final=10.0)

if result['exit_reason'] == 'safety_violation':
    print(f"Safety violation: {result['violation_type']}")
```

**Safety Constraints**:
- **Angle limits**: Prevent physical damage (e.g., |θ1| < 45°)
- **Velocity limits**: Detect runaway behavior
- **Control saturation**: Detect actuator limits
- **Timeout**: Prevent infinite loops

---

### 5. Monte Carlo Simulations (`orchestrators/monte_carlo.py`)

**Purpose**: Statistical analysis via random initial conditions.

**Example**:
```python
from src.simulation.orchestrators.monte_carlo import MonteCarloSimulator

mc_sim = MonteCarloSimulator(
    controller=controller,
    plant=plant,
    n_samples=1000,
    initial_state_distribution={
        'mean': [0, 0, 0, 0],
        'std': [0.1, 0.05, 0.2, 0.1]  # Gaussian distribution
    }
)

# Run Monte Carlo
results = mc_sim.run(t_final=5.0)

# Statistical analysis
success_rate = results['success_rate']  # % of stabilized runs
mean_ise = results['mean_ise']
std_ise = results['std_ise']
ci_95 = results['confidence_interval_95']  # [lower, upper]

print(f"Success rate: {success_rate*100:.1f}%")
print(f"ISE: {mean_ise:.4f} ± {std_ise:.4f} (95% CI: {ci_95})")
```

---

### 6. Parameter Sweep (`orchestrators/parameter_sweep.py`)

**Purpose**: Explore controller/plant parameter space.

**Example**:
```python
from src.simulation.orchestrators.parameter_sweep import ParameterSweep

# Sweep controller gains
sweep = ParameterSweep(
    controller_type='classical_smc',
    plant=plant,
    parameter_ranges={
        'k1': np.linspace(5, 20, 10),
        'k2': np.linspace(2, 10, 10)
    },
    fixed_gains=[None, None, 8, 3, 15, 2]  # Fix k3-k6
)

# Run sweep (10x10 = 100 simulations)
results = sweep.run(t_final=5.0)

# Visualize
sweep.plot_heatmap(metric='ise')
```

---

## Complete Simulation Workflow

### Basic Workflow

```python
# 1. Load configuration
from src.config import load_config
config = load_config('config.yaml')

# 2. Create controller
from src.controllers.factory import create_controller
controller = create_controller(
    controller_type=config.controller.type,
    gains=config.controller.gains,
    config=config.controller
)

# 3. Create plant
from src.plant.models.full.full_dynamics import FullDynamics
plant = FullDynamics(config=config.plant)

# 4. Create simulation runner
from src.simulation.engines.simulation_runner import SimulationRunner
runner = SimulationRunner(
    controller=controller,
    plant=plant,
    dt=config.simulation.dt,
    integrator=config.simulation.integrator
)

# 5. Run simulation
result = runner.run(
    initial_state=config.simulation.initial_state,
    t_final=config.simulation.t_final
)

# 6. Analyze results
from src.analysis.performance.control_metrics import compute_performance_metrics
metrics = compute_performance_metrics(result['states'], result['controls'], result['times'])

print(f"ISE: {metrics['ise']:.6f}")
print(f"Settling time: {metrics['settling_time']:.2f}s")
```

---

## Configuration

Simulation configuration in `config.yaml`:

```yaml
simulation:
  dt: 0.01                # Time step (seconds)
  t_final: 10.0           # Simulation duration (seconds)
  integrator: rk4         # Integration scheme
  initial_state: [0.1, 0.05, 0.0, 0.0]  # [θ1, θ2, θ̇1, θ̇2]

  # Safety constraints
  safety:
    max_angle_deg: 45.0
    max_angular_velocity: 10.0
    max_control: 60.0
    timeout: 20.0

  # Logging
  logging:
    save_trajectory: true
    log_interval: 0.1      # Log every 0.1 seconds
    output_dir: .logs/simulation/

  # Performance monitoring
  monitoring:
    enable_realtime: false  # Real-time monitoring (for HIL)
    latency_threshold: 0.02  # Max acceptable latency (seconds)
```

---

## Advanced Features

### 1. Real-time Monitoring

For hardware-in-the-loop (HIL) or real-time systems:

```python
from src.simulation.engines.simulation_runner import SimulationRunner
from src.utils.monitoring.latency import LatencyMonitor

# Create latency monitor
monitor = LatencyMonitor(dt=0.01)

# Run with monitoring
runner = SimulationRunner(
    controller=controller,
    plant=plant,
    dt=0.01,
    realtime_monitor=monitor
)

result = runner.run(initial_state=[...], t_final=10.0)

# Check for deadline misses
print(f"Deadline misses: {monitor.deadline_misses}")
print(f"Max latency: {monitor.max_latency:.6f}s")
```

---

### 2. Custom Logging

```python
from src.simulation.logging.sim_logger import SimulationLogger

logger = SimulationLogger(
    log_file='.logs/simulation/run_001.log',
    log_level='DEBUG'
)

runner = SimulationRunner(
    controller=controller,
    plant=plant,
    logger=logger
)

result = runner.run(initial_state=[...], t_final=10.0)

# Logs include: timestamps, states, controls, violations, performance
```

---

### 3. Checkpointing (for long simulations)

```python
runner = SimulationRunner(
    controller=controller,
    plant=plant,
    checkpoint_interval=100.0,  # Save every 100 seconds (simulation time)
    checkpoint_dir='.cache/simulation/checkpoints/'
)

# If simulation crashes, resume from last checkpoint
result = runner.resume(checkpoint_file='.cache/simulation/checkpoints/sim_100s.pkl')
```

---

## Performance Optimization

### 1. Choose Appropriate Time Step

```python
# Too large: Numerical instability
dt = 0.1  # BAD: May diverge

# Too small: Unnecessary computation
dt = 0.0001  # BAD: 100x slower with minimal accuracy gain

# Good: Balance accuracy and speed
dt = 0.01  # GOOD: Stable and efficient for most systems
```

**Rule of thumb**: `dt < 0.1 * (shortest time constant)`

For DIP system with natural frequency ~5 Hz, `dt = 0.01` is appropriate.

---

### 2. Use Batch Simulation for Multiple Runs

```python
# SLOW: Sequential simulations
results = []
for ic in initial_conditions:
    result = runner.run(initial_state=ic, t_final=5.0)
    results.append(result)

# FAST: Batch vectorized simulation
results = run_batch_simulation(
    controller=controller,
    plant=plant,
    initial_conditions=initial_conditions,  # (N, 4) array
    t_final=5.0
)
```

**Speedup**: 5-10x for 100+ simulations

---

### 3. Use Simplified Plant for Rapid Prototyping

```python
# SLOW: Full nonlinear dynamics (high fidelity)
from src.plant.models.full.full_dynamics import FullDynamics
plant = FullDynamics()

# FAST: Simplified linearized dynamics (good approximation near equilibrium)
from src.plant.models.simplified.simplified_dynamics import SimplifiedDynamics
plant = SimplifiedDynamics()
```

**Speedup**: 5-10x (use simplified for controller development, then validate on full)

---

## Testing

### Unit Tests

```python
# tests/test_simulation/test_engines/test_simulation_runner.py
import pytest
from src.simulation.engines.simulation_runner import SimulationRunner

def test_simulation_runner_basic():
    """Test basic simulation run."""
    from src.controllers.smc.classical_smc import ClassicalSMC
    from src.plant.models.simplified.simplified_dynamics import SimplifiedDynamics

    controller = ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])
    plant = SimplifiedDynamics()
    runner = SimulationRunner(controller, plant)

    result = runner.run(initial_state=[0.1, 0, 0, 0], t_final=5.0)

    assert result['converged'] is True
    assert result['exit_reason'] == 'completed'
    assert len(result['times']) > 0
```

### Integration Tests

```python
def test_closed_loop_stability():
    """Test closed-loop stability with full dynamics."""
    from src.controllers.smc.classical_smc import ClassicalSMC
    from src.plant.models.full.full_dynamics import FullDynamics
    from src.simulation.engines.simulation_runner import SimulationRunner

    controller = ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])
    plant = FullDynamics()
    runner = SimulationRunner(controller, plant)

    result = runner.run(initial_state=[0.1, 0.05, 0, 0], t_final=10.0)

    # Verify final state near equilibrium
    final_state = result['states'][-1]
    assert np.linalg.norm(final_state) < 0.05
```

---

## Common Issues & Troubleshooting

### Issue: Simulation diverges

**Symptoms**: State values grow without bound, `NaN` in results

**Causes & Solutions**:
1. **Time step too large**: Reduce `dt` (try `dt=0.001`)
2. **Unstable controller**: Tune controller gains or use different controller
3. **Initial state too far from equilibrium**: Use swing-up controller first

### Issue: Simulation too slow

**Symptoms**: Long run times for simple simulations

**Solutions**:
1. **Use simplified plant**: Switch from `FullDynamics` to `SimplifiedDynamics`
2. **Increase time step**: Try `dt=0.02` (if numerically stable)
3. **Use batch simulation**: For multiple runs, use `run_batch_simulation()`
4. **Profile code**: Use `pytest-benchmark` to find bottlenecks

### Issue: Safety violations not caught

**Cause**: Safety guards not enabled

**Solution**: Add safety guards:
```python
from src.simulation.safety.safety_guards import SafetyGuards

runner = SimulationRunner(
    controller=controller,
    plant=plant,
    safety_guards=SafetyGuards(max_angle_deg=45, max_control=60)
)
```

### Issue: ImportError for deprecated paths

**Error**: `from src.core.simulation_runner import SimulationRunner`

**Solution**: Update to canonical path:
```python
from src.simulation.engines.simulation_runner import SimulationRunner
```

See `src/deprecated/README.md` for migration guide.

---

## References

- **Architecture**: `src/ARCHITECTURE.md`
- **Controllers**: `src/controllers/README.md`
- **Plant**: `src/plant/` (dynamics models)
- **Configuration**: `config.yaml`
- **Testing**: `tests/test_simulation/`
- **CLI**: `python simulate.py --help`

---

**Maintained by**: Simulation module team
**Last Review**: December 19, 2025
**Next Review**: March 2026
