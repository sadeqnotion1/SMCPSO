# Step 3: Setup Automation Scripts

**Time**: 1 hour
**Difficulty**: Moderate (requires Python)
**Tools**: Python 3.9+, pip

---

## OBJECTIVE

Install and test 5 automation scripts that will save you ~50 hours over the next 29 days by automating:
1. Markdown → LaTeX conversion
2. CSV → LaTeX table generation
3. Figure generation from benchmark data
4. BibTeX citation extraction
5. Automated PDF compilation

---

## PREREQUISITES

### Check Python Installation

```bash
# Check Python version (must be 3.9+)
python --version
# Should output: Python 3.9.x or higher

# Check pip is installed
pip --version
```

**If Python not installed**:
- Windows: https://www.python.org/downloads/
- macOS: `brew install python3` (requires Homebrew)
- Linux: `sudo apt install python3 python3-pip`

### Install Required Packages

```bash
# Navigate to project root
cd D:\Projects\main  # Windows
# OR
cd ~/Projects/main  # macOS/Linux

# Install dependencies
pip install pandas matplotlib numpy pyyaml
```

**Verify installation**:
```bash
python -c "import pandas, matplotlib, numpy, yaml; print('[OK] All packages installed')"
```

---

## SCRIPT 1: MARKDOWN TO LATEX CONVERTER

### Purpose
Converts markdown documentation to LaTeX format, preserving:
- Headers → `\section{}`, `\subsection{}`
- Math: `$...$` → `$...$` (already compatible)
- Code blocks: ` ``` ` → `\begin{verbatim}`
- Citations: `[1]` → `\cite{ref1}`

### Copy Script

**File**: `D:\Projects\main\.artifacts\thesis_guide\automation_scripts\md_to_tex.py`

The script already exists in the automation_scripts directory created by previous agents. Verify it:

```bash
# Check script exists
ls D:\Projects\main\.artifacts\thesis_guide\automation_scripts\md_to_tex.py

# Test run (help message)
python D:\Projects\main\.artifacts\thesis_guide\automation_scripts\md_to_tex.py --help
```

**Expected Output**:
```
Usage: md_to_tex.py <input.md> <output.tex> [options]

Converts Markdown to LaTeX format for thesis chapters.

Options:
  --chapter-level <int>  Set chapter depth (1=chapter, 2=section)
  --preserve-comments    Keep markdown comments in output
  --help                 Show this help message
```

### Test Script

**Create test markdown** (`test_input.md`):
```markdown
# Introduction

The double-inverted pendulum (DIP) is a nonlinear system.

## Mathematical Model

The state vector is $\vect{x} = [x, \theta_1, \theta_2]^T$.

### Equation of Motion

The dynamics are governed by:
$$
M(\vect{q})\ddot{\vect{q}} + C(\vect{q}, \dot{\vect{q}}) + G(\vect{q}) = \vect{u}
$$
```

**Run conversion**:
```bash
python automation_scripts/md_to_tex.py test_input.md test_output.tex
```

**Expected Output** (`test_output.tex`):
```latex
\section{Introduction}

The double-inverted pendulum (DIP) is a nonlinear system.

\subsection{Mathematical Model}

The state vector is $\vect{x} = [x, \theta_1, \theta_2]^T$.

\subsubsection{Equation of Motion}

The dynamics are governed by:
\begin{equation}
M(\vect{q})\ddot{\vect{q}} + C(\vect{q}, \dot{\vect{q}}) + G(\vect{q}) = \vect{u}
\end{equation}
```

---

## SCRIPT 2: CSV TO LATEX TABLE GENERATOR

### Purpose
Converts CSV benchmark data to professional LaTeX tables with:
- Proper column alignment
- `booktabs` styling (no vertical lines)
- Caption and label
- Bold best values (optional)

### Test Script

The script exists at: `automation_scripts/csv_to_table.py`

**Create test CSV** (`test_data.csv`):
```csv
Controller,Settling Time (s),Overshoot (%),Energy (J)
Classical SMC,2.45,8.3,145.2
STA-SMC,2.12,5.1,132.8
Adaptive SMC,1.98,3.7,128.4
Hybrid SMC,1.85,2.9,121.6
```

**Run conversion**:
```bash
python automation_scripts/csv_to_table.py \
  test_data.csv \
  test_table.tex \
  "Performance Comparison" \
  "tab:performance"
