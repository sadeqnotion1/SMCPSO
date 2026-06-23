# Mathematical Notation Reference Guide

**Project:** DIP-SMC-PSO
**Purpose:** Ensure consistent notation across cited papers, documentation, and code
**Last Updated:** 2025-10-09



## Overview

This guide establishes the canonical mathematical notation used in the DIP-SMC-PSO project and maps it to Python code variables. It resolves notation conflicts between cited papers and provides a unified reference for developers and reviewers.



## Notation Conventions

### General Principles

1. **Bold Uppercase**: Matrices (e.g., $\mat{M}$, $\mat{C}$, $\mat{G}$)
2. **Bold Lowercase**: Vectors (e.g., $\vec{x}$, $\vec{u}$, $\vec{q}$)
3. **Italic Lowercase**: Scalars (e.g., $s$, $t$, $\eta$)
4. **Greek Letters**: Parameters and special quantities (e.g., $\alpha$, $\beta$, $\epsilon$)



## State Variables

### Double Inverted Pendulum System

| Mathematical Symbol | Description | Code Variable | Units | Source |
|---------------------|-------------|---------------|-------|--------|
| $\vec{q} = [x, \theta_1, \theta_2]^T$ | Generalized coordinates | `q` | `[m, rad, rad]` | {cite}`dip_goldstein_2002_classical_mechanics` |
| $\dot{\vec{q}}$ | Generalized velocities | `dq` | `[m/s, rad/s, rad/s]` | - |
| $\ddot{\vec{q}}$ | Generalized accelerations | `ddq` | `[m/s², rad/s², rad/s²]` | - |
| $x$ | Cart position | `state[0]` | `m` | - |
| $\theta_1$ | First pendulum angle | `state[1]` | `rad` | - |
| $\theta_2$ | Second pendulum angle | `state[2]` | `rad` | - |
| $\dot{x}$ | Cart velocity | `state[3]` | `m/s` | - |
| $\dot{\theta}_1$ | First pendulum angular velocity | `state[4]` | `rad/s` | - |
| $\dot{\theta}_2$ | Second pendulum angular velocity | `state[5]` | `rad/s` | - |

**Full State Vector:**
```math
\vec{x} = [x, \theta_1, \theta_2, \dot{x}, \dot{\theta}_1, \dot{\theta}_2]^T \in \mathbb{R}^6
```

**Code Mapping:**
```python
# State vector indexing
X_POS = 0      # Cart position x
THETA1 = 1     # First pendulum angle θ₁
THETA2 = 2     # Second pendulum angle θ₂
X_VEL = 3      # Cart velocity ẋ
OMEGA1 = 4     # First pendulum angular velocity θ̇₁
OMEGA2 = 5     # Second pendulum angular velocity θ̇₂
```



## System Dynamics Matrices

### Lagrangian Formulation

| Mathematical Symbol | Description | Code Variable | Dimensions | Source |
|---------------------|-------------|---------------|------------|--------|
| $\mat{M}(\vec{q})$ | Mass/inertia matrix | `M` | `3×3` | {cite}`dip_goldstein_2002_classical_mechanics` |
| $\mat{C}(\vec{q}, \dot{\vec{q}})$ | Coriolis/centrifugal matrix | `C` | `3×3` | {cite}`dip_spong_2006_robot_modeling_control` |
| $\mat{G}(\vec{q})$ | Gravitational torque vector | `G` | `3×1` | - |
| $\mat{B}$ | Control input matrix | `B` | `3×1` | - |
| $u$ | Control force (scalar) | `u` | scalar | `N` (Newtons) |

**Equations of Motion:**
```math
\mat{M}(\vec{q})\ddot{\vec{q}} + \mat{C}(\vec{q}, \dot{\vec{q}})\dot{\vec{q}} + \mat{G}(\vec{q}) = \mat{B}u
```



## Sliding Mode Control Notation

### Sliding Surface Design

| Mathematical Symbol | Description | Code Variable | Source |
|---------------------|-------------|---------------|--------|
| $s$ | Sliding surface variable (scalar) | `s` | {cite}`smc_utkin_1993_sliding_mode_control_design` |
| $\vec{s}$ | Sliding surface vector | `s_vec` | - |
| $\mat{S}$ | Sliding surface matrix | `S_matrix` | {cite}`smc_edwards_spurgeon_1998_sliding_mode_control` |
| $\vec{c} = [c_x, c_{\theta_1}, c_{\theta_2}]^T$ | Sliding surface parameters | `c_params` | {cite}`smc_farrell_2006_adaptive_approximation` |
| $\mat{C} = \text{diag}(c_x, c_{\theta_1}, c_{\theta_2})$ | Sliding surface parameter matrix | `C_diag` | - |

