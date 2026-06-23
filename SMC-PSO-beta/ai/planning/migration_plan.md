# Migration Plan: SMC-PSO to SMC-PSO-beta
[AI] Generated with AI assistance

This document outlines the step-by-step, file-by-file migration plan from the stable repository (SMC-PSO) to the beta repository (SMC-PSO-beta).

## 1. Migration Goals & Strategy
The migration will follow a dependency-first approach. We will migrate infrastructure, configuration, and models before transferring controllers and optimization routines. This ensures that each component can be tested and verified incrementally in the beta environment.

## 2. Order of Migration

### Phase 1: Environment & Configuration [INFO]
These files form the foundation of the execution environment and configuration parsing.
- [x] requirements.txt -- Dependency definitions [DONE]
- [x] setup.py -- Package structure [DONE]
- [x] config.yaml -- Default parameters [DONE]
- [x] src/config/ -- Pydantic schema and loading engine [DONE]

### Phase 2: Plant Dynamics (Physics Model) [INFO]
The plant models simulate the Double-Inverted Pendulum (DIP) dynamics and have no external project dependencies.
- [ ] src/plant/ -- Base interface, full nonlinear model, simplified model, and low-rank variants

### Phase 3: Utility & Math Primitives [INFO]
Base math functions, types, and monitoring utilities needed by simulation and control loops.
- [ ] src/utils/ -- Typing definitions, validation logic, logging, and metrics

### Phase 4: Controllers Base & Simulation Core [INFO]
Base classes for controllers and the context engines that orchestrate simulation runs.
- [ ] src/controllers/base.py -- Base controller interface
- [ ] src/simulation/ -- Integrators, simulation context, orchestrator

### Phase 5: Controller Implementations [INFO]
Specific sliding mode control variants.
- [ ] src/controllers/classical_smc.py
- [ ] src/controllers/sta_smc.py (Super-Twisting Algorithm)
- [ ] src/controllers/adaptive_smc.py
- [ ] src/controllers/hybrid_adaptive_sta_smc.py
- [ ] src/controllers/factory.py -- Controller factory registration

### Phase 6: Optimization Framework [INFO]
PSO optimization algorithms and objectives.
- [ ] src/optimization/ -- Tuning algorithms (PSO, etc.) and fitness functions

### Phase 7: Simulation Entrypoints & Visualization [INFO]
CLI and UI entry points.
- [ ] simulate.py -- Main CLI script
- [ ] streamlit_app.py -- Web UI dashboard

### Phase 8: Verification & Tests [INFO]
Unit tests, integration tests, and benchmarks.
- [ ] tests/ -- Test suite and verification gates

## 3. Migration Action Checklists
For each file migrated:
1. Copy the file/directory from SMC-PSO to the corresponding path in SMC-PSO-beta.
2. Run standard syntax checks and linting.
3. Validate imports (adjusting relative imports if package structures shift).
4. Mark the task as [DONE] in this checklist.
