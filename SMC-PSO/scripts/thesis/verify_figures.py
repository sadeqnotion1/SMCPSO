#!/usr/bin/env python3
"""
Thesis Figure & Table Verification Tool
========================================

Validates figures and tables in thesis chapters:
- All figures have captions (Figure X.Y: Description)
- All tables have captions (Table X.Y: Description)
- Numbering sequential (X.1, X.2, X.3... no gaps)
- All figures/tables referenced in text
- No broken references (Figure X.Y referenced but doesn't exist)

Usage:
    python verify_figures.py --chapter 3
    python verify_figures.py --all-chapters

Author: Claude Code (LT-8 Project)
Created: 2025-11-05
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set
import json

# ==============================================================================
# Constants
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THESIS_DIR = PROJECT_ROOT / "docs" / "thesis" / "chapters"
ISSUES_DIR = PROJECT_ROOT / ".artifacts" / "thesis" / "issues"

CHAPTERS = [
    {"num": 0, "file": "00_introduction.md"},
    {"num": 1, "file": "01_problem_statement.md"},
    {"num": 2, "file": "02_literature_review.md"},
    {"num": 3, "file": "03_system_modeling.md"},
    {"num": 4, "file": "04_sliding_mode_control.md"},
    {"num": 5, "file": "05_chattering_mitigation.md"},
    {"num": 6, "file": "06_pso_optimization.md"},
    {"num": 7, "file": "07_simulation_setup.md"},
    {"num": 8, "file": "08_results.md"},
    {"num": 9, "file": "09_conclusion.md"},
    {"num": "A", "file": "appendix_a_proofs.md"},
]

# ==============================================================================
# Figure & Table Extraction
# ==============================================================================

def extract_figures(content: str, chapter_num: int) -> List[Dict]:
    """
    Extract all figure definitions (with captions) from content.

    Patterns:
        **Figure X.Y**: Description
        Figure X.Y: Description
        ![alt](path) (markdown image)
    """
    figures = []

    # Pattern 1: **Figure X.Y**: Description
    # Pattern 2: Figure X.Y: Description (no bold)
    fig_pattern = r'(?:\*\*)?Figure\s+(\d+\.\d+)(?:\*\*)?\s*[:\-]\s*(.*?)(?=\n|$)'

    for match in re.finditer(fig_pattern, content, re.MULTILINE):
        fig_num = match.group(1)
        caption = match.group(2).strip()
        line_num = content[:match.start()].count('\n') + 1

        figures.append({
            "number": fig_num,
            "caption": caption,
            "line": line_num,
            "type": "figure",
        })

    # Pattern 3: Markdown images (may or may not have figure numbers)
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    for match in re.finditer(img_pattern, content):
        alt_text = match.group(1)
        img_path = match.group(2)
        line_num = content[:match.start()].count('\n') + 1

        # Check if this image is labeled as a figure
        # Look for "Figure X.Y" in alt text or nearby text
        nearby_text = content[max(0, match.start()-100):match.end()+100]
        fig_match = re.search(r'Figure\s+(\d+\.\d+)', nearby_text)

        if fig_match:
            fig_num = fig_match.group(1)
            # Check if already captured
            if not any(f['number'] == fig_num and abs(f['line'] - line_num) < 3 for f in figures):
                figures.append({
                    "number": fig_num,
                    "caption": alt_text,
                    "line": line_num,
                    "type": "figure",
                    "image_path": img_path,
                })

    return figures


def extract_tables(content: str, chapter_num: int) -> List[Dict]:
    """
    Extract all table definitions (with captions) from content.

    Patterns:
        **Table X.Y**: Description
        Table X.Y: Description
    """
    tables = []

    # Pattern: **Table X.Y**: Description
    table_pattern = r'(?:\*\*)?Table\s+(\d+\.\d+)(?:\*\*)?\s*[:\-]\s*(.*?)(?=\n|$)'

    for match in re.finditer(table_pattern, content, re.MULTILINE):
        table_num = match.group(1)
        caption = match.group(2).strip()
        line_num = content[:match.start()].count('\n') + 1

        tables.append({
            "number": table_num,
            "caption": caption,
            "line": line_num,
            "type": "table",
        })

    return tables


def extract_figure_references(content: str) -> Set[str]:
    """
    Extract all figure references from text.

    Patterns:
        Figure X.Y
        Fig X.Y
        Fig. X.Y
    """
    references = set()

    # Patterns: "Figure X.Y", "Fig. X.Y", "Fig X.Y"
    ref_patterns = [
        r'Figure\s+(\d+\.\d+)',
        r'Fig\.\s+(\d+\.\d+)',
        r'Fig\s+(\d+\.\d+)',
    ]

    for pattern in ref_patterns:
        for match in re.finditer(pattern, content):
            fig_num = match.group(1)
            references.add(fig_num)

    return references


def extract_table_references(content: str) -> Set[str]:
    """
    Extract all table references from text.

    Patterns:
        Table X.Y
    """
    references = set()

    table_pattern = r'Table\s+(\d+\.\d+)'
    for match in re.finditer(table_pattern, content):
        table_num = match.group(1)
        references.add(table_num)

    return references


# ==============================================================================
# Validation Functions
# ==============================================================================

def check_numbering(items: List[Dict], item_type: str, chapter_num: int) -> List[Dict]:
    """
    Check that figure/table numbers are sequential (X.1, X.2, X.3...).

    Returns list of issues.
    """
    issues = []

    if not items:
        return issues

    expected_prefix = f"{chapter_num}."

    # Sort by number
    sorted_items = sorted(items, key=lambda x: float(x['number']))

    expected_seq = 1
    for item in sorted_items:
        item_num = item['number']

        # Check prefix
        if not item_num.startswith(expected_prefix):
            issues.append({
                "severity": "MAJOR",
                "category": "Formatting Consistency",
                "line": item["line"],
                "description": f"{item_type.capitalize()} {item_num} should start with {expected_prefix}",
                "current_text": f"{item_type.capitalize()} {item_num}",
                "expected_text": f"{item_type.capitalize()} {expected_prefix}{expected_seq}",
            })

        # Check sequence
        actual_seq = int(item_num.split('.')[-1])
        if actual_seq != expected_seq:
            issues.append({
                "severity": "MAJOR",
                "category": "Formatting Consistency",
                "line": item["line"],
                "description": f"{item_type.capitalize()} numbering gap: expected {expected_prefix}{expected_seq}, found {item_num}",
                "current_text": f"{item_type.capitalize()} {item_num}",
                "expected_text": f"{item_type.capitalize()} {expected_prefix}{expected_seq}",
            })

        expected_seq += 1

    return issues


def check_references(items: List[Dict], references: Set[str], item_type: str) -> List[Dict]:
    """
    Check that all items are referenced in text.

    Returns list of issues (unreferenced items).
    """
    issues = []

    for item in items:
        item_num = item['number']

        # Allow self-reference (the caption itself may contain the number)
        # But check if it's actually referenced elsewhere
        if item_num not in references:
            issues.append({
                "severity": "MINOR",
                "category": "Content Completeness",
                "line": item["line"],
                "description": f"{item_type.capitalize()} {item_num} is defined but not referenced in text",
                "current_text": f"{item_type.capitalize()} {item_num}: {item['caption'][:50]}...",
                "expected_text": f"Reference {item_type.capitalize()} {item_num} somewhere in text",
            })

    return issues


def check_broken_references(items: List[Dict], references: Set[str], item_type: str) -> List[Dict]:
    """
    Check for references to non-existent figures/tables.

    Returns list of issues (broken references).
    """
    issues = []

    item_nums = {item['number'] for item in items}

    for ref_num in references:
        if ref_num not in item_nums:
            issues.append({
                "severity": "CRITICAL",
                "category": "Cross-References",
                "line": 0,  # Can't determine line from references alone
                "description": f"{item_type.capitalize()} {ref_num} is referenced but does not exist",
                "current_text": f"{item_type.capitalize()} {ref_num}",
                "expected_text": f"Add {item_type.capitalize()} {ref_num} or remove reference",
            })

    return issues


def check_captions(items: List[Dict], item_type: str) -> List[Dict]:
    """
    Check that all figures/tables have non-empty captions.

    Returns list of issues (missing/empty captions).
    """
    issues = []

    for item in items:
        caption = item.get('caption', '').strip()

        if not caption or len(caption) < 10:
            issues.append({
                "severity": "MAJOR",
                "category": "Content Completeness",
                "line": item["line"],
                "description": f"{item_type.capitalize()} {item['number']} has missing or too-short caption",
                "current_text": f"{item_type.capitalize()} {item['number']}: {caption}",
                "expected_text": f"{item_type.capitalize()} {item['number']}: [descriptive caption]",
            })

    return issues


# ==============================================================================
# Main Verification Function
# ==============================================================================

def verify_chapter_figures_tables(chapter_num: int) -> Dict:
    """
    Verify all figures and tables in a chapter.

    Returns:
        {
            "chapter": chapter_num,
            "figures_count": int,
            "tables_count": int,
            "issues": [...]
        }
    """

    # Find chapter file
    chapter_file = None
    for ch in CHAPTERS:
        if ch["num"] == chapter_num:
            chapter_file = THESIS_DIR / ch["file"]
            break

    if not chapter_file or not chapter_file.exists():
        print(f"[ERROR] Chapter {chapter_num} not found: {chapter_file}")
        return {"error": f"Chapter {chapter_num} not found"}

    # Read content
    with open(chapter_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract figures and tables
    figures = extract_figures(content, chapter_num)
    tables = extract_tables(content, chapter_num)

    # Extract references
    figure_refs = extract_figure_references(content)
    table_refs = extract_table_references(content)

    # Verify
    issues = []

    # 1. Check figure numbering
    fig_numbering_issues = check_numbering(figures, "figure", chapter_num)
    issues.extend(fig_numbering_issues)

    # 2. Check table numbering
    table_numbering_issues = check_numbering(tables, "table", chapter_num)
    issues.extend(table_numbering_issues)

    # 3. Check figure captions
    fig_caption_issues = check_captions(figures, "figure")
    issues.extend(fig_caption_issues)

    # 4. Check table captions
    table_caption_issues = check_captions(tables, "table")
    issues.extend(table_caption_issues)

    # 5. Check figure references
    fig_ref_issues = check_references(figures, figure_refs, "figure")
    issues.extend(fig_ref_issues)

    # 6. Check table references
    table_ref_issues = check_references(tables, table_refs, "table")
    issues.extend(table_ref_issues)

    # 7. Check for broken references
    broken_fig_issues = check_broken_references(figures, figure_refs, "figure")
    issues.extend(broken_fig_issues)

    broken_table_issues = check_broken_references(tables, table_refs, "table")
    issues.extend(broken_table_issues)

    return {
        "chapter": chapter_num,
        "chapter_file": str(chapter_file),
        "figures_count": len(figures),
        "tables_count": len(tables),
        "figure_numbers": [f['number'] for f in figures],
        "table_numbers": [t['number'] for t in tables],
        "issues": issues,
    }


# ==============================================================================
# CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thesis Figure & Table Verification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--chapter",
        type=lambda x: int(x) if x.isdigit() else x,
        help="Chapter number to verify (0-9, A)"
    )
    parser.add_argument(
        "--all-chapters",
        action="store_true",
        help="Verify all chapters"
    )
    parser.add_argument(
        "--save-issues",
        action="store_true",
        help="Save issues to .artifacts/thesis/issues/"
    )

    args = parser.parse_args()

    if args.all_chapters:
        chapters_to_verify = [ch["num"] for ch in CHAPTERS]
    elif args.chapter is not None:
        chapters_to_verify = [args.chapter]
    else:
        parser.print_help()
        return

    all_results = []

    for chapter_num in chapters_to_verify:
        print(f"[FIGURE/TABLE VERIFICATION] Chapter {chapter_num}")
        result = verify_chapter_figures_tables(chapter_num)

        if "error" in result:
            print(f"  [ERROR] {result['error']}")
            continue

        print(f"  Figures: {result['figures_count']} ({result['figure_numbers']})")
        print(f"  Tables: {result['tables_count']} ({result['table_numbers']})")
        print(f"  Issues found: {len(result['issues'])}")

        if result['issues']:
            critical = sum(1 for iss in result['issues'] if iss['severity'] == 'CRITICAL')
            major = sum(1 for iss in result['issues'] if iss['severity'] == 'MAJOR')
            minor = sum(1 for iss in result['issues'] if iss['severity'] == 'MINOR')
            print(f"    Critical: {critical} | Major: {major} | Minor: {minor}")

        all_results.append(result)

        # Save issues if requested
        if args.save_issues and result['issues']:
            ISSUES_DIR.mkdir(parents=True, exist_ok=True)
            issue_file = ISSUES_DIR / f"chapter_{chapter_num}_figures_tables.json"
            with open(issue_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  Issues saved: {issue_file}")

        print("")

    # Summary
    if len(all_results) > 1:
        total_issues = sum(len(r['issues']) for r in all_results)
        total_figures = sum(r['figures_count'] for r in all_results)
        total_tables = sum(r['tables_count'] for r in all_results)
        print(f"[SUMMARY] {total_figures} figures, {total_tables} tables, {total_issues} issues across {len(all_results)} chapters")


if __name__ == "__main__":
    main()
