# Episode 03 - Four Controllers, One Surface: The Control Laws

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 10-12 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode goes controller by controller through the actual math. Each controller is a distinct philosophy for driving sigma to zero. Know the equations, know the rationale for each design parameter, and know the one open issue - the STA robust gain inconsistency.]**

## Opening: Same Surface, Four Philosophies

In the previous episode, we designed the sliding surface sigma. Every controller in this project shares that same surface. What differs is the control law - the function that takes sigma as input and outputs a force to apply to the cart.

Think of sigma as a car's speedometer. The speedometer is the same in every car. What differs is the engine and transmission - the mechanism that responds to what the speedometer says. We have four different engines, each with different characteristics and tradeoffs.

Let us go through them one by one.

## Controller 1: Classical SMC

Classical SMC is the baseline. It has been the standard in the field since Utkin's 1977 work, and it remains the reference against which everything else is measured.

The control law has three terms: an equivalent control component, a switching component, and a derivative damping component.

u equals u-equivalent plus K times sat of sigma over epsilon, minus k-d times sigma-dot.

**The equivalent control** is derived from the ideal sliding condition: what force would be needed to keep sigma exactly zero if the model were perfect? Set sigma-dot to zero, substitute the equations of motion, and solve for u. The result is: u-equivalent equals minus L times M-inverse times F, divided by L times M-inverse times B, where F collects all the nonlinear forcing terms - Coriolis, gravity, and friction - and L is the surface gradient vector zero-k-one-k-two. In code, this is two matrix multiplications and a scalar division.

**The switching term** uses a saturation function rather than the pure sign function. The saturation is piecewise: inside the boundary layer where the absolute value of sigma is less than epsilon, it equals sigma divided by epsilon - a linear ramp. Outside, it equals the sign of sigma - hard switching. This eliminates the chattering that pure sign-function switching produces. The boundary layer width epsilon equals 0.3 in operational use. The MT-6 study found the optimal chattering value is epsilon equals 0.02, but that comes at a cost to tracking accuracy - more on that in Episode 8.

**The derivative term** minus k-d times sigma-dot provides additional damping. It is proportional to how fast sigma is changing, which damps oscillations as the trajectory approaches the surface.

PSO tunes six parameters for this controller: k-one, k-two, lambda-one, lambda-two - the four surface parameters from Episode 2 - plus K, the switching gain, and k-d, the derivative gain. All six are searched in bounds of 2.0 to 30.0 for surface gains, 2.0 to 50.0 for K.

## Controller 2: Super-Twisting Algorithm

The Super-Twisting Algorithm, or STA-SMC, is a second-order sliding mode controller. The key difference from Classical SMC: the switching action is pushed one level deeper into the control structure so that the output force u is continuous. This directly reduces chattering.

The control law splits into two components that add together:

u equals u-one plus u-two.

u-one equals minus K-one times the absolute value of sigma to the power 0.5, times the sign of sigma. This is continuous everywhere - the exponent 0.5 means that as sigma approaches zero, u-one smoothly approaches zero rather than jumping. Near sigma equals zero, a small regularization is applied: instead of the exact absolute value, a tiny floor of delta equals ten-to-the-minus-ten is used to avoid numerical singularity. This is an implementation detail, not a theoretical modification.

u-two equals minus K-two times the integral from zero to t of the sign of sigma, integrated over time. This integral term is what handles steady-state error - it accumulates until sigma is zero. Without it, u-one alone would leave a residual error.

The critical constraint is K-one must be greater than K-two, both greater than zero. The Moreno-Osorio conditions - which we will cover in the Lyapunov episode - require K-one to exceed two times the square root of two d-bar over beta, where d-bar bounds the disturbance and beta is L times M-inverse times B. The nominal PSO-tuned gains satisfy this: K-one equals 8, K-two equals 4.

There is a known open issue in the report. The robust PSO tuning - which we cover in Episode 4 - produced STA gains with K-one equals 2.02 and K-two equals 6.67. That violates K-one greater than K-two. The report documents this explicitly as an integrity issue. The robust gains reduce chattering across the scenario set empirically, but they are not theoretically guaranteed by the Moreno-Osorio proof. This requires either a constrained re-run of the robust PSO with the K-one greater than K-two constraint enforced, or a revised stability analysis for the K-one less than K-two case.

