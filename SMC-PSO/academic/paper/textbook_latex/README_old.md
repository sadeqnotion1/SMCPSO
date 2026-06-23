# SMC Textbook - LaTeX Source Files

## Directory Structure

```
textbook_latex/
├── source/               # LaTeX source files
│   ├── chapters/        # Chapter .tex files (ch01_*.tex, ch02_*.tex, ...)
│   ├── appendices/      # Appendix .tex files (appendix_*.tex)
│   └── front/           # Front matter (abstract, preface, acknowledgments)
├── figures/             # All figures (PNG, PDF, generated plots)
├── tables/              # Standalone table files
├── bibliography/        # BibTeX files (main.bib)
├── build/               # Compilation outputs (PDF, aux, log, etc.)
├── scripts/             # Helper scripts (figure generation, build automation)
├── main.tex            # Main document file
├── preamble.tex        # Package imports and custom commands
└── metadata.tex        # Title, author, date

## Planning Documents

See `../textbook/` for:
- **TEXTBOOK_PLAN.json**: Complete chapter structure, agent orchestration plan
- **DEEP_THINKING_ANALYSIS.md**: 10-layer pedagogical analysis
- **README.md**: User-friendly overview and implementation guide

## Build Instructions

```bash
# Full 3-pass build (for bibliography and cross-references)
cd academic/paper/textbook_latex
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Output: build/main.pdf
```

## Current Status

- [OK] Folder structure created
- [PENDING] Preamble extension (minted, tcolorbox, algorithm2e)
- [PENDING] Chapter LaTeX files (12 chapters)
- [PENDING] Algorithm pseudocode extraction (30+ algorithms)
- [PENDING] Figure integration (50+ figures)
- [PENDING] Exercise creation (120+ exercises with solutions)

## Agent Orchestration

**7 Specialized Agents** working in parallel:

1. **Theory Extraction Agent**: Convert .md docs → LaTeX chapters (Chapters 1-4)
2. **Algorithm Conversion Agent**: Python → LaTeX pseudocode (30+ algorithms)
3. **Figure Curator Agent**: Organize and caption 50+ figures
4. **Exercise Designer Agent**: Create 120+ exercises with solutions
5. **Benchmarking Agent**: Format experimental results (Chapter 8)
6. **Software Chapter Agent**: Document architecture and usage (Chapter 9)
7. **Integration Agent**: Consolidate all outputs, ensure consistency

**Timeline**: 7-8 days with parallel execution

## Next Steps

1. Launch Agent 1 (Theory Extraction) → Chapters 1-4 LaTeX
2. Launch Agent 2 (Algorithm Conversion) → 30+ algorithm blocks
3. Launch Agent 3 (Figure Curator) → 50+ captioned figures
4. Launch Agent 4 (Exercise Designer) → 120+ exercises
5. Launch Agent 5 (Benchmarking) → Chapter 8 results
6. Launch Agent 6 (Software) → Chapter 9 documentation
7. Agent 7 integrates all outputs → compile → verify

---

**See**: `../textbook/TEXTBOOK_PLAN.json` for complete specification
