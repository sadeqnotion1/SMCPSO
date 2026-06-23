# Complete Sliding Mode Control Mathematical Theory

**Double-Inverted Pendulum Control System** **Document Version**: 1.0
**Created**: 2025-10-04
**Status**: Research-Grade Reference **Purpose**: Unified mathematical foundation for all SMC variants in the DIP-SMC-PSO system, including rigorous Lyapunov stability proofs, convergence analysis, finite-time convergence theory, and implementation considerations.

---

## Table of Contents 1. [Introduction and Fundamentals](#1-introduction-and-fundamentals)

2. [Classical SMC Theory](#2-classical-smc-theory)
3. [Super-Twisting SMC Theory](#3-super-twisting-smc-theory)
4. [Adaptive SMC Theory](#4-adaptive-smc-theory)
5. [Hybrid Adaptive STA-SMC Theory](#5-hybrid-adaptive-sta-smc-theory)
6. [Convergence Analysis Comparison](#6-convergence-analysis-comparison)
7. [Numerical Considerations](#7-numerical-considerations)
8. [References](#8-references)

---

## 1. Introduction and Fundamentals ### 1.1 Overview The double-inverted pendulum (DIP) is a canonical benchmark for nonlinear, underactuated control systems. With two pendula attached in series to a horizontally moving cart, the system has fewer actuators than degrees of freedom, making it both **underactuated** and **strongly nonlinear**. Conventional linear controllers struggle with large deflections, parameter variations, and model uncertainty. Sliding Mode Control (SMC) addresses these challenges by forcing the system state onto a pre-defined **sliding manifold**. When the state reaches this manifold, the resulting closed-loop dynamics become insensitive to matched disturbances and uncertainties. The control law compensates modeling errors through the control input channel, causing the plant to behave according to the reduced-order dynamics on the manifold. This robustness and finite-time convergence (for higher-order SMC) make SMC attractive for underactuated systems. However, the discontinuous switching law of classical SMC induces **chattering**, a high-frequency oscillation caused by rapid control switching when the state crosses the sliding surface. Chattering increases control effort, excites unmodeled high-frequency modes, and can cause wear in actuators. Introducing a boundary layer around the sliding surface alleviates chattering but enlarges the tracking error. This document presents the unified mathematical theory for four SMC variants implemented in this project:

1. **Classical SMC**: First-order sliding mode with boundary layer
2. **Super-Twisting SMC (STA)**: Second-order sliding mode for continuous control
3. **Adaptive SMC**: Online gain adaptation for unknown disturbances
4. **Hybrid Adaptive STA-SMC**: Combined adaptive and super-twisting algorithms ### 1.2 State Space Formulation The dynamics of the double-inverted pendulum are described by the Euler-Lagrange equations: ```
M(q)q̈ + C(q,q̇)q̇ + G(q) = Bu
``` where:
- **q** = [x, θ₁, θ₂]ᵀ is the generalized coordinate vector (cart position, pendulum angles)
- **M(q)** ∈ ℝ³ˣ³ is the inertia matrix (configuration-dependent)
- **C(q,q̇)q̇** represents Coriolis and centrifugal forces
- **G(q)** is the gravitational force vector
- **B** = [1, 0, 0]ᵀ is the input distribution matrix
- **u** ∈ ℝ is the control force applied to the cart **State vector**: x = [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]ᵀ ∈ ℝ⁶ **Key Properties**:
- **Underactuated**: rank(B) = 1 < 3 (fewer actuators than degrees of freedom)
- **Matched disturbances**: Disturbances d entering through the same channel as control input
- **Controllability**: The system is locally controllable around the upright equilibrium ### 1.3 Sliding Mode Fundamentals **Sliding Surface**: A hypersurface σ(x) = 0 in the state space, designed such that the system exhibits desired behavior when constrained to this surface. **Reachability Condition**: The fundamental condition ensuring the system state reaches the sliding surface: ```
σσ̇ < 0 whenever σ ≠ 0
``` This condition guarantees that σ acts as a Lyapunov function, driving the system toward the surface. **Invariance Property**: Once on the sliding surface (σ = 0), the system remains on it under ideal conditions (no disturbances, perfect control implementation). **Equivalent Control Method**: The equivalent control u_eq is the control required to maintain σ̇ = 0, derived by setting: ```

σ̇ = (∂σ/∂x)ẋ = (∂σ/∂x)f(x, u_eq) = 0
``` Solving for u_eq gives the **ideal** control that keeps the system on the sliding surface, assuming perfect knowledge of the dynamics. ### 1.4 Matched vs Unmatched Disturbances **Matched Disturbances**: Disturbances that enter through the same channel as the control input: ```
M(q)q̈ + C(q,q̇)q̇ + G(q) = B(u + d)
``` SMC can **completely reject** matched disturbances by choosing switching gain K > ||d||∞. **Unmatched Disturbances**: Disturbances entering through different channels. Classical SMC provides limited robustness against unmatched disturbances. Advanced techniques (integral SMC, higher-order SMC) can handle certain classes of unmatched disturbances.

---

## 2. Classical SMC Theory ### 2.1 Sliding Surface Design The sliding surface for the DIP system is defined as: ```

σ = λ₁θ₁ + λ₂θ₂ + k₁θ̇₁ + k₂θ̇₂
``` where:
- **θ₁, θ₂**: pendulum angles
- **θ̇₁, θ̇₂**: pendulum angular velocities
- **λ₁, λ₂ > 0**: sliding surface slope parameters (must be strictly positive)
- **k₁, k₂ > 0**: velocity feedback gains (must be strictly positive) **Mathematical Properties**: 1. **Hurwitz Stability Requirement**: The characteristic polynomial of the sliding dynamics must have all roots in the left half-plane: ``` s² + k₁s + λ₁ = 0 (for pendulum 1) s² + k₂s + λ₂ = 0 (for pendulum 2) ``` 2. **Positivity Constraints**: For asymptotic stability: ``` λ₁, λ₂ > 0 (slope parameters ensure stable surface) k₁, k₂ > 0 (damping parameters) ``` 3. **Pole Placement Interpretation**: The sliding surface parameters define the poles of the reduced-order dynamics: - **Critically damped**: k²ᵢ = 4λᵢ → poles at s = -kᵢ/2 (repeated real poles) - **Underdamped**: k²ᵢ < 4λᵢ → complex conjugate poles (faster, oscillatory) - **Overdamped**: k²ᵢ > 4λᵢ → distinct real poles (slower, smooth) **Design Guidelines**:
- Start with critically damped case: kᵢ = 2√λᵢ
- Increase kᵢ for more damping (slower convergence, smoother response)
- Decrease kᵢ for less damping (faster convergence, more oscillation) ### 2.2 Control Law Decomposition The control input u is decomposed into **equivalent control** and **robust switching**: ```
u = u_eq - K·sat(σ/ε) - k_d·σ
``` **Components**: 1. **Equivalent Control (u_eq)**: Cancels the nominal dynamics. Derived from σ̇ = 0: ``` σ̇ = L(M⁻¹(Bu + d) - M⁻¹(C(q,q̇)q̇ + G(q))) = 0 ``` where L = [λ₁, λ₂, k₁, k₂, 0, 0] is the sliding surface gradient. Solving for u: ``` u_eq = (LM⁻¹B)⁻¹ · L(M⁻¹(C(q,q̇)q̇ + G(q)) - [k₁λ₁θ̇₁ + k₂λ₂θ̇₂]) ``` 2. **Switching Term (-K·sat(σ/ε))**: Provides robustness against disturbances. The gain K must satisfy: ``` K > ||d||∞ ``` 3. **Damping Term (-k_d·σ)**: Improves transient response, reduces overshoot. ### 2.3 Boundary Layer Theory The discontinuous sign function is approximated within a boundary layer of width ε > 0 to reduce chattering: **Linear Saturation**:

```
sat(σ/ε) = { σ/ε, if |σ| ≤ ε sign(σ), if |σ| > ε
}
``` **Hyperbolic Tangent Approximation**:

```
sat(σ/ε) = tanh(σ/ε)
``` **Properties**:

- **Continuity**: Linear saturation is continuous at σ = ±ε
- **Smoothness**: tanh is C∞ everywhere
- **Approximation Error**: Bounded by ε **Trade-offs**:
- **Smaller ε** → Better tracking, more chattering
- **Larger ε** → Smoother control, larger steady-state error
- **Adaptive boundary layer**: ε = ε₀ + ε₁||σ|| adjusts based on sliding surface magnitude ### 2.4 Lyapunov Stability Analysis **Lyapunov Function**:
```
V = ½σ²
``` **Proof of Stability**: 1. **Positive Definiteness**: V > 0 for σ ≠ 0, V(0) = 0 ✓ 2. **Time Derivative**: ``` V̇ = σσ̇ = σ[λ₁θ̇₁ + λ₂θ̇₂ + k₁θ̈₁ + k₂θ̈₂] ``` 3. **Substitute Dynamics**: M(q)q̈ = Bu - C(q,q̇)q̇ - G(q) + d Solving for q̈ and substituting: ``` V̇ = σ · L · M⁻¹ · (B(u_eq - K·sign(σ) - k_d·σ + d) - C(q,q̇)q̇ - G(q)) ``` 4. **Simplification using σ̇ = 0 for u_eq**: The equivalent control u_eq is designed such that σ̇ = 0 when d = 0. Therefore: ``` V̇ = σ · L · M⁻¹ · B · (-K·sign(σ) + d - k_d·σ) ``` Let η_c = L·M⁻¹·B (controllability measure). Then: ``` V̇ = η_c · σ · (-K·sign(σ) + d - k_d·σ) = η_c · (-K|σ| + σd - k_d·σ²) ≤ η_c · (-K|σ| + |d|·|σ| - k_d·σ²) = η_c · (-(K - ||d||∞)|σ| - k_d·σ²) ``` 5. **Negative Definiteness**: If K > ||d||∞, then: ``` V̇ ≤ -η_c·η|σ| where η = K - ||d||∞ > 0 ``` Since η_c > 0 (controllability condition) and η > 0, we have V̇ < 0 for all σ ≠ 0. 6. **Conclusion**: By Lyapunov's theorem, σ → 0 asymptotically. ### 2.5 Convergence Rate Analysis **Exponential Convergence**: From V̇ ≤ -η_c·η|σ|, we can derive: ```

|σ(t)| ≤ |σ(0)|e^(-ηt)
``` **Time Constants**: On the sliding surface (σ = 0), the reduced-order dynamics are: ```
λ₁θ₁ + λ₂θ₂ + k₁θ̇₁ + k₂θ̇₂ = 0
``` For the critically damped case (k²ᵢ = 4λᵢ): ```

τᵢ = 2/kᵢ (time constant for pendulum i)
``` **Practical Implications**:
- Classical SMC achieves **exponential convergence** (not finite-time)
- Convergence rate determined by gains k₁, k₂
- Larger kᵢ → Faster convergence but potentially more oscillation

---

## 3. Super-Twisting SMC Theory ### 3.1 Second-Order Sliding Mode Concept The **super-twisting algorithm** (STA) is a second-order sliding mode technique that suppresses chattering by applying the discontinuity on the **derivative** of the control signal rather than on the control itself. **Key Innovation**: Move discontinuity to u̇ instead of u:
- **Classical SMC**: u contains sign(σ) → discontinuous control
- **STA SMC**: u̇ contains sign(σ) → continuous control, discontinuous derivative **Result**:
- u is continuous
- Both σ and σ̇ converge to zero in **finite time** **Sliding Variable** (for STA):
```

σ = k₁(θ̇₁ + λ₁θ₁) + k₂(θ̇₂ + λ₂θ₂)
``` ### 3.2 Super-Twisting Algorithm The STA control law consists of two components: ```
u = u_c + u_i + u_eq
``` **1. Continuous Term**:

```
u_c = -K₁√|σ|·sign(σ)
``` - Square-root law provides finite-time convergence

- Continuous but non-smooth at σ = 0
- Acts as nonlinear damping proportional to √|σ| **2. Integral Term**:
```
u̇_i = -K₂·sign(σ)
``` - Discontinuity applied to derivative

- Integrated to produce continuous u_i **Discrete Implementation**:
```
u_i(t+dt) = u_i(t) - K₂·sign(σ)·dt
``` **3. Equivalent Control**: Model-based feedforward (same as classical SMC) ### 3.3 Lyapunov Function for STA **Candidate Lyapunov Function** (Moreno & Osorio, 2012): ```

V = k₁|σ|^(3/2) + ½z²
``` where z is an auxiliary variable related to σ̇. **Finite-Time Convergence Proof (Sketch)**: 1. **Positive Definiteness**: V > 0 for (σ, z) ≠ (0, 0) ✓ 2. **Time Derivative** (using homogeneity argument): ``` V̇ = (3k₁/2)|σ|^(1/2)·σ̇·sign(σ) + z·ż ``` 3. **Substitute STA Dynamics**: - σ̇ is related to z through system dynamics - ż = -K₂·sign(σ) from control law 4. **Gain Conditions**: - K₁ > L (L = Lipschitz constant of disturbance derivative) - K₂ > K₁·C (C depends on system parameters) 5. **Result**: Under these conditions: ``` V̇ ≤ -β·V^(1/2) for some β > 0 ``` 6. **Finite-Time Convergence**: Integrating V̇ ≤ -β·V^(1/2) gives: ``` V(t) = 0 for all t ≥ T_reach ``` where: ``` T_reach ≤ 2V(0)^(1/2)/β ≤ 2|σ(0)|^(1/2)/(K₁^(1/2)) ``` **Key Takeaway**: Both σ and σ̇ reach zero in finite time, unlike classical SMC which only achieves exponential convergence. ### 3.4 Gain Selection Guidelines **K₁ Selection**:
- Must exceed max disturbance derivative: K₁ > L
- Larger K₁ → Faster convergence, higher control effort
- Typical range: K₁ ∈ [1, 50] **K₂ Selection**:
- Sufficient condition: K₂ ≥ K₁·C (C depends on system)
- Practical guideline: K₂ ≈ K₁ balances proportional/integral action
- Too large K₂ → Oscillations, potential instability **Tuning Strategy**:
1. Start with K₁ = 5, K₂ = 5
2. Increase K₁ if convergence is too slow
3. Adjust K₂ to balance integral action (typically K₂ ≈ K₁)
4. Use PSO optimization for fine-tuning **Advantages**:
- Finite-time convergence
- Continuous control (reduced chattering)
- Robustness against matched uncertainties **Disadvantages**:
- More complex tuning (2 gains vs 1 for classical)
- Higher computational cost (square root, integration)

---

## 4. Adaptive SMC Theory ### 4.1 Motivation and Problem Statement **Challenge**: Classical SMC requires prior knowledge of disturbance bounds (K > ||d||∞). In practice:
- Disturbance bounds may be unknown
- Conservative estimates lead to excessive control effort
- Time-varying disturbances require adaptive response **Solution**: Adaptive SMC adjusts the switching gain K(t) online based on observed sliding surface magnitude. **Advantages**:
- No need for disturbance bound knowledge a priori
- Avoids overly conservative gains
- Maintains robustness to unknown disturbances ### 4.2 Adaptation Law **Piecewise Adaptation with Dead Zone**: ```
K̇(t) = { γ|σ|, if |σ| > δ (outside dead zone - adaptation active) -αK, if |σ| ≤ δ (inside dead zone - leak prevents windup)
}
``` **Parameters**:

- **γ > 0**: Adaptation rate (how fast K grows)
- **δ > 0**: Dead zone width (noise tolerance threshold)
- **α ≥ 0**: Leak rate (prevents unbounded growth) **Bounded Adaptation**:
```
K_min ≤ K(t) ≤ K_max
``` **Rate Limiting**:

```
|K̇| ≤ Γ_max
``` **Rationale**:

- **Outside dead zone** (|σ| > δ): System is far from sliding surface → increase gain to dominate disturbances
- **Inside dead zone** (|σ| ≤ δ): Near sliding surface → hold or decay gain to prevent noise-induced windup
- **Leak term** (-αK): Prevents indefinite growth, allows gain to decrease when disturbances subside
- **Bounds**: Safety constraints prevent numerical issues and actuator saturation ### 4.3 Lyapunov Stability with Adaptation **Extended Lyapunov Function**: ```
V = ½σ² + 1/(2γ)(K - K*)²
``` where K* is the ideal (unknown) switching gain that would perfectly dominate disturbances. **Proof of Bounded Adaptation and Convergence**: 1. **Positive Definiteness**: V ≥ 0 for all (σ, K) ✓ 2. **Time Derivative**: ``` V̇ = σσ̇ + 1/γ·(K - K*)·K̇ ``` 3. **Substitute Control Law**: u = u_eq - K·sat(σ/ε) ``` σσ̇ = σ(L·M⁻¹·B·(-K·sat(σ/ε) + d)) ``` Assuming |σ| > ε (outside boundary layer): ``` σσ̇ = σ(-K·sign(σ) + d) = -K|σ| + σd ``` 4. **Substitute Adaptation Law**: K̇ = γ|σ| when |σ| > δ ``` V̇ = (-K|σ| + σd) + (K - K*)|σ| = -K|σ| + σd + K|σ| - K*|σ| = σd - K*|σ| ``` 5. **Bound Using Disturbance Magnitude**: ``` V̇ ≤ ||d||∞|σ| - K*|σ| = (||d||∞ - K*)|σ| ``` 6. **Negative Definiteness**: Since K* > ||d||∞ by definition: ``` V̇ ≤ -η|σ| where η = K* - ||d||∞ > 0 ``` 7. **Conclusion**: - V̇ < 0 whenever |σ| > δ → σ converges to dead zone - (K - K*)² remains bounded → K remains bounded - Inside dead zone: leak term prevents unbounded growth **Key Result**: Both σ → 0 and K remains bounded, ensuring stable adaptation without prior knowledge of ||d||∞. ### 4.4 Dead Zone Trade-offs **Benefits**:
- Prevents chattering from sensor noise
- Avoids gain windup in steady state
- Reduces control effort when near equilibrium
- Allows adaptation to focus on significant errors **Drawbacks**:
- Introduces small steady-state error (|σ| ≤ δ)
- Slows convergence near sliding surface
- Requires tuning of δ **Optimal Sizing**: δ ≈ 2-3× sensor noise magnitude **Leak Rate Selection**:
- **Small α** (α ≈ 10⁻³): Slow decay, maintains gain for persistent disturbances
- **Large α** (α ≈ 10⁻¹): Fast decay, quickly forgets past disturbances **Practical Guidelines**:
- Start with δ = 0.01, α = 0.001
- Increase δ if chattering persists despite adaptation
- Increase α if gain grows excessively during transients

---

## 5. Hybrid Adaptive STA-SMC Theory ### 5.1 Unified Sliding Surface The hybrid controller combines the adaptive law with the super-twisting algorithm using a **single sliding surface** that captures both pendulum dynamics and cart recentering. **Absolute Formulation** (default): ```
σ = c₁(θ̇₁ + λ₁θ₁) + c₂(θ̇₂ + λ₂θ₂) + k_c(ẋ + λ_c x)
``` **Relative Formulation** (optional, `use_relative_surface=True`): ```

σ = c₁(θ̇₁ + λ₁θ₁) + c₂((θ̇₂-θ̇₁) + λ₂(θ₂-θ₁)) + k_c(ẋ + λ_c x)
``` **Design Principles**:
- **Positive Coefficients**: cᵢ, λᵢ, k_c, λ_c > 0 (Hurwitz stability requirement)
- **Cart Recentering**: k_c, λ_c terms encourage cart to return to center
- **Relative Formulation**: Improves decoupling between pendulums but complicates analysis **Stability Condition**: All coefficients must be positive to ensure the sliding manifold is attractive and defines a stable reduced-order error surface. ### 5.2 Combined Super-Twisting with Adaptive Gains **Control Law**: ```
u = -k₁(t)√|σ|·sat(σ) + u_int - k_d·σ + u_eq
``` where:

- **k₁(t), k₂(t)**: Adaptive gains (time-varying)
- **u_int**: Integral term satisfying u̇_int = -k₂(t)·sat(σ)
- **k_d**: Damping gain (fixed)
- **u_eq**: Equivalent control (model-based feedforward) **Adaptive Law for Both Gains**: ```
k̇ᵢ(t) = { γᵢ|σ|·τ(σ), if |σ| > δ -leak, otherwise
}
``` **Self-Tapering Function**: ```
τ(σ) = |σ|/(|σ| + ε_taper)
``` **Properties**:

- τ(σ) → 1 as |σ| → ∞ (full adaptation when far from surface)
- τ(σ) → 0 as |σ| → 0 (adaptation slows near surface)
- Prevents overshoot and oscillation as σ → 0 **Bounded Adaptation**:
```
0 ≤ k₁(t) ≤ k₁_max
0 ≤ k₂(t) ≤ k₂_max
|u_int| ≤ u_int_max
``` Separating integral windup limit from actuator saturation ensures adaptation can proceed even when actuator saturates. ### 5.3 Lyapunov Analysis **Composite Lyapunov Function**: ```

V = k₁|σ|^(3/2) + ½z² + 1/(2γ₁)(k₁ - k₁*)² + 1/(2γ₂)(k₂ - k₂*)²
``` **Proof Sketch**: 1. **Combines STA and Adaptive Terms**: - First two terms: STA Lyapunov function (finite-time convergence) - Last two terms: Adaptive parameter error (bounded adaptation) 2. **Time Derivative Analysis**: ``` V̇ = (∂V/∂σ)σ̇ + (∂V/∂z)ż + (∂V/∂k₁)k̇₁ + (∂V/∂k₂)k̇₂ ``` 3. **Substitute Dynamics**: - σ̇ from STA control law with adaptive gains - ż = -k₂(t)·sign(σ) - k̇₁, k̇₂ from adaptation law with self-tapering 4. **Negative Definiteness**: Under appropriate gain conditions (k₁ > L, k₂ > k₁·C): ``` V̇ ≤ -β·V^(1/2) for some β > 0 ``` 5. **Key Results**: - **Finite-time convergence**: σ → 0 in finite time T ≤ 2V(0)^(1/2)/β - **Bounded gains**: k₁(t), k₂(t) remain in [0, k_max] - **Unknown disturbances**: No prior knowledge of ||d||∞ required ### 5.4 Advantages and Complexity **Advantages**:
- **Finite-time convergence** (from STA)
- **Continuous control** (low chattering from STA)
- **Adaptive to unknown disturbances** (from adaptation)
- **Single sliding surface** (simpler than dual-surface designs)
- **Cart recentering** (unified treatment of cart and pendulum dynamics) **Complexity**:
- **More parameters to tune**: c₁, λ₁, c₂, λ₂, k_c, λ_c, γ₁, γ₂, δ, ε_taper, k_d, ...
- **Higher computational cost**: Square root, integral update, adaptation law
- **Careful tuning required**: PSO optimization recommended **Recommended Use Cases**:
- Complex, highly coupled systems (✓ double-inverted pendulum)
- High uncertainty environments
- Research applications requiring maximum performance
- Systems needing finite-time convergence with minimal chattering

---

## 6. Convergence Analysis Comparison ### 6.1 Convergence Rate Summary | Controller | Convergence Type | Rate | Time to Surface | Steady-State Error |
|-----------|------------------|------|-----------------|-------------------|
| **Classical SMC** | Asymptotic | Exponential: O(e^(-ηt)) | Infinite (theoretically) | Bounded by ε (boundary layer) |
| **Adaptive SMC** | Asymptotic | Exponential: O(e^(-ηt)) | Infinite (theoretically) | Zero (if no dead zone) or bounded by δ |
| **STA SMC** | Finite-time | O(t^(1/2)) | T ≤ 2\|σ₀\|^(1/2)/K₁^(1/2) | Zero (exact convergence) |
| **Hybrid SMC** | Finite-time | O(t^(1/2)) | T ≤ 2\|σ₀\|^(1/2)/k₁(0)^(1/2) | Zero (exact convergence) | ### 6.2 Mathematical Definitions **Exponential Convergence**: ```
|σ(t)| ≤ Ce^(-ηt)|σ(0)|
``` - **Never reaches exactly zero** in finite time

- **Practical convergence**: Reaches ε-neighborhood quickly
- **Advantage**: Simple analysis, well-understood
- **Disadvantage**: Technically never achieves perfect tracking **Finite-Time Convergence**: ```
∃ T < ∞ : σ(t) = 0 for all t ≥ T
``` - **Exact convergence** in finite time T
- **Requires higher-order sliding modes** (e.g., STA)
- **Advantage**: Exact tracking after convergence time
- **Disadvantage**: More complex control law, higher computational cost ### 6.3 Convergence Time Bounds **Classical SMC** (95% settling time): ```
t_95% ≈ 3/η where η = K - ||d||∞
``` **STA SMC**: ```

T_reach ≤ 2|σ(0)|^(1/2)/(K₁^(1/2))
``` For typical initial condition |σ(0)| = 1.0 and K₁ = 25:
```

T_reach ≤ 2·1.0^(1/2)/25^(1/2) = 2/5 = 0.4 seconds
``` **Practical Implications**:
- **STA converges faster** for large initial errors
- **Classical SMC** can be competitive with well-tuned gains
- **Adaptive SMC** convergence time depends on adaptation rate ### 6.4 Phase Portrait Analysis **Classical SMC**:
- Spiral approach to σ = 0 line in (σ, σ̇) plane
- Exponential decay of both σ and σ̇
- Never reaches origin exactly **STA SMC**:
- Direct finite-time reach to origin in (σ, σ̇) plane
- Both σ and σ̇ reach zero simultaneously
- Twisting motion around origin during convergence **Adaptive SMC**:
- Spiral approach with varying damping (due to adaptive gain)
- Convergence rate changes as K(t) evolves
- Dead zone creates limit cycle around origin **Hybrid SMC**:
- Direct finite-time reach with adaptive rate
- Combines advantages of STA (finite-time) and adaptive (robustness)
- Self-tapering prevents overshoot near origin

---

## 7. Numerical Considerations ### 7.1 Matrix Regularization **Problem**: The inertia matrix M(q) can become ill-conditioned near singular configurations, leading to large rounding errors in inversion. **Tikhonov Regularization**: ```
M_reg = M(q) + αI, α > 0
``` **Benefits**:

- Prevents singularity when det(M) ≈ 0
- Shifts eigenvalues: λᵢ → λᵢ + α (all eigenvalues become ≥ α)
- Converts nearly-singular matrix to well-conditioned **Trade-off**: Introduces small approximation error in equivalent control **Typical Value**: α = 10⁻⁸ to 10⁻⁶ **Mathematical Justification**: Adding a positive constant to the diagonal of a symmetric matrix shifts all eigenvalues upward, converting an indefinite or singular matrix into a positive-definite one. ### 7.2 Condition Number Monitoring **Definition**: ```
κ(M) = ||M|| · ||M⁻¹||
``` **Thresholds**:
- **κ < 10³**: Well-conditioned (safe for direct inversion)
- **10³ < κ < 10⁶**: Moderate conditioning (use with caution)
- **κ > 10⁶**: Ill-conditioned → **use pseudo-inverse** **Pseudo-Inverse**: ```
M⁺ = (MᵀM + αI)⁻¹Mᵀ (Moore-Penrose pseudo-inverse)
``` - Provides least-squares solution

- Minimizes effect of noise
- More robust than direct inversion for ill-conditioned systems **Implementation**:
```python
if np.linalg.cond(M) > 1e6: M_inv = np.linalg.pinv(M) # Use pseudo-inverse
else: M_inv = np.linalg.inv(M) # Direct inversion safe
``` ### 7.3 Discrete-Time Implementation **Euler Integration** (for adaptive gains and STA integral): ```

u_int(k+1) = u_int(k) - K₂·sign(σ(k))·dt
K(k+1) = K(k) + γ|σ(k)|·dt
``` **Sampling Effects**:
- **dt too large** → Discrete chattering (control jumps between bounds)
- **dt too small** → Computational cost increases, numerical precision issues
- **Recommended**: dt ≤ 0.01s for DIP system **Discrete Chattering**: When dt is large relative to system dynamics, the control oscillates between saturation limits even though σ ≈ 0. Solution: Reduce dt or increase boundary layer ε. ### 7.4 Numerical Stability Checks **Implementation Safeguards**: 1. **Finite Value Checking**: ```python if not np.isfinite(u): u = 0.0 # Emergency fallback log_error("Non-finite control value detected") ``` 2. **Controllability Check**: ```python controllability = abs(L @ M_inv @ B) if controllability < ε_threshold: # System near uncontrollable configuration u_eq = 0.0 # Disable equivalent control ``` Typical threshold: ε_threshold = 10⁻⁴ 3. **Actuator Saturation**: ```python u_sat = np.clip(u, -max_force, max_force) ``` 4. **Emergency Reset**: ```python if state_norm > 10.0 or velocity_norm > 50.0: # System diverging - reset controller state u_int = 0.0 K = K_init ``` **Robustness Best Practices**:
- Always validate outputs before applying control
- Monitor condition numbers of matrix operations
- Implement fallback strategies for edge cases
- Log warnings for numerical issues without crashing

---

## 8. References ### Primary SMC References [1] **Utkin, V.I.** (1992). "Sliding Modes in Control and Optimization". Springer-Verlag, Berlin. doi: 10.1007/978-3-642-84379-2
*Foundational text on SMC theory, sliding mode equations, and exponential stability.* [2] **Edwards, C. and Spurgeon, S.K.** (1998). "Sliding Mode Control: Theory and Applications". CRC Press, Boca Raton, FL. ISBN: 978-0748406012
*Chapter 3: Sliding Surface Design - pole placement via surface parameters.* [3] **Slotine, J.-J.E. and Li, W.** (1991). "Applied Nonlinear Control". Prentice Hall, Englewood Cliffs, NJ. ISBN: 0-13-040890-5
*Practical implementation of SMC for nonlinear systems.* ### Higher-Order SMC References [4] **Levant, A.** (2003). "Higher-order sliding modes, differentiation and output-feedback control". International Journal of Control, 76(9-10):924-941. doi: 10.1080/0020717031000099029
*Foundations of higher-order sliding modes and super-twisting algorithms.* [5] **Levant, A.** (2007). "Principles of 2-sliding mode design". Automatica, 43(4):576-586. doi: 10.1016/j.automatica.2006.10.008
*Systematic design methodology for second-order sliding modes.* [6] **Moreno, J.A. and Osorio, M.** (2012). "Strict Lyapunov Functions for the Super-Twisting Algorithm". IEEE Transactions on Automatic Control, 57(4):1035-1040.
*Rigorous Lyapunov analysis proving finite-time convergence of STA.* ### Adaptive SMC References [7] **Yang, Y., Meng, M.Q.-H., and Tan, K.K.** (2007). "Adaptive sliding mode control for uncertain systems". Automatica, 43(2):201-207.
*Online gain adaptation for unknown disturbance bounds.* [8] **Huang, J., Yao, B., and Tao, G.** (2008). "Adaptive second-order sliding-mode control of nonlinear systems". IEEE Transactions on Automatic Control, 53(11):2689-2694.
*Combines adaptation with second-order sliding modes.* ### Chattering Reduction References [9] **Burton, J.A. and Zinober, A.S.I.** (1986). "Continuous approximation of variable structure control". International Journal of Systems Science, 17(6):875-885. doi: 10.1080/00207728608926853
*Boundary layer theory for chattering reduction.* [10] **Utkin, V.I., Guldner, J., and Shi, J.** (2009). "Sliding Mode Control in Electro-Mechanical Systems" (2nd ed.). CRC Press, Boca Raton, FL. doi: 10.1201/9781420065619
*Practical techniques for chattering mitigation.* ### Control Theory Fundamentals [11] **Utkin, V.I.** (1977). "Variable structure systems with sliding modes". IEEE Transactions on Automatic Control, 22(2):212-222.
*Seminal paper establishing sliding mode control theory.* [12] **Slotine, J.-J. and Sastry, S.** (1983). "Tracking control of nonlinear systems using sliding surfaces". International Journal of Control, 38(2):465-492.
*Application of SMC to tracking problems.* [13] **Young, K.D., Utkin, V.I., and Özgüner, Ü.** (1999). "A control engineer's guide to sliding mode control". IEEE Transactions on Control Systems Technology, 7(3):328-342. doi: 10.1109/87.761053
*Practical guide for implementing SMC in engineering applications.* ### Recent Advances [14] **Shtessel, Y., Edwards, C., Fridman, L., and Levant, A.** (2014). "Sliding Mode Control and Observation". Birkhäuser, New York, NY. doi: 10.1007/978-0-8176-4893-0
*modern treatment of SMC and observation techniques.* [15] **Levant, A.** (1993). "Sliding order and sliding accuracy in sliding mode control". International Journal of Control, 58(6):1247-1263. doi: 10.1080/00207179308923053
*Analysis of sliding accuracy and convergence properties.* ### Optimization and Tuning [16] **Messina, A., Lanzafame, R., and Tomarchio, S.** (2013). "Multi-objective optimal tuning of sliding mode controllers by evolutionary algorithms". IEEE/ASME Transactions on Mechatronics, 18(5):1446-1454.
*PSO and evolutionary algorithms for SMC gain tuning.* ### Underactuated Systems [17] **Utkin, V.I.** (1993). "Sliding mode control design principles and applications to electric drives". IEEE Transactions on Industrial Electronics, 40(1):23-36. doi: 10.1109/41.184818
*Application of SMC to underactuated mechanical systems.* [18] **Gong, Z., Ba, Y., Zhang, M., and Guo, Y.** (2022). "Robust sliding mode control of the permanent magnet synchronous motor with an improved power reaching law". Energies, 15(5):1935.
*Modern applications of adaptive reaching laws.*

---

**Document Classification**: Research-Grade Mathematical Theory
**Maintenance**: Update when new SMC variants are added
**Next Review**: 2025-11-04
**Version History**: v1.0 (2025-10-04) - Initial theory document
