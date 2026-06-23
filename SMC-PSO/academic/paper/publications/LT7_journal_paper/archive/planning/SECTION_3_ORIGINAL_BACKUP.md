## 3. Controller Design

This section presents the control law design for each of the seven SMC variants evaluated in this study. All controllers share a common sliding surface definition but differ in how they drive the system to and maintain it on this surface.

### 3.1 Sliding Surface (Common to All SMC Variants)

**Definition:**

The sliding surface $\sigma: \mathbb{R}^6 \to \mathbb{R}$ combines pendulum angle errors and their derivatives:

```math
\sigma = \lambda_1 \theta_1 + \lambda_2 \theta_2 + k_1 \dot{\theta}_1 + k_2 \dot{\theta}_2
```

where:
- $\lambda_1, \lambda_2 > 0$ - position error weights
- $k_1, k_2 > 0$ - velocity error weights

**Physical Interpretation:**

The sliding surface represents a weighted combination of pendulum state errors. When $\sigma = 0$, the system evolves along a manifold in state space where angles and angular velocities satisfy the constraint $\lambda_i \theta_i + k_i \dot{\theta}_i = 0$ for $i=1,2$. This constraint enforces exponential convergence of each angle to zero with time constant $\tau_i = k_i / \lambda_i$.

**Design Philosophy:**

1. **Reaching Phase:** Drive system toward sliding surface ($\sigma \to 0$)
2. **Sliding Phase:** Maintain system on surface ($\sigma = 0$), ensuring exponential convergence to equilibrium
3. **Steady-State:** System remains at equilibrium ($\theta_1 = \theta_2 = 0$)

---

### 3.2 Classical Sliding Mode Control

**Control Law:**

```math
u = u_{\text{eq}} - K \cdot \text{sat}\left(\frac{\sigma}{\epsilon}\right) - k_d \cdot \sigma
```

where:
- $u_{\text{eq}}$ - equivalent control (model-based feedforward)
- $K > 0$ - switching gain (drives system to sliding surface)
- $\epsilon > 0$ - boundary layer width (chattering reduction)
- $k_d \geq 0$ - derivative gain (damping)
- $\text{sat}(\cdot)$ - saturation function (continuous approximation of sign function)

**Equivalent Control:**

The equivalent control compensates for known dynamics:

```math
u_{\text{eq}} = (L M^{-1} B)^{-1} \left[ L M^{-1}(C\dot{q} + G) - \lambda_1 \dot{\theta}_1 - \lambda_2 \dot{\theta}_2 \right]
```

where:
- $L = [0, k_1, k_2]$ - sliding surface gradient vector
- $M, C, G$ - inertia, Coriolis, gravity matrices from Section 2
- $B = [1, 0, 0]^T$ - control input matrix

**Saturation Function (Boundary Layer):**

Two options implemented:

1. **Hyperbolic Tangent (Default):**
   ```math
   \text{sat}(\sigma/\epsilon) = \tanh(\sigma/\epsilon)
   ```
   Smooth transition, maintains control authority near $\sigma=0$

2. **Linear Saturation:**
   ```math
   \text{sat}(\sigma/\epsilon) = \begin{cases}
   \sigma/\epsilon & |\sigma| \leq \epsilon \\
   \text{sign}(\sigma) & |\sigma| > \epsilon
   \end{cases}
   ```
   Piecewise linear, sharper switching

**Design Parameters:**

| Parameter | Symbol | Typical Value | Purpose |
|-----------|--------|---------------|---------|
| Sliding gains | $k_1, k_2$ | 5.0, 3.0 | Surface gradient |
| Convergence rates | $\lambda_1, \lambda_2$ | 10.0, 8.0 | Angle convergence speed |
| Switching gain | $K$ | 15.0 | Reaching phase robustness |
| Derivative gain | $k_d$ | 2.0 | Damping |
| Boundary layer | $\epsilon$ | 0.02 | Chattering reduction |

**Advantages:**
- Simple implementation (6 gains)
- Fastest computation (18.5 μs, Section 7.1)
- Well-understood theory
- Good energy efficiency (12.4 J, Section 7.4)

**Disadvantages:**
- Moderate chattering (index 8.2, Section 7.3)
- Larger overshoot (5.8%, Section 7.2)
- Boundary layer introduces steady-state error

---

### 3.3 Super-Twisting Algorithm (STA-SMC)

**Control Law:**

STA employs a continuous 2nd-order sliding mode algorithm:

