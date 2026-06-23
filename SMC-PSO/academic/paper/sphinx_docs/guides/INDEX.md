# User Guides & Tutorials

**Complete learning resources for the DIP SMC PSO Framework**

[BLUE] **Looking for something specific?** See the [Master Navigation Hub](../NAVIGATION.md) for complete documentation mapping across all 985 files and 11 navigation systems.

[GREEN] **Complete Beginner?** Start with [Path 0: Beginner Roadmap](../learning/beginner-roadmap.md) (125-175 hours) - Takes you from ZERO coding/control theory background to running simulations confidently. **NOW COMPLETE** with all 5 phases! [OK]

This is your central navigation hub for all user guides, tutorials, and learning resources. Whether you're a beginner taking your first steps or an experienced researcher implementing novel controllers, you'll find the right resources here.

---

## Overview

The guides are organized into six main categories:

- **[Getting Started](#getting-started)** - Installation, setup, and first simulations
- **[Tutorials](#tutorials)** - Step-by-step learning with hands-on examples (5 tutorials, 10.5 hours)
- **[How-To Guides](#how-to-guides)** - Task-oriented recipes for specific goals (4 guides)
- **[API Reference](#api-reference)** - Technical specifications and usage details (7 modules)
- **[Theory & Background](#theory--background)** - Mathematical foundations (4 theory guides)
- **[Workflows](#workflows)** - Complete end-to-end procedures (14 workflow documents)

**Total Documentation**: 12,525 lines across 43 documents

---

## Getting Started

Essential documentation for new users to install and configure the framework.

```{toctree}
:maxdepth: 2
:caption: Getting Started

getting-started
user-guide
QUICK_REFERENCE
README
interactive_configuration_guide
interactive_visualizations
```

**Start Here:**
- [Getting Started Guide](getting-started.md) - 15-minute installation and first simulation
- [User Guide](user-guide.md) - Comprehensive daily usage reference (826 lines, 30 min)
- [Quick Reference](QUICK_REFERENCE.md) - Command syntax cheat sheet (5 min)

**Recommended Start**: Getting Started Guide -> Tutorial 01 -> User Guide

---

## Tutorials

Step-by-step learning paths with hands-on examples and expected results.

```{toctree}
:maxdepth: 2
:caption: Tutorials

tutorials/tutorial-01-first-simulation
tutorials/tutorial-02-controller-comparison
tutorials/tutorial-03-pso-optimization
tutorials/tutorial-04-custom-controller
tutorials/tutorial-05-research-workflow
```

### Tutorial Series

| Tutorial | Level | Duration | Topics |
|----------|-------|----------|--------|
| [Tutorial 01: First Simulation](tutorials/tutorial-01-first-simulation.md) | Beginner | 45 min | DIP system, Classical SMC, result interpretation |
| [Tutorial 02: Controller Comparison](tutorials/tutorial-02-controller-comparison.md) | Intermediate | 60 min | 4 SMC types, performance tradeoffs, selection criteria |
| [Tutorial 03: PSO Optimization](tutorials/tutorial-03-pso-optimization.md) | Intermediate | 90 min | Automated gain tuning, convergence analysis, custom cost functions |
| [Tutorial 04: Custom Controller](tutorials/tutorial-04-custom-controller.md) | Advanced | 120 min | Terminal SMC from scratch, factory integration, testing |
| [Tutorial 05: Research Workflow](tutorials/tutorial-05-research-workflow.md) | Advanced | 120 min | End-to-end research project, statistical analysis, publication workflow |

**Total**: 5 tutorials, 635 minutes (10.5 hours) of guided learning

---

## How-to Guides

Task-oriented recipes for accomplishing specific goals quickly.

```{toctree}
:maxdepth: 2
:caption: How-To Guides

how-to/running-simulations
how-to/result-analysis
how-to/optimization-workflows
how-to/testing-validation
```

| Guide | Topics | Duration |
|-------|--------|----------|
| [Running Simulations](how-to/running-simulations.md) | CLI usage, Streamlit dashboard, programmatic API, batch processing | 20 min |
| [Result Analysis](how-to/result-analysis.md) | Metrics interpretation, statistical analysis, visualization, data export | 20 min |
| [Optimization Workflows](how-to/optimization-workflows.md) | PSO tuning, custom cost functions, convergence diagnostics, parallel execution | 25 min |
| [Testing & Validation](how-to/testing-validation.md) | Test suite overview, unit testing, performance benchmarking, coverage analysis | 20 min |

**Total**: 4 guides, practical approaches for common tasks

---

## API Reference

Technical specifications for programmatic usage of the framework.

```{toctree}
:maxdepth: 2
:caption: API Reference

api/README
api/controllers
api/simulation
api/optimization
api/configuration
api/plant-models
api/utilities
```

### API Modules

| Module | Description | Key Classes | Lines | Duration |
|--------|-------------|-------------|-------|----------|
| [API Index](api/README.md) | Overview and navigation | - | 203 | 10 min |
| [Controllers API](api/controllers.md) | Factory system, SMC types, gain bounds, custom controllers | `create_controller()`, `SMCType` | 726 | 30 min |
| [Simulation API](api/simulation.md) | SimulationRunner, dynamics models, batch processing, performance | `SimulationRunner`, `DynamicsModel` | 517 | 25 min |
| [Optimization API](api/optimization.md) | PSOTuner, cost functions, gain bounds, convergence monitoring | `PSOTuner`, `CostFunction` | 543 | 25 min |
| [Configuration API](api/configuration.md) | YAML loading, validation, programmatic configuration | `load_config()`, `ConfigSchema` | 438 | 20 min |
| [Plant Models API](api/plant-models.md) | Physics models, parameter configuration, custom dynamics | `SimplifiedDynamics`, `FullDynamics` | 424 | 20 min |
| [Utilities API](api/utilities.md) | Validation, control primitives, monitoring, analysis tools | `validate_params()`, `saturation()` | 434 | 20 min |

**Total**: 7 API guides, 3,285 lines of technical documentation

---

## Theory & Background

Mathematical foundations and conceptual explanations for the control strategies.

```{toctree}
:maxdepth: 2
:caption: Theory & Background

theory/README
theory/smc-theory
theory/pso-theory
theory/dip-dynamics
```

| Theory Guide | Topics | Lines | Duration |
|--------------|--------|-------|----------|
| [Theory Index](theory/README.md) | Overview and navigation | 104 | 5 min |
| [SMC Theory](theory/smc-theory.md) | Lyapunov stability, chattering analysis, super-twisting mathematics, practical design | 619 | 30 min |
| [PSO Theory](theory/pso-theory.md) | Swarm intelligence principles, convergence theory, parameter selection, benchmarks | 438 | 25 min |
| [DIP Dynamics](theory/dip-dynamics.md) | Lagrangian derivation, equations of motion, linearization, controllability analysis | 501 | 25 min |

**Total**: 4 theory guides, 1,662 lines explaining the "why" behind the code

---

## Workflows

Complete end-to-end procedures for common research and operational tasks.

### General Workflows

```{toctree}
:maxdepth: 2
:caption: General Workflows

workflows/pso-optimization-workflow
workflows/batch-simulation-workflow
workflows/monte-carlo-validation-quickstart
workflows/custom-cost-functions
workflows/pso-vs-grid-search
```

### PSO Optimization Workflows

Controller-specific PSO tuning procedures with optimal parameter bounds.

```{toctree}
:maxdepth: 1
:caption: PSO Controller Workflows

workflows/pso-adaptive-smc
workflows/pso-hybrid-smc
workflows/pso-sta-smc
```

### Hardware-in-the-loop (hil) Workflows

Real-time simulation and hardware integration procedures.

```{toctree}
:maxdepth: 1
:caption: HIL Workflows

workflows/hil-workflow
workflows/hil-production-checklist
workflows/hil-safety-validation
workflows/hil-multi-machine
workflows/hil-disaster-recovery
workflows/pso-hil-tuning
```

---

## Learning Paths

### Path 1: Quick Start (1-2 Hours)
**Perfect for**: First-time users, rapid prototyping, initial exploration

```bash
Getting Started -> Tutorial 01 -> How-To: Running Simulations
```

**Outcome**: Run simulations, modify parameters, interpret basic results

---

### Path 2: Controller Expert (4-6 Hours)
**Perfect for**: Control systems researchers, comparative studies, selecting optimal controller

```bash
Getting Started -> Tutorial 01 -> Tutorial 02 -> Tutorial 03 -> SMC Theory -> How-To: Optimization Workflows
```

**Outcome**: Select best controller for your application, optimize gains, understand tradeoffs

---

### Path 3: Custom Development (8-12 Hours)
**Perfect for**: Implementing novel SMC algorithms, extending the framework

```bash
Getting Started -> Tutorials 01-02 -> Controllers API -> Tutorial 04 -> Tutorial 03 -> How-To: Testing & Validation -> SMC Theory
```

**Outcome**: Custom SMC ready for research, fully tested, integrated with PSO

---

### Path 4: Research Publication (12+ Hours)
**Perfect for**: Graduate students, academic researchers, industrial R&D

```bash
Complete Paths 1-2 -> Tutorial 05 -> How-To: Result Analysis -> PSO Theory -> DIP Dynamics -> User Guide (Batch Processing) -> All API Reference
```

**Outcome**: Publication-ready research with statistical validation, reproducible results

---

## Quick Search

### By Task

| I want to... | Go to |
|--------------|-------|
| **Install the framework** | [Getting Started](getting-started.md) |
| **Run my first simulation** | [Tutorial 01](tutorials/tutorial-01-first-simulation.md) |
| **Compare different controllers** | [Tutorial 02](tutorials/tutorial-02-controller-comparison.md) |
| **Optimize controller gains** | [Tutorial 03](tutorials/tutorial-03-pso-optimization.md) |
| **Create a custom controller** | [Tutorial 04](tutorials/tutorial-04-custom-controller.md) |
| **Understand SMC mathematics** | [SMC Theory](theory/smc-theory.md) |
| **Use the factory system** | [Controllers API](api/controllers.md) |
| **Configure PSO parameters** | [Optimization API](api/optimization.md) |
| **Interpret performance metrics** | [How-To: Result Analysis](how-to/result-analysis.md) |
| **Run batch simulations** | [User Guide - Batch Processing](user-guide.md#batch-processing) |

### By Component

| Component | Documentation |
|-----------|---------------|
| **Controllers** | [Controllers API](api/controllers.md), [Tutorial 02](tutorials/tutorial-02-controller-comparison.md) |
| **Plant Models** | [Plant Models API](api/plant-models.md), [DIP Dynamics Theory](theory/dip-dynamics.md) |
| **PSO Optimization** | [Optimization API](api/optimization.md), [Tutorial 03](tutorials/tutorial-03-pso-optimization.md) |
| **Simulation Engine** | [Simulation API](api/simulation.md), [How-To: Running Simulations](how-to/running-simulations.md) |
| **Configuration** | [Configuration API](api/configuration.md), [User Guide](user-guide.md) |

### By Skill Level

| Level | Start Here |
|-------|------------|
| **Beginner** | [Getting Started](getting-started.md) -> [Tutorial 01](tutorials/tutorial-01-first-simulation.md) |
| **Intermediate** | [Tutorial 02](tutorials/tutorial-02-controller-comparison.md) -> [Tutorial 03](tutorials/tutorial-03-pso-optimization.md) |
| **Advanced** | [Tutorial 04](tutorials/tutorial-04-custom-controller.md) -> [Theory Guides](theory/README.md) |

---

## Most Popular Pages

Based on user engagement and typical workflows:

1. **[Getting Started Guide](getting-started.md)** [STAR][STAR][STAR][STAR][STAR]
   - Entry point for 95% of users
   - Installation and first simulation
   - 523 lines, 15 minutes

2. **[Tutorial 01: First Simulation](tutorials/tutorial-01-first-simulation.md)** [STAR][STAR][STAR][STAR][STAR]
   - Hands-on introduction to DIP and Classical SMC
   - Expected results and troubleshooting
   - 600 lines, 45 minutes

3. **[Tutorial 03: PSO Optimization](tutorials/tutorial-03-pso-optimization.md)** [STAR][STAR][STAR][STAR]
   - Automated gain tuning is highly requested
   - Practical convergence analysis
   - 865 lines, 90 minutes

4. **[Controllers API](api/controllers.md)** [STAR][STAR][STAR][STAR]
   - Essential for programmatic usage
   - Factory patterns and gain bounds
   - 726 lines, 30 minutes

5. **[User Guide](user-guide.md)** [STAR][STAR][STAR][STAR]
   - Comprehensive reference
   - Daily usage workflows
   - 826 lines, 30 minutes

---

## External Links

- **[Main Documentation Hub](../index.md)** - Complete project documentation
- **[Mathematical Foundations](../mathematical_foundations/index.md)** - Rigorous control theory proofs
- **[Controller Factory Guide](../factory/README.md)** - Factory system and PSO integration
- **[Testing Documentation](../testing/index.md)** - Test suite and validation procedures
- **[Project Planning](../plans/index.md)** - Roadmaps and development plans

---

## Organization Principles

This documentation follows the **Diátaxis framework** for technical documentation:

1. **Tutorials** (Learning-oriented): Step-by-step lessons for beginners
2. **How-To Guides** (Task-oriented): Recipes for accomplishing specific goals
3. **API Reference** (Information-oriented): Technical specifications and details
4. **Theory & Explanation** (Understanding-oriented): Conceptual and mathematical foundations

**Benefits of this structure:**
- Clear separation of concerns
- Easy to find what you need
- Supports different learning styles
- Scales with project complexity

---

## Contributing to Documentation

Found an issue or want to improve the docs?

1. **Open an issue**: [GitHub Issues](https://github.com/theSadeQ/dip-smc-pso/issues)
2. **Suggest improvements**: Tag issues with `documentation`
3. **Follow the style guide**: Consistent formatting, clear examples, Mermaid diagrams

**Documentation Quality Standards:**
- All code examples must be tested and working
- Mermaid diagrams for visual explanations
- Cross-references between related documents
- Estimated reading times for planning
- Clear learning objectives

---

**Last Updated**: 2025-10-10 (Week 16)
**Documentation Status**: Complete (43 files, all accessible via toctree navigation)
**Total Documentation Size**: 12,525 lines across 43 documents

---

**Ready to Get Started?**
- New users: [Getting Started Guide](getting-started.md)
- Researchers: [Tutorial 02: Controller Comparison](tutorials/tutorial-02-controller-comparison.md)
- Developers: [API Reference](api/README.md)
