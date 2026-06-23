# Mathematical Notation Standards for DIP-SMC-PSO Documentation

This document provides standards and examples for mathematical notation in the DIP-SMC-PSO project documentation.

## 1. Unicode Mathematical Symbols

### 1.1 Greek Letters (Preferred)

- Use Unicode Greek letters: `θ₁, θ₂, λ₁, λ₂, ω, φ`
- Not ASCII approximations: `theta1, theta2, lambda1, lambda2`

### 1.2 Mathematical Operators

- Integral: `∫₀ᵀ` (not `integral from 0 to T`)
- Partial derivative: `∂f/∂x` (not `df/dx`)
- Nabla operator: `∇f` (not `grad f`)
- Summation: `∑ᵢ₌₁ⁿ` (not `sum from i=1 to n`)

### 1.3 Subscripts and Superscripts

- Position subscripts: `x₁, x₂, x₃`
- Time derivatives: `θ̇₁, θ̈₁` (preferred) or `θ₁_dot, θ₁_ddot`
- Powers: `x²` (preferred) or `x^2`

## 2. Control Theory Notation Standards

### 2.1 Sliding Mode Control

```python
# example-metadata:
# runnable: false

"""
Classical SMC sliding surface definition:

s = λ₁e₁ + λ₂e₂ + ė₁ + ė₂

where:
- e₁ = θ₁ - θ₁ᵈ (angular position error for pendulum 1)
- e₂ = θ₂ - θ₂ᵈ (angular position error for pendulum 2)
- ė₁ = θ̇₁ - θ̇₁ᵈ (angular velocity error for pendulum 1)
- ė₂ = θ̇₂ - θ̇₂ᵈ (angular velocity error for pendulum 2)
- λ₁, λ₂ > 0 (sliding surface gains for Hurwitz stability)

Stability Condition:
For exponential convergence to the sliding surface, require:
λ₁, λ₂ > 0 ensuring the characteristic polynomial s² + λ₂s + λ₁ = 0
has roots in the left half-plane.
"""
```

## 2.2 Lyapunov Function Documentation

```python
"""
Lyapunov stability analysis for SMC reaching condition:

V(s) = ½s²

Taking the time derivative along system trajectories:
V̇(s) = s·ṡ = s·(λ₁ė₁ + λ₂ė₂ + ë₁ + ë₂)

For the reaching condition V̇ < 0 when s ≠ 0, the switching gain K must satisfy:
K > |f_eq(x)| + δ

where f_eq is the equivalent control and δ > 0 accounts for uncertainties.
"""
```

### 2.3 Super-Twisting Algorithm

```python
# example-metadata:
# runnable: false

"""
Second-order sliding mode (Super-Twisting) control law:

u = u₁ + u₂

where:
u₁ = -α|s|^(1/2)sign(s)
u₂ = ∫₀ᵗ(-β sign(s))dτ

Parameters α, β > 0 must satisfy the convergence condition:
α > √(2L), β > α²/(2(α-√(2L)))

where L is the Lipschitz constant of the uncertainty.
"""
```

## 3. Optimization Theory Notation

### 3.1 PSO Dynamics

```python
# example-metadata:
# runnable: false

"""
Particle Swarm Optimization update equations:

vᵢᵗ⁺¹ = w·vᵢᵗ + c₁r₁(pᵢ - xᵢᵗ) + c₂r₂(g - xᵢᵗ)
xᵢᵗ⁺¹ = xᵢᵗ + vᵢᵗ⁺¹

where:
- xᵢᵗ ∈ ℝⁿ: position of particle i at iteration t
- vᵢᵗ ∈ ℝⁿ: velocity of particle i at iteration t
- pᵢ ∈ ℝⁿ: personal best position of particle i
- g ∈ ℝⁿ: global best position
- w ∈ [0,1]: inertia weight
- c₁, c₂ > 0: acceleration coefficients
- r₁, r₂ ~ U(0,1): random variables

Convergence requires: w < 1 and c₁ + c₂ < 4(1 + w)
"""
```

