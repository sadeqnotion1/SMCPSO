# Step 1: Create Directory Structure

**Time**: 30 minutes
**Difficulty**: Easy
**Tools**: Command line (terminal/PowerShell)

---

## OBJECTIVE

Create the complete `thesis/` folder structure that will house your 200-page thesis.

---

## COMMANDS TO RUN

### Windows (PowerShell)

```powershell
# Navigate to project root
cd D:\Projects\main

# Create main thesis directory
mkdir thesis

# Create all subdirectories
cd thesis
mkdir chapters, appendices, figures, tables, bibliography, front, scripts, build

# Create figure subdirectories
cd figures
mkdir architecture, benchmarks, convergence, lyapunov, schematics
cd..

# Create table subdirectories
cd tables
mkdir benchmarks, parameters, comparisons
cd ..

# Verify structure
tree /F
```

### Linux/macOS (Bash)

```bash
# Navigate to project root
cd ~/Projects/main  # or wherever your project is

# Create complete structure in one command
mkdir -p thesis/{chapters,appendices,front,scripts,build}
mkdir -p thesis/figures/{architecture,benchmarks,convergence,lyapunov,schematics}
mkdir -p thesis/tables/{benchmarks,parameters,comparisons}
mkdir -p thesis/bibliography

# Verify structure
tree thesis
# OR if tree not installed:
find thesis -type d
```

---

## FOLDER EXPLANATIONS

### Main Folders

**`thesis/`** - Root directory for all thesis-related files
- This is where `main.tex` will live
- All paths are relative to this directory

**`chapters/`** - Individual chapter files (15 files)
- `chapter01_introduction.tex`
- `chapter02_literature.tex`
- ... through ...
- `chapter15_conclusion.tex`

**`appendices/`** - Appendix files (4 files)
- `appendix_a_proofs.tex`
- `appendix_b_code.tex`
- `appendix_c_data.tex`
- `appendix_d_config.tex`

**`figures/`** - All figures (~60 PDF/PNG files)
- Subdirectories organize by type
- LaTeX will reference as: `\includegraphics{figures/benchmarks/settling_time.pdf}`

**`tables/`** - Auto-generated LaTeX tables (~30 files)
- Generated from CSV data via scripts
- Included in chapters with `\input{tables/benchmarks/baseline.tex}`

**`bibliography/`** - BibTeX files (100+ references)
- `main.bib` - Master file that imports others
- `books.bib` - Book references
- `papers.bib` - Journal/conference papers
- `software.bib` - Software citations

**`front/`** - Front matter (before main content)
- `abstract.tex`
- `acknowledgments.tex`
- `nomenclature.tex`

**`scripts/`** - Automation scripts (5 files)
- Created in Step 3
- Python and Bash scripts for automation

**`build/`** - LaTeX compilation output
- `main.pdf` - Your final thesis!
- `*.aux`, `*.log`, `*.toc`, etc. (temporary files)
- Can delete and rebuild anytime

### Figure Subdirectories

**`architecture/`** - System architecture diagrams (8 figures)
- Control loop, software modules, factory pattern, etc.

**`benchmarks/`** - Performance comparison plots (20 figures)
- Settling time, overshoot, energy, chattering, etc.

**`convergence/`** - PSO and Lyapunov convergence (12 figures)
- PSO swarm evolution, Lyapunov V(t) decay, etc.

**`lyapunov/`** - Stability analysis plots (8 figures)
- Sliding variable s(t), phase portraits, etc.

**`schematics/`** - Physical system diagrams (8 figures)
- DIP schematic, free body diagrams, etc.

### Table Subdirectories

**`benchmarks/`** - Performance comparison tables (15 tables)
- Statistical results, controller rankings, etc.

**`parameters/`** - System and controller parameters (10 tables)
- Physical params, controller gains, PSO settings, etc.

**`comparisons/`** - Literature comparison tables (5 tables)
- This work vs. prior art

---

## VERIFICATION STEPS

### 1. Count Directories

**Expected**: 13 directories total (including `thesis/` root)

```bash
# Windows PowerShell
(Get-ChildItem -Directory -Recurse thesis | Measure-Object).Count

# Linux/macOS
find thesis -type d | wc -l
```

Should output: **13**

### 2. Visual Inspection

Your structure should look like:

```
thesis/
├── appendices/
├── bibliography/
├── build/
├── chapters/
├── figures/
│   ├── architecture/
│   ├── benchmarks/
│   ├── convergence/
│   ├── lyapunov/
│   └── schematics/
├── front/
├── scripts/
└── tables/
    ├── benchmarks/
    ├── comparisons/
    └── parameters/
```

### 3. Write Permissions Test

```bash
# Create test file
echo "test" > thesis/test.txt

# If successful, you have write permissions
# Clean up
rm thesis/test.txt
```

---

## COMMON ISSUES

**Issue**: `mkdir: cannot create directory 'thesis': File exists`
- Cause: Directory already exists
- Fix: Either delete it (`rm -rf thesis`) or skip this step if intentional

**Issue**: `Permission denied`
- Cause: Insufficient permissions in current directory
- Fix: Use `sudo` (Linux/Mac) or run terminal as Administrator (Windows)

**Issue**: `tree command not found`
- Not a problem: Use `ls -R thesis` instead
- OR install: `sudo apt install tree` (Linux), `brew install tree` (Mac)

---

## NEXT STEP

Once directories are created and verified:
- [ ] All 13 directories exist
- [ ] Structure matches diagram above
- [ ] Write permissions confirmed

**Proceed to**: `step_02_latex_templates.md`

---

**Time Check**: This should take ~30 minutes including reading this file.

If it took less time, great! If more, no worries - thoroughness is more important than speed.
