# Step 4: Generate Table of Contents

**Time**: 1 hour
**Output**: Auto-generated TOC, LOF, LOT (3-4 pages total)
**Difficulty**: Easy (mostly automatic)

---

## OBJECTIVE

Configure LaTeX to automatically generate:
1. Table of Contents (TOC) - Lists all chapters and sections
2. List of Figures (LOF) - Lists all figures with captions
3. List of Tables (LOT) - Lists all tables with captions

---

## CONFIGURATION IN MAIN.TEX

Your `main.tex` should already have these commands (from Day 1):

```latex
\frontmatter  % Roman numerals

%%% TABLE OF CONTENTS %%%
\tableofcontents
\clearpage

%%% LIST OF FIGURES %%%
\listoffigures
\clearpage

%%% LIST OF TABLES %%%
\listoftables
\clearpage
```

---

## CUSTOMIZATION (OPTIONAL)

### Control TOC Depth

By default, TOC shows chapters, sections, subsections.

**To show only chapters and sections** (hide subsections):
```latex
% In preamble.tex
\setcounter{tocdepth}{1}  % 0=chapter, 1=section, 2=subsection, 3=subsubsection
```

**To show all levels** (chapter → subsubsection):
```latex
\setcounter{tocdepth}{3}
```

### Control Section Numbering

**Default**: Chapters numbered (1, 2, 3...), sections numbered (1.1, 1.2, 1.3...)

**To number only chapters** (sections unnumbered):
```latex
\setcounter{secnumdepth}{0}
```

**Recommended for thesis**: Leave at default (secnumdepth=3)

### TOC Formatting

**Add dots between title and page number**:
```latex
% In preamble.tex
\usepackage{tocloft}
\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}  % Dots for chapters
```

**Change TOC title**:
```latex
\renewcommand{\contentsname}{Table of Contents}  % Default
% OR
\renewcommand{\contentsname}{Contents}  % Shorter
```

---

## ADD ENTRIES TO TOC

### Chapters and Sections (Automatic)

These automatically appear in TOC:
```latex
\chapter{Introduction}  % Appears as: 1 Introduction
\section{Motivation}    % Appears as: 1.1 Motivation
\subsection{Background} % Appears as: 1.1.1 Background
```

### Unnumbered Chapters (Manual)

For front matter (Abstract, Acknowledgments, etc.):
```latex
\chapter*{Abstract}  % Asterisk = no number
\addcontentsline{toc}{chapter}{Abstract}  % Manually add to TOC
```

### Figures and Tables (Automatic)

Every `\caption{}` adds entry:
```latex
\begin{figure}[htbp]
\centering
\includegraphics{figures/test.pdf}
\caption{System architecture}  % Appears in List of Figures
\label{fig:architecture}
\end{figure}

\begin{table}[htbp]
\centering
\caption{Performance comparison}  % Appears in List of Tables
\label{tab:performance}
\begin{tabular}{lrr}
... table content ...
\end{tabular}
\end{table}
```

---

## TEST COMPILATION

### Build with TOC Generation

```bash
cd thesis

# First pass (generates .toc file)
pdflatex main.tex

# Second pass (uses .toc to create TOC)
pdflatex main.tex
```

**Important**: TOC requires 2 passes!
- Pass 1: Collects chapter/section titles → writes to `main.toc`
- Pass 2: Reads `main.toc` → generates TOC pages

### Verify Output

**Open `main.pdf`**:

**Table of Contents (pages iii-iv)**:
- [ ] Lists all 15 chapters
- [ ] Shows section numbers (1.1, 1.2, etc.)
- [ ] Page numbers accurate
- [ ] Clickable hyperlinks (click → jumps to chapter)
- [ ] Front matter included (Abstract, Acknowledgments, etc.)

**List of Figures (page v)**:
- [ ] Lists all figures (even if none yet, should show header)
- [ ] Format: "Figure 1.1: Caption text ........... 5"
- [ ] Page numbers correct

