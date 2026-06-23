# Step 7: Compile and Verify Chapter 13

**Time**: 30 minutes
**Output**: Complete Chapter 13 PDF (14-16 pages)

---

## OBJECTIVE

Compile Chapter 13 - Robustness Analysis, verify all components, fix compilation errors, and validate formatting.

---

## COMPILATION CHECKLIST

### 1. Pre-Compilation Checks (5 min)

Verify all sections complete:
```bash
cd D:\Projects\main\thesis

# Check all section files exist
ls -1 chapters/chapter13_robustness.tex
ls -1 figures/chapter13/*.pdf | wc -l  # Should be ≥6 figures

# Check bibliography entries
grep -c "cite{" chapters/chapter13_robustness.tex
```

Expected structure:
```latex
% chapter13_robustness.tex
\chapter{Robustness Analysis}
\label{ch:robustness}

\section{Introduction}
\label{sec:robustness:intro}
[2 pages]

\section{Lyapunov Stability Proofs}
\label{sec:robustness:stability}
[5 pages]

\section{Uncertainty Bounds Analysis}
\label{sec:robustness:bounds}
[3 pages]

\section{Monte Carlo Validation}
\label{sec:robustness:monte_carlo}
[4 pages]

\section{Sensitivity Analysis}
\label{sec:robustness:sensitivity}
[3 pages]
```

### 2. Initial Compilation (5 min)

```bash
cd thesis
pdflatex -interaction=nonstopmode main.tex 2>&1 | tee compile_log.txt
```

**Expected warnings** (okay for now):
- Citation 'XYZ' undefined (will fix in Day 27)
- Label 'fig:...' multiply defined (check for duplicates)

**Fatal errors to fix immediately**:
- Undefined control sequence
- Missing $ inserted
- File not found

### 3. Fix Common Errors (10 min)

#### Error: "Undefined control sequence \vect"

**Fix**: Add to preamble (main.tex):
```latex
\newcommand{\vect}[1]{\mathbf{#1}}
\newcommand{\Real}{\mathbb{R}}
```

#### Error: "File 'fig13_1_success_rates.pdf' not found"

**Fix**: Check figure paths:
```bash
# Verify figures exist
ls -la figures/chapter13/

# Fix path in .tex file
\includegraphics[width=0.8\textwidth]{figures/chapter13/fig13_1_success_rates.pdf}
```

#### Error: "Environment 'theorem' undefined"

**Fix**: Add to preamble:
```latex
\usepackage{amsthm}
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
```

#### Error: "! Missing $ inserted" in equations

**Fix**: Ensure all math in $ ... $ or \begin{equation}:
```latex
% WRONG
The gain k > 5.0 ensures stability.

% CORRECT
The gain $k > 5.0$ ensures stability.
```

### 4. Verify Cross-References (5 min)

```bash
# Check for undefined references
grep "ref{" chapters/chapter13_robustness.tex | \
  while read line; do
    ref=$(echo $line | sed -n 's/.*ref{\([^}]*\)}.*/\1/p')
    grep -q "label{$ref}" chapters/*.tex || echo "MISSING: $ref"
  done
```

**Fix missing labels**:
```latex
% If references to Chapter 7 fail, add label there:
% In chapter07_classical_smc.tex
\chapter{Classical Sliding Mode Control}
\label{ch:classical_smc}  % <-- ADD THIS

\section{Controller Design}
\label{sec:classical_smc:design}  % <-- AND THIS
```

### 5. Verify Page Count (3 min)

```bash
pdflatex main.tex
pdfinfo main.pdf | grep Pages
```

**Expected**: Chapter 13 should be ~14-16 pages
- Section 13.1: 2 pages
- Section 13.2: 5 pages
- Section 13.3: 3 pages
- Section 13.4: 4 pages
- Section 13.5: 3 pages
- **Total**: 17 pages (nominal) ± 2 pages acceptable

**If too short** (<12 pages):
- Add more explanation to proofs (Section 13.2)
- Expand discussion in Monte Carlo (Section 13.4)

**If too long** (>18 pages):
- Condense methodology (Section 13.4)
- Move detailed derivations to appendix

### 6. Verify Figures and Tables (2 min)

Check all visuals render:
```bash
# Open PDF and visually inspect
# On Windows
start main.pdf

# Verify figure quality
pdfimages -list main.pdf | grep chapter13
```

**Quality checks**:
- [ ] All 6 figures visible
- [ ] Figures high resolution (not pixelated)
- [ ] All tables formatted with booktabs
- [ ] Table columns aligned
- [ ] Captions descriptive (not "Results")

---

## POST-COMPILATION VALIDATION

### Content Validation

Open `main.pdf` and verify:

**Section 13.1 (Introduction)**:
- [ ] Purpose of robustness analysis clear
- [ ] Roadmap of 4 analysis types present
- [ ] Connection to previous chapters established

**Section 13.2 (Stability Proofs)**:
- [ ] All 6 theorems numbered (13.1-13.6)
- [ ] Proofs complete (not just stated)
- [ ] Lyapunov functions displayed
- [ ] Summary table present

