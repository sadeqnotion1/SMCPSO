# Optimization API Guide

**Module:** `src.optimizer`
**Purpose:** PSO-based controller gain tuning and optimization workflows
**Level:** Intermediate to Advanced



## Table of Contents

- [Overview](#overview)
- [PSOTuner](#psotuner)
- [Cost Functions](#cost-functions)
- [Gain Bounds](#gain-bounds)
- [Advanced Features](#advanced-features)
- [Integration Patterns](#integration-patterns)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)



## Overview

The Optimization API provides Particle Swarm Optimization (PSO) for automated controller gain tuning.

**Key Features:**
- ✅ **PSOTuner:** High-level PSO interface for controller optimization
- ✅ **Custom Cost Functions:** Flexible performance metric definitions
- ✅ **Smart Bounds:** Automatic gain bounds based on controller type
- ✅ **Convergence Monitoring:** Real-time optimization progress tracking
- ✅ **Multi-Objective:** Support for weighted multi-objective optimization

**Related Documentation:**
- [Tutorial 03: PSO Optimization](../tutorials/tutorial-03-pso-optimization.md)
- [How-To: Optimization Workflows](../how-to/optimization-workflows.md)
- [Controllers API](controllers.md)

**Theory & Foundations:**
- [PSO Algorithm Theory](../theory/pso-theory.md): Swarm intelligence, convergence theory, parameter selection



## PSOTuner

The primary interface for PSO-based gain tuning.

### Initialization

```python
from src.optimizer import PSOTuner
from src.controllers import SMCType, get_gain_bounds_for_pso

# Get recommended bounds for controller type
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)

# Initialize tuner
tuner = PSOTuner(
    controller_type=SMCType.CLASSICAL,
    bounds=bounds,
    n_particles=30,        # Swarm size
    iters=100,            # Number of iterations
    config=config         # Simulation configuration
)
```

## Parameters

**Required:**
- `controller_type`: SMCType enum (CLASSICAL, ADAPTIVE, SUPER_TWISTING, HYBRID)
- `bounds`: List of (min, max) tuples for each gain
- `config`: Configuration object with simulation settings

**Optional:**
- `n_particles`: Swarm size (default: 30)
  - Larger = better exploration, slower convergence
  - Recommended: 20-50 particles
- `iters`: Number of iterations (default: 100)
  - More iterations = better convergence
  - Recommended: 50-200 iterations
- `w`: Inertia weight (default: 0.7298)
  - Controls exploration vs exploitation
- `c1`: Cognitive coefficient (default: 1.49618)
  - Personal best influence
- `c2`: Social coefficient (default: 1.49618)
  - Global best influence

### Basic Optimization

```python
# Run optimization
best_gains, best_cost = tuner.optimize()

print(f"Optimized gains: {best_gains}")
print(f"Best cost: {best_cost:.4f}")

# Create optimized controller
from src.controllers import create_smc_for_pso

optimized_controller = create_smc_for_pso(
    SMCType.CLASSICAL,
    gains=best_gains,
    max_force=100.0
)
```

## With Convergence Monitoring

```python
# Enable convergence tracking
history = tuner.optimize(track_convergence=True)

best_gains = history['best_gains']
best_cost = history['best_cost']
convergence = history['convergence']

# Plot convergence
import matplotlib.pyplot as plt

plt.plot(convergence)
plt.xlabel('Iteration')
plt.ylabel('Best Cost')
plt.title('PSO Convergence')
plt.grid(True)
plt.show()
```

## Saving and Loading Results

```python
import json

# Save optimized gains
results = {
    'controller_type': 'classical_smc',
    'gains': best_gains.tolist(),
    'cost': float(best_cost),
    'optimization_params': {
        'n_particles': 30,
        'iters': 100,
        'bounds': bounds
    }
}

with open('optimized_gains.json', 'w') as f:
    json.dump(results, f, indent=2)

# Load and use
with open('optimized_gains.json', 'r') as f:
    loaded = json.load(f)

controller = create_smc_for_pso(
    SMCType.CLASSICAL,
    gains=loaded['gains'],
    max_force=100.0
)
```



## Cost Functions

Define custom performance metrics for optimization.

### Default Cost Function

The default cost function minimizes Integral of Squared Error (ISE):

```python
def default_cost_function(gains):
    """Default: Minimize ISE for angle tracking."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = runner.run(controller)
    return result['metrics']['ise']
```

### Custom Cost Function Design

**Example 1: Minimize settling time**
```python
def settling_time_cost(gains):
    """Optimize for fast settling."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = runner.run(controller)

    # Penalize slow settling
    settling_time = result['metrics']['settling_time']
    if settling_time > 3.0:
        return 1000.0 + settling_time  # Large penalty

    return settling_time
```

**Example 2: Minimize control effort**
```python
def energy_efficient_cost(gains):
    """Optimize for energy efficiency."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = runner.run(controller)

    # Total control energy
    control_effort = result['metrics']['control_effort']
    return control_effort
```

**Example 3: Multi-objective (weighted sum)**
```python
# example-metadata:
# runnable: false

def multi_objective_cost(gains, w_ise=0.6, w_energy=0.3, w_time=0.1):
    """Balance tracking, energy, and speed."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = runner.run(controller)

    # Normalize metrics
    ise_normalized = result['metrics']['ise'] / 10.0
    energy_normalized = result['metrics']['control_effort'] / 5000.0
    time_normalized = result['metrics']['settling_time'] / 5.0

    # Weighted sum
    total_cost = (w_ise * ise_normalized +
                  w_energy * energy_normalized +
                  w_time * time_normalized)

    return total_cost

# Use with tuner
tuner = PSOTuner(
    controller_type=SMCType.CLASSICAL,
    bounds=bounds,
    cost_function=multi_objective_cost
)
```

## Constraint Handling

**Hard constraints (invalid gains → infinite cost):**
```python
# example-metadata:
# runnable: false

def constrained_cost(gains):
    """Enforce stability constraints."""
    # Constraint: First gain must be larger than second
    if gains[0] <= gains[1]:
        return float('inf')

    # Constraint: Switching gain must be significant
    if gains[4] < 10.0:
        return float('inf')

    # Evaluate if valid
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = runner.run(controller)
    return result['metrics']['ise']
```

**Soft constraints (penalty-based):**
```python
# example-metadata:
# runnable: false

def penalty_based_cost(gains):
    """Use penalties for soft constraints."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = runner.run(controller)

    cost = result['metrics']['ise']

    # Penalty for excessive control saturation
    if result['metrics']['saturation_percentage'] > 20.0:
        penalty = result['metrics']['saturation_percentage'] * 0.5
        cost += penalty

    # Penalty for overshoot
    max_theta = max(result['metrics']['max_theta1'], result['metrics']['max_theta2'])
    if max_theta > 0.3:  # 17 degrees
        cost += (max_theta - 0.3) * 100

    return cost
```

### Robustness Testing

**Test across multiple scenarios:**
```python
# example-metadata:
# runnable: false

def robust_cost(gains):
    """Optimize for robustness across scenarios."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)

    scenarios = [
        np.array([0, 0, 0.1, 0, 0.15, 0]),   # Nominal
        np.array([0, 0, 0.2, 0, 0.25, 0]),   # Large angles
        np.array([0.1, 0, 0.15, 0, 0.2, 0]), # Cart offset
        np.array([0, 0, -0.1, 0, -0.15, 0]), # Negative angles
    ]

    costs = []
    for ic in scenarios:
        result = runner.run(controller, initial_state=ic)
        costs.append(result['metrics']['ise'])

    # Worst-case optimization
    return max(costs)

    # Or average-case
    # return np.mean(costs)
```



## Gain Bounds

### Automatic Bounds

```python
from src.controllers import get_gain_bounds_for_pso

# Get recommended bounds for each controller type
bounds_classical = get_gain_bounds_for_pso(SMCType.CLASSICAL)
# Returns: [(0.1, 50), (0.1, 50), (0.1, 50), (0.1, 50), (1.0, 200), (0.0, 50)]
#           k1      k2      λ1      λ2      K          ε

bounds_adaptive = get_gain_bounds_for_pso(SMCType.ADAPTIVE)
# Returns: [(0.1, 50), (0.1, 50), (0.1, 50), (0.1, 50), (0.01, 10)]
#           k1      k2      λ1      λ2      γ (adaptation rate)

bounds_sta = get_gain_bounds_for_pso(SMCType.SUPER_TWISTING)
# Returns: [(0.1, 50), (0.1, 50), (0.1, 50), (0.1, 50), (1.0, 100), (1.0, 100)]
#           k1      k2      λ1      λ2      α          β

bounds_hybrid = get_gain_bounds_for_pso(SMCType.HYBRID)
# Returns: [(0.1, 50), (0.1, 50), (0.1, 50), (0.1, 50)]
#           k1      k2      λ1      λ2
```

## Custom Bounds

**Narrower bounds for faster convergence:**
```python
# example-metadata:
# runnable: false

# Instead of wide bounds [0.1, 50]
wide_bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)

# Use narrower bounds based on prior knowledge
narrow_bounds = [
    (5.0, 15.0),   # k1: expect around 10
    (5.0, 15.0),   # k2: expect around 10
    (10.0, 20.0),  # λ1: expect around 15
    (8.0, 16.0),   # λ2: expect around 12
    (30.0, 70.0),  # K: expect around 50
    (1.0, 10.0),   # ε: expect around 5
]

tuner = PSOTuner(SMCType.CLASSICAL, bounds=narrow_bounds)
```

**Physical constraints:**
```python
# Ensure stability margins
physics_constrained_bounds = [
    (0.1, 50),     # k1 > 0 (positive definite)
    (0.1, 50),     # k2 > 0
    (0.1, 50),     # λ1 > 0
    (0.1, 50),     # λ2 > 0
    (10.0, 200),   # K: minimum switching gain for robustness
    (0.1, 50),     # ε: minimum boundary layer to prevent chattering
]
```

## Bounds Validation

```python
from src.controllers import validate_smc_gains

# Check if gains are within valid range
candidate_gains = [10, 8, 15, 12, 50, 5]
is_valid = validate_smc_gains(SMCType.CLASSICAL, candidate_gains)

if not is_valid:
    print("Invalid gains detected!")

# Validate bounds themselves
def validate_bounds(bounds, controller_type):
    """Ensure bounds are physically meaningful."""
    n_expected = {
        SMCType.CLASSICAL: 6,
        SMCType.ADAPTIVE: 5,
        SMCType.SUPER_TWISTING: 6,
        SMCType.HYBRID: 4
    }

    if len(bounds) != n_expected[controller_type]:
        raise ValueError(f"Expected {n_expected[controller_type]} bounds")

    for i, (low, high) in enumerate(bounds):
        if low >= high:
            raise ValueError(f"Bound {i}: low ({low}) >= high ({high})")
        if low <= 0:
            raise ValueError(f"Bound {i}: non-positive lower bound")

    return True
```



## Advanced Features

### Parallel PSO Execution

```python
from concurrent.futures import ProcessPoolExecutor
import numpy as np

def optimize_controller(controller_type):
    """Optimize a single controller type."""
    bounds = get_gain_bounds_for_pso(controller_type)
    tuner = PSOTuner(controller_type, bounds, n_particles=30, iters=100)
    best_gains, best_cost = tuner.optimize()
    return controller_type, best_gains, best_cost

# Optimize all controllers in parallel
controller_types = [
    SMCType.CLASSICAL,
    SMCType.ADAPTIVE,
    SMCType.SUPER_TWISTING,
    SMCType.HYBRID
]

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(optimize_controller, ct) for ct in controller_types]
    results = [future.result() for future in futures]

for ctrl_type, gains, cost in results:
    print(f"{ctrl_type}: Cost={cost:.4f}, Gains={gains}")
```

## Hyperparameter Tuning

**Optimize PSO hyperparameters:**
```python
# example-metadata:
# runnable: false

def tune_pso_hyperparameters():
    """Find best PSO settings for your problem."""
    best_overall_cost = float('inf')
    best_config = None

    # Grid search over PSO parameters
    for n_particles in [20, 30, 50]:
        for w in [0.5, 0.7, 0.9]:
            for c1 in [1.0, 1.5, 2.0]:
                c2 = c1  # Keep symmetric

                tuner = PSOTuner(
                    SMCType.CLASSICAL,
                    bounds=bounds,
                    n_particles=n_particles,
                    iters=50,
                    w=w,
                    c1=c1,
                    c2=c2
                )

                _, cost = tuner.optimize()

                if cost < best_overall_cost:
                    best_overall_cost = cost
                    best_config = {
                        'n_particles': n_particles,
                        'w': w,
                        'c1': c1,
                        'c2': c2
                    }

    return best_config, best_overall_cost

optimal_pso_config, best_cost = tune_pso_hyperparameters()
print(f"Optimal PSO config: {optimal_pso_config}")
```

### Convergence Diagnostics

```python
# example-metadata:
# runnable: false

def diagnose_convergence(history):
    """Analyze PSO convergence quality."""
    convergence = history['convergence']

    # Check if converged
    final_cost = convergence[-1]
    improvement = convergence[0] - convergence[-1]
    improvement_percent = (improvement / convergence[0]) * 100

    # Detect premature convergence (plateau early)
    plateau_start = None
    for i in range(len(convergence) - 10):
        if np.std(convergence[i:i+10]) < 0.01 * final_cost:
            plateau_start = i
            break

    diagnostics = {
        'converged': improvement_percent > 20,
        'improvement_percent': improvement_percent,
        'final_cost': final_cost,
        'plateau_start': plateau_start,
        'early_plateau': plateau_start is not None and plateau_start < len(convergence) * 0.3
    }

    return diagnostics

# Use diagnostics
history = tuner.optimize(track_convergence=True)
diag = diagnose_convergence(history)

if diag['early_plateau']:
    print("Warning: PSO converged prematurely. Try:")
    print("  - Increase swarm diversity (larger w)")
    print("  - Increase swarm size (more particles)")
    print("  - Widen search bounds")
```

## Multi-Objective Optimization

**Pareto frontier approach:**
```python
def pareto_optimization(gains):
    """Return multiple objectives for Pareto analysis."""
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = runner.run(controller)

    return {
        'ise': result['metrics']['ise'],
        'energy': result['metrics']['control_effort'],
        'time': result['metrics']['settling_time']
    }

# Run PSO multiple times with different weights
pareto_front = []
weight_combinations = [
    (0.8, 0.1, 0.1),  # Prioritize ISE
    (0.5, 0.4, 0.1),  # Balance ISE and energy
    (0.3, 0.3, 0.4),  # Prioritize settling time
]

for w_ise, w_energy, w_time in weight_combinations:
    cost_fn = lambda g: multi_objective_cost(g, w_ise, w_energy, w_time)
    tuner = PSOTuner(SMCType.CLASSICAL, bounds, cost_function=cost_fn)
    gains, _ = tuner.optimize()

    metrics = pareto_optimization(gains)
    pareto_front.append({
        'gains': gains,
        'weights': (w_ise, w_energy, w_time),
        'metrics': metrics
    })

# Visualize Pareto front
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ise_vals = [p['metrics']['ise'] for p in pareto_front]
energy_vals = [p['metrics']['energy'] for p in pareto_front]
time_vals = [p['metrics']['time'] for p in pareto_front]

ax.scatter(ise_vals, energy_vals, time_vals)
ax.set_xlabel('ISE')
ax.set_ylabel('Energy')
ax.set_zlabel('Settling Time')
plt.title('Pareto Front: Multi-Objective Optimization')
plt.show()
```



## Integration Patterns

### Pattern 1: Full Optimization Pipeline

```python
from src.config import load_config
from src.optimizer import PSOTuner
from src.controllers import SMCType, get_gain_bounds_for_pso, create_smc_for_pso
from src.core import SimulationRunner

# Setup
config = load_config('config.yaml')
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)

# Optimize
tuner = PSOTuner(SMCType.CLASSICAL, bounds, n_particles=30, iters=100, config=config)
best_gains, best_cost = tuner.optimize()

# Validate
controller = create_smc_for_pso(SMCType.CLASSICAL, best_gains)
runner = SimulationRunner(config)
result = runner.run(controller)

print(f"Optimized Cost: {best_cost:.4f}")
print(f"Validation ISE: {result['metrics']['ise']:.4f}")
```

## Pattern 2: Iterative Refinement

```python
# example-metadata:
# runnable: false

# Coarse optimization with wide bounds
initial_bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
tuner_coarse = PSOTuner(SMCType.CLASSICAL, initial_bounds, n_particles=50, iters=50)
coarse_gains, _ = tuner_coarse.optimize()

# Fine optimization with narrow bounds around coarse solution
refined_bounds = [(g*0.8, g*1.2) for g in coarse_gains]
tuner_fine = PSOTuner(SMCType.CLASSICAL, refined_bounds, n_particles=30, iters=100)
fine_gains, fine_cost = tuner_fine.optimize()

print(f"Coarse gains: {coarse_gains}")
print(f"Fine gains: {fine_gains}")
print(f"Final cost: {fine_cost:.4f}")
```

## Pattern 3: Robustness Optimization

```python
# example-metadata:
# runnable: false

# Define robust cost function
def robust_cost(gains):
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    worst_case = 0.0

    for theta_scale in [0.5, 1.0, 1.5, 2.0]:
        ic = np.array([0, 0, 0.1*theta_scale, 0, 0.15*theta_scale, 0])
        result = runner.run(controller, initial_state=ic)
        worst_case = max(worst_case, result['metrics']['ise'])

    return worst_case

# Optimize for worst-case performance
tuner = PSOTuner(SMCType.CLASSICAL, bounds, cost_function=robust_cost)
robust_gains, _ = tuner.optimize()
```



## Performance Tips

### 1. Choose Appropriate Swarm Size

```python
# Problem complexity vs swarm size
problem_dimensions = len(bounds)

if problem_dimensions <= 4:
    n_particles = 20  # Hybrid controller (4 gains)
elif problem_dimensions <= 6:
    n_particles = 30  # Classical/STA (6 gains)
else:
    n_particles = 50  # Complex problems
```

## 2. Set Iteration Budget Wisely

```python
# example-metadata:
# runnable: false

# Iteration count based on convergence needs
tuner_fast = PSOTuner(..., iters=50)    # Quick prototyping
tuner_standard = PSOTuner(..., iters=100)  # Standard optimization
tuner_thorough = PSOTuner(..., iters=200)  # Publication-quality
```

## 3. Use Batch Evaluation

```python
# example-metadata:
# runnable: false

# Expensive to evaluate one controller at a time
def slow_cost(gains):
    for ic in scenarios:  # Sequential
        result = runner.run(controller, initial_state=ic)
    return ...

# Fast: Evaluate all scenarios in parallel
def fast_cost(gains):
    from src.core.vector_sim import run_batch_simulation
    results = run_batch_simulation(controller, dynamics, scenarios, sim_params)
    return ...
```



## Troubleshooting

### Problem: PSO not converging

**Solutions:**
1. Increase iterations: `iters=200`
2. Increase swarm size: `n_particles=50`
3. Adjust inertia: `w=0.9` (more exploration)
4. Widen bounds if search space too narrow

### Problem: Optimized gains invalid

**Solutions:**
1. Add validation in cost function:
   ```python
   if not validate_smc_gains(controller_type, gains):
       return float('inf')
   ```
2. Check bounds cover valid region

### Problem: Optimization too slow

**Solutions:**
1. Reduce swarm size: `n_particles=20`
2. Use simplified dynamics during optimization
3. Reduce simulation duration for fitness evaluation
4. Use batch simulation for robustness testing



## Next Steps

- **Learn PSO basics:** [Tutorial 03: PSO Optimization](../tutorials/tutorial-03-pso-optimization.md)
- **Create controllers:** [Controllers API Guide](controllers.md)
- **Run simulations:** [Simulation API Guide](simulation.md)
- **Technical details:** [Optimizer Technical Reference](../../reference/optimizer/__init__.md)



**Last Updated:** October 2025
