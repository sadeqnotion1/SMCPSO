# DIP-SMC-PSO Comprehensive Presentation

**A Complete Technical Overview: From Foundational Theory to Production Infrastructure**

---

## Overview

This directory contains a **comprehensive academic presentation** covering every aspect of the DIP-SMC-PSO (Double-Inverted Pendulum Sliding Mode Control with PSO Optimization) project. The presentation is designed for:

- **PhD defense** preparation
- **Academic conference** presentations
- **Comprehensive technical documentation**
- **Educational resource** for understanding the complete project

**Scope:** ~400 slides across 24 sections, ~6-8 hours of presentation time
**Level:** PhD-level technical depth with self-contained explanations
**Format:** LaTeX Beamer presentation + detailed speaker scripts

---

## Workspace Organization (2026-02-24)

This folder now hosts multiple presentation channels and derivative formats:

- `slides/` - canonical LaTeX slide sources
- `speaker/` - canonical speaker script sources
- `episodes/` - episode-first content hub (`E###_slug` folders)
- `layers/` - audience-depth variants (`L1` to `L4`)
- `podcasts/` - podcast episode generation and outputs
- `beautiful_ai/` - Beautiful.ai-adapted materials
- `code_snippets/` - shared teaching/demo code
- `figures/` - shared visual assets

See `ORGANIZATION.md` for ownership and flow rules.
See `episodes/README.md` for episode-first structure and migration status.
See `EPISODE_TRACEABILITY_MAP.md` and `EPISODE_TRACEABILITY_MAP.csv` for
source-to-episode mapping from `slides/` and `speaker/`.

Bulk episode migration command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\migrate_all_episodes.ps1
```

Pre-commit hygiene check:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\audit_presentation_hygiene.ps1 -FailOnFindings
```