```math
\begin{aligned}
u &= u_{\text{eq}} + u_{\text{STA}} \\
u_{\text{STA}} &= -K_1 |\sigma|^{1/2} \text{sign}(\sigma) + z \\
\dot{z} &= -K_2 \text{sign}(\sigma)
\end{aligned}
```

where:
- $K_1, K_2 > 0$ - STA algorithm gains (satisfy Lyapunov conditions)
- $z$ - integral state (provides continuous control action)
- $\text{sign}(\sigma)$ - smoothed via saturation function: $\text{sign}(\sigma) \approx \tanh(\sigma/\epsilon)$

**Key Features:**

1. **Continuous Control:** Unlike classical SMC, $u_{\text{STA}}$ is continuous (no discontinuity at $\sigma=0$)
2. **Finite-Time Convergence:** Guaranteed convergence to $\sigma=0$ in finite time (not just asymptotic)
3. **Chattering Reduction:** Continuous action inherently eliminates chattering

**Gain Selection (Lyapunov-Based):**

For stability, gains must satisfy:

```math
K_2 > \frac{2 \bar{d}}{\epsilon}, \quad K_1 > \sqrt{2 K_2 \bar{d}}
```

where $\bar{d}$ is the upper bound on disturbances.

**Convergence Time Estimate:**

Upper bound on reaching time:

```math
T_{\text{reach}} \leq \frac{2 |\sigma(0)|^{1/2}}{K_1 - \sqrt{2 K_2 \bar{d}}}
```

**Design Parameters:**

| Parameter | Symbol | Typical Value | Purpose |
|-----------|--------|---------------|---------|
| Algorithm gain 1 | $K_1$ | 12.0 | Proportional to $\|\sigma\|^{1/2}$ |
| Algorithm gain 2 | $K_2$ | 8.0 | Integral term (sign of $\sigma$) |
| Boundary layer | $\epsilon$ | 0.01 | Sign function smoothing |

**Advantages:**
- Best overall performance (1.82s settling, 2.3% overshoot)
- Lowest chattering (index 2.1, 74% reduction vs Classical)
- Most energy-efficient (11.8 J)
- Finite-time convergence guarantee

**Disadvantages:**
- +31% compute overhead vs Classical (24.2 μs)
- More complex gain tuning (Lyapunov conditions)
- Less intuitive than classical SMC

---

### 3.4 Adaptive Sliding Mode Control

**Control Law:**

```math
\begin{aligned}
u &= u_{\text{eq}} - K(t) \cdot \text{sat}\left(\frac{\sigma}{\epsilon}\right) - k_d \cdot \sigma \\
\dot{K}(t) &= \begin{cases}
\gamma |\sigma| & |\sigma| > \delta \\
-\beta (K - K_{\text{init}}) & |\sigma| \leq \delta
\end{cases}
\end{aligned}
```

where:
- $K(t)$ - time-varying adaptive gain
- $\gamma > 0$ - adaptation rate (increase when $|\sigma|$ large)
- $\beta > 0$ - leak rate (decay toward $K_{\text{init}}$ when $|\sigma|$ small)
- $\delta > 0$ - dead-zone threshold
- $K_{\text{init}}$ - nominal gain value

**Adaptation Mechanism:**

1. **Outside Dead-Zone ($|\sigma| > \delta$):** Gain increases proportionally to sliding surface magnitude, providing more control authority when far from surface
2. **Inside Dead-Zone ($|\sigma| \leq \delta$):** Gain decays toward nominal value, preventing unbounded growth

**Bounded Gain Constraint:**

```math
K_{\min} \leq K(t) \leq K_{\max}
```

Prevents gain saturation or underflow.

**Design Parameters:**

| Parameter | Symbol | Typical Value | Purpose |
|-----------|--------|---------------|---------|
| Adaptation rate | $\gamma$ | 5.0 | Gain increase speed |
| Leak rate | $\beta$ | 0.1 | Decay to nominal |
| Dead-zone | $\delta$ | 0.01 | Adaptation threshold |
| Initial gain | $K_{\text{init}}$ | 10.0 | Nominal switching gain |
| Gain bounds | $K_{\min}, K_{\max}$ | 5.0, 50.0 | Saturation limits |

**Advantages:**
- Adapts to model uncertainty online
- Predicted best robustness to parameter errors (15% tolerance, Section 8.1)
- Bounded gains prevent instability

**Disadvantages:**
- Slowest settling (2.35s, Section 7.2)
- Highest chattering (index 9.7, Section 7.3)
- Highest energy (13.6 J, +15% vs STA)
- Most complex computation (31.6 μs)

---

### 3.5 Hybrid Adaptive STA-SMC

**Control Law:**

Hybrid controller switches between STA mode and Adaptive mode based on sliding surface magnitude:

