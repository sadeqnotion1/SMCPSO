# DAY 1: LaTeX Setup + Automation Scripts

**Time**: 8 hours
**Output**: Working LaTeX build system + 5 automation scripts
**Difficulty**: Technical setup (moderate)

---

## OVERVIEW

Day 1 establishes the foundation for your entire thesis writing process. You'll create the LaTeX project structure, write essential templates, and build automation scripts that will save you ~50 hours over the next 29 days.

**Why This Matters**: Investing 8 hours today in setup and automation will make Days 2-30 significantly faster and smoother.

---

## OBJECTIVES

By end of Day 1, you will have:

1. [ ] Complete `thesis/` directory structure (chapters, figures, tables, etc.)
2. [ ] Working LaTeX templates (`main.tex`, `preamble.tex`, `metadata.tex`)
3. [ ] 5 automation scripts (md_to_tex, csv_to_table, generate_figures, extract_bibtex, build.sh)
4. [ ] Successful test PDF compilation

---

## TIME BREAKDOWN

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | Create directory structure | 30 min | `thesis/` folder tree |
| 2 | Write LaTeX templates | 1 hour | 3 template files |
| 3 | Write automation scripts | 4 hours | 5 Python/Bash scripts |
| 4 | Test build system | 30 min | test.pdf compiled |
| **TOTAL** | | **6 hours** | **Working build system** |

**Buffer**: 2 hours for troubleshooting, learning LaTeX basics

---

## STEPS

### Step 1: Create Directory Structure (30 min)
**File**: `step_01_create_directories.md`
- Create `thesis/` with 20+ subdirectories
- Understand folder organization
- Verify structure

### Step 2: Write LaTeX Templates (1 hour)
**File**: `step_02_latex_templates.md`
- Create `main.tex` (master document)
- Create `preamble.tex` (packages, formatting)
- Create `metadata.tex` (title, author, abstract)

### Step 3: Write Automation Scripts (4 hours)
**File**: `step_03_automation_scripts.md`
- Script 1: `md_to_tex.py` (90 min)
- Script 2: `csv_to_table.py` (60 min)
- Script 3: `generate_figures.py` (90 min)
- Script 4: `extract_bibtex.py` (30 min)
- Script 5: `build.sh` (30 min)

### Step 4: Test Build System (30 min)
**File**: `step_04_test_build.md`
- Compile test PDF
- Verify cross-references work
- Check bibliography compilation

---

## PREREQUISITES

### Required Software

