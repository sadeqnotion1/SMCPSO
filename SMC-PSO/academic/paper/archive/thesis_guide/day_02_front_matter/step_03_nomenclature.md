# Step 3: Create Nomenclature

**Time**: 2 hours
**Output**: 4-5 pages (Complete list of mathematical symbols)
**Source**: `docs/theory/smc_theory_complete.md`, `config.yaml`

---

## OBJECTIVE

Create a comprehensive nomenclature listing ALL mathematical symbols, operators, and abbreviations used in your thesis.

---

## SOURCE MATERIALS TO EXTRACT (30 min)

### Primary Sources
1. **Read**: `D:\Projects\main\docs\theory\smc_theory_complete.md`
   - Extract all SMC notation (s, lambda, phi, K, etc.)

2. **Read**: `D:\Projects\main\docs\theory\pso_optimization_complete.md`
   - Extract PSO symbols (w, c1, c2, pbest, gbest)

3. **Read**: `D:\Projects\main\config.yaml`
   - Extract physical parameters (m0, m1, m2, L1, L2, g)

4. **Read**: `D:\Projects\main\docs\thesis\chapters\04_sliding_mode_control.md`
   - Extract controller-specific symbols

---

## NOMENCLATURE STRUCTURE

### Organization by Category (5 categories)

**Category 1: State Variables** (~10 symbols)
- Cart and pendulum positions, velocities

**Category 2: Physical Parameters** (~15 symbols)
- Masses, lengths, friction, gravity

**Category 3: Control Variables** (~12 symbols)
- Control input, sliding surface, gains

**Category 4: SMC Parameters** (~15 symbols)
- Controller gains for 7 variants

**Category 5: PSO Parameters** (~10 symbols)
- Optimization settings

**Category 6: Mathematical Operators** (~8 symbols)
- Norms, sign, saturation

**Category 7: Abbreviations** (~15 terms)
- DIP, SMC, STA, PSO, etc.

---

## EXACT PROMPT TO USE

### Copy This Into Your AI Assistant:

```
Create a comprehensive Nomenclature (List of Symbols) for a Master's thesis on "Sliding Mode Control of Double-Inverted Pendulum with PSO Optimization."

Extract symbols from these source files:
- `docs/theory/smc_theory_complete.md` (SMC notation)
- `docs/theory/pso_optimization_complete.md` (PSO notation)
- `config.yaml` (physical parameters)

Organize into 7 categories:

### 1. STATE VARIABLES
Format: Symbol - Description [Units]

Example:
- $x$ - Cart position [m]
- $\dot{x}$ - Cart velocity [m/s]
- $\theta_1$ - First pendulum angle from vertical [rad]
- $\dot{\theta}_1$ - Angular velocity of first pendulum [rad/s]
- $\theta_2$ - Second pendulum angle [rad]
- $\dot{\theta}_2$ - Angular velocity of second pendulum [rad/s]
- $\vect{x}$ - State vector $\in \Real^6$

### 2. PHYSICAL PARAMETERS
- $m_0$ - Cart mass [kg]
- $m_1$ - First pendulum mass [kg]
- $m_2$ - Second pendulum mass [kg]
- $L_1$ - Length of first pendulum [m]
- $L_2$ - Length of second pendulum [m]
- $g$ - Gravitational acceleration [m/s²]
- $b$ - Cart friction coefficient [N·s/m]
- $b_1$ - Friction at first joint [N·m·s/rad]
- $b_2$ - Friction at second joint [N·m·s/rad]

### 3. CONTROL VARIABLES
- $u(t)$ - Control input (force applied to cart) [N]
- $s(\vect{x})$ - Sliding surface function
- $\lambda$ - Sliding surface slope parameter
- $K$ - Control gain
- $\epsilon$ - Boundary layer thickness
- $\phi$ - Boundary layer scaling factor
- $\alpha$ - Super-twisting gain (1st order)
- $\beta$ - Super-twisting gain (2nd order)

### 4. SMC CONTROLLER GAINS
For each controller variant, list gains:

**Classical SMC**:
- $K_1, K_2, K_3$ - Position/velocity gains
- $K_4, K_5, K_6$ - Angular gains

**STA-SMC**:
- $\alpha_1, \alpha_2$ - Super-twisting gains

**Adaptive SMC**:
- $\gamma$ - Adaptation rate
- $\hat{K}(t)$ - Estimated gain

**Hybrid SMC**:
- $K_{bl}$ - Boundary layer gain
- $K_{sta}$ - STA component gain

### 5. PSO OPTIMIZATION PARAMETERS
- $w$ - Inertia weight
- $c_1$ - Cognitive coefficient
- $c_2$ - Social coefficient
- $N_p$ - Number of particles
- $N_{iter}$ - Number of iterations
- $\vect{p}_{best}$ - Personal best position
- $\vect{g}_{best}$ - Global best position
- $\vect{v}_i$ - Velocity of particle $i$
- $J$ - Cost function (objective)

### 6. MATHEMATICAL OPERATORS
- $\| \cdot \|$ - Euclidean norm
- $\sign(\cdot)$ - Sign function
- $\sat(\cdot)$ - Saturation function
- $\Real^n$ - n-dimensional real space
- $\diff{}{t}$ - Time derivative
- $\pdiff{}{x}$ - Partial derivative
- $\langle \cdot, \cdot \rangle$ - Inner product

### 7. ABBREVIATIONS
- DIP - Double-Inverted Pendulum
- SMC - Sliding Mode Control
- STA - Super-Twisting Algorithm
- PSO - Particle Swarm Optimization
- LQR - Linear Quadratic Regulator
- MPC - Model Predictiive Control
- PID - Proportional-Integral-Derivative
- DOF - Degrees of Freedom
- RMS - Root Mean Square
- FFT - Fast Fourier Transform
- TOL - Tolerance
- ODE - Ordinary Differential Equation

Quality Requirements:
- Total symbols: 60+ entries
- All symbols from theory docs included
- Consistent notation throughout
- SI units specified for physical quantities
- LaTeX math mode for all symbols
- Alphabetical within each category

Output Format: LaTeX nomenclature environment
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Review for Completeness (30 min)

Cross-check against theory docs:
```bash
# Extract all math symbols from theory docs
grep -E "\$.*\$" docs/theory/smc_theory_complete.md | sort -u > symbols_found.txt

