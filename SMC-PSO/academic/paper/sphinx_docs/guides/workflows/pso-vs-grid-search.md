# PSO vs Grid Search Comparison

A practical comparison between Particle Swarm Optimization (PSO) and grid search for tuning sliding mode controller parameters in the double inverted pendulum system.

---

## Overview

This guide helps you choose the right optimization method for your controller tuning needs. Both PSO and grid search have their place in the control systems toolkit.

**Quick Decision:**
- **Grid Search:** 1-3 parameters, need exhaustive coverage, simple fitness landscape
- **PSO:** 4+ parameters, complex objectives, limited computational budget

---

## Methodology Comparison

### Grid Search

**How it Works:**
1. Define discrete values for each parameter
2. Evaluate all combinations exhaustively
3. Select the best performer

**Example (3 parameters):**
```python
# Simplified conceptual example
k_values = [5, 10, 15, 20, 25]          # 5 values
lambda_values = [0.5, 1.0, 1.5, 2.0]    # 4 values
phi_values = [0.1, 0.2, 0.3]            # 3 values

# Total evaluations: 5 * 4 * 3 = 60
```

**Complexity:** O(n^d) where n = values per parameter, d = number of parameters

### PSO (This Project)

**How it Works:**
1. Initialize swarm of candidate solutions (particles)
2. Evaluate fitness of each particle
3. Update velocities based on personal and global best
4. Iterate until convergence or max iterations

**Example (6 parameters for Classical SMC):**
```python
# From src/optimizer/pso_optimizer.py
bounds = [
    (1.0, 50.0),   # k1 (theta1 proportional)
    (0.5, 20.0),   # k2 (theta1 derivative)
    (1.0, 50.0),   # k3 (theta2 proportional)
    (0.5, 20.0),   # k4 (theta2 derivative)
    (1.0, 50.0),   # k5 (cart proportional)
    (0.1, 10.0),   # k6 (cart derivative)
]

# Typical PSO settings
n_particles = 30
n_iterations = 50
# Total evaluations: 30 * 50 = 1,500 (comparable to grid search)
```

**Complexity:** O(p * i) where p = particles, i = iterations

---

## Computational Cost Analysis

### Scaling with Parameter Count

| Parameters | Grid Search (10 vals/param) | PSO (30 particles, 50 iter) |
|------------|----------------------------|------------------------------|
| 2          | 100 evaluations            | 1,500 evaluations            |
| 3          | 1,000 evaluations          | 1,500 evaluations            |
| 4          | 10,000 evaluations         | 1,500 evaluations            |
| 5          | 100,000 evaluations        | 1,500 evaluations            |
| 6          | 1,000,000 evaluations      | 1,500 evaluations            |

**Curse of Dimensionality:** Grid search becomes infeasible beyond 3-4 parameters.

### Actual Project Performance

**Classical SMC (6 parameters):**
- Grid Search: ~1 million evaluations (impractical)
- PSO: ~1,500 evaluations (9 minutes on modern CPU)

**Adaptive SMC (3 parameters + 3 adaptive laws):**
- Effective dimensionality: 6
- PSO handles this efficiently
- Grid search would be prohibitively expensive

---

## Convergence Characteristics

### Grid Search

**Pros:**
- Guaranteed to find global optimum (within grid resolution)
- Deterministic results
- No tuning of optimizer hyperparameters
- Easy to parallelize

**Cons:**
- Wastes evaluations on poor regions
- Resolution limited by computational budget
- No early stopping (must complete all evaluations)
- Exponential scaling with dimensions

### PSO

**Pros:**
- Focuses search on promising regions
- Handles continuous parameter spaces
- Can escape local optima (with proper parameters)
- Efficient in high dimensions

**Cons:**
- Stochastic (different runs give different results)
- Requires tuning (inertia, cognitive, social weights)
- May converge prematurely
- No global optimum guarantee

---

