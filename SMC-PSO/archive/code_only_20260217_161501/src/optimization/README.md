# Optimization Module

**Total Files**: 47
**Test Coverage**: 87%
**Status**: Active Development (PSO production-ready, others experimental)

---

## Overview

The optimization module provides hyperparameter tuning for controllers via metaheuristic algorithms. Primary focus is Particle Swarm Optimization (PSO) for control gain tuning, with experimental support for CMA-ES, Differential Evolution, and Genetic Algorithms.

---

## Directory Structure

```
src/optimization/               (47 files total)
├── algorithms/                 Optimization algorithms
│   ├── pso_optimizer.py        Particle Swarm Optimization [PRIMARY]
│   ├── cmaes_optimizer.py      CMA-ES (experimental)
│   ├── de_optimizer.py         Differential Evolution (experimental)
│   └── ga_optimizer.py         Genetic Algorithm (experimental)
│
├── core/                       Base classes and utilities
│   ├── optimizer_base.py       Abstract optimizer interface
│   └── population.py           Population management
│
├── objectives/                 Objective function definitions
│   ├── control_objectives.py   Standard control objectives (ISE, IAE, ITAE)
│   └── custom_objectives.py    User-defined objectives
│
├── validation/                 Result validation and analysis
│   ├── convergence_analyzer.py Convergence analysis
│   └── result_validator.py     Result validation
│
├── results/                    Result storage and processing
│   ├── result_manager.py       Result collection
│   └── data_export.py          Export to CSV/JSON
│
├── integration/                Bridges to other modules
│   ├── pso_factory_bridge.py   PSO + controller factory integration
│   └── simulation_bridge.py    PSO + simulation integration
│
└── tuning/                     High-level tuning interfaces
    └── controller_tuner.py     Unified controller tuning API
```

---

## Algorithms

### 1. Particle Swarm Optimization (PSO) [PRIMARY]

**Status**: Production-ready
**Use Case**: Controller gain tuning (recommended)

**Key Features**:
- Fast convergence (typically 50-100 iterations)
- Robust to local minima
- No gradient information required
- Parallel evaluation support

**Example**:
```python
from src.optimization.algorithms.pso_optimizer import PSOTuner

# Define bounds for 6 controller gains
bounds = [
    (0.1, 20.0),  # k1
    (0.1, 15.0),  # k2
    (0.1, 20.0),  # k3
    (0.1, 15.0),  # k4
    (0.1, 25.0),  # k5
    (0.1, 10.0),  # k6
]

# Create PSO tuner
tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    config={
        'n_particles': 30,
        'max_iter': 100,
        'w': 0.9,  # Inertia weight
        'c1': 2.0,  # Cognitive parameter
        'c2': 2.0,  # Social parameter
    }
)

# Run optimization
best_gains, best_cost = tuner.optimize()

print(f"Best gains: {best_gains}")
print(f"Best ISE: {best_cost}")
```

**Recommended PSO Parameters**:
- `n_particles`: 20-40 (more for high-dimensional problems)
- `max_iter`: 50-150 (convergence typically by iteration 100)
- `w`: 0.7-0.9 (inertia weight, controls exploration)
- `c1`: 1.5-2.5 (cognitive, attraction to personal best)
- `c2`: 1.5-2.5 (social, attraction to global best)

---

### 2. CMA-ES (Covariance Matrix Adaptation Evolution Strategy)

**Status**: Experimental
**Use Case**: High-dimensional optimization, local refinement

**Key Features**:
- Adapts search distribution
- Good for local optimization
- Slower than PSO but more thorough

**Example**:
```python
from src.optimization.algorithms.cmaes_optimizer import CMAESOptimizer

optimizer = CMAESOptimizer(
    objective=custom_objective_function,
    bounds=bounds,
    config={'popsize': 20, 'sigma0': 0.5}
)

best_params, best_cost = optimizer.optimize(max_iterations=200)
```

**Note**: Requires `cma` package. Install with `pip install cma`.

---

### 3. Differential Evolution (DE)

**Status**: Experimental
**Use Case**: Global optimization with simple implementation

**Example**:
```python
from src.optimization.algorithms.de_optimizer import DEOptimizer

optimizer = DEOptimizer(
    objective=custom_objective_function,
    bounds=bounds,
    config={'popsize': 30, 'mutation': 0.8, 'recombination': 0.7}
)

best_params, best_cost = optimizer.optimize(max_iterations=150)
```

---

### 4. Genetic Algorithm (GA)

**Status**: Experimental
**Use Case**: Discrete or mixed optimization problems