Cleanup generated artifacts (preview first):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_presentation_artifacts.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_presentation_artifacts.ps1 -Apply
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_presentation_artifacts.ps1 -Apply -IncludeReservedNames
```

---

## Contents

### Main Deliverables

| File | Description | Pages/Slides | Size |
|------|-------------|--------------|------|
| `comprehensive_project_presentation.tex` | Main Beamer presentation | ~400 slides | 5,353 lines |
| `speaker_scripts.tex` | Detailed lecture-style scripts | ~120 pages | Academic narrative |
| `references.bib` | Complete bibliography | 39 academic + 30+ software | BibTeX format |
| `beamer_config.tex` | Shared preamble and packages | Configuration | Reusable |

### Supporting Files

| Directory/File | Description |
|----------------|-------------|
| `code_snippets/` | Python code examples (5 files) |
| `figures/` | Diagrams, charts, screenshots (to be populated) |
| `compile.sh` | Linux/Mac build script |
| `compile.bat` | Windows build script |
| `build/` | Temporary LaTeX build files (auto-generated) |
| `output/` | Final PDF outputs (auto-generated) |

---

## Presentation Structure

### Part I: Foundations (Slides 1-80, ~90-120 minutes)

1. **Project Overview** (15 slides) -- What, why, unique contributions
2. **Control Theory Foundations** (20 slides) -- 7 controllers, SMC fundamentals, Lyapunov stability
3. **Plant Models & Dynamics** (15 slides) -- 3 model variants, equations of motion
4. **Optimization System** (15 slides) -- PSO algorithm, convergence analysis
5. **Simulation Engine** (15 slides) -- Core runner, vectorized computation, Numba acceleration

### Part II: Infrastructure (Slides 81-160, ~120-150 minutes)

6. **Analysis & Visualization** (15 slides) -- DIPAnimator, statistical tools, Monte Carlo
7. **Testing & QA** (20 slides) -- 11/11 test suites, coverage standards, thread safety
8. **Research Outputs** (20 slides) -- Phase 5 completion, 11 tasks, LT-7 paper
9. **Educational Materials** (20 slides) -- 125-hour beginner roadmap, NotebookLM podcasts
10. **Documentation System** (15 slides) -- Sphinx docs, 985 files, 11 navigation systems
11. **Configuration & Deployment** (10 slides) -- YAML validation, reproducibility

### Part III: Advanced Topics (Slides 161-260, ~120-150 minutes)

12. **HIL System** (15 slides) -- Hardware-in-the-loop architecture
13. **Monitoring Infrastructure** (15 slides) -- Latency tracking, weakly-hard constraints
14. **Development Infrastructure** (25 slides) -- Session continuity, checkpoint system
15. **Architectural Standards** (15 slides) -- Invariants, quality gates
16. **Attribution & Citations** (15 slides) -- 39 academic references, license compliance
17. **Memory & Performance** (15 slides) -- Weakref patterns, memory leak prevention

### Part IV: Professional Practice (Slides 261-340, ~90-120 minutes)

18. **Browser Automation & UI Testing** (15 slides) -- Puppeteer, WCAG 2.1 AA
19. **Workspace Organization** (15 slides) -- Three-category academic structure
20. **Version Control** (10 slides) -- Git workflows, automated tracking
21. **Future Work & Roadmap** (15 slides) -- Research directions, production readiness
22. **Key Statistics** (10 slides) -- Quantitative metrics
23. **Visual Diagrams** (15 slides) -- Architecture visualizations
24. **Lessons Learned** (15 slides) -- What worked, recommendations

### Appendix (Slides 341-380, ~30-45 minutes)

- Quick reference commands
- Complete bibliography (39 academic + 30+ software)
- Code repository structure walkthrough
- Contact information

---

## Compilation Instructions

### Prerequisites

You need a **LaTeX distribution** installed:

- **Linux/Mac:** TeX Live
  ```bash
  # Ubuntu/Debian
  sudo apt-get install texlive-full biber

  # macOS (Homebrew)
  brew install --cask mactex
  ```

- **Windows:** MiKTeX or TeX Live
  - Download from: https://miktex.org/ or https://tug.org/texlive/
  - Ensure `pdflatex` and `biber` are in your PATH

### Building the Presentation

#### Option 1: Using Build Scripts (Recommended)

**Linux/Mac:**
```bash
# Make script executable (first time only)
chmod +x compile.sh

# Compile presentation only
./compile.sh presentation

# Compile speaker scripts only
./compile.sh scripts

# Compile both (default)
./compile.sh all

# Clean build artifacts
./compile.sh clean
```

**Windows:**
```batch
REM Compile presentation only
compile.bat presentation

REM Compile speaker scripts only
compile.bat scripts

REM Compile both (default)
compile.bat all

REM Clean build artifacts
compile.bat clean
```

#### Option 2: Manual Compilation

```bash
# Compile presentation
pdflatex -output-directory=build comprehensive_project_presentation.tex
biber --input-directory=build --output-directory=build comprehensive_project_presentation
pdflatex -output-directory=build comprehensive_project_presentation.tex
pdflatex -output-directory=build comprehensive_project_presentation.tex

# Compile speaker scripts
pdflatex -output-directory=build speaker_scripts.tex
biber --input-directory=build --output-directory=build speaker_scripts
pdflatex -output-directory=build speaker_scripts.tex
pdflatex -output-directory=build speaker_scripts.tex
```

### Output Files

After compilation, find PDFs in the `output/` directory:

- `comprehensive_project_presentation.pdf` -- Main Beamer slides (~400 slides)
- `speaker_scripts.pdf` -- Detailed lecture scripts (~120 pages)

---

## Speaker Scripts Format

Each slide in the main presentation has a corresponding 5-10 minute detailed script covering:

1. **Context:** Why this topic matters, how it fits into the narrative
2. **Content:** Detailed technical explanation with equations, diagrams, code
3. **Connections:** Relationships to other sections, repository files, research tasks
4. **Critical Insights:** Key takeaways beyond surface-level understanding
5. **Anticipated Q&A:** Expected questions with comprehensive answers

**Example Script Structure:**

```latex
\slidetitle{Slide 10: Classical SMC: Control Law}
\speakertime{8-10}

