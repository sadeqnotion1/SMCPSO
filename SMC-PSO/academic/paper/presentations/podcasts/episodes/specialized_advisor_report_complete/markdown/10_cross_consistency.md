# Episode 10 - Cross-Consistency: Resolving the Apparent Contradictions

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 7-8 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode exists because the report contains numbers that look inconsistent on first read. Knowing these reconciliations cold prevents getting tripped up by an advisor who noticed them. None of the apparent contradictions are real - they all resolve cleanly.]**

## Opening: When Numbers Look Like They Conflict

An advisor reading the report carefully will find things that appear to contradict each other. The same controller has different chattering values in different tables. The same epsilon appears with two different values in two different sections. The Hybrid controller shows performance numbers even though it failed all 100 Monte Carlo runs.

These are not errors. They are legitimate differences in context, metric definition, and experimental setup. But without understanding the reconciliations, they look like inconsistencies. This episode goes through each one systematically.

## Contradiction A: Two Chattering Numbers for the Same Controller

In the MT-5 primary performance table, Classical SMC shows a chattering value of 0.647 plus or minus 0.347. In the FFT chattering analysis table, Classical SMC shows a chattering index of 8.2. These numbers are not the same metric.

The MT-5 chattering value is a time-domain measurement: the RMS amplitude of the control signal fluctuation, computed across the simulation window, averaged over 100 runs. Its units are roughly Newtons - the scale of the control signal itself.

The FFT chattering index is a frequency-domain measurement: the ratio of energy in the high-frequency band above 20 Hz to total signal energy, expressed as a percentage and scaled by 100 for readability. It captures how much of the control signal's energy is concentrated in rapid oscillations.

These measure fundamentally different things. The time-domain RMS tells you how large the control fluctuations are. The frequency-domain index tells you how concentrated the fluctuations are in the high-frequency range. A controller could have large but slow fluctuations - high RMS, low FFT index. Or small but rapid fluctuations - low RMS, high FFT index.

The report now explicitly labels both metrics in every table where they appear. When quoting chattering results, specify which metric: "chattering by FFT index" or "chattering by RMS amplitude."

For the actuator wear claim - the assertion that STA would reduce hardware wear - the FFT index is the appropriate metric. Actuator wear is driven primarily by high-frequency switching cycles, not by the total amplitude of motion.

## Contradiction B: The STA Robust Gain Violation

In Episode 3 and again in Episode 4, we flagged that the STA robust PSO row shows K-one equals 2.02 and K-two equals 6.67. This violates K-one greater than K-two, the Moreno-Osorio condition required for the finite-time convergence proof.

Is this publishable? The direct answer: not without resolution. The nominal STA gains - K-one equals 8, K-two equals 4 - satisfy the theoretical conditions and the corresponding results are fully valid. The robust gains are labeled explicitly as empirical results that reduce chattering across the 15-scenario set but lack a theoretical guarantee.

The path to resolution has two options. Option one: re-run the robust PSO with the constraint K-one greater than K-two enforced as a hard bound during the search. The gain at the constrained boundary might sacrifice some chattering performance versus the unconstrained result, but the resulting gains would have theoretical backing. Option two: investigate whether a different stability proof - perhaps an extended Moreno-Osorio result - covers the K-one less than K-two regime. There are papers examining this; the report has not yet cited them.

Until one of these paths is completed, the robust STA gains should be presented as empirical, not proven. The report states this clearly.

## Contradiction C: Epsilon Equals 0.3 vs. Epsilon Equals 0.02

In the controller formulations and all Monte Carlo benchmarks, epsilon equals 0.3. In the MT-6 boundary layer study from Episode 8, the near-optimal value was found to be epsilon equals 0.02. Which one is correct?

Both are correct in their context.

Epsilon equals 0.3 is the operational value used in all published results. The PSO gains were tuned with this epsilon. The Monte Carlo statistics, the energy numbers, the settling times, the Lyapunov validation - all of these used epsilon equals 0.3.

Epsilon equals 0.02 is the MT-6 study finding: within the three tested values, epsilon equals 0.02 minimized the FFT chattering index with acceptable tracking accuracy. This result was found after the benchmarks were complete.

The inconsistency is temporal, not logical. It represents work in progress. The correct next step - documented in the report - is to re-tune PSO gains with epsilon equals 0.02 and re-run the benchmarks. Until that is done, all results use epsilon equals 0.3.

If an advisor asks: the benchmarks are internally consistent because they all use the same epsilon. The MT-6 finding is a direction for future improvement, not a contradiction in the existing results.

## Contradiction D: Hybrid Shows CI Numbers Despite Failing

The report contains a row for Hybrid Adaptive STA in the confidence interval table: settling time CI of 1.79 to 2.11 seconds, overshoot CI of 3.0 to 4.0 percent. But earlier tables show Hybrid returned sentinel values on all 100 Monte Carlo runs, meaning it failed.

These numbers come from different experimental contexts.

The sentinel values - energy of 10-to-the-sixth, chattering of zero - come specifically from the MT-5 study with the standard Monte Carlo initial conditions described in Episode 6. These initial conditions, while modest in absolute terms, push the Hybrid controller into its gain-divergence failure mode.

The confidence intervals for settling time and overshoot come from a separate earlier study - QW-2 or a controller-specific validation run - where the Hybrid controller was tested with smaller, more controlled initial conditions that did not trigger the amplification instability. Under those conditions, Hybrid performed well with settling around 1.95 seconds.

The two results are consistent with the Episode 3 explanation: Hybrid works for small perturbations but fails for larger ones. The MT-5 initial conditions are large enough to trigger failure. The earlier study used smaller ones that did not.

The report now labels these clearly: sentinel values flagged as controller failure, CI values sourced to the specific study where Hybrid performed well. An advisor who sees both needs to know the source context for each.

## Consistency of the Argument

Stepping back: all four apparent contradictions resolve into the same underlying issue - the same word or number can mean different things depending on the measurement context. Chattering means two different things in two different tables. Epsilon is used as-tuned in benchmarks and as-studied in the MT-6 analysis. Hybrid performance exists both in a regime where it works and a regime where it fails.

The report's job is to make these contextual differences explicit rather than letting them appear as contradictions. And it does - each case has a note, a label, or a section clarifying the distinction.

## Takeaway

None of the apparent contradictions in the report are errors. They are differences in metric definition, experimental context, or timing of analysis. Know the reconciliation for each one:

- Two chattering metrics: time-domain RMS versus frequency-domain FFT index.
- STA robust gains: empirical results, not theoretically guaranteed, need constrained re-optimization.
- Two epsilon values: operational benchmark value versus MT-6 study finding.
- Hybrid CI numbers: from a different experimental context where Hybrid performed well.

Next episode: what needs to be added to the thesis before final submission.

---

*Report references: Section 3.5, Section 5.2 through 5.4, Section 6.*