**LaTeX Distribution** (choose one):
- Windows: MiKTeX (https://miktex.org/)
- macOS: MacTeX (https://www.tug.org/mactex/)
- Linux: TeX Live (`sudo apt install texlive-full`)
- **OR** Overleaf (online, no installation)

**Python 3.9+**:
- Download from https://www.python.org/
- Verify: `python --version`

**Python Packages**:
```bash
pip install pandas matplotlib numpy
```

**Text Editor** (choose one):
- VS Code + LaTeX Workshop extension (recommended)
- TeXstudio (beginner-friendly)
- Overleaf (online)

### Required Knowledge

- Basic command line (cd, mkdir, ls)
- Basic Python (reading scripts, not writing from scratch)
- No LaTeX experience needed (templates provided)

---

## SOURCE FILES

**No extraction needed on Day 1** - This is pure setup.

**Reference Materials**:
- LaTeX tutorial: https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes
- Python pandas docs: https://pandas.pydata.org/docs/
- Matplotlib docs: https://matplotlib.org/stable/tutorials/index.html

---

## EXPECTED OUTPUT

### Directory Structure Created

```
thesis/
├── main.tex
├── preamble.tex
├── metadata.tex
├── chapters/ (15 .tex files)
├── appendices/ (4 .tex files)
├── figures/ (5 subdirectories)
├── tables/ (3 subdirectories)
├── bibliography/ (4 .bib files)
├── front/ (3 .tex files)
├── scripts/ (5 scripts)
└── build/ (output directory)
```

### Templates Created

1. **main.tex** (~80 lines): Master document that includes all chapters
2. **preamble.tex** (~120 lines): Package imports, custom commands, formatting
3. **metadata.tex** (~30 lines): Title, author, abstract template

### Scripts Created

1. **md_to_tex.py** (~150 lines): Converts markdown → LaTeX
2. **csv_to_table.py** (~80 lines): Generates LaTeX tables from CSV
3. **generate_figures.py** (~200 lines): Creates 60 figures from data
4. **extract_bibtex.py** (~60 lines): Formats citations as BibTeX
5. **build.sh** (~40 lines): Automated PDF compilation

### Test Output

- **test.pdf**: 5-10 page test document
- No LaTeX errors or warnings
- Cross-references work (chapters, figures, citations)
- Bibliography compiles correctly

---

## VALIDATION CHECKLIST

Complete before moving to Day 2:

### Directory Structure
- [ ] `thesis/` folder exists in project root (`D:\Projects\main\thesis\`)
- [ ] All subdirectories created (chapters, figures, tables, bibliography, etc.)
- [ ] File permissions correct (can write to all directories)

### Templates
- [ ] `main.tex` exists and has \documentclass, \begin{document}, etc.
- [ ] `preamble.tex` has 10+ packages (amsmath, graphicx, hyperref, etc.)
- [ ] `metadata.tex` has title, author, date fields

### Scripts
- [ ] All 5 scripts exist in `thesis/scripts/`
- [ ] Python scripts have correct shebang (`#!/usr/bin/env python`)
- [ ] Scripts are executable (`chmod +x *.py` on Linux/Mac)
- [ ] Test run: `python thesis/scripts/md_to_tex.py --help` shows usage

### Build System
- [ ] Can run: `cd thesis && pdflatex main.tex`
- [ ] Generates `main.pdf` without errors
- [ ] Can run: `bash scripts/build.sh`
- [ ] Build script completes all 4 passes + bibtex

### Version Control
- [ ] Committed to git: `git add thesis/ && git commit -m "setup(thesis): Day 1 complete"`
- [ ] Pushed to remote: `git push`

---

## TROUBLESHOOTING

### LaTeX Installation Issues

**Windows - MiKTeX not found**:
```bash
# Add to PATH
setx PATH "%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64"
```

**Linux - Missing packages**:
```bash
sudo apt update
sudo apt install texlive-latex-extra texlive-science texlive-bibtex-extra
```

**macOS - Command not found**:
```bash
# Add to PATH in ~/.zshrc or ~/.bash_profile
export PATH="/Library/TeX/texbin:$PATH"
```

### Python Script Errors

**ModuleNotFoundError: No module named 'pandas'**:
```bash
pip install pandas matplotlib numpy
# If using conda:
conda install pandas matplotlib numpy
```

**Permission denied when running scripts**:
```bash
chmod +x thesis/scripts/*.py
# OR use python explicitly:
python thesis/scripts/md_to_tex.py
```

### Build Errors

**! LaTeX Error: File 'amsmath.sty' not found**:
- Cause: Incomplete LaTeX installation
- Fix: Install full distribution (texlive-full on Linux)

**! Undefined control sequence**:
- Cause: Custom command not defined in preamble
- Fix: Check `preamble.tex` has all \newcommand definitions

---

## NEXT STEPS

Once Day 1 checklist is complete:

1. Review what you built (30 min)
2. Test each script manually (30 min)
3. Read `day_02_front_matter/README.md` (10 min)
4. Get a good night's sleep!

**Tomorrow (Day 2)**: Write abstract, acknowledgments, and nomenclature (front matter)

---

## ESTIMATED COMPLETION TIME

- **Beginner** (first time with LaTeX): 8-10 hours
- **Intermediate** (some LaTeX experience): 6-8 hours
- **Advanced** (LaTeX expert): 4-6 hours

**Don't rush!** A solid foundation today makes Days 2-30 much easier.

---

**[OK] Ready to begin? Open `step_01_create_directories.md` and start!**