```

**Expected Output** (`test_table.tex`):
```latex
\begin{table}[htbp]
\centering
\caption{Performance Comparison}
\label{tab:performance}
\begin{tabular}{lrrr}
\toprule
Controller & Settling Time (s) & Overshoot (\%) & Energy (J) \\
\midrule
Classical SMC & 2.45 & 8.3 & 145.2 \\
STA-SMC & 2.12 & 5.1 & 132.8 \\
Adaptive SMC & 1.98 & 3.7 & 128.4 \\
Hybrid SMC & \textbf{1.85} & \textbf{2.9} & \textbf{121.6} \\
\bottomrule
\end{tabular}
\end{table}
```

---

## SCRIPT 3: FIGURE GENERATOR

### Purpose
Generates all 60 thesis figures from benchmark data:
- Settling time comparisons
- PSO convergence plots
- Lyapunov function decay
- Chattering analysis (FFT)
- Robustness analysis

### Test Script

The script exists at: `automation_scripts/generate_figures.py`

**Run generation** (takes 2-3 minutes):
```bash
python automation_scripts/generate_figures.py --output-dir thesis/figures/
```

**Expected Output**:
```
[INFO] Generating benchmark figures...
[OK] Created: thesis/figures/benchmarks/settling_time_comparison.pdf
[OK] Created: thesis/figures/benchmarks/overshoot_comparison.pdf
[OK] Created: thesis/figures/benchmarks/energy_comparison.pdf
...
[OK] Generated 60 figures in 127.4 seconds
```

**Verify**:
```bash
# Count generated figures
ls thesis/figures/**/*.pdf | wc -l
# Should output: 60
```

---

## SCRIPT 4: BIBTEX CITATION EXTRACTOR

### Purpose
Converts academic citations from markdown to BibTeX format.

### Test Script

The script exists at: `automation_scripts/extract_bibtex.py`

**Run extraction**:
```bash
python automation_scripts/extract_bibtex.py \
  docs/CITATIONS_ACADEMIC.md \
  thesis/bibliography/papers.bib
```

**Expected Output** (`papers.bib`):
```bibtex
@article{Utkin1977,
  author = {Utkin, V. I.},
  title = {Variable structure systems with sliding modes},
  journal = {IEEE Transactions on Automatic Control},
  year = {1977},
  volume = {22},
  number = {2},
  pages = {212--222},
  doi = {10.1109/TAC.1977.1101446}
}

@book{Khalil2002,
  author = {Khalil, Hassan K.},
  title = {Nonlinear Systems},
  publisher = {Prentice Hall},
  year = {2002},
  edition = {3rd},
  isbn = {0130673897}
}

... (39 total entries)
```

**Verify**:
```bash
# Count BibTeX entries
grep -c "@article\|@book\|@inproceedings" thesis/bibliography/papers.bib
# Should output: 39
```

---

## SCRIPT 5: BUILD SCRIPT

### Purpose
Automates multi-pass LaTeX compilation:
1. `pdflatex` (1st pass - generates aux files)
2. `bibtex` (process citations)
3. `pdflatex` (2nd pass - resolve citations)
4. `pdflatex` (3rd pass - resolve cross-references)

### Create Build Script

**Windows** (`thesis/scripts/build.bat`):
```batch
@echo off
REM Automated Thesis Build Script

echo [INFO] Starting thesis compilation...

REM First pass
echo [STEP 1/4] Running pdflatex (1st pass)...
pdflatex -interaction=nonstopmode main.tex

REM BibTeX
echo [STEP 2/4] Running bibtex...
bibtex main

REM Second pass
echo [STEP 3/4] Running pdflatex (2nd pass)...
pdflatex -interaction=nonstopmode main.tex

REM Third pass
echo [STEP 4/4] Running pdflatex (3rd pass)...
pdflatex -interaction=nonstopmode main.tex

REM Cleanup
echo [INFO] Cleaning auxiliary files...
del main.aux main.log main.out main.toc main.lof main.lot main.bbl main.blg

echo [OK] Build complete! Output: main.pdf
pause
```

**macOS/Linux** (`thesis/scripts/build.sh`):
```bash
#!/bin/bash
# Automated Thesis Build Script

echo "[INFO] Starting thesis compilation..."

# First pass
echo "[STEP 1/4] Running pdflatex (1st pass)..."
pdflatex -interaction=nonstopmode main.tex

# BibTeX
echo "[STEP 2/4] Running bibtex..."
bibtex main

# Second pass
echo "[STEP 3/4] Running pdflatex (2nd pass)..."
pdflatex -interaction=nonstopmode main.tex

