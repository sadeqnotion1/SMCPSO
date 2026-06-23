# How-To: Optimization Workflows

**Type:** Task-Oriented Guide

**Level:** Intermediate to Advanced

**What This Guide Covers:**
This guide shows you how to optimize controller gains using Particle Swarm Optimization (PSO). You'll learn how to choose the right settings, design cost functions, and diagnose problems when optimization doesn't work as expected.

**Prerequisites:**
- [Tutorial 03: PSO Optimization](../tutorials/tutorial-03-pso-optimization.md) - basic PSO concepts
- [How-To: Running Simulations](running-simulations.md) - simulation basics

---

## Overview

**Why Optimization Matters:**
Default controller gains work, but they're not optimal for your specific setup. Optimization finds better gains automatically by testing thousands of combinations and keeping the best.

**What You'll Learn:**
- Run PSO optimization with appropriate settings
- Design custom cost functions for specific goals
- Diagnose convergence issues when PSO gets stuck
- Parallelize optimization to save time
- Deploy optimized controllers to production

**Expected Time:**
- Quick optimization: 2-3 minutes
- Production optimization: 8-10 minutes
- Thorough research optimization: 30-40 minutes

---

## Table of Contents - [PSO Parameter Tuning](#pso-parameter-tuning)

- [Custom Cost Functions](#custom-cost-functions)
- [Convergence Diagnostics](#convergence-diagnostics)
- [Production Optimization](#production-optimization)

---

## PSO Parameter Tuning

**What This Section Covers:**
PSO has several parameters that affect optimization quality and speed. This section shows you how to choose the right values for your situation.

### Quick Start

**Basic Commands:**
Start here if you just want to optimize quickly with default settings.

```bash
# Basic PSO optimization
python simulate.py --ctrl classical_smc --run-pso --save optimized_gains.json

# With specific seed for reproducibility
python simulate.py --ctrl classical_smc --run-pso --seed 42 --save gains.json

# Test optimized gains
python simulate.py --load optimized_gains.json --plot
```

### Choosing Swarm Size

**What Swarm Size Means:**
The swarm size is how many "particles" (candidate solutions) PSO uses. More particles mean better exploration but slower computation.

**Rule of Thumb:**
Use 10× the number of parameters you're optimizing.
- Formula: `n_particles = 10 × n_parameters`

**Examples for Different Controllers:**

```bash
# Classical SMC (6 gains) → 30-60 particles recommended
python simulate.py --ctrl classical_smc --run-pso \
  --override "pso.n_particles=30" \
  --save gains.json

# Adaptive SMC (5 gains) → 25-50 particles recommended
python simulate.py --ctrl adaptive_smc --run-pso \
  --override "pso.n_particles=30" \
  --save gains.json

# Hybrid SMC (4 gains) → 20-40 particles recommended
python simulate.py --ctrl hybrid_adaptive_sta_smc --run-pso \
  --override "pso.n_particles=25" \
  --save gains.json
``` **Swarm Size Trade-offs:** | Size | Exploration | Computation | Convergence | Best For |

|------|-------------|-------------|-------------|----------|
| Small (10-20) | Low | Fast | May get stuck | Quick prototyping |
| Medium (30-50) | Good | Moderate | Balanced | Production use |
| Large (60-100) | High | Slow | Robust | Difficult problems | ### Choosing Iteration Count ```bash
# Quick optimization (prototyping)

python simulate.py --ctrl classical_smc --run-pso \ --override "pso.iters=50" \ --override "pso.n_particles=15" \ --save quick_gains.json
# Time: ~2-3 minutes # Standard optimization (production)

python simulate.py --ctrl classical_smc --run-pso \ --override "pso.iters=100" \ --override "pso.n_particles=30" \ --save standard_gains.json
# Time: ~8-10 minutes # Thorough optimization (research)

python simulate.py --ctrl classical_smc --run-pso \ --override "pso.iters=200" \ --override "pso.n_particles=50" \ --save thorough_gains.json
# Time: ~30-40 minutes

``` **Iteration Count Guidelines:** - **Converged by iteration 50:** Increase bounds or swarm size (search space too constrained)
- **Converged by iteration 80:** Good convergence
- **Still improving at iteration 100:** Increase iterations to 150-200
- **No improvement by iteration 30:** Problem with cost function or bounds ### Optimizing Parameter Bounds **Default bounds (config.yaml):**
```yaml

pso: bounds: - [0.1, 50.0] # k₁ - [0.1, 50.0] # k₂ - [0.1, 50.0] # λ₁ - [0.1, 50.0] # λ₂ - [1.0, 200.0] # K - [0.0, 50.0] # ε (classical only)
``` **Narrow bounds (fine-tuning around known solution):**
```yaml

pso: bounds: - [8.0, 15.0] # k₁ near 10 - [6.0, 12.0] # k₂ near 8 - [12.0, 20.0] # λ₁ near 15 - [10.0, 16.0] # λ₂ near 12 - [40.0, 80.0] # K near 60 - [0.005, 0.05] # ε near 0.01
``` **Wide bounds (exploratory search):**
```yaml

pso: bounds: - [0.1, 100.0] # Very wide k₁ - [0.1, 100.0] # Very wide k₂ - [0.1, 100.0] # Very wide λ₁ - [0.1, 100.0] # Very wide λ₂ - [1.0, 500.0] # Very wide K - [0.001, 1.0] # Wide ε
``` **Bounds optimization workflow:** 1. **Start wide** (default bounds)
2. **Run PSO**, observe best gains
3. **Narrow bounds** around best solution (±30%)
4. **Re-run PSO** for fine-tuning
5. **Validate** on diverse scenarios ### Seed Strategy for Reproducibility ```bash
# Run multiple PSO trials with different seeds
for seed in 42 123 456 789 1337; do python simulate.py --ctrl classical_smc --run-pso \ --seed $seed \ --save "gains_seed_${seed}.json"
done # Compare results
python -c "
import json
import numpy as np seeds = [42, 123, 456, 789, 1337]
costs = [] for seed in seeds: data = json.load(open(f'gains_seed_{seed}.json')) costs.append(data['pso_cost']) print(f'Seed {seed}: Cost = {data[\"pso_cost\"]:.4f}') print(f'\nMean: {np.mean(costs):.4f}')
print(f'Std: {np.std(costs):.4f}')
print(f'Best: {np.min(costs):.4f} (seed {seeds[np.argmin(costs)]})')
"
``` **Seed selection guidelines:** - **Research/publication:** Run 5-10 seeds, report best + confidence interval

- **Production deployment:** Run 3-5 seeds, select most robust (not just best cost)
- **Quick testing:** Single seed (42 by convention)

---

## Custom Cost Functions ### Default Cost Function ```yaml

# config.yaml

pso: cost_function: weights: ise: 0.4 # Tracking accuracy itae: 0.3 # Convergence speed control_effort: 0.2 # Energy efficiency overshoot: 0.1 # Safety margin
``` ### Custom Weight Configurations **Emphasize tracking accuracy:**
```yaml

pso: cost_function: weights: ise: 0.7 # Dominant itae: 0.2 control_effort: 0.05 overshoot: 0.05
``` **Emphasize fast convergence:**
```yaml

pso: cost_function: weights: ise: 0.2 itae: 0.6 # Dominant control_effort: 0.1 overshoot: 0.1
``` **Emphasize energy efficiency:**
```yaml

pso: cost_function: weights: ise: 0.2 itae: 0.2 control_effort: 0.5 # Dominant overshoot: 0.1
``` ### Implementing Custom Cost Function Create `custom_cost.py`: ```python
# example-metadata:
# runnable: false def minimal_settling_time_cost(metrics, config): """ Custom cost emphasizing fast settling. Hard constraints: - Overshoot < 10% - Peak control < max_force Soft objective: - Minimize settling time """ # Hard constraints (return infinite cost if violated) if metrics['overshoot'] > 10.0: return float('inf') # Infeasible if metrics.get('max_control', 0) > config.get('max_force', 100.0): return float('inf') # Actuator limit violated # Primary objective: settling time cost = 0.7 * metrics['settling_time'] # Secondary objectives cost += 0.2 * metrics['ise'] cost += 0.1 * metrics['control_effort'] / 100.0 # Normalize return cost
``` **Use custom cost function:** ```python

from src.optimizer.pso_optimizer import PSOTuner
from custom_cost import minimal_settling_time_cost
from src.config import load_config # Load configuration
config = load_config('config.yaml') # Create PSO tuner with custom cost
tuner = PSOTuner( controller_type='classical_smc', config=config, cost_function=minimal_settling_time_cost # Custom!
) # Run optimization
best_gains, best_cost = tuner.optimize() print(f"Optimized gains: {best_gains}")
print(f"Final cost: {best_cost:.4f}")
``` ### Multi-Objective Cost Functions ```python
def pareto_cost(metrics, config, alpha=0.5): """ Pareto front exploration: performance vs efficiency. alpha=0.0: Pure efficiency (low control effort) alpha=1.0: Pure performance (low ISE) alpha=0.5: Balanced trade-off """ # Normalize metrics to [0, 1] range performance_cost = metrics['ise'] / 2.0 # Assume ISE < 2.0 efficiency_cost = metrics['control_effort'] / 500.0 # Assume effort < 500 # Weighted combination cost = alpha * performance_cost + (1 - alpha) * efficiency_cost return cost # Run PSO for multiple alpha values
alphas = [0.1, 0.3, 0.5, 0.7, 0.9]
pareto_solutions = [] for alpha in alphas: custom_cost = lambda m, c: pareto_cost(m, c, alpha=alpha) tuner = PSOTuner( controller_type='classical_smc', config=config, cost_function=custom_cost ) gains, cost = tuner.optimize() # Re-evaluate to get actual metrics result = evaluate_controller(gains) pareto_solutions.append({ 'alpha': alpha, 'gains': gains, 'ise': result['metrics']['ise'], 'control_effort': result['metrics']['control_effort'] }) # Plot Pareto front
import matplotlib.pyplot as plt ise_values = [sol['ise'] for sol in pareto_solutions]
effort_values = [sol['control_effort'] for sol in pareto_solutions] plt.plot(ise_values, effort_values, 'bo-')
plt.xlabel('ISE (Performance)')
plt.ylabel('Control Effort (Energy)')
plt.title('Pareto Front: Performance vs Efficiency')
plt.grid(True)
plt.show()
``` ### Constraint Handling ```python
# example-metadata:

# runnable: false def constrained_cost(metrics, config): """ Cost function with strict constraints. """ # Constraint 1: Settling time < 5 seconds if metrics['settling_time'] > 5.0: penalty = 1000 * (metrics['settling_time'] - 5.0) return penalty # Heavy penalty # Constraint 2: Overshoot < 5% if metrics['overshoot'] > 5.0: penalty = 1000 * (metrics['overshoot'] - 5.0) return penalty # Constraint 3: Control effort < 200 if metrics['control_effort'] > 200.0: penalty = 1000 * (metrics['control_effort'] - 200.0) return penalty # All constraints satisfied, minimize ISE return metrics['ise']

```

---

## Convergence Diagnostics ### Monitoring Convergence ```python
import matplotlib.pyplot as plt
import json # Load PSO results (if history is saved)
with open('optimized_gains.json') as f: data = json.load(f) if 'pso_history' in data: iterations = data['pso_history']['iterations'] best_costs = data['pso_history']['best_costs'] mean_costs = data['pso_history']['mean_costs'] # Plot convergence fig, ax = plt.subplots(figsize=(10, 6)) ax.plot(iterations, best_costs, 'b-', linewidth=2, label='Global Best') ax.plot(iterations, mean_costs, 'r--', linewidth=1, label='Swarm Mean') ax.set_xlabel('Iteration') ax.set_ylabel('Cost') ax.set_title('PSO Convergence') ax.legend() ax.grid(True) ax.set_yscale('log') # Log scale for better visibility plt.show()
``` ### Detecting Premature Convergence **Symptoms:**

- Best cost plateaus before iteration 50
- Mean cost equals best cost (swarm collapsed)
- No diversity in particle positions **Diagnosis:**
```python
# example-metadata:
# runnable: false # Check if swarm collapsed
if 'pso_history' in data: final_best = best_costs[-1] final_mean = mean_costs[-1] diversity_ratio = final_mean / final_best if diversity_ratio < 1.05: # Within 5% print("WARNING: Swarm collapsed (premature convergence)") print(f" Best: {final_best:.4f}") print(f" Mean: {final_mean:.4f}") print(f" Ratio: {diversity_ratio:.3f}") else: print("OK: Swarm maintains diversity")
``` **Solutions:**

1. **Increase swarm size:** `--override "pso.n_particles=50"`
2. **Widen bounds:** Increase parameter search space
3. **Adjust inertia weight:** `--override "pso.options.w=0.8"`
4. **Increase cognitive/social coefficients:** Promote exploration ### Oscillatory Convergence **Symptoms:**
- Best cost jumps around
- No clear downward trend **Diagnosis:**
```python
# Check cost volatility
cost_changes = np.diff(best_costs)
volatility = np.std(cost_changes) if volatility > 0.1 * np.mean(best_costs): print("WARNING: High convergence volatility") print(f" Volatility: {volatility:.4f}")
``` **Solutions:**

1. **Increase inertia weight:** Stabilize particle movement
2. **Reduce cognitive/social coefficients:** Less aggressive updates
3. **Check cost function:** May be discontinuous or noisy ### Restart Strategies ```python
# example-metadata:

# runnable: false def multi_start_pso(n_restarts=3): """ Run PSO multiple times with different initializations. """ best_overall_cost = float('inf') best_overall_gains = None for restart in range(n_restarts): print(f"\nRestart {restart + 1}/{n_restarts}") # Different seed for each restart seed = 42 + restart * 100 tuner = PSOTuner( controller_type='classical_smc', config=config, seed=seed ) gains, cost = tuner.optimize() print(f" Best cost: {cost:.4f}") if cost < best_overall_cost: best_overall_cost = cost best_overall_gains = gains print(f"\nBest across all restarts: {best_overall_cost:.4f}") return best_overall_gains, best_overall_cost

```

---

## Production Optimization ### Parallel PSO Execution ```python
import multiprocessing as mp
from functools import partial def run_pso_trial(seed, controller_type, config): """Run single PSO trial.""" tuner = PSOTuner( controller_type=controller_type, config=config, seed=seed ) gains, cost = tuner.optimize() return { 'seed': seed, 'gains': gains, 'cost': cost } # Define seeds
seeds = [42, 123, 456, 789, 1337] # Run in parallel
with mp.Pool(5) as pool: run_func = partial( run_pso_trial, controller_type='classical_smc', config=config ) results = pool.map(run_func, seeds) # Find best
best_result = min(results, key=lambda x: x['cost']) print(f"Best cost: {best_result['cost']:.4f}")
print(f"Best seed: {best_result['seed']}")
print(f"Best gains: {best_result['gains']}")
``` ### Checkpointing ```python

import pickle
import os def pso_with_checkpointing(checkpoint_interval=10): """ Run PSO with periodic checkpoints. """ checkpoint_file = 'pso_checkpoint.pkl' # Load checkpoint if exists if os.path.exists(checkpoint_file): with open(checkpoint_file, 'rb') as f: checkpoint = pickle.load(f) print(f"Resuming from iteration {checkpoint['iteration']}") start_iter = checkpoint['iteration'] best_gains = checkpoint['best_gains'] best_cost = checkpoint['best_cost'] else: start_iter = 0 best_gains = None best_cost = float('inf') # Run PSO (pseudo-code, adapt to your PSO implementation) for iteration in range(start_iter, 100): # PSO update step gains, cost = pso_step(iteration) if cost < best_cost: best_cost = cost best_gains = gains # Checkpoint every N iterations if (iteration + 1) % checkpoint_interval == 0: checkpoint = { 'iteration': iteration + 1, 'best_gains': best_gains, 'best_cost': best_cost } with open(checkpoint_file, 'wb') as f: pickle.dump(checkpoint, f) print(f"Checkpoint saved at iteration {iteration + 1}") # Clean up checkpoint if os.path.exists(checkpoint_file): os.remove(checkpoint_file) return best_gains, best_cost
``` ### Validation After Optimization ```bash
# After PSO, validate on multiple scenarios
python simulate.py --load optimized_gains.json \ --override "simulation.initial_conditions=[0,0,0.1,0,0.15,0]" \ --save validation_scenario1.json python simulate.py --load optimized_gains.json \ --override "simulation.initial_conditions=[0,0,0.2,0,0.25,0]" \ --save validation_scenario2.json python simulate.py --load optimized_gains.json \ --override "simulation.initial_conditions=[0,0,0.3,0,0.35,0]" \ --save validation_scenario3.json # Check robustness
python -c "
import json
import numpy as np scenarios = ['scenario1', 'scenario2', 'scenario3']
ise_values = [] for scenario in scenarios: data = json.load(open(f'validation_{scenario}.json')) ise_values.append(data['metrics']['ise']) print(f'Mean ISE: {np.mean(ise_values):.4f}')
print(f'Std ISE: {np.std(ise_values):.4f}')
print(f'Max ISE: {np.max(ise_values):.4f}') # Check if performance degrades too much
if np.std(ise_values) / np.mean(ise_values) > 0.3: print('WARNING: High performance variance (gains may be over-tuned)')
"
``` ### Deployment Checklist Before deploying optimized gains: - [ ] Validated on ≥3 different initial conditions

- [ ] Validated on ≥2 different mass configurations (±20%)
- [ ] Settling time < 5 seconds for all scenarios
- [ ] No actuator saturation (max control < max_force)
- [ ] No instability (state remains bounded)
- [ ] Tested in long-duration simulation (≥60 seconds)
- [ ] Documented: PSO settings, cost function, validation results
- [ ] Version controlled: committed gains + config to git

---

## Troubleshooting ### PSO Not Improving **Check 1: Cost function**

```python
# Test cost function manually
test_gains = [10, 8, 15, 12, 50, 5]
result = evaluate_controller(test_gains)
cost = compute_cost(result['metrics'], config)
print(f"Test cost: {cost:.4f}") # Try different gains, ensure cost changes
``` **Check 2: Bounds**

```python
# Verify bounds allow good approaches print("Parameter bounds:")
for i, bounds in enumerate(config.pso.bounds): print(f" Gain {i+1}: [{bounds[0]}, {bounds[1]}]")
``` **Check 3: Simulation stability**

```bash
# Test if simulations complete successfully
python simulate.py --ctrl classical_smc --plot
``` ### PSO Too Slow ```bash
# Reduce computational cost

python simulate.py --ctrl classical_smc --run-pso \ --override "simulation.duration=3.0" \ --override "simulation.use_full_dynamics=false" \ --override "pso.n_particles=20" \ --override "pso.iters=50" \ --save fast_gains.json
``` ### Optimized Gains Cause Instability ```python
# example-metadata:
# runnable: false # Check gains for physical plausibility
with open('optimized_gains.json') as f: gains = json.load(f)['gains'] print("Optimized gains:")
print(f" k1 (should be positive): {gains[0]:.2f}")
print(f" k2 (should be positive): {gains[1]:.2f}")
print(f" λ1 (should be positive): {gains[2]:.2f}")
print(f" λ2 (should be positive): {gains[3]:.2f}")
print(f" K (should be >> 0): {gains[4]:.2f}")
print(f" ε (should be small): {gains[5]:.4f}") # If gains are at bounds, widen search
```

---

## Next Steps ### Related Workflows

- [PSO Optimization Workflow](../workflows/pso-optimization-workflow.md): Step-by-step PSO workflow
- [Batch Simulation Workflow](../workflows/batch-simulation-workflow.md): Monte Carlo and parameter sweeps
- [Monte Carlo Validation](../workflows/monte-carlo-validation-quickstart.md): Statistical validation quickstart ### Related Guides
- [How-To: Result Analysis](result-analysis.md): Validate optimized controllers
- [Tutorial 03: PSO Optimization](../tutorials/tutorial-03-pso-optimization.md): PSO guide
- [How-To: Testing & Validation](testing-validation.md): Test optimized controllers
- [User Guide](../user-guide.md): Complete reference

---

**Last Updated:** October 2025
