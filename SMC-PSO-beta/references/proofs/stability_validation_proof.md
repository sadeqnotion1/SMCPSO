# Physical, Geometric & Control-Theoretic Stability Proofs

This document provides the mathematical derivations, physical proofs, and control-theoretic justifications for the geometric, thermodynamic, gain, and numerical stability parameters configured in `config.yaml` and verified by the simulation and validation infrastructure.

---

## 1. Geometric Consistency Constraints ($d_i \le l_i$)

### 1.1 Mathematical Proof of Boundary Limits
Let a pendulum link $i$ be represented as a rigid body of mass $m_i$ distributed over a spatial volume $\mathcal{V}_i$ with density function $\rho_i(\mathbf{r})$. Let the pivot point of the link be located at the origin $\mathbf{r}_0 = \mathbf{0}$. The total length of the link along its major axis is $l_i$ [m].

The center of mass (COM) distance $d_i$ from the pivot point is defined as:
$$d_i = \frac{1}{m_i} \int_{\mathcal{V}_i} \|\mathbf{r}\| \rho_i(\mathbf{r}) d\mathcal{V}$$

Since the physical body of the link is bounded by its total length $l_i$, any point mass element $dm = \rho_i(\mathbf{r}) d\mathcal{V}$ must lie within the range:
$$\|\mathbf{r}\| \le l_i \quad \forall \mathbf{r} \in \mathcal{V}_i$$

Integrating this inequality over the entire volume yields:
$$d_i = \frac{1}{m_i} \int_{\mathcal{V}_i} \|\mathbf{r}\| \rho_i(\mathbf{r}) d\mathcal{V} \le \frac{1}{m_i} \int_{\mathcal{V}_i} l_i \rho_i(\mathbf{r}) d\mathcal{V} = \frac{l_i}{m_i} \int_{\mathcal{V}_i} \rho_i(\mathbf{r}) d\mathcal{V} = \frac{l_i}{m_i} m_i = l_i$$

Thus, the geometric constraint is strictly bounded by:
$$d_i \le l_i$$

If the link is modeled as a uniform rod, the density $\rho_i$ is constant, yielding:
$$d_i = \frac{l_i}{2} < l_i$$

### 1.2 Configuration Alignment
In `config.yaml`, the geometric parameters are configured as:
- **Link 1:** Length $l_1 = 0.4$ m, COM distance $d_1 = 0.2$ m.
  $$0.2 \le 0.4 \quad [\text{Pass}]$$
- **Link 2:** Length $l_2 = 0.3$ m, COM distance $d_2 = 0.15$ m.
  $$0.15 \le 0.3 \quad [\text{Pass}]$$

---

## 2. Viscous Friction Thermodynamic Constraints ($b \ge 0$)

### 2.1 Physical Proof from Entropy Generation
Viscous friction forces ($F_{f,c} = -b_c \dot{x}$) and joint torques ($\tau_{f,i} = -b_i \dot{\theta}_i$) represent the irreversible conversion of mechanical kinetic energy into thermal energy (heat). 

The rate of mechanical energy dissipation $\dot{E}_{\mathrm{diss}}$ in the system due to friction is:
$$\dot{E}_{\mathrm{diss}} = - \left( b_c \dot{x}^2 + b_1 \dot{\theta}_1^2 + b_2 \dot{\theta}_2^2 \right)$$

According to the **Second Law of Thermodynamics** (Clausius inequality), the rate of entropy generation $\dot{S}_{\mathrm{gen}}$ in an isolated system at temperature $T > 0$ [K] must be non-negative:
$$\dot{S}_{\mathrm{gen}} = -\frac{\dot{E}_{\mathrm{diss}}}{T} = \frac{1}{T} \left( b_c \dot{x}^2 + b_1 \dot{\theta}_1^2 + b_2 \dot{\theta}_2^2 \right) \ge 0$$

For this inequality to hold for any arbitrary velocity trajectory $(\dot{x}, \dot{\theta}_1, \dot{\theta}_2)$, the quadratic form must be positive semi-definite, which mathematically requires all viscous friction coefficients to be non-negative:
$$b_c \ge 0, \quad b_1 \ge 0, \quad b_2 \ge 0$$

### 2.2 Configuration Alignment
Viscous friction parameters in `config.yaml` are configured as:
- Cart Friction: $b_c = 0.2$ N-s/m
- Joint 1 Friction: $b_1 = 0.005$ N-m-s/rad
- Joint 2 Friction: $b_2 = 0.004$ N-m-s/rad
All parameters are strictly positive ($> 0$), satisfying thermodynamic consistency.

