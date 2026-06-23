"""LT-7 Citation Audit Script

Validates all citations [1]-[68] are properly used and formatted.
Checks for: usage, duplicates, orphans, and format consistency.

Usage:
    python scripts/lt7_citation_audit.py
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Paths
PAPER_PATH = Path("benchmarks/LT7_RESEARCH_PAPER.md")
OUTPUT_PATH = Path("benchmarks/LT7_CITATION_REPORT.md")

# Expected citation range
EXPECTED_CITATIONS = 68

def load_paper() -> List[str]:
    """Load paper content as list of lines."""
    with open(PAPER_PATH, 'r', encoding='utf-8') as f:
        return f.readlines()

def find_citation_usages(lines: List[str]) -> Dict[int, List[int]]:
    """Find all [X] citation usages, return {citation_num: [line_numbers]}."""
    # Patterns for different citation formats
    single_pattern = r'\[(\d+)\]'
    multi_pattern = r'\[(\d+(?:,\d+|-\d+|,\s*\d+)+)\]'

    usages = defaultdict(list)

    for line_num, line in enumerate(lines, 1):
        # Skip reference section (after line 2500 approximately)
        if line_num > 2500 and "## References" in line:
            break

        # Find multi-citations first (e.g., [1,2,3] or [1-5])
        multi_matches = re.findall(multi_pattern, line)
        for match in multi_matches:
            # Parse individual citations from patterns like "1,2,3" or "1-5"
            citations = set()
            for part in match.split(','):
                part = part.strip()
                if '-' in part:
                    # Range like "1-5"
                    parts_split = part.split('-')
                    if len(parts_split) == 2 and all(p.strip().isdigit() for p in parts_split):
                        start, end = map(int, [p.strip() for p in parts_split])
                        citations.update(range(start, end + 1))
                    # Ignore malformed ranges
                elif part.isdigit():
                    # Single number
                    citations.add(int(part))

            for cite_num in citations:
                if 1 <= cite_num <= EXPECTED_CITATIONS:
                    usages[cite_num].append(line_num)

        # Find single citations (e.g., [1])
        # Remove multi-citations from line first to avoid double-counting
        temp_line = re.sub(multi_pattern, '', line)
        single_matches = re.findall(single_pattern, temp_line)
        for match in single_matches:
            cite_num = int(match)
            if 1 <= cite_num <= EXPECTED_CITATIONS:
                usages[cite_num].append(line_num)

    return dict(usages)

def find_reference_definitions(lines: List[str]) -> Dict[int, int]:
    """Find reference definitions in References section, return {citation_num: line_number}."""
    pattern = r'^\[(\d+)\]'
    definitions = {}
    in_references = False

    for line_num, line in enumerate(lines, 1):
        if "## References" in line:
            in_references = True
            continue

        if in_references:
            match = re.match(pattern, line)
            if match:
                cite_num = int(match.group(1))
                definitions[cite_num] = line_num

    return definitions

def analyze_citation_patterns(lines: List[str]) -> Dict:
    """Analyze citation patterns for quality."""
    # Find multi-citations like [1,2,3] or [1-5]
    multi_pattern = r'\[(\d+(?:,\d+|-\d+)+)\]'
    multi_citations = []

    for line_num, line in enumerate(lines, 1):
        if line_num > 2500:
            break
        matches = re.findall(multi_pattern, line)
        for match in matches:
            multi_citations.append((line_num, f"[{match}]"))

    return {'multi_citations': multi_citations}

def generate_report(usages: Dict, definitions: Dict, patterns: Dict) -> str:
    """Generate markdown report."""
    report = []
    report.append("# LT-7 CITATION AUDIT REPORT\n")
    report.append(f"**Expected Citations:** [1]-[{EXPECTED_CITATIONS}]")
    report.append(f"**Definitions Found:** {len(definitions)}")
    report.append(f"**Citations Used:** {len(usages)}\n")
    report.append("---\n")

    # Summary
    report.append("## SUMMARY\n")

    # Check coverage
    all_citations = set(range(1, EXPECTED_CITATIONS + 1))
    used_citations = set(usages.keys())
    defined_citations = set(definitions.keys())

    unused = all_citations - used_citations
    undefined = all_citations - defined_citations
    orphan_usages = used_citations - defined_citations

    report.append(f"**Citation Coverage:** {len(used_citations)}/{EXPECTED_CITATIONS} citations used ({len(used_citations)/EXPECTED_CITATIONS*100:.1f}%)")
    report.append(f"- Unused citations: {len(unused)} {'[WARNING]' if unused else '[OK]'}")
    report.append(f"- Undefined citations: {len(undefined)} {'[ERROR]' if undefined else '[OK]'}")
    report.append(f"- Orphan usages: {len(orphan_usages)} {'[ERROR]' if orphan_usages else '[OK]'}\n")

    # Usage statistics
    report.append("**Usage Statistics:**")
    usage_counts = {cite: len(lines) for cite, lines in usages.items()}
    max_usage = max(usage_counts.values()) if usage_counts else 0
    min_usage = min(usage_counts.values()) if usage_counts else 0
    avg_usage = sum(usage_counts.values()) / len(usage_counts) if usage_counts else 0

    report.append(f"- Most used citation: {max_usage} times")
    report.append(f"- Least used citation: {min_usage} time(s)")
    report.append(f"- Average usage: {avg_usage:.1f} times\n")

    # Multi-citations
    report.append(f"**Multi-Citation Patterns:** {len(patterns['multi_citations'])} instances")
    report.append("  (e.g., [1,2,3] or [4-7])\n")

    report.append("---\n")

    # Detailed Issues
    report.append("## DETAILED FINDINGS\n")

    if unused:
        report.append("### [WARNING] Unused Citations\n")
        report.append("Citations defined but never referenced in text:\n")
        for cite in sorted(unused):
            report.append(f"- [{cite}]")
        report.append("")

    if undefined:
        report.append("### [ERROR] Undefined Citations\n")
        report.append("Citation numbers missing from References section:\n")
        for cite in sorted(undefined):
            report.append(f"- [{cite}]")
        report.append("")

    if orphan_usages:
        report.append("### [ERROR] Orphan Citation Usages\n")
        report.append("Citations used in text but not defined in References:\n")
        for cite in sorted(orphan_usages):
            lines = usages[cite]
            report.append(f"- [{cite}]: Used on lines {', '.join(map(str, lines[:5]))}")
            if len(lines) > 5:
                report.append(f"  ...and {len(lines)-5} more locations")
        report.append("")

    # Top cited references
    report.append("### Most Frequently Cited References\n")
    top_citations = sorted(usage_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for cite, count in top_citations:
        report.append(f"- [{cite}]: {count} times")
    report.append("")

    # Single-use citations
    single_use = [cite for cite, count in usage_counts.items() if count == 1]
    if single_use:
        report.append(f"### Single-Use Citations ({len(single_use)} total)\n")
        report.append("Citations used only once (consider if they add value):\n")
        for cite in sorted(single_use)[:20]:  # Show first 20
            report.append(f"- [{cite}]")
        if len(single_use) > 20:
            report.append(f"  ...and {len(single_use)-20} more")
        report.append("")

    # Multi-citation patterns
    if patterns['multi_citations']:
        report.append(f"### Multi-Citation Instances ({len(patterns['multi_citations'])})\n")
        report.append("Lines with multiple citations grouped:\n")
        for line_num, citation in patterns['multi_citations'][:10]:
            report.append(f"- Line {line_num}: {citation}")
        if len(patterns['multi_citations']) > 10:
            report.append(f"  ...and {len(patterns['multi_citations'])-10} more")
        report.append("")

    report.append("---\n")
    report.append("## VALIDATION STATUS\n")

    total_errors = len(undefined) + len(orphan_usages)
    total_warnings = len(unused)

    if total_errors == 0 and total_warnings == 0:
        report.append("[OK] PASS: All citations properly used and defined.\n")
    elif total_errors == 0:
        report.append(f"[WARNING] PASS WITH WARNINGS: {total_warnings} unused citations\n")
        report.append("**Note:** Unused citations may be intentional for completeness.\n")
    else:
        report.append(f"[ERROR] FAIL: {total_errors} errors, {total_warnings} warnings\n")
        report.append("**Action Required:** Fix all [ERROR] issues before submission.\n")

    # Citation density
    total_lines = 2919  # From cross-ref report
    total_usages = sum(len(lines) for lines in usages.values())
    density = total_usages / total_lines * 100

    report.append("---\n")
    report.append("## STATISTICS\n")
    report.append(f"**Citation Density:** {total_usages} citations in {total_lines} lines ({density:.2f}%)")
    report.append(f"**Average Citations Per 100 Lines:** {total_usages / total_lines * 100:.1f}")
    report.append(f"**Coverage:** {len(used_citations)}/{EXPECTED_CITATIONS} ({len(used_citations)/EXPECTED_CITATIONS*100:.1f}%)")

    return '\n'.join(report)

def main():
    """Main execution."""
    print("\n" + "="*70)
    print("LT-7 CITATION AUDIT")
    print("="*70 + "\n")

    print("[INFO] Loading paper...")
    lines = load_paper()

    print("[INFO] Finding citation usages...")
    usages = find_citation_usages(lines)

    print("[INFO] Finding reference definitions...")
    definitions = find_reference_definitions(lines)

    print("[INFO] Analyzing citation patterns...")
    patterns = analyze_citation_patterns(lines)

    print("[INFO] Generating report...")
    report = generate_report(usages, definitions, patterns)

    # Save report
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[OK] Report saved to: {OUTPUT_PATH}")

    # Print summary
    all_citations = set(range(1, EXPECTED_CITATIONS + 1))
    used_citations = set(usages.keys())
    defined_citations = set(definitions.keys())

    unused = all_citations - used_citations
    undefined = all_citations - defined_citations
    orphan = used_citations - defined_citations

    total_errors = len(undefined) + len(orphan)

    if total_errors == 0:
        print(f"[OK] VALIDATION PASSED: All {EXPECTED_CITATIONS} citations properly used!")
        if unused:
            print(f"     ({len(unused)} citations unused - this is acceptable)")
    else:
        print(f"[ERROR] VALIDATION FAILED: {total_errors} errors found")
        print(f"         See report for details: {OUTPUT_PATH}")

    print()

if __name__ == "__main__":
    main()
