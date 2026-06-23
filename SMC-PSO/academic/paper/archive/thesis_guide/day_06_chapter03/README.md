# DAY 6: Chapter 3 - Problem Formulation

**Time**: 8 hours
**Output**: 10-12 pages
**Difficulty**: Moderate

---

## OVERVIEW

Day 6 formalizes the control problem: what system are we controlling, what are the objectives, what constraints exist, and how do we measure success? This chapter bridges the literature review (Chapter 2) and mathematical modeling (Chapter 4).

**Why This Matters**: Clear problem formulation ensures readers understand exactly what you're solving before diving into solutions.

---

## OBJECTIVES

By end of Day 6, you will have:

1. [ ] Section 3.1: DIP system description with schematic (2 pages)
2. [ ] Section 3.2: Control objectives mathematically defined (2 pages)
3. [ ] Section 3.3: Physical and safety constraints (2 pages)
4. [ ] Section 3.4: Performance metrics specification (2 pages)
5. [ ] Section 3.5: Formal problem statement (2 pages)
6. [ ] System schematic figure (Figure 3.1)
7. [ ] Control objectives table (Table 3.1)

---

## TIME BREAKDOWN

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | Extract existing problem statement | 1 hour | Base content (57 lines) |
| 2 | Write Section 3.1 (System description) | 1.5 hours | 2 pages |
| 3 | Write Section 3.2 (Control objectives) | 1.5 hours | 2 pages |
| 4 | Write Section 3.3 (Constraints) | 1.5 hours | 2 pages |
| 5 | Write Section 3.4 (Performance metrics) | 1.5 hours | 2 pages |
| 6 | Write Section 3.5 (Problem statement) | 1 hour | 2 pages |
| 7 | Create figure and table | 1 hour | Figure 3.1, Table 3.1 |
| **TOTAL** | | **8 hours** | **10-12 pages** |

---

## STEPS

### Step 1: Extract Existing Content (1 hour)
**File**: `step_01_extract_sources.md`
- Read `docs/thesis/chapters/01_problem_statement.md` (57 lines)
- Convert to LaTeX base
- Identify sections to expand

### Step 2: Section 3.1 - System Description (1.5 hours)
**File**: `step_02_section_3_1_system.md`
- Physical description: cart, two pendulums, rails
- Degrees of freedom: x, θ₁, θ₂
- Control input: force u on cart
- Underactuated nature (1 input, 3 DOF)

### Step 3: Section 3.2 - Control Objectives (1.5 hours)
**File**: `step_03_section_3_2_objectives.md`
- Stabilization: both pendulums upright
- Regulation: cart returns to center
- Disturbance rejection: external forces
- Robustness: parameter uncertainties

### Step 4: Section 3.3 - Constraints (1.5 hours)
**File**: `step_04_section_3_3_constraints.md`
- Input saturation: |u| ≤ u_max
- State constraints: rail length limits |x| ≤ x_max
- Angle limits: |θ₁|, |θ₂| ≤ some safe range
- Safety requirements

### Step 5: Section 3.4 - Performance Metrics (1.5 hours)
**File**: `step_05_section_3_4_metrics.md`
- Settling time (t_s)
- Maximum overshoot (M_p)
- Steady-state error (e_ss)
- Control effort (integral |u| dt)
- Chattering metric (FFT analysis)

### Step 6: Section 3.5 - Formal Problem Statement (1 hour)
**File**: `step_06_section_3_5_statement.md`
- Mathematical formulation
- Optimization problem statement
- Multi-objective nature

### Step 7: Create Visuals (1 hour)
**File**: `step_07_figure_table.md`
- Figure 3.1: DIP schematic with labels
- Table 3.1: Control objectives summary

---

## SOURCE FILES

### Primary Source (57 lines - needs expansion!)
- `docs/thesis/chapters/01_problem_statement.md`
  - Lines 1-20: Control objectives
  - Lines 21-40: Constraints
  - Lines 41-57: Metrics

### Secondary Sources

**For System Description**:
- `docs/guides/theory/dip-dynamics.md` (physical description)
- `config.yaml` (parameter values: m₀, m₁, m₂, L₁, L₂)
- System schematic (if exists in docs/)

**For Constraints**:
- `config.yaml` - simulation_settings section
  - u_max value
  - x_bounds
  - angle limits

**For Metrics**:
- `docs/theory/smc_theory_complete.md` (performance definitions)
- `src/utils/analysis/chattering.py` (chattering metrics)
- Benchmark CSV files (shows which metrics are used)

---

## EXPECTED OUTPUT

