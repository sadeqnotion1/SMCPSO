#### 2.1.1 Physical System Description

**Figure 2.1:** Double-inverted pendulum system schematic

```
                     ┌─────┐ m₂, L₂, I₂
                     │  ●  │ (Pendulum 2)
                     └──┬──┘
                        │ θ₂
                        │
                   ┌────┴────┐ m₁, L₁, I₁
                   │    ●    │ (Pendulum 1)
                   └────┬────┘
                        │ θ₁
    ════════════════════┼════════════════════ Track
                    ┌───┴───┐
                    │   ●   │ m₀ (Cart)
                    └───────┘
                      ← u (Control Force)

    Coordinate System:
    - x: horizontal cart position (rightward positive)
    - θ₁, θ₂: angles from upright (counterclockwise positive)
    - r₁, r₂: centers of mass along each link
    - b₀: cart friction, b₁, b₂: joint friction
```

**System Configuration:**
- **Cart:** Moves along 1D horizontal track (±1m travel limit in simulation)
- **Pendulum 1:** Rigid link pivoting at cart position, free to rotate 360° (±π rad)
- **Pendulum 2:** Rigid link pivoting at end of pendulum 1, free to rotate 360°
- **Actuation:** Single horizontal force u applied to cart (motor-driven)
- **Sensing:** Encoders measure cart position x and angles θ1, θ2; velocities estimated via differentiation

**Physical Constraints:**
- Mass distribution: m0 > m1 > m2 (cart heaviest, tip lightest - typical configuration)
- Length ratio: L1 > L2 (longer base link provides larger control authority)
- Inertia moments: I1 > I2 (proportional to m·L²)

**Model Derivation Approach:**

We derive the equations of motion using the **Euler-Lagrange method** (rather than Newton-Euler) because:
1. Lagrangian mechanics automatically handles constraint forces (no need to compute reaction forces at joints)
2. Kinetic/potential energy formulation is systematic for multi-link systems
3. Resulting M-C-G structure is standard for robot manipulators, enabling direct application of nonlinear control theory

The Lagrangian L = T - V (kinetic minus potential energy) yields equations via:
```math
\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_i}\right) - \frac{\partial L}{\partial q_i} = Q_i
```
where Q_i are generalized forces (control input u for cart, zero for unactuated joints).

---

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

**Nonlinearity Characterization:**

The DIP system exhibits **strong nonlinearity** across multiple mechanisms:

1. **Configuration-Dependent Inertia:**
   - M12 varies by up to 40% as θ1 changes from 0 to π/4 (for m1=0.2kg, L1=0.4m)
   - M23 varies by up to 35% as θ1-θ2 changes (coupling between pendulum links)
   - This creates **state-dependent effective mass**, making control gains tuned at θ=0 potentially ineffective at θ=±0.3 rad

2. **Trigonometric Nonlinearity in Gravity:**
