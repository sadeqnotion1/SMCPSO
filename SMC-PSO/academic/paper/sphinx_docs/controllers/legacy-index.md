# Control Systems Documentation (Legacy)

This section covers the various control strategies implemented for the double-inverted pendulum system.

## Controller Types

```{toctree}
:maxdepth: 2

classical_smc_technical_guide
sta_smc_technical_guide
adaptive_smc_technical_guide
hybrid_smc_technical_guide
```

Note: This page has moved. See Reference → Controllers.

## Overview

The DIP_SMC_PSO project implements multiple advanced sliding mode control strategies:

- **Classical SMC**: Traditional sliding mode with boundary layer
- **Super-Twisting SMC**: Higher-order sliding mode for chattering reduction
- **Adaptive SMC**: Self-tuning controller for uncertainty handling
- **Hybrid Adaptive STA-SMC**: Combined model-based and robust control

Each controller is optimized using Particle Swarm Optimization (PSO) for optimal performance.
