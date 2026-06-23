# Step 4: Create main.tex Master Document

**Time**: 30 minutes
**Difficulty**: Easy
**Tools**: Text editor, LaTeX

---

## OBJECTIVE

Create the master `main.tex` file that serves as the entry point for your entire thesis, including:
- Document class and formatting
- All chapter includes
- Front matter (abstract, TOC, etc.)
- Bibliography configuration

---

## CREATE MAIN.TEX

**File**: `D:\Projects\main\thesis\main.tex`

### Copy This Template

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MASTER THESIS TEMPLATE
% Sliding Mode Control of Double-Inverted Pendulum with PSO Optimization
%
% Author: [Your Name]
% University: [Your University]
% Date: [Current Date]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% DOCUMENT CLASS %%%
\documentclass[12pt, a4paper, oneside]{report}

%%% LOAD PREAMBLE (packages, custom commands) %%%
\input{preamble}

%%% METADATA (title, author, etc.) %%%
\input{metadata}

%%% BEGIN DOCUMENT %%%
\begin{document}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FRONT MATTER
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\frontmatter  % Roman numerals (i, ii, iii...)

%%% TITLE PAGE %%%
\input{front/title_page}
\clearpage

%%% ABSTRACT %%%
\input{front/abstract}
\clearpage

%%% ACKNOWLEDGMENTS %%%
\input{front/acknowledgments}
\clearpage

%%% TABLE OF CONTENTS %%%
\tableofcontents
\clearpage

%%% LIST OF FIGURES %%%
\listoffigures
\clearpage

%%% LIST OF TABLES %%%
\listoftables
\clearpage

%%% NOMENCLATURE %%%
\input{front/nomenclature}
\clearpage

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MAIN CONTENT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\mainmatter  % Arabic numerals (1, 2, 3...)

%%% CHAPTER 1: INTRODUCTION %%%
\include{chapters/chapter01_introduction}

%%% CHAPTER 2: LITERATURE REVIEW %%%
\include{chapters/chapter02_literature}

%%% CHAPTER 3: PROBLEM FORMULATION %%%
\include{chapters/chapter03_problem}

%%% CHAPTER 4: MATHEMATICAL MODELING %%%
\include{chapters/chapter04_modeling}

%%% CHAPTER 5: SLIDING MODE CONTROL THEORY %%%
\include{chapters/chapter05_smc_theory}

%%% CHAPTER 6: CHATTERING MITIGATION %%%
\include{chapters/chapter06_chattering}

%%% CHAPTER 7: PSO OPTIMIZATION %%%
\include{chapters/chapter07_pso}

%%% CHAPTER 8: SYSTEM IMPLEMENTATION %%%
\include{chapters/chapter08_implementation}

%%% CHAPTER 9: EXPERIMENTAL SETUP %%%
\include{chapters/chapter09_experiments}

%%% CHAPTER 10: CONTROLLER COMPARISON %%%
\include{chapters/chapter10_comparison}

%%% CHAPTER 11: ROBUSTNESS ANALYSIS %%%
\include{chapters/chapter11_robustness}

%%% CHAPTER 12: PSO TUNING RESULTS %%%
\include{chapters/chapter12_pso_results}

%%% CHAPTER 13: LYAPUNOV STABILITY ANALYSIS %%%
\include{chapters/chapter13_stability}

%%% CHAPTER 14: DISCUSSION %%%
\include{chapters/chapter14_discussion}

%%% CHAPTER 15: CONCLUSION %%%
\include{chapters/chapter15_conclusion}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% BIBLIOGRAPHY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% BibTeX style (choose one)
\bibliographystyle{IEEEtran}  % IEEE style (recommended for engineering)
% \bibliographystyle{plain}      % Plain numeric style
% \bibliographystyle{apalike}    % APA style

% Bibliography file
\bibliography{bibliography/main}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% APPENDICES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\appendix

%%% APPENDIX A: LYAPUNOV PROOFS %%%
\include{appendices/appendix_a_proofs}

%%% APPENDIX B: CODE LISTINGS %%%
\include{appendices/appendix_b_code}

%%% APPENDIX C: BENCHMARK DATA %%%
\include{appendices/appendix_c_data}

