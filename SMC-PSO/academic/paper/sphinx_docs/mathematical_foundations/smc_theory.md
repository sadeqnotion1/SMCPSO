# SMC Mathematical Theory Documentation

## Mathematical Foundations of Sliding Mode Control

### 1. Sliding Surface Design Theory

#### 1.1 Classical SMC Sliding Surface

The sliding surface for the double-inverted pendulum system is defined as:

```latex
σ = λ₁θ₁ + λ₂θ₂ + k₁θ̇₁ + k₂θ̇₂
```

where:
- `θ₁, θ₂`: pendulum angles
- `θ̇₁, θ̇₂`: pendulum angular velocities
- `λ₁, λ₂ > 0`: sliding surface slope parameters (must be strictly positive)
- `k₁, k₂ > 0`: velocity feedback gains (must be strictly positive)

**Mathematical Properties:**

1. **Hurwitz Stability Requirement**: The characteristic polynomial of the sliding dynamics must have all roots in the left half-plane:
   ```latex
   s² + k₁s + λ₁ = 0  (for pendulum 1)
   s² + k₂s + λ₂ = 0  (for pendulum 2)
   ```

2. **Positivity Constraints**: For asymptotic stability, we require:
   ```latex
   λ₁, λ₂ > 0  (slope parameters)
   k₁, k₂ > 0   (damping parameters)
   ```

#### 1.2 Super-Twisting Sliding Surface

For the Super-Twisting Algorithm (STA), the sliding surface combines position and velocity errors:

```latex
σ = k₁(θ̇₁ + λ₁θ₁) + k₂(θ̇₂ + λ₂θ₂)
```

**Convergence Properties:**
- Finite-time convergence to σ = 0
- Robustness against matched uncertainties
- Chattering reduction compared to classical SMC

### 2. Boundary Layer Theory

#### 2.1 Continuous Approximation of Sign Function

The discontinuous sign function is approximated within a boundary layer of width `ε > 0`:

**Linear Saturation:**
```latex
sat(σ/ε) = {
  σ/ε,     if |σ| ≤ ε
  sign(σ), if |σ| > ε
}
```

**Hyperbolic Tangent Approximation:**
```latex
sat(σ/ε) = tanh(σ/ε)
```

#### 2.2 Mathematical Properties of Boundary Layer

1. **Chattering Reduction**: The continuous approximation eliminates infinite switching frequency
2. **Steady-State Error**: A non-zero boundary layer introduces bounded tracking error
3. **Trade-off**: Smaller ε reduces steady-state error but increases chattering

**Boundary Layer Width Selection:**
```latex
ε = ε₀ + ε₁ ||σ||
```

where:
- `ε₀ > 0`: nominal boundary layer thickness
- `ε₁ ≥ 0`: adaptive scaling factor

### 3. Lyapunov Stability Analysis

#### 3.1 Classical SMC Lyapunov Function

Consider the Lyapunov candidate function:
```latex
V = ½σ²
```

**Stability Proof:**
```latex
V̇ = σσ̇ = σ[λ₁θ̇₁ + λ₂θ̇₂ + k₁θ̈₁ + k₂θ̈₂]
```

For the double-inverted pendulum dynamics:
```latex
V̇ = σ[L(M⁻¹(u + d) - M⁻¹(C(q,q̇)q̇ + G(q)))]
```

where `L = [0, k₁, k₂]` and `d` represents matched disturbances.

**Control Law Design:**
```latex
u = u_eq - K sign(σ)
```

where:
- `u_eq`: equivalent control to cancel known dynamics
- `K > ||d||_∞`: switching gain to dominate disturbances

**Convergence Condition:**
```latex
V̇ = σ(-K sign(σ) + d) ≤ -η|σ|
```

where `η = K - ||d||_∞ > 0`.

#### 3.2 Super-Twisting Lyapunov Analysis

For the super-twisting algorithm, consider the Lyapunov function:
```latex
V = k₁|σ|^(3/2) + ½z²
```

