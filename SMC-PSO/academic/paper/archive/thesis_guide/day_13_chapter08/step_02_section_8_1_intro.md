# Step 2: Write Section 8.1 - Introduction to Simulation Setup

**Time**: 45 minutes
**Output**: 1.5 pages
**Goal**: Overview of experimental design and chapter organization

---

## EXACT PROMPT

```
Write Section 8.1 - Introduction (1.5 pages) for Chapter 8 (Simulation Setup).

Context:
- Chapter 8 of 200-page Master's thesis
- Describes experimental setup for Chapters 10-12 results
- IEEE style, formal academic tone

Structure:

Paragraph 1: Purpose of experimental design
- Systematic evaluation requires careful setup
- Four key aspects: initial conditions, disturbances, metrics, hardware
- Emphasis on reproducibility (global seed: 42, configuration files)

Paragraph 2: Experimental scenarios
- Baseline: Nominal conditions, no disturbances
- Robustness: 4 initial conditions (small/medium/large/extreme)
- Disturbance rejection: Step (10N @ t=2s), Impulse (30N pulse)
- Uncertainty: ±20% mass, ±10% length, ±30% friction variations

Paragraph 3: Chapter organization
- Section 8.2: Initial conditions and state-space setup
- Section 8.3: Disturbance scenarios (step, impulse, combined)
- Section 8.4: Performance metrics (6 metrics defined)
- Section 8.5: Hardware specifications and computational cost

Summary: "All experiments use identical setup to enable fair controller comparison. Complete configuration files are provided in Appendix D."

Citations: cite:config (config.yaml documentation)

Length: 1.5 pages
```

---

## VALIDATION

- [ ] 4 experimental scenarios listed
- [ ] Chapter organization clear
- [ ] Reproducibility emphasized
- [ ] 1.3-1.7 pages when compiled

---

## TIME: ~45 min

## NEXT STEP: `step_03_section_8_2_initial_conditions.md`
