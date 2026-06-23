# Makefile for Thesis Compilation
# Double-Inverted Pendulum SMC Thesis
# Last Updated: December 29, 2025

# Configuration
MAIN = main
TEX = pdflatex
BIB = bibtex
VIEWER = start # Windows default (use 'open' on macOS, 'xdg-open' on Linux)

# Directories
SOURCE_DIR = source
ARCHIVE_DIR = archive/build_artifacts
FIGURES_DIR = figures
TABLES_DIR = tables

# Build artifacts
AUX_FILES = *.aux *.log *.toc *.lof *.lot *.nlo *.out *.bbl *.blg *.fdb_latexmk *.fls *.synctex.gz
CHAPTER_AUX = $(SOURCE_DIR)/chapters/*.aux
APPENDIX_AUX = $(SOURCE_DIR)/appendices/*.aux

# Default target: full build
.PHONY: all
all: $(MAIN).pdf

# Full compilation with bibliography
$(MAIN).pdf: $(MAIN).tex
	@echo "[INFO] Starting full compilation (pdflatex + bibtex + pdflatex x2)..."
	$(TEX) $(MAIN).tex
	$(BIB) $(MAIN)
	$(TEX) $(MAIN).tex
	$(TEX) $(MAIN).tex
	@echo "[OK] Compilation complete: $(MAIN).pdf"

# Fast compilation (single pass, no bibtex)
.PHONY: fast
fast:
	@echo "[INFO] Fast compilation (single pass, no bibtex)..."
	$(TEX) $(MAIN).tex
	@echo "[OK] Fast compilation complete: $(MAIN).pdf"

# Clean build artifacts (keep PDF)
.PHONY: clean
clean:
	@echo "[INFO] Cleaning build artifacts..."
	-rm -f $(AUX_FILES)
	-rm -f $(CHAPTER_AUX)
	-rm -f $(APPENDIX_AUX)
	-rm -f pdflatex_output.txt
	@echo "[OK] Build artifacts cleaned"

# Archive build artifacts before cleaning
.PHONY: archive-artifacts
archive-artifacts:
	@echo "[INFO] Archiving build artifacts to $(ARCHIVE_DIR)..."
	@mkdir -p $(ARCHIVE_DIR)
	-mv -f $(AUX_FILES) $(ARCHIVE_DIR)/ 2>/dev/null || true
	-mv -f $(SOURCE_DIR)/chapters/*.aux $(ARCHIVE_DIR)/ 2>/dev/null || true
	-mv -f $(SOURCE_DIR)/appendices/*.aux $(ARCHIVE_DIR)/ 2>/dev/null || true
	@echo "[OK] Artifacts archived"

# Clean everything (including PDF)
.PHONY: cleanall
cleanall: clean
	@echo "[INFO] Removing PDF output..."
	-rm -f $(MAIN).pdf
	@echo "[OK] All generated files removed"

# Compile and open PDF
.PHONY: view
view: all
	@echo "[INFO] Opening $(MAIN).pdf..."
	$(VIEWER) $(MAIN).pdf

# Word count (requires texcount)
.PHONY: count
count:
	@echo "[INFO] Counting words (requires texcount)..."
	@if command -v texcount > /dev/null; then \
		texcount -inc -total $(MAIN).tex; \
	else \
		echo "[ERROR] texcount not found. Install with: tlmgr install texcount"; \
	fi

# Spell check (requires aspell)
.PHONY: spell
spell:
	@echo "[INFO] Spell checking (requires aspell)..."
	@if command -v aspell > /dev/null; then \
		aspell --mode=tex --lang=en check $(MAIN).tex; \
	else \
		echo "[ERROR] aspell not found. Install with package manager"; \
	fi

# Validate structure
.PHONY: validate
validate:
	@echo "[INFO] Validating directory structure..."
	@test -d $(SOURCE_DIR) || (echo "[ERROR] Missing $(SOURCE_DIR)/" && exit 1)
	@test -d $(FIGURES_DIR) || (echo "[ERROR] Missing $(FIGURES_DIR)/" && exit 1)
	@test -d $(TABLES_DIR) || (echo "[ERROR] Missing $(TABLES_DIR)/" && exit 1)
	@test -f $(MAIN).tex || (echo "[ERROR] Missing $(MAIN).tex" && exit 1)
	@test -f preamble.tex || (echo "[ERROR] Missing preamble.tex" && exit 1)
	@test -f metadata.tex || (echo "[ERROR] Missing metadata.tex" && exit 1)
	@echo "[OK] Directory structure validated"

# Help target
.PHONY: help
help:
	@echo "Thesis Makefile - Available Targets:"
	@echo ""
	@echo "  make               - Full compilation (pdflatex + bibtex + pdflatex x2)"
	@echo "  make fast          - Quick compilation (single pass, no bibtex)"
	@echo "  make clean         - Remove build artifacts (keep PDF)"
	@echo "  make cleanall      - Remove all generated files (including PDF)"
	@echo "  make archive       - Archive build artifacts to $(ARCHIVE_DIR)/"
	@echo "  make view          - Compile and open PDF"
	@echo "  make count         - Word count (requires texcount)"
	@echo "  make spell         - Spell check (requires aspell)"
	@echo "  make validate      - Validate directory structure"
	@echo "  make help          - Show this help message"
	@echo ""
	@echo "Quick Examples:"
	@echo "  make && make clean        - Compile and clean artifacts"
	@echo "  make view                 - Compile and view PDF"
	@echo "  make archive && make clean - Archive then clean"

# Continuous compilation (requires latexmk)
.PHONY: watch
watch:
	@echo "[INFO] Starting continuous compilation (requires latexmk)..."
	@if command -v latexmk > /dev/null; then \
		latexmk -pdf -pvc $(MAIN).tex; \
	else \
		echo "[ERROR] latexmk not found. Install with: tlmgr install latexmk"; \
	fi
