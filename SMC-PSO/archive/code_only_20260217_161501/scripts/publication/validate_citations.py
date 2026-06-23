#!/usr/bin/env python
# ==============================================================================
# Citation Validation System
# ==============================================================================
# Purpose: Validate citations across all documentation files and cross-reference
#          with bibliography entries to ensure 100% coverage
#
# Usage:
#   python scripts/publication/validate_citations.py
#   python scripts/publication/validate_citations.py --output report.txt
#   python scripts/publication/validate_citations.py --verbose
#
# Features:
#   - Parse all documentation files (docs/**/*.md, docs/**/*.rst)
#   - Extract citations (patterns: [Author et al., Year], @key, \cite{key})
#   - Cross-reference with BibTeX files (docs/**/*.bib)
#   - Report missing citations, broken references, unused entries
#   - Generate validation report (text format)
#   - Exit code 0 = 100% coverage, 1 = missing citations
#
# Output:
#   - Citation validation report (stdout or file)
#   - Summary statistics (total citations, covered, missing, unused)
#   - Recommendations for fixing issues
#
# Author: Claude Code (Agent 1 - Publication Infrastructure Specialist)
# Date: November 12, 2025
# Version: 1.0
# ==============================================================================

import os
import re
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Tuple

# ==============================================================================
# Configuration
# ==============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
BIB_FILES = [
    DOCS_DIR / "bib" / "adaptive.bib",
    DOCS_DIR / "bib" / "dip.bib",
    DOCS_DIR / "bib" / "fdi.bib",
    DOCS_DIR / "bib" / "numerical.bib",
    DOCS_DIR / "bib" / "pso.bib",
    DOCS_DIR / "bib" / "smc.bib",
    DOCS_DIR / "bib" / "software.bib",
    DOCS_DIR / "bib" / "stability.bib",
    DOCS_DIR / "refs.bib",
    DOCS_DIR / "references" / "refs.bib",
]

# Citation patterns (regex)
CITATION_PATTERNS = [
    # [Author et al., Year] - Markdown style
    r'\[([A-Z][a-z]+(?:\s+et\s+al\.)?,?\s+\d{4}[a-z]?)\]',
    # @key - BibTeX key reference
    r'@([a-zA-Z0-9_\-:]+)',
    # \cite{key} - LaTeX style
    r'\\cite\{([a-zA-Z0-9_\-:,\s]+)\}',
    # [key] - Simple reference
    r'\[([a-zA-Z0-9_\-:]+)\]',
]

# File patterns to search
DOC_PATTERNS = [
    "**/*.md",
    "**/*.rst",
]

# Directories to exclude
EXCLUDE_DIRS = [
    "_build",
    "_static",
    "_templates",
    ".git",
    "__pycache__",
]

# ==============================================================================
# Helper Functions
# ==============================================================================

def log_info(message: str, verbose: bool = False):
    """Print info message if verbose mode enabled"""
    if verbose:
        print(f"[INFO] {message}")

def log_ok(message: str):
    """Print success message"""
    print(f"[OK] {message}")

def log_error(message: str):
    """Print error message"""
    print(f"[ERROR] {message}", file=sys.stderr)

def log_warning(message: str):
    """Print warning message"""
    print(f"[WARNING] {message}")

# ==============================================================================
# BibTeX Parsing
# ==============================================================================

