# Day 8 Step 1: Extract Existing SMC Content

**Time**: 2 hours
**Output**: ~16 pages LaTeX base (from 468 lines markdown)
**Source**: `docs/thesis/chapters/04_sliding_mode_control.md`

---

## OBJECTIVE

Extract and convert the existing 468-line SMC theory chapter to LaTeX. This is ~70-75% of Chapter 5 already written! This step automates the bulk of the work.

---

## SOURCE FILE TO READ

**Primary Source** (468 lines - EXCELLENT!):
- **File**: `D:\Projects\main\docs\thesis\chapters\04_sliding_mode_control.md`
- **Content breakdown**:
  - Lines 1-100: SMC fundamentals (reaching, sliding, equivalent control)
  - Lines 101-200: Classical SMC (control law, chattering, boundary layer)
  - Lines 201-300: Super-Twisting Algorithm (STA formulation, finite-time convergence)
  - Lines 301-400: Adaptive SMC (gain adaptation, Lyapunov analysis)
  - Lines 401-468: Hybrid Adaptive STA-SMC (mode switching, combined benefits)

**What This Gives You**:
- Complete controller descriptions
- Mathematical formulations
- Control law equations
- Algorithm descriptions
- Advantages/disadvantages analysis

---

## EXACT COMMANDS TO USE

### Step 1: Read the Source File (30 min)

```bash
cd D:\Projects\main
cat docs\thesis\chapters\04_sliding_mode_control.md
```

Or open in VS Code:
```bash
code docs\thesis\chapters\04_sliding_mode_control.md
```

**What to look for**:
- Section structure (how is it organized?)
- Equations (which need special LaTeX formatting?)
- References (any citations to add?)
- Algorithm boxes (need to recreate in LaTeX)

### Step 2: Run Automated Conversion (5 min)

```bash
cd D:\Projects\main
python thesis\scripts\md_to_tex.py ^
  docs\thesis\chapters\04_sliding_mode_control.md ^
  thesis\chapters\chapter05_smc_theory.tex
```

**Expected output**:
```
[INFO] Reading markdown: docs\thesis\chapters\04_sliding_mode_control.md
[INFO] Found 468 lines
[INFO] Converting equations to LaTeX format
[INFO] Converting headers to \section{} commands
[INFO] Writing to: thesis\chapters\chapter05_smc_theory.tex
[OK] Conversion complete: ~16 pages LaTeX generated
```

### Step 3: Review Converted Output (1 hour)

Open the generated file:
```bash
code thesis\chapters\chapter05_smc_theory.tex
```

**Check these items**:

1. **Chapter header correct**:
```latex
\chapter{Sliding Mode Control Theory}
\label{chap:smc_theory}
```

2. **Section structure preserved**:
```latex
\section{SMC Fundamentals}
\label{sec:smc:fundamentals}

\section{Classical SMC}
\label{sec:smc:classical}

\section{Super-Twisting Algorithm}
\label{sec:smc:sta}

\section{Adaptive SMC}
\label{sec:smc:adaptive}

\section{Hybrid Adaptive STA-SMC}
\label{sec:smc:hybrid}
```

3. **Equations formatted correctly**:

Check that markdown equations like:
```markdown
s(x) = lambda_1 * e_1 + lambda_2 * e_2
```

Became LaTeX equations:
```latex
\begin{equation}
s(x) = \lambda_1 e_1 + \lambda_2 e_2
\label{eq:sliding_surface}
\end{equation}
```

4. **Inline math correct**:

Markdown `$theta_1$` → LaTeX `$\theta_1$`

5. **Algorithm boxes need manual creation**:

The script can't convert algorithm descriptions to LaTeX `algorithm` environment. You'll need to create these manually in later steps.

### Step 4: Identify What Needs Expansion (30 min)

Create a list: `chapter05_expansion_needed.txt`

**Typical gaps**:
- [ ] Section 5.1: Add Utkin citations (1977, 1992)
- [ ] Section 5.2: Create Algorithm Box 5.1 (Classical SMC)
- [ ] Section 5.3: Expand finite-time convergence proof
- [ ] Section 5.4: Create Algorithm Box 5.2 (Adaptive SMC)
- [ ] Section 5.5: Add computational complexity analysis
- [ ] Overall: Add 5-10 more citations
- [ ] Overall: Add transition paragraphs between sections

---

## WHAT TO DO WITH THE OUTPUT

### 1. Test Compile (10 min)

```bash
cd D:\Projects\main\thesis
pdflatex main.tex
```

**Expected issues**:
- Missing \chapter{} command → Add at top of file
- Undefined citations → Expected (will fix in Day 27)
- Some equations malformatted → Mark for manual fix

### 2. Verify Page Count (5 min)

```bash
pdflatex main.tex
# Check page numbers in PDF viewer
```

**Expected**: ~14-18 pages

468 lines of markdown typically converts to ~16 pages LaTeX with double-spacing and equations.

If too short (<12 pages):
- Missing content in conversion
- Check equations rendered correctly
- May need to expand later

