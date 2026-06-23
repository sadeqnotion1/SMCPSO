# DAY 28: Full Build and First Review

**Time**: 8 hours
**Output**: Complete thesis PDF (first draft) + error log
**Difficulty**: Moderate (debugging focus)

---

## OVERVIEW

Day 28 is the first time you compile the ENTIRE thesis from start to finish. This is a critical quality gate: find and fix all LaTeX errors, missing references, broken citations, and formatting issues before the polish phase.

**Why This Matters**: You can't polish (Day 29) until the PDF builds cleanly. This day is about making the thesis "compilable and complete."

---

## OBJECTIVES

By end of Day 28, you will have:

1. [ ] Complete thesis PDF compiles without errors
2. [ ] All cross-references resolved (no "??" markers)
3. [ ] All citations resolved (no "Citation undefined")
4. [ ] All figures and tables included and referenced
5. [ ] Page count verified (180-220 pages target)
6. [ ] Error log documenting all fixes
7. [ ] First complete read-through notes

---

## TIME BREAKDOWN

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | First build attempt | 1 hour | Error list |
| 2 | Fix LaTeX compilation errors | 2 hours | Clean build |
| 3 | Fix cross-reference warnings | 1 hour | No "??" |
| 4 | Fix citation warnings | 1 hour | All cites resolved |
| 5 | Verify figures/tables | 1 hour | All included |
| 6 | First complete read-through | 2 hours | Notes for Day 29 |
| **TOTAL** | | **8 hours** | **Working thesis PDF** |

---

## STEPS

### Step 1: First Build Attempt (1 hour)
**File**: `step_01_first_build.md`
- Run full 4-pass build: `bash scripts/build.sh`
- Collect all errors and warnings
- Create error log: `build_errors_day28.txt`
- Categorize issues: fatal errors, warnings, minor issues

### Step 2: Fix LaTeX Compilation Errors (2 hours)
**File**: `step_02_fix_compilation.md`
- Fix syntax errors (missing }, unmatched delimiters)
- Fix package conflicts
- Fix overfull/underfull boxes
- Achieve clean pdflatex run (no fatal errors)

### Step 3: Fix Cross-Reference Warnings (1 hour)
**File**: `step_03_fix_references.md`
- Search PDF for "??" markers
- Fix undefined labels (\label{...} missing)
- Verify all \ref{}, \cref{}, \eqref{} resolve
- Run build twice (references need multiple passes)

### Step 4: Fix Citation Warnings (1 hour)
**File**: `step_04_fix_citations.md`
- Check for "Citation undefined" warnings
- Verify all \cite{} keys exist in .bib files
- Fix duplicate BibTeX entries
- Ensure bibtex ran successfully

### Step 5: Verify Figures and Tables (1 hour)
**File**: `step_05_verify_visuals.md`
- Check all 60 figures appear in PDF
- Check all 30 tables appear in PDF
- Verify captions and labels correct
- Check List of Figures and List of Tables complete