\context{
We've established the sliding surface concept. Now we present the actual
control law—the equation that computes the force applied to the cart...
}

\content{
"Now let's see how we actually compute the control input from the sliding surface.
The most common form uses a boundary layer approximation:
\begin{equation}
u = -K \cdot \tanh\left(\frac{s}{\epsilon}\right)
\end{equation}
Let me break down each component..."
}

\connections{
This slide connects to:
- Section 4 (Optimization System): PSO tunes K and epsilon automatically
- Section 8 (Research Outputs): MT-6 boundary layer optimization research task...
}

\insights{
- The boundary layer epsilon is NOT a "hack"—it's a principled trade-off...
}

\qa{
Q: Why use tanh instead of sat (saturation function)?
A: Both work, but tanh is: 1) Differentiable everywhere...
}
```

---

## Code Snippets

The `code_snippets/` directory contains 5 standalone Python examples demonstrating key concepts:

| File | Description | Lines | Demonstrates |
|------|-------------|-------|--------------|
| `01_classical_smc_basic.py` | Basic classical SMC control law | ~50 | Sliding surface, boundary layer, saturation |
| `02_pso_optimization.py` | PSO gain tuning workflow | ~100 | Cost function, PSO setup, optimization loop |
| `03_simulation_runner.py` | Main simulation loop | ~80 | RK45 integration, closed-loop control |
| `04_factory_pattern.py` | Controller factory pattern | ~120 | Unified interface, registry pattern |
| `05_configuration_loading.py` | YAML config with Pydantic | ~150 | Type-safe validation, error handling |

All snippets are **runnable** (with minor placeholder adaptations) and **extensively commented** for educational purposes.

---

## Bibliography

The `references.bib` file contains **39 academic citations** + **30+ software dependencies**:

### Academic Citations by Category

- **SMC Foundational Works:** Utkin, Slotine, Edwards, Shtessel (8 references)
- **Super-Twisting Algorithm:** Levant, Moreno, Seeber (6 references)
- **Adaptive SMC:** Yang, Plestan, Roy, Krstic (4 references)
- **Chattering Reduction:** Burton, Sahamijoo (2 references)
- **PSO Foundations:** Kennedy, Clerc, Poli, Zhang, Freitas (6 references)
- **PSO for SMC Tuning:** Pham, Khan, Messina, Liu (4 references)
- **Numerical Methods:** Butcher, Dormand & Prince, Raichle (3 references)

### Software Dependencies

- **Core Scientific:** NumPy, SciPy, Matplotlib
- **Performance:** Numba (JIT compilation)
- **Optimization:** PySwarms
- **Validation:** Pydantic
- **Testing:** pytest
- **UI:** Streamlit

---

## Presentation Tips

### For PhD Defense

1. **Start with Part I (Foundations)** -- Establish theoretical rigor
2. **Highlight Part II Section 8 (Research Outputs)** -- Show validation work
3. **Be prepared for deep dives** -- Have LT-7 paper figures ready
4. **Emphasize novelty** -- PSO automation, 7-controller validation, educational materials

### For Conference Presentation

1. **Extract 20-30 key slides** from the comprehensive deck
2. **Focus on:** Problem statement → Novel contributions → Results → Impact
3. **Recommended subset:**
   - Slides 1-5 (Introduction)
   - Slides 10-15 (Classical SMC + STA)
   - Slides 60-70 (PSO optimization)
   - Slides 140-160 (Research outputs, MT-5, LT-7)
   - Slides 370-380 (Conclusions)

### For Technical Workshop

1. **Use Part I + Part II** as the core narrative
2. **Include live demos** from `code_snippets/`
3. **Show Streamlit UI** during Section 18 (Browser Automation)
4. **Provide GitHub repo link** early for hands-on exploration

---

## Customization

### Changing Theme/Colors

Edit `beamer_config.tex`:

```latex
% Change Beamer theme
\usetheme{Madrid}  % Options: Madrid, Berlin, Copenhagen, etc.