**List of Tables (page vi)**:
- [ ] Lists all tables
- [ ] Format: "Table 1.1: Caption text ........... 7"
- [ ] Page numbers correct

---

## TROUBLESHOOTING

### Issue: TOC is empty or shows "??"

**Cause**: Need multiple compile passes

**Solution**:
```bash
pdflatex main.tex  # First pass
pdflatex main.tex  # Second pass (TOC appears)
```

### Issue: TOC not showing chapter numbers

**Cause**: Using `\chapter*{}` instead of `\chapter{}`

**Solution**: Use `\chapter{}` for numbered chapters, `\chapter*{}` only for front matter

### Issue: LOF/LOT empty despite having figures/tables

**Cause**: Figures/tables missing `\caption{}`

**Solution**: Every figure/table MUST have:
```latex
\caption{Description here}
```

### Issue: TOC too long (5+ pages)

**Cause**: Too many subsections listed

**Solution**: Reduce TOC depth:
```latex
\setcounter{tocdepth}{1}  % Show only chapters and sections
```

### Issue: Page numbers wrong in TOC

**Cause**: Stale .toc file

**Solution**: Delete auxiliary files and rebuild:
```bash
rm main.toc main.lof main.lot main.aux
pdflatex main.tex
pdflatex main.tex
```

### Issue: Hyperlinks not working (not clickable)

**Cause**: `hyperref` package not loaded

**Solution**: Add to `preamble.tex`:
```latex
\usepackage[colorlinks=true, linkcolor=blue]{hyperref}
```

---

## ADVANCED: MINI TOC PER CHAPTER

**Optional**: Add mini-TOC at start of each chapter

```latex
% In preamble.tex
\usepackage{minitoc}
\setcounter{minitocdepth}{2}
\dominitoc

% In main.tex before \mainmatter
\faketableofcontents

% At start of each chapter
\chapter{Introduction}
\minitoc  % Mini table of this chapter only
```

---

## VALIDATION CHECKLIST

### Table of Contents
- [ ] All 15 chapters listed
- [ ] Sections listed under each chapter
- [ ] Page numbers accurate
- [ ] Hyperlinks work (clickable)
- [ ] Front matter included
- [ ] 2-3 pages length

### List of Figures
- [ ] All figures listed (once you add them in later days)
- [ ] Format: "Figure X.Y: Caption ... Page"
- [ ] Hyperlinks to figures work
- [ ] 1-2 pages (once figures added)

### List of Tables
- [ ] All tables listed (once you add them in later days)
- [ ] Format: "Table X.Y: Caption ... Page"
- [ ] Hyperlinks to tables work
- [ ] 1 page (once tables added)

### Compilation
- [ ] No errors or warnings about TOC
- [ ] .toc, .lof, .lot files generated
- [ ] PDF output shows all three lists

---

## TIPS

**Efficiency Trick**: Use build script (from Day 1) instead of manual compilation:
```bash
bash scripts/build.sh  # Automatically does 3 passes
```

**Quality Check**: After adding a new chapter/figure/table, always rebuild to update TOC/LOF/LOT

**Professional Touch**: Ensure all captions are descriptive:
- Bad: "Figure 1.1: Plot"
- Good: "Figure 1.1: Settling time comparison across 7 controllers"

---

## TIME CHECK

- Add TOC/LOF/LOT to main.tex: 5 min (already done Day 1)
- Customize formatting (optional): 15 min
- Test compilation: 10 min
- Verify output: 15 min
- Troubleshoot issues: 15 min
- **Total**: ~1 hour (mostly verification)

---

## NEXT STEP

Once TOC/LOF/LOT are generating correctly:

**Proceed to**: `step_05_title_page.md` (if not done) OR **Day 3**: Start Chapter 1

**Day 2 Complete!** You now have:
- Abstract
- Acknowledgments
- Nomenclature
- Table of Contents
- List of Figures
- List of Tables

Tomorrow you'll write the first full chapter (Introduction).

---

**[OK] TOC/LOF/LOT working? Day 2 complete!**