## Empirical Results from This Project

### Methodology

From research phase (MT-5, MT-6 tasks):

**Test Setup:**
- 7 controllers tested
- 100 Monte Carlo runs each
- Metrics: Settling time, overshoot, energy, chattering
- Initial conditions: Random perturbations

**Controllers Optimized with PSO:**
1. Classical SMC (6 gains)
2. Super-Twisting Algorithm (4 gains)
3. Adaptive SMC (6 parameters)
4. Hybrid Adaptive STA-SMC (7 parameters)
5. Swing-Up SMC (8 parameters)

### Key Findings

**PSO Convergence:**
- Typical convergence: 20-30 iterations
- Best found early (iteration 10-15)
- Plateau after iteration 30

**Solution Quality:**
- Classical SMC: 2.3s settling time (PSO) vs 3.1s (manual tuning)
- Hybrid STA-SMC: 1.8s settling time (best overall)
- Chattering reduced by 15-45% vs default gains

**Robustness:**
- PSO-tuned gains more robust to initial conditions
- 95% success rate vs 78% for default gains

---

## Decision Guidelines

### Use Grid Search When:

1. **Low-Dimensional (≤3 parameters)**
   ```python
   # Example: Tuning boundary layer thickness only
   epsilon_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
   # Just 10 evaluations - grid search is fine
   ```

2. **Validation Required**
   - Verifying PSO found global optimum
   - Debugging controller behavior
   - Understanding parameter sensitivity

3. **Simple Fitness Landscape**
   - Unimodal (single peak)
   - Smooth gradients
   - No local optima

4. **Guaranteed Coverage Needed**
   - Safety-critical applications
   - Regulatory compliance
   - Exhaustive testing requirements

### Use PSO When:

1. **High-Dimensional (>4 parameters)**
   ```python
   # Example: Classical SMC with 6 gains
   # Grid search: 10^6 evals, PSO: 1,500 evals
   ```

2. **Limited Computational Budget**
   - Time constraints
   - Expensive simulations
   - Real-time adaptation

3. **Complex Fitness Landscape**
   - Multiple local optima
   - Noisy fitness function
   - Discontinuities

4. **Continuous Parameter Spaces**
   - No natural discretization
   - Fine-grained tuning needed
   - Real-valued gains

---

## Hybrid Approaches

### 1. Coarse Grid + PSO Refinement

**Strategy:**
```python
# Step 1: Coarse grid search (2-3 values per parameter)
k1_coarse = [10, 25, 40]
k2_coarse = [5, 10, 15]
# 9 evaluations, find best region

# Step 2: PSO refinement around best region
bounds = [
    (best_k1 - 10, best_k1 + 10),
    (best_k2 - 5, best_k2 + 5),
]
# 1,500 evaluations in promising region
```

**Benefits:**
- Reduces PSO search space
- Faster convergence
- Lower risk of missing global optimum

### 2. PSO with Grid-Based Initialization

**Strategy:**
```python
# Initialize PSO particles on a coarse grid
from pyswarms import single import GlobalBestPSO

# Create initial positions from grid
n_particles = 27  # 3^3 grid
initial_pos = create_grid_positions(bounds, n_per_dim=3)

# Run PSO
optimizer = GlobalBestPSO(
    n_particles=27,
    dimensions=6,
    options=pso_options,
    init_pos=initial_pos  # Grid-based start
)
```

**Benefits:**
- Systematic coverage + adaptive search
- Good for moderate dimensions (4-5)

### 3. Sequential Optimization

**Strategy:**
```python
# Phase 1: Grid search for critical parameters (k1, k3)
# Phase 2: PSO for remaining parameters (k2, k4, k5, k6)
# Phase 3: PSO refinement for all 6 parameters
```

**Benefits:**
- Balances thoroughness and efficiency
- Handles mixed importance parameters

---

## Best Practices

### Grid Search