**Sliding Surface Definition:**
```math
s = \mat{S}\vec{e} = \vec{c}^T\vec{e}_p + \dot{\vec{e}}_p
```

**Code Mapping:**
```python
# In ClassicalSMC.compute_sliding_surface()
def sliding_surface_matrix(self, c_params):
    """Compute sliding surface matrix S ∈ R^{3×6}"""
    S = np.array([
        [c_params[0], 0, 0, 1, 0, 0],  # Cart: c_x * e_x + ė_x
        [0, c_params[1], 0, 0, 1, 0],  # Pendulum 1: c_θ₁ * e_θ₁ + ė_θ₁
        [0, 0, c_params[2], 0, 0, 1]   # Pendulum 2: c_θ₂ * e_θ₂ + ė_θ₂
    ])
    return S
```

## Control Law Components

| Mathematical Symbol | Description | Code Variable | Units | Source |
|---------------------|-------------|---------------|-------|--------|
| $u_{eq}$ | Equivalent control | `u_eq` | `N` | {cite}`smc_slotine_li_1991_applied_nonlinear_control` |
| $u_{sw}$ | Switching control | `u_sw` | `N` | - |
| $\eta$ | Switching gain | `eta` | `N` | {cite}`smc_khalil_lecture33_sliding_mode` |
| $\epsilon$ | Boundary layer thickness | `epsilon` | dimensionless | {cite}`smc_burton_1986_continuous` |
| $\rho$ | Uncertainty bound | `rho` | `N` | {cite}`smc_khalil_lecture32_sliding_mode` |

**Classical SMC Law:**
```math
u = u_{eq} + u_{sw} = u_{eq} - \eta \frac{s}{|s| + \epsilon}
```



## Super-Twisting Algorithm

| Mathematical Symbol | Description | Code Variable | Units | Source |
|---------------------|-------------|---------------|-------|--------|
| $u_1$ | Integral term | `u1` | `N` | {cite}`smc_levant_2003_higher_order_introduction` |
| $u_2$ | Discontinuous term | `u2` | `N` | - |
| $\alpha$ | Integral gain | `alpha` | `N/s` | {cite}`smc_moreno_2008_lyapunov_sta` |
| $\beta$ | Discontinuous gain | `beta` | `N` | - |
| $\gamma$ | Control effectiveness lower bound | `gamma` | dimensionless | {cite}`smc_seeber_2017_sta_parameter_setting` |

**Super-Twisting Control Law:**
```math
\begin{aligned}
u &= u_1 + u_2 \\
\dot{u_1} &= -\alpha |s|^{1/2} \text{sign}(s) \\
u_2 &= -\beta \text{sign}(s)
\end{aligned}
```

**Parameter Conditions:**
```math
\alpha > \frac{2\sqrt{2\rho}}{\sqrt{\gamma}}, \quad \beta > \frac{\rho}{\gamma}
```



## Adaptive Control Notation

| Mathematical Symbol | Description | Code Variable | Units | Source |
|---------------------|-------------|---------------|-------|--------|
| $\vec{\theta}$ | True parameter vector | `theta_true` | varies | {cite}`smc_plestan_2010_adaptive_methodologies` |
| $\hat{\vec{\theta}}$ | Parameter estimates | `theta_hat` | varies | - |
| $\tilde{\vec{\theta}} = \vec{\theta} - \hat{\vec{\theta}}$ | Parameter error | `theta_tilde` | varies | - |
| $\Gamma$ | Adaptation gain matrix | `Gamma` | varies | {cite}`smc_roy_2020_adaptive_unbounded` |
| $\mat{Y}(\vec{q}, \dot{\vec{q}}, \ddot{\vec{q}})$ | Regression matrix | `Y_regressor` | varies | - |

**Adaptation Law:**
```math
\dot{\hat{\vec{\theta}}} = -\Gamma \mat{Y}^T \mat{S}^T s
```



## PSO Optimization Notation