### Step 6: First Complete Read-Through (2 hours)
**File**: `step_06_first_review.md`
- Read thesis cover-to-cover (skim, don't deep edit)
- Note major issues: missing sections, wrong figures, inconsistencies
- Create priority fix list for Day 29
- Verify page count in target range

---

## SOURCE FILES

### Build System (from Day 1)
- `thesis/scripts/build.sh`
- Main file: `thesis/main.tex`
- Preamble: `thesis/preamble.tex`

### All Chapter Files
- `thesis/chapters/chapter01_introduction.tex` through `chapter15_conclusion.tex`
- `thesis/appendices/appendix_a_proofs.tex` through `appendix_d_config.tex`
- `thesis/front/*.tex` (abstract, acknowledgments, etc.)

### Bibliography Files
- `thesis/bibliography/papers.bib`
- `thesis/bibliography/books.bib`
- `thesis/bibliography/software.bib`

---

## EXPECTED OUTPUT

### Successful Build Log

```
[INFO] Running 4-pass LaTeX build...
[PASS 1] pdflatex main.tex - Building structure
[PASS 2] bibtex main - Processing bibliography
[PASS 3] pdflatex main.tex - Resolving references
[PASS 4] pdflatex main.tex - Final compilation
[OK] Build complete: thesis/build/main.pdf
[OK] Page count: 198 pages
[OK] No errors, 3 warnings (acceptable)
[OK] All cross-references resolved
[OK] All citations resolved
```

### Error Log (initial state)

Example `build_errors_day28.txt`:
```
[ERROR] Undefined control sequence \vect on line 234 of chapter05_smc_theory.tex
[WARNING] Citation 'Utkin1992' undefined in chapter02_literature.tex
[WARNING] Reference 'fig:dip_schematic' undefined on page 45
[WARNING] Overfull \hbox (5.2pt too wide) in paragraph at line 89
[INFO] 15 total issues to fix
```

### Fixed Build (end state)

```
[OK] All errors resolved
[OK] 0 fatal errors, 0 reference warnings, 0 citation warnings
[OK] Minor warnings: 2 overfull boxes (acceptable)
[OK] PDF compiles cleanly
```

### Read-Through Notes

Example notes for Day 29:
```
Priority Fixes:
1. Chapter 3 Section 3.2: Figure 3.1 mentioned but not included
2. Chapter 10: Table 10.3 has misaligned columns
3. Chapter 13: Proof 13.2 has typo ("therfore" → "therefore")
4. Appendix B: Code listing line 45 cut off at page break

Style Issues:
1. Inconsistent notation: θ₁ vs. theta1 in Chapter 5
2. AI pattern detected in Chapter 14 ("Let's explore...")
3. Some figure captions too short (need more context)

Page Count:
- Current: 198 pages (target: 200 ± 10% → 180-220 OK!)
- Front matter: 18 pages
- Main content: 142 pages
- Appendices: 38 pages
```

---

## VALIDATION CHECKLIST

### Build Success
- [ ] `pdflatex main.tex` exits with code 0 (no fatal errors)
- [ ] `bibtex main` runs successfully
- [ ] PDF file created: `thesis/build/main.pdf`
- [ ] PDF opens in viewer without corruption

### Cross-References
- [ ] Search PDF for "??" → 0 results
- [ ] All chapter numbers correct (1 through 15)
- [ ] All figure numbers sequential (10.1, 10.2, ...)
- [ ] All table numbers sequential
- [ ] All equation numbers sequential

### Citations
- [ ] Search PDF for "Citation undefined" → 0 results
- [ ] All [1], [2], ... in text link to bibliography
- [ ] Bibliography section present (8-10 pages)
- [ ] 100+ references listed

### Figures and Tables
- [ ] All 60 figures visible in PDF
- [ ] All figures referenced in text (no orphaned figures)
- [ ] All 30 tables visible in PDF
- [ ] All tables referenced in text
- [ ] List of Figures complete (60 entries)
- [ ] List of Tables complete (30 entries)

### Page Count
- [ ] Total pages: 180-220 (target range)
- [ ] Front matter: 15-20 pages (Roman numerals)
- [ ] Main content: 130-160 pages (Arabic numerals)
- [ ] Appendices: 30-50 pages
- [ ] Bibliography: 8-12 pages

### Structure
- [ ] Title page present
- [ ] Abstract present
- [ ] Table of Contents correct (all chapters listed)
- [ ] All 15 chapters present
- [ ] All 4 appendices present
- [ ] Bibliography present

---

## TROUBLESHOOTING

### Fatal Error: ! Undefined control sequence

**Example**: `! Undefined control sequence \vect`

**Cause**: Custom command not defined

**Solution**:
```latex
% Add to preamble.tex
\newcommand{\vect}[1]{\mathbf{#1}}
```

### Warning: Reference `fig:something' undefined

**Cause**: Label doesn't exist or typo in \label{} vs. \ref{}

**Solution**:
1. Search for `\label{fig:something}` in all .tex files
2. If missing, add to figure: `\caption{...}\label{fig:something}`
3. If typo, fix \ref{fig:somethng} → \ref{fig:something}

### Warning: Citation `Utkin1992' undefined

**Cause**: BibTeX entry missing or key mismatch

**Solution**:
1. Search `papers.bib` for `@article{Utkin1992,`
2. If missing, add entry from CITATIONS_ACADEMIC.md
3. If key wrong, fix: `\cite{Utkin1992}` → `\cite{Utkin1977}`

### Error: File `figure10_1.pdf' not found

**Cause**: Figure file doesn't exist or wrong path

**Solution**:
1. Check file exists: `ls thesis/figures/chapter10/figure10_1.pdf`
2. If missing, regenerate: `python scripts/generate_figures.py`
3. If path wrong, fix: `\includegraphics{figures/chapter10/figure10_1.pdf}`

### Overfull \hbox (badness 10000)

**Cause**: Line too wide (text extends beyond margin)

**Solution**:
- Non-critical: Acceptable if < 10pt overfull
- Critical: Reword sentence, break equation, use `\linebreak`

### PDF Only Shows First 50 Pages

**Cause**: Build crashed midway, partial PDF

**Solution**:
- Check build log for fatal error
- Fix error, rebuild
- Delete `main.aux` and `main.toc`, rebuild fresh

---

## BUILD SCRIPT USAGE

### Standard Build

```bash
cd thesis
bash scripts/build.sh
```

Output: `thesis/build/main.pdf`

### Build Script Contents (from Day 1)

```bash
#!/bin/bash
cd build
pdflatex -interaction=nonstopmode ../main.tex
bibtex main
pdflatex -interaction=nonstopmode ../main.tex
pdflatex -interaction=nonstopmode ../main.tex
cd ..
echo "[OK] Build complete: build/main.pdf"
```

### Manual Build (if script fails)

```bash
cd thesis
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## TIME MANAGEMENT

### If Many Errors (50+ issues)

**Problem**: First build has 50+ errors, will take >2 hours
**Solution**:
- Fix fatal errors first (build must succeed)
- Leave minor warnings for Day 29
- Prioritize: citations > cross-refs > formatting

### If Behind Schedule

At hour 5, still fixing errors (target: hour 4):
- **Option 1**: Extend Day 28 to 10 hours
- **Option 2**: Leave minor issues for Day 29
- **Option 3**: Skip read-through, do on Day 29 instead

### If Ahead of Schedule

At hour 6, build perfect (target: hour 8):
- **Option 1**: Start Day 29 polish tasks early
- **Option 2**: Do thorough read-through (not just skim)
- **Option 3**: Generate backup PDF, archive

---

## NEXT STEPS

Once Day 28 checklist is complete:

1. Backup PDF: `cp build/main.pdf ../backup_day28.pdf`
2. Commit to git: `git add . && git commit -m "docs(thesis): Day 28 complete build"`
3. Print notes for Day 29 (or digital TODO list)
4. Read `day_29_polish/README.md` (10 min)

**Tomorrow (Day 29)**: Content polishing, consistency checks, AI pattern removal

---

## ESTIMATED COMPLETION TIME

- **Clean build (0-10 errors)**: 4-6 hours
- **Moderate issues (10-30 errors)**: 7-9 hours
- **Many issues (30+ errors)**: 10-12 hours

**Most theses have 10-20 fixable issues on first full build.**

---

**[OK] Critical quality gate day! Open `step_01_first_build.md` and compile everything!**
