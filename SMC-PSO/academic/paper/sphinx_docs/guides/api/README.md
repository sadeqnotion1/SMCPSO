# API Reference Guides **Type:** Technical Reference with Examples

**Level:** Intermediate to Advanced
**Prerequisites:** [Getting Started](../getting-started.md), [Tutorial 01](../tutorials/tutorial-01-first-simulation.md)

---

## Overview The DIP SMC PSO framework provides a Python API for simulating, controlling, and optimizing double-inverted pendulum systems. These API guides bridge the gap between task-oriented [How-To Guides](../how-to/) and the detailed [Technical Reference](../../reference/index.md). **What You'll Find Here:**

- Module overviews with architecture diagrams
- Common usage patterns and examples
- Integration workflows
- Parameter references
- Links to detailed technical documentation **Related Documentation:**
- **Learning:** [Tutorials](../tutorials/) - Step-by-step learning path
- **Tasks:** [How-To Guides](../how-to/) - Task-oriented recipes
- **Reference:** [User Guide](../user-guide.md) - workflows
- **Technical:** [API Reference](../../reference/index.md) - Auto-generated docs

---

## Framework Architecture ```

┌─────────────────────────────────────────────────────────────┐
│ User Application Layer │
│ (simulate.py, streamlit_app.py, custom scripts) │
└───────────────┬─────────────────────────────────────────────┘ │
┌───────────────┴─────────────────────────────────────────────┐
│ High-Level API Layer │
├──────────────────────┬──────────────────┬───────────────────┤
│ Controllers API │ Simulation API │ Optimization API │
│ - Factory pattern │ - Runner │ - PSO Tuner │
│ - 4 SMC types │ - Dynamics │ - Cost functions │
│ - Custom creation │ - Context │ - Bounds │
└──────────────────────┴──────────────────┴───────────────────┘ │
┌───────────────┴─────────────────────────────────────────────┐
│ Supporting Services Layer │
├──────────────────────┬──────────────────┬───────────────────┤
│ Configuration API │ Plant Models │ Utilities API │
│ - YAML loading │ - Physics │ - Validation │
│ - Schema validation │ - Dynamics │ - Control prims │
│ - Overrides │ - Parameters │ - Monitoring │
└──────────────────────┴──────────────────┴───────────────────┘
```

---

## Module Guides ### [Controllers API](controllers.md) **Create and configure sliding mode controllers** ```python
from src.controllers import create_controller, SMCType controller = create_controller('classical_smc', config=config.controllers.classical_smc)
``` **Covers:**

- Factory pattern (create_controller, create_smc_for_pso)
- 4 SMC controller types (Classical, STA, Adaptive, Hybrid)
- Custom controller development
- Parameter configuration **When to use:** Creating controllers, tuning gains, implementing custom SMC variants **See:** [Controllers API Guide →](controllers.md)

---

### [Simulation API](simulation.md) **Run simulations with dynamics models** ```python

from src.core import SimulationRunner runner = SimulationRunner(config)
result = runner.run(controller)
``` **Covers:**
- SimulationRunner interface
- Dynamics models (simplified vs full)
- Simulation context and state management
- Batch processing with vector_sim **When to use:** Running simulations, selecting dynamics models, batch experiments **See:** [Simulation API Guide →](simulation.md)

---

### [Optimization API](optimization.md) **Optimize controller gains with PSO** ```python
from src.optimizer import PSOTuner tuner = PSOTuner(controller_type=SMCType.CLASSICAL, bounds=bounds)
best_gains, best_cost = tuner.optimize()
``` **Covers:**

- PSOTuner configuration
- Custom cost function design
- Gain bounds specification
- Convergence monitoring **When to use:** Automated gain tuning, multi-objective optimization, parameter search **See:** [Optimization API Guide →](optimization.md)

---

### [Configuration API](configuration.md) **Load and manage configuration** ```python

