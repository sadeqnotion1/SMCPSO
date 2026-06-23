# Thesis Directory - Professional Structure

## Overview

This directory contains the LaTeX source and documentation for the **Sliding Mode Control of Double-Inverted Pendulum with PSO Optimization** thesis/project report.

**Last Restructured**: December 29, 2025
**Status**: Active development
**Output**: 20-30 page project report (article format)

---

## Directory Structure

```
thesis/
├── main.tex                # Primary LaTeX entry point
├── main.pdf               # Compiled PDF output (692 KB)
├── preamble.tex           # LaTeX packages and custom commands
├── metadata.tex           # Document metadata (title, author, date)
│
├── source/                # LaTeX source files (organized by type)
│   ├── front/            # Front matter (abstract, acknowledgments, nomenclature)
│   ├── report/           # Report sections (introduction, methods, results, conclusion)
│   ├── chapters/         # Full thesis chapters (15 placeholders for future expansion)
│   └── appendices/       # Appendix content (proofs, code, data, config)
│
├── bibliography/         # BibTeX files
│   └── main.bib         # Primary bibliography database
│
├── figures/              # Figures organized by category
│   ├── architecture/    # System architecture diagrams (empty, reserved)
│   ├── benchmarks/      # Benchmark comparison plots (8 PDFs)
│   ├── convergence/     # PSO convergence plots (2 PDFs)
│   ├── lyapunov/        # Lyapunov analysis plots (empty, reserved)
│   └── schematics/      # System schematics (empty, reserved)
│
├── tables/               # Tables organized by category
│   ├── benchmarks/      # Benchmark results tables (5 .tex files)
│   ├── comparisons/     # Controller comparison tables (empty, reserved)
│   └── parameters/      # System parameter tables (empty, reserved)
│
├── references/           # Reference materials (96 MB)
│   ├── articles/        # Journal articles (12 MB)
│   ├── books/           # Control theory textbooks (43 MB)
│   ├── manuals/         # Technical manuals (3.5 MB)
│   ├── proceedings/     # Conference proceedings (629 KB)
│   ├── manually_downloaded/ # Manually acquired PDFs (38 MB)
│   ├── metadata/        # BibTeX and citation mappings (52 KB)
│   ├── archive/         # Archived documentation
│   └── README.md        # Reference management guide
│
├── scripts/              # Build and automation scripts
│   ├── build.sh         # Unix/Linux build script
│   ├── build.bat        # Windows build script
│   └── clean.sh         # Cleanup script for build artifacts
│
└── archive/              # Archived materials (not actively used)
    ├── old_versions/     # Previous thesis versions (backups)
    ├── build_artifacts/  # LaTeX build outputs (.aux, .log, .toc, etc.)
    ├── report_backups/   # Extracted/backup report sections
    └── empty_dirs/       # Documentation of removed empty directories
```

---

## Quick Start

### Compile the Thesis

**Using Makefile** (Recommended):
```bash
make                 # Compile PDF (pdflatex + bibtex)
make clean           # Remove build artifacts
make view            # Compile and open PDF
```

**Manual Compilation**:
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

**Windows**:
```cmd
scripts\build.bat
```

---

## File Descriptions

### Root Files

| File | Description | Size |
|------|-------------|------|
| `main.tex` | Primary LaTeX document | 2.7 KB |
| `main.pdf` | Compiled PDF output | 692 KB |
| `preamble.tex` | LaTeX preamble (packages, commands) | 5.2 KB |
| `metadata.tex` | Document metadata | 1.0 KB |

### Source Files (`source/`)

- **`front/`**: Front matter components
  - `abstract_report.tex` - Short abstract for project report
  - `abstract.tex` - Full thesis abstract
  - `acknowledgments.tex` - Acknowledgments section
  - `nomenclature.tex` - Nomenclature/symbols list
  - `title_page.tex` - Custom title page

- **`report/`**: Report sections (active for 20-30 page report)
  - `section1_introduction.tex` - Introduction
  - `section2_system_model.tex` - System model & problem formulation
  - `section3_controllers.tex` - Controller design
  - `section4_pso.tex` - PSO optimization
  - `section5_results.tex` - Simulation results
  - `section6_conclusion.tex` - Conclusion
  - `appendix_code.tex` - Code appendix
  - `appendix_b_lyapunov.tex` - Lyapunov analysis appendix

- **`chapters/`**: Full thesis chapters (15 placeholders)
  - `chapter01_placeholder.tex` through `chapter15_placeholder.tex`
  - Future expansion: convert report sections to full thesis chapters

- **`appendices/`**: Full thesis appendices
  - `appendix_a_proofs.tex` - Mathematical proofs
  - `appendix_b_code.tex` - Code listings
  - `appendix_c_data.tex` - Data tables
  - `appendix_d_config.tex` - Configuration details

---

## Build System

### Makefile Targets

```bash
make              # Compile PDF (full build with bibtex)
make fast         # Quick compile (no bibtex, single pass)
make clean        # Remove build artifacts (.aux, .log, etc.)
make cleanall     # Remove all generated files (including PDF)
make view         # Compile and open PDF in default viewer
make count        # Word count (texcount)
make spell        # Spell check (aspell)
```

