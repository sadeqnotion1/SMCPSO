# Step 4: Write Section 8.3 - Disturbance Scenarios

**Time**: 1 hour
**Output**: 2 pages
**Source**: thesis/notes/chapter08_disturbances.txt

---

## EXACT PROMPT

```
Write Section 8.3 - Disturbance Scenarios (2 pages) for Chapter 8.

Structure (2 pages):

**Page 1: External Force Disturbances**

Subsection: Step Disturbance
- Type: Constant force applied to cart
- Mathematical model: d(t) = 10·H(t-2), where H is Heaviside function
- Magnitude: 10 N
- Application time: t = 2.0 s (after initial stabilization)
- Duration: 1.0 s (until t_final = 3.0 s)
- Purpose: Test steady-state disturbance rejection
- Physical interpretation: Equivalent to 1 kg mass suddenly added to cart

Subsection: Impulse Disturbance
- Type: Short-duration pulse
- Mathematical model: d(t) = 30·[H(t-2) - H(t-2.1)]
- Magnitude: 30 N
- Application time: t = 2.0 s
- Duration: 0.1 s (100 ms)
- Impulse: ∫d(t)dt = 3 N·s
- Purpose: Test transient disturbance rejection
- Physical interpretation: Equivalent to rapid collision or impact

Include Figure 8.1: Disturbance profiles (time plots showing step and impulse)

**Page 2: Parameter Uncertainty**

Subsection: Model Parameter Variations (LT-6)
- Mass variations: m_cart, m₁, m₂ varied by ±20%
- Length variations: L₁, L₂ varied by ±10%
- Friction variations: b_cart, b₁, b₂ varied by ±30%
- Combinations: 2³ × 2² × 2³ = 64 total scenarios (if all permutations)
- Typical: 5 scenarios (nominal, +mass, -mass, +length, -length)

Table 8.2: Parameter Uncertainty Scenarios
| Scenario | Mass | Length | Friction | Description |
|----------|------|--------|----------|-------------|
| Nominal | 100% | 100% | 100% | Baseline model |
| Heavy | +20% | 100% | 100% | Increased inertia |
| Light | -20% | 100% | 100% | Decreased inertia |
| Long | 100% | +10% | 100% | Increased leverage |
| Short | 100% | -10% | 100% | Decreased leverage |

Subsection: Noise (if included)
- Sensor noise: Gaussian noise added to state measurements
- Position noise: σ_x = 0.001 m (1 mm standard deviation)
- Angle noise: σ_θ = 0.001 rad (0.057°)
- Purpose: Realistic sensor imperfections

Summary: "Disturbance scenarios test three robustness aspects: external forces (step/impulse), model uncertainty (parameter variations), and measurement noise. These represent realistic operating conditions."

Citations: cite:MT8 (robust PSO), cite:LT6 (uncertainty analysis)

Length: 2 pages
```

---

## WHAT TO DO

1. **Create Figure 8.1** (15 min) - Matplotlib script for disturbance plots
2. **Create Table 8.2** (10 min) - Parameter uncertainty scenarios
3. **Format as LaTeX** (10 min)

---

## VALIDATION

- [ ] Step and impulse disturbances defined mathematically
- [ ] Figure 8.1 shows disturbance time profiles
- [ ] Table 8.2 lists 5 uncertainty scenarios
- [ ] Physical interpretation provided
- [ ] 1.8-2.2 pages

---

## TIME: ~1 hour

## NEXT STEP: `step_05_section_8_4_performance_metrics.md`
