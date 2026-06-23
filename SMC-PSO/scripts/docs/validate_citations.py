#!/usr/bin/env python3
"""
Validate citation integrity across BibTeX files and documentation.

This script validates:
1. All BibTeX entries have DOI or URL fields
2. All {cite}`key` references in docs match BibTeX keys
3. No orphaned citations (BibTeX entry but no references)
4. No broken references (reference but no BibTeX entry)

Usage:
    python scripts/docs/validate_citations.py
    python scripts/docs/validate_citations.py --bibtex docs/bib --docs docs/theory
"""
# example-metadata:
# runnable: true
# expected_result: Validation report with citation coverage metrics

import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import sys


def parse_bibtex_file(bib_path: Path) -> Dict[str, Dict[str, str]]:
    """
    Parse a BibTeX file and extract entry keys and metadata.

    Returns:
        Dict mapping BibTeX key → {type, doi, url, note}
    """
    entries = {}
    content = bib_path.read_text(encoding='utf-8')

    # Find all entry starts: @type{key,
    entry_start_pattern = r'@(\w+)\{([^,]+),'

    for match in re.finditer(entry_start_pattern, content):
        entry_type = match.group(1)
        key = match.group(2).strip()
        start_pos = match.end()

        # Count braces to find matching closing brace
        brace_count = 1  # We already have the opening brace from @type{
        pos = start_pos
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            # Extract entry body between opening and closing braces
            body = content[start_pos:pos-1]

            # Extract DOI and URL from full entry body
            doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', body, re.IGNORECASE)
            url_match = re.search(r'url\s*=\s*\{([^}]+)\}', body, re.IGNORECASE)
            note_match = re.search(r'note\s*=\s*\{([^}]+)\}', body, re.IGNORECASE)

            entries[key] = {
                'type': entry_type,
                'doi': doi_match.group(1).strip() if doi_match else None,
                'url': url_match.group(1).strip() if url_match else None,
                'note': note_match.group(1).strip() if note_match else None,
                'source_file': bib_path.name
            }

    return entries


def find_cite_references(doc_path: Path) -> Set[str]:
    """
    Find all {cite}`key1,key2,key3` references in a Markdown file.

    Returns:
        Set of BibTeX keys referenced
    """
    content = doc_path.read_text(encoding='utf-8')

    # Pattern: {cite}`key1,key2,key3`
    cite_pattern = r'\{cite\}`([^`]+)`'

    references = set()
    for match in re.finditer(cite_pattern, content):
        keys = match.group(1).split(',')
        for key in keys:
            references.add(key.strip())

    return references


def validate_bibtex_accessibility(entries: Dict[str, Dict[str, str]]) -> Tuple[List[str], int]:
    """
    Check that all BibTeX entries have DOI or URL.

    Returns:
        (list of keys missing DOI/URL, total count)
    """
    missing = []
    for key, meta in entries.items():
        if not meta['doi'] and not meta['url']:
            missing.append(f"{key} [{meta['source_file']}]")

    return missing, len(entries)


def validate_cross_references(
    bibtex_keys: Set[str],
    doc_references: Dict[Path, Set[str]]
) -> Tuple[List[str], List[str]]:
    """
    Check for orphaned citations and broken references.

    Returns:
        (orphaned_citations, broken_references)
    """
    all_references = set()
    for refs in doc_references.values():
        all_references.update(refs)

    # Orphaned: in BibTeX but never referenced
    orphaned = sorted(bibtex_keys - all_references)

    # Broken: referenced but not in BibTeX
    broken = []
    for doc_path, refs in doc_references.items():
        for ref in refs:
            if ref not in bibtex_keys:
                broken.append(f"{ref} in {doc_path.name}")

    return orphaned, broken