%%% APPENDIX D: CONFIGURATION FILES %%%
\include{appendices/appendix_d_config}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\end{document}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
```

---

## CREATE PREAMBLE.TEX

**File**: `D:\Projects\main\thesis\preamble.tex`

### Purpose
Centralizes all package imports and custom commands.

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PREAMBLE: Packages, Formatting, Custom Commands
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% PAGE LAYOUT %%%
\usepackage[
    a4paper,
    left=3.5cm,      % Wider left margin for binding
    right=2.5cm,
    top=2.5cm,
    bottom=2.5cm,
    headheight=15pt
]{geometry}

%%% ENCODING & FONTS %%%
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}          % Latin Modern fonts (better than default)

%%% MATH PACKAGES %%%
\usepackage{amsmath}          % Core math environments
\usepackage{amsfonts}         % Math fonts (\mathbb{R})
\usepackage{amssymb}          % Extra symbols (\therefore, \because)
\usepackage{mathtools}        % Extensions to amsmath

%%% GRAPHICS & FIGURES %%%
\usepackage{graphicx}         % \includegraphics
\usepackage{float}            % [H] placement specifier
\usepackage{caption}          % Caption customization
\usepackage{subcaption}       % Subfigures (a), (b), (c)

%%% TABLES %%%
\usepackage{booktabs}         % Professional tables (\toprule, \midrule)
\usepackage{multirow}         % Multi-row cells
\usepackage{array}            % Enhanced column formatting

%%% ALGORITHMS & CODE %%%
\usepackage[ruled,vlined]{algorithm2e}  % Algorithm pseudocode
\usepackage{listings}         % Code listings
\usepackage{xcolor}           % Colors for code syntax highlighting

% Code listing style
\lstset{
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue},
    commentstyle=\color{gray},
    stringstyle=\color{red},
    showstringspaces=false,
    numbers=left,
    numberstyle=\tiny\color{gray},
    frame=single,
    breaklines=true
}

%%% BIBLIOGRAPHY %%%
\usepackage[numbers,sort&compress]{natbib}  % Numeric citations [1,2,3]
% Alternative: \usepackage{biblatex}

%%% HYPERLINKS & CROSS-REFERENCES %%%
\usepackage[
    colorlinks=true,
    linkcolor=blue,       % Internal links (chapters, figures)
    citecolor=red,        % Citation links
    urlcolor=cyan,        % External URLs
    bookmarks=true
]{hyperref}

%%% HEADERS & FOOTERS %%%
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}  % Clear defaults
\fancyhead[R]{\nouppercase{\leftmark}}  % Chapter name on right
\fancyfoot[C]{\thepage}                 % Page number centered

% Chapter pages (no header)
\fancypagestyle{plain}{
    \fancyhf{}
    \fancyfoot[C]{\thepage}
    \renewcommand{\headrulewidth}{0pt}
}

%%% SI UNITS %%%
\usepackage{siunitx}          % \SI{10}{\meter\per\second}

%%% NOMENCLATURE %%%
\usepackage{nomencl}
\makenomenclature

%%% THEOREM ENVIRONMENTS %%%
\usepackage{amsthm}
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}{Definition}[chapter]
\newtheorem{example}{Example}[chapter]

%%% TIKZ (for diagrams) %%%
\usepackage{tikz}
\usetikzlibrary{arrows,shapes,positioning,calc}

%%% CUSTOM COMMANDS %%%

% Vectors (bold)
\newcommand{\vect}[1]{\mathbf{#1}}

% Matrices (bold uppercase)
\newcommand{\mat}[1]{\mathbf{#1}}

% Real numbers
\newcommand{\Real}{\mathbb{R}}

% Derivative shortcuts
\newcommand{\diff}[2]{\frac{d #1}{d #2}}
\newcommand{\pdiff}[2]{\frac{\partial #1}{\partial #2}}

% Common symbols
\newcommand{\thetaone}{\theta_1}
\newcommand{\thetatwo}{\theta_2}

% Norm
\newcommand{\norm}[1]{\left\| #1 \right\|}

% Sign function
\DeclareMathOperator{\sign}{sign}

% Saturation function
\DeclareMathOperator{\sat}{sat}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
```

---

## CREATE METADATA.TEX

**File**: `D:\Projects\main\thesis\metadata.tex`

### Purpose
Stores thesis title, author, and university information.

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% METADATA: Title, Author, University
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% THESIS TITLE %%%
\title{
    \textbf{Sliding Mode Control of Double-Inverted Pendulum} \\
    \textbf{with Particle Swarm Optimization} \\
    \vspace{1cm}
    \large A Master's Thesis
}

%%% AUTHOR %%%
\author{
    [Your Full Name] \\
    \vspace{0.5cm}
    \normalsize [Student ID: XXXXXXXX]
}

%%% DATE %%%
\date{\today}

%%% UNIVERSITY INFO (for title page) %%%
\newcommand{\university}{[Your University Name]}
\newcommand{\department}{Department of [Your Department]}
\newcommand{\degree}{Master of Science in [Your Degree]}
\newcommand{\advisor}{Dr. [Advisor Name]}

% Committee members (if applicable)
\newcommand{\committeememberone}{Dr. [Name]}
\newcommand{\committeemembertwo}{Dr. [Name]}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
```

---

## CREATE PLACEHOLDER FILES

### Front Matter Files

**Create these empty files** (will fill in Days 2-3):

```bash
# Windows PowerShell
cd D:\Projects\main\thesis\front
New-Item -ItemType File -Name "title_page.tex"
New-Item -ItemType File -Name "abstract.tex"
New-Item -ItemType File -Name "acknowledgments.tex"
New-Item -ItemType File -Name "nomenclature.tex"

# Linux/macOS
cd ~/Projects/main/thesis/front
touch title_page.tex abstract.tex acknowledgments.tex nomenclature.tex
```

### Chapter Files

**Create 15 chapter files** (will fill in Days 3-25):

```bash
# Windows PowerShell
cd D:\Projects\main\thesis\chapters
for ($i=1; $i -le 15; $i++) {
    $num = "{0:D2}" -f $i
    New-Item -ItemType File -Name "chapter${num}_placeholder.tex"
}

