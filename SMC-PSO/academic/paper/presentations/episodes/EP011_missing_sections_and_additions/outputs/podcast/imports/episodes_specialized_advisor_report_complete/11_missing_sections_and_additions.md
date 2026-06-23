# Episode 11 - What Still Needs to Be Written: Thesis Completion Gaps

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 8-10 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode is explicitly forward-looking. The report is honest that it is 90 out of 100 - near submission-ready but not finished. Know these gaps in detail because an advisor who asks "what is still to be done?" should get a specific, prioritized answer, not vague reassurance.]**

## Opening: 90 Out of 100

The thesis completion score documented in the report is 90 out of 100. That means 90 percent of the work is done and the remaining 10 percent has been identified, broken into phases, and given target dates.

This episode goes through what that remaining 10 percent looks like in practice - the six specific gaps that need to be filled before the thesis is complete. Understanding these is important not just for completion planning but for advisor conversations: the gaps are documented honestly in the report, and an advisor may probe them directly.

## Gap 1: Literature Comparison Table

The report establishes performance results for four controllers on a double-inverted pendulum system. But it does not compare those results to published work from other researchers on similar or identical systems.

A literature benchmarking table would show: here is what the best published controllers achieved, here is what this work achieves, and here is where this work sits relative to the state of the art.

Without this comparison, a key question is unanswered: are these results good? Is 1.82 seconds settling time for STA-SMC competitive with the published literature, or is it unremarkable? Are the Lyapunov proofs more or less rigorous than comparable work?

The challenge for this gap: finding papers that studied identical or comparable DIP configurations - same number of links, same parameter regime, same performance metrics. Many DIP papers use different parameter values, different initial conditions, or different success criteria. A fair comparison requires careful matching of experimental conditions, which takes time.

For the thesis defense, the minimum viable version of this is: cite three to five relevant papers, note what their reported settling times and chattering metrics are, and acknowledge where direct comparison is possible and where it is not. A full table with matched conditions is the ideal.

## Gap 2: Simulation-to-Hardware Analysis

Every result in this project comes from simulation. The report is explicit about this. But what happens when this controller runs on real hardware?

Real hardware introduces effects that are absent in simulation: actuator saturation dynamics - the time constant between commanding a force and the motor producing it. Encoder quantization - angle measurements are digital, not continuous. Communication delays between sensor and controller. Coulomb friction and stiction that differ from the model. Structural resonances in the physical links.

A simulation-to-hardware analysis does not require actually building the hardware. It requires systematically identifying the assumptions in the simulation model that are most likely to break on hardware, and then either: analyzing whether the controllers are robust to each effect, or flagging each as a known limitation with a suggested mitigation.

For example: quantization. The simulation uses continuous floating-point angles. A real encoder with 2000 counts per revolution gives angular resolution of roughly 0.18 degrees. The Lyapunov condition requires sigma to reach zero. Can sigma reach zero with quantized angles? The answer involves the dead zone in the adaptation law and the boundary layer width. This analysis can be done analytically.

The six effects that need to be addressed: actuator dynamics and saturation, encoder quantization, delays and noise, unmodeled friction and stiction, structural flexibility and resonance, and real-time compute jitter. Each one has a standard mitigation approach in the SMC literature.

## Gap 3: PSO Computational Cost

The report documents PSO configuration - 40 particles, 200 iterations, three controllers taking minutes each. But it does not give specific wall-clock times per controller.

This matters for two reasons. First, reproducibility: if someone wants to reproduce the PSO results, knowing the expected compute time helps them plan. Second, comparison: the simplified versus full model choice for PSO was motivated by speed - but how much faster is it?

The specific items needed: per-controller PSO wall-clock time on the reference machine, CPU and memory specs, and a comparison of simplified versus full model simulation time to justify the speedup claim.

This is purely a measurement and documentation task, not a new experiment. The PSO runs were already done. The times just need to be logged and reported.

## Gap 4: QW-2 Baseline Reproducibility

The QW-2 study appears in the report as the baseline single-run validation. Confidence intervals for Hybrid Adaptive STA settling time and overshoot - the numbers that appear in the second CI table - come from this study.

The problem: the exact initial conditions vector and scenario settings for QW-2 are not stated in the main text. A reader cannot reproduce the QW-2 result without knowing the starting state.

This is a straightforward documentation gap. Adding three lines to the main text - the initial state vector used in QW-2, the simulation duration, and the noise or disturbance level if any - closes it completely.

## Gap 5: Figure Callout Integration

The report has a list of completed figures: system architecture diagram, control loop schematic, Lyapunov phase portrait, PSO convergence 3D surface. All figures exist and meet the 300 DPI quality standard.

The gap: not all figures are referenced in the text with explicit callout phrases. Academic writing convention requires every figure to have at least one in-body reference - "as shown in Figure 3" or "see Figure 5 for the phase portrait." If a figure has no callout, it appears to float in the document with no connection to the narrative.

This is a line-editing task, not a technical one. Go through each figure, find where in the text it is most relevant, and add the callout sentence. Estimated effort: one to two hours.

## Gap 6: Dedicated Future Work Section

The report currently documents limitations and open issues inline - scattered through individual sections as "known limitations," "open issues," and "required additions." This is useful for a progress memo but not for a thesis.

A thesis needs a dedicated Future Work section that:
- Collects all open items in one place
- Prioritizes them by importance and feasibility
- Links each item to the corresponding thesis contribution it would extend
- Distinguishes between items that are essential for the current claims (like the STA robust gain resolution) and items that would extend the work (like hardware validation)

The ranked priority list from the report gives a starting structure: constrained robust STA re-tuning first, finer MT-6 epsilon sweep second, hardware validation third. The section should be concise - one paragraph per item, five to six items total.

## The Completion Timeline

The report documents a completion plan with specific target dates.

Phases 1 and 2 - figures and tables - are already done. That was the work that brought the score from whatever it was before to 90 out of 100.

Phase 3: bibliography expansion by 15 or more references, target January 10. This supports the literature comparison gap and the STA stability proof gap.

Phase 4: proofreading pass, target January 13.

Phase 5: final QA audit - checking all figure callouts, all cross-references, all equation labels - target January 14.

Phase 6: advisor review, target January 24. That is the final deadline.

The remaining point total is 10 points spread across these phases. The research paper - LT-7 - is separately marked as submission-ready at version 2.1.

## Takeaway

Ninety percent complete is not finished. The six gaps - literature comparison, simulation-to-hardware analysis, PSO compute costs, QW-2 reproducibility, figure callouts, and future work section - are specific and actionable. None of them require new experiments. They require analysis, documentation, and literature search. Three to four focused working sessions should close all of them.

The thesis is not at "almost done hoping nothing comes up." It is at "specifically known what remains, with a date for each item." That is a defensible position.

Final episode: the complete advisor defense rehearsal - the seven most likely questions and how to answer each one.

---

*References: Gap analysis based on advisor_progress_report.tex and audit checklist mapping.*
