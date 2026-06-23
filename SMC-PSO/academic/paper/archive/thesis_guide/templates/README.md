# LaTeX Templates for Thesis Writing

**Complete collection of 7 LaTeX templates for 200-page Master's thesis**

---

## OVERVIEW

This directory contains all LaTeX templates needed to structure and compile your thesis. The templates are designed for IEEE-style formatting with professional typography, proper cross-referencing, and publication-quality output.

**Templates Included**:
1. **main.tex** - Master document structure (~80 lines)
2. **preamble.tex** - Package configuration (~165 lines)
3. **metadata.tex** - Title page information (~50 lines)
4. **chapter_template.tex** - Reusable chapter structure (~200 lines)
5. **front_abstract.tex** - Abstract template (~80 lines)
6. **front_acknowledgments.tex** - Acknowledgments template (~50 lines)
7. **appendix_template.tex** - Appendix structure (~250 lines)

**Total**: ~875 lines of LaTeX boilerplate ready to use

---

## QUICK START

### 1. Create Thesis Directory Structure

```bash
mkdir -p thesis/{chapters,front,appendices,figures,tables,bibliography}
cp templates/*.tex thesis/
```

### 2. Edit Metadata

Open `thesis/metadata.tex` and replace placeholders:
- [Your Full Name] → Your name
- [Your Student ID] → Your ID
- [Your University Name] → University
- [Your Department Name] → Department

### 3. Compile First Build

```bash
cd thesis
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf` (title page + table of contents)

### 4. Add Content

Copy `chapter_template.tex` for each chapter:
```bash
cp chapter_template.tex chapters/chapter01_introduction.tex
cp chapter_template.tex chapters/chapter02_literature_review.tex
# ... etc
```

Edit each chapter file with your content.

### 5. Full Compilation

```bash
pdflatex main.tex       # Pass 1
bibtex main             # Process bibliography
pdflatex main.tex       # Pass 2
pdflatex main.tex       # Pass 3
```

Or use the build script:
```bash
bash scripts/build.sh
```

---

## TEMPLATE DETAILS

### 1. main.tex - Master Document

**Purpose**: Top-level structure that includes all other files

**Key Sections**:
- `\frontmatter` - Front matter with Roman numerals (i, ii, iii, ...)
  - Title page
  - Abstract
  - Acknowledgments
  - Table of contents, List of figures, List of tables
  - Nomenclature (mathematical symbols)

- `\mainmatter` - Main content with Arabic numerals (1, 2, 3, ...)
  - 15 chapters organized into 5 parts:
    - Part I: Introduction and Background (Ch 1-3)
    - Part II: Theoretical Foundations (Ch 4-7)
    - Part III: Implementation (Ch 8-9)
    - Part IV: Results and Analysis (Ch 10-13)
    - Part V: Conclusion (Ch 14-15)

- `\backmatter` - Back matter
  - 4 appendices (A-D)
  - Bibliography

**How to Use**:
1. Copy to `thesis/main.tex`
2. Ensure all `\include{}` paths match your file structure
3. Add/remove chapters as needed
4. Compile with `pdflatex main.tex`

**Customization**:
- Add chapters: Insert `\include{chapters/chapter_new}` in appropriate part
- Change document class: Edit `\documentclass[12pt,twoside,openright]{report}`
- Adjust parts: Comment out `% Part I: ...` lines if not using parts

---

### 2. preamble.tex - Package Configuration

**Purpose**: All LaTeX packages, formatting, and custom commands

**Key Features**:
- **Page layout**: 1-inch margins, 1.5 line spacing
- **Typography**: Times font, microtype for improved spacing
- **Mathematics**: amsmath, amssymb, custom commands
- **Figures/Tables**: graphicx, booktabs, subcaption
- **Code listings**: syntax highlighting for Python, YAML, etc.
- **Hyperlinks**: clickable table of contents, citations, cross-references
- **IEEE style**: Professional formatting for academic publications

