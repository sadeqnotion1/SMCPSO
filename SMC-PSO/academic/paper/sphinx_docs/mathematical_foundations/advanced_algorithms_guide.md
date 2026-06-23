# Advanced Algorithms Guide **Technical Reference for Optimization, Numerical Stability, and Algorithm Comparison**

## Table of Contents 1. [Introduction](#introduction)

2. [Particle Swarm Optimization](#particle-swarm-optimization)
3. [Super-Twisting Algorithm](#super-twisting-algorithm)
4. [Numerical Stability Algorithms](#numerical-stability-algorithms)
5. [Algorithm Comparison Framework](#algorithm-comparison-framework)
6. [Performance Optimization Techniques](#performance-optimization-techniques)
7. [Advanced Topics](#advanced-topics)
8. [Best Practices](#best-practices)

---

## Introduction This guide provides technical documentation for the advanced algorithms implemented in the DIP-SMC-PSO project. These algorithms form the computational backbone of the system, enabling robust control, efficient optimization, and numerical stability.

### Algorithm Categories

**Optimization Algorithms:**
- Particle Swarm Optimization (PSO) with advanced features
- Genetic Algorithm (GA) comparison framework
- Differential Evolution (DE) comparison framework **Control Algorithms:**
- Super-Twisting Algorithm (STA) for second-order sliding mode
- Finite-time convergence techniques
- Chattering reduction methods **Numerical Algorithms:**
- Safe mathematical operations with IEEE 754 compliance
- Adaptive regularization for ill-conditioned systems
- Overflow/underflow protection **Benchmarking Algorithms:**
- Standard test functions (Sphere, Rosenbrock, Rastrigin, Ackley)
- Statistical significance testing
- Convergence analysis frameworks ### Implementation Philosophy All algorithms follow production-grade design principles: 1. **Numerical Stability:** Epsilon thresholds protect against division by zero, overflow, and underflow
2. **Reproducibility:** Explicit PRNG seeding for deterministic results
3. **Vectorization:** NumPy-based batch operations for high throughput
4. **Theoretical Grounding:** Each algorithm includes mathematical proofs and stability guarantees
5. **Testing:** Unit tests, property-based tests, and scientific validation

---

## Particle Swarm Optimization ### Mathematical Foundation Particle Swarm Optimization (PSO) is a population-based metaheuristic inspired by social behavior of bird flocking and fish schooling. #### Core PSO Dynamics Each particle $i$ in the swarm has:

- **Position:** $\mathbf{x}_i^{(t)} \in \mathbb{R}^D$ (candidate solution)
- **Velocity:** $\mathbf{v}_i^{(t)} \in \mathbb{R}^D$ (search direction and magnitude)
- **Personal best:** $\mathbf{p}_i$ (best position found by particle $i$)
- **Global best:** $\mathbf{g}$ (best position found by entire swarm) **Update Equations:** $$
\mathbf{v}_i^{(t+1)} = w \mathbf{v}_i^{(t)} + c_1 r_1 \odot (\mathbf{p}_i - \mathbf{x}_i^{(t)}) + c_2 r_2 \odot (\mathbf{g} - \mathbf{x}_i^{(t)})
$$ $$
\mathbf{x}_i^{(t+1)} = \mathbf{x}_i^{(t)} + \mathbf{v}_i^{(t+1)}
$$ where:
- $w \in [0.4, 0.9]$ is the inertia weight (exploration vs exploitation)
- $c_1, c_2 \approx 2.0$ are cognitive and social acceleration coefficients
- $r_1, r_2 \sim U(0,1)$ are random vectors (element-wise)
- $\odot$ denotes element-wise multiplication #### Convergence Theory **Constriction Factor Analysis (Clerc & Kennedy, 2002):** For convergence, the constriction coefficient $\chi$ is defined as: $$
\chi = \frac{2}{\left| 2 - \varphi - \sqrt{\varphi^2 - 4\varphi} \right|}
$$ where $\varphi = c_1 + c_2 > 4$. **Standard configuration:** $c_1 = c_2 = 2.05$, yielding $\chi \approx 0.729$ This ensures:
1. **Bounded oscillation** around personal and global bests
2. **Guaranteed convergence** to a point (not necessarily global optimum)
3. **No velocity divergence** with proper parameter selection ### Implementation: PSOTuner Class #### Architecture Overview Located in `src/optimization/algorithms/pso_optimizer.py`, the `PSOTuner` class provides: 1. **Decoupled state management** - No global variable mutations
2. **Explicit PRNG control** - Reproducible optimization with seed management
3. **Vectorized fitness evaluation** - Batch simulation of entire swarm
4. **Dynamic penalties** - Instability detection and graded penalties
5. **Uncertainty-aware optimization** - Robust optimization under parameter perturbations #### Key Features **1. Velocity Clamping** Prevents particles from overshooting search space: $$
\mathbf{v}_i^{(t+1)} = \text{clip}\left(\mathbf{v}_i^{(t+1)}, \delta_{\min} \Delta\mathbf{b}, \delta_{\max} \Delta\mathbf{b}\right)
$$ where $\Delta\mathbf{b} = \mathbf{b}_{\max} - \mathbf{b}_{\min}$ is the search range. Default: $\delta_{\min} = -0.5$, $\delta_{\max} = 0.5$ **2. Inertia Weight Scheduling** Linearly decreasing inertia promotes exploration → exploitation transition: $$
w(t) = w_{\text{start}} - \frac{t}{T} (w_{\text{start}} - w_{\text{end}})
$$ Default schedule: $w: 0.9 \rightarrow 0.4$ over $T$ iterations **3. Instability Penalties** Graded penalty for early trajectory failure: $$
P_{\text{instability}} = w_{\text{stab}} \cdot \frac{T - t_{\text{fail}}}{T} \cdot P_{\text{max}}
$$ where:
- $t_{\text{fail}}$ is the time of first instability detection
- $P_{\text{max}} = 100 \times (\text{norm}_{\text{ISE}} + \text{norm}_u + \text{norm}_{\Delta u} + \text{norm}_\sigma)$ This encourages particles to maintain stability for longer durations. **4. Cost Normalization** Prevents scale imbalance between cost components: $$
J = w_{\text{ISE}} \cdot \frac{\text{ISE}}{\text{norm}_{\text{ISE}}} + w_u \cdot \frac{U^2}{\text{norm}_u} + w_{\Delta u} \cdot \frac{(\Delta U)^2}{\text{norm}_{\Delta u}} + w_\sigma \cdot \frac{\sigma^2}{\text{norm}_\sigma}
$$ Normalization constants are automatically computed from baseline controller performance. **5. Uncertainty Evaluation** Robust optimization under physics parameter uncertainty: $$
J_{\text{robust}}(\mathbf{x}) = w_{\text{mean}} \cdot \frac{1}{N} \sum_{i=1}^N J(\mathbf{x}, \theta_i) + w_{\text{max}} \cdot \max_{i=1}^N J(\mathbf{x}, \theta_i)
$$ where $\theta_i$ are perturbed physics parameters sampled from: $$
\theta_i \sim \mathcal{U}(\theta_{\text{nominal}} - \delta\%, \theta_{\text{nominal}} + \delta\%)
$$ Default: $\delta = 10\%$, $N = 5$ evaluations ### Usage Examples #### Basic PSO Optimization ```python
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.controllers.factory import create_controller
from src.config import load_config # Load configuration
config = load_config("config.yaml") # Define controller factory
def controller_factory(gains): return create_controller( 'classical_smc', config=config, gains=gains ) # Initialize PSO tuner
tuner = PSOTuner( controller_factory=controller_factory, config=config, seed=42, # Reproducible results instability_penalty_factor=100.0
) # Run optimization
result = tuner.optimise( iters_override=100, # 100 PSO iterations n_particles_override=30, # 30 particles options_override={ 'w': 0.7, # Constant inertia 'c1': 2.05, # Cognitive coefficient 'c2': 2.05 # Social coefficient }
) # Extract results
best_gains = result['best_pos']
best_cost = result['best_cost']
convergence_history = result['history']['cost'] print(f"Optimal gains: {best_gains}")
print(f"Final cost: {best_cost:.6f}")
``` #### PSO with Inertia Scheduling ```python
# Configure inertia weight schedule in config.yaml:
# pso:
# w_schedule: [0.9, 0.4] # Start at 0.9, end at 0.4
# iters: 100
# n_particles: 30 result = tuner.optimise() # Uses w_schedule from config # Manual iteration loop for custom control
from pyswarms.single import GlobalBestPSO # Create optimizer
optimizer = GlobalBestPSO( n_particles=30, dimensions=6, options={'c1': 2.05, 'c2': 2.05, 'w': 0.9}, bounds=(np.array([0.1]*6), np.array([50.0]*6))
) # Inertia schedule
w_values = np.linspace(0.9, 0.4, 100) for iteration, w_val in enumerate(w_values): optimizer.options['w'] = w_val step_cost, step_pos = optimizer.step(tuner._fitness) print(f"Iteration {iteration}: w={w_val:.3f}, cost={step_cost:.6f}")
``` #### Uncertainty-Aware Optimization ```python
# example-metadata:

# runnable: false # Configure physics uncertainty in config.yaml:

# physics_uncertainty:

# n_evals: 5 # 5 perturbed models per evaluation

# cart_mass: 0.10 # ±10%

# pendulum1_mass: 0.15 # ±15%

# pendulum2_mass: 0.15 # ±15%

# pendulum1_length: 0.05 # ±5%

# pendulum2_length: 0.05 # ±5% tuner = PSOTuner( controller_factory=controller_factory, config=config, seed=42

) # PSO will automatically evaluate robustness across perturbed models
result = tuner.optimise() # Each fitness evaluation runs 5 simulations (1 nominal + 4 perturbed)
# Cost aggregation: 0.7 * mean + 0.3 * max

``` ### PSO Hyperparameter Tuning #### Recommended Ranges | Parameter | Symbol | Recommended Range | Default | Notes |
|-----------|--------|-------------------|---------|-------|
| Swarm size | $N$ | $[10, 50]$ | 30 | Larger swarms for high-dimensional problems |
| Iterations | $T$ | $[50, 200]$ | 100 | Budget vs convergence trade-off |
| Inertia weight | $w$ | $[0.4, 0.9]$ | 0.7 | Lower for exploitation, higher for exploration |
| Cognitive coeff | $c_1$ | $[1.5, 2.5]$ | 2.05 | Balance with $c_2$ |
| Social coeff | $c_2$ | $[1.5, 2.5]$ | 2.05 | $c_1 \approx c_2$ recommended |
| Velocity clamp | $\delta$ | $[-0.5, 0.5]$ | $[-0.5, 0.5]$ | Fraction of search range | #### Sensitivity Analysis **Impact of swarm size:**
- **Small swarms (10-15):** Fast convergence, risk of premature convergence
- **Medium swarms (20-30):** Balanced exploration/exploitation
- **Large swarms (40-50):** Better global search, slower convergence **Impact of inertia weight:**
- **High inertia (0.9):** Global exploration, slower convergence
- **Medium inertia (0.7):** Balanced search
- **Low inertia (0.4):** Local exploitation, faster convergence **Recommended strategy:** Use inertia scheduling $w: 0.9 \rightarrow 0.4$ ### Performance Characteristics #### Computational Complexity **Per-iteration cost:**
$$
\mathcal{O}(N \cdot D \cdot C_{\text{eval}})
$$ where:
- $N$ = swarm size
- $D$ = problem dimensionality
- $C_{\text{eval}}$ = fitness evaluation cost **For DIP-SMC tuning:**
- $N = 30$ particles
- $D = 6$ gains (classical SMC)
- $C_{\text{eval}} \approx 50$ ms (vectorized simulation)
- **Per-iteration:** ~1.5 seconds
- **100 iterations:** ~2.5 minutes #### Vectorization Benefits The `PSOTuner` implementation uses `simulate_system_batch()` to evaluate all particles simultaneously: ```python
# example-metadata:
# runnable: false # Vectorized evaluation (FAST)
t, x_b, u_b, sigma_b = simulate_system_batch( controller_factory=controller_factory, particles=particles, # Shape: (N, D) sim_time=T, dt=dt, u_max=u_max
)
# Returns: x_b.shape = (N, timesteps, 6) # Cost computation on entire batch
costs = self._compute_cost_from_traj(t, x_b, u_b, sigma_b)
# Returns: costs.shape = (N,)
``` **Speedup vs sequential:** ~20-30x for typical swarm sizes

---

## Super-Twisting Algorithm ### Mathematical Foundation The Super-Twisting Algorithm (STA) is a second-order sliding mode control technique that achieves finite-time convergence while reducing chattering. #### Control Law Structure The STA consists of two components: $$

u = u_1 + u_2
$$ **Continuous component:**
$$
u_1 = -K_1 |s|^\alpha \text{sign}(s)
$$ **Integral component:**
$$
u_2 = -K_2 \int \text{sign}(s) \, dt
$$ where:
- $s$ is the sliding surface
- $K_1, K_2 > 0$ are twisting gains with $K_1 > K_2$
- $\alpha \in (0, 1]$ is the power exponent (standard: $\alpha = 0.5$) #### Finite-Time Convergence **Lyapunov Function:** $$
V(s, \dot{s}) = K_2 |s| + \frac{1}{2}\left(u_2 + K_1 |s|^\alpha \text{sign}(s)\right)^2
$$ **Stability Condition:** If $K_1 > K_2 > 0$ and the disturbance bound is known, the STA drives $s \rightarrow 0$ and $\dot{s} \rightarrow 0$ in finite time. **Convergence Time Estimate:** For $\alpha = 0.5$:
$$
T_{\text{conv}} \approx \frac{2\sqrt{|s_0|}}{\sqrt{K_2}}
$$ For general $\alpha$:
$$
T_{\text{conv}} \approx \frac{(1-\alpha) |s_0|^{1-\alpha}}{K_2^\alpha}
$$ ### Implementation: SuperTwistingAlgorithm Class Located in `src/controllers/smc/algorithms/super_twisting/twisting_algorithm.py`: #### Key Features **1. Regularized Computation** Near $s = 0$, the term $|s|^\alpha$ can cause numerical issues. The implementation uses: $$
u_1 = \begin{cases}
-K_1 |s|^\alpha \text{sign}(s) & \text{if } |s| > \epsilon_{\text{reg}} \\
-K_1 \epsilon_{\text{reg}}^\alpha \text{sign}(s) & \text{otherwise}
\end{cases}
$$ Default: $\epsilon_{\text{reg}} = 10^{-10}$ **2. Anti-Windup Protection** The integral state is bounded to prevent windup: $$
\int \text{sign}(s) \, dt \in [-L_{\text{windup}}, L_{\text{windup}}]
$$ **3. Smooth Switching Functions** Three switching function options: | Method | Definition | Continuity | Chattering |
|--------|-----------|------------|------------|
| `sign` | $\text{sgn}(s)$ | Discontinuous | High |
| `tanh` | $\tanh(s/\epsilon)$ | $C^\infty$ | Low |
| `linear` | $\text{clip}(s/\epsilon, -1, 1)$ | $C^0$ | Medium | ### Usage Examples #### Basic Super-Twisting Control ```python
from src.controllers.smc.algorithms.super_twisting.twisting_algorithm import SuperTwistingAlgorithm # Initialize STA
sta = SuperTwistingAlgorithm( K1=5.0, # First twisting gain K2=4.0, # Second twisting gain (K1 > K2) alpha=0.5, # Standard power exponent anti_windup_limit=10.0, # Bound integral state regularization=1e-10 # Numerical safety
) # Compute control at each timestep
dt = 0.01 # 10 ms timestep for t in time_array: # Compute sliding surface (from SMC controller) s = sliding_surface(state) # Super-twisting control law control_dict = sta.compute_control( surface_value=s, dt=dt, switching_function='tanh', boundary_layer=0.01 ) # Extract components u_total = control_dict['u_total'] u1 = control_dict['u1_continuous'] u2 = control_dict['u2_integral'] # Apply control state = plant.step(u_total, dt)
``` #### Performance Analysis ```python
# example-metadata:
# runnable: false # Run simulation and collect surface history
surface_history = [] for t in time_array: s = sliding_surface(state) surface_history.append(s) control_dict = sta.compute_control(s, dt) state = plant.step(control_dict['u_total'], dt) # Analyze STA performance
analysis = sta.analyze_performance(surface_history) print("Stability Metrics:")
print(f" Gains satisfy K1 > K2: {analysis['stability_metrics']['gains_satisfy_condition']}")
print(f" Gain ratio K1/K2: {analysis['stability_metrics']['gain_ratio']:.2f}") print("\nConvergence Metrics:")
print(f" Convergence detected: {analysis['convergence_metrics']['convergence_detected']}")
print(f" Convergence time steps: {analysis['convergence_metrics']['convergence_time_steps']}")
print(f" Theoretical time: {analysis['convergence_metrics']['theoretical_convergence_time']:.3f} s")
print(f" Final surface RMS: {analysis['convergence_metrics']['final_surface_rms']:.6f}") print("\nControl Characteristics:")
print(f" Integral state: {analysis['control_characteristics']['integral_state']:.3f}")
print(f" Anti-windup active: {analysis['control_characteristics']['anti_windup_active']}")
``` ### Gain Tuning Guidelines #### Stability Constraint **Required:** $K_1 > K_2 > 0$ **Recommended:** $K_1 / K_2 \in [1.2, 3.0]$ - **Ratio too small ($< 1.2$):** Slower convergence, chattering

- **Ratio too large ($> 3.0$):** Aggressive control, potential overshoot #### Performance Trade-offs **Increasing $K_1$:**
- ✓ Faster convergence
- ✓ Stronger disturbance rejection
- ✗ Higher control effort
- ✗ More chattering **Increasing $K_2$:**
- ✓ Better steady-state precision
- ✓ Improved integral action
- ✗ Risk of instability if $K_2 \geq K_1$ **Decreasing $\alpha$:**
- ✓ Faster finite-time convergence
- ✗ More sensitive to noise
- ✗ Higher control effort near $s = 0$ ### Comparison: STA vs Classical SMC | Aspect | Classical SMC | Super-Twisting |
|--------|---------------|----------------|
| Convergence | Asymptotic ($\propto e^{-\lambda t}$) | Finite-time ($t < T_{\text{conv}}$) |
| Chattering | High (discontinuous control) | Low (continuous $u_1$) |
| Robustness | Good | (second-order SM) |
| Tuning complexity | Low (1 gain per DOF) | Medium (2 gains, power exponent) |
| Implementation | Simple | Moderate (integral state) | **Recommendation:** Use STA for applications requiring:
- Guaranteed finite-time convergence
- Minimal chattering (e.g., mechanical systems)
- Strong disturbance rejection

---

## Numerical Stability Algorithms ### IEEE 754 Floating-Point Considerations All numerical operations must account for: 1. **Machine epsilon:** $\epsilon_{\text{machine}} \approx 2.22 \times 10^{-16}$ (double precision)

2. **Overflow threshold:** $\approx 1.79 \times 10^{308}$
3. **Underflow threshold:** $\approx 2.23 \times 10^{-308}$
4. **Subnormal numbers:** Gradual underflow region ### Safe Operations Library Located in `src/utils/numerical_stability/safe_operations.py`: #### 1. Safe Division **Problem:** Division by zero or near-zero denominators **Solution:** $$
\text{safe\_divide}(a, b, \epsilon) = \begin{cases}
\text{fallback} & \text{if } b = 0 \\
\frac{a}{\max(|b|, \epsilon) \cdot \text{sign}(b)} & \text{if } 0 < |b| < \epsilon \\
\frac{a}{b} & \text{otherwise}
\end{cases}
$$ **Implementation:** ```python
from src.utils.numerical_stability import safe_divide # Control law with division
error = state[0]
velocity = state[1] # UNSAFE: division by zero if velocity = 0
# control = error / velocity # SAFE: protected division

control = safe_divide( error, velocity, epsilon=1e-12, # Minimum safe denominator fallback=0.0, # Value if velocity exactly zero warn=True # Issue warning for debugging
)
``` **Epsilon Selection:** | Application | Recommended $\epsilon$ | Rationale |
|-------------|----------------------|-----------|
| Control derivatives | $10^{-12}$ | Stability margin for numerical differentiation |
| Optimization gradients | $10^{-10}$ | Convergence tolerance for gradient descent |
| Physics parameters | $10^{-8}$ | Physical measurement precision |
| General computation | $10^{-15}$ | Near machine epsilon for maximum precision | #### 2. Safe Square Root **Problem:** Domain errors from negative arguments (e.g., numerical noise) **Solution:** $$
\text{safe\_sqrt}(x, \epsilon) = \sqrt{\max(x, \epsilon)}
$$ **Usage:** ```python
from src.utils.numerical_stability import safe_sqrt # Norm computation from squared values
squared_sum = x**2 + y**2 + z**2 # UNSAFE: if squared_sum slightly negative due to numerical error
# norm = np.sqrt(squared_sum) # SAFE: clips to non-negative
norm = safe_sqrt(squared_sum, min_value=1e-15)
``` #### 3. Safe Exponential **Problem:** Overflow for large exponents **Solution:** $$

\text{safe\_exp}(x, x_{\max}) = \exp(\min(x, x_{\max}))
$$ Default: $x_{\max} = 700$ (safe for double precision) **Usage in Control:** ```python
from src.utils.numerical_stability import safe_exp # Exponential barrier function
def barrier_cost(distance, sharpness=10.0): # UNSAFE: exp(1000) overflows # return np.exp(-sharpness * distance) # SAFE: clipped to prevent overflow return safe_exp(-sharpness * distance, max_value=700.0)
``` #### 4. Safe Normalization **Problem:** Zero-length vectors cause division by zero **Solution:** $$
\text{safe\_normalize}(\mathbf{v}) = \frac{\mathbf{v}}{\max(\|\mathbf{v}\|, \epsilon)}
$$ **Usage in Gradient Descent:** ```python
from src.utils.numerical_stability import safe_normalize # Normalized gradient for optimization
gradient = compute_gradient(params) # UNSAFE: if gradient is exactly zero
# step_direction = gradient / np.linalg.norm(gradient) # SAFE: returns zero vector if gradient is zero
step_direction = safe_normalize( gradient, min_norm=1e-15, fallback=np.zeros_like(gradient)
)
``` ### Adaptive Regularization For ill-conditioned matrix operations: $$

\mathbf{M}_{\text{reg}} = \mathbf{M} + \lambda \mathbf{I}
$$ where $\lambda$ is adaptively chosen based on condition number: $$
\lambda = \max(\epsilon_{\text{min}}, \alpha \cdot \kappa(\mathbf{M}) \cdot \epsilon_{\text{machine}})
$$ **Reference:** See `docs/mathematical_foundations/numerical_integration_theory.md` for matrix conditioning details

---

## Algorithm Comparison Framework ### Benchmark Functions Standard test functions for optimization algorithm validation: #### 1. Sphere Function (Unimodal) $$

f(\mathbf{x}) = \sum_{i=1}^D x_i^2
$$ - **Global minimum:** $f(\mathbf{0}) = 0$
- **Bounds:** $x_i \in [-5.12, 5.12]$
- **Properties:** Convex, smooth, separable
- **Use case:** Test convergence speed on simple landscape #### 2. Rosenbrock Function (Multimodal) $$
f(\mathbf{x}) = \sum_{i=1}^{D-1} \left[100(x_{i+1} - x_i^2)^2 + (1 - x_i)^2\right]
$$ - **Global minimum:** $f(\mathbf{1}) = 0$ (at $\mathbf{x} = [1, 1, \ldots, 1]$)
- **Bounds:** $x_i \in [-2.048, 2.048]$
- **Properties:** Non-convex, narrow valley, non-separable
- **Use case:** Test navigation through complex landscapes #### 3. Rastrigin Function (Highly Multimodal) $$
f(\mathbf{x}) = 10D + \sum_{i=1}^D \left[x_i^2 - 10\cos(2\pi x_i)\right]
$$ - **Global minimum:** $f(\mathbf{0}) = 0$
- **Bounds:** $x_i \in [-5.12, 5.12]$
- **Properties:** Highly multimodal ($\sim 10^D$ local minima), separable
- **Use case:** Test escape from local minima #### 4. Ackley Function (Multimodal with Plateau) $$
f(\mathbf{x}) = -20 \exp\left(-0.2\sqrt{\frac{1}{D}\sum_{i=1}^D x_i^2}\right) - \exp\left(\frac{1}{D}\sum_{i=1}^D \cos(2\pi x_i)\right) + 20 + e
$$ - **Global minimum:** $f(\mathbf{0}) = 0$
- **Bounds:** $x_i \in [-32.768, 32.768]$
- **Properties:** Multimodal with nearly flat outer region
- **Use case:** Test global exploration capability ### Statistical Testing #### Mann-Whitney U Test **Null hypothesis:** Two algorithm distributions are identical **Test statistic:** $$
U = \min(U_A, U_B)
$$ where $U_A$ is the number of wins for algorithm A when comparing all pairs. **Decision:** Reject $H_0$ if $p < \alpha$ (typically $\alpha = 0.05$) #### Effect Size (Cohen's d) Measures practical significance beyond statistical significance: $$
d = \frac{|\mu_A - \mu_B|}{\sqrt{\frac{(n_A - 1)\sigma_A^2 + (n_B - 1)\sigma_B^2}{n_A + n_B - 2}}}
$$ **Interpretation:**
- $d < 0.2$: Negligible effect
- $0.2 \leq d < 0.5$: Small effect
- $0.5 \leq d < 0.8$: Medium effect
- $d \geq 0.8$: Large effect ### Convergence Analysis Metrics **1. Convergence Rate:** $$
r = \frac{f(\mathbf{x}_0) - f(\mathbf{x}_T)}{T}
$$ **2. Convergence Speed:** Iterations to reach 90% of final improvement **3. Success Rate:** Fraction of runs achieving $f(\mathbf{x}_{\text{final}}) < \epsilon_{\text{tol}}$ **4. Stability Metric:** $$
\text{Stability} = \frac{1}{1 + \text{Var}(f(\mathbf{x}_{T-k:T}))}
$$ where variance is computed over the last $k$ iterations.

---

## Performance Optimization Techniques ### Vectorization Strategies **Key principle:** Minimize Python loops, maximize NumPy operations #### Batch Simulation Example ```python

# example-metadata:

# runnable: false # SLOW: Sequential simulation (Python loop)

def sequential_evaluation(particles, controller_factory): costs = [] for gains in particles: controller = controller_factory(gains) cost = simulate(controller, T, dt) costs.append(cost) return np.array(costs) # FAST: Vectorized simulation (NumPy operations)
def vectorized_evaluation(particles, controller_factory): # Single call for entire batch t, x_batch, u_batch, sigma_batch = simulate_system_batch( controller_factory=controller_factory, particles=particles, # Shape: (N, D) sim_time=T, dt=dt ) # Vectorized cost computation costs = compute_costs_batch(t, x_batch, u_batch, sigma_batch) return costs # Shape: (N,) # Speedup: ~20-30x for N=30 particles
``` ### Numba Just-In-Time Compilation For inner loops that cannot be vectorized: ```python
import numba @numba.jit(nopython=True, cache=True)
def fast_dynamics_update(state, control, dt, params): """Compiled dynamics integration.""" # Pure NumPy operations, no Python objects M = compute_mass_matrix(state, params) C = compute_coriolis(state, params) G = compute_gravity(state, params) # Solve: M * qdd = tau - C * qd - G qdd = np.linalg.solve(M, control - C @ state[3:] - G) return state + dt * np.concatenate([state[3:], qdd]) # First call: ~100 ms (compilation overhead)
# Subsequent calls: ~0.1 ms (compiled code)
``` **Speedup:** ~100-1000x for tight numerical loops ### Memory Management **Problem:** PSO creates thousands of controller instances **Solution:** Object pooling and explicit cleanup ```python

from src.controllers.smc import ClassicalSMC # Create controller pool
pool_size = 100
controller_pool = [ ClassicalSMC(gains=default_gains, max_force=100, boundary_layer=0.01) for _ in range(pool_size)
] # Reuse controllers (update gains instead of creating new instances)
for iteration in range(pso_iterations): for i, gains in enumerate(swarm_positions): controller = controller_pool[i % pool_size] controller.set_gains(gains) # Update in-place cost = evaluate(controller) # Explicit cleanup after optimization
for controller in controller_pool: controller.cleanup()
``` **Memory savings:** ~90% reduction vs creating new instances

---

## Advanced Topics ### Multi-Objective Optimization For problems with conflicting objectives: $$
\min_{\mathbf{x}} \mathbf{f}(\mathbf{x}) = [f_1(\mathbf{x}), f_2(\mathbf{x}), \ldots, f_m(\mathbf{x})]
$$ **Pareto dominance:** $\mathbf{x}_a$ dominates $\mathbf{x}_b$ if: $$
\forall i: f_i(\mathbf{x}_a) \leq f_i(\mathbf{x}_b) \quad \land \quad \exists j: f_j(\mathbf{x}_a) < f_j(\mathbf{x}_b)
$$ **Reference:** See `tests/test_optimization/test_algorithm_comparison.py` for multi-objective benchmarks (ZDT1, DTLZ2) ### Constraint Handling For optimization with constraints $g_i(\mathbf{x}) \leq 0$: **Penalty method:** $$
f_{\text{penalized}}(\mathbf{x}) = f(\mathbf{x}) + \sum_{i=1}^m r_i \cdot \max(0, g_i(\mathbf{x}))^2
$$ **Death penalty:** $f_{\text{penalized}}(\mathbf{x}) = \infty$ if any constraint violated ### Hybrid Algorithms Combining PSO with local search: 1. **Global phase:** PSO exploration (50 iterations)
2. **Local phase:** Gradient descent from best PSO solution (refinement) **Reference:** `src/optimization/algorithms/pso_optimizer.py:632` for optimization hooks

---

## Best Practices ### 1. Reproducibility **Always specify seeds:** ```python
# Set global seed in config
config.global_seed = 42 # PSO tuner uses this seed automatically
tuner = PSOTuner(controller_factory, config, seed=42) # Results are now fully reproducible
``` ### 2. Numerical Stability **Use safe operations for all divisions:** ```python

from src.utils.numerical_stability import safe_divide, safe_sqrt, safe_exp # Protect all potentially unstable operations
result = safe_divide(numerator, denominator, epsilon=1e-12)
norm = safe_sqrt(squared_sum, min_value=1e-15)
exponential = safe_exp(large_value, max_value=700.0)
``` ### 3. Validation **Run algorithm comparison tests:** ```bash
# Benchmark against standard test functions
pytest tests/test_optimization/test_algorithm_comparison.py -v # Check statistical significance
pytest tests/test_optimization/test_algorithm_comparison.py::TestAlgorithmComparison::test_statistical_significance_testing -v
``` ### 4. Performance Profiling **Measure optimization efficiency:** ```python

import time start = time.time()
result = tuner.optimise(iters_override=100, n_particles_override=30)
elapsed = time.time() - start evaluations = 100 * 30 # iters * particles
evals_per_second = evaluations / elapsed print(f"Optimization time: {elapsed:.2f} s")
print(f"Evaluations/second: {evals_per_second:.1f}")
print(f"Cost per evaluation: {1000 * elapsed / evaluations:.2f} ms")
``` ### 5. Convergence Monitoring **Track PSO convergence:** ```python
import matplotlib.pyplot as plt result = tuner.optimise() # Plot convergence curve
plt.figure(figsize=(10, 6))
plt.semilogy(result['history']['cost'], linewidth=2)
plt.xlabel('Iteration')
plt.ylabel('Best Cost (log scale)')
plt.title('PSO Convergence History')
plt.grid(True, alpha=0.3)
plt.show() # Check for premature convergence
if np.std(result['history']['cost'][-20:]) < 1e-6: print("Warning: PSO may have converged prematurely")
```

---

## References 1. **PSO Theory:** - Kennedy & Eberhart (1995). "Particle Swarm Optimization" - Clerc & Kennedy (2002). "The particle swarm - explosion, stability, and convergence in a multidimensional complex space" 2. **Super-Twisting Algorithm:** - Levant (1993). "Sliding order and sliding accuracy in sliding mode control" - Moreno & Osorio (2008). "A Lyapunov approach to second-order sliding mode controllers and observers" 3. **Numerical Algorithms:** - Golub & Van Loan (2013). "Matrix Computations", 4th edition - Higham (2002). "Accuracy and Stability of Numerical Algorithms", 2nd edition 4. **Algorithm Comparison:** - Derrac et al. (2011). "A practical tutorial on the use of nonparametric statistical tests" - García et al. (2009). "A study on the use of non-parametric tests for analyzing the evolutionary algorithms' behaviour"

**File Location:** `docs/mathematical_foundations/advanced_algorithms_guide.md`
**Lines:** 721
**Cross-references:**
- PSO implementation: `src/optimization/algorithms/pso_optimizer.py`
- Super-twisting: `src/controllers/smc/algorithms/super_twisting/twisting_algorithm.py`
- Safe operations: `src/utils/numerical_stability/safe_operations.py`
- Algorithm comparison: `tests/test_optimization/test_algorithm_comparison.py`
