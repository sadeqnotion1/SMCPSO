# Optimization & Simulation Documentation **PSO Optimization and Simulation Infrastructure**

## Overview This section provides documentation for the optimization algorithms (PSO) and simulation infrastructure used for controller gain tuning and performance evaluation.

## Technical Guides ```{toctree}

:maxdepth: 2
:caption: Optimization & Simulation guide
``` **Optimization & Simulation Guide** Complete documentation covering:
- **PSO Optimization**: Particle swarm algorithm, cost function design, uncertainty handling
- **Simulation Infrastructure**: Sequential runner, batch vectorization, integration methods
- **Configuration System**: Type-safe schemas, validation, physical constraints
- **Vectorized Batch Simulation**: Safety guards, early stopping, convergence detection
- **Simulation Context**: Framework integration and component management
- **Usage Examples**: PSO workflows, controller comparison, robustness analysis
- **Performance Optimization**: Memory efficiency, Numba JIT, vectorization

---

## Quick Reference ### PSO Cost Function $$
J = w_1 \cdot \frac{ISE}{n_{ISE}} + w_2 \cdot \frac{U^2}{n_U} + w_3 \cdot \frac{(\Delta U)^2}{n_{\Delta U}} + w_4 \cdot \frac{\sigma^2}{n_\sigma} + P_{fail}
$$ Components:
- **ISE**: Integral of squared error $\int_0^T \|\mathbf{x}(t)\|^2 dt$
- **U²**: Control effort $\int_0^T u(t)^2 dt$
- **(ΔU)²**: Control rate $\int_0^T \left(\frac{du}{dt}\right)^2 dt$
- **σ²**: Sliding variable energy $\int_0^T \sigma(t)^2 dt$
- **P_fail**: Graded instability penalty ### Integration Methods | Method | Order | Stability | Cost per Step | Use Case |
|--------|-------|-----------|---------------|----------|
| **Explicit Euler** | 1 | Conditional | 1× | Real-time, PSO optimization |
| **RK4** | 4 | Better | 4× | High-accuracy research |
| **Adaptive RK45** | 4-5 | | Variable | Energy conservation validation |

---

## Usage Examples ### PSO Optimization Workflow ```python
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.controllers import create_smc_for_pso, SMCType
from src.config import load_config # Load configuration
config = load_config("config.yaml") # Define controller factory
def controller_factory(gains): return create_smc_for_pso(SMCType.CLASSICAL, gains, max_force=100.0) # Initialize PSO tuner
tuner = PSOTuner( controller_factory=controller_factory, config=config, seed=42
) # Run optimization
result = tuner.optimise() # Extract best gains
best_gains = result['best_pos']
best_cost = result['best_cost']
``` ### Batch Controller Comparison ```python

from src.simulation.engines.vector_sim import simulate_system_batch
import numpy as np # Define controller configurations
particles = np.array([ [10.0, 8.0, 15.0, 12.0, 50.0, 5.0], # Conservative gains [20.0, 15.0, 25.0, 20.0, 80.0, 10.0], # Aggressive gains [5.0, 4.0, 10.0, 8.0, 30.0, 2.0], # Gentle gains
]) # Batch simulate
t, x_batch, u_batch, sigma_batch = simulate_system_batch( controller_factory=factory, particles=particles, sim_time=5.0, dt=0.01, u_max=100.0
) # Compute metrics
for i in range(len(particles)): ise = np.sum(x_batch[i, :-1, :3]**2 * 0.01, axis=1).sum() print(f"Controller {i+1} ISE: {ise:.4f}")
```

---

## Architecture Overview ```
Configuration System (Pydantic Schemas) │ ├──► PSO Optimizer │ ├─ Cost Function │ ├─ Uncertainty Evaluation │ └─ Batch Simulation │ ├──► Simulation Runner │ ├─ Euler Integration │ └─ State Management │ └──► Vector Simulation ├─ Safety Guards └─ Early Stopping
```

---

## Performance Features ### Memory Efficiency

- **View-Based Array Operations**: Minimize unnecessary copying
- **Broadcast Instead of Copy**: Reduce memory footprint for batch simulations
- **Eliminates 423+ copies** in typical 5-second simulation ### Computational Performance
- **Numba JIT Compilation**: 10-100× speedup for repeated evaluations
- **Vectorized Batch Simulation**: Replace sequential loops with parallel operations
- **Early Convergence Stopping**: 30-70% reduction in PSO computation time

---

## Related Documentation - **{doc}`../controllers/index`** - SMC controllers for PSO optimization

- **{doc}`../plant/index`** - Dynamics models for simulation
- **{doc}`../mathematical_foundations/index`** - Optimization theory and PSO algorithms
- **{doc}`../reference/optimization/index`** - API reference for optimization modules
- **{doc}`../reference/simulation/index`** - API reference for simulation engines

---

**Documentation Version:** 1.0 (Week 3 Complete)
**Last Updated:** 2025-10-04
**Coverage:** PSO optimization, simulation infrastructure, configuration system
---

**Navigation**: Return to [Master Navigation Hub](../NAVIGATION.md) | Browse all [Documentation Categories](../index.md)