```math
u = \begin{cases}
u_{\text{STA}} & |\sigma| > \sigma_{\text{switch}} \quad \text{(Far from surface)} \\
u_{\text{Adaptive}} & |\sigma| \leq \sigma_{\text{switch}} \quad \text{(Near surface)}
\end{cases}
```

where:
- $u_{\text{STA}}$ - STA control law (Section 3.3)
- $u_{\text{Adaptive}}$ - Adaptive control law (Section 3.4)
- $\sigma_{\text{switch}}$ - mode switching threshold

**Switching Logic:**

1. **Reaching Phase ($|\sigma|$ large):** Use STA for fast, chattering-free convergence
2. **Sliding Phase ($|\sigma|$ small):** Use Adaptive for robustness to model uncertainty
3. **Hysteresis:** Implement hysteresis band to prevent chattering between modes

**Mode Transition:**

```math
\text{Mode} = \begin{cases}
\text{STA} & |\sigma| > \sigma_{\text{switch}} + \Delta \\
\text{Adaptive} & |\sigma| < \sigma_{\text{switch}} - \Delta \\
\text{Previous Mode} & \sigma_{\text{switch}} - \Delta \leq |\sigma| \leq \sigma_{\text{switch}} + \Delta
\end{cases}
```

where $\Delta$ is hysteresis margin.

**Design Parameters:**

| Parameter | Symbol | Typical Value | Purpose |
|-----------|--------|---------------|---------|
| Switch threshold | $\sigma_{\text{switch}}$ | 0.05 | Mode selection |
| Hysteresis margin | $\Delta$ | 0.01 | Prevent mode chattering |
| STA gains | $K_1, K_2$ | 12.0, 8.0 | Reaching phase |
| Adaptive gains | $\gamma, \beta$ | 5.0, 0.1 | Sliding phase |

**Advantages:**
- Balanced performance (1.95s settling, 3.5% overshoot)
- Best predicted robustness (16% model uncertainty tolerance)
- Good disturbance rejection (89% attenuation)
- Combines STA speed with Adaptive robustness

**Disadvantages:**
- Complex switching logic requires validation
- Moderate compute overhead (26.8 μs)
- Requires tuning both STA and Adaptive gains

---

### 3.6 Swing-Up SMC

**Two-Phase Control:**

Swing-up SMC operates in two distinct modes:

**Phase 1: Swing-Up (Energy-Based Control)**

When total system energy $E < E_{\text{threshold}}$:

```math
u_{\text{swing}} = k_{\text{swing}} \cos(\theta_1) \dot{\theta}_1
```

where:
- $k_{\text{swing}} > 0$ - swing-up gain
- Energy pumping: Adds energy when $\cos(\theta_1) \dot{\theta}_1 > 0$ (constructive phase)

**Phase 2: Stabilization (SMC)**

When $E \geq E_{\text{threshold}}$ and $|\theta_1|, |\theta_2| < \theta_{\text{switch}}$:

```math
u_{\text{stabilize}} = u_{\text{SMC}}(\theta_1, \theta_2, \dot{\theta}_1, \dot{\theta}_2)
```

Uses any SMC variant (typically Classical or STA) for stabilization.

**Energy Calculation:**

```math
E = \frac{1}{2}m_0 \dot{x}^2 + \frac{1}{2}I_1 \dot{\theta}_1^2 + \frac{1}{2}I_2 \dot{\theta}_2^2 - m_1 g r_1 \cos\theta_1 - m_2 g (L_1 \cos\theta_1 + r_2 \cos\theta_2)
```

**Mode Transition Logic:**

```math
\text{Mode} = \begin{cases}
\text{Swing-Up} & E < E_{\text{target}} \text{ OR } |\theta_1| > 0.3 \text{ rad} \\
\text{Stabilize} & E \geq E_{\text{target}} \text{ AND } |\theta_1|, |\theta_2| < 0.1 \text{ rad}
\end{cases}
```

**Design Parameters:**

| Parameter | Symbol | Typical Value | Purpose |
|-----------|--------|---------------|---------|
| Swing gain | $k_{\text{swing}}$ | 20.0 | Energy pumping rate |
| Target energy | $E_{\text{target}}$ | 95% of upright energy | Transition threshold |
| Angle threshold | $\theta_{\text{switch}}$ | 0.1 rad (5.7°) | Stabilizer activation |

**Advantages:**
- Global controller (works from any initial condition)
- Can bring pendulum from downward to upward position
- Combines energy-based and model-based control