## 3.2 Cost Function Definition

```python
# example-metadata:
# runnable: false

"""
Multi-objective cost function for controller optimization:

J(k) = w₁·ISE(k) + w₂·ITAE(k) + w₃·U_max(k) + w₄·Penalty(k)

where:
- ISE(k) = ∫₀ᵀ ‖e(t,k)‖² dt (Integral Squared Error)
- ITAE(k) = ∫₀ᵀ t·‖e(t,k)‖₁ dt (Integral Time Absolute Error)
- U_max(k) = max_{t∈[0,T]} |u(t,k)| (Control effort penalty)
- Penalty(k): Instability penalty (→ ∞ if unstable)
- wᵢ ≥ 0: weighting factors with ∑wᵢ = 1
"""
```

## 4. Performance Metrics Notation

### 4.1 Standard Control Metrics

```python
# example-metadata:
# runnable: false

"""
Performance Metrics for Control Systems:

1. Integral Squared Error (ISE):
   ISE = ∫₀ᵀ ‖e(t)‖² dt

2. Integral Time Absolute Error (ITAE):
   ITAE = ∫₀ᵀ t·‖e(t)‖₁ dt

3. Integral Absolute Error (IAE):
   IAE = ∫₀ᵀ ‖e(t)‖₁ dt

4. Root Mean Square Error (RMSE):
   RMSE = √(1/T ∫₀ᵀ ‖e(t)‖² dt)

5. Maximum Overshoot:
   OS = max(x(t)) - x_final / x_final × 100%

6. Settling Time (2% criterion):
   t_s = inf{t > 0 : |x(τ) - x_final| ≤ 0.02|x_final| ∀τ ≥ t}
"""
```

## 5. Statistical Analysis Notation

### 5.1 Monte Carlo Validation

```python
# example-metadata:
# runnable: false

"""
Monte Carlo Uncertainty Quantification:

Given N independent samples {J₁, J₂, ..., Jₙ} of the cost function:

Sample Mean: μ̂ = 1/N ∑ᵢ₌₁ᴺ Jᵢ

Sample Variance: σ̂² = 1/(N-1) ∑ᵢ₌₁ᴺ (Jᵢ - μ̂)²

Confidence Interval (α = 0.05):
CI₀.₉₅ = μ̂ ± t_{N-1,α/2} · σ̂/√N

where t_{N-1,α/2} is the (1-α/2) quantile of the t-distribution with N-1 degrees of freedom.
"""
```

## 5.2 Hypothesis Testing

```python
# example-metadata:
# runnable: false

"""
Welch's t-test for comparing controller performance:

H₀: μ₁ = μ₂ (no difference in mean performance)
H₁: μ₁ ≠ μ₂ (significant difference in performance)

Test Statistic:
t = (x̄₁ - x̄₂) / √(s₁²/n₁ + s₂²/n₂)

Degrees of Freedom (Welch-Satterthwaite):
ν = (s₁²/n₁ + s₂²/n₂)² / ((s₁²/n₁)²/(n₁-1) + (s₂²/n₂)²/(n₂-1))

Reject H₀ if |t| > t_{ν,α/2} where α is the significance level.
"""
```

## 6. LaTeX Integration Guidelines

### 6.1 Sphinx Documentation

For Sphinx-generated documentation, use LaTeX math blocks:

```rst
.. math::
   s = \lambda_1 e_1 + \lambda_2 e_2 + \dot{e}_1 + \dot{e}_2

   \text{where } e_i = \theta_i - \theta_i^d
```

### 6.2 Jupyter Notebooks

For interactive documentation in notebooks:

```python
from IPython.display import Math, display

display(Math(r's = \lambda_1 e_1 + \lambda_2 e_2 + \dot{e}_1 + \dot{e}_2'))
```

