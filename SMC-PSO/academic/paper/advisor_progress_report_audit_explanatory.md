# Advisor Progress Report Audit: Expanded Explanatory Findings

Source reviewed:
- `academic/paper/advisor_progress_report_out.pdf` (text extracted for audit)
- `academic/paper/advisor_progress_report.tex` (equation/table verification)

Date: 2026-02-18
Purpose: Expand prior audit findings with clearer technical justification and concrete expected additions. This is an audit note, not a rewrite of the report.

1. [SECTION]: 1.2 Equations of Motion  
   [TYPE]: Missing  
   [EXPANDED FINDING]: The report lists only unique inertia terms (`M11, M12, M13, M22, M23, M33`) but does not present the full 3x3 inertia matrix with all entries shown explicitly.  
   [WHY ADVISOR WILL ASK]: For thesis-level dynamics, advisors expect the full matrix form to verify indexing, coupling structure, and consistency with implementation.  
   [WHAT TO ADD]: One full matrix equation with all nine positions populated, including `M21=M12`, `M31=M13`, `M32=M23`.

2. [SECTION]: 1.2 Equations of Motion  
   [TYPE]: Missing  
   [EXPANDED FINDING]: `C(q, q_dot)` is referenced conceptually, but no explicit term-by-term Coriolis/centrifugal matrix is provided.  
   [WHY ADVISOR WILL ASK]: Without explicit `C`, it is impossible to verify whether velocity coupling terms used in simulation/controller derivation are physically and mathematically correct.  
   [WHAT TO ADD]: Explicit `C(q, q_dot)` matrix entries or equivalent vector form `C(q,q_dot)q_dot` with all nonlinear terms.

3. [SECTION]: 1.2 Gravity Vector  
   [TYPE]: Missing  
   [EXPANDED FINDING]: The gravity expression includes `G2` and `G3` but does not explicitly state `G1=0` for the cart DOF.  
   [WHY ADVISOR WILL ASK]: Incomplete gravity vectors are a common source of model ambiguity and implementation mismatch.  
   [WHAT TO ADD]: Full vector notation `G=[0, G2, G3]^T` and one sentence explaining why the cart term is zero.

4. [SECTION]: 1.2 Model Derivation  
   [TYPE]: Needs expansion  
   [EXPANDED FINDING]: Nonlinear coupling term forms (such as `cos(theta1-theta2)` in `M23`) are listed but not visibly tied to a derivation check.  
   [WHY ADVISOR WILL ASK]: Advisors will expect at least a compact validation trail from Lagrangian expressions to final dynamics for sign/trig correctness.  
   [WHAT TO ADD]: A short derivation trace or cross-check reference (appendix or citation to derivation notebook/script).

5. [SECTION]: 1.4 Simplified vs Full Model  
   [TYPE]: Missing  
   [EXPANDED FINDING]: The simplified linearized model used for PSO is claimed but its actual linearization (`A`, `B`, equilibrium assumptions) is absent.  
   [WHY ADVISOR WILL ASK]: PSO results rely on this model choice; without explicit linearization, reproducibility and validity are weak.  
   [WHAT TO ADD]: Linearized state-space equations around upright equilibrium with variable definitions and operating point.

6. [SECTION]: 1.2 Friction Model  
   [TYPE]: Inconsistency  
   [EXPANDED FINDING]: Text says "asymmetric viscous + Coulomb friction," but the written equation contains only linear viscous terms.  
   [WHY ADVISOR WILL ASK]: This is a direct contradiction in model definition and can materially change robustness and energy metrics.  
   [WHAT TO ADD]: Either include Coulomb/asymmetric terms mathematically, or revise wording to match the equation.

7. [SECTION]: 2.1 Sliding Surface Design  
   [TYPE]: Needs expansion  
   [EXPANDED FINDING]: The selected linear sliding surface is given, but no design comparison versus integral/terminal alternatives is provided.  
   [WHY ADVISOR WILL ASK]: Surface choice governs convergence/chattering tradeoffs and should be justified, not only stated.  
   [WHAT TO ADD]: One short design rationale paragraph with rejected alternatives and why linear surface fits DIP objectives.