### Particle Swarm Variables

| Mathematical Symbol | Description | Code Variable | Units | Source |
|---------------------|-------------|---------------|-------|--------|
| $\vec{x}_i(t)$ | Position of particle $i$ | `position` | parameter space | {cite}`pso_kennedy_1995_particle_swarm_optimization` |
| $\vec{v}_i(t)$ | Velocity of particle $i$ | `velocity` | parameter space/iter | - |
| $\vec{p}_i$ | Personal best position | `pbest` | parameter space | {cite}`pso_trelea_2003_convergence` |
| $\vec{g}$ | Global best position | `gbest` | parameter space | - |
| $w$ | Inertia weight | `w` | dimensionless | {cite}`pso_clerc_2002_particle_swarm` |
| $c_1$ | Cognitive parameter | `c1` | dimensionless | - |
| $c_2$ | Social parameter | `c2` | dimensionless | - |
| $r_1, r_2$ | Random numbers $\in [0, 1]$ | `r1, r2` | dimensionless | - |

**PSO Update Equations:**
```math
\begin{aligned}
\vec{v}_i(t+1) &= w\vec{v}_i(t) + c_1 r_1 (\vec{p}_i - \vec{x}_i(t)) + c_2 r_2 (\vec{g} - \vec{x}_i(t)) \\
\vec{x}_i(t+1) &= \vec{x}_i(t) + \vec{v}_i(t+1)
\end{aligned}
```

**Code Mapping:**
```python
# In PSOTuner.optimize()
velocity = (self.w * velocity +
           self.c1 * r1 * (pbest - position) +
           self.c2 * r2 * (gbest - position))
position = position + velocity
```

## Convergence Parameters

| Mathematical Symbol | Description | Code Variable | Typical Value | Source |
|---------------------|-------------|---------------|---------------|--------|
| $\phi = c_1 + c_2$ | Acceleration coefficient sum | `phi` | `4.1` | {cite}`pso_trelea_2003_convergence` |
| $\chi$ | Constriction factor | `chi` | `0.729` | {cite}`pso_van_den_bergh_2001_analysis` |
| $\kappa$ | von Neumann stability parameter | `kappa` | varies | {cite}`pso_gopal_2019_stability_analysis` |

**Stability Condition (Trelea 2003):**
```math
0 < \phi < 4, \quad w = \frac{2}{\phi - 2 + \sqrt{\phi^2 - 4\phi}}
```



## Lyapunov Stability Notation

| Mathematical Symbol | Description | Code Variable | Source |
|---------------------|-------------|---------------|--------|
| $V(\vec{x})$ | Lyapunov function | `V` | {cite}`dip_khalil_2002_nonlinear_systems` |
| $\dot{V}(\vec{x})$ | Lyapunov derivative | `V_dot` | - |
| $\lambda_{\min}(\mat{P})$ | Minimum eigenvalue of matrix $\mat{P}$ | `lambda_min` | - |
| $\lambda_{\max}(\mat{P})$ | Maximum eigenvalue of matrix $\mat{P}$ | `lambda_max` | - |

**Lyapunov Stability Conditions:**
- $V(\vec{x}) > 0$ for all $\vec{x} \neq 0$ (positive definite)
- $\dot{V}(\vec{x}) < 0$ for all $\vec{x} \neq 0$ (negative definite)



## Physical Parameters

### System Constants

| Mathematical Symbol | Description | Code Variable | Typical Value | Units |
|---------------------|-------------|---------------|---------------|-------|
| $m_c$ | Cart mass | `m_c` | `1.0` | `kg` |
| $m_1$ | First pendulum mass | `m_1` | `0.1` | `kg` |
| $m_2$ | Second pendulum mass | `m_2` | `0.1` | `kg` |
| $L_1$ | First pendulum length | `L_1` | `0.5` | `m` |
| $L_2$ | Second pendulum length | `L_2` | `0.5` | `m` |
| $g$ | Gravitational acceleration | `g` | `9.81` | `m/s²` |
| $b$ | Cart friction coefficient | `b` | `0.1` | `N·s/m` |



## Notation Conflicts & Resolutions

### Conflict 1: Sliding Surface Parameter Notation

