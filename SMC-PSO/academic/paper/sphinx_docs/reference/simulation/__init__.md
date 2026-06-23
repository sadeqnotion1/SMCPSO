# simulation.__init__

**Source:** `src\simulation\__init__.py`

## Module Overview Professional

simulation framework for control engineering applications

. This module provides a simulation framework with:


- Multiple execution strategies (sequential, batch, parallel, real-time)
- Advanced numerical integration methods (adaptive and fixed-step)
- safety monitoring and constraint enforcement
- Professional result processing and analysis
- Extensible architecture for research and production use For backward compatibility, legacy interfaces are maintained. ## Complete Source Code ```{literalinclude} ../../../src/simulation/__init__.py
:language: python
:linenos:
```

---

## Functions

### `create_simulation_engine(engine_type, config_path)`

Create a simulation engine of specified type. Parameters
----------
engine_type : str, optional Type of engine: 'sequential', 'batch', 'parallel', 'real_time'
config_path : str, optional Path to configuration file Returns
-------
SimulationEngine Configured simulation engine #### Source Code ```{literalinclude} ../../../src/simulation/__init__.py
:language: python
:pyobject: create_simulation_engine
:linenos:
```

---

## `run_monte_carlo_analysis(simulation_fn, n_samples)`

Run Monte Carlo analysis on simulation function. Parameters

simulation_fn : callable Simulation function to analyze
n_samples : int, optional Number of Monte Carlo samples
**kwargs Additional parameters for analysis Returns
-------
dict Monte Carlo analysis results #### Source Code ```{literalinclude} ../../../src/simulation/__init__.py
:language: python
:pyobject: run_monte_carlo_analysis
:linenos:
```

---

## Dependencies This module imports: - `from .core import SimulationEngine, Integrator, Orchestrator, SimulationStrategy, SafetyGuard, ResultContainer, SimulationContext, StateSpaceUtilities, TimeManager`
- `from .orchestrators import SequentialOrchestrator, BatchOrchestrator, ParallelOrchestrator, RealTimeOrchestrator`
- `from .integrators import ForwardEuler, RungeKutta4, DormandPrince45, ZeroOrderHold`
- `from .safety import apply_safety_guards, SafetyViolationError, SafetyMonitor, PerformanceMonitor`
- `from .results import StandardResultContainer, BatchResultContainer, ResultProcessor`
- `from .strategies import MonteCarloStrategy`
- `from .orchestrators.sequential import get_step_fn, step, run_simulation`
- `from .core.simulation_context import SimulationContext`
- `from .orchestrators.batch import simulate_batch as simulate`
- `from .integrators.adaptive.runge_kutta import rk45_step` *... and 1 more*