8. [SECTION]: 2.1 Sliding Surface Design  
   [TYPE]: Missing  
   [EXPANDED FINDING]: Stability is described via eigenvalues `-lambda_i/k_i`, but required sign constraints are not explicitly stated as design conditions.  
   [WHY ADVISOR WILL ASK]: Theoretical stability claims should include explicit inequalities, not implied assumptions.  
   [WHAT TO ADD]: Formal condition statement (e.g., `lambda_i>0`, `k_i>0`) linked to reduced-order stability.

9. [SECTION]: 2 Sliding Conditions  
   [TYPE]: Missing  
   [EXPANDED FINDING]: There is no explicit relative-degree check of `sigma` with respect to control input `u`.  
   [WHY ADVISOR WILL ASK]: SMC formulations require this structural property to ensure switching action affects `sigma_dot` correctly.  
   [WHAT TO ADD]: A concise calculation showing relative degree and nonzero input channel term.

10. [SECTION]: 2 Sliding Conditions  
    [TYPE]: Missing  
    [EXPANDED FINDING]: Matching condition verification is not shown (disturbances/uncertainties entering through same channel as control).  
    [WHY ADVISOR WILL ASK]: Claimed robustness guarantees are incomplete without matching-condition context.  
    [WHAT TO ADD]: One short statement/equation specifying matched disturbance assumptions.

11. [SECTION]: 2.2.1 Classical SMC  
    [TYPE]: Needs expansion  
    [EXPANDED FINDING]: Equivalent control is presented as final closed form only; no derivation from `sigma_dot=0` is shown.  
    [WHY ADVISOR WILL ASK]: Thesis evaluation usually expects derivational transparency for controller correctness.  
    [WHAT TO ADD]: Stepwise derivation from sliding condition to `u_eq`.

12. [SECTION]: 2.2 Control Laws  
    [TYPE]: Missing  
    [EXPANDED FINDING]: `sat(sigma/epsilon)` is mentioned but not mathematically defined.  
    [WHY ADVISOR WILL ASK]: Different saturation definitions produce different boundary-layer behavior and chattering levels.  
    [WHAT TO ADD]: Piecewise saturation function definition in equation form.

13. [SECTION]: 2.2.2 STA-SMC  
    [TYPE]: Missing  
    [EXPANDED FINDING]: Finite-time convergence is claimed, but no explicit convergence-time bound `T_f(K1,K2,initial)` is provided.  
    [WHY ADVISOR WILL ASK]: "Finite-time" is stronger than asymptotic; advisors often ask for explicit time-bound expression or upper bound.  
    [WHAT TO ADD]: Bound equation and brief interpretation.

14. [SECTION]: 2.2.3 Adaptive SMC  
    [TYPE]: Unjustified claim  
    [EXPANDED FINDING]: `delta_leak=0.01` and `d_z=0.05` are asserted without sensitivity study or design rule.  
    [WHY ADVISOR WILL ASK]: These constants strongly affect adaptation speed, noise rejection, and gain drift.  
    [WHAT TO ADD]: Brief tuning rationale and small sensitivity summary.

15. [SECTION]: 2.2.4 Hybrid Adaptive STA  
    [TYPE]: Needs expansion  
    [EXPANDED FINDING]: Instability root cause is described qualitatively, but there is no quantitative feedback/robustness analysis.  
    [WHY ADVISOR WILL ASK]: Without quantitative analysis, the "root cause" remains a hypothesis.  
    [WHAT TO ADD]: Small-signal/margin style analysis or a parameter-sensitivity plot around unstable region.

16. [SECTION]: 3.1 PSO Hyperparameters  
    [TYPE]: Needs expansion  
    [EXPANDED FINDING]: `N_p=40`, `c1=c2=2.0`, and `w=0.7` are only lightly justified.  
    [WHY ADVISOR WILL ASK]: Optimizer settings can dominate reported gains; weak justification reduces confidence.  
    [WHAT TO ADD]: Short ablation comparison (e.g., particle count and coefficient variants).