from src.config import load_config config = load_config('config.yaml')
``` **Covers:**
- Configuration loading and validation
- Schema structure (physics, controllers, simulation, PSO)
- Programmatic configuration creation
- Environment variables and overrides **When to use:** Managing configurations, parameter validation, environment-specific setups **See:** [Configuration API Guide →](configuration.md)

---

### [Plant Models API](plant-models.md) **Physics models and parameters** ```python
from src.core import DoubleInvertedPendulum dynamics = DoubleInvertedPendulum(m0=1.0, m1=0.1, m2=0.1, l1=0.5, l2=0.5)
``` **Covers:**

- System physics and equations of motion
- Model types (simplified, full nonlinear, low-rank)
- Parameter definitions (masses, lengths, friction)
- Custom dynamics implementation **When to use:** Understanding system physics, selecting models, parameter sensitivity analysis **See:** [Plant Models API Guide →](plant-models.md)

---

### [Utilities API](utilities.md) **Helper functions and tools** ```python

# example-metadata:

# runnable: false from src.utils import validate_state, saturation, PerformanceMonitor

``` **Covers:**
- Validation utilities
- Control primitives (saturation, deadzone, smoothing)
- Monitoring and diagnostics
- Analysis tools **When to use:** Input validation, real-time monitoring, performance analysis **See:** [Utilities API Guide →](utilities.md)

---

## Quick Start Patterns ### Pattern 1: Basic Simulation ```python
from src.config import load_config
from src.controllers import create_controller
from src.core import SimulationRunner # Load configuration
config = load_config('config.yaml') # Create controller
controller = create_controller('classical_smc', config=config.controllers.classical_smc) # Run simulation
runner = SimulationRunner(config)
result = runner.run(controller) # Access results
print(f"ISE: {result['metrics']['ise']:.4f}")
``` ### Pattern 2: PSO Optimization ```python

from src.optimizer import PSOTuner
from src.controllers import get_gain_bounds_for_pso, SMCType # Get bounds for controller type
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL) # Create PSO tuner
tuner = PSOTuner( controller_type=SMCType.CLASSICAL, bounds=bounds, n_particles=30, iters=100
) # Optimize
best_gains, best_cost = tuner.optimize()
``` ### Pattern 3: Custom Configuration ```python
from src.config.schemas import SimulationConfig # Programmatic configuration
config = SimulationConfig( duration=5.0, dt=0.01, initial_conditions=[0, 0, 0.1, 0, 0.15, 0]
)
```

---

## Learning Paths ### For Beginners

1. [Getting Started Guide](../getting-started.md) → Basic CLI usage
2. [Tutorial 01](../tutorials/tutorial-01-first-simulation.md) → First simulation
3. [Controllers API](controllers.md) → Understand controller creation
4. [Simulation API](simulation.md) → Learn simulation execution ### For Researchers
1. [Tutorial 02](../tutorials/tutorial-02-controller-comparison.md) → Compare controllers
2. [Controllers API](controllers.md) → Deep dive into SMC variants
3. [Optimization API](optimization.md) → Automated tuning
4. [Tutorial 05](../tutorials/tutorial-05-research-workflow.md) → Research workflow ### For Developers
1. [Tutorial 04](../tutorials/tutorial-04-custom-controller.md) → Custom controller
2. [Controllers API](controllers.md) → Factory integration
3. [Configuration API](configuration.md) → Advanced configuration
4. [Utilities API](utilities.md) → Helper tools

---

## Common Questions **Q: What's the difference between these API guides and the Technical Reference?** A: **API Guides** are user-friendly, example-driven introductions to each module with common patterns. **Technical Reference** (`docs/reference/`) is auto-generated, API documentation with all classes, methods, and parameters. **Q: Should I use create_controller() or create_smc_for_pso()?** A: Use `create_controller()` for general usage with full configuration. Use `create_smc_for_pso()` for PSO optimization workflows where you only need to pass gain arrays. See [Controllers API](controllers.md#factory-system). **Q: When should I use simplified vs full dynamics?** A: Use **simplified dynamics** for rapid iteration and PSO optimization (10x faster). Use **full nonlinear dynamics** for high-fidelity simulation and final validation. See [Simulation API](simulation.md#dynamics-models). **Q: How do I create custom cost functions?** A: Implement a function with signature `(metrics: dict, config: dict) -> float`. See [Optimization API](optimization.md#custom-cost-functions) for examples.

## Next Steps - **Start Learning:** [Tutorial 01: First Simulation](../tutorials/tutorial-01-first-simulation.md)

- **Task Recipes:** [How-To Guides](../how-to/)
- **Workflows:** [User Guide](../user-guide.md)
- **Technical Details:** [API Reference](../../reference/index.md)

---

**Last Updated:** October 2025