**Example**:
```python
from src.optimization.algorithms.ga_optimizer import GAOptimizer

optimizer = GAOptimizer(
    objective=custom_objective_function,
    bounds=bounds,
    config={'popsize': 50, 'mutation_rate': 0.1, 'crossover_rate': 0.8}
)

best_params, best_cost = optimizer.optimize(max_iterations=200)
```

---

## Objective Functions

### Built-in Control Objectives

```python
from src.optimization.objectives.control_objectives import (
    minimize_ise,    # Integral Squared Error
    minimize_iae,    # Integral Absolute Error
    minimize_itae,   # Integral Time-weighted Absolute Error
    multi_objective  # Combined objectives
)

# Use ISE (most common)
tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    objective='ise'  # Default: Integral Squared Error
)

# Use multi-objective
tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    objective='multi',
    config={
        'objective_weights': {
            'ise': 0.6,
            'control_effort': 0.2,
            'settling_time': 0.2
        }
    }
)
```

### Objective Function Definitions

**ISE (Integral Squared Error)**:
```
J = ∫[0,T] (θ₁² + θ₂² + θ̇₁² + θ̇₂²) dt
```
- Minimizes state deviations
- Penalizes large errors more than small errors
- Most commonly used

**IAE (Integral Absolute Error)**:
```
J = ∫[0,T] (|θ₁| + |θ₂| + |θ̇₁| + |θ̇₂|) dt
```
- Less sensitive to outliers than ISE
- More robust to measurement noise

**ITAE (Integral Time-weighted Absolute Error)**:
```
J = ∫[0,T] t * (|θ₁| + |θ₂| + |θ̇₁| + |θ̇₂|) dt
```
- Penalizes late-time errors more
- Encourages fast settling

---

### Custom Objective Functions

Define custom objectives for specialized requirements:

```python
from src.optimization.objectives.custom_objectives import CustomObjective

def custom_objective(gains, controller_type, plant_config):
    """
    Custom objective with constraints.

    Args:
        gains: Candidate controller gains
        controller_type: Controller type string
        plant_config: Plant configuration

    Returns:
        cost: Scalar cost (lower is better)
    """
    from src.controllers.factory import create_controller
    from src.simulation.engines.simulation_runner import SimulationRunner
    from src.plant.models.simplified.simplified_dynamics import SimplifiedDynamics

    # Create controller with candidate gains
    controller = create_controller(controller_type, gains=gains)
    plant = SimplifiedDynamics(config=plant_config)
    runner = SimulationRunner(controller, plant)

    # Run simulation
    result = runner.run(t_final=5.0)

    # Compute custom cost
    states = result['states']
    controls = result['controls']
    times = result['times']

    # ISE on states
    ise = np.sum(np.sum(states**2, axis=1) * np.diff(times, prepend=0))

    # Control effort penalty
    control_effort = np.sum(np.abs(controls) * np.diff(times, prepend=0))

    # Constraint: Penalize if max deflection > 30 degrees
    max_theta1 = np.max(np.abs(states[:, 0]))
    constraint_penalty = 1000.0 if max_theta1 > np.deg2rad(30) else 0.0

    # Combined cost
    cost = ise + 0.1 * control_effort + constraint_penalty

    return cost

# Use custom objective
tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    objective=custom_objective
)
```

---

## Complete Tuning Workflow

### Step 1: Define Configuration

```yaml
# config.yaml
optimization:
  pso:
    n_particles: 30
    max_iter: 100
    w: 0.9
    c1: 2.0
    c2: 2.0

  bounds:
    classical_smc:
      - [0.1, 20.0]  # k1
      - [0.1, 15.0]  # k2
      - [0.1, 20.0]  # k3
      - [0.1, 15.0]  # k4
      - [0.1, 25.0]  # k5
      - [0.1, 10.0]  # k6

controller:
  type: classical_smc
  u_max: 50.0
  dt: 0.01

plant:
  type: simplified
  # Physical parameters...
```

### Step 2: Run Optimization

```python
from src.config import load_config
from src.optimization.algorithms.pso_optimizer import PSOTuner

# Load configuration
config = load_config('config.yaml')

# Create tuner
tuner = PSOTuner(
    controller_type=config.controller.type,
    bounds=config.optimization.bounds.classical_smc,
    config=config.optimization.pso
)

# Run optimization
print("Starting PSO optimization...")
best_gains, best_cost = tuner.optimize()

print(f"Optimization complete!")
print(f"Best gains: {best_gains}")
print(f"Best ISE: {best_cost:.6f}")
```

### Step 3: Save Results

