# config.logging

**Source:** `src\config\logging.py`

## Module Overview

Centralised logging configuration with provenance stamping.

This module configures the root logger to record run provenance in every
log message.  Provenance fields include the short Git commit SHA of
the working directory, a hash of the configuration dictionary and the
master random seed.  The logger is configured using a filter that
adds these fields to each ``LogRecord`` and a format string that
prefixes messages with ``[commit|cfg_hash|seed=<seed>]``.  By
including such metadata in logs, researchers can unambiguously trace
results back to the precise code and configuration that generated
them, satisfying reproducibility guidelines【985132039892507†L364-L377】.

The design of this module is inspired by best practices for
reproducible computational research.  Sandve et al. (2013) emphasise
that analyses involving randomness must record the underlying random
seed so that results can be replicated exactly【985132039892507†L364-L377】.
Similarly, tagging logs with the commit SHA and configuration hash
allows others to verify that they are running the same code base and
parameters.  Logging provenance promotes transparency and fosters
confidence in published results.

## Complete Source Code

```{literalinclude} ../../../src/config/logging.py
:language: python
:linenos:
```



## Classes

### `ProvenanceFilter`

**Inherits from:** `logging.Filter`

Inject commit, configuration hash and seed into log records.

Parameters
commit_sha : str
    Short Git commit SHA (or "unknown" if unavailable).
config_hash : str
    Truncated SHA‑256 hash of the configuration dictionary.
seed : int
    Master random seed recorded in logs.

#### Source Code

```{literalinclude} ../../../src/config/logging.py
:language: python
:pyobject: ProvenanceFilter
:linenos:
```

#### Methods (2)

##### `__init__(self, commit_sha, config_hash, seed)`

[View full source →](#method-provenancefilter-__init__)

##### `filter(self, record)`

[View full source →](#method-provenancefilter-filter)



## Functions

### `_compute_config_hash(config)`

Compute a truncated SHA‑256 hash of a configuration dictionary.

When PyYAML is available the configuration is serialised via
``yaml.safe_dump`` to obtain a canonical representation.  When
unavailable, ``repr`` is used as a fallback.  The full SHA‑256
digest is computed and truncated to the first eight hexadecimal
characters to produce a compact identifier.  Hashing the
configuration ensures that even small changes in parameter values
produce different identifiers, facilitating provenance tracking.

#### Source Code

```{literalinclude} ../../../src/config/logging.py
:language: python
:pyobject: _compute_config_hash
:linenos:
```



### `_get_git_commit()`

Return the short Git commit SHA of the current working tree.

If the repository is not under version control or Git is not
installed, return "unknown".  The commit SHA is determined by
invoking ``git rev-parse --short HEAD`` via subprocess.  Any
exceptions are caught and masked to preserve robustness.

#### Source Code

```{literalinclude} ../../../src/config/logging.py
:language: python
:pyobject: _get_git_commit
:linenos:
```



### `configure_provenance_logging(config, seed)`

Configure the root logger with provenance stamping.

This helper sets up logging such that each log record includes
provenance metadata.  It should be called once near the start of
an application, before any logging calls are made.  Subsequent
calls will reconfigure the root logger and may override previous
handlers.

Parameters
----------
config : dict
    The configuration dictionary to hash.  Nested structures are
    supported.  Passing ``None`` results in a constant hash.
seed : int
    The master random seed to record.  According to reproducibility
    guidelines, this value should be stored in logs so that
    stochastic runs can be reproduced exactly【985132039892507†L364-L377】.
level : int, optional
    Logging level for the root logger.  Defaults to ``logging.INFO``.

#### Source Code

```{literalinclude} ../../../src/config/logging.py
:language: python
:pyobject: configure_provenance_logging
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import hashlib`
- `import logging`
- `import os`
- `import subprocess`
- `from typing import Any, Dict`
