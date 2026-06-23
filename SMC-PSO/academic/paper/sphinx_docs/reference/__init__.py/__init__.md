# __init__

**Source:** `src\__init__.py`

## Module Overview

Expose the top‑level ``src`` package and provide convenient access
to its submodules.

This module exists to ensure that the ``src`` directory is treated as
a proper Python package during test collection.  Without an
``__init__.py`` file, pytest may fail to locate attributes such as
``src.config`` when performing monkeypatching.

In addition to making the package importable, we deliberately expose
the ``config`` submodule as an attribute on the package.  Some tests
refer to ``src.config`` directly when patching configuration loaders
via ``monkeypatch.setattr``.  Importing the submodule here ensures
that ``src.config`` resolves to the actual configuration module,
rather than raising ``AttributeError: module 'src' has no attribute
'config'`` during test execution.

We avoid importing any other submodules by default to prevent
side effects or unnecessary dependencies from being loaded at
package import time.  Users should import submodules explicitly as
needed.

## Complete Source Code

```{literalinclude} ../../../src/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from importlib import import_module`
- `import warnings`