**Custom Math Commands**:
```latex
\vect{x}        % Bold vector: x
\mat{M}         % Bold matrix: M
\Real           % Real numbers: R
\norm{x}        % Norm: ||x||
\abs{x}         % Absolute value: |x|
\diff{f}{x}     % Derivative: df/dx
\pdiff{f}{x}    % Partial: ∂f/∂x
\sign           % Sign function
\sat            % Saturation function
```

**Usage Example**:
```latex
\begin{equation}
    \dot{\vect{x}} = \mat{A}\vect{x} + \mat{B}\vect{u}
\end{equation}
```

**How to Use**:
1. Copy to `thesis/preamble.tex`
2. No editing needed (already configured)
3. Add packages if needed (see customization below)

**Customization**:
- Change margins: Edit `\usepackage[letterpaper,margin=1in]{geometry}`
- Change line spacing: Edit `\onehalfspacing` (options: `\singlespacing`, `\doublespacing`)
- Add new package: Insert `\usepackage{packagename}` before hyperref
- Add custom command: Insert `\newcommand{\name}{definition}` at end

---

### 3. metadata.tex - Title Page Information

**Purpose**: Thesis title, author, university details

**What to Edit**:
```latex
\title{Your Thesis Title}
\author{Your Name}
```

Replace all placeholders:
- `[Your Full Name]` → Your name
- `[Your Student ID]` → Student ID
- `[Your University Name]` → University
- `[Your Department Name]` → Department (e.g., Electrical Engineering)
- `[City, Country]` → Location

**Optional Sections** (uncomment to use):
- Thesis committee names
- Copyright notice

**How to Use**:
1. Copy to `thesis/metadata.tex`
2. Replace all placeholders
3. Uncomment optional sections if needed

---

### 4. chapter_template.tex - Reusable Chapter Structure

**Purpose**: Complete example chapter with all common elements

**Includes Examples of**:
- Chapter introduction with objectives
- Sections and subsections with labels
- Mathematical equations (single, multi-line, aligned)
- Figures (single, subfigures)
- Tables (booktabs format)
- Algorithms (pseudocode)
- Code listings (Python syntax highlighting)
- Theorems and proofs
- Chapter summary

**How to Use**:
1. Copy template for each chapter:
   ```bash
   cp chapter_template.tex chapters/chapter01_introduction.tex
   ```
2. Edit chapter title: `\chapter{Your Chapter Title}`
3. Edit chapter label: `\label{chap:your-label}`
4. Replace all section content
5. Delete unused sections (e.g., if no algorithms needed)

**LaTeX Elements Reference**:

**Citations**:
```latex
Single citation: \cite{Utkin1977}
Multiple: \cite{Utkin1977,Khalil2002}
```

**Cross-references**:
```latex
\cref{eq:state-space}      % Equation reference
\cref{fig:example}         % Figure reference
\cref{tab:results}         % Table reference
\cref{chap:introduction}   % Chapter reference
```

**Equations**:
```latex
% Single equation with label
\begin{equation}
    E = mc^2
    \label{eq:einstein}
\end{equation}

% Multiple aligned equations
\begin{align}
    \dot{x}_1 &= x_2 \label{eq:sys1} \\
    \dot{x}_2 &= f(x) + u \label{eq:sys2}
\end{align}
```

**Figures**:
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/my_figure.pdf}
    \caption{Figure caption here}
    \label{fig:my-figure}
\end{figure}
```

**Tables**:
```latex
\begin{table}[htbp]
    \centering
    \caption{Table caption}
    \label{tab:my-table}
    \begin{tabular}{lccc}
        \toprule
        \textbf{Header 1} & \textbf{Header 2} & \textbf{Header 3} \\
        \midrule
        Data 1 & Data 2 & Data 3 \\
        Data 4 & Data 5 & Data 6 \\
        \bottomrule
    \end{tabular}
