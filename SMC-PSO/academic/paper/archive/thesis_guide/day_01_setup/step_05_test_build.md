# Step 5: Test Build System

**Time**: 30 minutes
**Difficulty**: Easy
**Tools**: LaTeX, command line

---

## OBJECTIVE

Verify the complete thesis build system works end-to-end by:
1. Compiling the complete document
2. Testing cross-references
3. Verifying bibliography compilation
4. Checking PDF output quality

---

## FULL BUILD TEST

### Run Complete Build

**Windows**:
```powershell
cd D:\Projects\main\thesis
scripts\build.bat
```

**Linux/macOS**:
```bash
cd ~/Projects/main/thesis
bash scripts/build.sh
```

**Expected Output**:
```
[INFO] Starting thesis compilation...
[STEP 1/4] Running pdflatex (1st pass)...
This is pdfTeX, Version 3.141592653...
Output written on main.pdf (15 pages, 45231 bytes).

[STEP 2/4] Running bibtex...
This is BibTeX, Version 0.99d...

[STEP 3/4] Running pdflatex (2nd pass)...
Output written on main.pdf (15 pages, 46102 bytes).

[STEP 4/4] Running pdflatex (3rd pass)...
Output written on main.pdf (15 pages, 46158 bytes).

[INFO] Cleaning auxiliary files...
[OK] Build complete! Output: main.pdf
```

### Manual Build (if script fails)

```bash
cd thesis

# First pass
pdflatex -interaction=nonstopmode main.tex

# BibTeX
bibtex main

# Second pass
pdflatex -interaction=nonstopmode main.tex

# Third pass
pdflatex -interaction=nonstopmode main.tex
```

---

## VERIFY PDF OUTPUT

### 1. Check File Size

```bash
# Windows PowerShell
Get-Item main.pdf | Select-Object Name, Length

# Linux/macOS
ls -lh main.pdf
```

**Expected**: 40-100 KB (for minimal thesis with placeholders)

**If > 1 MB**: Check for accidentally embedded large images

**If < 10 KB**: PDF may be corrupted, recompile

### 2. Open PDF

```bash
# Windows
start main.pdf

# macOS
open main.pdf

# Linux
xdg-open main.pdf
```

### 3. Visual Inspection

Check the following pages:

**Title Page (page i)**:
- [ ] Thesis title displayed correctly
- [ ] Author name present
- [ ] University name present
- [ ] Date shown

**Abstract (page ii)**:
- [ ] "Abstract" header
- [ ] Placeholder text visible
- [ ] Added to table of contents

**Table of Contents (page iii-iv)**:
- [ ] Lists all 15 chapters
- [ ] Page numbers present (even if wrong for now)
- [ ] Hyperlinks work (click chapter → jumps to page)

**List of Figures (page v)**:
- [ ] Empty or placeholder message (okay for Day 1)

**List of Tables (page vi)**:
- [ ] Empty or placeholder message (okay for Day 1)

**Nomenclature (page vii)**:
- [ ] "Nomenclature" header
- [ ] Placeholder text or empty (okay for Day 1)

**Chapter 1 (page 1)**:
- [ ] Page number changes from Roman (vii) to Arabic (1)
- [ ] "Chapter 1: Introduction" header
- [ ] Placeholder text visible
- [ ] Page header shows "CHAPTER 1. INTRODUCTION"

**Bibliography (last pages)**:
- [ ] "Bibliography" or "References" section
- [ ] Empty or shows "No references" (okay for Day 1)

**Appendices (after bibliography)**:
- [ ] "Appendix A" starts
- [ ] Labeled as Appendix A, B, C, D
- [ ] Placeholder text in each

---

## TEST CROSS-REFERENCES

### Add Test References

**Edit `chapters/chapter01_placeholder.tex`**:
```latex
\chapter{Introduction}
\label{chap:introduction}

This chapter introduces the problem. See Chapter \ref{chap:literature} for literature review.

\section{Motivation}
\label{sec:intro:motivation}

The motivation is explained here.

\section{Objectives}

The objectives reference Section \ref{sec:intro:motivation}.
```

**Edit `chapters/chapter02_placeholder.tex`**:
```latex
\chapter{Literature Review}
\label{chap:literature}

This chapter reviews existing work mentioned in Chapter \ref{chap:introduction}.
```

