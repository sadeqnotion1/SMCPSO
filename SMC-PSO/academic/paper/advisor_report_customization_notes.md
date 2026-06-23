# Advisor Report Customization Notes

## Section 1.1 - State Vector and Coordinate Definition

- Add explicit units for each state variable:
  - `x` (m), `theta_1` and `theta_2` (rad), `dx` (m/s), `dtheta_1` and `dtheta_2` (rad/s).
- Add clear sign conventions:
  - positive cart motion direction,
  - positive angular direction (clockwise or counterclockwise).
- Define the zero-angle reference explicitly (upright vertical frame).
- Add target equilibrium state:
  - `x_star = [0, 0, 0, 0, 0, 0]^T` (or mission-specific value).
- Add error-state definition:
  - `e = x - x_star`.
- Add state bounds/safety limits used in simulation or HIL runs.
- Add measured output vector `y` and note sensor/estimation source.
- Add (or reference) a coordinate-frame figure.

## Section 1.2 - Equations of Motion

- Add modeling assumptions in one short paragraph:
  - planar motion, rigid links, actuator limits, friction assumptions.
- Keep the compact matrix equation, then add first-order state-space form:
  - `dot(x) = f(x) + g(x)u + d(t)` (if disturbance term is used).
- State structural properties used by control proofs:
  - `M(q)` is symmetric positive definite,
  - `dot(M) - 2C` skew-symmetric property (if used in Lyapunov analysis).
- Clarify exactly which terms are included/excluded in each model:
  - full nonlinear validation model,
  - simplified PSO model.
- Add uncertainty and disturbance model definitions:
  - parameter perturbation ranges, external force profile, noise assumptions.
- Add linearization statement with operating point and method:
  - around upright equilibrium, finite-difference Jacobian or symbolic form.
- Add numerical implementation details for reproducibility:
  - solver, integration step, sample rate, saturation handling.
- Add a one-line validation note:
  - analytical energy checks / numerical consistency checks against benchmark trajectories.

