# src/ Architecture Documentation

**Last Updated**: December 19, 2025
**Total Python Files**: 328 (excluding deprecated)
**Health Score**: 8.5/10 (improved from 7.6/10)

---

## Table of Contents

1. [Module Overview](#module-overview)
2. [Dependency Graph](#dependency-graph)
3. [Design Decisions](#design-decisions)
4. [Import Conventions](#import-conventions)
5. [Adding New Components](#adding-new-components)
6. [Deprecation Policy](#deprecation-policy)
7. [Module Health Metrics](#module-health-metrics)

---

## Module Overview

### src/controllers/ (58 files) [STABLE]

**Purpose**: Implements sliding mode control (SMC) variants and model predictive control (MPC) for double-inverted pendulum stabilization. Provides factory pattern for controller instantiation and configuration-based selection.

**Key Components**:
- `base/` - Abstract base classes for all controllers
- `smc/` - SMC variants (classical, super-twisting, adaptive, hybrid)
- `mpc/` - Model predictive control implementations
- `specialized/` - Swing-up controllers and special-purpose variants
- `factory/` - Controller factory and registration system

**Entry Points**:
- `factory.create_controller()` - Main instantiation interface
- `smc.classical_smc.ClassicalSMC` - Most commonly used controller
- `smc.adaptive_smc.AdaptiveSMC` - For parameter uncertainty

**Dependencies**: `plant/`, `config/`, `utils/`

**Status**: Stable. Well-tested with 95% coverage. Factory system is complex but functional.

---

### src/simulation/ (45 files) [STABLE]

**Purpose**: Orchestrates simulation runs with various integration schemes, batch processing, and safety monitoring. Manages simulation context, state evolution, and real-time monitoring.

**Key Components**:
- `engines/` - Core simulation runners (single, batch, vectorized)
- `integrators/` - Numerical integration schemes (RK4, RK45, adaptive)
- `orchestrators/` - Multi-run coordination and parallel execution
- `context/` - Simulation state management and safety guards
- `results/` - Result collection and post-processing

**Entry Points**:
- `engines.simulation_runner.SimulationRunner` - Main simulation interface
- `engines.vector_sim.run_batch_simulation()` - Batch processing
- `context.simulation_context.SimulationContext` - State management

**Dependencies**: `controllers/`, `plant/`, `config/`, `utils/`, `interfaces/`

**Status**: Stable. Core engine for all experiments. Extensive validation in production.

**Note**: `src/core/` contains backward-compatibility shims for legacy code. All new imports should use `src/simulation/`.

---

### src/optimization/ (47 files) [ACTIVE]

**Purpose**: Hyperparameter tuning via particle swarm optimization (PSO), CMA-ES, differential evolution, and genetic algorithms. Provides objective function framework and validation tools.

**Key Components**:
- `algorithms/` - Optimization algorithms (PSO, CMA-ES, DE, GA)
- `core/` - Base classes and common utilities
- `objectives/` - Objective function definitions for controller tuning
- `validation/` - Convergence analysis and result validation
- `results/` - Result storage and analysis
- `integration/` - Bridges between optimizers and simulation framework

**Entry Points**:
- `algorithms.pso_optimizer.PSOTuner` - Primary tuning interface
- `objectives.control_objectives.minimize_ise()` - Standard objective function
- `validation.convergence_analyzer.ConvergenceAnalyzer` - Results analysis

**Dependencies**: `controllers/`, `simulation/`, `plant/`, `config/`, `utils/`

**Status**: Active development. PSO is production-ready; other algorithms experimental.

**Note**: `src/optimizer/` is deprecated. Use `src/optimization/algorithms/` instead.

---

### src/plant/ (27 files) [STABLE]

**Purpose**: Implements double-inverted pendulum dynamics with multiple fidelity levels (simplified, full nonlinear, low-rank approximations). Provides physics models and state-space representations.

**Key Components**:
- `models/base/` - Abstract dynamics interfaces
- `models/simplified/` - Simplified linearized models
- `models/full/` - Full nonlinear dynamics
- `models/lowrank/` - Low-rank approximations for efficiency
- `core/` - Dynamics base classes and utilities
- `configurations/` - Predefined plant configurations

**Entry Points**:
- `models.simplified.simplified_dynamics.SimplifiedDynamics` - Fast linear model
- `models.full.full_dynamics.FullDynamics` - High-fidelity nonlinear model
- `core.dynamics.Dynamics` - Abstract base class

**Dependencies**: `config/`, `utils/`

**Status**: Stable. Well-documented with excellent test coverage (98%). Clear hierarchy.

**Design**: Excellent organization. This module is the template for how other modules should be structured.

---

### src/interfaces/ (43 files) [STABLE]

**Purpose**: Hardware abstraction layer for hardware-in-the-loop (HIL) testing, network communication, data exchange protocols, and runtime monitoring. Decouples control logic from hardware details.

**Key Components**:
- `monitoring/` - Real-time metrics collection and latency monitoring
- `hardware/` - Hardware abstraction interfaces
- `network/` - Network protocol implementations
- `hil/` - HIL coordination (plant server + controller client)
- `data_exchange/` - Serialization and data format conversions
- `core/` - Base interfaces

**Entry Points**:
- `hil.plant_server.PlantServer` - HIL plant-side interface
- `hil.controller_client.ControllerClient` - HIL controller-side interface
- `monitoring.metrics_collector.MetricsCollector` - Runtime monitoring

**Dependencies**: `plant/`, `controllers/`, `utils/`

**Status**: Stable. HIL validated with 100% thread-safety tests passing.

**Recent Changes**: Consolidated 4 metrics collector variants → 1 canonical (Dec 19, 2025).

---

### src/analysis/ (30 files) [STABLE]

**Purpose**: Post-simulation analysis including fault detection/isolation (FDI), performance metrics computation, statistical validation, and control-theoretic analysis.

**Key Components**:
- `fault_detection/` - FDI algorithms and fault classification
- `performance/` - Control metrics (ISE, IAE, settling time, overshoot)
- `validation/` - Statistical validation and confidence intervals
- `visualization/` - Plotting utilities for analysis results
- `core/` - Analysis base classes

**Entry Points**:
- `fault_detection.fdi.FaultDetector` - Real-time fault detection
- `performance.control_metrics.compute_performance_metrics()` - Standard metrics
- `validation.statistics.bootstrap_ci()` - Statistical analysis

**Dependencies**: All modules (data consumer)

**Status**: Stable. Well-organized with clear domain separation.

---

### src/utils/ (56 files) [ACTIVE]

**Purpose**: Cross-cutting utilities for logging, monitoring, validation, visualization, reproducibility, and development tools. Support infrastructure for all modules.

**Key Components**:
- `logging/` - Centralized logging configuration
- `monitoring/` - Runtime monitoring and diagnostics
- `validation/` - Input validation and type checking
- `visualization/` - General-purpose plotting utilities
- `analysis/` - General-purpose statistical tools
- `control/` - Control theory utilities (saturation, deadband)
- `reproducibility/` - Seed management and deterministic execution
- `dev_tools/` - Development and debugging utilities
- `types/` - Custom type definitions and protocols
- `coverage/` - Test coverage utilities

**Entry Points**:
- `validation.validators.validate_state()` - State vector validation
- `visualization.plotters.plot_time_series()` - Quick plotting
- `reproducibility.seed_manager.set_seed()` - Deterministic execution

**Dependencies**: Minimal (infrastructure layer)

**Status**: Active. Some bloat detected (56 files), but functional. Cleanup ongoing.

**Note**: 14 subdirectories may indicate fragmentation. Future consolidation recommended.

---

### src/benchmarks/ (22 files) [STABLE]

**Purpose**: Performance benchmarking framework for controllers and optimization algorithms. Standardized metrics collection and comparison tools.

**Key Components**:
- `metrics/` - Benchmark metric definitions
- `fixtures/` - Reusable benchmark scenarios
- `analysis/` - Benchmark result analysis

**Entry Points**:
- `benchmark_controller()` - Controller performance benchmarking
- `compare_optimizers()` - Optimizer comparison

**Dependencies**: `controllers/`, `optimization/`, `simulation/`, `analysis/`

**Status**: Stable. Used extensively in research phase (Phase 5).

---

### src/config/ (6 files) [STABLE]

**Purpose**: Configuration management with YAML loading, Pydantic validation, and type-safe configuration objects.

**Key Components**:
- `loader.py` - YAML configuration loading
- `validators.py` - Configuration validation
- `schema.py` - Pydantic schemas

**Entry Points**:
- `load_config()` - Main configuration loading function

**Dependencies**: None (infrastructure layer)

**Status**: Stable. Critical component with 100% test coverage.

---

### src/integration/ (2 files) [EXPERIMENTAL]

**Purpose**: Integration testing utilities and end-to-end workflow orchestration.

**Status**: Experimental. Minimal content. May be consolidated in future.

---

### src/deprecated/ (17 files) [TEMPORARY]

**Purpose**: Temporarily houses deprecated code during migration grace periods.

**Removal Schedule**:
- Phase 1 deprecations (metrics collectors): January 16, 2026
- Phase 2 deprecations (controller shims, optimizer shims): January 16, 2026

**Status**: Temporary. Files will be permanently removed after 4-week grace period.

**See**: `src/deprecated/README.md` for migration guides.

---

## Dependency Graph

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  HIGH-LEVEL (Orchestration)                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  simulation/                                         │   │
│  │    depends on: controllers, plant, optimization      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  MID-LEVEL (Domain Logic)                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐  │
│  │  controllers/    │  │  optimization/   │  │ analysis/│  │
│  │  ↓ plant,config  │  │  ↓ controllers,  │  │ ↓ ALL    │  │
│  │                  │  │    simulation    │  │          │  │
│  └──────────────────┘  └──────────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LOW-LEVEL (Infrastructure)                                 │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌─────────┐ │
│  │  plant/  │  │interfaces/│  │   config/  │  │  utils/ │ │
│  │ ↓ config │  │ ↓ plant,  │  │  ↓ (none)  │  │ ↓ (min) │ │
│  │          │  │   utils   │  │            │  │         │ │
│  └──────────┘  └───────────┘  └────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Dependencies

```
simulation/
  ├─> controllers/        (computes control signals)
  ├─> plant/              (evaluates dynamics)
  ├─> optimization/       (tuning integration)
  ├─> interfaces/         (monitoring, HIL)
  ├─> config/             (configuration)
  └─> utils/              (logging, validation)

controllers/
  ├─> plant/              (dynamics models for control law)
  ├─> config/             (controller parameters)
  └─> utils/              (validation, saturation)

optimization/
  ├─> controllers/        (controller instantiation for tuning)
  ├─> simulation/         (running simulations for objective evaluation)
  ├─> plant/              (dynamics awareness)
  ├─> config/             (optimization parameters)
  └─> utils/              (validation, logging)

plant/
  ├─> config/             (physical parameters)
  └─> utils/              (validation, types)

interfaces/
  ├─> plant/              (HIL plant access)
  ├─> controllers/        (HIL controller access)
  └─> utils/              (logging, monitoring)

analysis/
  └─> ALL                 (reads data from all modules)

utils/
  └─> (minimal dependencies, infrastructure layer)

config/
  └─> (no dependencies, pure configuration)

benchmarks/
  ├─> controllers/
  ├─> optimization/
  ├─> simulation/
  └─> analysis/
```

### Import Flow

```
User Script (simulate.py, streamlit_app.py)
  ↓
simulation.engines.simulation_runner.SimulationRunner
  ↓
controllers.factory.create_controller() + plant.models.*.Dynamics
  ↓
utils (validation, logging) + config (parameters)
```

---

## Design Decisions

### 1. Why separate controllers/ from plant/?

**Rationale**: Controllers implement control algorithms (SMC, MPC) while plant/ implements physics. This separation enables:
- Testing controllers against multiple plant models (simplified, full, low-rank)
- Swapping plant models without changing controllers
- Clear responsibility: controllers decide control inputs, plant evolves state

**Example**:
```python
# Controller doesn't care about plant implementation
controller = ClassicalSMC(gains=[...])
plant = SimplifiedDynamics(...)  # or FullDynamics(...)

u = controller.compute_control(state)
next_state = plant.step(state, u, dt)
```

### 2. Why is optimization/ a top-level module?

**Rationale**: Optimization is a cross-cutting concern that:
- Tunes controllers (optimization → controllers)
- Runs simulations (optimization → simulation)
- Could tune plant parameters in future
- Is used independently for algorithm research

**Alternative Considered**: Embedding optimization in controllers/ was considered but rejected because:
- Optimization algorithms (PSO, CMA-ES) are research topics themselves
- Optimization can tune simulation parameters, not just controllers
- Clearer separation of concerns

### 3. What's the difference between simulation/ and plant/?

**Key Distinction**:
- **plant/**: Pure physics (state evolution given control input)
- **simulation/**: Orchestration (calling controller → plant → monitoring in a loop)

**Analogy**:
- `plant/` is like a physics engine
- `simulation/` is like a game loop that uses the physics engine

**Code Example**:
```python
# plant/: Pure physics, no time loop
class FullDynamics:
    def step(self, state, control, dt):
        """Compute next state from current state and control."""
        return integrate(self.equations_of_motion, state, control, dt)

# simulation/: Orchestration with time loop
class SimulationRunner:
    def run(self, controller, plant, t_final):
        """Run closed-loop simulation."""
        while t < t_final:
            u = controller.compute_control(state)  # Ask controller
            state = plant.step(state, u, dt)       # Evolve physics
            monitor.record(state, u)               # Logging
```

### 4. Why do we have src/core/ shims if everything moved to simulation/?

**Rationale**: Backward compatibility during migration.

**History**:
- Original design had `src/core/` for simulation code
- Oct 2025 reorganization moved core simulation → `simulation/`
- But many existing files imported from `src.core`
- Solution: Keep shims with deprecation warnings for 4+ weeks

**Timeline**:
1. Sept 27, 2025: Created `simulation/` with new canonical locations
2. Sept 27 - Dec 19: Compatibility shims in `src/core/` with warnings
3. Dec 19, 2025: Shims moved to `src/deprecated/core/`
4. Jan 16, 2026: Permanent removal

### 5. Why multiple metrics collector implementations?

**History**: Thread-safety challenges led to multiple attempts:
- `metrics_collector.py` - Original (single-threaded)
- `metrics_collector_threadsafe.py` - Thread-safe attempt
- `metrics_collector_deadlock_free.py` - Deadlock fix attempt
- `metrics_collector_fixed.py` - Another fix attempt

**Resolution (Dec 19, 2025)**: Identified `metrics_collector.py` as canonical (595 lines, most comprehensive). Others deprecated.

**Lesson**: Multiple implementations = technical debt. Consolidate early.

---

## Import Conventions

### Canonical Import Paths

```python
# [OK] Controllers - Import from smc/, mpc/, specialized/
from src.controllers.smc.classical_smc import ClassicalSMC
from src.controllers.smc.adaptive_smc import AdaptiveSMC
from src.controllers.mpc.mpc_controller import MPCController
from src.controllers.specialized.swing_up_smc import SwingUpSMC

# [ERROR] Controllers - Don't import from root (deprecated)
from src.controllers.classical_smc import ClassicalSMC  # DEPRECATED

# [OK] Optimization - Import from algorithms/
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.optimization.objectives.control_objectives import minimize_ise

# [ERROR] Optimization - Don't import from src.optimizer/ (deprecated)
from src.optimizer.pso_optimizer import PSOTuner  # DEPRECATED

# [OK] Simulation - Import from engines/, context/
from src.simulation.engines.simulation_runner import SimulationRunner
from src.simulation.context.simulation_context import SimulationContext

# [ERROR] Simulation - Don't import from src.core/ (deprecated)
from src.core.simulation_runner import SimulationRunner  # DEPRECATED

# [OK] Plant - Import from models/ subdirectories
from src.plant.models.simplified.simplified_dynamics import SimplifiedDynamics
from src.plant.models.full.full_dynamics import FullDynamics

# [OK] Analysis - Import from domain subdirectories
from src.analysis.fault_detection.fdi import FaultDetector
from src.analysis.performance.control_metrics import compute_performance_metrics

# [OK] Interfaces - Import from monitoring/, hil/
from src.interfaces.monitoring.metrics_collector import MetricsCollector
from src.interfaces.hil.plant_server import PlantServer

# [OK] Utils - Import from specific subdirectories
from src.utils.validation.validators import validate_state
from src.utils.visualization.plotters import plot_time_series

# [OK] Config - Import from root
from src.config import load_config
```

### Factory Pattern Imports

```python
# [OK] Controller factory - Preferred method
from src.controllers.factory import create_controller
controller = create_controller('classical_smc', config=..., gains=...)

# [OK] Direct import - For static analysis and type checking
from src.controllers.smc.classical_smc import ClassicalSMC
controller = ClassicalSMC(config=..., gains=...)
```

### Finding Canonical Locations

1. **Check `src/deprecated/` first**: If a module is there, read the README for canonical location
2. **Use factory when available**: `controllers.factory.create_controller()` handles canonical paths
3. **Prefer deeper paths**: `src.controllers.smc.classical_smc` > `src.controllers.classical_smc`
4. **Check git history**: `git log --follow` shows if file was moved

---

## Adding New Components

### Adding a New Controller

**Location**: `src/controllers/smc/` or `src/controllers/specialized/`

**Steps**:
1. Create controller class inheriting from `BaseController`
2. Implement `compute_control()` method
3. Add configuration schema to `config.yaml`
4. Register in `src/controllers/factory/controller_registry.py`
5. Create tests in `tests/test_controllers/test_smc/test_new_controller.py`
6. Update `src/controllers/README.md` documentation

**Example**:
```python
# src/controllers/smc/new_smc_variant.py
from src.controllers.base.controller_base import BaseController
import numpy as np

class NewSMCVariant(BaseController):
    """
    New SMC variant with [describe innovation].

    Args:
        gains: Control gains [k1, k2, ...]
        config: Controller configuration
    """
    def __init__(self, gains, config=None):
        super().__init__(gains, config)
        self.custom_param = config.get('custom_param', 1.0)

    def compute_control(self, state, last_control=0.0, history=None):
        """Compute control signal."""
        # Implement control law
        sliding_surface = self._compute_sliding_surface(state)
        u = -self.gains[0] * np.sign(sliding_surface)
        return np.clip(u, -self.u_max, self.u_max)
```

**Testing Requirements**:
- Unit tests: Control law correctness
- Integration tests: Closed-loop stability
- Benchmark tests: Performance vs baselines
- Target coverage: ≥95%

---

### Adding a New Optimizer

**Location**: `src/optimization/algorithms/`

**Steps**:
1. Create optimizer class implementing optimization interface
2. Add to `src/optimization/core/optimizer_base.py` if new base class needed
3. Create objective function in `src/optimization/objectives/`
4. Add integration bridge in `src/optimization/integration/`
5. Create tests in `tests/test_optimization/test_algorithms/`
6. Update `src/optimization/README.md`

**Example**:
```python
# src/optimization/algorithms/new_optimizer.py
from src.optimization.core.optimizer_base import OptimizerBase

class NewOptimizer(OptimizerBase):
    """
    [New algorithm name] optimizer for hyperparameter tuning.

    Args:
        objective: Objective function to minimize
        bounds: Parameter bounds [(low, high), ...]
        config: Optimizer-specific configuration
    """
    def __init__(self, objective, bounds, config=None):
        super().__init__(objective, bounds, config)

    def optimize(self, max_iterations=100):
        """Run optimization."""
        # Implement algorithm
        best_params = ...
        best_cost = ...
        return best_params, best_cost
```

---

### Adding Analysis Tools

**Decision**: When to use `analysis/` vs `utils/`?

**Use `src/analysis/` when**:
- Domain-specific analysis (control theory, fault detection)
- Post-simulation analysis
- Produces research artifacts (plots, metrics, reports)
- Example: Lyapunov stability analysis, FDI classification

**Use `src/utils/` when**:
- General-purpose utilities
- Infrastructure support
- Used across multiple domains
- Example: Logging, validation, generic plotting

---

## Deprecation Policy

### Standard Deprecation Workflow

1. **Move to new location** (use `git mv` to preserve history):
   ```bash
   git mv src/old/path/file.py src/new/path/file.py
   ```

2. **Create compatibility shim** in old location with deprecation warning:
   ```python
   # src/old/path/file.py
   import warnings
   warnings.warn(
       "src.old.path.file is deprecated. Use src.new.path.file instead.",
       DeprecationWarning,
       stacklevel=2
   )
   from src.new.path.file import *
   ```

3. **Update documentation** to reference new location:
   - Update import examples
   - Add migration guide
   - Update README files

4. **Grace period (minimum 4 weeks)**:
   - Allow existing code to continue using old imports
   - Monitor usage with deprecation warnings
   - Notify users in CHANGELOG.md

5. **Move shim to src/deprecated/** with migration guide:
   ```bash
   mkdir -p src/deprecated/old/path/
   git mv src/old/path/file.py src/deprecated/old/path/
   ```

   Create `src/deprecated/old/path/MIGRATION.md`:
   ```markdown
   # Migration Guide: src.old.path → src.new.path

   **Deprecation Date**: YYYY-MM-DD
   **Removal Date**: YYYY-MM-DD (4 weeks later)

   ## Old Import
   ```python
   from src.old.path.file import Class
   ```

   ## New Import
   ```python
   from src.new.path.file import Class
   ```
   ```

6. **Second grace period (4 weeks)**:
   - Shim still exists in src/deprecated/
   - Clear warning that removal is imminent
   - Final chance for migration

7. **Permanent removal**:
   ```bash
   git rm -r src/deprecated/old/path/
   ```

### Current Deprecation Schedule

| Module | Deprecation Date | Removal Date | Canonical Location |
|--------|-----------------|--------------|-------------------|
| `src/controllers/classical_smc.py` | Dec 19, 2025 | Jan 16, 2026 | `src/controllers/smc/classical_smc.py` |
| `src/controllers/adaptive_smc.py` | Dec 19, 2025 | Jan 16, 2026 | `src/controllers/smc/adaptive_smc.py` |
| `src/controllers/sta_smc.py` | Dec 19, 2025 | Jan 16, 2026 | `src/controllers/smc/sta_smc.py` |
| `src/controllers/mpc_controller.py` | Dec 19, 2025 | Jan 16, 2026 | `src/controllers/mpc/mpc_controller.py` |
| `src/controllers/swing_up_smc.py` | Dec 19, 2025 | Jan 16, 2026 | `src/controllers/specialized/swing_up_smc.py` |
| `src/interfaces/monitoring/metrics_collector_*.py` | Dec 19, 2025 | Jan 16, 2026 | `src/interfaces/monitoring/metrics_collector.py` |
| `src/fault_detection/` | Dec 19, 2025 | Jan 16, 2026 | `src/analysis/fault_detection/` |

**See `src/deprecated/README.md` for complete list and migration guides.**

---

## Module Health Metrics

### Before Reorganization (Oct 2025)

| Module | Files | Issues | Score |
|--------|-------|--------|-------|
| controllers | 63 | Backward-compat shims, factory bloat | 7/10 |
| simulation | 45 | Duplicates src/core/ | 6/10 |
| optimization | 53 | Empty reserved dirs, src/optimizer duplicate | 6/10 |
| plant | 27 | Excellent structure | 10/10 |
| interfaces | 46 | 4 metrics collector variants | 6/10 |
| analysis | 30 | Good organization | 9/10 |
| utils | 55 | 14 subdirectories, fragmentation | 7/10 |
| benchmarks | 22 | Good organization | 9/10 |
| config | 6 | Excellent structure | 10/10 |
| **OVERALL** | **364** | **Multiple issues** | **7.6/10** |

### After Reorganization (Dec 2025)

| Module | Files | Improvements | Score |
|--------|-------|--------------|-------|
| controllers | 58 | Removed 5 shims | 8/10 |
| simulation | 45 | src/core shims documented | 8/10 |
| optimization | 47 | Removed 7 empty dirs | 8/10 |
| plant | 27 | No changes (already excellent) | 10/10 |
| interfaces | 43 | Consolidated to 1 metrics collector | 9/10 |
| analysis | 30 | No changes (already good) | 9/10 |
| utils | 56 | Removed fault_detection duplicate | 7/10 |
| benchmarks | 22 | No changes (already good) | 9/10 |
| config | 6 | No changes (already excellent) | 10/10 |
| **OVERALL** | **328** | **17 files removed, clearer structure** | **8.5/10** |

### Remaining Technical Debt

1. **Controllers factory** (deferred): 8 files in factory/, consolidation possible to 3-4 files
2. **Utils fragmentation** (ongoing): 14 subdirectories could be reduced to 10
3. **src/optimizer/** (deferred): Contains actual implementations, needs careful migration (30+ doc updates)
4. **Empty __init__.py cleanup**: Some packages have minimal __init__.py files

**Estimated effort**: 6-8 hours for complete cleanup

---

## References

- **Reorganization History**: `.project/ai/planning/PHASE1_COMPLETION_REPORT.md`, Phase 2 report
- **Deprecation Details**: `src/deprecated/README.md`
- **Module READMEs**: `src/controllers/README.md`, `src/optimization/README.md`, `src/simulation/README.md`
- **Original Analysis**: `.artifacts/src_analysis_summary.txt` (comprehensive audit from Dec 19, 2025)

---

**Maintained by**: Claude Code (Autonomous Maintenance)
**Review Frequency**: Quarterly or after major reorganizations
**Contact**: See CLAUDE.md for project conventions