**Section 13.3 (Uncertainty Bounds)**:
- [ ] Table 13.1 has numerical values (not TBD)
- [ ] Design example included
- [ ] Bounds match proofs from 13.2

**Section 13.4 (Monte Carlo)**:
- [ ] Table 13.2 with statistics (mean, std, CI)
- [ ] Figure 13.1 (success rates) clear
- [ ] Figure 13.2 (box plots) readable
- [ ] Figure 13.3 (heatmap) informative
- [ ] Statistical significance reported (p-values)

**Section 13.5 (Sensitivity)**:
- [ ] Figure 13.4 (mass) shows degradation curves
- [ ] Figure 13.5 (length) present
- [ ] Figure 13.6 (friction) demonstrates highest impact
- [ ] Table 13.3 (sensitivity ranking) filled
- [ ] Design recommendations actionable

### Cross-Reference Validation

Search PDF for:
- [ ] No "??" (undefined references)
- [ ] All "Section X.X" hyperlinks work
- [ ] All "Figure X.X" references exist
- [ ] All "Table X.X" references exist
- [ ] All "Theorem X.X" references exist
- [ ] All citations show [?] or number (will fix in Day 27)

### Formatting Validation

- [ ] Chapter starts on odd page (right side)
- [ ] Section numbers correct (13.1, 13.2, ...)
- [ ] Equations numbered (13.1), (13.2), ...
- [ ] Figures numbered sequentially (13.1, 13.2, ...)
- [ ] Tables numbered sequentially (13.1, 13.2, ...)
- [ ] Consistent font (no random bold/italic)
- [ ] Margins uniform (1 inch all sides)

---

## FIXING SPECIFIC ISSUES

### Issue: Figures too large (overflow page)

```latex
% Reduce width
\includegraphics[width=0.7\textwidth]{...}  % was 0.9

% Or force smaller
\includegraphics[height=3in]{...}
```

### Issue: Table doesn't fit

```latex
% Rotate landscape
\begin{sidewaystable}
\begin{tabular}{...}
...
\end{tabular}
\end{sidewaystable}

% Or reduce font size
{\small
\begin{tabular}{...}
...
\end{tabular}
}
```

### Issue: Equation numbering wrong

```latex
% Reset counter if needed (at chapter start)
\setcounter{equation}{0}

% Or use \tag for manual numbering
\begin{equation}
V = \frac{1}{2} s^T s \tag{13.1}
\end{equation}
```

### Issue: Proof environment not working

```latex
% Add to preamble
\usepackage{amsthm}
\theoremstyle{definition}
\newtheorem{proof}{Proof}

% Or use manual formatting
\noindent\textbf{Proof.} [proof text] \hfill $\square$
```

---

## FINAL VALIDATION SCRIPT

```bash
#!/bin/bash
# validate_chapter13.sh

echo "=== Chapter 13 Validation ==="

# 1. Check file exists
[ -f chapters/chapter13_robustness.tex ] && echo "[OK] Source file exists" || echo "[FAIL] Missing source"

# 2. Check figures
fig_count=$(ls figures/chapter13/*.pdf 2>/dev/null | wc -l)
[ $fig_count -ge 6 ] && echo "[OK] $fig_count figures found" || echo "[WARN] Only $fig_count figures (expected 6)"

# 3. Compile
pdflatex -interaction=batchmode main.tex > /dev/null
[ $? -eq 0 ] && echo "[OK] Compilation successful" || echo "[FAIL] Compilation errors"

# 4. Check page count
pages=$(pdfinfo main.pdf 2>/dev/null | grep "Pages:" | awk '{print $2}')
echo "[INFO] Total thesis pages: $pages"

# 5. Check for undefined references
undef=$(grep "Rerun to get cross-references right" main.log 2>/dev/null | wc -l)
[ $undef -eq 0 ] && echo "[OK] All references defined" || echo "[WARN] Undefined refs (rerun needed)"

# 6. Check for overfull hboxes (formatting issues)
hbox=$(grep "Overfull" main.log 2>/dev/null | wc -l)
echo "[INFO] Overfull hboxes: $hbox (should be <10)"

echo "=== Validation Complete ==="
```

Run with:
```bash
bash validate_chapter13.sh
```

---

## SUCCESS CRITERIA

Before moving to Day 24:

### Compilation
- [ ] `pdflatex main.tex` completes without fatal errors
- [ ] PDF file `main.pdf` generated
- [ ] No "Emergency stop" messages

### Content
- [ ] All 5 sections present (13.1-13.5)
- [ ] All 6 theorems/lemmas numbered
- [ ] All 6 figures visible
- [ ] All 3 tables formatted

### Formatting
- [ ] Page count: 14-18 pages
- [ ] Equations numbered correctly
- [ ] Cross-references resolve (no ??)
- [ ] Professional appearance

### Quality
- [ ] Mathematical proofs complete
- [ ] Statistical results reported
- [ ] Design implications stated
- [ ] Figures publication-quality

---

## NEXT STEP

Chapter 13 complete!

**Proceed to**: Day 24 - Chapter 14 (Future Work)
**File**: `.artifacts/thesis_guide/day_24_chapter14/step_01_brainstorm_extensions.md`

---

**[OK] Chapter 13 - Robustness Analysis complete and validated!**
