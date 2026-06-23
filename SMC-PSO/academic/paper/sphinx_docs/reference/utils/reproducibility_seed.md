# utils.reproducibility.seed

**Source:** `src\utils\reproducibility\seed.py`

## Module Overview

Global seeding utilities for reproducible simulations.

This module centralises the handling of pseudo‑random number generators used
throughout the project.  Reproducibility is a cornerstone of computational
experiments; when models include stochastic elements, the random seeds used
must be recorded and shared so that results can be replicated on different
machines and numbers of processors【675644021986605†L385-L388】.  Failing to set
a consistent seed can lead to subtle nondeterministic behaviour when code
implicitly calls Python’s ``random`` module or NumPy’s global generator.

The ``set_global_seed`` function below initializes both Python’s built‑in
``random`` module and NumPy’s global random number generator with the same
integer seed.  If additional pseudo‑random number generators (PRNGs) are
introduced (e.g., in Numba kernels), this function can be extended to
configure them as well.

Usage
-----
Call ``set_global_seed(seed)`` once at the start of your program or in
``load_config`` to ensure that all subsequent stochastic operations
produce deterministic results.  Note that individual components of the
project, such as the PSO tuner, may still instantiate their own local
``numpy.random.Generator`` instances for thread safety; those generators
should be seeded explicitly using the same or a derived seed.

## Complete Source Code

```{literalinclude} ../../../src/utils/reproducibility/seed.py
:language: python
:linenos:
```



## Classes

### `SeedManager`

Manage deterministic seed generation for reproducibility.

A ``SeedManager`` creates a master :class:`numpy.random.Generator`
initialised with a given seed.  Each call to :meth:`spawn` returns
a fresh 32‑bit integer seed that can be used to initialise
independent RNGs in other modules.  All generated seeds are stored
in the ``history`` attribute for logging and provenance.

Parameters
----------
master_seed : int
    Seed used to initialise the internal generator.  If ``None`` the
    generator is seeded nondeterministically.

Examples
--------
>>> mgr = SeedManager(42)
>>> rng = np.random.default_rng(mgr.spawn())

#### Source Code

```{literalinclude} ../../../src/utils/reproducibility/seed.py
:language: python
:pyobject: SeedManager
:linenos:
```

#### Methods (2)

##### `__init__(self, master_seed)`

[View full source →](#method-seedmanager-__init__)

##### `spawn(self)`

Return a new integer seed derived from the master generator.

[View full source →](#method-seedmanager-spawn)



## Functions

### `set_global_seed(seed)`

Seed Python and NumPy global PRNGs for reproducibility.

Parameters
----------
seed : int or None
    The integer seed to use.  If ``None``, no seeding is performed.

Notes
-----
A simulation or optimisation routine that relies on random numbers
should be seeded to ensure that repeated runs yield identical
trajectories and results.  According to reproducibility guidelines in
computational science, when random number generation is part of a
model, the seeds form part of the model description and must be
recorded and shared to allow replicability【675644021986605†L385-L388】.

Examples
--------
>>> from src.utils.seed import set_global_seed
>>> set_global_seed(123)
>>> import random
>>> import numpy as np
>>> random.random(), np.random.rand()
(0.052363598850944326, 0.6964691855978616)

Calling ``set_global_seed`` again with the same seed resets both
generators to their initial state:

>>> set_global_seed(123)
>>> random.random(), np.random.rand()
(0.052363598850944326, 0.6964691855978616)

#### Source Code

```{literalinclude} ../../../src/utils/reproducibility/seed.py
:language: python
:pyobject: set_global_seed
:linenos:
```



### `create_rng(seed)`

Create a local NumPy random number generator.

Parameters
----------
seed : int or None, optional
    Seed for the generator.  If None, NumPy will choose a random
    seed.  Passing an integer ensures deterministic behaviour of
    subsequent random draws.

Returns
-------
numpy.random.Generator
    A new random number generator instance seeded with ``seed``.

Notes
-----
Creating local PRNGs instead of seeding the global RNG allows
different components to use independent random streams without
interfering with each other.  This is particularly important when
running concurrent simulations or optimisation algorithms【675644021986605†L385-L388】.

#### Source Code

```{literalinclude} ../../../src/utils/reproducibility/seed.py
:language: python
:pyobject: create_rng
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import random`
- `import numpy as np`
- `from typing import Optional`


## Architecture Diagram

```{mermaid}
graph TD
    A[Component] --> B[Subcomponent 1]
    A --> C[Subcomponent 2]
    B --> D[Output]
    C --> D

    style A fill:#e1f5ff
    style D fill:#e8f5e9
```


## Usage Examples

### Example 1: Basic Usage

```python
# Basic usage example
from src.utils import Component

component = Component()
result = component.process(data)
```

## Example 2: Advanced Configuration

```python
# Advanced configuration
component = Component(
    option1=value1,
    option2=value2
)
```

## Example 3: Integration with Framework

```python
# Integration example
from src.simulation import SimulationRunner

runner = SimulationRunner()
runner.use_component(component)
```

## Example 4: Performance Optimization

```python
# Performance-optimized usage
component = Component(enable_caching=True)
```

## Example 5: Error Handling

```python
# Error handling
try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
```