# Linux/macOS
cd ~/Projects/main/thesis/chapters
for i in {01..15}; do
    touch "chapter${i}_placeholder.tex"
done
```

### Appendix Files

```bash
# Windows PowerShell
cd D:\Projects\main\thesis\appendices
New-Item -ItemType File -Name "appendix_a_proofs.tex"
New-Item -ItemType File -Name "appendix_b_code.tex"
New-Item -ItemType File -Name "appendix_c_data.tex"
New-Item -ItemType File -Name "appendix_d_config.tex"

# Linux/macOS
cd ~/Projects/main/thesis/appendices
touch appendix_a_proofs.tex appendix_b_code.tex appendix_c_data.tex appendix_d_config.tex
```

### Bibliography File

```bash
# Create main bibliography file
# Windows
New-Item -ItemType File -Path "D:\Projects\main\thesis\bibliography\main.bib"

# Linux/macOS
touch ~/Projects/main/thesis/bibliography/main.bib
```

---

## TEST COMPILATION

### Add Minimal Content to Placeholders

**Edit `front/title_page.tex`**:
```latex
\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge \textbf{Sliding Mode Control of Double-Inverted Pendulum}} \\
\vspace{1cm}
{\large with Particle Swarm Optimization} \\
\vspace{2cm}
{\Large [Your Name]} \\
\vfill
{\large \university} \\
{\large \department} \\
\vspace{1cm}
{\large \today}
\end{titlepage}
```

**Edit `front/abstract.tex`**:
```latex
\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}

This thesis presents a comprehensive study of sliding mode control (SMC) applied to double-inverted pendulum (DIP) stabilization, with controller gains optimized using particle swarm optimization (PSO).

[More content to be added in Day 2]
```

**Edit `chapters/chapter01_placeholder.tex`**:
```latex
\chapter{Introduction}
\label{chap:introduction}

This chapter introduces the double-inverted pendulum control problem.

[Content to be added in Day 3]
```

### Compile Test

```bash
cd D:\Projects\main\thesis

# Windows
pdflatex main.tex

# Linux/macOS
pdflatex main.tex
```

**Expected Output**:
- `main.pdf` created
- 10-15 pages (title, TOC, 1 chapter)
- No fatal errors (warnings are okay for now)

**Common Warnings** (safe to ignore for now):
```
LaTeX Warning: Empty bibliography
LaTeX Warning: Citation undefined
LaTeX Warning: There were undefined references
```

---

## VALIDATION CHECKLIST

Before proceeding to Step 5:

### File Structure
- [ ] `main.tex` exists and has 15 chapter includes
- [ ] `preamble.tex` exists with 20+ packages
- [ ] `metadata.tex` exists with title/author
- [ ] All front matter files created (4 files)
- [ ] All chapter files created (15 files)
- [ ] All appendix files created (4 files)
- [ ] Bibliography file `main.bib` exists

### Compilation
- [ ] `pdflatex main.tex` runs without fatal errors
- [ ] `main.pdf` generated
- [ ] PDF has title page
- [ ] PDF has table of contents
- [ ] PDF has at least 1 chapter

### Content
- [ ] Title page shows thesis title
- [ ] Abstract page exists (even if minimal)
- [ ] Chapter 1 page exists (even if minimal)
- [ ] Page numbering: Roman (i, ii...) for front, Arabic (1, 2...) for chapters

---

## TROUBLESHOOTING

### Issue: "! LaTeX Error: File 'preamble.tex' not found"

**Cause**: Wrong working directory

**Solution**:
```bash
# Make sure you're in thesis/ directory
cd D:\Projects\main\thesis
pdflatex main.tex
```

### Issue: "! Undefined control sequence: \vect"

**Cause**: Custom command not defined in preamble

**Solution**: Verify `preamble.tex` has:
```latex
\newcommand{\vect}[1]{\mathbf{#1}}
```

### Issue: Compilation hangs at "Overfull \hbox" warnings

**Cause**: LaTeX waiting for user input

**Solution**: Run with `-interaction=nonstopmode`:
```bash
pdflatex -interaction=nonstopmode main.tex
```

### Issue: "! Package hyperref Error: Wrong DVI mode driver option"

**Cause**: Hyperref incompatibility

**Solution**: Add to preamble before `\usepackage{hyperref}`:
```latex
\usepackage[pdftex]{hyperref}
```

---

## TIME CHECK

- Copy main.tex template: 5 min
- Copy preamble.tex: 5 min
- Copy metadata.tex: 2 min
- Create placeholder files: 5 min
- Add minimal content: 5 min
- Test compilation: 5 min
- Debug errors: 5 min
- **Total**: ~30 minutes

---

## NEXT STEP

Once `main.pdf` compiles successfully:

**Proceed to**: `step_05_test_build.md`

This will verify the complete build system works end-to-end.

---

**[OK] main.tex compiling? Great! Move to final Step 5!**