### Recompile

```bash
bash scripts/build.sh
```

### Verify References

**Open `main.pdf`**:

1. **Chapter 1, first paragraph**:
   - Should say: "See Chapter 2 for literature review"
   - Click "2" → jumps to Chapter 2

2. **Chapter 1, Objectives section**:
   - Should say: "reference Section 1.1"
   - Click "1.1" → jumps back to Motivation section

3. **Chapter 2, first paragraph**:
   - Should say: "mentioned in Chapter 1"
   - Click "1" → jumps back to Chapter 1

**If you see "??" instead of numbers**:
- Normal on first compile
- Run `pdflatex` again (should resolve after 2-3 passes)

---

## TEST BIBLIOGRAPHY

### Add Test Citation

**Edit `chapters/chapter01_placeholder.tex`**:
```latex
\chapter{Introduction}
\label{chap:introduction}

The inverted pendulum has been studied extensively \cite{Khalil2002, Utkin1977}.
```

**Add to `bibliography/main.bib`**:
```bibtex
@book{Khalil2002,
  author = {Khalil, Hassan K.},
  title = {Nonlinear Systems},
  publisher = {Prentice Hall},
  year = {2002},
  edition = {3rd}
}

@article{Utkin1977,
  author = {Utkin, V. I.},
  title = {Variable structure systems with sliding modes},
  journal = {IEEE Transactions on Automatic Control},
  year = {1977},
  volume = {22},
  number = {2},
  pages = {212--222}
}
```

### Rebuild

```bash
bash scripts/build.sh
```

### Verify Citations

**In main.pdf, Chapter 1**:
- Should show: "studied extensively [1, 2]"
- Numbers are hyperlinks (click → jumps to bibliography)

**In Bibliography section**:
- Should list:
  ```
  [1] H. K. Khalil, Nonlinear Systems, 3rd ed. Prentice Hall, 2002.
  [2] V. I. Utkin, "Variable structure systems with sliding modes," IEEE
      Transactions on Automatic Control, vol. 22, no. 2, pp. 212-222, 1977.
  ```

**If citations show as "[?]"**:
- Run `bibtex main` manually
- Then `pdflatex main.tex` twice more

---

## TEST FIGURE INCLUSION

### Add Test Figure

**Create simple plot** (`thesis/figures/test_plot.pdf`):

Option 1: Use Python (if matplotlib installed):
```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(6, 4))
plt.plot(x, y)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Test Sinusoid')
plt.grid(True)
plt.savefig('thesis/figures/test_plot.pdf', bbox_inches='tight')
print("[OK] Created test_plot.pdf")
```

Option 2: Use any image (convert to PDF):
- Save any image as `test_image.png`
- Use online converter: png → pdf
- Save as `thesis/figures/test_plot.pdf`

### Add Figure to Chapter

**Edit `chapters/chapter01_placeholder.tex`**:
```latex
\chapter{Introduction}
\label{chap:introduction}

Figure \ref{fig:test} shows a test plot.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.6\textwidth]{figures/test_plot.pdf}
\caption{Test sinusoid plot}
\label{fig:test}
\end{figure}
```

### Rebuild and Verify

```bash
bash scripts/build.sh
```

**In main.pdf**:
- Figure should appear in Chapter 1
- Caption: "Figure 1.1: Test sinusoid plot"
- List of Figures page now shows this figure

---

## TEST TABLE INCLUSION

### Add Test Table

**Edit `chapters/chapter01_placeholder.tex`**:
```latex
Table \ref{tab:test} shows test data.

\begin{table}[htbp]
\centering
\caption{Test performance data}
\label{tab:test}
\begin{tabular}{lrr}
\toprule
Controller & Settling Time (s) & Overshoot (\%) \\
\midrule
Classical SMC & 2.45 & 8.3 \\
Adaptive SMC & 1.98 & 3.7 \\
\bottomrule
\end{tabular}
\end{table}
```

### Rebuild and Verify

```bash
bash scripts/build.sh
```

**In main.pdf**:
- Table appears in Chapter 1
- Caption: "Table 1.1: Test performance data"
- List of Tables page now shows this table

---

## VALIDATION CHECKLIST

