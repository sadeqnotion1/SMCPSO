# Episode 02 - Sliding Surface Design: Building the Highway to Stability

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 8-10 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode explains the core design decision of the entire project - the sliding surface. Everything from Lyapunov proofs to PSO tuning is downstream of this choice. Understanding why we made this choice matters as much as knowing what the choice was.]**

## Opening: What Is a Sliding Surface?

In the last episode, we established our system - a six-dimensional state vector describing a double-inverted pendulum. Now the question is: how do you control it?

The Sliding Mode Control approach starts with a clever idea. Instead of trying to drive the full six-dimensional state to zero directly, we first define a lower-dimensional target surface in state space. If we can drive the system onto that surface and keep it there, the reduced dynamics on the surface are guaranteed to be stable. We have turned a hard six-dimensional stabilization problem into two simpler sub-problems: get to the surface, then stay on it.

Think of it like landing a plane. You do not try to go directly from cruise altitude to wheels on the runway in one motion. You first intercept the glide path - a defined approach trajectory - and then follow that path down. The glide path is our sliding surface. Once you are on it, the rest of the approach is governed by a much simpler set of dynamics.

## The Surface Equation

The sliding surface used across all four controllers in this project is:

sigma equals lambda-one times theta-one, plus lambda-two times theta-two, plus k-one times theta-one-dot, plus k-two times theta-two-dot.

Sigma is a scalar - a single number that summarizes the state of both pendulums. When sigma equals zero, you are on the surface. The surface is a weighted sum of the two pendulum angles and their angular velocities. Notably, cart position and velocity do not appear in sigma directly - they enter through the equations of motion when you differentiate sigma.

When sigma equals zero, what are the dynamics? The reduced-order system decouples into two independent first-order equations: theta-one-dot equals minus lambda-one over k-one times theta-one, and theta-two-dot equals minus lambda-two over k-two times theta-two. These are exponential decays. They are stable if and only if all four parameters are positive.

That gives the stability conditions: lambda-one, lambda-two, k-one, k-two must all be strictly greater than zero. These inequalities become hard lower bounds in PSO - every candidate set of gains must satisfy them, or it is immediately rejected with the maximum penalty.

## Why This Surface, Not Another?

The report explicitly documents the rejection of two alternatives. An advisor will almost certainly ask about this.

**Integral sliding surface.** This design augments sigma with an integral of the error. It eliminates steady-state offset - appealing in theory. It was rejected because adding an integrator state means the Lyapunov analysis must account for a seventh state variable. For a system already at six dimensions, this significantly increases the proof complexity without a proportional benefit - steady-state error in our simulation is already small.

**Terminal sliding surface.** This replaces the linear angular velocity term with e to the power p over q, where the ratio is a fraction less than one. Terminal surfaces guarantee finite-time convergence - which sounds better than asymptotic convergence. They were rejected because the fractional exponent creates a derivative singularity at the equilibrium. When the pendulum angle is exactly zero, the derivative of e to the p/q with p/q less than one blows up. That is a numerical problem in simulation and a physical problem on hardware where quantization noise ensures the state never sits exactly at zero.

**Linear surface.** This is what the project uses. The relative degree is exactly one - verified analytically. The Lyapunov analysis is tractable. PSO can tune all four surface parameters simultaneously. No numerical issues at equilibrium. This is the right tradeoff for a thesis-level system.

## The Relative Degree Check

Relative degree is a technical prerequisite for standard SMC - it must equal exactly one. It means: differentiate sigma once, and the control input u must appear explicitly.

Here is the check. Differentiate sigma with respect to time. The result contains theta-one-dot, theta-two-dot, and the angular accelerations theta-one-double-dot and theta-two-double-dot. Substitute the equations of motion: the accelerations depend on M-inverse times B times u, among other terms. The control u appears through the product L times M-inverse times B, where L is the vector zero, k-one, k-two.

This product is a scalar. For relative degree one, it must be nonzero. It equals k-one times the second row of M-inverse times B plus k-two times the third row. Since M is positive definite for any physical DIP configuration - any set of positive masses and lengths - its inverse is well-defined, and the product is nonzero. Relative degree one is confirmed.

If relative degree were two or higher, standard SMC would fail. You would need higher-order sliding mode methods, which are significantly more complex. The linear surface choice, combined with the DIP's physical structure, gives us exactly degree one.

## The Matching Condition

The matching condition is the assumption that makes SMC's disturbance rejection work. It states that external disturbances enter the system through the same input channel as the control signal.

For the DIP: the control force acts horizontally on the cart. External disturbances - floor vibration, parameter uncertainty, wind - also act through forces on the cart. When you write out sigma-dot, the disturbance d appears in the same term as u: L times M-inverse times B times the quantity u plus d. Because they enter together, the switching gain K can reject any disturbance whose magnitude is bounded by K. You do not need to know d - you just need K to be large enough.

This is not guaranteed in general. For a system where disturbances enter through a different channel than the control - say, a disturbance directly on a pendulum joint - standard SMC cannot reject it. The matching condition is an assumption, and the report states it explicitly. An advisor question worth preparing: is this assumption realistic? For our system - a cart with a horizontal force input and disturbances acting on that same cart - yes, it is reasonable.

## What This Means for PSO

The surface contributes four tunable parameters: lambda-one, lambda-two, k-one, k-two. PSO searches these in bounds of 2.0 to 30.0. The lower bound enforces the stability conditions with margin - no gain goes below 2.0, so all four stability inequalities are satisfied by construction.

These four parameters are shared by all four controllers. The sliding surface equation does not change between Classical SMC, STA, Adaptive, or Hybrid Adaptive. What varies is the control law - the function that maps sigma to a force. That is the subject of the next episode.

## Takeaway

The sliding surface converts a hard multi-dimensional stabilization problem into a one-dimensional reaching problem plus a stable reduced-order system. The linear form was chosen for mathematical cleanliness and numerical reliability. The matching condition justifies disturbance rejection. And the relative degree of one ensures standard SMC applies.

Next episode: four different controllers, one shared surface. How does each turn sigma into a force?

---

*Report references: Section 2.1, Equations eq:surface, eq:stability_cond.*