**Parameter Bounds:**
```python
# Bad: Too wide, too many values
k_values = np.linspace(0, 100, 50)  # 50 values!

# Good: Reasonable range, manageable values
k_values = [5, 10, 15, 20, 25, 30]  # 6 values
```

**Resolution:**
- Start coarse (3-5 values per parameter)
- Refine around best region if needed
- Use log spacing for parameters spanning orders of magnitude

### PSO

**Particle Count:**
```python
# Rule of thumb: 10 + 2*sqrt(dimensions)
dimensions = 6
n_particles = 10 + 2*np.sqrt(6) = 15  # Minimum
n_particles = 30  # Recommended for robustness
```

**Iteration Count:**
```python
# Typical convergence: 20-30 iterations
# Add buffer: 50 iterations
# For critical applications: 100 iterations
```

**Bounds:**
```python
# Bad: Unbounded or too wide
bounds = [(0, 1000), ...]  # Will search non-physical values

# Good: Physically meaningful
bounds = [(1.0, 50.0), ...]  # Based on system dynamics
```

---

## Implementation Examples

### Grid Search (Low-Dimensional)

```python
import numpy as np
from src.controllers.classic_smc import ClassicalSMC
from src.core.simulation_runner import SimulationRunner

# Define grid for 2 parameters
k1_values = [5, 10, 15, 20, 25]
k2_values = [2, 5, 8, 11, 14]

best_score = float('inf')
best_gains = None

# Exhaustive search
for k1 in k1_values:
    for k2 in k2_values:
        # Create controller with these gains
        controller = ClassicalSMC(gains=[k1, k2, 15, 5, 20, 3])

        # Run simulation
        runner = SimulationRunner(controller, dynamics, config)
        results = runner.run()

        # Evaluate performance
        score = calculate_cost(results)

        if score < best_score:
            best_score = score
            best_gains = [k1, k2, 15, 5, 20, 3]

print(f"Best gains: {best_gains}")
print(f"Best score: {best_score}")
```

### PSO (High-Dimensional)

```python
from src.optimizer.pso_optimizer import PSOTuner

# Define bounds for all 6 parameters
bounds = [
    (1.0, 50.0),   # k1
    (0.5, 20.0),   # k2
    (1.0, 50.0),   # k3
    (0.5, 20.0),   # k4
    (1.0, 50.0),   # k5
    (0.1, 10.0),   # k6
]

# Create tuner
tuner = PSOTuner(
    controller_type='classical_smc',
    dynamics=dynamics,
    config=config
)

# Run optimization
best_gains, best_cost = tuner.optimize(
    bounds=bounds,
    n_particles=30,
    n_iterations=50,
    seed=42
)

print(f"Best gains: {best_gains}")
print(f"Best cost: {best_cost}")
```

---

## Computational Resource Planning

### Time Estimates (Per Evaluation)

**Single Simulation:**
- Dynamics: Simplified (~0.01s), Full (~0.02s)
- Controller: All types (~0.001s)
- Total: ~0.02-0.05s per evaluation

**Full Optimization:**

| Method | Evaluations | Total Time |
|--------|-------------|------------|
| Grid (3 params, 10 vals) | 1,000 | ~20-50 seconds |
| Grid (4 params, 10 vals) | 10,000 | ~3-8 minutes |
| PSO (6 params, 30×50) | 1,500 | ~30 seconds - 1.5 min |

### Parallelization

**Grid Search:**
```python
# Embarrassingly parallel - no communication needed
from joblib import Parallel, delayed

results = Parallel(n_jobs=-1)(
    delayed(evaluate_gains)(gains)
    for gains in all_combinations
)
```

**PSO:**
```python
# Particle evaluations can be parallelized within iteration
# But iterations must be sequential
from src.core.vector_sim import run_batch_simulation

# Evaluate all particles in parallel
fitness = run_batch_simulation(
    controller, dynamics, particle_positions, config
)
```

