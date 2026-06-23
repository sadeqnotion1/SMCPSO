# Step 5: Write Section 8.4 - Performance Metrics

**Time**: 1 hour
**Output**: 2.5 pages
**Source**: thesis/notes/chapter08_metrics.txt

---

## EXACT PROMPT

```
Write Section 8.4 - Performance Metrics (2.5 pages) for Chapter 8.

Structure (2.5 pages):

**Page 1: Primary Metrics**

Subsection: Settling Time (t_s)
- Definition: Time for state to reach and remain within 2% band of reference
- Mathematical criterion: t_s = min{t : ||x(τ)||₂ < 0.02 for all τ > t}
- Threshold: |θ₁| < 0.02 rad AND |θ₂| < 0.02 rad AND |x| < 0.02 m
- Units: seconds
- Typical values: 2-8 s (good controller), >10 s (poor), ∞ (unstable)
- Importance: Primary performance indicator

Subsection: Maximum Overshoot (M_p)
- Definition: Peak deviation from reference during transient
- Formula: M_p = max_{t∈[0,t_s]} ||x(t)||₂
- Units: Dimensionless (normalized to IC) or meters/radians (absolute)
- Typical values: 0.05-0.20 rad (acceptable), >0.30 rad (excessive)
- Importance: Safety constraint (physical limits)

Subsection: Steady-State Error (e_ss)
- Definition: Residual error at simulation end
- Formula: e_ss = ||x(t_final)||₂
- Target: e_ss < 0.01 (converged)
- Failure: e_ss > 0.1 (diverged or poor tracking)
- Importance: Final accuracy

**Page 2: Secondary Metrics**

Subsection: Control Effort (E)
- Definition: Integrated squared control signal
- Formula: E = ∫₀^T u²(t) dt ≈ Σᵢ uᵢ² Δt
- Units: N²·s
- Physical meaning: Energy consumption
- Typical values: 100-5000 N²·s
- Importance: Actuator wear, energy efficiency

Subsection: Chattering Index (C)
- Definition: Sum of absolute control changes
- Formula: C = Σᵢ₌₁ⁿ |uᵢ - uᵢ₋₁|
- Units: N
- Physical meaning: High-frequency switching intensity
- Typical values: 500-10,000 N (low chattering), >20,000 N (high)
- Importance: Actuator lifespan, practical feasibility

Subsection: Convergence Rate (λ) - Optional
- Definition: Exponential decay rate from initial condition
- Fit: ||x(t)|| ≈ ||x₀|| exp(-λt)
- Units: 1/s (or rad/s)
- Estimation: Linear regression on log(||x(t)||) vs t
- Importance: Characterizes transient dynamics

**Page 3: Composite Ranking**

Subsection: Multi-Objective Performance Index
- Weighted sum for controller ranking (Chapter 10)
- Formula: J = 0.3·(t_s/t_s,max) + 0.25·(M_p/M_p,max) + 0.2·e_ss + 0.15·(E/E_max) + 0.1·(C/C_max)
- Weights justified: Settling time and overshoot most critical (safety), control effort moderate importance (energy), chattering lowest weight (practical concern)
- Normalization: Each metric divided by maximum observed value
- Result: J ∈ [0,1], lower is better

Table 8.3: Performance Metrics Summary
| Metric | Symbol | Formula | Units | Weight | Importance |
|--------|--------|---------|-------|--------|------------|
| Settling time | t_s | min{t: ‖x(τ)‖<0.02, τ>t} | s | 0.30 | Primary |
| Overshoot | M_p | max ‖x(t)‖ | rad | 0.25 | Primary |
| Steady-state error | e_ss | ‖x(t_final)‖ | - | 0.20 | Primary |
| Control effort | E | Σ u² Δt | N²·s | 0.15 | Secondary |
| Chattering | C | Σ |Δu| | N | 0.10 | Secondary |

Summary: "Six metrics provide comprehensive evaluation: three primary (accuracy, safety) and three secondary (energy, feasibility). Composite ranking enables fair multi-objective comparison in Chapter 10."

Citations: cite:Ogata2009 (control metrics), cite:QW2 (ranking methodology)

Length: 2.5 pages
```

---

## WHAT TO DO

1. **Create Table 8.3** (15 min) - Performance metrics summary
2. **Verify formulas** (10 min) - Check against src/utils/analysis/
3. **Format as LaTeX** (10 min)

---

## VALIDATION

- [ ] All 6 metrics defined with formulas
- [ ] Units specified for each metric
- [ ] Typical value ranges provided
- [ ] Table 8.3 with 6 rows
- [ ] Composite ranking formula explained
- [ ] 2.3-2.7 pages

---

## TIME: ~1 hour

## NEXT STEP: `step_06_section_8_5_hardware_specs.md`
