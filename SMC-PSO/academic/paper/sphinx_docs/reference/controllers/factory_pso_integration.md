# controllers.factory.pso_integration

**Source:** `src\controllers\factory\pso_integration.py`

## Module Overview Advanced

PSO Integration Module for SMC Controllers

. This module provides optimized integration between SMC controllers and PSO optimization,


featuring thread-safe operations, performance monitoring, and error handling. ## Mathematical Foundation ### PSO-Controller Integration Architecture **Problem:** Particle Swarm Optimization (PSO) searches high-dimensional gain space for optimal controller performance. ```{math}
\min_{\vec{g} \in \mathcal{G}} J(\vec{g})
``` Where:
- $\vec{g}$: Gain vector (e.g., $[c_1, c_2, \lambda_1, \lambda_2, K, \epsilon]$)
- $\mathcal{G}$: Admissible gain space (bounds + constraints)
- $J$: Cost function (e.g., ITAE + control effort) ### Fitness Function Design **Multi-objective cost:** ```{math}
J(\vec{g}) = w_1 \text{ITAE}(\vec{g}) + w_2 \text{RMS}_u(\vec{g}) + w_3 \text{CHAT}(\vec{g}) + w_4 \text{VIOL}(\vec{g})
``` Where:

- **ITAE:** $\int_0^T t |\vec{e}(t)| dt$ (tracking error weighted by time)
- **RMS_u:** $\sqrt{\frac{1}{T} \int_0^T u^2(t) dt}$ (control effort)
- **CHAT:** $\int_0^T |\dot{u}(t)| dt$ (chattering index)
- **VIOL:** Constraint violations (saturation events) **Typical weights:** $w_1 = 1.0, w_2 = 0.1, w_3 = 0.05, w_4 = 10.0$ ### Gain Bounds for PSO **Physical constraints** define search space: ```{math}
\mathcal{G} = \prod_{i=1}^{n_g} [g_i^{min}, g_i^{max}]
``` **Example (Classical SMC with 6 gains):** | Gain | Symbol | Lower | Upper | Unit |
|------|--------|-------|-------|------|
| $c_1$ | Position 1 | 0.1 | 50.0 | — |
| $c_2$ | Position 2 | 0.1 | 50.0 | — |
| $\lambda_1$ | Velocity 1 | 0.1 | 50.0 | — |
| $\lambda_2$ | Velocity 2 | 0.1 | 50.0 | — |
| $K$ | Switching | 1.0 | 200.0 | N |
| $\epsilon$ | Boundary | 0.0 | 50.0 | rad | ### Factory-PSO Integration Pattern **Closure-based fitness function:** ```python
# example-metadata:
# runnable: false def

create_fitness_function( ctrl_type: SMCType, config: Config
) -> Callable[[np.ndarray], float]: """Returns fitness function for PSO.""" def fitness(gains: np.ndarray) -> float: # Create controller with candidate gains controller = create_smc_for_pso(ctrl_type, gains) # Simulate result = simulate(controller, config) # Compute cost return compute_cost(result) return fitness
``` **Benefits:**

- Encapsulates controller creation
- PSO only sees fitness function
- Easy to change controller type ### Batch Evaluation Optimization **Vectorized simulation** for PSO swarm: ```python
def batch_fitness( gains_population: np.ndarray, # Shape: (n_particles, n_gains) ctrl_type: SMCType
) -> np.ndarray: # Shape: (n_particles,) """Evaluate all particles in parallel.""" controllers = [create_smc_for_pso(ctrl_type, g) for g in gains_population] results = batch_simulate(controllers, config) return np.array([compute_cost(r) for r in results])
``` **Speedup:** $5{-}10\times$ using Numba JIT compilation ### Convergence Criteria **PSO stops when:** 1. **Fitness stagnation:** ```{math} \frac{f_{best}^{(k)} - f_{best}^{(k-10)}}{f_{best}^{(k-10)}} < \epsilon_{conv} ``` Typical: $\epsilon_{conv} = 10^{-4}$ 2. **Diversity collapse:** ```{math} \frac{1}{n_p} \sum_{i=1}^{n_p} \|\vec{g}_i - \bar{\vec{g}}\| < \epsilon_{div} ``` Where $\bar{\vec{g}}$ is swarm centroid 3. **Maximum iterations:** $k \geq k_{max}$ (e.g., 100) ### Post-Optimization Validation After PSO converges: 1. **Validate gains:** Check Hurwitz, Lyapunov, bounds
2. **Monte Carlo robustness:** Test with parameter uncertainty
3. **Frequency response:** Verify bandwidth requirements
4. **Hardware limits:** Check control authority **Rejection rate:** ~5-10% of PSO results fail validation. ### Hyperparameter Tuning **PSO meta-parameters:** ```{math}
\begin{align}
w &: \text{Inertia weight} \quad (0.729) \\
c_1 &: \text{Cognitive coefficient} \quad (1.494) \\
c_2 &: \text{Social coefficient} \quad (1.494) \\
n_p &: \text{Particles} \quad (30) \\
k_{max} &: \text{Iterations} \quad (50{-}100)
\end{align}
``` **Tuning guidelines:**

- Larger $w$: More exploration (slower convergence)
- Larger $c_1$: More individualism (local search)
- Larger $c_2$: More social behavior (global search) ## Architecture Diagram ```{mermaid}
graph TD A[PSO Optimizer] --> B[Generate Particle Swarm] B --> C[For Each Particle: gains] C --> D[Factory.create_smc_for_pso_ctrl_type_ gains_] D --> E[Simulate with Controller] E --> F[Compute Fitness: J_gains_] F --> G[Update Personal Best] G --> H[Update Global Best] H --> I{Converged?} I -->|No| J[Update Velocities & Positions] J --> C I -->|Yes| K[Validate Best Gains] K --> L{Pass Validation?} L -->|Yes| M[Return Optimal Gains] L -->|No| N[Re-run PSO with Stricter Constraints] style D fill:#9cf style F fill:#ff9 style M fill:#9f9 style N fill:#f99
``` ## Usage Examples ### Example 1: Basic PSO-Controller Integration ```python
from src.controllers.factory import create_smc_for_pso, SMCType, get_gain_bounds_for_pso
from src.optimizer.pso_optimizer import PSOTuner # Get parameter bounds for Classical SMC
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL) # Define fitness function
def fitness_function(gains): controller = create_smc_for_pso(SMCType.CLASSICAL, gains) result = simulate(controller, duration=5.0) return result.itae + 0.1 * result.rms_control # Initialize PSO
pso = PSOTuner( n_particles=30, bounds=bounds, fitness_function=fitness_function
) # Optimize
best_gains, best_fitness = pso.optimize(max_iterations=50)
print(f"Optimal gains: {best_gains}")
print(f"Best fitness: {best_fitness:.4f}")
``` ### Example 2: Multi-Objective Optimization ```python
# example-metadata:

