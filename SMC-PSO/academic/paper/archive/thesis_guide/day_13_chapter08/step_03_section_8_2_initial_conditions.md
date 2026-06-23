# Step 3: Write Section 8.2 - Initial Conditions

**Time**: 1 hour
**Output**: 2 pages
**Source**: thesis/notes/chapter08_initial_conditions.txt

---

## EXACT PROMPT

```
Write Section 8.2 - Initial Conditions (2 pages) for Chapter 8.

Structure (2 pages):

**Page 1: Standard Initial Condition**

Subsection: Baseline State
- State vector: x = [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]ᵀ
- Standard IC: x₀ = [0.1, 0.05, 0.03, 0, 0, 0]ᵀ
- Rationale: Small perturbation from unstable equilibrium
- Physical interpretation:
  * Cart displaced 10 cm to right
  * Pendulum 1 tilted 2.86° from vertical
  * Pendulum 2 tilted 1.72° from vertical
  * All velocities initially zero (released from rest)

Table 8.1: Standard Initial Condition
| Variable | Symbol | Value | Units | Physical Meaning |
|----------|--------|-------|-------|------------------|
| Cart position | x | 0.1 | m | 10 cm right of origin |
| Pendulum 1 angle | θ₁ | 0.05 | rad | 2.86° from vertical |
| Pendulum 2 angle | θ₂ | 0.03 | rad | 1.72° from vertical |
| Cart velocity | ẋ | 0 | m/s | At rest |
| Pendulum 1 angular velocity | θ̇₁ | 0 | rad/s | At rest |
| Pendulum 2 angular velocity | θ̇₂ | 0 | rad/s | At rest |

**Page 2: Robustness Test Initial Conditions**

Subsection: Multiple Initial Conditions (LT-6)
- IC1 (Small): [0.05, 0.03, 0.02, 0, 0, 0]ᵀ - 50% of standard
- IC2 (Medium): [0.1, 0.05, 0.03, 0, 0, 0]ᵀ - Standard (100%)
- IC3 (Large): [0.2, 0.1, 0.08, 0, 0, 0]ᵀ - 200% of standard
- IC4 (Extreme): [0.3, 0.15, 0.12, 0, 0, 0]ᵀ - 300% of standard

Purpose: Evaluate controller performance across varying perturbation magnitudes

Subsection: Monte Carlo Initial Conditions (if used)
- Random perturbations: x₀ + δx, where δx ~ U(-0.01, 0.01) for each component
- Number of trials: 100
- Seed: 42 (reproducibility)
- Purpose: Statistical analysis of robustness

Summary: "The standard IC represents a typical small perturbation. Robustness tests use 4 IC magnitudes spanning 50-300% of standard to evaluate controller performance limits."

Citations: cite:LT6 (robustness report)

Length: 2 pages
```

---

## WHAT TO DO

1. **Create Table 8.1** (15 min) - LaTeX booktabs format
2. **Verify IC values** (5 min) - Check against config.yaml
3. **Format as LaTeX** (10 min)

---

## VALIDATION

- [ ] Table 8.1 present with 6 rows
- [ ] 4 robustness ICs listed (IC1-IC4)
- [ ] Physical interpretation clear (degrees, cm)
- [ ] 1.8-2.2 pages

---

## TIME: ~1 hour

## NEXT STEP: `step_04_section_8_3_disturbances.md`
