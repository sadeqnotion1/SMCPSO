# Implementation Guide -

Code Documentation Index **Note:** Code documentation has been integrated into the API reference. **See:** [API Reference Index](../index.md)

## Complete Code Documentation

For detailed implementation documentation, refer to: - **Controllers:** [reference/controllers/index.md](../controllers/index.md)
- **Plant Models:** [reference/plant/models_base___init__.md](../plant/models_base___init__.md)
- **Simulation Engine:** [reference/simulation/core___init__.md](../simulation/core___init__.md)
- **Optimization:** [reference/optimization/__init__.md](../optimization/__init__.md) ## Implementation Guides ### Controller Implementation
- [Classical SMC Implementation](../../controllers/classical_smc_technical_guide.md)
- [Adaptive SMC Implementation](../../controllers/adaptive_smc_technical_guide.md)
- [Super-Twisting SMC Implementation](../../controllers/sta_smc_technical_guide.md)
- [Hybrid Adaptive STA Implementation](../../controllers/hybrid_smc_technical_guide.md) ### Factory System
- [Factory System Guide](../../controllers/factory_system_guide.md)
- [Factory API Reference](../controllers/factory.md)
- [PSO Integration](../../factory/enhanced_pso_integration_guide.md) ### Plant Dynamics
- [Plant Models Guide](../../plant/models_guide.md)
- [Dynamics Derivations](../../mathematical_foundations/dynamics_derivations.md) ## Code Organization The implementation follows this structure:
```
src/
├── controllers/ # SMC controller implementations
├── plant/ # Dynamics models
├── core/ # Simulation engine
├── optimization/ # PSO and optimization
├── analysis/ # Performance analysis
└── utils/ # Utilities and helpers
``` For complete API reference, see the [main API index](../index.md).
