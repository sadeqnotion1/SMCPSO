# Mathematical Foundations

**Rigorous control theory and stability analysis for sliding mode controllers**

## Overview

This section provides mathematical foundations for the sliding mode control strategies implemented in the DIP_SMC_PSO project. All proofs follow standard control theory literature with rigorous Lyapunov stability analysis.

---

## SMC Control Theory

Comprehensive mathematical foundations for all sliding mode control variants.

```{toctree}
:maxdepth: 2
:caption: SMC Theory

README
smc_complete_theory
smc_theory
sliding_surface_analysis
boundary_layer_derivations
```

**Unified Mathematical Theory for All SMC Variants** ### Topics Covered: #### 1. Classical Sliding Mode Control
- Linear sliding surface design: $s = \lambda_1 \theta_1 + \lambda_2 \theta_2 + k_1 \dot{\theta}_1 + k_2 \dot{\theta}_2$
- Lyapunov function: $V = \frac{1}{2}s^2$
- Exponential convergence: $\dot{V} \leq -\eta|s|$ where $\eta = K - ||d||_\infty > 0$
- Boundary layer chattering reduction
- Reaching phase and sliding phase analysis #### 2. Super-Twisting Sliding Mode Control
- 2nd-order sliding mode algorithm
- Finite-time convergence: $T_{reach} \leq \frac{2|s(0)|^{1/2}}{K_1^{1/2}}$
- Continuous control law: $u = -K_1\sqrt{|s|}\text{sign}(s) + z$
- Integral component: $\dot{z} = -K_2 \text{sign}(s)$
- Stability condition: $K_1 > 2L$, $K_2 > \frac{5L}{2}$ where $L$ is Lipschitz constant #### 3. Adaptive Sliding Mode Control
- Online gain adaptation without prior disturbance knowledge
- Adaptation law: $\dot{K} = \gamma |s| - \beta(K - K_{init})$ with leak term
- Dead zone freeze mechanism for robustness
- Exponential convergence with adaptive parameters
- Stability proof via Lyapunov-like analysis #### 4. Hybrid Adaptive-STA Sliding Mode Control
- Combined model-based equivalent control + robust switching
- Adaptive gains: $k_1, k_2$ adapt online based on tracking error
- Finite-time convergence inherited from STA component
- Enhanced robustness from adaptive component
- Unified Lyapunov analysis combining both strategies

---

## Controller Comparison & Analysis

```{toctree}
:maxdepth: 2
:caption: Controller Analysis

controller_comparison_theory
advanced_algorithms_guide
algorithm_fixes_summary
```

**Systematic Comparison of All 4 SMC Controllers** ### Comparison Criteria: #### Performance Metrics:

- **Convergence Time**: $T_{settle}$ from initial condition to $||e|| < \epsilon$
- **Chattering Index**: $CI = \frac{1}{T}\int_0^T |\dot{u}(t)| dt$
- **Control Effort**: $J_u = \int_0^T u^2(t) dt$
- **Tracking Error**: $ISE = \int_0^T ||x(t) - x_{ref}(t)||^2 dt$ #### Theoretical Properties:
- **Convergence Type**: Exponential vs Finite-time
- **Robustness**: Matched vs Unmatched uncertainties
- **Computational Complexity**: $O(1)$ vs $O(n^2)$ per timestep
- **Parameter Sensitivity**: Gain tuning difficulty #### Practical Considerations:
- **Ease of Implementation**: Code complexity and dependencies
- **Real-time Feasibility**: Computational requirements
- **Sensor Requirements**: Measurement quality needed
- **Tuning Difficulty**: PSO convergence and parameter ranges ### Decision Matrices: **Performance vs Complexity:** | Controller | Performance | Complexity | Overall Score |
|-----------|-------------|------------|---------------|
| Classical SMC | ★★★☆☆ | ★★★★★ | 4.0/5 |
| Adaptive SMC | ★★★★☆ | ★★★☆☆ | 3.5/5 |
| Super-Twisting SMC | ★★★★☆ | ★★★★☆ | 4.5/5 |
| Hybrid Adaptive-STA | ★★★★★ | ★★☆☆☆ | 4.0/5 |

