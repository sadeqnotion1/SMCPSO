#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/validate_heading_anchors.py
#==============================================================================
# Heading Anchor Validator - Phase 1
#
# Validates heading anchors to detect:
# - Duplicate anchors across files
# - Heading hierarchy violations
# - Special character issues
# - Explicit vs auto-generated anchor conflicts
#
# Usage:
#     python scripts/docs/validate_heading_anchors.py
#     python scripts/docs/validate_heading_anchors.py --path docs
#==============================================================================
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


def extract_headings(content: str, filepath: Path) -> List[Dict]:
    """
    Extract all headings from markdown content.

    Args:
        content: File content
        filepath: Path to file

    Returns:
        List of dictionaries with heading metadata
    """
    headings = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Match markdown headings: # Title or {#anchor}
        heading_match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{#([a-zA-Z0-9_-]+)\})?\s*$', line)

        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            explicit_anchor = heading_match.group(3)

            # Generate auto anchor (simplified version of what MyST does)
            auto_anchor = text.lower()
            auto_anchor = re.sub(r'[^\w\s-]', '', auto_anchor)
            auto_anchor = re.sub(r'[-\s]+', '-', auto_anchor)
            auto_anchor = auto_anchor.strip('-')

            headings.append({
                "filepath": str(filepath),
                "line": i,
                "level": level,
                "text": text,
                "explicit_anchor": explicit_anchor,
                "auto_anchor": auto_anchor,
                "anchor": explicit_anchor if explicit_anchor else auto_anchor
            })

    return headings


def find_duplicate_anchors(all_headings: List[Dict]) -> Dict:
    """
    Find duplicate heading anchors across all files.

    Args:
        all_headings: All headings from all files

    Returns:
        Dictionary with duplicate anchor analysis
    """
    # Group by anchor
    anchors_by_id = defaultdict(list)
    for heading in all_headings:
        anchors_by_id[heading["anchor"]].append(heading)

    # Find duplicates
    duplicates = {}
    for anchor, headings in anchors_by_id.items():
        if len(headings) > 1:
            duplicates[anchor] = {
                "count": len(headings),
                "locations": [
                    {
                        "file": h["filepath"],
                        "line": h["line"],
                        "text": h["text"],
                        "explicit": bool(h["explicit_anchor"])
                    }
                    for h in headings
                ]
            }

    return duplicates


def find_hierarchy_violations(headings: List[Dict]) -> List[Dict]:
    """
    Find heading hierarchy violations in a single file.

    Args:
        headings: Headings from one file

    Returns:
        List of violations
    """
    violations = []
    last_level = 0

    for heading in headings:
        level = heading["level"]

        # Check for skipped levels (e.g., H1 -> H3)
        if last_level > 0 and level > last_level + 1:
            violations.append({
                "line": heading["line"],
                "from_level": last_level,
                "to_level": level,
                "text": heading["text"],
                "type": "level_skip",
                "severity": "MEDIUM"
            })

        last_level = level

    return violations


def generate_report(all_headings: List[Dict], docs_path: Path) -> Dict:
    """
    Generate comprehensive heading anchor validation report.

    Args:
        all_headings: All headings from all files
        docs_path: Path to docs directory

    Returns:
        Report dictionary
    """
    # Find duplicate anchors
    duplicates = find_duplicate_anchors(all_headings)

    # Group headings by file for hierarchy analysis
    headings_by_file = defaultdict(list)
    for heading in all_headings:
        headings_by_file[heading["filepath"]].append(heading)

    # Find hierarchy violations per file
    all_violations = []
    for filepath, headings in headings_by_file.items():
        violations = find_hierarchy_violations(headings)
        for violation in violations:
            violation["file"] = filepath
            all_violations.append(violation)

    # Statistics
    total_headings = len(all_headings)
    explicit_anchor_count = sum(1 for h in all_headings if h["explicit_anchor"])
    files_with_violations = len({v["file"] for v in all_violations})

    # Level distribution
    level_dist = defaultdict(int)
    for heading in all_headings:
        level_dist[f"H{heading['level']}"] += 1

    return {
        "metadata": {
            "total_files": len(headings_by_file),
            "total_headings": total_headings,
            "explicit_anchors": explicit_anchor_count,
            "explicit_percentage": round(explicit_anchor_count / total_headings * 100, 1) if total_headings else 0
        },
        "duplicate_anchors": {
            "count": len(duplicates),
            "details": duplicates
        },
        "hierarchy_violations": {
            "count": len(all_violations),
            "files_affected": files_with_violations,
            "details": all_violations
        },
        "level_distribution": dict(level_dist),
        "recommendations": {
            "use_explicit_anchors": len(duplicates) > 0,
            "fix_hierarchy": len(all_violations) > 0,
            "priority": "HIGH" if len(duplicates) > 10 or len(all_violations) > 20 else "MEDIUM"
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate heading anchors in Sphinx documentation"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".artifacts/heading_anchor_report.json"),
        help="Output JSON report path"
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"ERROR: Path not found: {args.path}")
        return 1

    print(f"Scanning documentation in {args.path}...")

    # Find all markdown files
    md_files = list(args.path.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")

    # Extract all headings
    all_headings = []
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            headings = extract_headings(content, md_file)
            all_headings.extend(headings)
        except Exception as e:
            print(f"WARNING: Failed to process {md_file}: {e}")

    print(f"Extracted {len(all_headings)} headings")

    # Generate report
    print("Analyzing heading anchors...")
    report = generate_report(all_headings, args.path)

    # Save report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("HEADING ANCHOR VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total headings:           {report['metadata']['total_headings']}")
    print(f"Explicit anchors:         {report['metadata']['explicit_anchors']} ({report['metadata']['explicit_percentage']}%)")
    print(f"Duplicate anchors:        {report['duplicate_anchors']['count']}")
    print(f"Hierarchy violations:     {report['hierarchy_violations']['count']}")
    print(f"Files with violations:    {report['hierarchy_violations']['files_affected']}")
    print()
    print("Level distribution:")
    for level, count in sorted(report['level_distribution'].items()):
        print(f"  {level}: {count}")
    print()
    print(f"Report saved to: {args.output}")

    # Show top duplicate anchors
    if report['duplicate_anchors']['details']:
        print("\nTop 10 duplicate anchors:")
        sorted_duplicates = sorted(
            report['duplicate_anchors']['details'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        for anchor, data in sorted_duplicates[:10]:
            print(f"  '{anchor}': {data['count']} occurrences")

    # Show top files with hierarchy violations
    if report['hierarchy_violations']['details']:
        file_violation_counts = defaultdict(int)
        for violation in report['hierarchy_violations']['details']:
            file_violation_counts[violation['file']] += 1

        print("\nTop 10 files with hierarchy violations:")
        for filepath, count in sorted(
            file_violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            print(f"  {filepath}: {count} violations")

    return 0


if __name__ == "__main__":
    exit(main())
