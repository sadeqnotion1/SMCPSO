# DAY 7: Chapter 4 - Mathematical Modeling

**Time**: 8 hours
**Output**: 15-18 pages
**Difficulty**: Hard (complex derivations)

---

## OVERVIEW

Day 7 derives the mathematical model of the DIP system using Lagrangian mechanics. This is the most equation-heavy chapter, showing how physical laws produce the nonlinear differential equations that controllers must handle.

**Why This Matters**: Mathematical model is the foundation for all controller design. Rigorous derivation shows you understand the physics.

---

## OBJECTIVES

By end of Day 7, you will have:

1. [ ] Section 4.1: Lagrangian formulation (4 pages)
2. [ ] Section 4.2: State-space representation (3 pages)
3. [ ] Section 4.3: Simplified model derivation (3 pages)
4. [ ] Section 4.4: Full nonlinear model (4 pages)
5. [ ] Section 4.5: Physical parameters table (2 pages)
6. [ ] Complete equations of motion (20-30 equations)
7. [ ] Parameter values table (Table 4.1)

---

## TIME BREAKDOWN

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | Extract existing modeling content | 1 hour | 32 lines base |
| 2 | Write Section 4.1 (Lagrangian) | 2 hours | 4 pages |
| 3 | Write Section 4.2 (State-space) | 1.5 hours | 3 pages |
| 4 | Write Section 4.3 (Simplified model) | 1.5 hours | 3 pages |
| 5 | Write Section 4.4 (Full model) | 2 hours | 4 pages |
| 6 | Write Section 4.5 (Parameters) | 1 hour | 2 pages |
| **TOTAL** | | **8 hours** | **15-18 pages** |

---

## STEPS

### Step 1: Extract Existing Content (1 hour)
**File**: `step_01_extract_sources.md`
- Read `docs/thesis/chapters/03_system_modeling.md` (32 lines - brief!)
- Extract equations from `src/core/dynamics.py` docstrings
- Identify what needs expansion

### Step 2: Section 4.1 - Lagrangian Formulation (2 hours)
**File**: `step_02_section_4_1_lagrangian.md`
- Define generalized coordinates: q = [x, θ₁, θ₂]
- Kinetic energy: T = T_cart + T_pend1 + T_pend2
- Potential energy: V = V_pend1 + V_pend2
- Lagrangian: L = T - V
- Euler-Lagrange equations: d/dt(∂L/∂q̇) - ∂L/∂q = Q

### Step 3: Section 4.2 - State-Space (1.5 hours)
**File**: `step_03_section_4_2_statespace.md`
- State vector: x = [x, ẋ, θ₁, θ̇₁, θ₂, θ̇₂]ᵀ
- State-space form: ẋ = f(x, u)
- Affine form: ẋ = f(x) + g(x)u
- Linearization around equilibrium

### Step 4: Section 4.3 - Simplified Model (1.5 hours)
**File**: `step_04_section_4_3_simplified.md`
- Assumptions: small angles, massless links
- Linearized dynamics: ẋ = Ax + Bu
- Matrices A and B
- Comparison with full model

### Step 5: Section 4.4 - Full Nonlinear Model (2 hours)
**File**: `step_05_section_4_4_full.md`
- Mass matrix M(q)
- Coriolis/centrifugal matrix C(q, q̇)
- Gravity vector G(q)
- Equation: M(q)q̈ + C(q,q̇)q̇ + G(q) = Bu
- Code implementation reference

### Step 6: Section 4.5 - Physical Parameters (1 hour)
**File**: `step_06_section_4_5_parameters.md`
- Table 4.1: All parameter values from config.yaml
- Parameter uncertainty ranges
- Units and typical values

---

## SOURCE FILES

### Primary Source (32 lines - heavily expand!)
- `docs/thesis/chapters/03_system_modeling.md`

### Secondary Sources (critical!)

**For Lagrangian Derivation**:
- `docs/guides/theory/dip-dynamics.md` (if exists)
- Fantoni & Lozano (2001) - Underactuated Systems book
- Lagrangian mechanics reference

**For State-Space**:
- `src/core/dynamics.py` (lines 50-150)
  - SimplifiedDynamics class
  - compute_derivatives() method
  - Docstrings explain equations

**For Full Model**:
- `src/core/dynamics_full.py` (lines 80-250)
  - FullDynamics class
  - Mass matrix M(q)
  - Coriolis matrix C(q, q̇)
  - Gravity vector G(q)

**For Parameters**:
- `config.yaml` - physics section
  - m0, m1, m2 (masses)
  - L1, L2 (lengths)
  - g (gravity)
  - friction coefficients

---

## EXPECTED OUTPUT

### Section 4.1: Lagrangian (4 pages)

Generalized coordinates:
```
q = [x, θ₁, θ₂]ᵀ
```

