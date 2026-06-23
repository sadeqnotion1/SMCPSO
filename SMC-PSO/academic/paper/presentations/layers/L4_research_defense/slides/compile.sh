#!/bin/bash
# ============================================================================
# Compile Script for DIP-SMC-PSO Presentation (Linux/Mac)
# ============================================================================
# This script compiles both the main Beamer presentation and speaker scripts
# Usage: bash compile.sh [presentation|scripts|all|clean]
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PRESENTATION="comprehensive_project_presentation"
SCRIPTS="speaker_scripts"
BUILD_DIR="build"
OUTPUT_DIR="output"

# Create output directories
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

# Function: Compile LaTeX document
compile_latex() {
    local filename=$1
    local document_type=$2

    echo -e "${BLUE}[INFO]${NC} Compiling $document_type: $filename.tex"

    # First pass: Generate aux files
    echo -e "${YELLOW}[COMPILE]${NC} First pass (pdflatex)..."
    pdflatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$filename.tex" > /dev/null

    # Second pass: Process bibliography (if exists)
    if [ -f "references.bib" ]; then
        echo -e "${YELLOW}[COMPILE]${NC} Processing bibliography (biber)..."
        biber --input-directory="$BUILD_DIR" --output-directory="$BUILD_DIR" "$filename" > /dev/null || true
    fi

    # Third pass: Resolve references
    echo -e "${YELLOW}[COMPILE]${NC} Second pass (pdflatex)..."
    pdflatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$filename.tex" > /dev/null

    # Fourth pass: Final compilation
    echo -e "${YELLOW}[COMPILE]${NC} Final pass (pdflatex)..."
    pdflatex -interaction=nonstopmode -output-directory="$BUILD_DIR" "$filename.tex" > /dev/null

    # Move PDF to output directory
    if [ -f "$BUILD_DIR/$filename.pdf" ]; then
        mv "$BUILD_DIR/$filename.pdf" "$OUTPUT_DIR/"
        echo -e "${GREEN}[OK]${NC} PDF generated: $OUTPUT_DIR/$filename.pdf"

        # Display file size
        local filesize=$(du -h "$OUTPUT_DIR/$filename.pdf" | cut -f1)
        echo -e "${BLUE}[INFO]${NC} File size: $filesize"

        # Count pages
        local pages=$(pdfinfo "$OUTPUT_DIR/$filename.pdf" 2>/dev/null | grep "Pages:" | awk '{print $2}')
        if [ -n "$pages" ]; then
            echo -e "${BLUE}[INFO]${NC} Total pages: $pages"
        fi
    else
        echo -e "${RED}[ERROR]${NC} PDF generation failed for $filename"
        return 1
    fi
}

# Function: Clean build artifacts
clean_build() {
    echo -e "${YELLOW}[CLEAN]${NC} Removing build artifacts..."
    rm -rf "$BUILD_DIR"
    rm -rf "$OUTPUT_DIR"
    echo -e "${GREEN}[OK]${NC} Build directories cleaned"
}

# Function: Display usage
usage() {
    echo "Usage: $0 [presentation|scripts|all|clean]"
    echo ""
    echo "Options:"
    echo "  presentation  - Compile main Beamer presentation only"
    echo "  scripts       - Compile speaker scripts only"
    echo "  all           - Compile both presentation and scripts (default)"
    echo "  clean         - Remove all build artifacts"
    echo ""
}

# Main execution
main() {
    local target=${1:-all}

    case "$target" in
        presentation)
            echo -e "${BLUE}=====================================${NC}"
            echo -e "${BLUE}Compiling Beamer Presentation${NC}"
            echo -e "${BLUE}=====================================${NC}"
            compile_latex "$PRESENTATION" "Beamer Presentation"
            ;;
        scripts)
            echo -e "${BLUE}=====================================${NC}"
            echo -e "${BLUE}Compiling Speaker Scripts${NC}"
            echo -e "${BLUE}=====================================${NC}"
            compile_latex "$SCRIPTS" "Speaker Scripts"
            ;;
        all)
            echo -e "${BLUE}=====================================${NC}"
            echo -e "${BLUE}Compiling All Documents${NC}"
            echo -e "${BLUE}=====================================${NC}"
            compile_latex "$PRESENTATION" "Beamer Presentation"
            echo ""
            compile_latex "$SCRIPTS" "Speaker Scripts"
            echo ""
            echo -e "${GREEN}=====================================${NC}"
            echo -e "${GREEN}Compilation Complete!${NC}"
            echo -e "${GREEN}=====================================${NC}"
            echo -e "${BLUE}[INFO]${NC} Output files:"
            ls -lh "$OUTPUT_DIR"/*.pdf
            ;;
        clean)
            clean_build
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown option: $target"
            usage
            exit 1
            ;;
    esac
}

# Check for required tools
check_dependencies() {
    local missing_deps=()

    for cmd in pdflatex biber pdfinfo; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        fi
    done

    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}[ERROR]${NC} Missing required dependencies: ${missing_deps[*]}"
        echo -e "${YELLOW}[INFO]${NC} Please install TeX Live or MiKTeX"
        exit 1
    fi
}

# Entry point
check_dependencies
main "$@"