---

## 3. Mass Ratio Controllability Guidelines

### 3.1 Control-Theoretic Derivation
The underactuated double-inverted pendulum has 3 degrees of freedom ($q = [x, \theta_1, \theta_2]^T$) but only 1 control input $u$ (force on cart). The coupling between the actuated coordinate $x$ and the underactuated coordinates $\theta_1, \theta_2$ is governed by the input coupling matrix:
$$M(q) \ddot{q} + \mathbf{h}(q, \dot{q}) = \begin{bmatrix} 1 \\ 0 \\ 0 \end{bmatrix} u \implies \ddot{q} = M(q)^{-1} \begin{bmatrix} 1 \\ 0 \\ 0 \end{bmatrix} u - M(q)^{-1} \mathbf{h}(q, \dot{q})$$

The control authority over the pendulum angles $\theta_i$ depends directly on the off-diagonal coupling terms in the inverse inertia matrix $M(q)^{-1}$. Let the total mass of the pendulums be $m_p = m_1 + m_2$ and the cart mass be $m_0$.

If $m_p \gg m_0$, the reaction force from the pendulums' acceleration dominates the cart dynamics. The inertial coupling terms become ill-conditioned, and the force $u$ required to stabilize the pendulums scales exponentially, leading to actuator saturation. To prevent loss of controllability and high susceptibility to input disturbances, we enforce a mass distribution ratio guideline:
$$\mu = \frac{m_1 + m_2}{m_0} \le 1.0$$

### 3.2 Configuration Alignment
Using parameters from `config.yaml`:
$$\mu = \frac{0.2 + 0.15}{1.5} = \frac{0.35}{1.5} \approx 0.233 \le 1.0 \quad [\text{Pass}]$$

---

## 4. Moreno-Osorio Stability Bounds for STA-SMC ($K_1 > K_2 > 0$)

### 4.1 Strict Lyapunov Stability Derivation
The Super-Twisting Algorithm (STA) acts on the sliding variable $s$ and its derivative $\dot{s} = u_{\mathrm{sta}} + \phi(t)$, where $\phi(t)$ represents bounded disturbances satisfying $|\dot{\phi}(t)| \le L$ for a constant $L > 0$. The control law is:
$$u_{\mathrm{sta}} = -K_1 |s|^{1/2} \text{sgn}(s) + v$$
$$\dot{v} = -K_2 \text{sgn}(s)$$

Let the state vector be $\xi = [|s|^{1/2} \text{sgn}(s), v + \phi(t)]^T = [\xi_1, \xi_2]^T$. The state equations are:
$$\dot{\xi}_1 = \frac{1}{2|\xi_1|} \left( -K_1 \xi_1 + \xi_2 \right)$$
$$\dot{\xi}_2 = -K_2 \text{sgn}(\xi_1) + \dot{\phi}(t)$$

Moreno & Osorio (2008) proposed the following strict Lyapunov candidate function:
$$V(\xi) = \xi^T P \xi = P_{11} \xi_1^2 + 2 P_{12} \xi_1 \xi_2 + P_{22} \xi_2^2$$
where $P$ is a symmetric positive-definite matrix:
$$P = \begin{bmatrix} K_2 + \frac{1}{2} K_1^2 & -\frac{1}{2} K_1 \\ -\frac{1}{2} K_1 & 1 \end{bmatrix}$$

For $P$ to be positive-definite, the eigenvalues of $P$ must be positive, which requires:
$$\text{det}(P) = K_2 + \frac{1}{2} K_1^2 - \frac{1}{4} K_1^2 = K_2 + \frac{1}{4} K_1^2 > 0$$
This is always satisfied if $K_2 > 0$.

Taking the derivative of $V(\xi)$ along the trajectories of the system:
$$\dot{V}(\xi) = -\frac{1}{|\xi_1|} \xi^T Q \xi + 2 \dot{\phi}(t) \left( P_{12} \xi_1 + P_{22} \xi_2 \right)$$

Substituting $P$ values and using the disturbance bound $|\dot{\phi}(t)| \le L$:
$$\dot{V}(\xi) \le -\frac{1}{|\xi_1|} \xi^T Q_{\mathrm{min}} \xi$$
where the stability condition requires the matrix $Q$ to be positive-definite. This is guaranteed if the proportional gain $K_1$ dominates the integral gain $K_2$ and disturbance bound $L$ according to the strict relation:
$$K_1 > 0, \quad K_2 > L, \quad K_1 > K_2 > 0$$