# Compare to nomenclature - anything missing?
```

Common missing symbols:
- Lyapunov function: $V(\vect{x})$
- Reaching time: $t_r$
- Settling time: $t_s$
- Error variables: $e_1, e_2$
- Reference signals: $x_{ref}, \theta_{ref}$

### 2. Format as LaTeX (20 min)

Save to: `D:\Projects\main\thesis\front\nomenclature.tex`

**Method 1: Using `nomencl` Package** (Automatic)
```latex
\chapter*{Nomenclature}
\addcontentsline{toc}{chapter}{Nomenclature}

\printnomenclature
```

Then throughout thesis, use:
```latex
\nomenclature{$x$}{Cart position [m]}
\nomenclature{$m_0$}{Cart mass [kg]}
```

**Method 2: Manual List** (More control)
```latex
\chapter*{Nomenclature}
\addcontentsline{toc}{chapter}{Nomenclature}

\section*{State Variables}
\begin{tabular}{@{} p{3cm} p{11cm} @{}}
$x$ & Cart position [m] \\
$\dot{x}$ & Cart velocity [m/s] \\
$\theta_1$ & First pendulum angle from vertical [rad] \\
$\dot{\theta}_1$ & Angular velocity of first pendulum [rad/s] \\
... \\
\end{tabular}

\section*{Physical Parameters}
\begin{tabular}{@{} p{3cm} p{11cm} @{}}
$m_0$ & Cart mass [kg] \\
$m_1$ & First pendulum mass [kg] \\
... \\
\end{tabular}