17. [SECTION]: 3.1 PSO Convergence/Stopping  
    [TYPE]: Needs expansion  
    [EXPANDED FINDING]: "Convergence verified experimentally" is claimed without showing convergence behavior or defining plateau criteria.  
    [WHY ADVISOR WILL ASK]: Advisors need to know whether 200 iterations are sufficient or wasteful.  
    [WHAT TO ADD]: Convergence curve reference and stop-condition statement (fixed-iteration vs early-stop).

18. [SECTION]: 3.2 Fitness Function  
    [TYPE]: Unjustified claim  
    [EXPANDED FINDING]: Normalization thresholds `[10,100,1000,1]` and instability penalty `10^6` are listed without scale calibration evidence.  
    [WHY ADVISOR WILL ASK]: If these constants are not justified, optimization may be biased toward one metric.  
    [WHAT TO ADD]: One paragraph showing typical metric magnitudes and why these scales/penalty dominate as intended.

19. [SECTION]: 3.4 Robust PSO  
    [TYPE]: Needs expansion  
    [EXPANDED FINDING]: The 15-scenario split (3 nominal, 4 moderate, 8 large) is presented without rationale or sensitivity analysis.  
    [WHY ADVISOR WILL ASK]: Robust tuning outcomes could be dependent on arbitrary scenario weighting.  
    [WHAT TO ADD]: Justification for distribution and at least one alternate split comparison.

20. [SECTION]: 3.5 and Appendix A  
    [TYPE]: Inconsistency  
    [EXPANDED FINDING]: The report states a hard constraint `K1 > K2`, but the robust STA gains shown are `K1=2.02`, `K2=6.67`.  
    [WHY ADVISOR WILL ASK]: This directly challenges correctness of either PSO constraints or reported table values.  
    [WHAT TO ADD]: Corrected gains or corrected constraint statement, plus short explanation.

21. [SECTION]: 4 Lyapunov Proofs  
    [TYPE]: Missing  
    [EXPANDED FINDING]: Key constants remain symbolic (`beta, eta, c1, c2, L, alpha1, alpha2`) with no numerical instantiation for DIP parameters/gains.  
    [WHY ADVISOR WILL ASK]: Practical applicability of theoretical inequalities is unverified without parameter mapping.  
    [WHAT TO ADD]: A compact "constants instantiation" subsection with computed bounds.

22. [SECTION]: 4.1 Numerical Lyapunov Validation  
    [TYPE]: Unclear  
    [EXPANDED FINDING]: Statement "96.2% of samples satisfy V_dot<0 outside boundary layer" leaves 3.8% unexplained.  
    [WHY ADVISOR WILL ASK]: Remaining violations may indicate transient/measurement artifacts or actual stability risk.  
    [WHAT TO ADD]: Clarify where and why violations occur (e.g., near switching/boundary transitions) and whether expected.

23. [SECTION]: 4.5 Swing-Up  
    [TYPE]: Needs expansion  
    [EXPANDED FINDING]: Zeno prevention is asserted by hysteresis but no formal switching-time lower bound is shown.  
    [WHY ADVISOR WILL ASK]: Hybrid proofs are commonly challenged at switching logic level.  
    [WHAT TO ADD]: Short lemma-style argument or reference proving finite switching.

24. [SECTION]: 5.1 Monte Carlo Methodology  
    [TYPE]: Missing  
    [EXPANDED FINDING]: Initial condition distributions/ranges, failure criteria, and seed protocol are not explicitly defined.  
    [WHY ADVISOR WILL ASK]: Monte Carlo results are not reproducible or auditable without generation and failure rules.  
    [WHAT TO ADD]: Exact distribution definitions, divergence thresholds, and random seeding policy.

