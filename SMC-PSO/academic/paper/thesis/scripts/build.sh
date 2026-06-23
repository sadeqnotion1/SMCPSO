#!/bin/bash
#
# Thesis Build Automation Script
#
# Compiles LaTeX thesis with 4-pass compilation + BibTeX
# Handles cross-references, bibliography, and table of contents
#
# Usage:
#   cd thesis
#   bash scripts/build.sh
#
# Output: build/main.pdf
#
# Saves ~5 hours of manual compilation over 30 days!

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
THESIS_DIR="."
OUTPUT_DIR="build"
MAIN_FILE="main"

# Banner
echo ""
echo "========================================"
echo "  THESIS BUILD AUTOMATION"
echo "========================================"
echo ""

# Check if main.tex exists
if [ ! -f "${MAIN_FILE}.tex" ]; then
    echo -e "${RED}[ERROR]${NC} File '${MAIN_FILE}.tex' not found!"
    echo "Make sure you're in the thesis/ directory"
    exit 1
fi

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Function to run pdflatex quietly
run_pdflatex() {
    local pass=$1
    echo -e "${BLUE}[INFO]${NC} Running pdflatex (pass ${pass}/4)..."

    if pdflatex -output-directory="${OUTPUT_DIR}" \
                -interaction=nonstopmode \
                "${MAIN_FILE}.tex" > "${OUTPUT_DIR}/build_${pass}.log" 2>&1; then
        echo -e "${GREEN}[OK]${NC} Pass ${pass} completed"
        return 0
    else
        echo -e "${RED}[ERROR]${NC} Pass ${pass} failed!"
        echo "Check ${OUTPUT_DIR}/build_${pass}.log for details"
        return 1
    fi
}

# Function to run bibtex
run_bibtex() {
    echo -e "${BLUE}[INFO]${NC} Running BibTeX..."

    cd "${OUTPUT_DIR}"
    if bibtex "${MAIN_FILE}" > bibtex.log 2>&1; then
        cd ..
        echo -e "${GREEN}[OK]${NC} BibTeX completed"
        return 0
    else
        cd ..
        echo -e "${YELLOW}[WARNING]${NC} BibTeX had issues (may be okay if no citations yet)"
        echo "Check ${OUTPUT_DIR}/bibtex.log for details"
        return 0  # Don't fail build on bibtex errors
    fi
}

# Clean previous build (optional - comment out to speed up)
# echo -e "${BLUE}[INFO]${NC} Cleaning previous build..."
# rm -rf "${OUTPUT_DIR}"/*

# Build process
echo ""
echo "Starting 4-pass compilation..."
echo ""

# Pass 1: Generate .aux files
if ! run_pdflatex 1; then
    echo -e "${RED}[FAIL]${NC} Build failed on pass 1"
    exit 1
fi

# Run BibTeX
run_bibtex

# Pass 2: Include bibliography
if ! run_pdflatex 2; then
    echo -e "${RED}[FAIL]${NC} Build failed on pass 2"
    exit 1
fi

# Pass 3: Resolve cross-references
if ! run_pdflatex 3; then
    echo -e "${RED}[FAIL]${NC} Build failed on pass 3"
    exit 1
fi

# Pass 4: Final compilation
echo -e "${BLUE}[INFO]${NC} Running pdflatex (pass 4/4 - final)..."
if pdflatex -output-directory="${OUTPUT_DIR}" \
            "${MAIN_FILE}.tex" > "${OUTPUT_DIR}/build_final.log" 2>&1; then
    echo -e "${GREEN}[OK]${NC} Pass 4 completed"
else
    echo -e "${RED}[ERROR]${NC} Final pass failed!"
    echo "Check ${OUTPUT_DIR}/build_final.log for details"
    tail -n 50 "${OUTPUT_DIR}/build_final.log"
    exit 1
fi

# Check for warnings
echo ""
echo -e "${BLUE}[INFO]${NC} Checking for warnings..."

# Count undefined references
UNDEF_REFS=$(grep -c "Reference.*undefined" "${OUTPUT_DIR}/${MAIN_FILE}.log" || true)
# Count undefined citations
UNDEF_CITES=$(grep -c "Citation.*undefined" "${OUTPUT_DIR}/${MAIN_FILE}.log" || true)
# Count overfull hboxes (line overflow)
OVERFULL=$(grep -c "Overfull.*hbox" "${OUTPUT_DIR}/${MAIN_FILE}.log" || true)

if [ "$UNDEF_REFS" -gt 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} ${UNDEF_REFS} undefined references found"
fi

if [ "$UNDEF_CITES" -gt 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} ${UNDEF_CITES} undefined citations found"
fi

if [ "$OVERFULL" -gt 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} ${OVERFULL} overfull hboxes (lines too long)"
fi

# Get page count
if command -v pdfinfo &> /dev/null; then
    PAGE_COUNT=$(pdfinfo "${OUTPUT_DIR}/${MAIN_FILE}.pdf" 2>/dev/null | grep "Pages:" | awk '{print $2}')
    echo ""
    echo -e "${GREEN}[INFO]${NC} Page count: ${PAGE_COUNT}"
else
    echo -e "${YELLOW}[INFO]${NC} Install 'pdfinfo' to see page count"
fi

# Success message
echo ""
echo "========================================"
echo -e "${GREEN}[SUCCESS]${NC} Build completed!"
echo "========================================"
echo ""
echo "Output: ${OUTPUT_DIR}/${MAIN_FILE}.pdf"
echo ""

# Open PDF (optional - platform specific)
# Uncomment for your platform:

# Windows (Windows Subsystem for Linux)
# /mnt/c/Windows/System32/cmd.exe /c start "${OUTPUT_DIR}/${MAIN_FILE}.pdf"

# macOS
# open "${OUTPUT_DIR}/${MAIN_FILE}.pdf"

# Linux
# xdg-open "${OUTPUT_DIR}/${MAIN_FILE}.pdf" &

echo "To view: Open ${OUTPUT_DIR}/${MAIN_FILE}.pdf in your PDF reader"
echo ""

# Clean auxiliary files (optional)
# Uncomment to keep build directory clean:
# rm -f "${OUTPUT_DIR}"/*.aux "${OUTPUT_DIR}"/*.log "${OUTPUT_DIR}"/*.toc
# echo "Cleaned auxiliary files"

exit 0
