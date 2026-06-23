"""LT-7 Cross-Reference Validation Script

Validates all figure, table, section, and equation references in the research paper.
Generates detailed report with line numbers for any issues found.

Usage:
    python scripts/lt7_validate_crossrefs.py
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# Paths
PAPER_PATH = Path("benchmarks/LT7_RESEARCH_PAPER.md")
FIGURES_DIR = Path("benchmarks/figures")
OUTPUT_PATH = Path("benchmarks/LT7_CROSSREF_REPORT.md")

# Patterns
FIGURE_REF_PATTERN = r'Figure\s+(\d+(?:\.\d+)?[a-d]?)'
TABLE_REF_PATTERN = r'Table\s+(\d+(?:\.\d+)?)'
SECTION_REF_PATTERN = r'Section\s+(\d+(?:\.\d+)?)'
EQUATION_REF_PATTERN = r'(?:Eq\.|Equation)\s*\((\d+(?:\.\d+)?)\)'
FIGURE_DEF_PATTERN = r'!\[Figure\s+(\d+(?:\.\d+)?[a-d]?):'
TABLE_DEF_PATTERN = r'\*\*Table\s+(\d+(?:\.\d+)?)'
SECTION_DEF_PATTERN = r'^#{1,3}\s+(\d+(?:\.\d+)?)\.'

def load_paper() -> List[str]:
    """Load paper content as list of lines."""
    with open(PAPER_PATH, 'r', encoding='utf-8') as f:
        return f.readlines()

def find_references(lines: List[str], pattern: str) -> Dict[str, List[int]]:
    """Find all references matching pattern, return {ref_id: [line_numbers]}."""
    refs = defaultdict(list)
    for line_num, line in enumerate(lines, 1):
        matches = re.findall(pattern, line, re.IGNORECASE)
        for match in matches:
            refs[match].append(line_num)
    return dict(refs)

def find_definitions(lines: List[str], pattern: str) -> Set[str]:
    """Find all definitions (actual figures/tables/sections), return set of IDs."""
    defs = set()
    for line in lines:
        matches = re.findall(pattern, line, re.IGNORECASE)
        defs.update(matches)
    return defs

def check_figure_files() -> Dict[str, bool]:
    """Check if figure files exist."""
    expected_figures = [
        "LT7_section_5_1_pso_convergence.png",
        "MT6_pso_convergence.png",
        "LT7_section_7_1_compute_time.png",
        "LT7_section_7_2_transient_response.png",
        "LT7_section_7_3_chattering.png",
        "LT7_section_7_4_energy.png",
        "LT7_section_8_1_model_uncertainty.png",
        "LT7_section_8_2_disturbance_rejection.png",
        "LT7_section_8_3_pso_generalization.png",
        "MT7_robustness_chattering_distribution.png",
        "MT7_robustness_per_seed_variance.png",
        "MT7_robustness_success_rate.png",
        "MT7_robustness_worst_case.png",
        "MT6_performance_comparison.png"  # Extra, not referenced yet
    ]

    file_status = {}
    for fig in expected_figures:
        file_path = FIGURES_DIR / fig
        file_status[fig] = file_path.exists()

    return file_status

def validate_crossrefs() -> Dict[str, any]:
    """Main validation function."""
    print("[INFO] Loading paper...")
    lines = load_paper()

    print("[INFO] Finding figure references...")
    figure_refs = find_references(lines, FIGURE_REF_PATTERN)
    figure_defs = find_definitions(lines, FIGURE_DEF_PATTERN)

    print("[INFO] Finding table references...")
    table_refs = find_references(lines, TABLE_REF_PATTERN)
    table_defs = find_definitions(lines, TABLE_DEF_PATTERN)

    print("[INFO] Finding section references...")
    section_refs = find_references(lines, SECTION_REF_PATTERN)
    section_defs = find_definitions(lines, SECTION_DEF_PATTERN)

    print("[INFO] Finding equation references...")
    equation_refs = find_references(lines, EQUATION_REF_PATTERN)

    print("[INFO] Checking figure files...")
    figure_files = check_figure_files()

    # Validate
    results = {
        'figures': {
            'refs': figure_refs,
            'defs': figure_defs,
            'orphan_refs': set(figure_refs.keys()) - figure_defs,
            'unused_defs': figure_defs - set(figure_refs.keys()),
            'files': figure_files
        },
        'tables': {
            'refs': table_refs,
            'defs': table_defs,
            'orphan_refs': set(table_refs.keys()) - table_defs,
            'unused_defs': table_defs - set(table_refs.keys())
        },
        'sections': {
            'refs': section_refs,
            'defs': section_defs,
            'orphan_refs': set(section_refs.keys()) - section_defs,
            'unused_defs': section_defs - set(section_refs.keys())
        },
        'equations': {
            'refs': equation_refs,
            'count': len(equation_refs)
        },
        'stats': {
            'total_lines': len(lines),
            'figure_count': len(figure_defs),
            'table_count': len(table_defs),
            'section_count': len(section_defs)
        }
    }

    return results

def generate_report(results: Dict) -> str:
    """Generate markdown report."""
    report = []
    report.append("# LT-7 CROSS-REFERENCE VALIDATION REPORT\n")
    report.append(f"**Generated:** {Path(__file__).name}")
    report.append(f"**Paper:** {PAPER_PATH}")
    report.append(f"**Total Lines:** {results['stats']['total_lines']}\n")
    report.append("---\n")

    # Summary
    report.append("## SUMMARY\n")

    # Figures
    fig_orphans = len(results['figures']['orphan_refs'])
    fig_unused = len(results['figures']['unused_defs'])
    fig_missing = sum(1 for exists in results['figures']['files'].values() if not exists)

    report.append(f"**Figures:** {results['stats']['figure_count']} defined")
    report.append(f"- Orphan references: {fig_orphans} {'[ERROR]' if fig_orphans > 0 else '[OK]'}")
    report.append(f"- Unused definitions: {fig_unused} {'[WARNING]' if fig_unused > 0 else '[OK]'}")
    report.append(f"- Missing files: {fig_missing} {'[ERROR]' if fig_missing > 0 else '[OK]'}\n")

    # Tables
    tbl_orphans = len(results['tables']['orphan_refs'])
    tbl_unused = len(results['tables']['unused_defs'])

    report.append(f"**Tables:** {results['stats']['table_count']} defined")
    report.append(f"- Orphan references: {tbl_orphans} {'[ERROR]' if tbl_orphans > 0 else '[OK]'}")
    report.append(f"- Unused definitions: {tbl_unused} {'[WARNING]' if tbl_unused > 0 else '[OK]'}\n")

    # Sections
    sec_orphans = len(results['sections']['orphan_refs'])
    sec_unused = len(results['sections']['unused_defs'])

    report.append(f"**Sections:** {results['stats']['section_count']} defined")
    report.append(f"- Orphan references: {sec_orphans} {'[ERROR]' if sec_orphans > 0 else '[OK]'}")
    report.append(f"- Unused definitions: {sec_unused} {'[INFO]' if sec_unused > 0 else '[OK]'}\n")

    # Equations
    report.append(f"**Equations:** {results['equations']['count']} explicit references found")
    report.append("  (Note: Many equations use informal numbering)\n")

    report.append("---\n")

    # Detailed Issues
    report.append("## DETAILED FINDINGS\n")

    # Figure issues
    if fig_orphans > 0:
        report.append("### [ERROR] Orphan Figure References\n")
        report.append("References to figures that don't exist:\n")
        for ref in sorted(results['figures']['orphan_refs']):
            lines = results['figures']['refs'][ref]
            report.append(f"- **Figure {ref}:** Referenced on lines {', '.join(map(str, lines))}")
        report.append("")

    if fig_unused > 0:
        report.append("### [WARNING] Unused Figure Definitions\n")
        report.append("Figures defined but never referenced:\n")
        for fig_id in sorted(results['figures']['unused_defs']):
            report.append(f"- **Figure {fig_id}**")
        report.append("")

    if fig_missing > 0:
        report.append("### [ERROR] Missing Figure Files\n")
        report.append("Figure files that don't exist:\n")
        for fig, exists in sorted(results['figures']['files'].items()):
            if not exists:
                report.append(f"- {fig}")
        report.append("")

    # Table issues
    if tbl_orphans > 0:
        report.append("### [ERROR] Orphan Table References\n")
        report.append("References to tables that don't exist:\n")
        for ref in sorted(results['tables']['orphan_refs']):
            lines = results['tables']['refs'][ref]
            report.append(f"- **Table {ref}:** Referenced on lines {', '.join(map(str, lines))}")
        report.append("")

    if tbl_unused > 0:
        report.append("### [WARNING] Unused Table Definitions\n")
        report.append("Tables defined but never referenced:\n")
        for tbl_id in sorted(results['tables']['unused_defs']):
            report.append(f"- **Table {tbl_id}**")
        report.append("")

    # Section issues
    if sec_orphans > 0:
        report.append("### [ERROR] Orphan Section References\n")
        report.append("References to sections that don't exist:\n")
        for ref in sorted(results['sections']['orphan_refs']):
            lines = results['sections']['refs'][ref]
            report.append(f"- **Section {ref}:** Referenced on lines {', '.join(map(str, lines))}")
        report.append("")

    if sec_unused > 0:
        report.append("### [INFO] Unreferenced Sections\n")
        report.append("Sections never explicitly referenced (not necessarily an issue):\n")
        for sec_id in sorted(results['sections']['unused_defs']):
            report.append(f"- **Section {sec_id}**")
        report.append("")

    # Statistics
    report.append("---\n")
    report.append("## REFERENCE STATISTICS\n")

    report.append(f"**Most Referenced Figures:**")
    fig_counts = [(fig_id, len(lines)) for fig_id, lines in results['figures']['refs'].items()]
    for fig_id, count in sorted(fig_counts, key=lambda x: x[1], reverse=True)[:5]:
        report.append(f"- Figure {fig_id}: {count} references")
    report.append("")

    report.append(f"**Most Referenced Tables:**")
    tbl_counts = [(tbl_id, len(lines)) for tbl_id, lines in results['tables']['refs'].items()]
    for tbl_id, count in sorted(tbl_counts, key=lambda x: x[1], reverse=True)[:5]:
        report.append(f"- Table {tbl_id}: {count} references")
    report.append("")

    report.append(f"**Most Referenced Sections:**")
    sec_counts = [(sec_id, len(lines)) for sec_id, lines in results['sections']['refs'].items()]
    for sec_id, count in sorted(sec_counts, key=lambda x: x[1], reverse=True)[:5]:
        report.append(f"- Section {sec_id}: {count} references")
    report.append("")

    report.append("---\n")
    report.append("## VALIDATION STATUS\n")

    total_errors = fig_orphans + tbl_orphans + sec_orphans + fig_missing
    total_warnings = fig_unused + tbl_unused

    if total_errors == 0 and total_warnings == 0:
        report.append("[OK] PASS: No issues found. All cross-references valid.\n")
    elif total_errors == 0:
        report.append(f"[WARNING] PASS WITH WARNINGS: {total_warnings} warnings (non-critical)\n")
    else:
        report.append(f"[ERROR] FAIL: {total_errors} errors, {total_warnings} warnings\n")
        report.append("**Action Required:** Fix all [ERROR] issues before submission.\n")

    return '\n'.join(report)

def main():
    """Main execution."""
    print("\n" + "="*70)
    print("LT-7 CROSS-REFERENCE VALIDATION")
    print("="*70 + "\n")

    results = validate_crossrefs()
    report = generate_report(results)

    # Save report
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[OK] Report saved to: {OUTPUT_PATH}")

    # Print summary
    total_errors = (len(results['figures']['orphan_refs']) +
                   len(results['tables']['orphan_refs']) +
                   len(results['sections']['orphan_refs']) +
                   sum(1 for exists in results['figures']['files'].values() if not exists))

    if total_errors == 0:
        print("[OK] VALIDATION PASSED: All cross-references valid!")
    else:
        print(f"[ERROR] VALIDATION FAILED: {total_errors} errors found")
        print(f"         See report for details: {OUTPUT_PATH}")

    print()

if __name__ == "__main__":
    main()