## 7. Docstring Examples

### 7.1 Function Documentation with Math

```python
# example-metadata:
# runnable: false

def compute_sliding_surface(self, state: np.ndarray, target: np.ndarray) -> float:
    """Compute the sliding surface value for classical SMC.

    The sliding surface is defined as:
    s = λ₁e₁ + λ₂e₂ + ė₁ + ė₂

    where:
    - e₁, e₂: position errors for pendulum 1 and 2
    - ė₁, ė₂: velocity errors for pendulum 1 and 2
    - λ₁, λ₂: sliding surface gains (must be positive)

    Mathematical Background:
    The sliding surface design ensures that once the system reaches
    the surface (s=0), it will remain on the surface and converge
    to the desired equilibrium point in finite time.

    Parameters
    # ---------- (RST section marker)
    state : np.ndarray, shape (6,)
        Current system state [θ₁, θ₂, x, θ̇₁, θ̇₂, ẋ]
    target : np.ndarray, shape (6,)
        Target state (typically upright equilibrium [0, 0, 0, 0, 0, 0])

    Returns
    # ------- (RST section marker)
    float
        Sliding surface value. System is on sliding surface when s = 0.

    References
    # ---------- (RST section marker)
    .. [1] Utkin, V. "Sliding Modes in Control and Optimization", 1992
    .. [2] Edwards, C. "Sliding Mode Control: Theory and Applications", 1998
    """
```

### 7.2 Class Documentation with Theory

```python
# example-metadata:
# runnable: false

class ClassicalSMC:
    """Classical Sliding Mode Controller for double-inverted pendulum.

    Implements the classical SMC algorithm with boundary layer for chattering
    reduction. The control law consists of equivalent control and switching
    control components:

    u = u_eq + u_sw

    where:
    - u_eq: Equivalent control (model-based feedforward)
    - u_sw: Switching control (robust feedback)

    The sliding surface is designed as:
    s = λ₁e₁ + λ₂e₂ + ė₁ + ė₂

    Stability is guaranteed when λ₁, λ₂ > 0, ensuring the characteristic
    polynomial s² + λ₂s + λ₁ = 0 has stable roots.

    Parameters
    # ---------- (RST section marker)
    gains : List[float]
        Controller gains [k₁, k₂, λ₁, λ₂, K, k_d] where:
        - k₁, k₂: Position feedback gains
        - λ₁, λ₂: Sliding surface gains
        - K: Switching gain
        - k_d: Derivative gain
    max_force : float
        Maximum control force (saturation limit)
    boundary_layer : float
        Boundary layer thickness for chattering reduction

    Attributes
    # ---------- (RST section marker)
    n_gains : int
        Number of controller gains (6 for classical SMC)

    Examples
    # -------- (RST section marker)
    >>> controller = ClassicalSMC(
    ...     gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    ...     max_force=100.0,
    ...     boundary_layer=0.01
    ... )
    >>> state = np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.0])
    >>> result = controller.compute_control(state, None, {})
    >>> print(f"Control output: {result['u']:.4f}")
    """
```

## 8. Validation and Quality Assurance

### 8.1 Mathematical Accuracy Checklist

- [ ] All Greek letters use Unicode symbols
- [ ] Subscripts and superscripts properly formatted
- [ ] Mathematical operators use standard Unicode symbols
- [ ] Equations are mathematically correct and consistent
- [ ] Units are specified where applicable
- [ ] Stability conditions are properly documented
- [ ] References to literature are accurate

### 8.2 Documentation Review Process

1. **Technical Review**: Verify mathematical accuracy
2. **Consistency Check**: Ensure notation consistency across modules
3. **Literature Validation**: Verify references and citations
4. **User Testing**: Validate documentation clarity with target audience
5. **Rendering Verification**: Check mathematical notation displays correctly

This standard ensures consistent, professional mathematical documentation throughout the DIP-SMC-PSO project.