**Disadvantages:**
- Complex mode logic requires careful tuning
- Swing-up phase performance not guaranteed (heuristic energy pumping)
- Not applicable to small perturbation stabilization (this study's focus)

---

### 3.7 Model Predictive Control (MPC)

**Optimization Problem:**

At each time step, solve finite-horizon optimal control problem:

```math
\begin{aligned}
\min_{u(0), \ldots, u(N-1)} \quad & J = \sum_{k=0}^{N-1} \left[ \mathbf{x}(k)^T Q \mathbf{x}(k) + u(k)^T R u(k) \right] + \mathbf{x}(N)^T Q_f \mathbf{x}(N) \\
\text{subject to} \quad & \mathbf{x}(k+1) = f(\mathbf{x}(k), u(k)) \quad k=0, \ldots, N-1 \\
& |u(k)| \leq u_{\max} \quad k=0, \ldots, N-1 \\
& \mathbf{x}(0) = \mathbf{x}_{\text{current}}
\end{aligned}
```

where:
- $N$ - prediction horizon (number of future time steps)
- $Q, R, Q_f$ - state, input, terminal cost weight matrices
- $f(\cdot, \cdot)$ - discretized nonlinear dynamics (Section 2)
- $u_{\max}$ - actuator limit

**Linearization (For Computational Efficiency):**

Approximate nonlinear dynamics around current trajectory:

```math
\mathbf{x}(k+1) \approx A(k) \mathbf{x}(k) + B(k) u(k) + \mathbf{c}(k)
```

where $A(k), B(k)$ are Jacobians computed via finite differences.

**Implementation:**

Uses `cvxpy` library to solve quadratic program (QP) at each time step.

**Design Parameters:**

| Parameter | Symbol | Typical Value | Purpose |
|-----------|--------|---------------|---------|
| Horizon | $N$ | 20 steps (0.2s) | Prediction window |
| State weight | $Q$ | $\text{diag}(1, 50, 50, 0.1, 5, 5)$ | Penalize angles heavily |
| Input weight | $R$ | 0.01 | Control effort penalty |
| Terminal weight | $Q_f$ | $100 \times Q$ | Final state penalty |

**Advantages:**
- Explicit handling of constraints (actuator limits, state bounds)
- Optimal control over finite horizon
- Can incorporate future reference trajectories

**Disadvantages:**
- Computationally expensive (requires external optimizer)
- Not self-contained (depends on `cvxpy`)
- Real-time feasibility questionable for 10 kHz control
- Excluded from main comparative analysis (dependency issue)

---

### 3.8 Summary and Comparison

**Table 3.1: Controller Characteristics Comparison**

| Controller | Control Type | Continuity | Gains | Computation | Key Feature |
|------------|-------------|------------|-------|-------------|-------------|
| **Classical SMC** | Discontinuous (smoothed) | $C^0$ | 6 | 18.5 μs | Boundary layer chattering reduction |
| **STA SMC** | 2nd-order sliding mode | $C^1$ | 2 + sliding | 24.2 μs | Finite-time convergence, continuous |
| **Adaptive SMC** | Adaptive gain | $C^0$ | 5 + $K(t)$ | 31.6 μs | Online parameter estimation |
| **Hybrid STA** | Mode-switching | $C^0$ | 8 + mode | 26.8 μs | Combines STA + Adaptive |
| **Swing-Up SMC** | Energy + SMC | $C^0$ | 3 + stabilizer | Variable | Global control (swing-up + stabilize) |
| **MPC** | Optimal control | $C^{\infty}$ | N/A (weights) | >>100 μs | Constrained optimization |

**Convergence Guarantees:**

| Controller | Stability Type | Convergence | Proof in Section 4 |
|------------|---------------|-------------|-------------------|
| Classical SMC | Asymptotic | Exponential ($e^{-\lambda t}$) | 4.1 |
| STA SMC | Finite-time | Finite-time ($T < T_{\max}$) | 4.2 |
| Adaptive SMC | Asymptotic | Exponential with adaptive gains | 4.3 |
| Hybrid STA | ISS | Finite-time + Adaptive | 4.4 |
| Swing-Up SMC | Multiple Lyapunov | Phase-dependent | 4.5 |
| MPC | Optimal | Depends on horizon | (Not proven) |

**Design Complexity:**

1. **Simplest:** Classical SMC (6 scalar gains)
2. **Moderate:** STA SMC (2 gains + Lyapunov conditions), Adaptive SMC (5 gains + adaptation law)
3. **Complex:** Hybrid STA (8 gains + switching logic)
4. **Most Complex:** Swing-Up SMC (energy calculation + mode transitions), MPC (weight matrices + optimization)

---

