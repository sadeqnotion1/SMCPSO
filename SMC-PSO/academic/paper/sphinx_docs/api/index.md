# API Reference Documentation

**Complete API documentation for all modules in the DIP SMC PSO project**

This section provides comprehensive API documentation including controller APIs, optimization modules, configuration schemas, simulation engines, and factory system references.

---

## Overview

The API documentation covers:

- **[Controller APIs](#controller-apis)** - Factory methods, controller interfaces, control theory
- **[Factory System](#factory-system)** - Enhanced factory API, factory methods, PSO integration
- **[Optimization](#optimization)** - PSO optimization module API and algorithms
- **[Simulation Engine](#simulation-engine)** - Simulation runner, dynamics, performance
- **[Configuration](#configuration)** - Configuration schemas and validation
- **[Phase Completion Reports](#phase-completion-reports)** - API documentation development progress

---

## Controller APIs

Complete API documentation for all controller types and factory patterns.

```{toctree}
:maxdepth: 2
:caption: Controller APIs

controller_api_reference
controller_theory
```

**Key Documents:**
- [Controller API Reference](controller_api_reference.md) - Complete controller interface documentation
- [Controller Theory](controller_theory.md) - Mathematical foundations and control theory

---

## Factory System

Enhanced controller factory system API with PSO integration.

```{toctree}
:maxdepth: 2
:caption: Factory System

factory_system_api_reference
factory_reference
factory_methods_reference
```

**Factory Documentation:**
- [Factory System API Reference](factory_system_api_reference.md) - Complete factory system API
- [Factory Reference](factory_reference.md) - Factory patterns and usage
- [Factory Methods Reference](factory_methods_reference.md) - Factory method signatures and examples

---

## Optimization

PSO optimization module API and algorithm documentation.

```{toctree}
:maxdepth: 2
:caption: Optimization

optimization_module_api_reference
pso_optimization
```

**Optimization API:**
- [Optimization Module API Reference](optimization_module_api_reference.md) - Complete optimization API
- [PSO Optimization](pso_optimization.md) - Particle Swarm Optimization algorithms

---

## Simulation Engine

Simulation runner, dynamics models, and performance benchmarks.

```{toctree}
:maxdepth: 2
:caption: Simulation Engine

simulation_engine_api_reference
performance_benchmarks
```

**Simulation Documentation:**
- [Simulation Engine API Reference](simulation_engine_api_reference.md) - Simulation runner and dynamics
- [Performance Benchmarks](performance_benchmarks.md) - Benchmark results and optimization

---

## Configuration

Configuration schemas and validation framework.

```{toctree}
:maxdepth: 2
:caption: Configuration

configuration_schema
```

**Configuration API:**
- [Configuration Schema](configuration_schema.md) - YAML configuration schema and validation

---

## Phase Completion Reports

API documentation development progress reports across multiple phases.

```{toctree}
:maxdepth: 1
:caption: Phase Reports

phase_4_1_completion_report
phase_4_2_completion_report
phase_4_3_progress_report
phase_4_3_completion_report
phase_4_4_completion_report
```

**Development Progress:**
- Phase 4.1 - Controller API documentation foundation
- Phase 4.2 - Factory system API documentation
- Phase 4.3 - Optimization and simulation API documentation
- Phase 4.4 - Configuration and validation API documentation

---

## Auto-Generated Documentation

The following documentation is automatically generated from Python docstrings using Sphinx autodoc, ensuring synchronization with the codebase.

```{eval-rst}
.. automodule:: src.core.dynamics
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.controllers.factory
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.optimization.algorithms.pso_optimizer
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mt6_statistical_comparison
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mt6_visualize_pso_convergence
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mt6_visualize_performance_comparison_simple
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mt6_generate_report
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: optimize_adaptive_boundary
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## Key Modules

### Core Modules
- **src.core.dynamics** - Simulation engine and dynamics models
- **src.core.simulation_runner** - Simulation orchestration
- **src.core.vector_sim** - Batch/vectorized simulations

### Controllers
- **src.controllers.factory** - Controller factory and registry
- **src.controllers.classic_smc** - Classical sliding mode control
- **src.controllers.sta_smc** - Super-twisting algorithm
- **src.controllers.adaptive_smc** - Adaptive sliding mode control
- **src.controllers.hybrid_adaptive_sta_smc** - Hybrid adaptive STA-SMC

### Optimization Modules
- **src.optimization.algorithms.pso_optimizer** - PSO tuning algorithms
- **src.optimizer.cost_functions** - Cost function definitions

### MT-6 Analysis Scripts
- **mt6_statistical_comparison** - Welch t-tests and effect size calculations for MT-6 metrics
- **mt6_visualize_pso_convergence** - Publication-ready PSO convergence plots
- **mt6_visualize_performance_comparison_simple** - Summary-based performance comparisons
- **mt6_generate_report** - Markdown report generation pipeline for MT-6
- **optimize_adaptive_boundary** - PSO driver for adaptive boundary-layer tuning

### Configuration Modules
- **src.config.loader** - Configuration loading and validation
- **src.config.schemas** - Pydantic configuration schemas

### Hardware-in-the-Loop
- **src.hil.plant_server** - Plant simulation server
- **src.hil.controller_client** - Controller client interface

---

## External Links

- **[Main Documentation Hub](../index.md)** - Complete project documentation
- **[User Guides](../guides/index.md)** - Tutorials and how-to guides
- **[Mathematical Foundations](../mathematical_foundations/index.md)** - Control theory proofs
- **[Controller Factory](../factory/README.md)** - Factory system comprehensive guide

---

**Last Updated**: 2025-10-10
**API Documentation Status**: Complete (16 files, all accessible via toctree navigation)
**Auto-Generated Docs**: Sphinx autodoc integration active

---

**Quick Links:**
- Controller API: [controller_api_reference.md](controller_api_reference.md)
- Factory System: [factory_system_api_reference.md](factory_system_api_reference.md)
- PSO Optimization: [optimization_module_api_reference.md](optimization_module_api_reference.md)
---

**Navigation**: Return to [Master Navigation Hub](../NAVIGATION.md) | Browse all [Documentation Categories](../index.md)
