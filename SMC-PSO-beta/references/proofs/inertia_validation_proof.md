# Physical & Mathematical Proof: Pendulum Moment of Inertia Constraints

This document provides the mathematical derivation and physical proof for the moment of inertia bounds configured in `config.yaml` and enforced by the plant configuration validation engine.

---

## 1. Mechanical Definitions & Assumptions

Consider a pendulum link modeled as a rigid body of:
- Mass $m$ [kg]
- Total length $l$ [m]
- Center-of-mass (COM) distance $d$ [m] from the pivot (for a uniform rod, $d = l/2$)

### 1.1 Moment of Inertia about Center of Mass ($I_{\mathrm{com}}$)
The moment of inertia of a rigid body about its center of mass ($I_{\mathrm{com}}$) depends on its geometry and mass distribution. For a uniform thin rod, it is:
$$I_{\mathrm{com}} = \frac{1}{12} m l^2$$

For any physically realistic rigid body, the moment of inertia about its center of mass must satisfy:
$$I_{\mathrm{com}} > 0$$

This is the only hard physical constraint on the center-of-mass moment of inertia.

### 1.2 Moment of Inertia about Pivot Point ($I_{\mathrm{pivot}}$)
According to the **Parallel Axis Theorem**, the moment of inertia of any rigid body about a pivot point parallel to the axis passing through its center of mass is:
$$I_{\mathrm{pivot}} = I_{\mathrm{com}} + m d^2$$

Substituting the thin rod definition of $I_{\mathrm{com}}$ and $d = l/2$ into the Parallel Axis Theorem yields:
$$I_{\mathrm{pivot}} = \frac{1}{12} m l^2 + m \left(\frac{l}{2}\right)^2 = \frac{1}{12} m l^2 + \frac{1}{4} m l^2 = \frac{1}{3} m l^2$$

---

## 2. Derivation of the Physical Inequality Constraint

Because $I_{\mathrm{com}} > 0$, we have:
$$I_{\mathrm{pivot}} - m d^2 = I_{\mathrm{com}} > 0$$

Therefore, the total moment of inertia about the pivot point must satisfy the strict inequality:
$$I_{\mathrm{pivot}} > m d^2$$

In the limiting case where the pendulum link is modeled as an infinitely thin point mass concentrated entirely at the center of mass ($I_{\mathrm{com}} \to 0$), the lower physical boundary for the pivot inertia is reached:
$$I_{\mathrm{pivot, min}} = m d^2$$

However, the configuration fields `pendulum1_inertia` and `pendulum2_inertia` in `config.yaml` represent the **center-of-mass moment of inertia** ($I_{\mathrm{com}}$), which is directly added to the structural link inertia in the equations of motion (e.g., $M_{22} = m_1 L_{c1}^2 + m_2 L_1^2 + I_{1,\mathrm{com}}$). Therefore, the appropriate physical constraint for the configuration validator is simply:
$$I_{\mathrm{com}} > 0$$

---

## 3. Application to Prasad et al. (2012) Parameters

The nominal masses and lengths configured in this Double-Inverted Pendulum (DIP) setup correspond to the experimental benchmark model described in:
- **Reference:** Prasad, L. B., Tyagi, B., & Gupta, H. O. (2012). *"Modelling and Simulation for Optimal Control of Nonlinear Inverted Pendulum Dynamical System Using PID Controller and LQR"*.

### 3.1 Prasad (2012) Original Parameters:
- Cart Mass ($m_0$): $1.5$ kg
- Pendulum 1 Mass ($m_1$): $0.2$ kg
- Pendulum 2 Mass ($m_2$): $0.15$ kg
- Pendulum 1 Length ($l_1$): $0.4$ m (Center of Mass distance $d_1 = 0.2$ m)
- Pendulum 2 Length ($l_2$): $0.3$ m (Center of Mass distance $d_2 = 0.15$ m)
- Pendulum 1 Center-of-Mass Moment of Inertia ($I_1$): $2.65 \times 10^{-3}$ kg·m²
- Pendulum 2 Center-of-Mass Moment of Inertia ($I_2$): $1.15 \times 10^{-3}$ kg·m²

### 3.2 Verification & Comparison Table:

| Parameter | Symbol | Prasad (2012) Value | config.yaml Value | Physical Lower Bound ($I_{\mathrm{com}} > 0$) | Validation Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Cart Mass | $m_0$ | $1.5$ kg | `1.5` | N/A | Pass |
| Link 1 Mass | $m_1$ | $0.2$ kg | `0.2` | N/A | Pass |
| Link 2 Mass | $m_2$ | $0.15$ kg | `0.15` | N/A | Pass |
| Link 1 Length | $l_1$ | $0.4$ m | `0.4` | N/A | Pass |
| Link 2 Length | $l_2$ | $0.3$ m | `0.3` | N/A | Pass |
| Link 1 COM | $d_1$ | $0.2$ m | `0.2` | N/A | Pass |
| Link 2 COM | $d_2$ | $0.15$ m | `0.15` | N/A | Pass |
| Link 1 COM Inertia | $I_{1,\mathrm{com}}$ | $2.65 \times 10^{-3}$ kg·m² | `0.00265` | $> 0$ | Pass |
| Link 2 COM Inertia | $I_{2,\mathrm{com}}$ | $1.15 \times 10^{-3}$ kg·m² | `0.00115` | $> 0$ | Pass |

### 3.3 Evaluation of Physical Bounds:

#### Pendulum 1:
- Center of Mass (COM) Inertia:
  $$I_{1,\mathrm{com}} = 0.00265\,\text{kg}\cdot\text{m}^2 > 0 \quad (\text{Physically Valid})$$
- Uniform Rod COM Inertia Estimate:
  $$I_{1,\mathrm{rod, com}} = \frac{1}{12} m_1 l_1^2 = \frac{1}{12} \cdot 0.2 \cdot (0.4)^2 \approx 0.002667\,\text{kg}\cdot\text{m}^2$$
  *Note:* The Prasad (2012) COM value ($0.00265$) matches the uniform rod approximation ($0.002667$) within a very tight tolerance (under 1% error).

#### Pendulum 2:
- Center of Mass (COM) Inertia:
  $$I_{2,\mathrm{com}} = 0.00115\,\text{kg}\cdot\text{m}^2 > 0 \quad (\text{Physically Valid})$$
- Uniform Rod COM Inertia Estimate:
  $$I_{2,\mathrm{rod, com}} = \frac{1}{12} m_2 l_2^2 = \frac{1}{12} \cdot 0.15 \cdot (0.3)^2 \approx 0.001125\,\text{kg}\cdot\text{m}^2$$
  *Note:* The Prasad (2012) COM value ($0.00115$) matches the uniform rod approximation ($0.001125$) within a very tight tolerance (under 3.3% error).

---

## 4. Codebase Validation & Alignment

The plant configuration validation engine, implemented in `src/plant/configurations/validation.py` (specifically within the `validate_inertia_consistency` method), checks that the moment of inertia for each link satisfies the physical limits.

The validation script enforces:
- `inertia > 0` (strict physical COM lower bound)
- `inertia <= mass * length**2` (conservative physical COM upper bound)

This ensures that the configured center-of-mass moments of inertia (`0.00265` and `0.00115`) pass validation while faithfully representing the real physical properties of the Prasad (2012) benchmark system.