```python
from src.optimization.results.result_manager import save_optimization_result

# Save to JSON
save_optimization_result(
    filename='optimization_results/pso_classical_smc.json',
    gains=best_gains,
    cost=best_cost,
    metadata={
        'controller_type': 'classical_smc',
        'algorithm': 'pso',
        'n_particles': 30,
        'iterations': 100,
        'timestamp': datetime.now().isoformat()
    }
)
```

### Step 4: Load and Use Tuned Gains

```python
from src.optimization.results.result_manager import load_optimization_result
from src.controllers.factory import create_controller

# Load tuned gains
result = load_optimization_result('optimization_results/pso_classical_smc.json')
tuned_gains = result['gains']

# Create controller with tuned gains
controller = create_controller('classical_smc', gains=tuned_gains)

# Use in simulation
from src.simulation.engines.simulation_runner import SimulationRunner
from src.plant.models.full.full_dynamics import FullDynamics

plant = FullDynamics()
runner = SimulationRunner(controller, plant)
result = runner.run(t_final=10.0)
```

---

## CLI Usage

Use `simulate.py` CLI for optimization:

```bash
# Run PSO optimization for classical SMC
python simulate.py --ctrl classical_smc --run-pso --save gains_classical.json

# Run PSO for adaptive SMC
python simulate.py --ctrl adaptive_smc --run-pso --save gains_adaptive.json

# Load and test tuned gains
python simulate.py --load gains_classical.json --plot

# Compare tuned vs default gains
python simulate.py --ctrl classical_smc --plot
python simulate.py --load gains_classical.json --plot
```

---

## Convergence Analysis

Monitor PSO convergence:

```python
from src.optimization.validation.convergence_analyzer import ConvergenceAnalyzer

# During optimization, collect history
tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    config={'n_particles': 30, 'max_iter': 100, 'verbose': True}
)

best_gains, best_cost, history = tuner.optimize(return_history=True)

# Analyze convergence
analyzer = ConvergenceAnalyzer(history)

# Plot convergence curve
analyzer.plot_convergence()

# Check if converged
is_converged, convergence_iter = analyzer.check_convergence(
    tolerance=1e-4,
    patience=10
)

print(f"Converged: {is_converged} at iteration {convergence_iter}")
```

**Typical Convergence Patterns**:
- Rapid improvement: Iterations 1-30
- Refinement: Iterations 30-80
- Convergence: Iterations 80-100
- If no improvement after 50 iterations, consider stopping early

---

## Parallel Evaluation

PSO supports parallel objective function evaluation:

```python
from src.optimization.algorithms.pso_optimizer import PSOTuner

tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    config={
        'n_particles': 30,
        'max_iter': 100,
        'parallel': True,  # Enable parallel evaluation
        'n_processes': 4   # Use 4 CPU cores
    }
)

best_gains, best_cost = tuner.optimize()
```

**Speedup**: ~3x on 4 cores (overhead from inter-process communication)

**Note**: Requires `multiprocessing` support. May not work in Jupyter notebooks.

---

## Adding a New Optimization Algorithm

### Step 1: Create Optimizer Class

```python
# src/optimization/algorithms/new_optimizer.py
from src.optimization.core.optimizer_base import OptimizerBase
import numpy as np

class NewOptimizer(OptimizerBase):
    """
    Brief description of new algorithm.

    Args:
        objective: Objective function to minimize
        bounds: Parameter bounds [(low, high), ...]
        config: Algorithm-specific configuration
    """
    def __init__(self, objective, bounds, config=None):
        super().__init__(objective, bounds, config)

        # Extract config parameters
        self.param1 = config.get('param1', 1.0) if config else 1.0

    def optimize(self, max_iterations=100):
        """
        Run optimization.

        Args:
            max_iterations: Maximum number of iterations

        Returns:
            best_params: Best parameters found
            best_cost: Best cost achieved
        """
        # Initialize population
        population = self._initialize_population()

        for iteration in range(max_iterations):
            # Evaluate population
            costs = [self.objective(ind) for ind in population]

            # Update population (implement algorithm logic)
            population = self._update_population(population, costs)

            # Track best
            best_idx = np.argmin(costs)
            if costs[best_idx] < self.best_cost:
                self.best_cost = costs[best_idx]
                self.best_params = population[best_idx]

            # Log progress
            if self.verbose:
                print(f"Iteration {iteration}: Best cost = {self.best_cost:.6f}")

        return self.best_params, self.best_cost
```

### Step 2: Add Tests

