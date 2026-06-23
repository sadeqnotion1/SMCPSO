# arXiv Submission Guide - DIP-SMC-PSO Research Paper

**Document Version:** 1.0
**Date:** November 12, 2025
**Status:** OPERATIONAL
**Target Paper:** LT-7 v2.1 (Research Paper - SUBMISSION-READY)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Workflow](#detailed-workflow)
5. [Metadata Configuration](#metadata-configuration)
6. [Troubleshooting](#troubleshooting)
7. [arXiv Submission Portal](#arxiv-submission-portal)
8. [Post-Submission](#post-submission)
9. [References](#references)

---

## Overview

This guide describes the automated workflow for preparing the DIP-SMC-PSO research paper (LT-7 v2.1) for submission to arXiv.org. The workflow automates:

- LaTeX compilation and validation (3-pass + bibtex)
- Figure inclusion verification (14 publication-quality figures)
- Tarball creation (<10MB arXiv limit)
- Metadata generation (title, abstract, authors, categories)
- Pre-flight validation (no undefined references, proper formatting)

**Time Savings:** Manual submission (8 hours) → Automated workflow (30 minutes) = 93% reduction

---

## Prerequisites

### Software Requirements

1. **LaTeX Distribution:**
   - **Linux:** TeX Live (`sudo apt install texlive-full`)
   - **macOS:** MacTeX (`brew install --cask mactex`)
   - **Windows:** MiKTeX (https://miktex.org/download)

2. **Required LaTeX Packages:**
   - IEEEtran (document class)
   - graphicx (figure inclusion)
   - amsmath, amssymb (mathematics)
   - hyperref (cross-references)
   - cite (bibliography)

3. **Bash Shell:**
   - **Linux/macOS:** Built-in
   - **Windows:** Git Bash or WSL (Windows Subsystem for Linux)

### Paper Source Files

All source files must be placed in `.artifacts/thesis/`:

```
.artifacts/thesis/
├── paper.tex           # Main LaTeX document
├── references.bib      # Bibliography (BibTeX format)
├── figures/            # 14 publication-quality figures
│   ├── fig1_*.png
│   ├── fig2_*.pdf
│   └── ...
├── IEEEtran.cls        # LaTeX class file (optional, if custom)
└── IEEEtran.bst        # Bibliography style (optional, if custom)
```

**Note:** If LaTeX files don't exist yet, convert the LT-7 v2.1 Markdown research paper to LaTeX format.

---

## Quick Start

### Step 1: Run Automated Workflow

```bash
# Navigate to project root
cd D:/Projects/main

# Run arXiv submission workflow
bash scripts/publication/arxiv_submit.sh

# Or with options:
bash scripts/publication/arxiv_submit.sh --dry-run      # Validate only
bash scripts/publication/arxiv_submit.sh --skip-compile # Skip LaTeX compilation
```

### Step 2: Review Output

The workflow generates:

- **Tarball:** `.artifacts/thesis/arxiv_submission.tar.gz`
- **Metadata:** `scripts/publication/arxiv_metadata.json`
- **Log:** `.artifacts/arxiv_submission.log`

### Step 3: Verify Tarball Contents

```bash
# List files in tarball
tar -tzf .artifacts/thesis/arxiv_submission.tar.gz

# Extract tarball (for inspection)
mkdir /tmp/arxiv_test
tar -xzf .artifacts/thesis/arxiv_submission.tar.gz -C /tmp/arxiv_test
```

### Step 4: Update Metadata

Edit `scripts/publication/arxiv_metadata.json`:

```json
{
  "title": "Sliding Mode Control with PSO Optimization for Double-Inverted Pendulum",
  "abstract": "This paper presents...",
  "authors": [
    {
      "name": "Your Name",
      "affiliation": "Your Institution",
      "email": "your.email@institution.edu"
    }
  ],
  "categories": ["cs.SY", "cs.RO", "math.OC"]
}
```

### Step 5: Submit to arXiv

1. Go to https://arxiv.org/submit
2. Create account or log in
3. Upload tarball: `arxiv_submission.tar.gz`
4. Enter metadata (copy from `arxiv_metadata.json`)
5. Submit for moderation

---

## Detailed Workflow

### Phase 1: Validation (2-3 minutes)

The workflow validates:

1. **Dependencies:** pdflatex, bibtex installed
2. **Directory structure:** `.artifacts/thesis/` exists
3. **Required files:** `paper.tex`, `references.bib` present
4. **Figure count:** 14 figures in `figures/` directory

**Exit codes:**
- `0` - Success
- `1` - LaTeX compilation failed
- `2` - Missing required files
- `3` - Tarball size exceeds 10MB
- `4` - Validation failed (undefined references)

### Phase 2: LaTeX Compilation (5-10 minutes)

**3-pass compilation + bibtex:**

```bash
pdflatex paper.tex    # Pass 1: Generate aux file
bibtex paper          # Generate bibliography
pdflatex paper.tex    # Pass 2: Resolve citations
pdflatex paper.tex    # Pass 3: Finalize cross-references
```

**Compilation log:** `.artifacts/arxiv_submission.log`

**Common errors:**
- **Undefined references:** Missing `\label` or `\cite` keys
- **Missing figures:** Check `\includegraphics` paths
- **Package errors:** Install missing LaTeX packages

### Phase 3: Tarball Creation (1-2 minutes)

**Staging directory:**
- All files copied to `/tmp/arxiv_submission_<PID>/`
- Flat directory structure (arXiv requirement)
- No subdirectories (figures moved to root)

**Tarball contents:**
```
arxiv_submission.tar.gz
├── paper.tex
├── references.bib
├── fig1_*.png
├── fig2_*.pdf
├── ...
├── IEEEtran.cls (if present)
└── IEEEtran.bst (if present)
```

**Size constraints:**
- **Limit:** 10MB (arXiv hard limit)
- **Typical:** 2-5MB (with 14 compressed figures)
- **Optimization:** Use JPEG for photos, PDF for vector graphics

### Phase 4: Metadata Generation (1 minute)

**Extracted from LaTeX:**
- **Title:** `\title{...}` command
- **Abstract:** `\begin{abstract}...\end{abstract}` environment

**Default categories:**
- `cs.SY` - Systems and Control
- `cs.RO` - Robotics
- `math.OC` - Optimization and Control

**License:**
- Default: `http://arxiv.org/licenses/nonexclusive-distrib/1.0/`
- Allows publication in journals after arXiv preprint

### Phase 5: Validation (1 minute)

**Checks:**
- Tarball size < 10MB
- File count reasonable (typically 15-30 files)
- No undefined references in LaTeX log
- Figures included in tarball

---

## Metadata Configuration

### Required Fields

```json
{
  "title": "Full paper title (250 char limit)",
  "abstract": "Concise abstract (1920 char limit, ~250 words)",
  "authors": [
    {
      "name": "FirstName LastName",
      "affiliation": "Institution Name",
      "email": "email@domain.edu"
    }
  ],
  "categories": [
    "cs.SY",     // Primary category (required)
    "cs.RO",     // Secondary category
    "math.OC"    // Tertiary category
  ]
}
```

### Optional Fields

```json
{
  "comments": "Submitted to IEEE CDC 2025",
  "msc_class": "93B12, 93C10",           // Mathematics Subject Classification
  "acm_class": "I.2.9, J.7",             // ACM Computing Classification
  "journal_ref": "IEEE Trans. on Auto. Control", // If published
  "doi": "10.1109/TAC.2025.1234567",     // If published
  "report_no": "TR-2025-001",            // Institution report number
  "license": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/"
}
```

### Category Selection Guide

**Primary Categories (choose one):**
- `cs.SY` - Systems and Control (best fit for DIP-SMC-PSO)
- `cs.RO` - Robotics (if robotic application emphasized)
- `math.OC` - Optimization and Control (if PSO theory emphasized)

**Cross-List Categories (optional, up to 2):**
- `eess.SY` - Electrical Engineering and Systems Science
- `cs.LG` - Machine Learning (if PSO as ML optimization)
- `cs.NA` - Numerical Analysis (if numerical methods emphasized)

**Subject Classifications:**
- **MSC (Mathematics Subject Classification):**
  - `93B12` - Variable structure systems (SMC)
  - `93C10` - Nonlinear systems
  - `93C95` - Applications of control and systems theory
- **ACM (Computing Classification):**
  - `I.2.9` - Robotics
  - `J.7` - Computers in Other Systems

---

## Troubleshooting

### Error: "pdflatex not found"

**Cause:** LaTeX distribution not installed or not in PATH

**Solution:**
```bash
# Linux
sudo apt install texlive-full

# macOS
brew install --cask mactex

# Windows (use MiKTeX installer)
# Then restart terminal
```

### Error: "Missing paper.tex"

**Cause:** LaTeX source file not created yet

**Solution:**
```bash
# Convert LT-7 v2.1 Markdown to LaTeX
# Manual conversion or use Pandoc:
cd .artifacts/thesis
pandoc research_paper_lt7.md -o paper.tex --template=ieee.tex
```

### Error: "Undefined references"

**Cause:** Missing `\label` or `\cite` keys

**Solution:**
```bash
# Check log file for undefined references
grep "undefined" .artifacts/arxiv_submission.log

# Example fixes:
# - Missing citation: Add entry to references.bib
# - Missing label: Add \label{sec:intro} to section
```

### Error: "Tarball exceeds 10MB"

**Cause:** Figures too large (uncompressed or high-resolution)

**Solution:**
```bash
# Compress PNG figures
cd .artifacts/thesis/figures
for f in *.png; do
  convert "$f" -quality 85 -compress jpeg "${f%.png}_compressed.png"
done

# Or convert to JPEG
for f in *.png; do
  convert "$f" -quality 90 "${f%.png}.jpg"
done

# Verify size reduction
du -sh .
```

### Error: "LaTeX compilation failed (pass 1)"

**Cause:** Syntax error in `paper.tex`

**Solution:**
```bash
# Review log file for error location
tail -50 .artifacts/arxiv_submission.log

# Common errors:
# - Missing \begin{document}
# - Unmatched braces { }
# - Missing \end{document}
# - Invalid command (typo in \cite, \ref, etc.)
```

### Warning: "Package hyperref Warning: Token not allowed"

**Cause:** Special characters in `\title{}` or `\section{}`

**Solution:**
```latex
% Escape special characters
\title{SMC with PSO: A \$10\^9\$ Optimization Problem}

% Or use \texorpdfstring for hyperref
\section{\texorpdfstring{$\alpha$-Stability}{Alpha-Stability}}
```

---

## arXiv Submission Portal

### Step 1: Create Account

1. Go to https://arxiv.org/user/login
2. Create account or use ORCID login
3. Verify email address

### Step 2: Start Submission

1. Go to https://arxiv.org/submit
2. Click "Start New Submission"
3. Select license: "arXiv.org perpetual, non-exclusive license"

### Step 3: Upload Files

**Option 1: Upload Tarball (Recommended)**
- Upload `arxiv_submission.tar.gz`
- arXiv will automatically extract and compile

**Option 2: Upload Individual Files**
- Upload `paper.tex`, `references.bib`, figures separately
- arXiv will compile using detected main file

### Step 4: Enter Metadata

**Title:** Copy from `arxiv_metadata.json`

**Authors:**
- Full name, affiliation, email
- Order matters (first author = corresponding author)

**Abstract:**
- 250-word limit
- Plain text (no LaTeX math)
- Use Unicode for special characters (α, β, etc.)

**Categories:**
- Primary: `cs.SY` (Systems and Control)
- Cross-list: `cs.RO`, `math.OC`

**Comments (optional):**
- "Submitted to IEEE CDC 2025"
- "14 figures, 10 pages"

**MSC/ACM Classes (optional):**
- MSC: `93B12, 93C10`
- ACM: `I.2.9, J.7`

### Step 5: Preview and Submit

1. **Preview:** arXiv compiles paper and shows PDF
2. **Verify:**
   - All figures appear correctly
   - Cross-references resolved
   - Bibliography formatted properly
3. **Submit:** Click "Submit to arXiv"
4. **Moderation:** Wait 24-48 hours for admin review

---

## Post-Submission

### Confirmation Email

arXiv sends confirmation email with:
- **Submission ID:** `2025.12345` (year.number format)
- **Moderation status:** "Submitted for review"
- **Expected announcement:** Next business day, 8pm ET

### Track Status

1. Go to https://arxiv.org/user
2. Click "Submissions"
3. Check status:
   - **Submitted:** Awaiting moderation
   - **On Hold:** Requires revision (rare)
   - **Announced:** Live on arXiv

### Announcement

**When:**
- Papers announced daily at 8pm ET (midnight UTC)
- Submissions by 2pm ET announce same day

**arXiv ID:**
- Format: `YYMM.NNNNN` (e.g., `2511.12345`)
- Permanent identifier for citations

**Versions:**
- v1: Initial submission
- v2, v3, ...: Updates (allowed after announcement)

### Sharing

**arXiv URL:** `https://arxiv.org/abs/2511.12345`

**PDF URL:** `https://arxiv.org/pdf/2511.12345`

**Social Media:**
```
Excited to share our new preprint on arXiv!

"Sliding Mode Control with PSO Optimization for Double-Inverted Pendulum"
https://arxiv.org/abs/2511.12345

We present 7 SMC controllers with formal stability proofs and comprehensive benchmarks.

#ControlTheory #Robotics #Optimization
```

**ResearchGate/Academia.edu:**
- Upload PDF from arXiv
- Link to arXiv page
- Tag co-authors

**Twitter/X:**
- Share arXiv link
- Mention relevant accounts (@IEEEControl, @IFAC_TC, etc.)
- Use hashtags: #arXiv, #ControlTheory, #SMC, #PSO

---

## References

### Official Documentation

- **arXiv Help:** https://arxiv.org/help
- **Submit Help:** https://arxiv.org/help/submit
- **TeX Submission:** https://arxiv.org/help/submit_tex
- **Metadata:** https://arxiv.org/help/prep
- **Moderation:** https://arxiv.org/help/moderation

### Category Descriptions

- **cs.SY:** https://arxiv.org/archive/cs.SY
- **cs.RO:** https://arxiv.org/archive/cs.RO
- **math.OC:** https://arxiv.org/archive/math.OC

### LaTeX Resources

- **IEEEtran Class:** https://www.ctan.org/pkg/ieeetran
- **arXiv TeX Templates:** https://arxiv.org/help/submit_tex_templates
- **Overleaf Guide:** https://www.overleaf.com/learn

### Related Guides

- **Submission Checklist:** `docs/publication/SUBMISSION_CHECKLIST.md`
- **Citation Guide:** `docs/publication/CITATION_GUIDE.md`
- **GitHub Pages Guide:** `docs/publication/GITHUB_PAGES_GUIDE.md`

---

## Appendix: Example Submission

### Sample paper.tex Structure

```latex
\documentclass[conference]{IEEEtran}

\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{cite}
\usepackage{hyperref}

\title{Sliding Mode Control with PSO Optimization\\for Double-Inverted Pendulum: A Comprehensive Study}

\author{
  \IEEEauthorblockN{Your Name}
  \IEEEauthorblockA{Department of Control Engineering\\
    Your Institution\\
    Email: your.email@institution.edu}
}

\begin{document}

\maketitle

\begin{abstract}
This paper presents a comprehensive study of sliding mode control (SMC)
techniques applied to a double-inverted pendulum (DIP) system...
\end{abstract}

\section{Introduction}
\label{sec:intro}
The double-inverted pendulum is a benchmark control problem...

\section{Methodology}
\label{sec:method}
We implement seven SMC controllers...

\subsection{Classical SMC}
The classical sliding mode controller uses...

\begin{figure}[htbp]
\centering
\includegraphics[width=0.48\textwidth]{fig1_classical_smc.pdf}
\caption{Classical SMC performance}
\label{fig:classical}
\end{figure}

\section{Results}
\label{sec:results}
Comprehensive benchmarks show...

\section{Conclusion}
\label{sec:conclusion}
This study demonstrates...

\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
```

### Sample references.bib

```bibtex
@article{utkin1977,
  author={Utkin, V.I.},
  title={Variable structure systems with sliding modes},
  journal={IEEE Transactions on Automatic Control},
  year={1977},
  volume={22},
  number={2},
  pages={212--222},
  doi={10.1109/TAC.1977.1101446}
}

@article{kennedy1995,
  author={Kennedy, J. and Eberhart, R.},
  title={Particle swarm optimization},
  journal={Proceedings of IEEE International Conference on Neural Networks},
  year={1995},
  pages={1942--1948},
  doi={10.1109/ICNN.1995.488968}
}
```

---

**End of arXiv Submission Guide**

**Document Version:** 1.0
**Last Updated:** November 12, 2025
**Status:** OPERATIONAL
**Maintenance:** Update after first successful submission
