## 2. System Model and Problem Formulation

### 2.1 Double-Inverted Pendulum Dynamics

The double-inverted pendulum (DIP) system consists of a cart of mass $m_0$ moving horizontally on a track, with two pendulum links (masses $m_1$, $m_2$; lengths $L_1$, $L_2$) attached sequentially to form a double-joint structure. The system is actuated by a horizontal force $u$ applied to the cart, with the control objective to stabilize both pendulums in the upright position ($\theta_1 = \theta_2 = 0$).

**State Vector:**
```math
\mathbf{x} = [x, \theta_1, \theta_2, \dot{x}, \dot{\theta}_1, \dot{\theta}_2]^T \in \mathbb{R}^6
```

where:
- $x$ - cart position (m)
- $\theta_1$ - angle of first pendulum from upright (rad)
- $\theta_2$ - angle of second pendulum from upright (rad)
- $\dot{x}, \dot{\theta}_1, \dot{\theta}_2$ - corresponding velocities

**Equations of Motion:**

The nonlinear dynamics are derived using the Euler-Lagrange method, yielding:

```math
\mathbf{M}(\mathbf{q})\ddot{\mathbf{q}} + \mathbf{C}(\mathbf{q}, \dot{\mathbf{q}})\dot{\mathbf{q}} + \mathbf{G}(\mathbf{q}) + \mathbf{F}_{\text{friction}}\dot{\mathbf{q}} = \mathbf{B}u + \mathbf{d}(t)
```

where $\mathbf{q} = [x, \theta_1, \theta_2]^T$ (generalized coordinates).

**Inertia Matrix** $\mathbf{M}(\mathbf{q}) \in \mathbb{R}^{3 \times 3}$ (symmetric, positive definite):

```math
\mathbf{M} = \begin{bmatrix}
M_{11} & M_{12} & M_{13} \\
M_{21} & M_{22} & M_{23} \\
M_{31} & M_{32} & M_{33}
\end{bmatrix}
```

with elements (derived from kinetic energy):
- $M_{11} = m_0 + m_1 + m_2$
- $M_{12} = M_{21} = (m_1 r_1 + m_2 L_1)\cos\theta_1 + m_2 r_2 \cos\theta_2$
- $M_{13} = M_{31} = m_2 r_2 \cos\theta_2$
- $M_{22} = m_1 r_1^2 + m_2 L_1^2 + I_1$
- $M_{23} = M_{32} = m_2 L_1 r_2 \cos(\theta_1 - \theta_2) + I_2$
- $M_{33} = m_2 r_2^2 + I_2$

where $r_i$ = distance to center of mass, $I_i$ = moment of inertia.

**Coriolis/Centrifugal Matrix** $\mathbf{C}(\mathbf{q}, \dot{\mathbf{q}}) \in \mathbb{R}^{3 \times 3}$:

Captures velocity-dependent forces, including centrifugal terms $\propto \dot{\theta}_i^2$ and Coriolis terms $\propto \dot{\theta}_i \dot{\theta}_j$.

**Gravity Vector** $\mathbf{G}(\mathbf{q}) \in \mathbb{R}^3$:

```math
\mathbf{G} = \begin{bmatrix}
0 \\
-(m_1 r_1 + m_2 L_1)g\sin\theta_1 \\
-m_2 r_2 g \sin\theta_2
\end{bmatrix}
```

**Friction Vector** $\mathbf{F}_{\text{friction}}\dot{\mathbf{q}}$:

```math
\mathbf{F}_{\text{friction}} = \text{diag}(b_0, b_1, b_2) \cdot \dot{\mathbf{q}}
```

where $b_0, b_1, b_2$ are cart friction and joint damping coefficients.

**Control Input Matrix** $\mathbf{B} \in \mathbb{R}^3$:

```math
\mathbf{B} = [1, 0, 0]^T
```

indicating force applied to cart only (underactuated system: 1 input, 3 degrees of freedom).

**Disturbances** $\mathbf{d}(t) \in \mathbb{R}^3$:

External disturbances (wind, measurement noise, unmodeled dynamics).

### 2.2 System Parameters

**Physical Configuration (from config.yaml):**

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Cart mass | $m_0$ | 1.5 | kg |
| Pendulum 1 mass | $m_1$ | 0.2 | kg |
| Pendulum 2 mass | $m_2$ | 0.15 | kg |
| Pendulum 1 length | $L_1$ | 0.4 | m |
| Pendulum 2 length | $L_2$ | 0.3 | m |
| Pendulum 1 COM | $r_1$ | 0.2 | m |
| Pendulum 2 COM | $r_2$ | 0.15 | m |
| Pendulum 1 inertia | $I_1$ | 0.0081 | kg·m² |
| Pendulum 2 inertia | $I_2$ | 0.0034 | kg·m² |
| Gravity | $g$ | 9.81 | m/s² |
| Cart friction | $b_0$ | 0.2 | N·s/m |
| Joint 1 friction | $b_1$ | 0.005 | N·m·s/rad |
| Joint 2 friction | $b_2$ | 0.004 | N·m·s/rad |

