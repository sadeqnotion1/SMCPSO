# benchmarks.core.trial_runner

**Source:** `src\benchmarks\core\trial_runner.py`

## Module Overview

Core trial execution engine for statistical benchmarking.

This module implements the trial execution logic for running multiple
independent simulations of control systems. It handles:
- Batch simulation execution
- Randomization and seeding
- Error handling and fallbacks
- Trial orchestration and coordination

The Central Limit Theorem implies that for skewed distributions, a sample
size of at least 25–30 trials is required for the sample mean to approximate
a normal distribution. By default, 30 trials are executed.

## Complete Source Code

```{literalinclude} ../../../src/benchmarks/core/trial_runner.py
:language: python
:linenos:
```



## Functions

### `execute_single_trial(controller_factory, trial_seed, sim_duration, sim_dt, max_force, noise_std)`

Execute a single simulation trial with the given parameters.

Parameters
----------
controller_factory : Callable
    Factory function that creates controller instances
trial_seed : int
    Random seed for this specific trial
sim_duration : float
    Simulation duration in seconds
sim_dt : float, optional
    Simulation time step. If None, use default from simulator
max_force : float
    Maximum control force magnitude
noise_std : float, optional
    Standard deviation of measurement noise

Returns
-------
dict
    Performance metrics for this trial

Raises
------
RuntimeError
    If simulation fails and no fallback succeeds

#### Source Code

```{literalinclude} ../../../src/benchmarks/core/trial_runner.py
:language: python
:pyobject: execute_single_trial
:linenos:
```



### `run_multiple_trials(controller_factory, cfg, n_trials, seed, randomise_physics, noise_std, progress_callback)`

Execute multiple independent simulation trials.

This function runs n_trials independent simulations and collects
performance metrics from each trial. Each trial uses a different
random seed to ensure statistical independence.

Parameters
----------
controller_factory : Callable[[np.ndarray], Any]
    Factory function that returns controller instances when provided
    with gain vectors. Must have 'n_gains' attribute.
cfg : Any
    Configuration object with 'simulation.duration' and optionally
    'simulation.dt' attributes
n_trials : int, optional
    Number of independent trials to execute. Default is 30.
seed : int, optional
    Base random seed for trial generation
randomise_physics : bool, optional
    Whether to randomize physical parameters (reserved for future use)
noise_std : float, optional
    Standard deviation of measurement noise
progress_callback : callable, optional
    Callback function called with (current_trial, total_trials)

Returns
-------
list of dict
    List containing metrics dictionary for each trial

Notes
-----
The randomise_physics parameter is included for future extensibility
but is not currently implemented. It would allow testing controller
robustness against parameter uncertainties.

#### Source Code

```{literalinclude} ../../../src/benchmarks/core/trial_runner.py
:language: python
:pyobject: run_multiple_trials
:linenos:
```



### `validate_trial_configuration(controller_factory, cfg, n_trials)`

Validate configuration before starting trial execution.

Parameters
----------
controller_factory : Callable
    Controller factory to validate
cfg : Any
    Configuration object to validate
n_trials : int
    Number of trials to validate

Raises
------
ValueError
    If configuration is invalid

#### Source Code

```{literalinclude} ../../../src/benchmarks/core/trial_runner.py
:language: python
:pyobject: validate_trial_configuration
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Callable, Any, List, Dict, Tuple, Optional`
- `import numpy as np`
- `from src.core.vector_sim import simulate_system_batch`
- `from ..metrics import compute_basic_metrics`