```python
# tests/test_optimization/test_algorithms/test_new_optimizer.py
import pytest
from src.optimization.algorithms.new_optimizer import NewOptimizer

def test_new_optimizer_initialization():
    """Test optimizer initialization."""
    def objective(x):
        return sum(xi**2 for xi in x)

    bounds = [(0, 10)] * 5
    optimizer = NewOptimizer(objective, bounds)
    assert optimizer.bounds == bounds

def test_new_optimizer_optimization():
    """Test optimization on simple problem."""
    def sphere(x):
        return sum(xi**2 for xi in x)

    bounds = [(-5, 5)] * 3
    optimizer = NewOptimizer(sphere, bounds)
    best_params, best_cost = optimizer.optimize(max_iterations=50)

    # Should find minimum near [0, 0, 0]
    assert best_cost < 0.1
    assert all(abs(x) < 0.5 for x in best_params)
```

### Step 3: Integrate with simulate.py CLI

Update `simulate.py`:

```python
if args.run_new_optimizer:
    from src.optimization.algorithms.new_optimizer import NewOptimizer

    optimizer = NewOptimizer(
        objective=...,
        bounds=...,
        config=config.optimization.new_optimizer
    )

    best_params, best_cost = optimizer.optimize()
    print(f"Best parameters: {best_params}")
```

---

## Performance Tips

### 1. Choose Appropriate Bounds

```python
# Too wide: Slow convergence
bounds = [(0.001, 1000.0)] * 6  # BAD: 6 orders of magnitude

# Good: Reasonable range based on physics/experience
bounds = [(0.1, 20.0)] * 6  # GOOD: ~2 orders of magnitude
```

### 2. Use Simplified Plant for Tuning

```python
# SLOW: Use full nonlinear dynamics for tuning (expensive)
plant = FullDynamics()  # ~10x slower

# FAST: Use simplified dynamics for initial tuning
plant = SimplifiedDynamics()  # Fast, good approximation
```

Then verify on full dynamics:
```python
# After tuning on simplified
tuned_gains = [...]

# Verify on full nonlinear
controller = create_controller('classical_smc', gains=tuned_gains)
plant_full = FullDynamics()
runner = SimulationRunner(controller, plant_full)
result = runner.run(t_final=10.0)
```

### 3. Early Stopping

```python
tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    config={
        'max_iter': 200,
        'early_stopping': True,
        'patience': 20  # Stop if no improvement for 20 iterations
    }
)
```

### 4. Adaptive PSO Parameters

```python
# Adaptive inertia weight: Start high (exploration), end low (exploitation)
def adaptive_w(iteration, max_iter):
    return 0.9 - 0.5 * (iteration / max_iter)

tuner = PSOTuner(
    controller_type='classical_smc',
    bounds=bounds,
    config={
        'adaptive_w': True,  # Use adaptive inertia weight
        'w_range': (0.4, 0.9)
    }
)
```

---

## Common Issues & Troubleshooting

### Issue: PSO not converging

**Symptoms**: Cost remains high or fluctuates

**Causes & Solutions**:
1. **Bounds too wide**: Narrow bounds based on physics
2. **Population too small**: Increase `n_particles` (try 40-50)
3. **Max iterations too low**: Increase `max_iter` (try 150-200)
4. **Objective function noisy**: Add averaging over multiple trials

### Issue: Tuned gains perform poorly on full dynamics

**Cause**: Tuned on simplified plant, doesn't transfer

**Solution**: Use hierarchical tuning:
```python
# Step 1: Coarse tuning on simplified
tuner_simple = PSOTuner(plant_type='simplified', bounds=wide_bounds)
coarse_gains, _ = tuner_simple.optimize()

# Step 2: Fine tuning on full dynamics with narrow bounds
narrow_bounds = [(g*0.8, g*1.2) for g in coarse_gains]
tuner_full = PSOTuner(plant_type='full', bounds=narrow_bounds)
fine_gains, _ = tuner_full.optimize()
```

### Issue: ImportError for deprecated paths

**Error**: `from src.optimizer.pso_optimizer import PSOTuner`

**Solution**: Update to canonical path:
```python
from src.optimization.algorithms.pso_optimizer import PSOTuner
```

See `src/deprecated/README.md` for migration guide.

---

## References

- **Architecture**: `src/ARCHITECTURE.md`
- **Controllers**: `src/controllers/README.md`
- **Configuration**: `config.yaml`
- **Testing**: `tests/test_optimization/`
- **CLI**: `python simulate.py --help`
- **Research Paper**: `.artifacts/research/paper/` (PSO benchmarks, Section 4)

---

**Maintained by**: Optimization module team
**Last Review**: December 19, 2025
**Next Review**: March 2026
