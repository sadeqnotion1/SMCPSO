# Simulation API Guide

**Module:** `src.core`
**Purpose:** Simulation engine, dynamics models, and execution frameworks
**Level:** Intermediate to Advanced



## Table of Contents

- [Overview](#overview)
- [SimulationRunner](#simulationrunner)
- [Dynamics Models](#dynamics-models)
- [Simulation Context](#simulation-context)
- [Batch Simulation](#batch-simulation)
- [Integration Patterns](#integration-patterns)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)



## Overview

The Simulation API provides the core engine for running double-inverted pendulum simulations with sliding mode controllers.

**Key Features:**
- ✅ **SimulationRunner:** High-level simulation orchestration
- ✅ **Multiple Dynamics:** Simplified and full nonlinear models
- ✅ **Unified Context:** Consistent simulation state management
- ✅ **Batch Processing:** Numba-accelerated parallel simulations
- ✅ **Safety Guards:** Numerical stability monitoring and error handling

**Related Documentation:**
- [Tutorial 01: First Simulation](../tutorials/tutorial-01-first-simulation.md)
- [How-To: Running Simulations](../how-to/running-simulations.md)
- [Controllers API](controllers.md)
- [Technical Reference](../../reference/core/__init__.md)



## SimulationRunner

The primary interface for running simulations.

### Initialization

```python
from src.core import SimulationRunner
from src.config import load_config

config = load_config('config.yaml')
runner = SimulationRunner(config)
```

### Configuration Requirements

**Required config sections:**
```yaml
simulation:
  duration: 5.0              # Simulation time (seconds)
  dt: 0.01                   # Timestep (seconds)
  use_full_dynamics: false   # True for full nonlinear, False for simplified

dip_params:
  m0: 1.5                    # Cart mass (kg)
  m1: 0.5                    # First pendulum mass (kg)
  m2: 0.75                   # Second pendulum mass (kg)
  l1: 0.5                    # First pendulum length (m)
  l2: 0.75                   # Second pendulum length (m)
  ## ... other physics parameters

initial_conditions:
  x0: 0.0
  x0_dot: 0.0
  theta1_0: 0.1              # 0.1 rad ≈ 5.7°
  theta1_0_dot: 0.0
  theta2_0: 0.15             # 0.15 rad ≈ 8.6°
  theta2_0_dot: 0.0
```

### Running Simulations

**Basic usage:**
```python
from src.controllers import create_smc_for_pso, SMCType

## Create controller
controller = create_smc_for_pso(
    SMCType.CLASSICAL,
    gains=[10, 8, 15, 12, 50, 5],
    max_force=100.0
)

## Run simulation
result = runner.run(controller)

## Access results
print(f"ISE: {result['metrics']['ise']:.4f}")
print(f"Final state: {result['state'][-1]}")
```

## Result Structure

```python
## example-metadata:
## runnable: false

result = {
    't': np.ndarray,          # Time vector, shape (N+1,)
    'state': np.ndarray,      # State trajectories, shape (N+1, 6)
                              ## [x, dx, θ₁, dθ₁, θ₂, dθ₂] at each timestep
    'control': np.ndarray,    # Control inputs, shape (N+1,)
    'metrics': {
        'ise': float,         # Integral of Squared Error
        'itae': float,        # Integral of Time-weighted Absolute Error
        'max_theta1': float,  # Maximum first pendulum angle (rad)
        'max_theta2': float,  # Maximum second pendulum angle (rad)
        'control_effort': float,  # Total control energy
        'settling_time': float    # Time to settle within 2% of target
    },
    'stability': {
        'converged': bool,    # Did system stabilize?
        'final_error': float  # Final tracking error
    }
}
```

### Advanced Usage

**Custom initial conditions:**
```python
import numpy as np

## Override initial conditions
custom_ic = np.array([
    0.0,    # x (cart position)
    0.0,    # dx (cart velocity)
    0.2,    # θ₁ (first pendulum angle, rad)
    0.0,    # dθ₁ (first pendulum angular velocity)
    0.25,   # θ₂ (second pendulum angle, rad)
    0.0     # dθ₂ (second pendulum angular velocity)
])

result = runner.run(controller, initial_state=custom_ic)
```

**Custom simulation duration:**
```python
## Run for 10 seconds instead of config value
result = runner.run(controller, duration=10.0)
```

**Enable real-time monitoring:**
```python
def progress_callback(t, state, control):
    """Called at each timestep."""
    print(f"t={t:.2f}s, θ₁={state[2]:.3f} rad, u={control:.2f} N")

result = runner.run(controller, callback=progress_callback)
```

## Error Handling

```python
from src.core.exceptions import NumericalInstabilityError, ControlSaturationError

try:
    result = runner.run(controller)
except NumericalInstabilityError as e:
    print(f"Simulation became unstable: {e}")
    ## Try smaller timestep
    runner.dt = 0.005
    result = runner.run(controller)
except ControlSaturationError as e:
    print(f"Control saturated: {e}")
    ## Reduce gains or increase max_force
```



## Dynamics Models

### Model Comparison

| Feature | Simplified | Full Nonlinear |
|---------|-----------|----------------|
| **Accuracy** | Good for small angles | Exact |
| **Speed** | Fast | Moderate |
| **Coupling** | Linear approximation | Full nonlinear coupling |
| **Use Case** | Prototyping, PSO | Validation, research |

### Simplified Dynamics

**File:** `src/core/dynamics.py`

**Assumptions:**
- Small angle approximation: sin(θ) ≈ θ, cos(θ) ≈ 1
- Linearized coupling between pendulums
- Simplified inertia matrix

**Activation:**
```yaml
simulation:
  use_full_dynamics: false
```

**Use when:**
- Running PSO optimization (faster iterations)
- Prototyping controllers
- Small angle stabilization (<15°)

**Example:**
```python
from src.core.dynamics import SimplifiedDynamics
from src.config import load_config

config = load_config('config.yaml')
dynamics = SimplifiedDynamics(config.dip_params)

## Compute derivatives
state = np.array([0, 0, 0.1, 0, 0.15, 0])
control = 50.0
state_dot = dynamics.compute_dynamics(state, control)
```

## Full Nonlinear Dynamics

**File:** `src/core/dynamics_full.py`

**Features:**
- Exact trigonometric functions
- Full nonlinear coupling
- Accurate inertia matrix
- Friction and damping

**Activation:**
```yaml
simulation:
  use_full_dynamics: true
```

**Use when:**
- Final validation
- Large angle stabilization (>15°)
- Research publications
- Hardware deployment validation

**Example:**
```python
from src.core.dynamics_full import FullDynamics

dynamics = FullDynamics(config.dip_params)
state_dot = dynamics.compute_dynamics(state, control)

## Full dynamics includes:
## - Exact sin(θ), cos(θ)
## - Full Coriolis and centrifugal terms
## - Nonlinear inertia matrix
```

## State Representation

Both models use the same state vector:

```python
state = [
    x,        # Cart position (m)
    dx,       # Cart velocity (m/s)
    theta1,   # First pendulum angle (rad, 0 = upright)
    dtheta1,  # First pendulum angular velocity (rad/s)
    theta2,   # Second pendulum angle (rad, 0 = upright)
    dtheta2   # Second pendulum angular velocity (rad/s)
]
```

### Custom Dynamics Implementation

**Step 1: Define your dynamics class**

```python
from src.core.dynamics import BaseDynamics
import numpy as np

class FrictionEnhancedDynamics(BaseDynamics):
    """Dynamics with enhanced friction model."""

    def __init__(self, params, friction_model='coulomb'):
        super().__init__(params)
        self.friction_model = friction_model

    def compute_dynamics(self, state, control):
        """
        Compute state derivatives with enhanced friction.

        Parameters
        ## ---------- (RST section marker)
        state : np.ndarray, shape (6,)
            Current state [x, dx, θ₁, dθ₁, θ₂, dθ₂]
        control : float
            Control force (N)

        Returns
        ## ------- (RST section marker)
        state_dot : np.ndarray, shape (6,)
            State derivatives
        """
        x, dx, theta1, dtheta1, theta2, dtheta2 = state

        ## Apply friction model
        if self.friction_model == 'coulomb':
            friction = self._coulomb_friction(dx)
        elif self.friction_model == 'viscous':
            friction = self._viscous_friction(dx)
        else:
            friction = 0.0

        ## Base dynamics computation
        base_dynamics = super().compute_dynamics(state, control)

        ## Add friction effects
        state_dot = base_dynamics.copy()
        state_dot[1] -= friction  # Apply friction to cart velocity

        return state_dot

    def _coulomb_friction(self, velocity):
        """Coulomb friction model."""
        mu_c = 0.2  # Coulomb friction coefficient
        return mu_c * np.sign(velocity)

    def _viscous_friction(self, velocity):
        """Viscous friction model."""
        b = 0.5  # Viscous friction coefficient
        return b * velocity
```

**Step 2: Integrate with SimulationRunner**

```python
## Create custom dynamics
custom_dynamics = FrictionEnhancedDynamics(config.dip_params, friction_model='coulomb')

## Use with simulation runner
runner = SimulationRunner(config, dynamics_model=custom_dynamics)
result = runner.run(controller)
```



## Simulation Context

Unified state management for simulations.

### SimulationContext Class

```python
from src.core.simulation_context import SimulationContext

context = SimulationContext(
    config=config,
    controller=controller,
    dynamics=dynamics,
    initial_state=np.array([0, 0, 0.1, 0, 0.15, 0])
)

## Context provides:
## - Consistent logging
## - Safety guards
## - Performance monitoring
## - Error recovery
```

## Safety Guards

**Numerical stability monitoring:**
```python
## Automatic instability detection
if context.is_numerically_unstable(state):
    print("Warning: Numerical instability detected")
    context.attempt_recovery()
```

**Control saturation tracking:**
```python
## Track saturation events
if context.is_saturated(control, max_force=100.0):
    context.log_saturation_event(time=t, control=control)

## Get saturation statistics
stats = context.get_saturation_stats()
print(f"Saturated {stats['count']} times ({stats['percentage']:.1f}%)")
```

## Logging and Monitoring

```python
## Enable detailed logging
context.enable_logging(level='DEBUG', log_file='simulation.log')

## Monitor performance
context.start_performance_monitor()
result = runner.run(controller)
perf_stats = context.get_performance_stats()

print(f"Execution time: {perf_stats['total_time']:.3f}s")
print(f"Average timestep: {perf_stats['avg_step_time']:.6f}s")
```



## Batch Simulation

High-performance parallel simulations using Numba acceleration.

### Basic Batch Execution

```python
from src.core.vector_sim import run_batch_simulation
import numpy as np

## Define multiple initial conditions
n_trials = 100
initial_conditions = np.random.uniform(
    low=[-0.1, 0, -0.2, 0, -0.25, 0],
    high=[0.1, 0, 0.2, 0, 0.25, 0],
    size=(n_trials, 6)
)

## Run batch simulation (Numba-accelerated)
batch_results = run_batch_simulation(
    controller=controller,
    dynamics=dynamics,
    initial_conditions=initial_conditions,
    sim_params={
        'duration': 5.0,
        'dt': 0.01,
        'max_force': 100.0
    }
)

## Results shape: (n_trials, n_timesteps, n_states)
print(f"Batch results shape: {batch_results.shape}")
```

## Monte Carlo Analysis

```python
## example-metadata:
## runnable: false

## Monte Carlo simulation for statistical analysis
n_samples = 1000

## Sample initial conditions from distribution
ic_mean = np.array([0, 0, 0.1, 0, 0.15, 0])
ic_std = np.array([0.05, 0, 0.05, 0, 0.05, 0])
initial_conditions = np.random.normal(ic_mean, ic_std, size=(n_samples, 6))

## Run batch
batch_results = run_batch_simulation(controller, dynamics, initial_conditions, sim_params)

## Compute statistics
ise_values = np.sum(batch_results[:, :, 2:4]**2, axis=(1, 2))  # ISE for θ₁, θ₂
mean_ise = np.mean(ise_values)
std_ise = np.std(ise_values)
percentile_95 = np.percentile(ise_values, 95)

print(f"ISE: {mean_ise:.4f} ± {std_ise:.4f}")
print(f"95th percentile: {percentile_95:.4f}")
```

## PSO Integration

```python
## Batch evaluation for PSO fitness function
def batch_fitness_function(gains_array):
    """Evaluate controller on multiple scenarios."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains_array)

    ## Test scenarios
    scenarios = [
        np.array([0, 0, 0.1, 0, 0.15, 0]),   # Nominal
        np.array([0, 0, 0.2, 0, 0.25, 0]),   # Large angles
        np.array([0.1, 0, 0.15, 0, 0.2, 0]), # Cart offset
    ]
    initial_conditions = np.array(scenarios)

    ## Run batch
    results = run_batch_simulation(controller, dynamics, initial_conditions, sim_params)

    ## Compute average performance
    ise = np.mean(np.sum(results[:, :, 2:4]**2, axis=(1, 2)))
    return ise

## Use with PSO
from src.optimizer import PSOTuner

tuner = PSOTuner(
    controller_type=SMCType.CLASSICAL,
    bounds=get_gain_bounds_for_pso(SMCType.CLASSICAL),
    cost_function=batch_fitness_function
)
best_gains, best_cost = tuner.optimize()
```

## Performance Tips

**Numba compilation:**
```python
## example-metadata:
## runnable: false

## First call compiles the function (slow)
batch_results = run_batch_simulation(...)  # ~2 seconds

## Subsequent calls use compiled code (fast)
batch_results = run_batch_simulation(...)  # ~0.1 seconds
```

**Batch size optimization:**
```python
## example-metadata:
## runnable: false

## Too small: Compilation overhead dominates
run_batch_simulation(..., n_trials=10)  # Not efficient

## Optimal: Amortize compilation cost
run_batch_simulation(..., n_trials=100)  # Good

## Too large: Memory issues
run_batch_simulation(..., n_trials=10000)  # May run out of RAM
```



## Integration Patterns

### Pattern 1: Complete Simulation Pipeline

```python
from src.config import load_config
from src.controllers import create_controller
from src.core import SimulationRunner
from src.utils.visualization import plot_results

## Load configuration
config = load_config('config.yaml')

## Create controller
controller = create_controller('classical_smc', config=config.controllers.classical_smc)

## Initialize simulation
runner = SimulationRunner(config)

## Run simulation
result = runner.run(controller)

## Visualize
plot_results(result)

## Analyze
print(f"Performance Metrics:")
print(f"  ISE: {result['metrics']['ise']:.4f}")
print(f"  Settling Time: {result['metrics']['settling_time']:.2f}s")
print(f"  Max θ₁: {result['metrics']['max_theta1']:.3f} rad")
```

## Pattern 2: Controller Comparison

```python
## Compare multiple controllers
controllers = {
    'Classical': create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5]),
    'STA': create_smc_for_pso(SMCType.SUPER_TWISTING, [25, 10, 15, 12, 20, 15], dt=0.01),
    'Adaptive': create_smc_for_pso(SMCType.ADAPTIVE, [10, 8, 15, 12, 0.5]),
}

results = {}
for name, ctrl in controllers.items():
    results[name] = runner.run(ctrl)
    print(f"{name}: ISE={results[name]['metrics']['ise']:.4f}")

## Statistical comparison
from src.utils.analysis import compare_controllers
comparison = compare_controllers(results)
print(comparison.summary())
```

## Pattern 3: Parameter Sensitivity Analysis

```python
## Test sensitivity to initial conditions
theta1_values = np.linspace(0.05, 0.3, 20)
ise_results = []

for theta1 in theta1_values:
    ic = np.array([0, 0, theta1, 0, theta1*1.5, 0])
    result = runner.run(controller, initial_state=ic)
    ise_results.append(result['metrics']['ise'])

## Plot sensitivity
import matplotlib.pyplot as plt
plt.plot(np.degrees(theta1_values), ise_results)
plt.xlabel('Initial θ₁ (degrees)')
plt.ylabel('ISE')
plt.title('Controller Sensitivity to Initial Conditions')
plt.show()
```



## Performance Optimization

### 1. Choosing the Right Dynamics Model

```python
## example-metadata:
## runnable: false

## PSO optimization: Use simplified dynamics for speed
config.simulation.use_full_dynamics = False
runner = SimulationRunner(config)
tuner = PSOTuner(..., simulation_runner=runner)
best_gains = tuner.optimize()  # Fast iterations

## Final validation: Use full dynamics for accuracy
config.simulation.use_full_dynamics = True
runner = SimulationRunner(config)
controller = create_smc_for_pso(SMCType.CLASSICAL, best_gains)
final_result = runner.run(controller)  # Accurate validation
```

## 2. Timestep Selection

```python
## Coarse timestep for prototyping (faster)
config.simulation.dt = 0.01  # 10ms
runner = SimulationRunner(config)

## Fine timestep for accuracy (slower)
config.simulation.dt = 0.001  # 1ms
runner_accurate = SimulationRunner(config)

## Adaptive timestep (future feature)
## runner = SimulationRunner(config, adaptive_dt=True, dt_min=0.0001, dt_max=0.01)
```

## 3. Batch Processing

```python
## Sequential (slow)
results = []
for ic in initial_conditions:
    result = runner.run(controller, initial_state=ic)
    results.append(result)

## Batch (fast, Numba-accelerated)
batch_results = run_batch_simulation(controller, dynamics, initial_conditions, sim_params)
```



## Troubleshooting

### Problem: "NumericalInstabilityError"

**Cause:** Numerical integration became unstable

**Solutions:**
1. **Reduce timestep:**
   ```python
   config.simulation.dt = 0.005  # Reduce from 0.01 to 0.005
   ```

2. **Use full dynamics for better numerical properties:**
   ```python
   config.simulation.use_full_dynamics = True
   ```

3. **Reduce controller gains:**
   ```python
   controller = create_smc_for_pso(SMCType.CLASSICAL, [5, 4, 8, 6, 25, 3])  # Halved gains
   ```

### Problem: Simulation is too slow

**Cause:** High computational cost

**Solutions:**
1. **Use simplified dynamics:**
   ```python
   config.simulation.use_full_dynamics = False
   ```

2. **Increase timestep (if stable):**
   ```python
   config.simulation.dt = 0.02  # Increase from 0.01
   ```

3. **Use batch processing for multiple runs:**
   ```python
## example-metadata:

## runnable: false

   batch_results = run_batch_simulation(...)  # Numba acceleration
   ```

### Problem: Results don't match expectations

**Cause:** Model mismatch or incorrect configuration

**Solutions:**
1. **Verify initial conditions:**
   ```python
   print(f"Initial state: {config.initial_conditions}")
   ```

2. **Check dynamics model:**
   ```python
   print(f"Using full dynamics: {config.simulation.use_full_dynamics}")
   ```

3. **Validate physics parameters:**
   ```python
   from src.utils.validation import validate_physics_params
   validate_physics_params(config.dip_params)
   ```

### Problem: Batch simulation crashes

**Cause:** Out of memory or incompatible types

**Solutions:**
1. **Reduce batch size:**
   ```python
## example-metadata:

## runnable: false

   ## Instead of 10000 trials
   batch_size = 1000
   results = run_batch_simulation(..., initial_conditions=ic[:batch_size])
   ```

2. **Ensure float64 dtype:**
   ```python
   initial_conditions = initial_conditions.astype(np.float64)
   ```



## Next Steps

- **Learn simulation basics:** [Tutorial 01: First Simulation](../tutorials/tutorial-01-first-simulation.md)
- **Optimize controllers:** [Optimization API Guide](optimization.md)
- **Configure physics:** [Plant Models API Guide](plant-models.md)
- **Technical details:** [Core Technical Reference](../../reference/core/__init__.md)



**Last Updated:** October 2025