# Third pass
echo "[STEP 4/4] Running pdflatex (3rd pass)..."
pdflatex -interaction=nonstopmode main.tex

# Cleanup
echo "[INFO] Cleaning auxiliary files..."
rm -f main.aux main.log main.out main.toc main.lof main.lot main.bbl main.blg

echo "[OK] Build complete! Output: main.pdf"
```

**Make executable** (Linux/macOS):
```bash
chmod +x thesis/scripts/build.sh
```

### Test Build Script

```bash
# Windows
cd thesis
scripts\build.bat

# macOS/Linux
cd thesis
bash scripts/build.sh
```

**Expected Output**:
```
[INFO] Starting thesis compilation...
[STEP 1/4] Running pdflatex (1st pass)...
[STEP 2/4] Running bibtex...
[STEP 3/4] Running pdflatex (2nd pass)...
[STEP 4/4] Running pdflatex (3rd pass)...
[INFO] Cleaning auxiliary files...
[OK] Build complete! Output: main.pdf
```

---

## INTEGRATION TEST

### Test All Scripts Together

**Workflow**:
1. Convert markdown → LaTeX
2. Generate tables from CSV
3. Generate figures from data
4. Extract citations
5. Build complete PDF

**Commands**:
```bash
# 1. Convert Chapter 1
python automation_scripts/md_to_tex.py \
  docs/thesis/chapters/00_introduction.md \
  thesis/chapters/chapter01_introduction.tex

# 2. Generate benchmark table
python automation_scripts/csv_to_table.py \
  benchmarks/baseline_performance.csv \
  thesis/tables/benchmarks/baseline.tex \
  "Baseline Performance" \
  "tab:baseline"

# 3. Generate all figures
python automation_scripts/generate_figures.py --output-dir thesis/figures/

# 4. Extract citations
python automation_scripts/extract_bibtex.py \
  docs/CITATIONS_ACADEMIC.md \
  thesis/bibliography/papers.bib

# 5. Build PDF
cd thesis && bash scripts/build.sh
```

---

## VALIDATION CHECKLIST

Before proceeding to Step 4:

### Script Tests
- [ ] `md_to_tex.py --help` shows usage
- [ ] Converted test markdown → LaTeX successfully
- [ ] `csv_to_table.py` generated test table
- [ ] `generate_figures.py` created 60 figures
- [ ] `extract_bibtex.py` extracted 39 citations
- [ ] `build.sh` / `build.bat` compiled test PDF

### Output Quality
- [ ] Markdown conversion preserves equations
- [ ] Tables use `booktabs` style (professional)
- [ ] Figures are PDFs (vector graphics, scalable)
- [ ] BibTeX entries have all required fields
- [ ] Build script runs all 4 passes

### File Organization
- [ ] All scripts in `automation_scripts/` directory
- [ ] Build script in `thesis/scripts/`
- [ ] Test outputs in temporary folder (not thesis/)

---

## TROUBLESHOOTING

### Issue: "ModuleNotFoundError: No module named 'pandas'"

**Solution**:
```bash
pip install pandas matplotlib numpy pyyaml
# If using conda:
conda install pandas matplotlib numpy pyyaml
```

### Issue: "Permission denied" when running build.sh

**Solution** (Linux/macOS):
```bash
chmod +x thesis/scripts/build.sh
# OR run with bash explicitly:
bash thesis/scripts/build.sh
```

### Issue: generate_figures.py fails with "No data files found"

**Cause**: Script looking for benchmarks in wrong location

**Solution**:
```bash
# Run from project root, not thesis/ directory
cd D:\Projects\main
python automation_scripts/generate_figures.py --output-dir thesis/figures/
```

### Issue: BibTeX entries have incomplete information

**Cause**: Source markdown may be missing DOI, page numbers

**Solution**:
- Manually add missing fields to `papers.bib`
- Use Google Scholar to find complete citation info
- Days 27-28 will refine bibliography

---

## TIME CHECK

- Install Python packages: 5 min
- Test md_to_tex.py: 10 min
- Test csv_to_table.py: 10 min
- Test generate_figures.py: 5 min (script runs fast)
- Test extract_bibtex.py: 5 min
- Create build script: 10 min
- Integration test: 15 min
- **Total**: ~60 minutes

---

## NEXT STEP

Once all scripts are working:

**Proceed to**: `step_04_create_main_tex.md`

This will create the master LaTeX document (`main.tex`) that ties everything together.

---

**[OK] Scripts working? Test with sample data and move to Step 4!**
