#!/usr/bin/env python3
"""
Quick status checker for thesis sources archive.

Usage:
    python check_status.py

Shows:
- Total PDFs in each category
- Acquisition progress
- Missing high-priority sources
"""

import os
import json
from pathlib import Path
from collections import defaultdict

# Directories to check
ARCHIVE_ROOT = Path(__file__).parent
CATEGORIES = ["books", "articles", "proceedings", "manuals"]
METADATA_FILE = ARCHIVE_ROOT / "metadata" / "citation_map.json"

def count_pdfs():
    """Count PDFs in each category."""
    counts = {}
    for category in CATEGORIES:
        category_path = ARCHIVE_ROOT / category
        if category_path.exists():
            pdfs = list(category_path.glob("*.pdf"))
            counts[category] = len(pdfs)
        else:
            counts[category] = 0
    return counts

def load_citation_map():
    """Load citation metadata."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def analyze_status():
    """Analyze acquisition status."""
    citation_map = load_citation_map()
    pdf_counts = count_pdfs()

    # Count by type
    type_counts = defaultdict(int)
    type_total = defaultdict(int)

    for key, meta in citation_map.items():
        source_type = meta.get("type", "unknown")
        type_total[source_type] += 1

        # Check if PDF exists
        file_path = ARCHIVE_ROOT / meta.get("file", "")
        if file_path.exists() and file_path.suffix == ".pdf":
            type_counts[source_type] += 1

    return type_counts, type_total, citation_map

def print_status():
    """Print formatted status report."""
    type_counts, type_total, citation_map = analyze_status()
    pdf_counts = count_pdfs()

    print("=" * 60)
    print("THESIS SOURCES ARCHIVE - STATUS REPORT")
    print("=" * 60)
    print()

    # Overall summary
    total_expected = sum(type_total.values())
    total_acquired = sum(type_counts.values())
    percentage = (total_acquired / total_expected * 100) if total_expected > 0 else 0

    print(f"[OVERALL] {total_acquired}/{total_expected} PDFs acquired ({percentage:.1f}%)")
    print()

    # By category
    print("BY CATEGORY:")
    print("-" * 60)
    for category in CATEGORIES:
        count = pdf_counts.get(category, 0)
        # Map category to type
        type_map = {
            "books": "book",
            "articles": ["article", "incollection"],
            "proceedings": "inproceedings",
            "manuals": "manual"
        }

        category_types = type_map[category]
        if isinstance(category_types, list):
            expected = sum(type_total.get(t, 0) for t in category_types)
        else:
            expected = type_total.get(category_types, 0)

        status = "[OK]" if count == expected else "[NEED]"
        print(f"{status} {category.capitalize():15} {count}/{expected} PDFs")
    print()

    # Missing high-priority sources
    print("MISSING HIGH-PRIORITY SOURCES:")
    print("-" * 60)
    missing_high = []
    for key, meta in citation_map.items():
        file_path = ARCHIVE_ROOT / meta.get("file", "")
        if not file_path.exists():
            if meta.get("acquisition_status") == "NEED":
                # Check if high priority (cited multiple times or foundational)
                title = meta.get("title", "Unknown")
                year = meta.get("year", "????")
                source_type = meta.get("type", "unknown")

                # Simple priority heuristic (you can customize this)
                if any(keyword in title.lower() for keyword in
                       ["nonlinear", "sliding mode", "particle swarm", "control"]):
                    missing_high.append((key, title, year, source_type))

    if missing_high:
        for key, title, year, source_type in missing_high[:10]:  # Top 10
            print(f"  [{key}] {title[:50]}... ({year})")
    else:
        print("  [OK] All high-priority sources acquired!")
    print()

    # Quick stats
    print("QUICK STATS:")
    print("-" * 60)
    print(f"  Total Sources: {total_expected}")
    print(f"  Books: {type_total.get('book', 0)}")
    print(f"  Articles: {type_total.get('article', 0) + type_total.get('incollection', 0)}")
    print(f"  Proceedings: {type_total.get('inproceedings', 0)}")
    print(f"  Manuals: {type_total.get('manual', 0)}")
    print()

    # Next steps
    print("NEXT STEPS:")
    print("-" * 60)
    if percentage < 25:
        print("  1. Start with open access sources (see acquisition_status.md)")
        print("  2. Check institutional access (IEEE, Springer, etc.)")
        print("  3. Focus on HIGH priority sources first")
    elif percentage < 75:
        print("  1. Continue with institutional access")
        print("  2. Request via ResearchGate if needed")
        print("  3. Consider purchasing key sources")
    else:
        print("  1. Acquire remaining low-priority sources")
        print("  2. Verify all PDFs are correct")
        print("  3. Update thesis_locations.md")
    print()

    print("=" * 60)
    print("For detailed status, see: metadata/acquisition_status.md")
    print("=" * 60)

if __name__ == "__main__":
    print_status()