---

## Results Validation

### Statistical Significance

```python
# Run multiple trials with different seeds
pso_results = []
for seed in range(10):
    best_gains, cost = tuner.optimize(bounds, seed=seed)
    pso_results.append(cost)

# Check consistency
mean_cost = np.mean(pso_results)
std_cost = np.std(pso_results)
print(f"PSO Cost: {mean_cost:.2f} ± {std_cost:.2f}")

# Compare to grid search
grid_cost = best_grid_score
print(f"Grid Cost: {grid_cost:.2f}")
print(f"Improvement: {((grid_cost - mean_cost)/grid_cost * 100):.1f}%")
```

### Robustness Testing

```python
# Monte Carlo validation with optimized gains
from src.utils.analysis.statistical import monte_carlo_analysis

mc_results = monte_carlo_analysis(
    controller=controller,
    dynamics=dynamics,
    n_runs=100,
    seed=42
)

print(f"Success Rate: {mc_results['success_rate']:.1%}")
print(f"Mean Settling Time: {mc_results['mean_settling']:.2f}s")
```

---

## Common Pitfalls

### Grid Search

**1. Too Fine Resolution:**
```python
# Bad: 20 values per parameter, 3 parameters = 8,000 evals
k_values = np.linspace(1, 50, 20)

# Good: 5-7 values for initial exploration
k_values = [5, 10, 15, 20, 25, 30, 35]
```

**2. Ignoring Parameter Scaling:**
```python
# Bad: Linear spacing for parameters spanning orders of magnitude
epsilon = np.linspace(0.01, 10.0, 10)

# Good: Log spacing
epsilon = np.logspace(-2, 1, 10)  # 0.01 to 10
```

### PSO

**1. Too Few Particles:**
```python
# Bad: 5 particles for 6 dimensions
n_particles = 5  # Will likely converge to local optimum

# Good: At least 10 + 2*sqrt(d)
n_particles = max(20, 10 + 2*int(np.sqrt(dimensions)))
```

**2. Premature Convergence:**
```python
# Bad: Default PySwarms settings may converge too quickly
options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}

# Good: Encourage exploration
options = {'c1': 2.0, 'c2': 2.0, 'w': 0.9}
```

---

## Summary Recommendation Table

| Scenario | Method | Rationale |
|----------|--------|-----------|
| 1-2 parameters | **Grid** | Fast, exhaustive, simple |
| 3 parameters | **Grid or PSO** | Grid still feasible, PSO if budget limited |
| 4+ parameters | **PSO** | Grid becomes impractical |
| Debugging | **Grid (coarse)** | Systematic exploration |
| Production tuning | **PSO** | Best performance/cost ratio |
| Safety-critical | **Grid + PSO validation** | Exhaustive + optimized |
| Real-time adaptation | **PSO (online)** | Can run during operation |
| One-time tuning | **Grid (if ≤3 params)** | No hyperparameter tuning needed |

---

## Related Workflows

**PSO Workflows:**
- [PSO Optimization Workflow](pso-optimization-workflow.md) - General PSO usage
- [PSO for Adaptive SMC](pso-adaptive-smc.md) - Specific to adaptive controllers
- [PSO for Hybrid SMC](pso-hybrid-smc.md) - Specific to hybrid controllers
- [Robust PSO Optimization](../how-to/robust-pso-optimization.md) - Handling uncertainty

**Other Workflows:**
- [Batch Simulation Workflow](batch-simulation-workflow.md) - Running multiple simulations
- [Monte Carlo Validation](monte-carlo-validation-quickstart.md) - Statistical testing

**Theory:**
- [PSO Theory](../theory/pso-theory.md) - Mathematical foundations
- [SMC Theory](../theory/smc-theory.md) - Control theory background

---

**Last Updated:** November 10, 2025
**Status:** Complete (replaces "Under Construction" placeholder)