\end{table}
```

---

### 5. front_abstract.tex - Abstract Template

**Purpose**: 500-800 word thesis abstract

**Structure** (5 paragraphs):
1. **Context and motivation** (100-150 words)
   - What problem are you solving?
   - Why is it important?

2. **Problem statement and objectives** (100-150 words)
   - What are you trying to achieve?
   - What are your research questions?

3. **Methodology** (150-200 words)
   - How did you approach the problem?
   - What methods/techniques did you use?

4. **Key results and findings** (150-200 words)
   - What did you discover?
   - What are the quantitative results?

5. **Contributions and impact** (100-150 words)
   - What are your main contributions?
   - What is the practical significance?

**Keywords**: 5-10 keywords (replace examples with yours)

**How to Use**:
1. Copy to `thesis/front/abstract.tex`
2. Replace `[INSTRUCTION: ...]` with your abstract
3. Follow the 5-paragraph structure
4. Update keywords
5. Ensure 500-800 words total

**Tips**:
- Write abstract LAST (after completing thesis)
- Be specific with numbers (e.g., "24% improvement")
- Avoid citations in abstract
- Make self-contained (readable without thesis)

---

### 6. front_acknowledgments.tex - Acknowledgments Template

**Purpose**: Express gratitude to contributors

**Structure** (6 paragraphs):
1. Primary supervisor
2. Committee members and collaborators
3. Technical support and resources
4. Funding (if applicable)
5. Peers and colleagues
6. Family and friends

**Optional**: Dedication (uncomment if needed)

**How to Use**:
1. Copy to `thesis/front/acknowledgments.tex`
2. Replace all placeholders with names
3. Add/remove paragraphs as appropriate
4. Keep professional and sincere

**Tips**:
- Order by contribution level (supervisor first)
- Be specific (mention what each person did)
- Keep brief (1-2 pages maximum)
- Proofread carefully (names must be correct)

---

### 7. appendix_template.tex - Appendix Structure

**Purpose**: Complete example appendix with all common elements

**Includes Examples of**:
- Detailed mathematical proofs
- Complete source code listings
- Long data tables (multi-page)
- Configuration files

**How to Use**:
1. Copy template for each appendix:
   ```bash
   cp appendix_template.tex appendices/appendix_a_proofs.tex
   cp appendix_template.tex appendices/appendix_b_code.tex
   cp appendix_template.tex appendices/appendix_c_data.tex
   cp appendix_template.tex appendices/appendix_d_config.tex
   ```
2. Edit appendix title: `\chapter{Your Appendix Title}`
3. Edit label: `\label{app:your-label}`
4. Replace content
5. Delete unused sections

**Appendix Suggestions**:
- **Appendix A**: Mathematical proofs (detailed Lyapunov proofs)
- **Appendix B**: Source code (controller implementations)
- **Appendix C**: Complete data tables (all benchmark results)
- **Appendix D**: Configuration files (config.yaml, parameters)

---

## COMPILATION WORKFLOW

### Manual Compilation (4 passes)

```bash
cd thesis

# Pass 1: Generate .aux files
pdflatex main.tex

# Process bibliography
bibtex main

# Pass 2: Include bibliography
pdflatex main.tex

# Pass 3: Resolve cross-references
pdflatex main.tex

# Optional Pass 4: Final polish
pdflatex main.tex
```

### Automated Compilation

Use the build script:
```bash
cd thesis
bash scripts/build.sh
```

Output: `build/main.pdf`

---

## TROUBLESHOOTING

### Error: Package not found

**Solution**: Install missing package
- **Windows (MiKTeX)**: Packages auto-install on first use
- **macOS (MacTeX)**: `sudo tlmgr install packagename`
- **Linux (TeX Live)**: `sudo apt install texlive-packagename`

### Error: Undefined control sequence

**Cause**: Using command before defining or loading package

**Solution**: Check `preamble.tex` has required package:
- Math commands → `\usepackage{amsmath}`
- Bold math → `\usepackage{bm}`
- Algorithms → `\usepackage{algorithm}`

### Warning: Citation undefined

**Cause**: BibTeX not run or .bib file missing

**Solution**:
1. Ensure `bibliography/references.bib` exists
2. Run: `bibtex main`
3. Run: `pdflatex main.tex` twice more

### Warning: Reference undefined

**Cause**: Label doesn't exist or needs another compilation

**Solution**: Run `pdflatex main.tex` one more time

### Error: File not found (figure/table)

**Cause**: Path incorrect or file doesn't exist

**Solution**:
1. Check file exists: `ls figures/my_figure.pdf`
2. Check path in LaTeX: `\includegraphics{figures/my_figure.pdf}`
3. Generate missing figures: `python automation_scripts/generate_figures.py`

### Warning: Overfull hbox

**Cause**: Line too long (text overflow)

**Solution**:
- Reword sentence to be shorter
- Use `\linebreak` to force break
- Use `\sloppy` before paragraph (last resort)

---

## CUSTOMIZATION

### Change Document Class

Edit `main.tex`:
```latex
% Current: Two-sided report
\documentclass[12pt,twoside,openright]{report}