# runnable: false # Multi-objective cost function

def multi_objective_fitness(gains): controller = create_smc_for_pso(SMCType.CLASSICAL, gains) result = simulate(controller, duration=5.0) # Weighted sum of objectives w_itae = 1.0 # Tracking error w_control = 0.1 # Control effort w_chat = 0.05 # Chattering w_viol = 10.0 # Constraint violations cost = (w_itae * result.itae + w_control * result.rms_control + w_chat * result.chattering_index + w_viol * result.violation_count) return cost pso = PSOTuner( n_particles=30, bounds=bounds, fitness_function=multi_objective_fitness
) best_gains, best_cost = pso.optimize(max_iterations=100)
``` ### Example 3: Convergence Monitoring ```python
# example-metadata:
# runnable: false #

PSO with convergence callback
def convergence_callback(iteration, best_fitness, diversity): print(f"Iteration {iteration:3d}: " f"Fitness={best_fitness:.4f}, " f"Diversity={diversity:.4f}") # Early stopping if fitness stagnant if iteration > 20: fitness_history = pso.get_fitness_history() improvement = abs(fitness_history[-1] - fitness_history[-10]) / fitness_history[-10] if improvement < 1e-4: print("Early stopping: convergence detected") return True # Stop optimization return False pso = PSOTuner( n_particles=30, bounds=bounds, fitness_function=fitness_function, convergence_callback=convergence_callback
) best_gains, _ = pso.optimize(max_iterations=200)
``` ### Example 4: Constraint Handling ```python
# Fitness with constraint penalties

def constrained_fitness(gains): # Create controller controller = create_smc_for_pso(SMCType.CLASSICAL, gains) # Validate gains first (cheap check) from src.controllers.smc.core.gain_validation import validate_all_criteria validation_config = { 'u_max': 100.0, 'omega_s': 2*np.pi*100, 'Delta_max': 20.0, 'u_eq_max': 80.0, } results = validate_all_criteria(gains, validation_config) # Heavy penalty for invalid gains if not all(results.values()): return 1e6 # Return worst fitness # Simulate only if gains valid result = simulate(controller, duration=5.0) return result.itae pso = PSOTuner(n_particles=30, bounds=bounds, fitness_function=constrained_fitness)
best_gains, _ = pso.optimize(max_iterations=100)
``` ### Example 5: Batch Fitness Evaluation (Parallel) ```python
from joblib import Parallel, delayed # Parallel fitness evaluation
def batch_fitness(gains_population): """Evaluate all particles in parallel.""" def eval_single(gains): controller = create_smc_for_pso(SMCType.CLASSICAL, gains) result = simulate(controller, duration=5.0) return result.itae # Parallel execution (8 cores) fitness_values = Parallel(n_jobs=8)( delayed(eval_single)(gains) for gains in gains_population ) return np.array(fitness_values) # PSO with batch evaluation
pso = PSOTuner( n_particles=30, bounds=bounds, fitness_function=batch_fitness, # Pass batch function batch_mode=True
) best_gains, _ = pso.optimize(max_iterations=50)
print(f"Speedup: ~8x using parallel evaluation")
``` ## Complete Source Code ```{literalinclude} ../../../src/controllers/factory/pso_integration.py

