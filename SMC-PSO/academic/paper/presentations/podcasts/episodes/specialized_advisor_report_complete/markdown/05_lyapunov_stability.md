# Episode 05 - Lyapunov Stability: The Mathematical Proof That It Works

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 10-12 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: Lyapunov stability is the theoretical backbone of the thesis. This episode covers the proofs for all six controllers. The key to explaining them confidently: understand what V represents physically, and understand why the symbolic constants beta and eta are NOT fixed numbers.]**

## Opening: Why Lyapunov?

Simulation results showing a controller working are not a proof. They are evidence. An advisor will ask: can you prove, mathematically, that your controller will stabilize the system - not just for the specific initial conditions you tested, but in general?

That is what Lyapunov stability theory provides. The basic idea is elegant: find a function V of the state that behaves like energy. It should be positive - like energy, it is always non-negative. And its time derivative along system trajectories should be negative - like energy dissipating from a damped system. If you can find such a function and show the derivative is negative, stability follows without needing to solve the differential equations.

The full proofs are in the theory documentation - 1427 lines, nine theorems, five lemmas. This episode covers the key results from the report.

## A Critical Clarification: What Are Beta and Eta?

Before the controller proofs, the report makes a point worth stating clearly because it will come up.

The stability inequalities involve constants beta, eta, c-one, c-two, alpha-one, alpha-two. These are not fixed numbers. They are state-dependent or gain-dependent quantities.

Specifically, beta equals L times M-inverse times B - the same product from the relative degree check. This depends on the current pendulum configuration through M-inverse. As the pendulums swing, beta changes. The proofs establish that beta stays positive along all physically valid trajectories - which it does, because M is always positive definite.

Similarly, eta equals K minus d-bar, where K is the switching gain and d-bar bounds the disturbance. This is positive by design: we require K to exceed d-bar.

Understanding this matters for advisor questions. "What is the value of beta?" is not the right question. The right answer: beta is a configuration-dependent scalar that stays positive throughout the motion, and the proof establishes this explicitly.

## Classical SMC: Asymptotic Exponential Stability

Lyapunov function: V equals one-half times sigma-squared.

This is the simplest possible candidate - the squared value of the sliding surface. It is positive when sigma is nonzero, and zero exactly on the surface.

Time derivative: V-dot equals sigma times sigma-dot. Substituting the closed-loop dynamics, the report shows:

V-dot is less than or equal to minus beta times eta times the absolute value of sigma, minus beta times k-d times sigma-squared.

Both terms are negative outside the boundary layer. The first term - linear in the absolute value of sigma - drives reaching. The second term - quadratic in sigma - provides exponential convergence once near the surface.

Stability type: exponential asymptotic. The reaching time satisfies t-reach is less than or equal to the absolute value of sigma at zero, divided by eta times beta.

Numerical validation: 96.2 percent of simulation samples satisfy V-dot less than zero outside the boundary layer. The remaining 3.8 percent occur during the initial reaching phase when the trajectory is crossing the boundary layer - sigma is between negative epsilon and positive epsilon. This is expected behavior. It does not indicate instability.

If an advisor asks why not 100 percent: the boundary layer is specifically designed to allow smooth behavior inside it. V-dot is not required to be negative inside the boundary layer - that is the whole point of introducing epsilon.

## STA-SMC: Finite-Time Convergence

Lyapunov function: V-STA equals the absolute value of sigma, plus one over two K-two times z-squared, where z equals u-two, the integral component.

This is the Moreno-Osorio Lyapunov structure for second-order sliding modes.

The time derivative satisfies: V-dot-STA is less than or equal to minus c-one times the norm of xi to the three-halves power, plus c-two times L, where xi is the vector of absolute-sigma to the one-half times sign-sigma and z, and L is the Lipschitz constant of the disturbance derivative.

When L equals zero - no time-varying disturbance - V-dot is strictly negative and finite-time convergence is guaranteed. This is the key result: unlike Classical SMC which converges asymptotically, STA drives sigma exactly to zero in finite time T-f.

The gain conditions required: K-one must exceed two times the square root of two d-bar over beta, and K-two must exceed d-bar over beta, and K-one must exceed K-two.

The nominal gains K-one equals 8, K-two equals 4 satisfy these conditions. The robust gains K-one equals 2.02, K-two equals 6.67 do not satisfy K-one greater than K-two - which is the documented open issue.

An explicit closed-form bound for T-f on the DIP is not derived in the report. It would require bounding beta over the state trajectory, which varies with configuration. The experimental result: convergence in 1.82 seconds for typical initial conditions, 16 percent faster than Classical SMC at 2.15 seconds.

## Adaptive SMC: Asymptotic with Bounded Gain

Lyapunov function: V-ad equals one-half sigma-squared, plus one over two gamma times K-tilde-squared, where K-tilde equals K-of-t minus K-star, the error between the current adaptive gain and the ideal gain K-star.

This is a composite Lyapunov function - it includes both the state error through sigma and the parameter estimation error through K-tilde. This is the standard approach for adaptive control stability proofs.

The time derivative satisfies: V-dot-ad is less than or equal to minus eta times the absolute value of sigma, which implies sigma converges to zero and K-of-t remains bounded.

Stability type: asymptotic convergence of the state, with bounded adaptive gain. Numerical validation: 100 percent of simulation samples show K-of-t within the bounds K-min equals 0.1 to K-max equals 100.

## Hybrid Adaptive STA: Input-to-State Stable

Lyapunov function: V-hyb equals one-half sigma-squared, plus k-one-tilde-squared over two gamma-one, plus k-two-tilde-squared over two gamma-two, plus one-half u-int-squared.

This extends the composite structure to include both adaptive gain errors and the integral state u-int.

Time derivative: V-dot-hyb is less than or equal to minus alpha-one times V-hyb, plus alpha-two times the norm of the disturbance vector w.

This is Input-to-State Stability, or ISS. The system is not unconditionally stable - the term alpha-two times the disturbance norm can be positive. But if the disturbance is bounded, the state remains bounded. ISS is a weaker but still rigorous stability notion appropriate for systems subject to persistent disturbances.

Numerical validation: all signals bounded, zero emergency resets during nominal conditions.

## Swing-Up SMC and MPC

For completeness. Swing-Up uses a switched Lyapunov function: an energy-based function during swing-up phase, one-half sigma-squared during stabilization phase. Global stability is proven, and hysteresis in the switching prevents Zeno behavior - finite switching is guaranteed.

MPC uses the optimal cost-to-go J-k-star as the Lyapunov function. Stability requires recursive feasibility - the optimization must have a solution at every time step. Under this assumption, the optimal cost decreases monotonically.

## Summary

| Controller | Lyapunov V | Stability Type | Settling |
|---|---|---|---|
| Classical SMC | half sigma-squared | Exponential asymptotic | 2.15 s |
| STA-SMC | abs-sigma plus z-squared | Finite-time | 1.82 s |
| Adaptive SMC | half sigma-squared plus gain error | Asymptotic, bounded gain | 2.35 s |
| Hybrid Adaptive | extended composite | ISS | 1.95 s |
| Swing-Up | energy-based switched | Global | -- |
| MPC | optimal cost J-star | Asymptotic | -- |

Convergence ordering fastest to slowest: STA, Hybrid, Classical, Adaptive.

Next episode: moving from theory to experiment - how were the Monte Carlo benchmarks designed and run?

---

*Report references: Section 4.1 through 4.7, Equations eq:lyap_classical, eq:lyap_classical_dot, eq:lyap_sta, eq:sta_conditions.*
