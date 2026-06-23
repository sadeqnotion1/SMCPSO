# PSO Optimization Documentation (Legacy)

This section covers the Particle Swarm Optimization implementation used for automatic controller tuning.

## Topics

```{toctree}
:maxdepth: 2

pso_core_algorithm_guide
```

**Note**: This page has moved. For complete PSO documentation see:
- [PSO Optimization Module API Reference](../api/optimization_module_api_reference.md)
- [Reference → Optimizer](../reference/optimizer/index.md)
- [Mathematical Foundations → PSO Theory](../mathematical_foundations/pso_algorithm_theory.md)

## Overview

The PSO optimization system automatically tunes controller parameters to minimize:

- Settling time and overshoot
- Control effort and chattering
- Robustness to uncertainties
- Lyapunov stability margins

The system uses PySwarms with custom cost functions tailored for control systems performance.
