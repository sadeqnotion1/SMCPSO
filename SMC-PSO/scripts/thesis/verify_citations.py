#!/usr/bin/env python3
"""
Thesis Citation Verification Tool
==================================

Validates citations in thesis chapters:
- All citation numbers [1-40] exist in references.md
- No orphan citations (cited but not in references)
- All references cited at least once
- Citation sequencing (mostly increasing order)

Usage:
    python verify_citations.py --chapter 2
    python verify_citations.py --all-chapters
    python verify_citations.py --references

Author: Claude Code (LT-8 Project)
Created: 2025-11-05
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple
import json

# ==============================================================================
# Constants
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THESIS_DIR = PROJECT_ROOT / "docs" / "thesis" / "chapters"
REFERENCES_FILE = THESIS_DIR / "references.md"
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
# Citation Extraction
# ==============================================================================

def extract_citations(content: str) -> List[Tuple[int, int, int]]:
    """
    Extract all citation references from content.

    Returns:
        List of (citation_num, line_num, position) tuples
    """
    citations = []

    # Pattern: [1], [2], [3-5], [10,12], etc.
    # Matches: [N] where N is a number or range/list
    citation_pattern = r'\[(\d+(?:[-,]\d+)*)\]'

    for match in re.finditer(citation_pattern, content):
        citation_str = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        position = match.start()

        # Parse citation (may be single, range, or list)
        citation_nums = parse_citation_string(citation_str)

        for num in citation_nums:
            citations.append((num, line_num, position))

    return citations


def parse_citation_string(citation_str: str) -> List[int]:
    """
    Parse citation string into list of citation numbers.

    Examples:
        "1" -> [1]
        "3-5" -> [3, 4, 5]
        "10,12,15" -> [10, 12, 15]
    """
    nums = []

    # Split by comma
    parts = citation_str.split(',')

    for part in parts:
        part = part.strip()

        # Check for range (e.g., "3-5")
        if '-' in part:
            start, end = part.split('-')
            nums.extend(range(int(start), int(end) + 1))
        else:
            nums.append(int(part))

    return nums


def extract_references(references_file: Path) -> Dict[int, Dict]:
    """
    Extract all references from references.md.

    Returns:
        Dict mapping citation number to reference metadata
    """
    if not references_file.exists():
        print(f"[ERROR] References file not found: {references_file}")
        return {}

    with open(references_file, "r", encoding="utf-8") as f:
        content = f.read()

    references = {}

    # Pattern: [1] Author, "Title", Journal/Conference, Year.
    # Or: **[1]** Author, "Title", ...
    ref_pattern = r'(?:\*\*)?\[(\d+)\](?:\*\*)?\s+(.*?)(?=(?:\*\*)?\[\d+\]|\Z)'

    for match in re.finditer(ref_pattern, content, re.DOTALL):
        ref_num = int(match.group(1))
        ref_text = match.group(2).strip()
        line_num = content[:match.start()].count('\n') + 1

        references[ref_num] = {
            "number": ref_num,
            "text": ref_text[:200],  # Truncate long references
            "line": line_num,
        }

    return references


# ==============================================================================
# Citation Validation
# ==============================================================================

def check_citations_exist(citations: List[Tuple[int, int, int]], references: Dict[int, Dict]) -> List[Dict]:
    """
    Check that all cited numbers exist in references.

    Returns list of issues (missing references).
    """
    issues = []

    for cite_num, line, pos in citations:
        if cite_num not in references:
            issues.append({
                "severity": "CRITICAL",
                "category": "Technical Accuracy",
                "line": line,
                "description": f"Citation [{cite_num}] not found in references.md",
                "current_text": f"[{cite_num}]",
                "expected_text": f"Add [{cite_num}] to references.md or remove citation",
            })

    return issues


def check_uncited_references(all_citations: Set[int], references: Dict[int, Dict]) -> List[Dict]:
    """
    Check for references that are never cited.

    Returns list of issues (uncited references).
    """
    issues = []

    for ref_num, ref_data in references.items():
        if ref_num not in all_citations:
            issues.append({
                "severity": "MINOR",
                "category": "Content Completeness",
                "line": ref_data["line"],
                "description": f"Reference [{ref_num}] is listed but never cited in thesis",
                "current_text": f"[{ref_num}] {ref_data['text'][:100]}...",
                "expected_text": f"Cite [{ref_num}] somewhere or remove from references",
            })

    return issues


def check_citation_sequence(citations: List[Tuple[int, int, int]], chapter_num: int) -> List[Dict]:
    """
    Check that citations appear in mostly increasing order.

    Note: Not strictly enforced, but flagged as a style issue.

    Returns list of issues (out-of-order citations).
    """
    issues = []

    if len(citations) < 2:
        return issues

    # Check for large backward jumps (e.g., [25] followed by [3])
    for i in range(1, len(citations)):
        prev_num, prev_line, _ = citations[i-1]
        curr_num, curr_line, _ = citations[i]

        # Flag if current citation is more than 10 numbers behind previous
        if curr_num < prev_num - 10:
            issues.append({
                "severity": "MINOR",
                "category": "Formatting Consistency",
                "line": curr_line,
                "description": f"Citation [{curr_num}] appears after [{prev_num}] (consider reordering for readability)",
                "current_text": f"[{curr_num}]",
                "expected_text": "Citations should generally appear in increasing order",
            })

    return issues


# ==============================================================================
# Main Verification Function
# ==============================================================================

def verify_chapter_citations(chapter_num: int, references: Dict[int, Dict]) -> Dict:
    """
    Verify all citations in a chapter.

    Returns:
        {
            "chapter": chapter_num,
            "citations_count": int,
            "unique_citations": int,
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

    # Extract citations
    citations = extract_citations(content)
    unique_citations = set(num for num, _, _ in citations)

    # Verify citations
    issues = []

    # 1. Check all citations exist in references
    existence_issues = check_citations_exist(citations, references)
    issues.extend(existence_issues)

    # 2. Check citation sequencing (style)
    sequence_issues = check_citation_sequence(citations, chapter_num)
    issues.extend(sequence_issues)

    return {
        "chapter": chapter_num,
        "chapter_file": str(chapter_file),
        "citations_count": len(citations),
        "unique_citations": len(unique_citations),
        "citation_numbers": sorted(unique_citations),
        "issues": issues,
    }


def verify_references() -> Dict:
    """
    Verify the references.md file.

    Returns:
        {
            "references_count": int,
            "reference_numbers": [1, 2, 3, ...],
            "issues": [...]
        }
    """

    references = extract_references(REFERENCES_FILE)

    issues = []

    if not references:
        issues.append({
            "severity": "CRITICAL",
            "category": "Content Completeness",
            "line": 0,
            "description": "No references found in references.md",
            "current_text": "",
            "expected_text": "Add references [1-40]",
        })
        return {
            "references_count": 0,
            "reference_numbers": [],
            "issues": issues,
        }

    # Check reference numbering (should be sequential: 1, 2, 3, ...)
    ref_nums = sorted(references.keys())
    expected_seq = list(range(1, len(ref_nums) + 1))

    if ref_nums != expected_seq:
        # Find gaps
        all_nums = set(ref_nums)
        expected_nums = set(expected_seq)
        missing = expected_nums - all_nums
        extra = all_nums - expected_nums

        if missing:
            issues.append({
                "severity": "MAJOR",
                "category": "Formatting Consistency",
                "line": 0,
                "description": f"Missing reference numbers: {sorted(missing)}",
                "current_text": f"References: {ref_nums}",
                "expected_text": f"References should be sequential: {expected_seq}",
            })

        if extra:
            issues.append({
                "severity": "MINOR",
                "category": "Formatting Consistency",
                "line": 0,
                "description": f"Unexpected reference numbers: {sorted(extra)}",
                "current_text": f"References: {ref_nums}",
                "expected_text": f"References should be sequential: {expected_seq}",
            })

    return {
        "references_count": len(references),
        "reference_numbers": ref_nums,
        "issues": issues,
    }


def verify_all_citations() -> Dict:
    """
    Verify citations across all chapters + references.

    Returns comprehensive report.
    """

    # Load references first
    references = extract_references(REFERENCES_FILE)

    if not references:
        print("[ERROR] Cannot verify citations without references.md")
        return {"error": "references.md not found or empty"}

    # Verify each chapter
    chapter_results = []
    all_citations = set()

    for ch in CHAPTERS:
        result = verify_chapter_citations(ch["num"], references)
        if "error" not in result:
            chapter_results.append(result)
            all_citations.update(result["citation_numbers"])

    # Verify references
    ref_result = verify_references()

    # Check for uncited references
    uncited_issues = check_uncited_references(all_citations, references)

    # Aggregate results
    total_issues = sum(len(r["issues"]) for r in chapter_results) + len(ref_result["issues"]) + len(uncited_issues)

    return {
        "chapter_results": chapter_results,
        "references_result": ref_result,
        "uncited_issues": uncited_issues,
        "total_issues": total_issues,
        "all_citations": sorted(all_citations),
        "citation_coverage": f"{len(all_citations)}/{len(references)} references cited",
    }


# ==============================================================================
# CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thesis Citation Verification Tool",
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
        "--references",
        action="store_true",
        help="Verify references.md only"
    )
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Comprehensive verification (all chapters + references + uncited)"
    )
    parser.add_argument(
        "--save-issues",
        action="store_true",
        help="Save issues to .artifacts/thesis/issues/"
    )

    args = parser.parse_args()

    # Load references (needed for most operations)
    references = extract_references(REFERENCES_FILE)

    if args.comprehensive or args.all_chapters:
        print("[CITATION VERIFICATION] Comprehensive check")
        result = verify_all_citations()

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        print(f"Total issues: {result['total_issues']}")
        print(f"Citation coverage: {result['citation_coverage']}")
        print(f"Citations used: {result['all_citations']}")
        print("")

        # Show chapter breakdowns
        for ch_result in result["chapter_results"]:
            ch_num = ch_result["chapter"]
            issues_count = len(ch_result["issues"])
            print(f"Chapter {ch_num}: {ch_result['citations_count']} citations, {issues_count} issues")

        # Show uncited references
        if result["uncited_issues"]:
            print(f"\nUncited references: {len(result['uncited_issues'])}")

        # Save if requested
        if args.save_issues:
            ISSUES_DIR.mkdir(parents=True, exist_ok=True)
            issue_file = ISSUES_DIR / "citations_comprehensive.json"
            with open(issue_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nIssues saved: {issue_file}")

    elif args.references:
        print("[CITATION VERIFICATION] References only")
        result = verify_references()

        print(f"References found: {result['references_count']}")
        print(f"Reference numbers: {result['reference_numbers']}")
        print(f"Issues: {len(result['issues'])}")

        if result['issues']:
            for issue in result['issues']:
                print(f"  - {issue['severity']}: {issue['description']}")

    elif args.chapter is not None:
        print(f"[CITATION VERIFICATION] Chapter {args.chapter}")
        result = verify_chapter_citations(args.chapter, references)

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        print(f"Citations: {result['citations_count']} ({result['unique_citations']} unique)")
        print(f"Citation numbers: {result['citation_numbers']}")
        print(f"Issues: {len(result['issues'])}")

        if result['issues']:
            critical = sum(1 for iss in result['issues'] if iss['severity'] == 'CRITICAL')
            major = sum(1 for iss in result['issues'] if iss['severity'] == 'MAJOR')
            minor = sum(1 for iss in result['issues'] if iss['severity'] == 'MINOR')
            print(f"  Critical: {critical} | Major: {major} | Minor: {minor}")

        # Save if requested
        if args.save_issues and result['issues']:
            ISSUES_DIR.mkdir(parents=True, exist_ok=True)
            issue_file = ISSUES_DIR / f"chapter_{args.chapter}_citations.json"
            with open(issue_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Issues saved: {issue_file}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