% Change color scheme
\definecolor{dipblue}{RGB}{0,102,204}  % Primary color
```

### Adding Slides

Insert new frames in `comprehensive_project_presentation.tex`:

```latex
\begin{frame}{Your New Slide Title}
    \textbf{Content goes here}

    \begin{itemize}
        \item Point 1
        \item Point 2
    \end{itemize}
\end{frame}
```

### Updating Speaker Scripts

Add corresponding script in `speaker_scripts.tex`:

```latex
\slidetitle{Your New Slide Title}
\speakertime{5-7}

\context{...}
\content{...}
\connections{...}
\insights{...}
\qa{...}
```

---

## Troubleshooting

### Common Errors

**Error: `! LaTeX Error: File 'beamerthemeMadrid.sty' not found.`**

**Solution:** Install complete LaTeX distribution (texlive-full on Linux, full MiKTeX/TeX Live on Windows)

---

**Error: `! Package biblatex Error: '\bibliographystyle' invalid.`**

**Solution:** Remove any `\bibliographystyle` commands (biblatex uses `\usepackage[style=...]{biblatex}` instead)

---

**Error: `! Undefined control sequence. \slidingsurf`**

**Solution:** Ensure you compile the main presentation file (not beamer_config.tex directly)

---

**Error: PDF not updated after recompilation**

**Solution:**
1. Close PDF viewer
2. Run `./compile.sh clean`
3. Recompile

---

### Performance Issues

**Slow compilation?**

- **Expected:** 2-3 minutes for 400 slides with bibliography + figures
- **Speed up:** Compile with `pdflatex -draftmode` for intermediate builds
- **Cache:** Subsequent compilations are faster (uses cached .aux files)

---

## Project Integration

This presentation integrates with the main DIP-SMC-PSO project:

### Repository Structure

```
dip-smc-pso/
├── academic/paper/presentations/          [THIS DIRECTORY]
│   ├── comprehensive_project_presentation.tex
│   ├── speaker_scripts.tex
│   ├── references.bib
│   └── code_snippets/
├── src/                                   [SOURCE CODE]
├── docs/                                  [SPHINX DOCUMENTATION]
├── academic/paper/experiments/            [RESEARCH DATA]
└── .ai_workspace/                         [AI GUIDES]
```

### Cross-References

The presentation references specific files/modules:

- **Controllers:** `src/controllers/smc/classic_smc.py:45-67`
- **PSO:** `src/optimizer/pso_optimizer.py`
- **Research:** `academic/paper/experiments/comparative/MT-5_comprehensive_benchmark/`
- **Documentation:** `docs/NAVIGATION.md`, `.ai_workspace/guides/`

---

## License & Attribution

- **Presentation content:** Original work by Sadegh Naderi
- **Academic references:** 39 citations (see `references.bib`)
- **Software dependencies:** 30+ packages with proper attribution
- **Project license:** Inherits from main repository (MIT or specified license)

**Cite this work:**

```bibtex
@misc{naderi2025dipsmc,
  author = {Naderi, Sadegh},
  title = {Double-Inverted Pendulum Sliding Mode Control with PSO Optimization: A Comprehensive Technical Overview},
  year = {2025},
  howpublished = {\url{https://github.com/theSadeQ/dip-smc-pso}},
  note = {Comprehensive presentation (400 slides)}
}
```

---

## Contact & Contributions

**Repository:** https://github.com/theSadeQ/dip-smc-pso.git
**Author:** Sadegh Naderi
**Issues:** Report presentation errors via GitHub issues
**Contributions:** Pull requests welcome for typo fixes, clarifications

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-22 | Initial comprehensive presentation (400 slides, 24 sections) |

---

**Last updated:** January 22, 2025
**Total presentation time:** 6-8 hours
**Slides:** ~400 across 24 sections
**Speaker scripts:** ~120 pages of detailed academic narratives