### Section 3.1: System Description (2 pages)
- Physical components: cart (m₀), pendulum 1 (m₁, L₁), pendulum 2 (m₂, L₂)
- State vector: x = [x, ẋ, θ₁, θ̇₁, θ₂, θ̇₂]ᵀ ∈ ℝ⁶
- Control input: u ∈ ℝ (horizontal force on cart)
- Underactuated: dim(u) < dim(q) where q = [x, θ₁, θ₂]
- Figure 3.1: Side-view schematic with labeled components

### Section 3.2: Control Objectives (2 pages)
1. **Stabilization**: lim_{t→∞} θ₁(t) = 0, lim_{t→∞} θ₂(t) = 0
2. **Regulation**: lim_{t→∞} x(t) = 0
3. **Disturbance Rejection**: ‖x(t)‖ bounded under d(t)
4. **Robustness**: Performance maintained under Δp ∈ [-30%, +30%]

Table 3.1: Control Objectives Summary

### Section 3.3: Constraints (2 pages)
- Input saturation: u(t) ∈ [-u_max, u_max] = [-50N, 50N]
- Position limits: x(t) ∈ [-1.5m, 1.5m] (rail length)
- Angle safety: θ₁, θ₂ ∈ [-π/2, π/2] (avoid collisions)
- Rate limits: |u̇| ≤ 500 N/s (actuator dynamics)

### Section 3.4: Performance Metrics (2 pages)
- **Settling time**: t_s = min{t : |θ₁(t')| < 0.01, |θ₂(t')| < 0.01, ∀t' > t}
- **Overshoot**: M_p = max(θ₁(t)) for t ∈ [0, t_s]
- **Steady-state error**: e_ss = lim_{t→∞} ‖[x, θ₁, θ₂]ᵀ‖
- **Control effort**: J_u = ∫₀^T |u(t)| dt
- **Chattering**: C = amplitude of dominant FFT frequency

### Section 3.5: Formal Problem Statement (2 pages)
Given DIP system dynamics, find control law u = u(x, t) that:
1. Stabilizes x = 0 (equilibrium)
2. Satisfies constraints u ∈ U, x ∈ X
3. Minimizes cost J = w₁·t_s + w₂·J_u + w₃·C
4. Maintains robustness under parameter uncertainty
5. Achieves performance: t_s < 5s, e_ss < 0.01 rad

---

## VALIDATION CHECKLIST

### Content Completeness
- [ ] All 5 sections present (3.1-3.5)
- [ ] System fully described (state, input, parameters)
- [ ] Objectives mathematically defined (not just words)
- [ ] All constraints quantified (with numerical bounds)
- [ ] Metrics have formulas (not just names)

### Mathematical Rigor
- [ ] State vector defined: x ∈ ℝⁿ
- [ ] Control input defined: u ∈ U ⊂ ℝᵐ
- [ ] Objectives have lim_{t→∞} statements
- [ ] Constraints have set notation: u ∈ [-u_max, u_max]
- [ ] Problem statement is solvable (not over-constrained)

### Figures and Tables
- [ ] Figure 3.1: DIP schematic clear and labeled
- [ ] Table 3.1: Objectives summary with 4-5 rows
- [ ] Both referenced in text
- [ ] Both have captions and labels

### Consistency with Other Chapters
- [ ] Matches Chapter 1 (objectives stated there)
- [ ] Prepares for Chapter 4 (parameters used in modeling)
- [ ] Aligns with Chapter 10-12 (metrics match results)

### LaTeX Quality
- [ ] Compiles without errors
- [ ] Math notation consistent with nomenclature
- [ ] Cross-references work (\cref{fig:system_schematic})
- [ ] Page count: 10-12 pages

---

## TROUBLESHOOTING

### Issue: Section 3.5 feels redundant with 3.1-3.4

**Solution**: Section 3.5 synthesizes into formal optimization problem
- 3.1-3.4: Prose descriptions
- 3.5: Mathematical formulation combining all elements

### Issue: Don't know parameter values (u_max, x_max)

**Solution**: Extract from config.yaml
```bash
grep -A 10 "simulation_settings:" config.yaml
```

### Issue: Figure 3.1 schematic missing

**Solution**: Create with:
- TikZ (LaTeX drawing package) - best for publication
- PowerPoint/Draw.io → export as PDF
- Hand-drawn → scan → include as image

---

## NEXT STEPS

Once Day 6 checklist is complete:

1. Verify problem statement is mathematically complete
2. Check all symbols defined in nomenclature
3. Read `day_07_chapter04/README.md` (10 min)

**Tomorrow (Day 7)**: Write Chapter 4 - Mathematical Modeling (15-18 pages)

---

## ESTIMATED COMPLETION TIME

- **Beginner**: 9-10 hours (learning formal problem statements)
- **Intermediate**: 7-8 hours (some control theory background)
- **Advanced**: 6-7 hours (experienced with optimization formulations)

---

**[OK] Ready to formalize the problem? Open `step_01_extract_sources.md`!**
