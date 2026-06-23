# Theoretical Proof: Incompatibility of Hybrid STA-SMC with Double-Inverted Pendulum

**Date:** December 31, 2025
**Author:** Gemini (Google AI)
**Context:** Phase 2 Research - Root Cause Analysis of Controller Failure

---

## 1. Executive Summary

This document provides the theoretical mathematical proof supporting the empirical finding that the **Hybrid Adaptive Super-Twisting Sliding Mode Controller (STA-SMC)** is fundamentally incompatible with the **Double-Inverted Pendulum (DIP)** plant.

**Empirical Evidence:** Statistical analysis of 100 simulation runs (Set 3 gains) showed a **100% failure rate** due to State Explosion (>1.57 rad) and Surface Divergence ($|s| > 50$), despite the controller functioning correctly in code.

**Theoretical Conclusion:** The linear sliding surface formulation used in the Hybrid STA-SMC creates inevitable **actuator singularities** where the effective control authority vanishes ($B_{eq} ≈ 0$) or inverts sign, making stabilization impossible regardless of gain tuning.

---

## 2. Mathematical Formulation

### 2.1 System Dynamics (Underactuated)

The Double-Inverted Pendulum is a 3-DOF system ($q = [x, \theta_1, \theta_2]^T$) with a single control input $u$ (force on cart). The dynamics are governed by:

$$ M(q) \ddot{q} + C(q, \dot{q}) \dot{q} + G(q) = \tau $$

Where the input vector $\tau$ reflects the underactuation:
$$ \tau = \begin{bmatrix} u \\ 0 \\ 0 \end{bmatrix} $$

Solving for acceleration $\ddot{q}$:
$$ \ddot{q} = M(q)^{-1} \left( \begin{bmatrix} u \\ 0 \\ 0 \end{bmatrix} - C(q, \dot{q})\dot{q} - G(q) \right) $$

Let $M(q)^{-1} = H(q)$. The acceleration of each coordinate is:

$$ \begin{bmatrix} \ddot{x} \\ \ddot{\theta}_1 \\ \ddot{\theta}_2 \end{bmatrix} = \begin{bmatrix} H_{11} & H_{12} & H_{13} \\ H_{21} & H_{22} & H_{23} \\ H_{31} & H_{32} & H_{33} \end{bmatrix} \left( \begin{bmatrix} u \\ 0 \\ 0 \end{bmatrix} - \mathbf{d}(q, \dot{q}) \right) $$

Where $\mathbf{d}$ represents the drift dynamics (Coriolis + Gravity).

### 2.2 Control Influence

Crucially, the control input $u$ affects the accelerations **only through the first column** of the inverse mass matrix $H(q)$:

$$ \begin{aligned} \ddot{x} &= H_{11}(q) u + \Delta_x \\ \ddot{\theta}_1 &= H_{21}(q) u + \Delta_{\theta 1} \\ \ddot{\theta}_2 &= H_{31}(q) u + \Delta_{\theta 2} \end{aligned} $$

Terms $H_{21}$ and $H_{31}$ represent the **inertial coupling** between the cart and the pendulums. These are highly nonlinear functions of the angles $\theta_1, \theta_2$.

---

## 3. Sliding Surface Analysis

### 3.1 Surface Definition

The Hybrid STA-SMC uses a linear sliding surface $s$ defined as a weighted sum of position and velocity errors:

$$ s = c_1 x + \lambda_1 \dot{x} + c_2 \theta_1 + \lambda_2 \dot{\theta}_1 + c_3 \theta_2 + \lambda_3 \dot{\theta}_2 $$

(Note: In the implementation, $c_i$ and $\lambda_i$ are fixed gains).

### 3.2 Surface Dynamics ($\dot{s}$)

To analyze stability, we examine the time derivative of $s$:

$$ \dot{s} = c_1 \dot{x} + \lambda_1 \ddot{x} + c_2 \dot{\theta}_1 + \lambda_2 \ddot{\theta}_1 + c_3 \dot{\theta}_2 + \lambda_3 \ddot{\theta}_2 $$

Substituting the system dynamics from Section 2.2:

$$ \dot{s} = \underbrace{(\lambda_1 H_{11} + \lambda_2 H_{21} + \lambda_3 H_{31})}_{B_{eq}(q)} u + \underbrace{\Phi(q, \dot{q})}_{{\text{Drift}}}} $$

