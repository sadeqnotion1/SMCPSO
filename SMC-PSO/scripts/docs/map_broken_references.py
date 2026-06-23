#!/usr/bin/env python3
"""
Map broken citation references to existing BibTeX keys or identify missing entries.

This script analyzes broken references from validate_citations.py and attempts to:
1. Find matching BibTeX entries with different key formats
2. Identify which entries need to be created
3. Suggest appropriate key mappings

Usage:
    python scripts/docs/map_broken_references.py
"""
# example-metadata:
# runnable: true
# expected_result: Mapping of broken references to BibTeX keys or "MISSING"

import re
from pathlib import Path
from typing import Dict, List
import sys

# Fix Windows UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def parse_bibtex_keys(bib_dir: Path) -> Dict[str, str]:
    """
    Parse all BibTeX files and return dict of {key: source_file}.

    Returns:
        Dict mapping BibTeX key → source filename
    """
    keys = {}

    for bib_file in bib_dir.glob('*.bib'):
        content = bib_file.read_text(encoding='utf-8')
        entry_pattern = r'@\w+\{([^,]+),'

        for match in re.finditer(entry_pattern, content):
            key = match.group(1).strip()
            keys[key] = bib_file.name

    return keys


def extract_year_author(key: str) -> tuple:
    """
    Extract year and author surname from simplified citation key.

    Examples:
        kennedy1995particle → ('kennedy', '1995')
        zhang2015comprehensive → ('zhang', '2015')
    """
    # Pattern: author + year + description
    match = re.match(r'([a-z]+)(\d{4})', key, re.IGNORECASE)
    if match:
        return (match.group(1).lower(), match.group(2))
    return (None, None)


def find_matching_keys(broken_key: str, all_keys: Dict[str, str]) -> List[str]:
    """
    Find BibTeX keys that might match the broken reference.

    Strategy:
    1. Extract author and year from broken key (e.g., kennedy1995particle)
    2. Search for keys containing both author and year
    3. Rank by similarity
    """
    author, year = extract_year_author(broken_key)

    if not author or not year:
        return []

    matches = []
    for key in all_keys.keys():
        key_lower = key.lower()
        # Check if key contains both author surname and year
        if author in key_lower and year in key_lower:
            matches.append(key)

    return matches


def main():
    # Broken references from validation output
    broken_pso = [
        'kennedy1995particle',
        'clerc2002particle',
        'zhang2015comprehensive',
        'coello2007evolutionary',
        'deb2001multi',
        'jiang2007stochastic',
        'van2006analysis',
        'wolpert1997no'
    ]

    broken_smc = [
        'utkin1999sliding',
        'shtessel2014sliding',
        'levant2003higher',
        'slotine1991applied',
        'moreno2012strict',
        'krstic1995nonlinear',
        'edwards1998sliding'
    ]

    broken_system = [
        'goldstein2002classical',
        'spong2006robot',
        'furuta2003swing',
        'boubaker2013double'
    ]

    all_broken = {
        'pso_optimization_complete.md': broken_pso,
        'smc_theory_complete.md': broken_smc,
        'system_dynamics_complete.md': broken_system
    }

    # Parse all existing BibTeX keys
    bib_dir = Path('docs/bib')
    existing_keys = parse_bibtex_keys(bib_dir)

    print("=" * 80)
    print("BROKEN REFERENCE MAPPING ANALYSIS")
    print("=" * 80)
    print()
    print(f"Existing BibTeX entries: {len(existing_keys)}")
    print(f"Broken references to map: {sum(len(refs) for refs in all_broken.values())}")
    print()

    mapping_results = {}
    missing_entries = []

    for doc_file, broken_refs in all_broken.items():
        print(f"=== {doc_file} ===")
        print()

        for broken_key in broken_refs:
            matches = find_matching_keys(broken_key, existing_keys)

            if matches:
                # Found potential match(es)
                if len(matches) == 1:
                    status = "[MATCH]"
                    suggestion = matches[0]
                    source_file = existing_keys[matches[0]]
                    print(f"{status} {broken_key:30} → {suggestion:50} ({source_file})")
                    mapping_results[broken_key] = suggestion
                else:
                    status = "[MULTI]"
                    print(f"{status} {broken_key:30} → Multiple matches:")
                    for match in matches:
                        source_file = existing_keys[match]
                        print(f"                                   - {match} ({source_file})")
                    mapping_results[broken_key] = matches[0]  # Use first match as suggestion
            else:
                # No match found - needs to be created
                status = "[MISSING]"
                print(f"{status} {broken_key:30} → NEEDS CREATION")
                missing_entries.append(broken_key)

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Matched to existing keys:  {len(mapping_results)}")
    print(f"Missing (need creation):   {len(missing_entries)}")
    print()

    if missing_entries:
        print("Missing entries to create:")
        for key in missing_entries:
            author, year = extract_year_author(key)
            print(f"  - {key:30} (author: {author}, year: {year})")
        print()

    # Generate replacement mapping for copy-paste
    print("=" * 80)
    print("REPLACEMENT MAPPING (for documentation updates)")
    print("=" * 80)
    print()
    for broken_key, correct_key in sorted(mapping_results.items()):
        print(f"{broken_key:30} → {correct_key}")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
