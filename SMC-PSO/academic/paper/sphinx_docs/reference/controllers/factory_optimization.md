# controllers.factory.optimization

**Source:** `src\controllers\factory\optimization.py`

## Module Overview

Factory Optimization Module for Enhanced Performance.

Provides optimizations for:
- Pre-compiled controller configurations
- Cached controller instances
- Lazy loading optimizations
- Reduced instantiation overhead

## Complete Source Code

```{literalinclude} ../../../src/controllers/factory/optimization.py
:language: python
:linenos:
```



## Classes

### `ControllerPreCompiler`

Pre-compile controller configurations for faster instantiation.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/optimization.py
:language: python
:pyobject: ControllerPreCompiler
:linenos:
```

#### Methods (4)

##### `__init__(self)`

[View full source →](#method-controllerprecompiler-__init__)

##### `get_optimized_config(self, controller_type, config_hash)`

Get pre-compiled controller configuration.

[View full source →](#method-controllerprecompiler-get_optimized_config)

##### `precompile_all(self)`

Pre-compile all controller configurations.

[View full source →](#method-controllerprecompiler-precompile_all)

##### `_precompile_default_config(self, controller_type)`

Pre-compile default configuration for a controller type.

[View full source →](#method-controllerprecompiler-_precompile_default_config)



### `ControllerInstanceCache`

Lightweight cache for controller instances with weak references.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/optimization.py
:language: python
:pyobject: ControllerInstanceCache
:linenos:
```

#### Methods (5)

##### `__init__(self, max_size)`

[View full source →](#method-controllerinstancecache-__init__)

##### `get_cached_instance(self, cache_key)`

Get cached controller instance if available.

[View full source →](#method-controllerinstancecache-get_cached_instance)

##### `cache_instance(self, cache_key, instance)`

Cache controller instance with weak reference.

[View full source →](#method-controllerinstancecache-cache_instance)

##### `_cleanup_old_entries(self)`

Remove oldest entries when cache is full.

[View full source →](#method-controllerinstancecache-_cleanup_old_entries)

##### `clear(self)`

Clear all cached instances.

[View full source →](#method-controllerinstancecache-clear)



### `FactoryOptimizer`

Main factory optimization coordinator.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/optimization.py
:language: python
:pyobject: FactoryOptimizer
:linenos:
```

#### Methods (9)

##### `__init__(self)`

[View full source →](#method-factoryoptimizer-__init__)

##### `optimize_instantiation(self, creation_func)`

Decorator to optimize controller instantiation.

[View full source →](#method-factoryoptimizer-optimize_instantiation)

##### `_generate_cache_key(self)`

Generate cache key for controller configuration.

[View full source →](#method-factoryoptimizer-_generate_cache_key)

##### `_update_performance_stats(self, instantiation_time_ms)`

Update performance statistics.

[View full source →](#method-factoryoptimizer-_update_performance_stats)

##### `get_performance_stats(self)`

Get performance optimization statistics.

[View full source →](#method-factoryoptimizer-get_performance_stats)

##### `enable_optimization(self)`

Enable factory optimizations.

[View full source →](#method-factoryoptimizer-enable_optimization)

##### `disable_optimization(self)`

Disable factory optimizations.

[View full source →](#method-factoryoptimizer-disable_optimization)

##### `clear_caches(self)`

Clear all caches.

[View full source →](#method-factoryoptimizer-clear_caches)

##### `precompile_configurations(self)`

Precompile all controller configurations.

[View full source →](#method-factoryoptimizer-precompile_configurations)



## Functions

### `get_factory_optimizer()`

Get the global factory optimizer instance.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/optimization.py
:language: python
:pyobject: get_factory_optimizer
:linenos:
```



### `optimize_controller_creation(func)`

Decorator to optimize controller creation functions.

#### Source Code

```{literalinclude} ../../../src/controllers/factory/optimization.py
:language: python
:pyobject: optimize_controller_creation
:linenos:
```



## Dependencies

This module imports:

- `import time`
- `import threading`
- `from typing import Dict, Any, Optional, Type, Callable`
- `from functools import lru_cache, wraps`
- `import weakref`
- `from ..smc.algorithms.classical.controller import ModularClassicalSMC`
- `from ..smc.algorithms.super_twisting.controller import ModularSuperTwistingSMC`
- `from ..smc.algorithms.adaptive.controller import ModularAdaptiveSMC`
- `from ..smc.algorithms.hybrid.controller import ModularHybridSMC`