Kinetic energy (cart):
```
T_0 = (1/2) m₀ ẋ²
```

Kinetic energy (pendulum 1):
```
T_1 = (1/2) m₁ [(ẋ + L₁cos(θ₁)θ̇₁)² + (L₁sin(θ₁)θ̇₁)²]
```

Potential energy (pendulum 1):
```
V_1 = m₁ g L₁ cos(θ₁)
```

Lagrangian:
```
L = T - V = (T_0 + T_1 + T_2) - (V_1 + V_2)
```

Euler-Lagrange:
```
d/dt(∂L/∂ẋ) - ∂L/∂x = u
d/dt(∂L/∂θ̇₁) - ∂L/∂θ₁ = 0
d/dt(∂L/∂θ̇₂) - ∂L/∂θ₂ = 0
```

### Section 4.2: State-Space (3 pages)

State vector:
```
x = [x, ẋ, θ₁, θ̇₁, θ₂, θ̇₂]ᵀ ∈ ℝ⁶
```

State-space form:
```
ẋ = f(x, u) = [ẋ, f_2(x,u), θ̇₁, f_4(x,u), θ̇₂, f_6(x,u)]ᵀ
```

Affine form:
```
ẋ = f(x) + g(x)u
```

### Section 4.3: Simplified Model (3 pages)

Small angle approximation:
```
sin(θ) ≈ θ, cos(θ) ≈ 1
```

Linearized matrices:
```
A = [matrix values]
B = [matrix values]
```

### Section 4.4: Full Model (4 pages)

Mass matrix:
```
M(q) = [3×3 matrix with m₀, m₁, m₂, L₁, L₂ terms]
```

Equation of motion:
```
M(q)q̈ + C(q,q̇)q̇ + G(q) = Bu
```

Where B = [1, 0, 0]ᵀ

### Section 4.5: Parameters (2 pages)

Table 4.1: Physical Parameters

| Symbol | Description | Value | Unit |
|--------|-------------|-------|------|
| m₀ | Cart mass | 5.0 | kg |
| m₁ | Pendulum 1 mass | 1.0 | kg |
| m₂ | Pendulum 2 mass | 0.5 | kg |
| L₁ | Pendulum 1 length | 0.5 | m |
| L₂ | Pendulum 2 length | 0.3 | m |
| g | Gravity | 9.81 | m/s² |

---

## VALIDATION CHECKLIST

### Mathematical Correctness
- [ ] All equations dimensionally consistent
- [ ] Lagrangian derivation steps shown (not just result)
- [ ] Mass matrix M(q) is 3×3 and symmetric
- [ ] Gravity vector G(q) matches potential energy gradient
- [ ] State-space has 6 equations (one per state)

### Code Consistency
- [ ] Equations match `src/core/dynamics.py` implementation
- [ ] Parameter values match `config.yaml`
- [ ] Variable names consistent (use θ not theta in equations)

### Presentation Quality
- [ ] Equations numbered: \begin{equation} \label{eq:lagrangian}
- [ ] Referenced in text: "Equation \ref{eq:lagrangian} shows..."
- [ ] Large equations broken across lines
- [ ] Clear notation (define every symbol first time used)

### Completeness
- [ ] Both simplified and full models derived
- [ ] Conversion to state-space shown
- [ ] All parameters tabulated
- [ ] Comparison: simplified vs. full models

---

## TROUBLESHOOTING

### Lagrangian Derivation Too Complex

**Problem**: Full derivation would take 10+ pages
**Solution**:
- Show setup and first term fully
- State "similarly for other terms..."
- Give final result
- Cite reference for detailed steps

### Equations Don't Match Code

**Problem**: dynamics.py uses different formulation
**Solution**:
- Document both formulations
- Explain equivalence
- Thesis uses mathematical form
- Code uses computational form (numerically stable)

### LaTeX Math Rendering Issues

**Problem**: Equation too wide for page
**Solution**:
```latex
\begin{align}
  long_equation_part_1 \\
  &\quad + long_equation_part_2 \\
  &\quad + long_equation_part_3
\end{align}
```

---

## NEXT STEPS

Once Day 7 checklist is complete:

1. Verify all equations compile
2. Check equation numbers sequential
3. Cross-reference with code
4. Read `day_08_09_chapter05/README.md` (10 min)

**Days 8-9**: Write Chapter 5 - SMC Theory (20-25 pages, 2 days)

---

## ESTIMATED COMPLETION TIME

- **Beginner**: 10-12 hours (learning Lagrangian mechanics)
- **Intermediate**: 8-9 hours (some dynamics background)
- **Advanced**: 6-7 hours (familiar with underactuated systems)

**Math-heavy chapter** - Budget extra time for typesetting equations in LaTeX.

---

**[OK] Ready for the physics? Open `step_01_extract_sources.md`!**
