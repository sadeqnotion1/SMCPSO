# optimization.algorithms.__init__

**Source:** `src\optimization\algorithms\__init__.py`

## Module Overview

Professional optimization algorithms for control engineering applications.

## Complete Source Code

```{literalinclude} ../../../src/optimization/algorithms/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .swarm.pso import ParticleSwarmOptimizer`
- `from .pso_optimizer import PSOTuner`
- `from .evolutionary.genetic import GeneticAlgorithm, GeneticAlgorithmConfig`
- `from .evolutionary.differential import DifferentialEvolution`
- `from .gradient_based.nelder_mead import NelderMead, NelderMeadConfig`
- `from .gradient_based.bfgs import BFGSOptimizer, BFGSConfig`