PSO tunes six parameters: c-one, lambda-one, c-two, lambda-two - the surface parameters in STA notation - plus K-one and K-two. The constraint K-one greater than K-two is enforced during PSO: any particle violating it receives the instability penalty of ten-to-the-sixth.

## Controller 3: Adaptive SMC

The Adaptive SMC controller addresses a real practical problem: what if you do not know how large the disturbances are? In Classical SMC, the switching gain K must be set large enough to reject all disturbances. But if you set K too conservatively - too large - you get excessive chattering. Set it too small and disturbances break through.

The Adaptive SMC solution: let K adapt online.

The control law is: u equals minus K-of-t times sat of sigma over epsilon. Same saturation structure as Classical, but the gain K is now a time-varying function.

The adaptation law governs how K changes: K-dot equals gamma times the absolute value of sigma, minus delta-leak times K, with a dead zone applied when the absolute value of sigma is less than d-z.

Let me explain each term. The term gamma times absolute-sigma drives K upward when the pendulum is far from the surface - large error means we need more gain. The term minus delta-leak times K creates a slow decay - without it, K would only ever increase and drift to infinity. The leak rate delta-leak equals 0.01 was chosen to let K decay slowly when the error is near zero, preventing gain windup over long horizons. If delta-leak is too large, K shrinks before a new disturbance arrives and you get chattering bursts. Too small, and K drifts upward unboundedly.

The dead zone prevents adaptation when sigma is smaller than d-z equals 0.05. This threshold was chosen to match the effective noise floor of the angle sensors - roughly 0.005 radians times a typical gain factor. Without the dead zone, sensor noise drives continuous adaptation even when the system is already well-controlled.

K is clamped between 0.1 and 100. PSO tunes five parameters: k-one, k-two, lambda-one, lambda-two, and gamma, the adaptation rate.

## Controller 4: Hybrid Adaptive STA-SMC

The Hybrid controller attempts to combine the best of STA and Adaptive: smooth continuous control from STA plus online gain adaptation from Adaptive.

The control law is: u equals minus k-one-of-t times the absolute value of sigma to the 0.5 times sign of sigma, minus k-two-of-t times the integral of sign of sigma.

Both gains k-one and k-two now adapt according to their own adaptation laws, with rates gamma-one equals 0.1 and gamma-two equals 0.05, and a rate limiter of 5.0 per second to prevent violent gain jumps.

The report documents a known instability: under large disturbances and aggressive initial conditions, the Hybrid controller produces 666.9 degrees of overshoot and a 176 percent increase in chattering. The root cause is a feedback loop: when sigma is large, k-one adapts upward. But the STA term is proportional to the square root of sigma times k-one - so as k-one grows and sigma grows, they amplify each other. This is an open research item.

In the Monte Carlo results, the Hybrid controller returns sentinel values: energy equals ten-to-the-sixth and chattering equals zero. These indicate internal controller failure - gain divergence, not simulation crash. The report documents this explicitly so it is not misread as missing data.

PSO tunes four parameters for Hybrid: c-one, lambda-one, c-two, lambda-two. The robust PSO results show a 21.4 percent cost reduction for Hybrid versus its nominal tuning.

## Summary: What Makes Each Controller Different

Classical SMC: switching via saturation, equivalent control handles the nonlinear model exactly, simple and reliable.

STA-SMC: continuous u-one term pushes switching into the integral u-two, dramatically reducing high-frequency chattering. 74 percent reduction in chattering index versus Classical in the FFT analysis.

Adaptive SMC: K adapts online, so the switching gain automatically tracks unknown disturbance bounds. Useful when disturbance magnitudes are uncertain.

Hybrid Adaptive STA: aims for the best of both, but currently unstable under large errors. Documented as an open issue.

The next episode covers how all these controllers get their gains - PSO optimization.

---

*Report references: Section 2.2, Equations eq:sat, eq:classical, eq:ueq, eq:sta, eq:adaptive, eq:adaptive_law, eq:hybrid.*