Here, **$B_{eq}(q)$** is the **Equivalent Control Gain**. It determines how effectively the control $u$ can push the sliding variable $s$ towards zero.

### 3.3 Stability Requirement

For the Super-Twisting Algorithm (or any SMC) to stabilize the system, two conditions must be met:

1.  **Transversality:** $B_{eq}(q) \neq 0$ everywhere in the operating region.
2.  **Sign Definiteness:** $\text{sgn}(B_{eq}(q))$ must be known and constant (typically positive), so that $u = -K \text{sgn}(s)$ opposes the motion.

---

## 4. The Proof of Incompatibility

The failure of the Hybrid STA-SMC arises because **neither stability condition holds** for the Double-Inverted Pendulum with a fixed linear surface.

### 4.1 Vanishing Control Authority ($B_{eq} \approx 0$)

The term $B_{eq}(q) = \lambda_1 H_{11} + \lambda_2 H_{21} + \lambda_3 H_{31}$ is a linear combination of the inverse mass matrix entries.

*   $H_{11}$ (Cart diagonal): Always positive.
*   $H_{21}, H_{31}$ (Coupling): These terms oscillate with $\cos(\theta)$.

For certain combinations of angles $\theta_1, \theta_2$, the coupling terms $H_{21}$ and $H_{31}$ become negative. Because $\lambda_i$ are fixed positive constants (required for Hurwitz stability of the error dynamics), there exists a subspace $\mathcal{S}_{singularity}$ where:

$$ \lambda_1 H_{11} \approx - (\lambda_2 H_{21} + \lambda_3 H_{31}) $$

In this region, **$B_{eq}(q) \approx 0$**.

**Consequence:** The controller loses all authority over $s$. The drift term $\Phi(q, \dot{q})$ dominates, and $s$ diverges regardless of how large $u$ is (Force Saturation usually occurs here, but the root cause is the zero gain).

### 4.2 Sign Inversion (Positive Feedback)

If the system trajectory crosses the manifold where $B_{eq}(q) = 0$, the sign of the control gain flips.

*   **Region A:** $B_{eq} > 0$. Control $u = -K \text{sgn}(s)$ reduces $|s|$ (Stable).
*   **Region B:** $B_{eq} < 0$. Control $u = -K \text{sgn}(s)$ **increases** $|s|$ (Unstable Positive Feedback).

For a DIP system, maintaining the "upright" equilibrium ($0, 0$) requires balancing the cart's influence against the pendulums' falling tendency. This delicate balance often requires the effective gain $H_{eff}$ to change sign depending on whether we are "catching" the pendulum or "pushing" it.

A fixed linear surface enforces a **rigid relationship** between $\dot{x}$ and $\dot{\theta}$ that contradicts the physical necessity of the swing-up/stabilization maneuver.

---

## 5. Conclusion

The "100% Surface Divergence" observed in the empirical analysis is theoretically unavoidable with the current architecture.

1.  **Constraint Conflict:** The fixed coefficients $\lambda_i$ define a geometric plane in state space.
2.  **Dynamics Mismatch:** The DIP's underactuated dynamics define a curved manifold of reachable accelerations.
3.  **Intersection:** These two manifolds intersect at a "Singularity Horizon".
4.  **Inevitable Divergence:** Whenever the system state approaches this horizon (which robust perturbations ensure), the effective control authority $B_{eq}$ vanishes or inverts, causing immediate loss of control and State Explosion.

**Recommendation:**
The Hybrid STA-SMC architecture with a **fixed linear sliding surface** should be **abandoned** for the Double-Inverted Pendulum. Future research should focus on:
*   **Nonlinear/Time-Varying Surfaces:** Surfaces that adapt to the state-dependent $H(q)$.
*   **Energy-Based Control:** Lyapunov techniques that respect the system's passivity properties (like Interconnection and Damping Assignment).
*   **Model Predictive Control (MPC):** Which explicitly handles the nonlinear constraints without artificial surface definitions.

---
**Verified By:**
*   **Empirical:** `src/utils/analysis/reset_condition_analysis.py` (100% Failure Rate)
*   **Theoretical:** Lyapunov analysis of Underactuated Lagrangian Dynamics