where `z` is the auxiliary variable.

**Finite-Time Convergence:**
Under appropriate gain selection (K₁, K₂ > 0), the system reaches σ = 0 in finite time.

### 4. Reachability Conditions

#### 4.1 Sliding Mode Reaching Condition

The fundamental reachability condition ensures the system state reaches the sliding surface:
```latex
σσ̇ < 0  whenever σ ≠ 0
```

#### 4.2 Equivalent Control Method

The equivalent control is derived by setting σ̇ = 0:
```latex
σ̇ = L(M⁻¹(u_eq - C(q,q̇)q̇ - G(q))) = 0
```

Solving for `u_eq`:
```latex
u_eq = (LM⁻¹B)⁻¹L(M⁻¹(C(q,q̇)q̇ + G(q)) - [k₁λ₁θ̇₁ + k₂λ₂θ̇₂])
```

**Controllability Condition:**
```latex
|LM⁻¹B| > ε_threshold
```

If this condition fails, the equivalent control computation becomes ill-conditioned.

### 5. Mathematical Failure Modes

#### 5.1 Boundary Layer Computation Failures

**Problem**: Division by zero when ε ≤ 0
**Solution**: Enforce strict positivity: ε > 0

**Problem**: Numerical instability for very small ε
**Solution**: Adaptive boundary layer with lower bound

#### 5.2 Equivalent Control Singularities

**Problem**: Matrix inversion failure when `det(M) ≈ 0`
**Solution**: Tikhonov regularization:
```latex
M_reg = M + αI, α > 0
```

**Problem**: Loss of controllability when `|LM⁻¹B| ≈ 0`
**Solution**: Controllability threshold check

#### 5.3 Gain Constraint Violations

**Mathematical Requirement**: All SMC gains must satisfy positivity constraints
**Implementation**: Use `require_positive()` validation in constructors

### 6. Convergence Analysis

#### 6.1 Classical SMC Exponential Convergence

On the sliding surface (σ = 0), the reduced-order dynamics are:
```latex
λ₁θ₁ + λ₂θ₂ + k₁θ̇₁ + k₂θ̇₂ = 0
```

This leads to exponential convergence with time constants determined by:
```latex
τ₁ = 2/k₁, τ₂ = 2/k₂  (for critically damped case when k₁² = 4λ₁, k₂² = 4λ₂)
```

#### 6.2 Super-Twisting Finite-Time Convergence

The super-twisting algorithm achieves finite-time convergence to σ = 0 under the gain conditions:
```latex
K₁ > 0, K₂ > 0
K₁ ≥ 4K₂L/(K₂ - L)  where L is the Lipschitz constant of disturbances
```

### 7. Implementation Validation Requirements

#### 7.1 Mathematical Property Tests

1. **Sliding Surface Computation**:
   - Verify linear combination properties
   - Test with known state vectors
   - Validate against analytical derivatives

2. **Boundary Layer Function**:
   - Test continuity at ±ε
   - Verify saturation properties
   - Check numerical stability

3. **Equivalent Control**:
   - Test matrix conditioning
   - Verify controllability thresholds
   - Validate against known dynamics

#### 7.2 Lyapunov Function Verification

Property-based tests should verify:
```latex
V(0) = 0                    (positive definiteness)
V(σ) > 0 for σ ≠ 0        (positive definiteness)
V̇(σ) < 0 for σ ≠ 0        (negative definiteness of derivative)
```

## References

1. Utkin, V.I. "Sliding Modes in Control and Optimization", Springer-Verlag, 1992
2. Edwards, C. and Spurgeon, S. "Sliding Mode Control: Theory and Applications", Taylor & Francis, 1998
3. Moreno, J.A. and Osorio, M. "Strict Lyapunov Functions for the Super-Twisting Algorithm", IEEE TAC, 2012
4. Levant, A. "Higher-order sliding modes, differentiation and output-feedback control", IJC, 2003