def main():
    # Fix Windows UTF-8 encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description='Validate citation integrity')
    parser.add_argument('--bibtex', type=Path, default=Path('docs/bib'),
                        help='Directory containing BibTeX files')
    parser.add_argument('--docs', type=Path, default=Path('docs/theory'),
                        help='Directory containing documentation with citations')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed validation results')

    args = parser.parse_args()

    # Collect all BibTeX entries
    print("=" * 80)
    print("CITATION VALIDATION REPORT")
    print("=" * 80)
    print()

    all_entries = {}
    bib_files = list(args.bibtex.glob('*.bib'))

    if not bib_files:
        print(f"[FAIL] No .bib files found in {args.bibtex}")
        return 1

    print(f"[BIB] Parsing BibTeX files from {args.bibtex}")
    for bib_file in bib_files:
        entries = parse_bibtex_file(bib_file)
        all_entries.update(entries)
        print(f"  [OK] {bib_file.name}: {len(entries)} entries")

    print(f"\n  Total BibTeX entries: {len(all_entries)}")
    print()

    # Check DOI/URL accessibility
    print("=" * 80)
    print("1. BibTeX Accessibility Check (DOI/URL)")
    print("=" * 80)

    missing_access, total = validate_bibtex_accessibility(all_entries)
    accessibility_pct = 100 * (total - len(missing_access)) / total if total > 0 else 0

    if not missing_access:
        print(f"[PASS] All {total} entries have DOI or URL (100%)")
    else:
        print(f"[WARN] {len(missing_access)}/{total} entries missing DOI/URL ({accessibility_pct:.1f}% accessible)")
        if args.verbose:
            print("\nMissing accessibility:")
            for item in missing_access[:10]:  # Show first 10
                print(f"  - {item}")
            if len(missing_access) > 10:
                print(f"  ... and {len(missing_access) - 10} more")

    print()

    # Find all {cite} references in docs
    print("=" * 80)
    print("2. Documentation Citation References")
    print("=" * 80)

    doc_files = list(args.docs.glob('**/*.md'))
    if not doc_files:
        print(f"[FAIL] No .md files found in {args.docs}")
        return 1

    doc_references = {}
    total_refs = 0

    print(f"[DOC] Scanning documentation in {args.docs}")
    for doc_file in doc_files:
        refs = find_cite_references(doc_file)
        if refs:
            doc_references[doc_file] = refs
            total_refs += len(refs)
            print(f"  [OK] {doc_file.name}: {len(refs)} citation(s)")

    print(f"\n  Total citation references: {total_refs}")
    print()

    # Cross-reference validation
    print("=" * 80)
    print("3. Cross-Reference Validation")
    print("=" * 80)

    bibtex_keys = set(all_entries.keys())
    orphaned, broken = validate_cross_references(bibtex_keys, doc_references)

    if not broken:
        print(f"[PASS] All {total_refs} references have BibTeX entries (0 broken)")
    else:
        print(f"[FAIL] {len(broken)} broken reference(s) found:")
        for item in broken:
            print(f"  - {item}")

    print()

    if not orphaned:
        print(f"[PASS] All {len(bibtex_keys)} BibTeX entries are referenced (0 orphaned)")
    else:
        print(f"[INFO] {len(orphaned)} orphaned citation(s) (in BibTeX but not referenced):")
        if args.verbose:
            for item in orphaned[:10]:
                print(f"  - {item}")
            if len(orphaned) > 10:
                print(f"  ... and {len(orphaned) - 10} more")

    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"BibTeX entries:        {len(all_entries)}")
    print(f"DOI/URL accessible:    {len(all_entries) - len(missing_access)} ({accessibility_pct:.1f}%)")
    print(f"Citation references:   {total_refs}")
    print(f"Broken references:     {len(broken)}")
    print(f"Orphaned citations:    {len(orphaned)}")
    print()

    # Exit code
    if broken or accessibility_pct < 95:
        print("[FAIL] VALIDATION FAILED")
        print()
        if broken:
            print(f"  - Fix {len(broken)} broken reference(s)")
        if accessibility_pct < 95:
            print(f"  - Add DOI/URL to {len(missing_access)} entry/entries (target: >=95%)")
        return 1
    else:
        print("[PASS] VALIDATION PASSED")
        print()
        print("All citations are properly formatted and accessible!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
