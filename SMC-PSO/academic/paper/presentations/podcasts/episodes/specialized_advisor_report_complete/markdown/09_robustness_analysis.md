# Episode 09 - Robustness Analysis: What Happens When the Model Is Wrong

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 8-10 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: Robustness is where theoretical controllers meet reality. The key concepts here are simultaneous perturbation - all parameters wrong at once, not one at a time - and the distinction between stability tolerance and performance degradation. The STA paradox - best disturbance rejection but lowest parameter tolerance - is the most interesting result.]**

## Opening: Simulations Assume a Perfect Model

Every result in this project - every settling time, every chattering index, every Lyapunov proof - was computed using a model with specific values for cart mass, link masses, lengths, and inertias. In a real system, none of those values are known exactly. Sensors add noise. Links flex slightly. The cart has friction that changes with temperature. Mass measurements have manufacturing tolerances.

Robustness analysis asks: how much can the model be wrong before the controller fails?

The report addresses this through two separate studies. The LT-6 model uncertainty study varies the physical parameters. The MT-8 disturbance rejection study applies external forces. Together they tell you how the controllers behave when the assumptions break down.

## LT-6: Model Parameter Uncertainty

The protocol for LT-6 was simultaneous parametric perturbation. All physical parameters were varied at the same time: cart mass, link masses, link lengths, moments of inertia, and friction coefficients.

This is a harder test than varying one parameter at a time. If you change only the cart mass, the controller might compensate easily because the other dynamics are still accurate. Changing all parameters simultaneously creates a worst-case scenario where every assumption in the model is wrong simultaneously.

Two perturbation levels were tested: plus or minus 10 percent and plus or minus 20 percent of all nominal values.

All four controllers remained stable at both levels. None diverged. This is a meaningful result - it tells you the controllers are not sensitive to moderate model errors in the sense that they do not fall over when the parameters are off by 20 percent.

## Mismatch Tolerance: What the Numbers Mean

The report also documents "mismatch tolerance" values per controller. Classical SMC: 12 percent. STA: 8 percent. Adaptive: 15 percent. Hybrid: 16 percent.

These require careful interpretation. Mismatch tolerance is not "the controller fails above this level." It is defined specifically as: the largest simultaneous uniform perturbation factor such that the controller remains stable - does not diverge within 10 seconds - under the perturbed model.

For Classical SMC at 12 percent: the controller was stable at 12 percent perturbation. Instability was first observed between 12 percent and the next tested perturbation level. The exact stability boundary - whether it fails at 13 percent or 19 percent - was not determined. A finer sweep would be needed to pin down the exact limit.

This is a documented limitation. The report describes the tolerance values as indicating the tested stability boundary, not the true stability limit. For a thesis examiner, the appropriate framing is: these numbers provide a lower bound on stability tolerance, with the understanding that finer resolution is needed to characterize the exact failure point.

## The STA Paradox

The most interesting result from LT-6 is a counterintuitive pattern.

STA-SMC has the lowest mismatch tolerance - 8 percent, compared to 12 to 16 percent for the other three controllers. Yet in the disturbance rejection test from MT-8, STA has the best performance - 91 percent attenuation, better than all others.

How can the best disturbance rejector also be the most sensitive to model uncertainty?

The answer lies in what each test measures. LT-6 varies the physical parameters - the masses and lengths used in the equations of motion. STA's finite-time convergence guarantee depends on the gain conditions K-one greater than K-two and specific bounds involving the parameter beta. When you perturb the physical parameters, beta changes. If the perturbation shifts beta enough that the K-one bound is no longer satisfied, the finite-time convergence proof breaks down - and stability follows it.

Classical SMC, by contrast, uses asymptotic stability with a simpler Lyapunov function. Its stability condition is less tightly coupled to the exact values of the physical parameters. It tolerates larger parameter errors before failing.

MT-8 tests external disturbances - step forces applied to the cart from outside. STA's continuous u-one component - the square-root-sigma term - provides smooth, proportional response to disturbances. The sign function in Classical SMC's switching term responds with discrete jumps. For rejecting external disturbances, the smooth STA response is inherently better.

The takeaway: STA is robust to external disturbances but fragile to model error. Classical SMC is the opposite - it tolerates model error better but rejects disturbances less cleanly. The choice between them depends on which uncertainty source dominates in the target application.

## MT-8 Disturbance Rejection: The Numbers

The attenuation metric is: one minus the norm of the disturbed state trajectory divided by the norm of the nominal state trajectory. A value of 91 percent means: under disturbance, the trajectory deviation was only 9 percent of what it would have been without the controller's disturbance rejection capability.

Ranking: STA 91 percent, Hybrid 89 percent, Classical 87 percent, Adaptive 78 percent.

The gap between the top three and Adaptive is notable. The Adaptive SMC adaptation law responds to sigma - the sliding variable - not directly to disturbances. When a step disturbance hits, K-of-t adapts upward, but there is a lag between the disturbance arriving and the gain responding. That lag allows more state deviation before the gain increases. The dead zone in the adaptation law - where adaptation stops when sigma is smaller than d-z equals 0.05 - also means small disturbances produce no adaptation response at all.

Why is Hybrid Adaptive not the best disturbance rejector despite having the best mismatch tolerance? Because the Hybrid controller in MT-8 context is operating near its instability boundary. Under large disturbances, the amplification feedback between sigma and k-one described in Episode 3 can trigger. The 89 percent result likely reflects moderate disturbances where the Hybrid performs well, not the large-disturbance regime where it fails.

## What Is Not in the Report: Known Gaps

The robustness analysis has explicit limitations documented in the report.

The parameter sweep is coarse. Tested: 10 percent and 20 percent. Not tested: values between and beyond these. For a rigorous worst-case characterization, you would want a complete sensitivity analysis identifying which parameter combinations are most dangerous - for example, is it worse to have the cart mass wrong, or the link inertias wrong? The report does not answer this.

The disturbance rejection metric uses step disturbances only. Real hardware encounters ramp disturbances, sinusoidal disturbances, impulsive disturbances, and noise. The 91 percent figure applies to step inputs. Whether STA maintains its ranking under other disturbance types is unknown from the current analysis.

No formal worst-case robustness sweep was performed. The report identifies this as a gap. The existing results provide directional insight, not worst-case guarantees.

## Adaptive and Hybrid: Why They Tolerate More Model Error

The Adaptive controllers - Adaptive SMC and Hybrid Adaptive STA - show higher mismatch tolerance than the non-adaptive controllers.

The ISS Lyapunov proof from Episode 5 is consistent with this. For Hybrid Adaptive, the ISS property states: if the disturbance - which includes model mismatch - is bounded, the state remains bounded. The adaptive gains K-of-t provide a self-correcting mechanism: when model mismatch increases the effective disturbance, K-of-t adapts upward to compensate. Classical and STA controllers have fixed gains that cannot respond to model changes.

This is the practical value of adaptation. Not faster settling, not lower chattering - better tolerance to the model being wrong.

## Takeaway

The robustness study shows all four controllers survive plus or minus 20 percent parameter perturbation and reject step disturbances at 78 to 91 percent efficiency. The interesting tradeoff: STA is the best disturbance rejector but the least tolerant to model error. Adaptive and Hybrid tolerate model errors best due to their self-correcting gain mechanisms. The analysis has coarse resolution and needs finer sweeps before worst-case claims can be made.

Next episode: reconciling the apparent contradictions in the data tables - how different metrics, different epsilon values, and the Hybrid sentinel values all fit together consistently.

---

*Report references: Section 7.1, Section 7.2.*