:language: python
:linenos:
```

---

## Classes

### `PSOOptimizable`

**Inherits from:** `Protocol` Protocol for PSO-optimizable controllers.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/pso_integration.py
:language: python
:pyobject: PSOOptimizable
:linenos:
``` #### Methods (2) ##### `compute_control(self, state)` Compute control output for given state. [View full source →](#method-psooptimizable-compute_control) ##### `max_force(self)` Maximum control force limit. [View full source →](#method-psooptimizable-max_force)

---

## `PSOPerformanceMetrics`

Performance metrics for PSO controller evaluation.

### Source Code ```

{literalinclude} ../../../src/controllers/factory/pso_integration.py

:language: python
:pyobject: PSOPerformanceMetrics
:linenos:
```

### `EnhancedPSOControllerWrapper`

Enhanced PSO-compatible controller wrapper with advanced features. Features:
- Thread-safe operation
- Performance monitoring
- Automatic saturation handling
- Error recovery mechanisms
- Statistical tracking #### Source Code ```{literalinclude} ../../../src/controllers/factory/pso_integration.py
:language: python
:pyobject: EnhancedPSOControllerWrapper
:linenos:
``` #### Methods (10) ##### `__init__(self, controller, controller_type, max_force, enable_monitoring)` Initialize enhanced PSO wrapper. [View full source →](#method-enhancedpsocontrollerwrapper-__init__) ##### `compute_control(self, state)` PSO-compatible control computation with enhanced error handling. [View full source →](#method-enhancedpsocontrollerwrapper-compute_control) ##### `_validate_state(self, state)` Validate input state vector. [View full source →](#method-enhancedpsocontrollerwrapper-_validate_state) ##### `_extract_control_value(self, result)` Extract control value from controller result. [View full source →](#method-enhancedpsocontrollerwrapper-_extract_control_value) ##### `_apply_safety_constraints(self, control_value)` Apply safety constraints to control value. [View full source →](#method-enhancedpsocontrollerwrapper-_apply_safety_constraints) ##### `_get_safe_fallback_control(self, state)` Generate safe fallback control for error conditions. [View full source →](#method-enhancedpsocontrollerwrapper-_get_safe_fallback_control) ##### `_update_metrics(self, computation_time, control_value)` Update performance metrics. [View full source →](#method-enhancedpsocontrollerwrapper-_update_metrics) ##### `get_performance_metrics(self)` Get current performance metrics. [View full source →](#method-enhancedpsocontrollerwrapper-get_performance_metrics) ##### `reset_metrics(self)` Reset performance metrics. [View full source →](#method-enhancedpsocontrollerwrapper-reset_metrics) ##### `n_gains(self)` Number of gains for PSO compatibility. [View full source →](#method-enhancedpsocontrollerwrapper-n_gains)

---

## Functions

### `create_enhanced_pso_controller(smc_type, gains, plant_config, max_force, dt, enable_monitoring)`

Create enhanced PSO-compatible controller with advanced features. Args: smc_type: SMC controller type gains: Controller gains plant_config: Plant configuration (optional) max_force: Maximum control force dt: Control timestep enable_monitoring: performance monitoring **kwargs: Additional controller parameters Returns: Enhanced PSO controller wrapper Raises: ValueError: If parameters are invalid

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/pso_integration.py

:language: python
:pyobject: create_enhanced_pso_controller
:linenos:
```

### `create_optimized_pso_factory(smc_type, plant_config, max_force, enable_monitoring)`

Create optimized PSO factory function for controller creation. Args: smc_type: SMC controller type plant_config: Plant configuration (optional) max_force: Maximum control force enable_monitoring: performance monitoring **kwargs: Additional factory parameters Returns: Factory function that creates PSO controllers from gains

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/pso_integration.py
:language: python
:pyobject: create_optimized_pso_factory
:linenos:
```

### `get_optimized_pso_bounds(smc_type, performance_target)`

Get optimized PSO bounds based on performance targets. Args: smc_type: Controller type performance_target: 'aggressive', 'balanced', or 'conservative' Returns: Tuple of (lower_bounds, upper_bounds)

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/pso_integration.py

:language: python
:pyobject: get_optimized_pso_bounds
:linenos:
```

### `validate_pso_gains_advanced(smc_type, gains, check_stability)`

Advanced validation of PSO gains with stability analysis. Args: smc_type: Controller type gains: Gains to validate check_stability: Perform stability checks Returns: Dictionary with validation results

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/pso_integration.py
:language: python
:pyobject: validate_pso_gains_advanced
:linenos:
```

---

## Dependencies This module imports: - `import logging`

- `import time`
- `from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union`
- `from dataclasses import dataclass`
- `from abc import ABC, abstractmethod`
- `import numpy as np`
- `from ..factory import SMCType, create_controller, CONTROLLER_REGISTRY`