[... Continue for all 7 categories ...]
```

### 3. Verify Consistency (20 min)

Check that ALL symbols used in thesis are defined:
- [ ] Chapter 3 (Modeling): All dynamics symbols listed
- [ ] Chapter 5 (SMC): All controller symbols listed
- [ ] Chapter 7 (PSO): All optimization symbols listed
- [ ] All equations use notation from nomenclature

### 4. Test Compile (10 min)

```bash
cd thesis
pdflatex main.tex
```

Verify:
- [ ] Nomenclature appears after TOC
- [ ] 4-5 pages length
- [ ] All categories present
- [ ] Symbols render correctly
- [ ] Units shown for physical quantities

---

## VALIDATION CHECKLIST

### Content Quality
- [ ] 60+ symbols listed
- [ ] All 7 categories present
- [ ] Alphabetical within categories
- [ ] Units specified for dimensional quantities
- [ ] No undefined symbols used later in thesis

### Notation Consistency
- [ ] Vectors bold: $\vect{x}$ not $\vec{x}$
- [ ] Matrices bold uppercase: $\mat{M}$ not $M$
- [ ] Scalars italic: $x$ not $\text{x}$
- [ ] Operators upright: $\sin$ not $sin$

### LaTeX Formatting
- [ ] All math in $...$ or \begin{equation}
- [ ] Special characters escaped: \%, \&, \_
- [ ] Units not italicized: [m] not [$m$]
- [ ] Tables aligned properly

---

## AUTOMATION OPTION

Use this Python script to extract symbols automatically:

```python
#!/usr/bin/env python
"""Extract mathematical symbols from markdown files"""

import re
import sys

def extract_symbols(filepath):
    """Extract LaTeX math symbols from markdown"""
    symbols = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all inline math: $...$
    inline_math = re.findall(r'\$([^\$]+)\$', content)

    # Find all display math: $$...$$
    display_math = re.findall(r'\$\$([^\$]+)\$\$', content)

    all_math = inline_math + display_math

    # Extract symbol patterns (simplified)
    for math in all_math:
        # Greek letters
        greek = re.findall(r'\\(alpha|beta|gamma|theta|lambda|epsilon|phi|psi|omega)', math)
        symbols.update(greek)

        # Single letter variables
        vars = re.findall(r'\b([a-zA-Z])\b', math)
        symbols.update(vars)

    return sorted(symbols)

if __name__ == '__main__':
    files = [
        'docs/theory/smc_theory_complete.md',
        'docs/theory/pso_optimization_complete.md',
        'docs/thesis/chapters/04_sliding_mode_control.md'
    ]

    all_symbols = set()
    for f in files:
        all_symbols.update(extract_symbols(f))

    print(f"Found {len(all_symbols)} unique symbols:")
    for sym in sorted(all_symbols):
        print(f"  {sym}")
```

Run:
```bash
python extract_symbols.py > symbols_list.txt
```

Then manually add descriptions and units.

---

## EXAMPLE OUTPUT SAMPLE

```latex
\chapter*{Nomenclature}
\addcontentsline{toc}{chapter}{Nomenclature}

\section*{State Variables}
\begin{tabular}{@{} p{3cm} p{11cm} @{}}
$x$ & Cart position [m] \\
$\dot{x}$ & Cart velocity [m/s] \\
$\theta_1$ & First pendulum angle from vertical [rad] \\
$\dot{\theta}_1$ & Angular velocity of first pendulum [rad/s] \\
$\theta_2$ & Second pendulum angle from vertical [rad] \\
$\dot{\theta}_2$ & Angular velocity of second pendulum [rad/s] \\
$\vect{x}$ & State vector $[\x, \dot{x}, \theta_1, \dot{\theta}_1, \theta_2, \dot{\theta}_2]^T \in \Real^6$ \\
\end{tabular}

\section*{Physical Parameters}
\begin{tabular}{@{} p{3cm} p{11cm} @{}}
$m_0$ & Cart mass (1.0 kg) \\
$m_1$ & First pendulum mass (0.1 kg) \\
$m_2$ & Second pendulum mass (0.1 kg) \\
$L_1$ & Length of first pendulum (0.5 m) \\
$L_2$ & Length of second pendulum (0.5 m) \\
$g$ & Gravitational acceleration (9.81 m/s²) \\
$b$ & Cart friction coefficient (0.1 N·s/m) \\
$b_1$ & Friction at first joint (0.01 N·m·s/rad) \\
$b_2$ & Friction at second joint (0.01 N·m·s/rad) \\
\end{tabular}

[... Continue for all categories ...]
```

---

## TIME CHECK

- Read source files: 30 min
- Run AI prompt: 10 min
- Review output: 30 min
- Format LaTeX: 20 min
- Verify consistency: 20 min
- Test compile: 10 min
- **Total**: ~2 hours

---

## NEXT STEP

Once Nomenclature is complete:

**Proceed to**: `step_04_table_of_contents.md`

This will configure auto-generated table of contents, list of figures, list of tables.

---

**[OK] Ready to list all symbols? Extract from theory docs and compile!**