### Build Artifacts

All build artifacts are automatically ignored by git (.gitignore) and stored in `archive/build_artifacts/`:
- `.aux` - Auxiliary files
- `.log` - Compilation logs
- `.toc` - Table of contents
- `.lof` - List of figures
- `.lot` - List of tables
- `.bbl`, `.blg` - Bibliography files
- `.out` - Hyperref output
- `.nlo` - Nomenclature output

---

## Version Control

### Current Branch
- **Branch**: `thesis-cleanup-2025-12-29`
- **Purpose**: Professional restructuring of thesis/ directory
- **Changes**: Organized source files, archived old versions, created professional structure

### Gitignore Rules
All LaTeX build artifacts are ignored per CLAUDE.md Section 14:
```gitignore
academic/paper/thesis/*.aux
academic/paper/thesis/*.log
academic/paper/thesis/*.toc
# ... (15 patterns total)
```

### Commit Messages
Follow project conventions:
```bash
git commit -m "docs(thesis): Brief description

[AI] Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## References Directory

**Size**: 96 MB
**Purpose**: Research papers, theses, books for citation and reference

**Organization**:
- `papers/` - Journal articles and conference papers
- `theses/` - Related master's/PhD theses
- `books/` - Control theory textbooks
- `web/` - Online resources and tutorials

**Usage**:
- Do NOT commit large PDFs to git (use .gitignore or git-lfs)
- Keep local for reference during writing
- Cite in `bibliography/main.bib`

---

## Archive Directory

**Purpose**: Preserve historical work without cluttering active workspace

**Contents**:
- `old_versions/` - Previous thesis versions (main_thesis_backup.tex)
- `build_artifacts/` - LaTeX build outputs (28 files, ignored by git)
- `report_backups/` - Extracted report sections from earlier iterations
- `empty_dirs/` - Documentation of removed empty directories

**Policy**: Never delete archived files; append date suffixes for new archives

---

## Workspace Standards

### Root File Limits
**Target**: ≤12 visible files at thesis/ root
**Current**: 13 visible items (6 files + 7 directories)
- Files: main.tex, main.pdf, preamble.tex, metadata.tex, Makefile, README.md
- Directories: source/, bibliography/, figures/, tables/, references/, scripts/, archive/

### Cleanup Policy
After compilation, build artifacts are automatically cleaned:
```bash
make clean     # Automatic cleanup via Makefile (recommended)
# Build artifacts are NOT tracked by git (.gitignore rules)
# Old artifacts preserved in archive/build_artifacts/ for reference
```

**Current Status**: All build artifacts moved to archive/ (Dec 29, 2025)

### Professional Standards (CLAUDE.md Section 14)
- [OK] Source files organized in subdirectories
- [OK] Build artifacts archived and gitignored
- [OK] README.md provides complete documentation
- [OK] Makefile automates common tasks
- [OK] Clean root directory (≤12 files)

---

## Status & Roadmap

### Current Status
- **Format**: 20-30 page project report (article class)
- **Sections**: 6 sections + 2 appendices
- **Compilation**: Working, generates 692 KB PDF
- **Structure**: Professional, organized, git-friendly

### Production Readiness

**Current Status**: 78/100 (NEAR SUBMISSION-READY)
**Target**: 100/100 (SUBMISSION-READY by January 24, 2025)

**Planning Documents**:
- [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md) - Detailed 6-phase plan (29 hours)
- [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md) - Quick reference checklist

**Key Gaps**:
1. Missing architecture/schematic figures (4 figures, 8 hours)
2. Missing parameter tables (3 tables, 4 hours)
3. Bibliography expansion needed (15 citations, 3 hours)
4. Proofreading and quality verification (6 hours)
5. External review and feedback (8 hours)

**See**: Production readiness analysis in commit message (Dec 29, 2025)

### Future Expansion
1. **Thesis Mode**: Switch from article to report/book class
2. **Chapter Expansion**: Convert report sections to full chapters (15 placeholders ready)
3. **Additional Appendices**: Expand appendix_a through appendix_d
4. **Figures/Tables**: Populate empty subdirectories with generated plots
5. **Bibliography**: Expand main.bib with additional references

---

## Troubleshooting

### Compilation Errors
```bash
# Check log file
cat main.log | grep -i "error"

# Clean and rebuild
make cleanall && make

# Manual troubleshooting
pdflatex main.tex 2>&1 | tee compile.log
```

### Missing References
```bash
# Ensure bibliography exists
ls bibliography/main.bib

# Run bibtex manually
bibtex main
```

### Path Issues
If LaTeX can't find files:
- Verify `\input{}` paths in main.tex match directory structure
- Check that `source/` subdirectories exist
- Ensure file extensions are correct (.tex)

---

## Contact & Maintenance

**Project**: dip-smc-pso
**Repository**: https://github.com/theSadeQ/dip-smc-pso.git
**Documentation**: See `docs/` and `.ai_workspace/guides/`
**Maintenance Mode**: Active development (Phase 5 - Research)

For questions or issues, refer to project documentation or raise an issue on GitHub.
