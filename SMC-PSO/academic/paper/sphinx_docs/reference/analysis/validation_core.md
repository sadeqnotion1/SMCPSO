# analysis.validation.core

**Source:** `src\analysis\validation\core.py`

## Module Overview

Core validation and trial execution utilities.

This module provides the core infrastructure for running validation trials,
managing experimental configurations, and coordinating statistical benchmarks.

## Complete Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:linenos:
```



## Classes

### `TrialConfiguration`

Configuration for validation trials.

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: TrialConfiguration
:linenos:
```

#### Methods (2)

##### `__init__(self, name, parameters, repetitions, timeout, parallel, random_seed)`

Initialize trial configuration.

[View full source →](#method-trialconfiguration-__init__)

##### `__repr__(self)`

[View full source →](#method-trialconfiguration-__repr__)



### `TrialResult`

Result from a single trial execution.

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: TrialResult
:linenos:
```

#### Methods (2)

##### `__init__(self, trial_id, success, metrics, execution_time, error_message)`

Initialize trial result.

[View full source →](#method-trialresult-__init__)

##### `__repr__(self)`

[View full source →](#method-trialresult-__repr__)



### `TrialBatch`

Collection of trial results with analysis methods.

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: TrialBatch
:linenos:
```

#### Methods (7)

##### `__init__(self, configuration, results)`

Initialize trial batch.

[View full source →](#method-trialbatch-__init__)

##### `success_rate(self)`

Get success rate for this batch.

[View full source →](#method-trialbatch-success_rate)

##### `successful_results(self)`

Get only successful results.

[View full source →](#method-trialbatch-successful_results)

##### `failed_results(self)`

Get only failed results.

[View full source →](#method-trialbatch-failed_results)

##### `get_metric_values(self, metric_name)`

Get all values for a specific metric from successful trials.

[View full source →](#method-trialbatch-get_metric_values)

##### `get_summary_statistics(self, metric_name)`

Get summary statistics for a metric.

[View full source →](#method-trialbatch-get_summary_statistics)

##### `__repr__(self)`

[View full source →](#method-trialbatch-__repr__)



## Functions

### `validate_trial_configuration(config)`

Validate trial configuration for common issues.

Args:
    config: Configuration to validate

Returns:
    List of validation error messages (empty if valid)

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: validate_trial_configuration
:linenos:
```



### `run_single_trial(trial_function, trial_id, parameters, timeout, random_seed)`

Run a single trial with error handling and timing.

Args:
    trial_function: Function to execute for this trial
    trial_id: Unique identifier for this trial
    parameters: Parameters to pass to trial function
    timeout: Optional timeout for execution
    random_seed: Optional random seed

Returns:
    TrialResult with execution results

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: run_single_trial
:linenos:
```



### `run_multiple_trials(trial_function, configuration, progress_callback)`

Run multiple trials according to configuration.

Args:
    trial_function: Function to execute for each trial
    configuration: Trial configuration
    progress_callback: Optional callback for progress updates

Returns:
    TrialBatch containing all results

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: run_multiple_trials
:linenos:
```



### `compare_trial_batches(batch1, batch2, metric_name)`

Compare two trial batches for a specific metric.

Args:
    batch1: First batch of trials
    batch2: Second batch of trials
    metric_name: Name of metric to compare

Returns:
    Dictionary containing comparison statistics

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: compare_trial_batches
:linenos:
```



### `create_standard_trial_configurations()`

Create standard trial configurations for common validation scenarios.

Returns:
    List of standard trial configurations

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: create_standard_trial_configurations
:linenos:
```



### `mock_trial_function()`

Mock trial function for testing validation infrastructure.

Args:
    **parameters: Trial parameters

Returns:
    Dictionary of mock metrics

#### Source Code

```{literalinclude} ../../../src/analysis/validation/core.py
:language: python
:pyobject: mock_trial_function
:linenos:
```



## Dependencies

This module imports:

- `from typing import Dict, List, Any, Optional, Callable, Union, Tuple`
- `import numpy as np`
- `import time`
- `import logging`
- `import warnings`
- `from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor`
- `from functools import partial`
