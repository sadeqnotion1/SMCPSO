#!/usr/bin/env bash
# ==============================================================================
# arXiv Submission Workflow Automation
# ==============================================================================
# Purpose: Automate LaTeX compilation, validation, and tarball creation for
#          arXiv submission of the DIP-SMC-PSO research paper (LT-7 v2.1)
#
# Usage:
#   bash scripts/publication/arxiv_submit.sh [options]
#
# Options:
#   --dry-run      : Validate without creating tarball
#   --skip-compile : Skip LaTeX compilation (use if already compiled)
#   --help         : Show this help message
#
# Requirements:
#   - pdflatex, bibtex (TeX Live or MiKTeX)
#   - Paper source: .artifacts/thesis/paper.tex
#   - Bibliography: .artifacts/thesis/references.bib
#   - Figures: .artifacts/thesis/figures/ (14 PNG/PDF files)
#
# Output:
#   - arxiv_submission.tar.gz (LaTeX tarball, <10MB)
#   - arxiv_metadata.json (submission metadata)
#   - arxiv_submission.log (compilation log)
#
# Exit Codes:
#   0 - Success
#   1 - LaTeX compilation failed
#   2 - Missing required files
#   3 - Tarball size exceeds 10MB
#   4 - Validation failed
#
# Author: Claude Code (Agent 1 - Publication Infrastructure Specialist)
# Date: November 12, 2025
# Version: 1.0
# ==============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# ==============================================================================
# Configuration
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PAPER_DIR="$PROJECT_ROOT/.artifacts/thesis"
STAGING_DIR="/tmp/arxiv_submission_$$"  # Use PID for uniqueness
OUTPUT_TARBALL="arxiv_submission.tar.gz"
LOG_FILE="$PROJECT_ROOT/.artifacts/arxiv_submission.log"
METADATA_FILE="$PROJECT_ROOT/scripts/publication/arxiv_metadata.json"

# arXiv constraints
MAX_TARBALL_SIZE_MB=10
REQUIRED_FIGURES=14

# Parse command-line arguments
DRY_RUN=false
SKIP_COMPILE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-compile)
      SKIP_COMPILE=true
      shift
      ;;
    --help)
      grep "^#" "$0" | grep -v "#!/" | sed 's/^# //' | sed 's/^#//'
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown option: $1"
      echo "Run with --help for usage information"
      exit 1
      ;;
  esac
done

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() {
  echo "[INFO] $1" | tee -a "$LOG_FILE"
}

log_error() {
  echo "[ERROR] $1" | tee -a "$LOG_FILE" >&2
}

log_ok() {
  echo "[OK] $1" | tee -a "$LOG_FILE"
}

check_dependency() {
  if ! command -v "$1" &> /dev/null; then
    log_error "$1 not found. Please install TeX Live or MiKTeX"
    exit 2
  fi
}

# ==============================================================================
# Pre-Flight Checks
# ==============================================================================

log_info "Starting arXiv submission workflow ($(date))"
log_info "Project root: $PROJECT_ROOT"
log_info "Paper directory: $PAPER_DIR"

# Check dependencies
log_info "Checking dependencies..."
check_dependency pdflatex
check_dependency bibtex
log_ok "All dependencies found"

# Check if paper directory exists
if [[ ! -d "$PAPER_DIR" ]]; then
  log_error "Paper directory not found: $PAPER_DIR"
  log_info "Creating paper directory structure..."
  mkdir -p "$PAPER_DIR/figures"

  log_info "Template structure created. Please add:"
  log_info "  - paper.tex (LaTeX source)"
  log_info "  - references.bib (bibliography)"
  log_info "  - figures/*.{png,pdf} (14 figures)"
  exit 2
fi

# Check for required files
log_info "Validating paper directory structure..."

if [[ ! -f "$PAPER_DIR/paper.tex" ]]; then
  log_error "Missing paper.tex in $PAPER_DIR"
  log_info "Please create paper.tex from LT-7 v2.1 research paper"
  exit 2
fi

if [[ ! -f "$PAPER_DIR/references.bib" ]]; then
  log_error "Missing references.bib in $PAPER_DIR"
  log_info "Please create references.bib with bibliography entries"
  exit 2
fi

if [[ ! -d "$PAPER_DIR/figures" ]]; then
  log_error "Missing figures directory in $PAPER_DIR"
  mkdir -p "$PAPER_DIR/figures"
  log_info "Created figures directory. Please add 14 figures"
  exit 2
fi

# Count figures
FIGURE_COUNT=$(find "$PAPER_DIR/figures" -type f \( -name "*.png" -o -name "*.pdf" \) 2>/dev/null | wc -l)
log_info "Found $FIGURE_COUNT figures (expected: $REQUIRED_FIGURES)"

