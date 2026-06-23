# Mathematical Foundations for Controller Factory Integration ## Overview This document provides mathematical foundations for the controller factory integration, focusing on the theoretical underpinnings of sliding mode control (SMC) algorithms, stability analysis, and optimization integration. The mathematical framework ensures that all factory-created controllers satisfy fundamental control theory requirements. ## Table of Contents 1. [Classical SMC Mathematical Framework](#classical-smc-mathematical-framework)

2. [Super-Twisting SMC Theory](#super-twisting-smc-theory)
3. [Adaptive SMC Mathematical Foundations](#adaptive-smc-mathematical-foundations)
4. [Hybrid SMC Integration Theory](#hybrid-smc-integration-theory)
5. [Stability Analysis Framework](#stability-analysis-framework)
6. [PSO Optimization Mathematical Framework](#pso-optimization-mathematical-framework)
7. [Numerical Analysis and Implementation](#numerical-analysis-and-implementation)

---

## Classical SMC Mathematical Framework ### System Model Consider the double-inverted pendulum system with state vector:

```latex
\mathbf{x} = [θ₁, θ₂, x, \dot{θ}₁, \dot{θ}₂, \dot{x}]^T ∈ \mathbb{R}^6
``` The nonlinear dynamics can be expressed in control-affine form:

```latex
\dot{\mathbf{x}} = f(\mathbf{x}) + g(\mathbf{x})u + d(\mathbf{x}, t)
``` where:

- f(x): drift dynamics vector field
- g(x): control effectiveness vector
- u: scalar control input (cart force)
- d(x,t): bounded disturbances ### Sliding Surface Design The sliding surface for classical SMC is designed as:
```latex
s = \mathbf{c}^T \mathbf{e} + \boldsymbol{\lambda}^T \dot{\mathbf{e}}
``` where:

- e = x - x_ref: tracking error vector
- c = [c₁, c₂]: position gain vector
- λ = [λ₁, λ₂]: velocity gain vector **Expanded Form:**
```latex
s = c₁e₁ + λ₁\dot{e}₁ + c₂e₂ + λ₂\dot{e}₂
``` where:

- e₁ = θ₁ - θ₁ᵣₑf: pendulum 1 position error
- e₂ = θ₂ - θ₂ᵣₑf: pendulum 2 position error ### Stability Conditions **Hurwitz Stability Requirement:**
The surface gains must satisfy the Hurwitz condition for the characteristic polynomial:
```latex
p(s) = s² + λᵢs + cᵢ, \quad i ∈ {1,2}
``` This requires:

```latex
cᵢ > 0, \quad λᵢ > 0, \quad \forall i ∈ {1,2}
``` **Reaching Condition:**

The reaching condition ensures finite-time convergence to the sliding surface:
```latex
s \cdot \dot{s} ≤ -η|s|, \quad η > 0
``` ### Control Law Design The classical SMC control law consists of equivalent and switching components:

```latex
u = u_{eq} + u_{sw}
``` **Equivalent Control:**

```latex
u_{eq} = -\frac{(\nabla s)^T f(\mathbf{x})}{(\nabla s)^T g(\mathbf{x})}
``` **Switching Control:**

```latex
u_{sw} = -K \cdot \text{sat}(s/\phi)
``` where:

- K: switching gain
- φ: boundary layer thickness
- sat(·): saturation function to reduce chattering ### Factory Implementation Validation The factory validates the following mathematical constraints: ```python
# example-metadata:

# runnable: false def validate_classical_smc_gains(gains): """Validate Classical SMC gains against mathematical requirements.""" c1, c2, lam1, lam2, K, kd = gains # Hurwitz stability conditions assert c1 > 0, "Surface gain c1 must be positive for Hurwitz stability" assert c2 > 0, "Surface gain c2 must be positive for Hurwitz stability" assert lam1 > 0, "Velocity gain λ1 must be positive for Hurwitz stability" assert lam2 > 0, "Velocity gain λ2 must be positive for Hurwitz stability" # Switching gain positivity assert K > 0, "Switching gain K must be positive for reaching condition" # Derivative gain non-negativity assert kd >= 0, "Derivative gain kd must be non-negative" # Numerical stability bounds assert all(1e-12 <= g <= 1e5 for g in gains[:5]), "Gains must be in numerically stable range"

```

---

## Super-Twisting SMC Theory ### Second-Order Sliding Mode Concept Super-Twisting SMC achieves finite-time convergence by utilizing second-order sliding mode dynamics:
```latex

s = 0, \quad \dot{s} = 0
``` ### Control Algorithm The Super-Twisting algorithm is given by:
```latex

u = -K₁|s|^{1/2}\text{sign}(s) + v
```
```latex

\dot{v} = -K₂\text{sign}(s)
``` where:
- K₁: first-order gain
- K₂: second-order gain
- v: auxiliary variable ### Finite-Time Stability Conditions **Lyapunov Function:**
Consider the Lyapunov function:
```latex

V = ζ^T P ζ
``` where ζ = [|s|^{1/2}sign(s), v]^T and P is a positive definite matrix. **Stability Requirements:**
For finite-time stability, the gains must satisfy:
```latex

K₁ > K₂ > 0
```
```latex

K₁² > 2α
``` where α is the Lipschitz constant of the uncertainty. **Convergence Time:**
The finite-time convergence is achieved in:
```latex

T_{conv} ≤ \frac{2V^{1/2}(0)}{k_{min}}
``` where k_min is the minimum eigenvalue of the stability matrix. ### Factory Validation for Super-Twisting ```python
# example-metadata:
# runnable: false def validate_super_twisting_gains(gains): """Validate Super-Twisting SMC gains for finite-time stability.""" K1, K2, c1, lam1, c2, lam2 = gains # Finite-time stability condition assert K1 > K2 > 0, "Must have K1 > K2 > 0 for finite-time stability" # Sufficient condition for robust finite-time stability # Assumes worst-case Lipschitz constant α = 1.0 assert K1**2 > 2.0, "K1² > 2α required for robust finite-time convergence" # Surface design validation (same as classical) assert c1 > 0 and c2 > 0, "Surface position gains must be positive" assert lam1 > 0 and lam2 > 0, "Surface velocity gains must be positive"
```

---

## Adaptive SMC Mathematical Foundations ### Parameter Estimation Theory Adaptive SMC addresses parametric uncertainties through online parameter estimation:

```latex
\dot{\mathbf{x}} = f(\mathbf{x}, \boldsymbol{\theta}) + g(\mathbf{x})u + d(\mathbf{x}, t)
``` where θ represents unknown parameters. ### Adaptation Law The parameter update law follows the gradient descent principle:

```latex
\dot{\hat{\boldsymbol{\theta}}} = -\boldsymbol{\Gamma} \frac{\partial V}{\partial \boldsymbol{\theta}}
``` where:

- θ̂: parameter estimates
- Γ: adaptation gain matrix
- V: Lyapunov function ### Adaptive Control Law The adaptive control consists of:
```latex
u = u_{eq}(\mathbf{x}, \hat{\boldsymbol{\theta}}) - K(\hat{\boldsymbol{\theta}}) \cdot \text{sign}(s)
``` ### Lyapunov Stability Analysis **Composite Lyapunov Function:**

```latex
V = \frac{1}{2}s² + \frac{1}{2}\tilde{\boldsymbol{\theta}}^T \boldsymbol{\Gamma}^{-1} \tilde{\boldsymbol{\theta}}
``` where θ̃ = θ̂ - θ represents parameter estimation error. **Stability Condition:**

```latex
\dot{V} = s\dot{s} + \tilde{\boldsymbol{\theta}}^T \boldsymbol{\Gamma}^{-1} \dot{\tilde{\boldsymbol{\theta}}} ≤ 0
``` ### Adaptation Bounds To ensure bounded parameter estimates:

```latex
\hat{\theta}_i(t) = \text{proj}[\hat{\theta}_{i,min}, \hat{\theta}_{i,max}](\hat{\theta}_i^*)
``` where proj[·] denotes projection onto the feasible parameter space. ### Factory Implementation for Adaptive SMC ```python
# example-metadata:

# runnable: false def validate_adaptive_smc_parameters(config): """Validate adaptive SMC parameters for stability.""" # Surface gains validation validate_surface_gains(config.gains[:4]) # Adaptation rate validation gamma = config.gains[4] # Adaptation rate assert 0 < gamma < 10.0, "Adaptation rate must be in (0, 10) for stability" # Parameter bounds validation assert hasattr(config, 'K_min') and hasattr(config, 'K_max') assert 0 < config.K_min < config.K_max, "Parameter bounds must satisfy 0 < K_min < K_max" # Dead zone validation assert config.dead_zone > 0, "Dead zone must be positive to prevent parameter drift"

```

---

## Hybrid SMC Integration Theory ### Multi-Mode Control Architecture Hybrid SMC combines multiple control strategies with switching logic:
```latex

u = \begin{cases}
u_{classical}(\mathbf{x}) & \text{if } \sigma(\mathbf{x}) ∈ \mathcal{R}_{classical} \\
u_{adaptive}(\mathbf{x}, \hat{\boldsymbol{\theta}}) & \text{if } \sigma(\mathbf{x}) ∈ \mathcal{R}_{adaptive} \\
u_{STA}(\mathbf{x}) & \text{if } \sigma(\mathbf{x}) ∈ \mathcal{R}_{STA}
\end{cases}
``` where σ(x) is the switching criterion and ℝ_i are the operating regions. ### Switching Logic Design The switching criterion is based on system performance metrics:
```latex

\sigma(\mathbf{x}) = \begin{bmatrix}
|s| \\
|\dot{s}| \\
\|\mathbf{e}\| \\
\text{adaptation\_confidence}
\end{bmatrix}
``` ### Stability Under Switching **Common Lyapunov Function Approach:**
Find V(x) such that for all subsystems i:
```latex

\frac{\partial V}{\partial \mathbf{x}} [f_i(\mathbf{x}) + g_i(\mathbf{x})u_i] < 0
``` **Dwell Time Condition:**
Ensure minimum dwell time τ_d between switches:
```latex

t_{k+1} - t_k ≥ τ_d > 0
``` ### Factory Validation for Hybrid Controllers ```python
# example-metadata:
# runnable: false def validate_hybrid_smc_configuration(config): """Validate hybrid SMC configuration for stability.""" # Validate sub-controller configurations assert hasattr(config, 'classical_config'), "Hybrid SMC requires classical sub-config" assert hasattr(config, 'adaptive_config'), "Hybrid SMC requires adaptive sub-config" validate_classical_smc_gains(config.classical_config.gains) validate_adaptive_smc_parameters(config.adaptive_config) # Validate switching logic parameters assert hasattr(config, 'hybrid_mode'), "Hybrid mode must be specified" assert config.dt > 0, "Timestep must be positive for switching logic" # Ensure dwell time constraint min_dwell_time = 0.001 # 1ms minimum assert config.dt >= min_dwell_time, f"Timestep must be ≥ {min_dwell_time}s for stability"
```

---

## Stability Analysis Framework ### Universal Lyapunov Analysis For all SMC variants, we use a unified Lyapunov framework: **General Lyapunov Function:**

```latex
V(\mathbf{x}, t) = V_s(s) + V_p(\tilde{\boldsymbol{\theta}}) + V_a(\mathbf{x}_a)
``` where:

- V_s(s): sliding surface component
- V_p(θ̃): parameter estimation component
- V_a(x_a): auxiliary state component ### Stability Certificates The factory generates stability certificates for each created controller: ```python
# example-metadata:

# runnable: false class StabilityCertificate: """Mathematical stability certificate for factory-created controllers.""" def __init__(self, controller_type: str, gains: List[float]): self.controller_type = controller_type self.gains = gains self.validation_results = {} def validate_hurwitz_conditions(self) -> bool: """Validate Hurwitz stability of surface design.""" if self.controller_type == 'classical_smc': c1, c2, lam1, lam2 = self.gains[:4] # Check characteristic polynomial: s² + λs + c return all(c > 0 for c in [c1, c2]) and all(lam > 0 for lam in [lam1, lam2]) def validate_reaching_conditions(self) -> bool: """Validate reaching condition satisfaction.""" # Implementation depends on controller type return self._controller_specific_reaching_validation() def compute_convergence_bounds(self) -> Dict[str, float]: """Compute theoretical convergence time bounds.""" bounds = {} if self.controller_type == 'classical_smc': # Classical SMC: exponential convergence lam_min = min(self.gains[2], self.gains[3]) # min(λ1, λ2) bounds['exponential_rate'] = lam_min bounds['settling_time_bound'] = 4.6 / lam_min # 1% criterion elif self.controller_type == 'sta_smc': # Super-Twisting: finite-time convergence K1, K2 = self.gains[0], self.gains[1] if K1 > K2 > 0: bounds['finite_time'] = True bounds['convergence_exponent'] = 0.5 return bounds

``` ### Robustness Analysis **Structured Uncertainty Model:**
```latex

\Delta f(\mathbf{x}) = \sum_{i=1}^{n} δ_i \phi_i(\mathbf{x})
```

where δ_i are uncertainty parameters and φ_i(x) are basis functions.

**Robust Stability Condition:**
```latex

\|(\mathbf{I} + \boldsymbol{\Delta})\| < \frac{1}{\gamma}
```

where γ is the robustness margin.

```python
# example-metadata:

# runnable: false

def compute_robustness_margin(controller, uncertainty_model):
    """Compute robustness margin for controller."""

    # Sample operating points
    test_points = generate_test_points() min_margin = float('inf') for x in test_points: # Compute local linearization A, B = linearize_dynamics(x) # Compute controller gain matrix K = compute_controller_gain_matrix(controller, x) # Closed-loop system A_cl = A + B @ K # Compute structured singular value mu = compute_structured_singular_value(A_cl, uncertainty_model) margin = 1.0 / mu if mu > 0 else float('inf') min_margin = min(min_margin, margin) return min_margin
```

---

## PSO Optimization Mathematical Framework ### Objective Function Design The PSO optimization seeks to minimize a cost function J(θ) where θ represents controller gains: ```latex
J(\boldsymbol{\theta}) = \int_0^{T} L(\mathbf{x}(t), u(t, \boldsymbol{\theta})) dt
``` **Typical Cost Function:**

```latex
L(\mathbf{x}, u) = \mathbf{x}^T \mathbf{Q} \mathbf{x} + u^T R u + \rho \Phi(\mathbf{x})
``` where:

- Q: state penalty matrix
- R: control penalty matrix
- ρ: constraint penalty weight
- Φ(x): constraint violation function ### PSO Algorithm Mathematics **Particle Dynamics:**
```latex
v_{i,j}^{(k+1)} = w v_{i,j}^{(k)} + c_1 r_1 (p_{i,j}^{(k)} - x_{i,j}^{(k)}) + c_2 r_2 (g_j^{(k)} - x_{i,j}^{(k)})
```

```latex
x_{i,j}^{(k+1)} = x_{i,j}^{(k)} + v_{i,j}^{(k+1)}
``` where:

- v_{i,j}: velocity of particle i, dimension j
- x_{i,j}: position of particle i, dimension j
- p_{i,j}: personal best position
- g_j: global best position
- w: inertia weight
- c₁, c₂: acceleration coefficients
- r₁, r₂: random numbers ∈ [0,1] ### Convergence Analysis **Convergence Condition:**
PSO converges when:
```latex
\lim_{k \to \infty} \|\mathbf{v}^{(k)}\| = 0
``` **Stability Analysis:**

The PSO particle dynamics can be analyzed as a discrete-time system:
```latex
\mathbf{z}^{(k+1)} = \mathbf{A} \mathbf{z}^{(k)} + \mathbf{B} \boldsymbol{\xi}^{(k)}
``` where z = [x, v]^T and ξ represents the stochastic terms. ### Constraint Handling **Gain Bounds:**

```latex
\boldsymbol{\theta}_{min} ≤ \boldsymbol{\theta} ≤ \boldsymbol{\theta}_{max}
``` **Stability Constraints:**

```latex
g_i(\boldsymbol{\theta}) ≤ 0, \quad i = 1, ..., n_c
``` where g_i represent stability constraints (e.g., Hurwitz conditions). ### Factory-PSO Integration ```python
# example-metadata:

# runnable: false class PSOOptimizedFactory: """Factory with integrated PSO optimization.""" def __init__(self, controller_type: str): self.controller_type = controller_type self.bounds = self._get_theoretical_bounds() def _get_theoretical_bounds(self) -> Tuple[List[float], List[float]]: """Get theoretically motivated gain bounds.""" if self.controller_type == 'classical_smc': # Based on pole placement and bandwidth requirements lower = [0.1, 0.1, 0.1, 0.1, 1.0, 0.0] # [c1, c2, λ1, λ2, K, kd] upper = [50.0, 50.0, 50.0, 50.0, 200.0, 50.0] elif self.controller_type == 'sta_smc': # Based on finite-time convergence requirements lower = [1.0, 0.5, 0.1, 0.1, 0.1, 0.1] # [K1, K2, c1, λ1, c2, λ2] upper = [100.0, 99.0, 50.0, 50.0, 50.0, 50.0] # Ensure K1 > K2 return lower, upper def optimize_gains(self, plant_model, cost_function, n_particles=30, n_iterations=100): """Optimize controller gains using PSO.""" # Initialize PSO with theoretical bounds pso = PSOOptimizer( bounds=self.bounds, n_particles=n_particles, n_iterations=n_iterations ) # Define fitness function def fitness(gains): try: # Create controller with gains controller = create_controller(self.controller_type, gains=gains) # Validate stability before simulation if not self._validate_stability(gains): return float('inf') # Simulate and compute cost cost = simulate_and_evaluate(controller, plant_model, cost_function) return cost except Exception: return float('inf') # Run optimization optimal_gains, optimal_cost = pso.optimize(fitness) return optimal_gains, optimal_cost

```

---

## Numerical Analysis and Implementation ### Numerical Stability Considerations **Conditioning of Control Computation:**
The condition number of the control matrix affects numerical stability:
```latex

\kappa(\mathbf{G}) = \|\mathbf{G}\| \|\mathbf{G}^{-1}\|
``` For well-conditioned control:
```latex

\kappa(\mathbf{G}) < 10^{12}
``` ### Discretization Effects **Euler Integration:**
```latex

\mathbf{x}_{k+1} = \mathbf{x}_k + h \cdot f(\mathbf{x}_k, u_k)
``` **Stability Constraint:**
For numerical stability of discrete-time SMC:
```latex

h < \frac{2}{|\lambda_{max}|}
``` where λ_max is the maximum eigenvalue of the linearized system. ### Implementation Validation ```python
# example-metadata:
# runnable: false def validate_numerical_implementation(controller, test_conditions): """Validate numerical properties of controller implementation.""" results = { 'conditioning': [], 'numerical_drift': [], 'conservation_properties': [] } for condition in test_conditions: # Test condition number condition_number = compute_control_conditioning(controller, condition) results['conditioning'].append(condition_number) # Test for numerical drift drift = simulate_long_term_stability(controller, condition) results['numerical_drift'].append(drift) # Test conservation properties (energy, momentum) conservation = check_conservation_properties(controller, condition) results['conservation_properties'].append(conservation) # Validation criteria assert max(results['conditioning']) < 1e12, "Poor numerical conditioning detected" assert max(results['numerical_drift']) < 1e-6, "Numerical drift exceeds tolerance" return results
``` ### Verification and Validation Framework **Formal Verification:**

The factory implements formal verification of mathematical properties: ```python
# example-metadata:

# runnable: false def formal_verification_suite(controller_type, gains): """Formal verification of mathematical properties.""" verification_results = { 'stability_verified': False, 'convergence_verified': False, 'robustness_verified': False, 'implementation_verified': False } # Stability verification try: stability_certificate = verify_lyapunov_stability(controller_type, gains) verification_results['stability_verified'] = stability_certificate.is_valid() except Exception as e: logger.warning(f"Stability verification failed: {e}") # Convergence verification try: convergence_proof = verify_convergence_properties(controller_type, gains) verification_results['convergence_verified'] = convergence_proof.is_valid() except Exception as e: logger.warning(f"Convergence verification failed: {e}") # Robustness verification try: robustness_analysis = verify_robustness_margins(controller_type, gains) verification_results['robustness_verified'] = robustness_analysis.is_sufficient() except Exception as e: logger.warning(f"Robustness verification failed: {e}") return verification_results

```

---

## Conclusion The mathematical foundations presented in this document provide the theoretical framework for ensuring that all factory-created controllers satisfy fundamental control theory requirements. The integration of formal stability analysis, convergence verification, and numerical validation ensures that the controller factory produces mathematically sound and practically implementable control systems. The framework supports: 1. **Rigorous stability analysis** for all SMC variants
2. **Convergence verification** with quantitative bounds
3. **Robustness analysis** under structured uncertainties
4. **PSO optimization** with theoretical gain bounds
5. **Numerical validation** for implementation reliability This mathematical foundation ensures that the controller factory integration maintains the highest standards of control theory while providing practical, high-performance implementations for the double-inverted pendulum system.