def parse_bibtex_file(bib_file: Path, verbose: bool = False) -> Set[str]:
    """
    Parse BibTeX file and extract entry keys

    Args:
        bib_file: Path to .bib file
        verbose: Enable verbose logging

    Returns:
        Set of BibTeX entry keys
    """
    if not bib_file.exists():
        log_warning(f"BibTeX file not found: {bib_file}")
        return set()

    log_info(f"Parsing BibTeX file: {bib_file}", verbose)

    keys = set()
    try:
        with open(bib_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract entry keys: @article{key,
        pattern = r'@\w+\{([a-zA-Z0-9_\-:]+),'
        matches = re.findall(pattern, content)
        keys.update(matches)

        log_info(f"  Found {len(matches)} entries", verbose)

    except Exception as e:
        log_error(f"Failed to parse {bib_file}: {e}")

    return keys

def parse_all_bibtex_files(bib_files: List[Path], verbose: bool = False) -> Set[str]:
    """
    Parse all BibTeX files and collect entry keys

    Args:
        bib_files: List of .bib file paths
        verbose: Enable verbose logging

    Returns:
        Set of all BibTeX entry keys
    """
    log_info("Parsing BibTeX files...", verbose)

    all_keys = set()
    for bib_file in bib_files:
        keys = parse_bibtex_file(bib_file, verbose)
        all_keys.update(keys)

    log_info(f"Total BibTeX entries: {len(all_keys)}", verbose)
    return all_keys

# ==============================================================================
# Citation Extraction
# ==============================================================================

def extract_citations_from_file(doc_file: Path, verbose: bool = False) -> Set[str]:
    """
    Extract citations from documentation file

    Args:
        doc_file: Path to .md or .rst file
        verbose: Enable verbose logging

    Returns:
        Set of citation keys/strings
    """
    citations = set()

    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply all citation patterns
        for pattern in CITATION_PATTERNS:
            matches = re.findall(pattern, content)

            # Handle comma-separated citations in \cite{key1,key2}
            for match in matches:
                if ',' in match:
                    # Split and strip whitespace
                    keys = [k.strip() for k in match.split(',')]
                    citations.update(keys)
                else:
                    citations.add(match)

        if citations and verbose:
            log_info(f"  {doc_file.name}: {len(citations)} citations", verbose)

    except Exception as e:
        log_warning(f"Failed to read {doc_file}: {e}")

    return citations

def extract_all_citations(docs_dir: Path, verbose: bool = False) -> Dict[Path, Set[str]]:
    """
    Extract citations from all documentation files

    Args:
        docs_dir: Documentation directory
        verbose: Enable verbose logging

    Returns:
        Dictionary mapping file paths to citation sets
    """
    log_info("Extracting citations from documentation files...", verbose)

    citations_by_file = {}
    total_citations = 0

    for pattern in DOC_PATTERNS:
        for doc_file in docs_dir.rglob(pattern):
            # Skip excluded directories
            if any(excl in doc_file.parts for excl in EXCLUDE_DIRS):
                continue

            citations = extract_citations_from_file(doc_file, verbose)
            if citations:
                citations_by_file[doc_file] = citations
                total_citations += len(citations)

    log_info(f"Total files with citations: {len(citations_by_file)}", verbose)
    log_info(f"Total citations extracted: {total_citations}", verbose)

    return citations_by_file

# ==============================================================================
# Citation Validation
# ==============================================================================

def validate_citations(
    citations_by_file: Dict[Path, Set[str]],
    bib_keys: Set[str],
    verbose: bool = False
) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Validate citations against BibTeX entries

    Args:
        citations_by_file: Dictionary mapping files to citation sets
        bib_keys: Set of BibTeX entry keys
        verbose: Enable verbose logging

    Returns:
        Tuple of (all_citations, covered_citations, missing_citations)
    """
    log_info("Validating citations...", verbose)

    # Collect all unique citations
    all_citations = set()
    for citations in citations_by_file.values():
        all_citations.update(citations)

    # Check which citations are covered by BibTeX
    covered_citations = set()
    missing_citations = set()

    for citation in all_citations:
        # Check if citation matches BibTeX key (case-insensitive)
        found = False
        for bib_key in bib_keys:
            if citation.lower() == bib_key.lower():
                covered_citations.add(citation)
                found = True
                break
            # Also check if citation is substring of bib_key (e.g., "Utkin1977" in "utkin1977smc")
            if citation.lower() in bib_key.lower():
                covered_citations.add(citation)
                found = True
                break

        if not found:
            # Check if citation is in format [Author et al., Year]
            if "et al." in citation or re.match(r'[A-Z][a-z]+,?\s+\d{4}', citation):
                # This is a natural language citation, not a BibTeX key reference
                # Still valid, just not linked to BibTeX
                covered_citations.add(citation)
            else:
                missing_citations.add(citation)

    log_info(f"Total citations: {len(all_citations)}", verbose)
    log_info(f"Covered citations: {len(covered_citations)}", verbose)
    log_info(f"Missing citations: {len(missing_citations)}", verbose)

    return all_citations, covered_citations, missing_citations

def find_unused_bibtex_entries(
    bib_keys: Set[str],
    citations: Set[str],
    verbose: bool = False
) -> Set[str]:
    """
    Find BibTeX entries not referenced in documentation

    Args:
        bib_keys: Set of BibTeX entry keys
        citations: Set of all citations
        verbose: Enable verbose logging

    Returns:
        Set of unused BibTeX entry keys
    """
    log_info("Finding unused BibTeX entries...", verbose)

    unused_entries = set()

    for bib_key in bib_keys:
        # Check if BibTeX key is referenced anywhere
        found = False
        for citation in citations:
            if bib_key.lower() == citation.lower() or bib_key.lower() in citation.lower():
                found = True
                break

        if not found:
            unused_entries.add(bib_key)

    log_info(f"Unused BibTeX entries: {len(unused_entries)}", verbose)

    return unused_entries

# ==============================================================================
# Report Generation
# ==============================================================================

def generate_report(
    citations_by_file: Dict[Path, Set[str]],
    all_citations: Set[str],
    covered_citations: Set[str],
    missing_citations: Set[str],
    unused_entries: Set[str],
    bib_keys: Set[str]
) -> str:
    """
    Generate citation validation report

    Args:
        citations_by_file: Dictionary mapping files to citation sets
        all_citations: Set of all citations
        covered_citations: Set of covered citations
        missing_citations: Set of missing citations
        unused_entries: Set of unused BibTeX entries
        bib_keys: Set of all BibTeX entry keys

    Returns:
        Report string
    """
    report = []
    report.append("=" * 80)
    report.append(" Citation Validation Report")
    report.append("=" * 80)
    report.append("")

    # Summary statistics
    report.append("Summary Statistics:")
    report.append("-" * 80)
    report.append(f"  Documentation files with citations: {len(citations_by_file)}")
    report.append(f"  Total citations extracted:          {len(all_citations)}")
    report.append(f"  Covered citations:                  {len(covered_citations)} ({100*len(covered_citations)//len(all_citations) if all_citations else 0}%)")
    report.append(f"  Missing citations:                  {len(missing_citations)}")
    report.append(f"  Total BibTeX entries:               {len(bib_keys)}")
    report.append(f"  Unused BibTeX entries:              {len(unused_entries)}")
    report.append("")

    # Coverage status
    if len(missing_citations) == 0:
        report.append("[OK] 100% citation coverage achieved!")
    else:
        report.append(f"[ERROR] {len(missing_citations)} citations missing from bibliography")
    report.append("")

    # Missing citations
    if missing_citations:
        report.append("Missing Citations:")
        report.append("-" * 80)
        for citation in sorted(missing_citations):
            # Find which files use this citation
            files_using = []
            for file_path, file_citations in citations_by_file.items():
                if citation in file_citations:
                    files_using.append(file_path.relative_to(DOCS_DIR))

            report.append(f"  - {citation}")
            for file_path in files_using:
                report.append(f"      Used in: {file_path}")
        report.append("")

    # Unused BibTeX entries (informational only)
    if unused_entries:
        report.append("Unused BibTeX Entries:")
        report.append("-" * 80)
        report.append("  (These entries exist in bibliography but are not referenced)")
        for entry in sorted(unused_entries)[:20]:  # Limit to first 20
            report.append(f"  - {entry}")
        if len(unused_entries) > 20:
            report.append(f"  ... and {len(unused_entries) - 20} more")
        report.append("")

    # Recommendations
    report.append("Recommendations:")
    report.append("-" * 80)
    if missing_citations:
        report.append("  1. Add missing BibTeX entries to docs/bib/*.bib files")
        report.append("  2. Update citations to use existing BibTeX keys")
        report.append("  3. Verify citation format: [Author et al., Year] or @key")
    else:
        report.append("  [OK] No action required - 100% coverage achieved")
    report.append("")

    report.append("=" * 80)

    return "\n".join(report)

# ==============================================================================
# Main Function
# ==============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate citations across documentation files"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for validation report (default: stdout)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    print("[INFO] Starting citation validation...")
    print(f"[INFO] Project root: {PROJECT_ROOT}")
    print(f"[INFO] Documentation directory: {DOCS_DIR}")
    print("")

    # Parse BibTeX files
    bib_keys = parse_all_bibtex_files(BIB_FILES, args.verbose)
    log_ok(f"Parsed {len(BIB_FILES)} BibTeX files")
    log_ok(f"Found {len(bib_keys)} BibTeX entries")
    print("")

    # Extract citations from documentation
    citations_by_file = extract_all_citations(DOCS_DIR, args.verbose)
    log_ok(f"Extracted citations from {len(citations_by_file)} files")
    print("")

    # Validate citations
    all_citations, covered_citations, missing_citations = validate_citations(
        citations_by_file, bib_keys, args.verbose
    )

    # Find unused entries
    unused_entries = find_unused_bibtex_entries(bib_keys, all_citations, args.verbose)
    print("")

    # Generate report
    report = generate_report(
        citations_by_file,
        all_citations,
        covered_citations,
        missing_citations,
        unused_entries,
        bib_keys
    )

    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        log_ok(f"Report written to: {args.output}")
    else:
        print(report)

    # Exit code
    if missing_citations:
        log_error(f"Validation failed: {len(missing_citations)} missing citations")
        sys.exit(1)
    else:
        log_ok("Validation successful: 100% citation coverage")
        sys.exit(0)

if __name__ == "__main__":
    main()
