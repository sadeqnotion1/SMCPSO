# EP001: Physical System Description - Learning Module

## Overview

This learning module provides comprehensive coverage of the Double-Inverted Pendulum (DIP) physical system, consolidating three authoritative sources into one unified document.

---

## 📚 Available Formats

### Primary Learning Material

1. **Unified Markdown Module** (Recommended for web viewing)
   - File: `EP001_unified.md`
   - Size: 17 KB, 411 lines
   - Format: Comprehensive Markdown with LaTeX math
   - Best for: Web browsers, GitHub, Markdown editors
   - **Use this for**: Easy reading, quick reference, web viewing

2. **LaTeX Source** (For PDF generation)
   - File: `EP001_unified.tex`
   - Size: ~45 KB
   - Format: Academic LaTeX with MathJax-compatible math
   - Best for: PDF generation, academic publishing, print
   - **Compile with**: `pdflatex EP001_unified.tex` (requires TeX Live, MiKTeX, or MacTeX)
   - **Note**: PDF compilation requires LaTeX compiler not available in this environment

3. **Source Materials** (Original references)
   - `source/LT7_section_2.1.1.md` - LT-7 research paper section
   - `source/E003_slides.md` - E003 educational slides
   - `source/thesis_system_model.tex` - Thesis Chapter 2 LaTeX

---

## 🎓 Learning Objectives

By completing this module, you will be able to:

- ✅ Describe the DIP physical system structure and all components
- ✅ Explain the coordinate system and state vector definition
- ✅ Understand and apply the Euler-Lagrange derivation approach
- ✅ Identify physical constraints and parameter relationships
- ✅ Select appropriate plant model based on speed/accuracy tradeoffs
- ✅ Apply system model knowledge to control design problems

---

## 📖 Quick Start

### Option A: Web Viewing (Recommended)
1. Open `EP001_unified.md` in any Markdown viewer
2. Read sequentially from Section 1 to Section 13
3. Time: ~2 hours for comprehensive study

### Option B: PDF Generation (Requires LaTeX)
```bash
cd /mnt/d/Projects/main/academic/learning/ep001_physical_system_description
pdflatex EP001_unified.tex
bibtex EP001_unified
pdflatex EP001_unified.tex
pdflatex EP001_unified.tex
# Output: EP001_unified.pdf
```

### Option C: GitHub Viewing
- Upload `EP001_unified.md` to GitHub
- View with MathJax rendering enabled
- Perfect for browser-based learning

---

## 📑 Module Structure

1. **Introduction** - Overview and key takeaways
2. **What is a Plant Model?** - Definition and importance
3. **Physical System Description** - Components, schematic, constraints
4. **State-Space Representation** - State vector and control objectives
5. **Mathematical Formulation** - Euler-Lagrange derivation
6. **Energy Formulation** - Kinetic and potential energy
7. **Inertia Matrix M(q)** - Complete matrix elements
8. **Coriolis Matrix C(q,q̇)** - Velocity-dependent forces
9. **Gravity Vector G(q)** - Gravitational torques
10. **Nominal System Parameters** - Complete parameter table
11. **Linearization and Controllability** - Stability analysis
12. **Model Selection Guide** - When to use each model type
13. **Summary and Key Takeaways** - Review and practice exercises

---

## 🎯 Time Estimates

- **Quick Read** (Sections 1-4, 9, 13): 30-45 minutes
- **Comprehensive Study** (All sections): ~2 hours
- **Deep Technical** (All + exercises): 3+ hours

---

## 🔗 Related Modules

| Episode | Topic | Status |
|---------|-------|--------|
| EP001 | Physical System Description | ✅ Complete |
| EP002 | Sliding Surface Design | 📋 Planned |
| EP003 | Controller Formulations | 📋 Planned |
| EP004 | PSO Configuration | 📋 Planned |
| EP005 | Lyapunov Stability | 📋 Planned |

---

## 📝 Prerequisites

**Required:**
- Calculus (derivatives, partial derivatives, chain rule)
- Physics (Newton's laws, energy concepts)
- Linear algebra (matrices, vectors, rank, eigenvalues)

**Recommended:**
- Basic control theory (state-space, stability)
- Programming (Python/MATLAB for simulations)

---

## 🛠️ File Structure

```
academic/learning/ep001_physical_system_description/
├── README.md                         # This file
├── INDEX.md                          # Learning module index
├── EP001_unified.md                  # ✅ Primary learning material (Markdown)
├── EP001_unified.tex                 # 📄 LaTeX source (compile to PDF)
├── EP001_unified.aux                 # LaTeX auxiliary (after compilation)
├── EP001_unified.log                 # LaTeX log (after compilation)
├── EP001_unified.pdf                 # 📕 Compiled PDF (after compilation)
├── source/
│   ├── LT7_section_2.1.1.md          # LT-7 paper section
│   ├── E003_slides.md                # E003 educational slides
│   └── thesis_system_model.tex       # Thesis LaTeX source
├── outputs/                          # Generated materials (future)
└── references/                       # External references
```

---

## 📚 Source Material Credits

This unified module consolidates content from three authoritative sources:

1. **LT-7 Research Paper** (Section 2.1.1)
   - Professional academic formatting
   - Complete mathematical derivations
   - Submission-ready quality

2. **E003: Plant Models and Dynamics**
   - Educational slides with speaker notes
   - Beginner-friendly explanations
   - Pedagogical analogies

3. **Thesis Chapter 2: System Model**
   - Complete parameter tables
   - Linearization and controllability analysis
   - Academic report format

---

## 📄 PDF Compilation Instructions

The LaTeX source is provided for PDF generation. If you have a LaTeX compiler installed:

### Required Packages
- `amsmath`, `amssymb`, `amsthm`
- `geometry`, `graphicx`, `booktabs`
- `hyperref`, `xcolor`, `listings`
- `tikz` (for diagrams)

### Compilation Commands
```bash
# Standard compilation
pdflatex EP001_unified.tex
bibtex EP001_unified
pdflatex EP001_unified.tex
pdflatex EP001_unified.tex

# Or with biber (if using biblatex)
pdflatex EP001_unified.tex
biber EP001_unified
pdflatex EP001_unified.tex
pdflatex EP001_unified.tex
```

### Alternative: Overleaf
1. Go to [overleaf.com](https://overleaf.com)
2. Create new project → Upload → Upload `EP001_unified.tex`
3. Click "Recompile"
4. Download PDF

---

## 📞 Feedback and Contributions

For questions, corrections, or contributions:
- Refer to episode Q&A in `/academic/paper/presentations/episodes/E003_plant_models_and_dynamics/qa/`
- Check project documentation in `.ai_workspace/`
- Review AGENTS.md for repository conventions

---

## 📜 License

This module is part of the Double-Inverted Pendulum Control Project.
License details: See `academic/paper/README.md`

---

*Module created: 2026-04-01*  
*Consolidated from 3 independent sources into 1 comprehensive learning module*  
*LaTeX version available for PDF generation*