if [[ $FIGURE_COUNT -lt $REQUIRED_FIGURES ]]; then
  log_error "Insufficient figures: $FIGURE_COUNT < $REQUIRED_FIGURES"
  log_info "Please add missing figures to $PAPER_DIR/figures/"
  exit 2
fi

log_ok "Paper directory structure validated"

# ==============================================================================
# LaTeX Compilation
# ==============================================================================

if [[ "$SKIP_COMPILE" == true ]]; then
  log_info "Skipping LaTeX compilation (--skip-compile flag)"
else
  log_info "Compiling LaTeX document (3-pass + bibtex)..."

  cd "$PAPER_DIR"

  # First pass: Generate aux file
  log_info "Pass 1: pdflatex (initial)"
  if ! pdflatex -interaction=nonstopmode -halt-on-error paper.tex >> "$LOG_FILE" 2>&1; then
    log_error "LaTeX compilation failed (pass 1)"
    log_info "See $LOG_FILE for details"
    exit 1
  fi

  # Generate bibliography
  log_info "Running bibtex..."
  if ! bibtex paper >> "$LOG_FILE" 2>&1; then
    log_error "BibTeX compilation failed"
    log_info "See $LOG_FILE for details"
    exit 1
  fi

  # Second pass: Resolve citations
  log_info "Pass 2: pdflatex (resolve citations)"
  if ! pdflatex -interaction=nonstopmode -halt-on-error paper.tex >> "$LOG_FILE" 2>&1; then
    log_error "LaTeX compilation failed (pass 2)"
    log_info "See $LOG_FILE for details"
    exit 1
  fi

  # Third pass: Finalize
  log_info "Pass 3: pdflatex (finalize)"
  if ! pdflatex -interaction=nonstopmode -halt-on-error paper.tex >> "$LOG_FILE" 2>&1; then
    log_error "LaTeX compilation failed (pass 3)"
    log_info "See $LOG_FILE for details"
    exit 1
  fi

  cd "$PROJECT_ROOT"

  log_ok "LaTeX compilation successful"

  # Check for missing references
  if grep -q "Warning.*undefined" "$LOG_FILE"; then
    log_error "Undefined references detected"
    grep "Warning.*undefined" "$LOG_FILE" | head -10
    log_info "See $LOG_FILE for complete list"
    exit 4
  fi

  log_ok "No undefined references"
fi

# ==============================================================================
# Tarball Creation
# ==============================================================================

if [[ "$DRY_RUN" == true ]]; then
  log_info "Dry-run mode: Skipping tarball creation"
  log_ok "Validation complete (dry-run)"
  exit 0
fi

log_info "Creating staging directory: $STAGING_DIR"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

# Copy required files to staging
log_info "Copying files to staging directory..."

cp "$PAPER_DIR/paper.tex" "$STAGING_DIR/"
cp "$PAPER_DIR/references.bib" "$STAGING_DIR/"

