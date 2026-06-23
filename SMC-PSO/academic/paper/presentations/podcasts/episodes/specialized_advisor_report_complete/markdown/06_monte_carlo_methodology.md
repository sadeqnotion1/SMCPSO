# Episode 06 - Monte Carlo Benchmarks: Designing an Honest Experiment

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 8-10 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode is about experimental design integrity - not just what the results are, but why the methodology is credible. The reproducibility gap (seed not logged) is the weakest point; acknowledge it directly rather than hoping it does not come up.]**

## Opening: One Run Proves Nothing

A single simulation showing your controller working is not a benchmark. It might have been a lucky set of initial conditions. The pendulum might have started almost upright. The disturbances might have been mild. A single run does not tell you how the controller behaves across the full range of conditions it will face.

Monte Carlo analysis addresses this by running the same experiment many times with randomized conditions. The statistical distribution of outcomes - not just one outcome - is the result.

The MT-5 study is the primary benchmark. 100 runs per controller, four controllers, 400 total simulations on the full nonlinear model.

## The Experimental Setup

Every detail of the Monte Carlo setup is documented in the report. Here is what that looks like in practice.

**Initial conditions** are drawn uniformly and independently for each run:

Cart position: uniform between minus 0.05 and plus 0.05 meters. That is 5 centimeters in either direction.

Pendulum angles theta-one and theta-two: uniform between minus 0.05 and plus 0.05 radians. That is approximately plus or minus 2.9 degrees from vertical - a small but non-negligible perturbation.

Cart velocity: uniform between minus 0.02 and plus 0.02 meters per second.

Angular velocities: uniform between minus 0.05 and plus 0.05 radians per second for both pendulums.

Uniform distributions were chosen because there is no prior knowledge of which starting conditions are more likely. Uniform is the least-assumption distribution - it weights every point in the initial condition range equally.

**Simulation duration:** 10 seconds at a control period of 0.01 seconds. That is 1000 control steps per run.

**Model:** full nonlinear dynamics. Every MT-5 result you will find in the report - every settling time, every overshoot, every energy value - was computed on the full nonlinear model, not the simplified PSO model.

## Success Criterion

How do you decide whether a run succeeded? The criterion: the absolute value of both pendulum angles must stay within 2 percent of the equilibrium angle for at least one continuous second within the 10-second window.

Two percent of upright means approximately 0.02 radians - about 1.1 degrees. Holding both angles within this band for a full second indicates the controller has genuinely stabilized the system, not just passed through the equilibrium while still diverging.

All four tested controllers achieved 100 percent success rate - no divergence across all 100 runs. This is the expected result given the PSO-tuned gains, but it needed to be verified empirically.

## Why Four Controllers, Not All Seven?

The report explicitly documents the exclusion rationale for the three untested controllers.

Swing-Up SMC was excluded because it is designed to handle pendulums starting from the hanging position. The MT-5 initial conditions start near the upright position. In this near-vertical regime, Swing-Up's energy-based control law is not engaged - the stabilization phase would need to trigger immediately, but the controller's transition logic is calibrated for swing-up, not near-vertical starts. Including it would produce misleading results.

MPC was excluded because it requires the cvxpy optimization library, which was not integrated into the batch simulation runner at the time of the MT-5 study. Practical infrastructure limitation.

The Factory wrapper is not a controller - it is a routing layer that instantiates controllers. Not applicable.

## The Hybrid Failure: Sentinel Values

The Hybrid Adaptive STA-SMC returned consistent failure on all 100 Monte Carlo runs. Not 50. Not some. Every single run.

The failure mode is internal: the adaptive gain diverges - it grows without bound due to the amplification feedback between sigma and k-one described in Episode 3. The simulation does not crash. The controller continues to run. But it produces garbage.

To represent this faithfully without crashing the statistics, the report assigns sentinel values: energy equals ten-to-the-sixth Newtons-squared-seconds, chattering equals zero. These values are flagged in the results table and explained as controller failure, not missing data. An advisor who sees energy of a million and chattering of zero needs to know this is a deliberate marker, not a real measurement.

The confidence intervals for Hybrid in the table - 1.79 to 2.11 seconds settling time, 3.0 to 4.0 percent overshoot - come from a different experimental context where Hybrid performed well, not from the MT-5 runs.

## The Reproducibility Gap

This is the honest part. The MT-5 Monte Carlo study did not log the random seed. The initial conditions are known to be drawn from uniform distributions with the stated ranges, and the method is documented. But if you tried to reproduce the exact 100 sets of initial conditions that were used, you could not.

The report documents this explicitly as a reproducibility gap. The statistical results - means, standard deviations, confidence intervals - remain valid. They are computed from 100 independent samples drawn from documented distributions. But exact run-for-run reproduction is not possible without the seed.

The action item: future runs of this benchmark should log the seed. A single line added to the run configuration: record numpy random seed at benchmark start.

## Energy Units: A Clarification That Matters

The MT-5 study reports energy in Newton-squared-seconds - the integral of u-squared over time. This is a control effort metric. It is not physical energy in Joules.

An earlier study, QW-2, reported energy in Joules - the integral of force times velocity. These are different measurements. When you see Classical SMC at 9843 N-squared-s in MT-5 and a different number in Joules from QW-2, they are not inconsistent - they are measuring different things. Episode 10 covers the full cross-consistency analysis, but it is worth flagging here: the metric name matters and must be specified when reporting results.

## Takeaway

The MT-5 benchmark is designed for credibility: 100 runs with randomized initial conditions, full nonlinear model, documented success criterion, explicit exclusion rationale for untested controllers, and honest acknowledgment of the seed gap. The Hybrid failure is represented as sentinel values rather than hidden or omitted.

Next episode: what the numbers from those 400 simulations actually mean - statistical analysis and significance testing.

---

*Report references: Section 5.1 through 5.5.*
