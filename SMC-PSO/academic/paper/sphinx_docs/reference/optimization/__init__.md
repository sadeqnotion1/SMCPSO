# optimization.__init__

**Source:** `src\optimization\__init__.py`

## Module Overview Professional

optimization framework for control engineering applications

. This module provides a optimization framework featuring:


- Multiple optimization (see references) algorithms (PSO, DE, GA, CMA-ES, Bayesian)
- Professional objective functions for control performance metrics
- Advanced convergence monitoring and analysis
- result visualization and comparison tools
- Extensible architecture for research and production use For backward compatibility, legacy interfaces are maintained. ## Complete Source Code ```{literalinclude} ../../../src/optimization/__init__.py
:language: python
:linenos:
```

---

## Functions

### `create_optimizer(algorithm, parameter_space)`

Create an optimizer of specified type. Parameters
----------
algorithm : str Algorithm name ('pso', 'de', 'ga', 'cma_es', 'bayesian', 'nelder_mead')
parameter_space : ParameterSpace Parameter space to optimize over
**kwargs Algorithm-specific parameters Returns
-------
Optimizer Configured optimizer instance Examples
--------
>>> import numpy as np
>>> from src.optimization import create_optimizer, ContinuousParameterSpace
>>>
>>> # Define parameter space
>>> bounds = ContinuousParameterSpace(
... lower_bounds=np.array([0.1, 0.1, 0.1]),
... upper_bounds=np.array([10.0, 10.0, 10.0]),
... names=['kp', 'ki', 'kd']
... )
>>>
>>> # Create PSO optimizer
>>> optimizer = create_optimizer('pso', bounds, population_size=50) #### Source Code ```{literalinclude} ../../../src/optimization/__init__.py
:language: python
:pyobject: create_optimizer
:linenos:
```

---

## `create_control_problem(objective_type, controller_factory, simulation_config, parameter_bounds)`

Create a control optimization problem. Parameters

objective_type : str Type of objective ('tracking', 'energy', 'settling_time', 'overshoot')
controller_factory : callable Function to create controller from parameters
simulation_config : dict Simulation configuration
parameter_bounds : tuple (lower_bounds, upper_bounds) arrays
**kwargs Objective-specific parameters Returns
-------
ControlOptimizationProblem Configured optimization problem Examples
--------
>>> def controller_factory(params):
... return PIDController(kp=params[0], ki=params[1], kd=params[2])
>>>
>>> problem = create_control_problem(
... 'tracking',
... controller_factory,
... {'sim_time': 10.0, 'dt': 0.01},
... (np.array([0.1, 0.1, 0.1]), np.array([10.0, 10.0, 10.0])),
... reference_trajectory=reference_signal
... ) #### Source Code ```{literalinclude} ../../../src/optimization/__init__.py
:language: python
:pyobject: create_control_problem
:linenos:
```

---

### `run_optimization_study(problems, algorithms, n_runs, parallel)`

Run optimization study comparing multiple algorithms. Parameters
----------
problems : list List of optimization problems
algorithms : list List of algorithm names or configured optimizers
n_runs : int, optional Number of independent runs per algorithm
parallel : bool, optional Whether to run in parallel
**kwargs Additional options Returns
-------
dict study results with statistical analysis Examples
--------
>>> problems = [problem1, problem2]
>>> algorithms = ['pso', 'de', 'ga']
>>> results = run_optimization_study(problems, algorithms, n_runs=30)
>>>
>>> # Results contain statistical analysis, convergence curves, etc.
>>> print(results['summary']) #### Source Code ```{literalinclude} ../../../src/optimization/__init__.py
:language: python
:pyobject: run_optimization_study
:linenos:
```

---

### `example_pid_tuning()`

Example: PID controller tuning using PSO. This example demonstrates how to optimize PID controller parameters

for a tracking objective using the new framework. #### Source Code ```{literalinclude} ../../../src/optimization/__init__.py
:language: python
:pyobject: example_pid_tuning
:linenos:
```

### `example_algorithm_comparison()`

Example: Compare multiple optimization algorithms. This example shows how to compare PSO, DE, and GA algorithms
on the same control optimization problem. #### Source Code ```{literalinclude} ../../../src/optimization/__init__.py
:language: python
:pyobject: example_algorithm_comparison
:linenos:
```

---

## Dependencies This module imports: - `from .core import Optimizer, ObjectiveFunction, Constraint, OptimizationProblem, OptimizationResult, ParameterSpace, ConvergenceMonitor, OptimizationProblemBuilder, ControlOptimizationProblem, ContinuousParameter, DiscreteParameter, ContinuousParameterSpace, OptimizationContext, optimize`

- `from .algorithms import ParticleSwarmOptimizer, DifferentialEvolution, GeneticAlgorithm, NelderMead, BFGSOptimizer`
- `from .objectives import TrackingErrorObjective, EnergyConsumptionObjective, StabilityMarginObjective, RobustnessObjective, SettlingTimeObjective, OvershootObjective, SteadyStateErrorObjective, WeightedSumObjective, ParetoObjective, SimulationBasedObjective, AnalyticalObjective, CompositeObjective`
- `from .algorithms.pso_optimizer import PSOTuner`
