# Controllers Module Documentation

**Documentation for sliding mode controllers, factory system, and control primitives**

## Overview

This section provides complete documentation for the DIP_SMC_PSO controllers module, including:

- **Technical Guides**: In-depth controller implementation and theory
- **Mathematical Foundations**: Control theory and stability analysis
- **API Reference**: Detailed code documentation
- **Best Practices**: Usage patterns and optimization workflows

## 📚 Technical Guides

### Core SMC Controllers

Technical guides for each sliding mode controller variant:

```{toctree}
:maxdepth: 2
:caption: Core SMC Technical Guides

classical_smc_technical_guide
adaptive_smc_technical_guide
sta_smc_technical_guide
```

**Coverage:**

- Mathematical foundation with complete Lyapunov proofs
- Architecture and implementation details
- Parameter configuration and tuning
- Integration examples and troubleshooting
- Performance characteristics

### Advanced SMC Controllers

```{toctree}
:maxdepth: 2
:caption: Advanced SMC Technical Guides

hybrid_smc_technical_guide
mpc_technical_guide
swing_up_smc_technical_guide
```

**Coverage:**

- Hybrid Adaptive-STA SMC for maximum performance
- Model Predictive Control with constraint handling
- Energy-based swing-up for large angle stabilization
- Optimization-based and mode-switching strategies

### Factory System & Primitives

```{toctree}
:maxdepth: 2
:caption: Infrastructure Documentation

factory_system_guide
control_primitives_reference
```

**Topics:**

- Enterprise factory pattern vs clean SMC factory
- PSO integration workflows
- Configuration management
- Control primitives (saturation, dead zones, safe operations)
- Numerical stability guarantees

## 🔬 Mathematical Foundations

```{toctree}
:maxdepth: 2
:caption: Control Theory

../mathematical_foundations/smc_complete_theory
../mathematical_foundations/controller_comparison_theory
```

**Content:**

- Unified mathematical theory for all 4 SMC variants
- Lyapunov stability proofs and convergence analysis
- Comparative controller analysis with decision matrices
- Theoretical performance bounds

---

## 📖 API Reference

Complete Python API documentation for all controller modules:

```{toctree}
:maxdepth: 2
:caption: Code Documentation

../reference/controllers/index
```

**Modules:**

- `src.controllers.smc` - Core SMC controllers
- `src.controllers.factory` - Controller factory system
- `src.controllers.specialized` - Swing-up and specialized controllers
- `src.controllers.mpc` - Model predictive control

---

## Quick Reference

### Controller Selection Guide

| Controller Type | Best For | Convergence | Chattering | Complexity |
|----------------|----------|-------------|------------|------------|
| **Classical SMC** | General purpose, known systems | Exponential | High | Low |
| **Adaptive SMC** | Unknown dynamics, online tuning | Exponential | Medium | Medium |
| **Super-Twisting SMC** | Chattering-free control | Finite-time | Low | Medium |
| **Hybrid Adaptive-STA** | Maximum performance | Finite-time | Very Low | High |

### Gain Count Summary

- **Classical SMC**: 6 gains `[k1, k2, λ1, λ2, K, kd]`
- **Adaptive SMC**: 5 gains `[k1, k2, λ1, λ2, γ]`
- **Super-Twisting SMC**: 6 gains `[K1, K2, k1, k2, λ1, λ2]`
- **Hybrid Adaptive-STA**: 4 gains `[k1, k2, λ1, λ2]`

### Usage Examples

**Classical SMC:**

```python
from src.controllers.factory import create_controller

controller = create_controller(
    'classical_smc',
    gains=[20.0, 15.0, 12.0, 8.0, 35.0, 5.0],
    config=config
)
```

**PSO Optimization:**

```python
# example-metadata:
# runnable: false

from src.controllers.factory import create_smc_for_pso, get_gain_bounds_for_pso
from src.controllers.factory import SMCType

lower_bounds, upper_bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)

def controller_factory(gains):
    return create_smc_for_pso(SMCType.CLASSICAL, gains)

# Use with PSO tuner...
```

**Control Primitives:**

```python
from src.utils.control import saturate, smooth_sign, dead_zone

# Chattering reduction
u_switch = -K * saturate(sigma, epsilon=0.01, method='tanh', slope=3.0)

# Adaptive gain freeze inside dead zone
if abs(sigma) <= dead_zone_threshold:
    dK = 0.0
else:
    dK = gamma * abs(sigma) - leak_rate * (K - K_init)
```

---

## Documentation Roadmap

### Completed (Weeks 1-4)

✅ **Week 1**: Documentation automation infrastructure
✅ **Week 2**: Core SMC controllers (Classical, Adaptive, STA) + mathematical foundations
✅ **Week 3**: Plant models + Optimization/Simulation infrastructure
✅ **Week 4**: Advanced controllers (Hybrid SMC, MPC, Swing-Up SMC)

### New in Week 4

📚 **{doc}`hybrid_smc_technical_guide`** - Hybrid Adaptive-STA SMC for maximum performance
📚 **{doc}`mpc_technical_guide`** - Model predictive control with constraint handling
📚 **{doc}`swing_up_smc_technical_guide`** - Energy-based large angle stabilization

### Documentation Coverage Summary

**Controller Guides** (7 total):
- Classical SMC, Adaptive SMC, Super-Twisting SMC (Week 2)
- Hybrid Adaptive-STA SMC, MPC, Swing-Up SMC (Week 4)
- Factory System & Control Primitives (Week 2)

**Supporting Documentation:**
- Mathematical Foundations (Lyapunov theory, stability proofs)
- Plant Models (Simplified, Full-Fidelity, Low-Rank dynamics)
- Optimization/Simulation Infrastructure (PSO, batch simulation, configuration)

**Total Documentation**: ~12,000+ lines of research-grade technical content

---

## Related Documentation

- **{doc}`../theory_overview`** - High-level control theory overview
- **{doc}`../architecture`** - System architecture and design patterns
- **{doc}`../reference/optimizer/index`** - PSO optimization documentation
- **{doc}`../TESTING`** - Testing protocols and validation

---

## Contributing

For guidelines on extending controllers or adding new features, see:
- **{doc}`../CONTRIBUTING`** - Contribution guidelines
- **{doc}`../context`** - Development context and patterns

---

**Documentation Version:** 2.0 (Week 4 Complete)
**Last Updated:** 2025-10-04
**Coverage:** 7 controller guides (3 core + 3 advanced + factory), Plant models, Optimization infrastructure, Mathematical foundations
---

**Navigation**: Return to [Master Navigation Hub](../NAVIGATION.md) | Browse all [Documentation Categories](../index.md)