# Copy figures
if ls "$PAPER_DIR/figures"/*.png 1> /dev/null 2>&1; then
  cp "$PAPER_DIR/figures"/*.png "$STAGING_DIR/"
fi
if ls "$PAPER_DIR/figures"/*.pdf 1> /dev/null 2>&1; then
  cp "$PAPER_DIR/figures"/*.pdf "$STAGING_DIR/"
fi

# Copy LaTeX class file if present (IEEEtran.cls)
if [[ -f "$PAPER_DIR/IEEEtran.cls" ]]; then
  log_info "Including IEEEtran.cls"
  cp "$PAPER_DIR/IEEEtran.cls" "$STAGING_DIR/"
fi

# Copy bibliography style if present
if [[ -f "$PAPER_DIR/IEEEtran.bst" ]]; then
  log_info "Including IEEEtran.bst"
  cp "$PAPER_DIR/IEEEtran.bst" "$STAGING_DIR/"
fi

log_ok "Files copied to staging directory"

# Create tarball
log_info "Creating tarball: $OUTPUT_TARBALL"
cd "$STAGING_DIR"
tar -czf "$OUTPUT_TARBALL" * >> "$LOG_FILE" 2>&1

# Move tarball to paper directory
mv "$OUTPUT_TARBALL" "$PAPER_DIR/"
cd "$PROJECT_ROOT"

log_ok "Tarball created: $PAPER_DIR/$OUTPUT_TARBALL"

# ==============================================================================
# Tarball Validation
# ==============================================================================

log_info "Validating tarball..."

# Check size
TARBALL_SIZE_MB=$(du -m "$PAPER_DIR/$OUTPUT_TARBALL" | cut -f1)
log_info "Tarball size: ${TARBALL_SIZE_MB}MB (limit: ${MAX_TARBALL_SIZE_MB}MB)"

if [[ $TARBALL_SIZE_MB -gt $MAX_TARBALL_SIZE_MB ]]; then
  log_error "Tarball exceeds arXiv size limit: ${TARBALL_SIZE_MB}MB > ${MAX_TARBALL_SIZE_MB}MB"
  log_info "Consider compressing figures or removing unnecessary files"
  exit 3
fi

log_ok "Tarball size within limit"

# List tarball contents
log_info "Tarball contents (first 20 files):"
tar -tzf "$PAPER_DIR/$OUTPUT_TARBALL" | head -20 | tee -a "$LOG_FILE"

# Count files in tarball
FILE_COUNT=$(tar -tzf "$PAPER_DIR/$OUTPUT_TARBALL" | wc -l)
log_info "Total files in tarball: $FILE_COUNT"

log_ok "Tarball validation complete"

# ==============================================================================
# Metadata Generation
# ==============================================================================

log_info "Generating arXiv metadata..."

# Extract title and abstract from LaTeX (basic extraction)
TITLE=$(grep "\\\\title{" "$PAPER_DIR/paper.tex" | head -1 | sed 's/.*\\title{\(.*\)}.*/\1/' || echo "DIP-SMC-PSO Research Paper")
ABSTRACT=$(grep -A 20 "\\\\begin{abstract}" "$PAPER_DIR/paper.tex" | grep -B 20 "\\\\end{abstract}" | sed '/\\begin{abstract}/d' | sed '/\\end{abstract}/d' | tr '\n' ' ' || echo "Research paper on double-inverted pendulum control using sliding mode control with PSO optimization")

# Trim whitespace
TITLE=$(echo "$TITLE" | xargs)
ABSTRACT=$(echo "$ABSTRACT" | xargs)

# Create metadata JSON
cat > "$METADATA_FILE" <<EOF
{
  "title": "$TITLE",
  "abstract": "$ABSTRACT",
  "authors": [
    {
      "name": "Your Name",
      "affiliation": "Your Institution",
      "email": "your.email@institution.edu"
    }
  ],
  "categories": [
    "cs.SY",
    "cs.RO",
    "math.OC"
  ],
  "comments": "Submitted to IEEE Conference on Decision and Control (CDC) or IFAC World Congress",
  "msc_class": "93B12, 93C10",
  "acm_class": "I.2.9, J.7",
  "journal_ref": null,
  "doi": null,
  "report_no": null,
  "license": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
  "submission_notes": [
    "Generated by arXiv submission workflow automation",
    "Tarball size: ${TARBALL_SIZE_MB}MB",
    "Figure count: $FIGURE_COUNT",
    "LaTeX engine: pdflatex",
    "Date: $(date -u +%Y-%m-%d)"
  ]
}
EOF

log_ok "Metadata generated: $METADATA_FILE"

# ==============================================================================
# Cleanup
# ==============================================================================

log_info "Cleaning up staging directory..."
rm -rf "$STAGING_DIR"
log_ok "Cleanup complete"

# ==============================================================================
# Success Summary
# ==============================================================================

echo ""
echo "=============================================================================="
echo " arXiv Submission Workflow Complete"
echo "=============================================================================="
echo ""
echo "  Output Files:"
echo "    - Tarball:  $PAPER_DIR/$OUTPUT_TARBALL"
echo "    - Metadata: $METADATA_FILE"
echo "    - Log:      $LOG_FILE"
echo ""
echo "  Tarball Details:"
echo "    - Size:     ${TARBALL_SIZE_MB}MB (limit: ${MAX_TARBALL_SIZE_MB}MB)"
echo "    - Files:    $FILE_COUNT"
echo "    - Figures:  $FIGURE_COUNT"
echo ""
echo "  Next Steps:"
echo "    1. Review tarball contents: tar -tzf $PAPER_DIR/$OUTPUT_TARBALL"
echo "    2. Update metadata: Edit $METADATA_FILE"
echo "    3. Submit to arXiv: https://arxiv.org/submit"
echo "    4. Upload tarball: Use 'Upload Files' option"
echo "    5. Copy metadata: Use information from $METADATA_FILE"
echo ""
echo "  Documentation:"
echo "    - Submission guide: docs/publication/ARXIV_SUBMISSION_GUIDE.md"
echo "    - arXiv help:       https://arxiv.org/help/submit_tex"
echo ""
echo "=============================================================================="
echo ""

log_ok "arXiv submission workflow complete ($(date))"

exit 0
