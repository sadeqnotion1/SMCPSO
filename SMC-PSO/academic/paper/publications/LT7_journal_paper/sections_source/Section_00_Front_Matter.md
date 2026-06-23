# Comparative Analysis of Sliding Mode Control Variants for Double-Inverted Pendulum Systems: Performance, Stability, and Robustness

**Authors:** [Author Names]¹*
**Affiliation:** ¹[Institution Name, Department, City, Country]
**Email:** [corresponding.author@institution.edu]
**ORCID:** [0000-0000-0000-0000]

---

**SUBMISSION INFORMATION:**
- **Document ID:** LT-7-RESEARCH-PAPER-v2.1
- **Status:** SUBMISSION-READY (98% Complete)
- **Date:** November 6, 2025
- **Word Count:** ~13,400 words (~25 journal pages)
- **References:** 68 citations (IEEE format)
- **Figures:** 13 tables, 14 figures (publication-ready, 300 DPI)
- **Supplementary Materials:** Code repository (https://github.com/theSadeQ/dip-smc-pso.git), simulation data
- **Target Journals:** International Journal of Control (Tier 3, best length fit), IEEE TCST (Tier 1, requires condensing)

**REMAINING TASKS FOR SUBMISSION:**
1. ✅ ALL TECHNICAL CONTENT COMPLETE (Sections 1-10, References)
2. ✅ ALL [REF] PLACEHOLDERS REPLACED WITH CITATION NUMBERS
3. ✅ ALL FIGURES INTEGRATED (14 figures with detailed captions)
4. ⏸️ Add author names, affiliations, emails (replace placeholders above)
5. ⏸️ Convert Markdown → LaTeX using journal template
6. ⏸️ Final proofread and spell check
7. ⏸️ Prepare cover letter and suggested reviewers

**Phase:** Phase 5 (Research) | **Task ID:** LT-7 (Long-Term Task 7, 20 hours invested)

---

## Abstract

This paper presents a comprehensive comparative analysis of seven sliding mode control (SMC) variants for stabilization of a double-inverted pendulum (DIP) system. We evaluate Classical SMC, Super-Twisting Algorithm (STA), Adaptive SMC, Hybrid Adaptive STA-SMC, Swing-Up SMC, Model Predictive Control (MPC), and their combinations across multiple performance dimensions: computational efficiency, transient response, chattering reduction, energy consumption, and robustness to model uncertainty and external disturbances. Through rigorous Lyapunov stability analysis, we establish theoretical convergence guarantees for each controller variant. Performance benchmarking with 400+ Monte Carlo simulations reveals that STA-SMC achieves superior overall performance (1.82s settling time, 2.3% overshoot, 11.8J energy), while Classical SMC provides the fastest computation (18.5 microseconds). PSO-based optimization demonstrates significant performance improvements but reveals critical generalization limitations: parameters optimized for small perturbations (±0.05 rad) exhibit 49.3x chattering degradation (RMS-based) and 90.2% failure rate under realistic disturbances (±0.3 rad). Robustness analysis with ±20% model parameter errors shows Hybrid Adaptive STA-SMC offers best uncertainty tolerance (16% mismatch before instability), while STA-SMC excels at disturbance rejection (91% attenuation). Our findings provide evidence-based controller selection guidelines for practitioners and identify critical gaps in current optimization approaches for real-world deployment.

**Keywords:** Sliding mode control, double-inverted pendulum, super-twisting algorithm, adaptive control, Lyapunov stability, particle swarm optimization, robust control, chattering reduction

---