% Option 1: One-sided
\documentclass[12pt,oneside]{report}

% Option 2: Book class
\documentclass[12pt,twoside]{book}

% Option 3: Article (for shorter documents)
\documentclass[12pt,twocolumn]{article}
```

### Change Margins

Edit `preamble.tex`:
```latex
% Current: 1-inch margins
\usepackage[letterpaper,margin=1in]{geometry}

% Custom margins
\usepackage[letterpaper,top=1in,bottom=1in,left=1.5in,right=1in]{geometry}

% A4 paper
\usepackage[a4paper,margin=2.5cm]{geometry}
```

### Change Line Spacing

Edit `preamble.tex`:
```latex
% Current: 1.5 spacing
\onehalfspacing

% Options:
\singlespacing      % 1.0
\doublespacing      % 2.0
\setstretch{1.3}    % Custom (1.3x)
```

### Change Font

Edit `preamble.tex`:
```latex
% Current: Times
\usepackage{times}

% Option 1: Computer Modern (LaTeX default)
% (Comment out \usepackage{times})

% Option 2: Palatino
\usepackage{palatino}

% Option 3: Helvetica
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
```

### Add New Package

Edit `preamble.tex` (before hyperref):
```latex
% Add before this line:
\usepackage{hyperref}

% Your new package:
\usepackage{yourpackage}
```

### Add Custom Command

Edit `preamble.tex` (at end):
```latex
% Your custom commands
\newcommand{\mycommand}[1]{\textbf{#1}}
\newcommand{\eq}[1]{Equation~(\ref{#1})}
```

---

## FILE ORGANIZATION

### Recommended Directory Structure

```
thesis/
├── main.tex                    [Master document]
├── preamble.tex                [Package configuration]
├── metadata.tex                [Title page info]
│
├── front/
│   ├── abstract.tex            [Abstract]
│   ├── acknowledgments.tex     [Acknowledgments]
│   └── nomenclature.tex        [Symbol list]
│
├── chapters/
│   ├── chapter01_introduction.tex
│   ├── chapter02_literature_review.tex
│   ├── chapter03_problem_formulation.tex
│   ├── ... (15 chapters total)
│   └── chapter15_conclusion.tex
│
├── appendices/
│   ├── appendix_a_proofs.tex
│   ├── appendix_b_code.tex
│   ├── appendix_c_data.tex
│   └── appendix_d_config.tex
│
├── figures/
│   ├── fig_settling_time_comparison.pdf
│   ├── fig_pso_convergence.pdf
│   └── ... (60 figures total)
│
├── tables/
│   ├── baseline.tex
│   ├── comprehensive.tex
│   └── ... (30 tables total)
│
├── bibliography/
│   ├── references.bib          [Combined bibliography]
│   ├── books.bib               [Book citations]
│   ├── papers.bib              [Journal papers]
│   └── conference.bib          [Conference papers]
│
└── build/
    ├── main.pdf                [OUTPUT: Final thesis PDF]
    ├── main.aux
    ├── main.log
    └── ... (build artifacts)
```

---

## BEST PRACTICES

### Cross-Referencing

**Always use `\cref{}` instead of `\ref{}`**:
```latex
% Good (automatic label)
See \cref{eq:state-space} for details.
→ "See Eq. (1.3) for details."

% Bad (manual label)
See Equation~\ref{eq:state-space} for details.
→ "See Equation 1.3 for details." (inconsistent)
```

### Labels

**Use consistent naming convention**:
```latex
\label{chap:introduction}      % Chapters
\label{sec:methodology}        % Sections
\label{subsec:pso-algorithm}   % Subsections
\label{eq:lyapunov}            % Equations
\label{fig:convergence}        % Figures
\label{tab:results}            % Tables
\label{alg:smc-control}        % Algorithms
\label{lst:python-code}        % Listings
\label{app:proofs}             % Appendices
```

### Figures

**Use vector graphics (PDF) whenever possible**:
```latex
% Good (vector, scales infinitely)
\includegraphics{figures/plot.pdf}

% Okay (raster, 300 DPI)
\includegraphics{figures/photo.png}

% Bad (raster, low resolution)
\includegraphics{figures/chart.jpg}
```

### Tables

**Always use booktabs package**:
```latex
% Good (professional)
\begin{tabular}{lcc}
    \toprule
    ... headers ...
    \midrule
    ... data ...
    \bottomrule
\end{tabular}

% Bad (ugly lines)
\begin{tabular}{|l|c|c|}
    \hline
    ... headers ...
    \hline
    ... data ...
    \hline
\end{tabular}
```

### Citations

**Cite properly at sentence end**:
```latex
% Good
Sliding mode control was introduced by Utkin~\cite{Utkin1977}.

% Good (multiple)
Several SMC variants exist~\cite{Utkin1977,Edwards1998,Shtessel2014}.

% Bad (space before citation)
... by Utkin \cite{Utkin1977}.
```

---

## QUALITY CHECKLIST

Before final submission:

- [ ] All placeholders replaced in metadata.tex
- [ ] Abstract is 500-800 words
- [ ] All chapters present (15 chapters)
- [ ] All appendices present (4 appendices)
- [ ] All figures referenced in text
- [ ] All tables referenced in text
- [ ] All equations numbered and referenced
- [ ] No undefined references (`??` in PDF)
- [ ] No undefined citations (`[?]` in PDF)
- [ ] Bibliography compiles correctly
- [ ] Table of contents accurate
- [ ] List of figures accurate
- [ ] List of tables accurate
- [ ] Page numbers correct (Roman/Arabic)
- [ ] Headers/footers correct
- [ ] No overfull/underfull boxes (or minimal)
- [ ] PDF metadata correct (title, author)
- [ ] Hyperlinks work (blue clickable links)
- [ ] Final page count: 180-220 pages

---

## ADDITIONAL RESOURCES

### LaTeX References

- **LaTeX Wikibook**: https://en.wikibooks.org/wiki/LaTeX
- **Overleaf Documentation**: https://www.overleaf.com/learn
- **TeX Stack Exchange**: https://tex.stackexchange.com/

### Package Documentation

- **amsmath**: `texdoc amsmath`
- **hyperref**: `texdoc hyperref`
- **booktabs**: `texdoc booktabs`
- **cleveref**: `texdoc cleveref`

### Online LaTeX Editors

- **Overleaf**: https://www.overleaf.com/ (collaborative, online)
- **TeXstudio**: https://www.texstudio.org/ (offline, feature-rich)
- **VS Code + LaTeX Workshop**: (modern, extensible)

---

## CREDITS

**Author**: Agent 2 (Automation & Templates Specialist)

**Created**: 2025-12-05

**Project**: DIP-SMC-PSO Thesis Writing Guide

**License**: MIT (open source, use freely)

---

## NEXT STEPS

1. **Copy templates** to thesis directory
2. **Edit metadata** with your information
3. **Test compilation** with `pdflatex main.tex`
4. **Start writing** using chapter templates
5. **Generate figures/tables** using automation scripts
6. **Build PDF** daily to catch errors early

**[OK] Templates Ready | [OK] IEEE Style | [OK] 875 Lines | [OK] Ready to Compile**