25. [SECTION]: 5.1 MT-5 Scope  
    [TYPE]: Unclear  
    [EXPANDED FINDING]: Only 4 controllers are included in MT-5 while the report discusses more controllers across sections; exclusion rationale is not explicit.  
    [WHY ADVISOR WILL ASK]: Selective inclusion can appear to bias comparative conclusions.  
    [WHAT TO ADD]: One paragraph stating inclusion/exclusion criteria by experiment.

26. [SECTION]: 5.2 to 5.4 Results Tables  
    [TYPE]: Inconsistency  
    [EXPANDED FINDING]: Hybrid controller is marked "Failed" in primary metrics but still has valid CI, FFT, and statistical comparisons.  
    [WHY ADVISOR WILL ASK]: Conflicting status undermines trust in the entire result pipeline.  
    [WHAT TO ADD]: Harmonize tables and define what "Failed" means (all runs, subset, or different test setup).

27. [SECTION]: 5.4 Statistical Analysis  
    [TYPE]: Missing  
    [EXPANDED FINDING]: No normality check evidence, no multiple-comparison correction, no shown formula for Cohen's d computation, and no CI-width rationale for bootstrap count.  
    [WHY ADVISOR WILL ASK]: Statistical claims can be challenged as invalid or overstated.  
    [WHAT TO ADD]: Brief statistical assumptions subsection with correction policy and effect-size formula.

28. [SECTION]: 6 Boundary Layer Study (MT-6)  
    [TYPE]: Needs expansion  
    [EXPANDED FINDING]: Only three epsilon points are tested; correction from 66.5% to 3.7% is explained qualitatively; model fidelity used in MT-6 is not explicit.  
    [WHY ADVISOR WILL ASK]: "Near-optimal epsilon=0.02" appears weakly supported from sparse sweep and limited method detail.  
    [WHAT TO ADD]: Finer sweep, exact corrected metric procedure, and model used (simplified/full nonlinear).

29. [SECTION]: 7 Robustness Analysis  
    [TYPE]: Missing  
    [EXPANDED FINDING]: "Mismatch tolerance" is reported (8-16%) but metric definition and measurement procedure are absent; also ±20% all-parameter stability appears inconsistent with these tolerance numbers.  
    [WHY ADVISOR WILL ASK]: Robustness claims are currently ambiguous and internally conflicting.  
    [WHAT TO ADD]: Formal tolerance definition, protocol (simultaneous vs one-at-a-time), and worst-case combination summary.

30. [SECTION]: Thesis-Level Context Sections  
    [TYPE]: Missing  
    [EXPANDED FINDING]: Missing or underdeveloped sections include literature benchmarking, simulation-to-hardware gap, PSO compute-time comparison, explicit QW-2 baseline initial condition, and future work.  
    [WHY ADVISOR WILL ASK]: These sections are expected in thesis progress reports to establish novelty, realism, and completion roadmap.  
    [WHAT TO ADD]: Short dedicated section(s) with concise comparative and practical context.

31. [SECTION]: Cross-Consistency and Reporting  
    [TYPE]: Inconsistency  
    [EXPANDED FINDING]: Chattering index appears as both 3.088 (MT-5) and 2.1 (FFT) without metric distinction; control-law epsilon and MT-6 epsilon differ without benchmark context; figures are said complete but are not visibly cited in results discussion.  
    [WHY ADVISOR WILL ASK]: Ambiguous metric definitions and uncited figures make conclusions hard to verify.  
    [WHAT TO ADD]: Metric-definition table, benchmark-value provenance note, and explicit figure callouts in results sections.

## Priority Reminder

- CRITICAL: 1, 2, 3, 5, 6, 9, 10, 11, 20, 21, 24, 26, 27, 29
- IMPORTANT: 4, 7, 8, 12, 13, 14, 15, 17, 18, 19, 22, 23, 28, 30, 31
- MINOR: 16, 25

## Estimated Addition Size Reminder

- Critical/important estimate ranges are unchanged from prior audit response and should be used for planning section expansion effort.
