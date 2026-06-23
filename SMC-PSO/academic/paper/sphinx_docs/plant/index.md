# Plant Models Documentation **Double Inverted Pendulum Dynamics Models**

## Overview This section provides documentation for the double inverted pendulum (DIP) plant models, including simplified, full-fidelity, and low-rank dynamics implementations.

## Technical Guides

```{toctree}
:maxdepth: 2
:caption: Plant Dynamics Documentation

models_guide
```

**Plant Models Guide** - Complete documentation covering:

- **3 Dynamics Models**: Simplified, Full-Fidelity, and Low-Rank implementations
- **Mathematical Foundations**: Lagrangian mechanics and equations of motion
- **Configuration System**: Type-safe parameter validation
- **Physics Computation**: Mass matrix, Coriolis forces, gravity terms
- **Numerical Stability**: Adaptive regularization and matrix conditioning
- **Usage Examples**: Integration with controllers and simulation
- **Performance Optimization**: Numba JIT compilation and matrix caching

---

## Quick Reference

### Model Comparison | Model Type | Fidelity | Speed | Use Case ||------------|----------|-------|----------|

| **Simplified** | Medium | Fast | Controller development, PSO optimization |
| **Full** | High | Moderate | Research-grade analysis, studies |
| **Low-Rank** | Low | Very Fast | Educational demonstrations, rapid prototyping |

### State Vector $$\mathbf{q} = \begin{bmatrix} x & \theta_1 & \theta_2 & \dot{x} & \dot{\theta}_1 & \dot{\theta}_2 \end{bmatrix}^T

$$ Where:
- $x$ - Cart position (m)
- $\theta_1$ - Pendulum 1 angle from upright (rad)
- $\theta_2$ - Pendulum 2 angle from upright (rad)
- $\dot{x}$ - Cart velocity (m/s)
- $\dot{\theta}_1$ - Pendulum 1 angular velocity (rad/s)
- $\dot{\theta}_2$ - Pendulum 2 angular velocity (rad/s)

### Equations of Motion $$M(\mathbf{q}) \ddot{\mathbf{q}} + C(\mathbf{q}, \dot{\mathbf{q}}) \dot{\mathbf{q}} + G(\mathbf{q}) = \mathbf{u} + \mathbf{d}

$$

---

## Usage Examples

### Basic Dynamics Evaluation

```python src.plant.models.simplified import SimplifiedDIPDynamics, SimplifiedDIPConfig # Create configuration
config = SimplifiedDIPConfig.create_default() # Initialize dynamics
dynamics = SimplifiedDIPDynamics( config, enable_fast_mode=True, enable_monitoring=True
) # Compute dynamics
state = [0.1, 0.05, -0.03, 0.0, 0.0, 0.0]
control = [5.0]
result = dynamics.compute_dynamics(state, control)
```

### Energy Conservation Validation

```python
from scipy.integrate import solve_ivp def dynamics_ode(t, state): control = [0.0] result = dynamics.compute_dynamics(state, control, time=t) return result.state_derivative if result.success else np.zeros(6) # Integrate
sol = solve_ivp(dynamics_ode, t_span=[0, 5], y0=state0, method='RK45', rtol=1e-8) # Check energy conservation
E0 = dynamics.compute_total_energy(state0)
E_final = dynamics.compute_total_energy(sol.y[:, -1])
energy_drift = abs(E_final - E0) / E0
print(f"Energy drift: {energy_drift:.2%}")
```

---

## Related Documentation

- **{doc}`../mathematical_foundations/index`** - Lagrangian mechanics and dynamics derivations
- **{doc}`../controllers/index`** - Controller integration with dynamics models
- **{doc}`../optimization_simulation/guide`** - Simulation infrastructure and integration methods
- **{doc}`../reference/plant/index`** - API reference for plant models

---

**Documentation Version:** 1.0 (Week 3 Complete)
**Last Updated:** 2025-10-04
**Coverage:** Simplified, Full, and Low-Rank DIP dynamics models
---

**Navigation**: Return to [Master Navigation Hub](../NAVIGATION.md) | Browse all [Documentation Categories](../index.md)