**Papers Use:**
- {cite}`smc_bucak_2020_analysis_robotics`: $\lambda_i$ for sliding surface parameters
- {cite}`smc_farrell_2006_adaptive_approximation`: $c_i$ for sliding surface parameters
- {cite}`smc_edwards_spurgeon_1998_sliding_mode_control`: $\alpha_i$ for sliding surface parameters

**Our Choice:** $c_i$ (Farrell & Polycarpou 2006)

**Rationale:** Avoids confusion with eigenvalues ($\lambda$) and other parameters ($\alpha$)



### Conflict 2: Switching Gain Notation

**Papers Use:**
- {cite}`smc_khalil_lecture33_sliding_mode`: $k$ for switching gain
- {cite}`smc_slotine_li_1991_applied_nonlinear_control`: $\eta$ for switching gain
- {cite}`smc_utkin_1993_sliding_mode_control_design`: $K$ for switching gain

**Our Choice:** $\eta$ (Slotine & Li 1991)

**Rationale:** Reserves $k$ for discrete time steps, $K$ for gain matrices



### Conflict 3: PSO Inertia Weight

**Papers Use:**
- {cite}`pso_trelea_2003_convergence`: $w$ for inertia weight
- {cite}`pso_clerc_2002_particle_swarm`: $\omega$ for inertia weight
- Some papers: $\alpha$ for inertia weight

**Our Choice:** $w$ (most common in recent literature)

**Rationale:** Standard in PySwarms and modern PSO implementations



## Code Variable Naming Conventions

### Python Naming Rules

1. **Vectors**: Append `_vec` or use lowercase (e.g., `state`, `velocity_vec`)
2. **Matrices**: Use UPPERCASE or append `_matrix` (e.g., `M_matrix`, `C_MATRIX`)
3. **Greek Letters**: Use full name (e.g., `eta`, `epsilon`, `alpha`, `beta`)
4. **Subscripts**: Use underscore (e.g., `c_x`, `theta_1`, `m_c`)
5. **Hats (estimates)**: Append `_hat` (e.g., `theta_hat`)
6. **Dots (derivatives)**: Append `_dot` (e.g., `x_dot`, `V_dot`)

### Type Hints

```python
# Type annotations for clarity
state: np.ndarray  # shape (6,) - state vector
M_matrix: np.ndarray  # shape (3, 3) - mass matrix
u: float  # scalar control input
theta_hat: np.ndarray  # shape (n_params,) - parameter estimates
```



## LaTeX Rendering in Documentation

### MyST Markdown Math Blocks

```markdown
<!-- Inline math -->
The sliding surface $s = \mat{S}\vec{e}$ is defined...

<!-- Display math -->
$$
\mat{M}(\vec{q})\ddot{\vec{q}} + \mat{C}(\vec{q}, \dot{\vec{q}})\dot{\vec{q}} + \mat{G}(\vec{q}) = \mat{B}u
$$

<!-- Labeled equations -->
```{math}

:label: eq:sliding_surface
s = \vec{c}^T\vec{e}_p + \dot{\vec{e}}_p
```



## Cross-Reference Table

### Quick Lookup: Math → Code

| Math | Code | Description |
|------|------|-------------|
| $\vec{x}$ | `state` | Full state vector |
| $\mat{M}$ | `M` | Mass matrix |
| $s$ | `s` | Sliding surface |
| $\eta$ | `eta` | Switching gain |
| $\epsilon$ | `epsilon` | Boundary layer |
| $\hat{\vec{\theta}}$ | `theta_hat` | Parameter estimates |
| $\vec{p}_i$ | `pbest` | PSO personal best |
| $w$ | `w` | PSO inertia weight |



## References

Primary sources for notation conventions:
- SMC: {cite}`smc_slotine_li_1991_applied_nonlinear_control`, {cite}`smc_edwards_spurgeon_1998_sliding_mode_control`
- PSO: {cite}`pso_trelea_2003_convergence`, {cite}`pso_clerc_2002_particle_swarm`
- Dynamics: {cite}`dip_goldstein_2002_classical_mechanics`, {cite}`dip_spong_2006_robot_modeling_control`
- Stability: {cite}`dip_khalil_2002_nonlinear_systems`



**Maintained By:** DIP-SMC-PSO Development Team
**Review Frequency:** Before each major release or when new papers are cited



**🤖 Generated with [Claude Code](https://claude.com/claude-code)**

**Co-Authored-By: Claude <noreply@anthropic.com>**
