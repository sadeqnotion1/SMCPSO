# Episode 04 - PSO Configuration: How the Gains Were Found

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 10-12 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode covers the full PSO setup - hyperparameters, cost function, search bounds, and the robust scenario extension. The STA robust gain inconsistency is flagged here and in Episode 3. Know it cold - it is the most likely integrity question an advisor will ask.]**

## Opening: Why Not Just Pick Gains Manually?

Before we talk about PSO, let us understand the problem it solves.

Each controller has four to six parameters to tune. The relationship between those parameters and performance is highly nonlinear - a small change in one gain can have wildly different effects depending on the values of the others. The search space is six-dimensional for most controllers. And the performance metric we care about involves running a 10-second nonlinear simulation to evaluate each candidate set of gains.

Manual tuning by an expert might find good gains for one controller in a day. We have four controllers, and we want gains that are not just good for one starting condition but robust across a wide range of initial angles and disturbances. Particle Swarm Optimization - PSO - automates this search.

## The Algorithm Parameters

The PSO configuration is documented exactly in the report. Forty particles. Two hundred iterations. Inertia weight w equals 0.7. Cognitive acceleration c-one equals 2.0. Social acceleration c-two equals 2.0. Random seed 42 for reproducibility.

Let me explain what these mean.

**Forty particles** means forty candidate gain sets are evaluated simultaneously each iteration. The report notes this was increased from 30 - the more common default - because our search space is six-dimensional. A heuristic from the PSO literature suggests approximately ten particles per dimension; six dimensions calls for sixty or more, so forty is a pragmatic compromise between coverage and runtime.

**Two hundred iterations** was chosen based on empirical observation: the convergence curves logged to the PSO log directory show cost reaching a stable plateau by iteration 150 to 180 in all controllers. The 200-iteration budget provides a buffer. There is no early stopping criterion - the full 200 iterations always run.

**Inertia weight 0.7** controls the balance between exploration - searching new regions - and exploitation - refining known good regions. A value of 0.7 falls in the middle of the typical range of 0.4 to 0.9. Lower values make particles converge faster but risk getting trapped in local optima. The standard Kennedy and Eberhart 1995 values were adopted without a formal ablation study over these hyperparameters - that is a documented limitation.

**Velocity update:** each particle's velocity in each dimension is updated as: v-new equals w times v-old, plus c-one times r-one times the difference between the particle's personal best position and current position, plus c-two times r-two times the difference between the global best position and current position. The r terms are random numbers from zero to one, resampled each iteration.

## The Cost Function

This is where the real design decisions live. We are not just minimizing one thing - we are balancing four competing objectives simultaneously.

The overall fitness function is: J equals 0.7 times the mean cost J-bar-mc, plus 0.3 times the maximum cost across scenarios, max-of-J-k.

That outer structure - 70 percent mean, 30 percent worst-case - ensures PSO does not find gains that work brilliantly for one scenario but fail catastrophically for another. The 30 percent worst-case penalty keeps extreme failures from being hidden by good average performance.

The per-scenario cost J-k has five components:

First, tracking error: w-err times ISE of x, integrated squared error of the state trajectory. Weight 1.0, normalized against a threshold of 10 rad-squared. This is the primary objective - keep the pendulums upright.

Second, control effort: w-u times IAE of u, integral absolute error of the control force. Weight 0.1, normalized against 100 Newton-seconds. This penalizes energy-hungry controllers.

Third, slew rate: w-r times IAE of u-dot, integral absolute error of the rate of change of control force. Weight 0.01, normalized against 1000 Newtons per second. This penalizes violent, rapidly-changing control signals that would damage hardware.

Fourth, sliding integral: w-s times the integral of sigma-squared. Weight 0.1, normalized against 1. This directly penalizes time spent off the sliding surface.

Fifth, instability penalty: P equals ten-to-the-sixth, applied as a binary flag if the simulation diverges. This value is approximately ten-thousand times the typical stable-run cost of 0.1 to 1.0, ensuring unstable particles are always ranked last in the swarm regardless of their other components.

The normalization thresholds deserve a brief explanation. ISE of 10 means: for a run with ISE near ten, the tracking component contributes roughly one unit to the cost. For a perfect run, it contributes near zero. This scaling ensures all four components contribute comparably to the total cost rather than one dominating due to units.

## Search Bounds per Controller

PSO searches a bounded region for each controller's gains. The bounds are:

Classical SMC, six-dimensional: surface gains lambda and k from 2.0 to 30.0, switching gain K from 2.0 to 50.0, derivative gain k-d from 0.05 to 3.0.

STA-SMC, six-dimensional: surface gains from 2.0 to 30.0, K-one and K-two from 2.0 to 30.0, with the hard constraint K-one greater than K-two enforced during evaluation.

Adaptive SMC, five-dimensional: surface gains from 2.0 to 30.0, adaptation rate gamma from 0.05 to 3.0. No switching gain bounds are needed since K adapts online.

Hybrid Adaptive, four-dimensional: surface gains only, 2.0 to 30.0. The adaptive laws govern the rest.

## Robust PSO: The Scenario Extension

Standard PSO found gains that worked well for one starting condition but degraded catastrophically for varied initial conditions. The report quantifies this: nominal chattering of 2.14 degraded to 107.61 under realistic initial conditions - a 50.4 times degradation. That is not a usable controller.

The robust PSO solution: instead of evaluating each particle on one scenario, evaluate it on 15 scenarios simultaneously. Three nominal scenarios with initial angles in plus or minus 0.05 radians. Four moderate scenarios with plus or minus 0.15 radians. Eight large scenarios with plus or minus 0.30 radians.

The split was chosen to weight large perturbations most heavily - 53 percent of scenarios use large initial angles. The reasoning: a controller that only works for small perturbations is nearly useless in practice. A sensitivity analysis on this exact split was not performed; the report documents this as a known limitation.

The result: chattering degradation reduced from 50.4 times to 7.5 times. Not eliminated, but substantially improved.

## The PSO-Tuned Gains and the Open Issue

The report provides a complete gains table for all four controllers, both nominal and robust tunings.

For Classical SMC robust: k-one equals 23.07, k-two equals 12.85, lambda-one equals 5.51, lambda-two equals 3.49, K equals 2.23, k-d equals 0.15. Cost improved by 2.2 percent versus nominal.

For Hybrid robust: gains show a 21.4 percent cost reduction versus nominal.

For STA robust: this is the open issue. The robust PSO found K-one equals 2.02 and K-two equals 6.67. This violates K-one greater than K-two. The Moreno-Osorio stability proof requires this constraint for finite-time convergence. The robust PSO with 15 scenarios found this gain combination reduced chattering across the scenario set, but it does not satisfy the theoretical guarantee.

The report is transparent about this. The robust STA gains should not be used without either: re-running the robust PSO with the K-one greater than K-two constraint actively enforced during the search, or developing an updated stability proof for the K-one less than K-two case.

## Takeaway

PSO automates the gain search across a high-dimensional nonlinear space. The cost function balances four objectives. Robust PSO extends the search to cover 15 scenarios, dramatically improving generalization. One unresolved issue remains: the robust STA gains violate the theoretical constraint and require correction before publication.

Next episode: given these gains, how do we mathematically prove the controllers are stable?

---

*Report references: Section 3.1 through 3.5, Equation eq:pso_cost.*