If $K_2 \ge K_1$, the system's trajectories can diverge from the sliding manifold due to over-correction of the integral component, causing phase-lag instability.

### 4.2 Configuration Alignment
The STA gains in `config.yaml` satisfy this inequality:
- **Nominal Gains:** $K_1 = 8.0, K_2 = 4.0 \implies 8.0 > 4.0 > 0 \quad [\text{Pass}]$
- **MT-8 Optimized Gains:** $K_1 = 6.672, K_2 = 2.017 \implies 6.672 > 2.017 > 0 \quad [\text{Pass}]$

---

## 5. Dead-Zone vs. Boundary Layer Constraints ($\text{sat\_soft\_width} \ge \text{dead\_zone}$)

### 5.1 Analysis of Limit Cycle Prevention
In the adaptive super-twisting controller, the sliding variable $s$ is processed via a smooth saturation function to eliminate high-frequency chattering:
$$\text{sat\_soft}(s) = \frac{s}{|s| + \epsilon}$$
where $\epsilon = \text{sat\_soft\_width}$ is the boundary layer thickness. Concurrently, the adaptive gains $k_1, k_2$ are frozen when the state is within a dead-zone $|s| \le \delta$ (where $\delta = \text{dead\_zone}$) to prevent parameter drift caused by noise wind-up.

If $\epsilon < \delta$, the transition region where the controller acts linearly is smaller than the zone where gain adaptation is halted. As a result, the controller switches abruptly between high-gain switching and zero-adaptation, triggering limit cycles and persistent oscillations at the boundary of the dead-zone. To guarantee smooth asymptotic convergence, we require:
$$\epsilon \ge \delta \implies \text{sat\_soft\_width} \ge \text{dead\_zone}$$

### 5.2 Configuration Alignment
In `config.yaml`, under `hybrid_adaptive_sta_smc`:
$$\text{sat\_soft\_width} = 0.35 \ge \text{dead\_zone} = 0.05 \quad [\text{Pass}]$$

---

## 6. Numerical Stability Monitoring Bounds

### 6.1 Lyapunov Decrease Ratio (LDR) Bound ($\text{LDR} < 1.0$)
The stability monitor tracks the discrete-time Lyapunov function ratio between successive time steps:
$$\text{LDR}(t_k) = \frac{V(t_k)}{V(t_{k-1})}$$

For a stable system, Lyapunov's direct method requires the energy to decrease monotonically:
$$\text{LDR}(t_k) < 1.0 \quad \forall t_k > t_{\mathrm{transient}}$$

Discretization error and measurement noise introduce small variations. To prevent false alarms during transient spikes, the threshold is configured as:
$$\text{LDR}_{\mathrm{threshold}} = 0.95$$
An LDR consistently above $0.95$ flags that the controller is failing to dissipate the system's tracking errors, triggering safety diagnostics before state explosion.

### 6.2 Dynamics Matrix Condition Number Bound ($\kappa(M(q)) < 10^7$)
The joint-space inertia matrix $M(q)$ for the double-inverted pendulum is:
$$M(q) = \begin{bmatrix} M_{11} & M_{12}\cos(\theta_1) & M_{13}\cos(\theta_2) \\ M_{21}\cos(\theta_1) & M_{22} & M_{23}\cos(\theta_1-\theta_2) \\ M_{31}\cos(\theta_2) & M_{32}\cos(\theta_1-\theta_2) & M_{33} \end{bmatrix}$$

The condition number is defined as:
$$\kappa(M(q)) = \|M(q)\| \cdot \|M(q)^{-1}\| = \frac{\sigma_{\mathrm{max}}(M)}{\sigma_{\mathrm{min}}(M)}$$

Physically, the system mass is positive-definite, meaning $\sigma_{\mathrm{min}}(M) > 0$. However, during chaotic oscillations or state explosion (e.g. $|\theta_i| > \pi/2$), the matrix terms can approach values that lead to $\text{det}(M) \approx 0$. 

If $\kappa(M(q)) \ge 10^7$, double-precision floating-point matrix inversion introduces numerical inaccuracies (loss of $\approx 7$ digits of precision). The thresholds are set to prevent numerical singularities:
- **Nominal Median Threshold:** $\kappa(M) < 10^7$ (flags persistent conditioning degradation)
- **Nominal Spike Threshold:** $\kappa(M) < 10^9$ (triggers emergency shutdown or fallback control)