---

## PSO Optimization Theory

Particle Swarm Optimization mathematical foundations and convergence analysis.

```{toctree}
:maxdepth: 2
:caption: PSO Theory

pso_algorithm_theory
optimization_landscape_analysis
```

---

## System Dynamics & Numerical Methods

Double inverted pendulum dynamics and numerical integration theory.

```{toctree}
:maxdepth: 2
:caption: Dynamics & Numerics

dynamics_derivations
numerical_integration_theory
simulation_architecture_guide
config_validation_specification
```

---

## Validation & Testing Methodology

Mathematical validation frameworks and testing standards.

```{toctree}
:maxdepth: 2
:caption: Validation Methodology

test_validation_methodology
validation_framework_guide
```

---

## Mathematical Notation ### State Vector

$$\vec{x} = [x, \theta_1, \theta_2, \dot{x}, \dot{\theta}_1, \dot{\theta}_2]^T \in \mathbb{R}^6$$ ### Sliding Surface
$$s(\vec{x}) = \lambda_1 \theta_1 + \lambda_2 \theta_2 + k_1 \dot{\theta}_1 + k_2 \dot{\theta}_2$$ ### Control Law Structure
$$u = u_{eq} + u_{sw}$$ where:
- $u_{eq}$: Equivalent control (model-based)
- $u_{sw}$: Switching control (robust term) ### Lyapunov Stability
$$V(\vec{x}) \geq 0 \quad \forall \vec{x} \neq 0$$
$$\dot{V}(\vec{x}) \leq -\alpha V(\vec{x}) \quad \alpha > 0$$

---

## Key References ### Sliding Mode Control Theory **Foundational Texts:**

- Utkin, V.I. "Sliding Modes in Control and Optimization" (1992)
- Slotine, J.J. & Li, W. "Applied Nonlinear Control" (1991)
- Edwards, C. & Spurgeon, S. "Sliding Mode Control: Theory and Applications" (1998) **Higher-Order Sliding Modes:**
- Levant, A. "Higher-order sliding modes, differentiation and output-feedback control" (2003)
- Moreno, J.A. & Osorio, M. "Strict Lyapunov Functions for the Super-Twisting Algorithm" (2012) **Adaptive Sliding Modes:**
- Plestan, F. et al. "A new algorithm for high-order sliding mode control" (2010)
- Shtessel, Y. et al. "Sliding Mode Control and Observation" (2014) ### Lyapunov Stability Theory
- Khalil, H.K. "Nonlinear Systems" (3rd ed., 2002)
- Slotine, J.J. & Li, W. "Applied Nonlinear Control" (1991)

---

## Practical Applications For implementation details and practical usage, see:

- **{doc}`../controllers/classical_smc_technical_guide`** - Classical SMC implementation
- **{doc}`../controllers/adaptive_smc_technical_guide`** - Adaptive SMC implementation
- **{doc}`../controllers/sta_smc_technical_guide`** - Super-Twisting SMC implementation
- **{doc}`../controllers/factory_system_guide`** - Factory system and PSO integration ### Plant Dynamics and Optimization - **{doc}`../plant/models_guide`** - Double inverted pendulum dynamics models with Lagrangian derivations
- **{doc}`../optimization_simulation/guide`** - PSO optimization algorithms and simulation infrastructure

---

## Verification and Validation All theoretical results are validated through:

- **Numerical simulations**: Monte Carlo with 1000+ trials
- **PSO parameter optimization**: Systematic gain tuning
- **Comparative benchmarking**: Statistical significance testing
- **Robustness analysis**: Parameter uncertainty studies See **{doc}`../TESTING`** for validation protocols.

---

**Documentation Version:** 1.0 (Week 2 Complete)
**Last Updated:** 2025-10-04
**Coverage:** 4 SMC variants with complete Lyapunov proofs, comparative analysis
---

**Navigation**: Return to [Master Navigation Hub](../NAVIGATION.md) | Browse all [Documentation Categories](../index.md)