**Key Properties:**
1. **Underactuated:** 1 control input ($u$), 3 degrees of freedom (cart, 2 pendulums)
2. **Unstable Equilibrium:** Upright position $(\theta_1, \theta_2) = (0, 0)$ is unstable
3. **Nonlinear:** $M(\mathbf{q})$ depends on angles; $\mathbf{G}(\mathbf{q})$ contains $\sin\theta_i$ terms
4. **Coupled:** Motion of cart affects both pendulums; pendulum 1 affects pendulum 2

### 2.3 Control Objectives

**Primary Objective:** Stabilize DIP system at upright equilibrium from small initial perturbations

**Formal Statement:**

Given initial condition $\mathbf{x}(0) = [x_0, \theta_{10}, \theta_{20}, 0, 0, 0]^T$ with $|\theta_{i0}| \leq \theta_{\max}$ (typically $\theta_{\max} = 0.05$ rad = 2.9°), design control law $u(t)$ such that:

1. **Asymptotic Stability:**
   ```math
   \lim_{t \to \infty} \|\mathbf{x}(t) - \mathbf{x}_{\text{eq}}\| = 0
   ```
   where $\mathbf{x}_{\text{eq}} = [0, 0, 0, 0, 0, 0]^T$ (equilibrium)

2. **Settling Time Constraint:**
   ```math
   \|\mathbf{x}(t) - \mathbf{x}_{\text{eq}}\| \leq 0.02 \|\mathbf{x}(0)\| \quad \forall t \geq t_s
   ```
   Target: $t_s < 3$ seconds (within 2% of equilibrium)

3. **Overshoot Constraint:**
   ```math
   \max_{t > 0} |\theta_i(t)| \leq \alpha |\theta_{i0}| \quad \text{for } i=1,2
   ```
   Target: $\alpha < 1.1$ (less than 10% overshoot)

4. **Control Input Bounds:**
   ```math
   |u(t)| \leq u_{\max} = 20 \text{ N}
   ```
   Prevent actuator saturation

5. **Real-Time Feasibility:**
   ```math
   t_{\text{compute}} < 50 \mu s
   ```
   For 10 kHz control loop (100 μs period), control law computation must complete in <50% of cycle

**Secondary Objectives:**

1. **Chattering Minimization:** Reduce high-frequency control switching to minimize actuator wear
2. **Energy Efficiency:** Minimize control effort $\int_0^{t_s} u^2(t) dt$
3. **Robustness:** Maintain performance under:
   - Model parameter uncertainty (±10-20% in masses, lengths, inertias)
   - External disturbances (sinusoidal, impulse, white noise)
   - Initial condition variations (±0.3 rad for challenging scenarios)

### 2.4 Problem Statement

**Problem:** Design and comparatively evaluate seven sliding mode control (SMC) variants for stabilization of the double-inverted pendulum system described in Section 2.1, subject to objectives in Section 2.3.

**Controllers to Evaluate:**
1. Classical SMC (boundary layer)
2. Super-Twisting Algorithm (STA-SMC)
3. Adaptive SMC (parameter estimation)
4. Hybrid Adaptive STA-SMC (mode-switching)
5. Swing-Up SMC (energy-based + stabilization)
6. Model Predictive Control (MPC, for comparison)
7. Combinations/variants

**Evaluation Criteria:**
- Computational efficiency (compute time, memory)
- Transient response (settling time, overshoot, convergence rate)
- Chattering characteristics (FFT analysis, amplitude, frequency)
- Energy consumption (control effort)
- Robustness (model uncertainty, disturbances, generalization)
- Theoretical guarantees (Lyapunov stability, convergence type)

**Constraints:**
1. All controllers operate on same physical system (parameters in Table 2.1)
2. Fair comparison: Same initial conditions, simulation parameters (dt = 0.01s, duration = 10s)
3. Same actuator limits ($|u| \leq 20$ N)
4. Real-time constraint (<50 μs compute time per control cycle)

**Assumptions:**
1. **Full State Measurement:** All 6 states ($x, \theta_1, \theta_2, \dot{x}, \dot{\theta}_1, \dot{\theta}_2$) measurable with negligible noise
2. **Matched Disturbances:** External disturbances enter through control channel: $\mathbf{d}(t) = \mathbf{B}d_u(t)$
3. **Bounded Disturbances:** $|\mathbf{d}(t)| \leq d_{\max}$ for known $d_{\max}$
4. **Small Angle Assumption (for linearization-based controllers):** Some controllers assume $|\theta_i| < 0.1$ rad during operation
5. **No Parameter Variations During Single Run:** System parameters fixed during 10s simulation (uncertainty tested across runs)

---