If too long (>20 pages):
- Excellent! May not need much expansion
- Can condense slightly if needed

### 3. Create Expansion Task List (10 min)

Based on review, create file: `day8_expansion_tasks.txt`

Example:
```
Priority 1 (Must Add):
- [ ] Algorithm Box 5.1: Classical SMC pseudocode
- [ ] Algorithm Box 5.2: STA-SMC pseudocode
- [ ] Algorithm Box 5.3: Adaptive SMC pseudocode
- [ ] Citations: Utkin 1977, Levant 1993, Edwards & Spurgeon 1998

Priority 2 (Should Add):
- [ ] Section 5.6: Stability overview (preview Chapter 13)
- [ ] Transition paragraphs between sections
- [ ] Example numerical values for gains

Priority 3 (Nice to Have):
- [ ] Comparison table: Classical vs STA vs Adaptive
- [ ] Computational complexity analysis
- [ ] Historical development timeline
```

---

## VALIDATION CHECKLIST

### Conversion Success
- [ ] chapter05_smc_theory.tex file created
- [ ] File size reasonable (>10 KB)
- [ ] Contains LaTeX commands (\section{}, \begin{equation}, etc.)
- [ ] No raw markdown formatting remaining (no ##, **, etc.)

### Content Completeness
- [ ] All 5 controller variants present
- [ ] Equations converted to LaTeX format
- [ ] Section structure preserved
- [ ] No large blocks of text missing

### Compilation
- [ ] pdflatex runs without fatal errors
- [ ] Chapter appears in PDF
- [ ] Page count ~14-18 pages
- [ ] Equations render correctly (not blank boxes)

### Quality
- [ ] Math notation correct (θ₁ not theta1)
- [ ] Vectors bold (\vect{x})
- [ ] No conversion artifacts ("backslash n", "dollar sign")
- [ ] Readable in PDF viewer

---

## TROUBLESHOOTING

### Conversion Script Fails

**Error**: `FileNotFoundError: md_to_tex.py not found`

**Solution**:
```bash
# Verify script exists
ls thesis\scripts\md_to_tex.py

# If missing, check Day 1 completion
# You may need to create the script first
```

### Output File Empty or Malformed

**Error**: chapter05_smc_theory.tex has 0 bytes or looks wrong

**Solution**:
- Check input file exists and has content
- Try manual conversion (copy-paste markdown, convert equations by hand)
- Use online markdown → LaTeX converters (Pandoc)

### Equations Not Converting

**Problem**: Equations still look like `s(x) = lambda * e` instead of LaTeX

**Solution**:
- Manual fix: Replace `lambda` with `\lambda`
- Wrap in equation environment:
```latex
\begin{equation}
s(x) = \lambda e
\label{eq:sliding_surface}
\end{equation}
```

### Page Count Too Low (<10 pages)

**Problem**: 468 lines should give ~16 pages, but only 10

**Causes**:
- Equations not rendered (showing as blank)
- Some sections missing in conversion
- Heavy use of bullet lists (compress in LaTeX)

**Solution**:
- Compare source markdown with LaTeX output
- Manually add missing sections
- Ensure all equations have \begin{equation}...\end{equation}

---

## AUTOMATION ADVANTAGES

### Why This Step Saves Massive Time

**Manual approach** (no automation):
- Copy-paste 468 lines manually: 1 hour
- Convert each equation to LaTeX: 3-4 hours
- Format sections, labels, references: 2 hours
- **Total**: 6-7 hours

**Automated approach** (with script):
- Run script: 5 minutes
- Review output: 1 hour
- Fix issues: 1 hour
- **Total**: 2 hours

**Time saved**: ~4-5 hours!

---

## EXPECTED OUTPUT SAMPLE

Here's what Section 5.1 might look like after conversion:

```latex
\section{Sliding Mode Control Fundamentals}
\label{sec:smc:fundamentals}

Sliding mode control (SMC) is a robust nonlinear control technique introduced by Utkin in the 1970s. The fundamental concept involves designing a sliding surface in the state space such that system trajectories are forced to reach and remain on this surface.

Consider a nonlinear system:
\begin{equation}
\dot{x} = f(x) + g(x)u
\label{eq:nonlinear_system}
\end{equation}
where $x \in \mathbb{R}^n$ is the state vector, $u \in \mathbb{R}$ is the control input, and $f(x)$, $g(x)$ are nonlinear functions.

The sliding surface is defined as:
\begin{equation}
s(x) = \lambda_1 e_1 + \lambda_2 e_2 + \cdots + \lambda_n e_n = 0
\label{eq:sliding_surface}
\end{equation}
where $e_i$ are state errors and $\lambda_i$ are design parameters.

...
```

---

## NEXT STEP

Once extraction is complete and validated:
**Proceed to**: `day8_step_02_section_5_1_fundamentals.md`

This will expand Section 5.1 with additional context and citations (2 hours)

---

**[OK] Best extraction step! 468 lines → 16 pages in 2 hours. Run the conversion!**