Complete before moving to Day 2:

### Build System
- [ ] `build.sh` / `build.bat` runs without errors
- [ ] All 4 passes complete (pdflatex, bibtex, pdflatex, pdflatex)
- [ ] `main.pdf` generated successfully
- [ ] PDF opens without corruption

### Document Structure
- [ ] Front matter uses Roman numerals (i, ii, iii...)
- [ ] Main content uses Arabic numerals (1, 2, 3...)
- [ ] Table of Contents lists all chapters
- [ ] List of Figures lists test figure
- [ ] List of Tables lists test table

### Cross-References
- [ ] Chapter references work (e.g., "Chapter 2")
- [ ] Section references work (e.g., "Section 1.1")
- [ ] Figure references work (e.g., "Figure 1.1")
- [ ] Table references work (e.g., "Table 1.1")
- [ ] All references are clickable hyperlinks

### Citations
- [ ] In-text citations show as [1], [2], etc.
- [ ] Citations are clickable (jump to bibliography)
- [ ] Bibliography lists cited papers
- [ ] BibTeX formatting correct (IEEE style)

### Figures & Tables
- [ ] Test figure displays correctly
- [ ] Test table renders with booktabs style
- [ ] Both appear in respective lists

---

## TROUBLESHOOTING

### Issue: References show as "??"

**Cause**: Need multiple compile passes

**Solution**:
```bash
pdflatex main.tex  # First pass
bibtex main        # Process bibliography
pdflatex main.tex  # Second pass (resolve citations)
pdflatex main.tex  # Third pass (resolve cross-refs)
```

### Issue: Bibliography empty despite .bib file

**Cause**: BibTeX not finding bibliography file

**Solution**: Check `main.tex` has:
```latex
\bibliography{bibliography/main}  % Path relative to main.tex
```

### Issue: Figure not appearing

**Cause**: Wrong file path or format

**Solutions**:
1. Check path: `figures/test_plot.pdf` (no leading slash)
2. Check file exists: `ls thesis/figures/test_plot.pdf`
3. Try different format: PNG, JPG (PDF preferred for quality)
4. Use absolute path temporarily: `\includegraphics{D:/Projects/main/thesis/figures/test_plot.pdf}`

### Issue: Build script fails at BibTeX step

**Cause**: No citations in document yet

**Solution**: This is okay for Day 1. BibTeX will show:
```
Warning--I didn't find any citation commands
```
This is normal. Continue to Step 5.

### Issue: PDF much larger than expected (> 10 MB)

**Cause**: Embedded high-resolution images

**Solution**:
1. Check figure sizes: `ls -lh figures/*.pdf`
2. Compress images: Use online tools or ImageMagick
3. For Day 1, remove test images and use placeholders

---

## PERFORMANCE BENCHMARKS

**Compilation Time** (on modern laptop):
- First pass: 3-5 seconds
- BibTeX: 1-2 seconds
- Second pass: 2-4 seconds
- Third pass: 2-4 seconds
- **Total**: 8-15 seconds

**If slower than 30 seconds**: Check for:
- Very large images (> 5 MB each)
- Network drives (compile locally instead)
- Antivirus scanning (add thesis/ to exclusions)

---

## BACKUP YOUR WORK

```bash
# Commit to git
cd D:\Projects\main
git add thesis/
git commit -m "setup(thesis): Day 1 complete - build system working"
git push

# Create backup
# Windows
Compress-Archive -Path thesis -DestinationPath thesis_backup_day1.zip

# Linux/macOS
tar -czf thesis_backup_day1.tar.gz thesis/
```

---

## TIME CHECK

- Full build test: 5 min
- Verify PDF output: 5 min
- Test cross-references: 5 min
- Test bibliography: 5 min
- Test figures/tables: 5 min
- Troubleshoot issues: 5 min
- **Total**: ~30 minutes

---

## NEXT STEPS

**Day 1 is complete!** You now have:
- Working LaTeX build system
- Master document structure
- 5 automation scripts
- Verified compilation pipeline

**Tomorrow (Day 2)**: Write front matter (abstract, acknowledgments, nomenclature)

Take a break! You've built the foundation for your 200-page thesis.

---

**[OK] Build system working? Excellent! Day 1 complete!**
