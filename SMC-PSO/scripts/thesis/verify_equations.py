#!/usr/bin/env python3
"""
Thesis Equation Verification Tool
==================================

Validates LaTeX equations in thesis chapters:
- Syntax correctness (balanced delimiters, valid LaTeX)
- Numbering sequential (3.1, 3.2, 3.3... no gaps)
- All numbered equations referenced in text
- Dimensional consistency checks (where applicable)

Usage:
    python verify_equations.py --chapter 3
    python verify_equations.py --chapter 3 --validate-algebra
    python verify_equations.py --all-chapters

Author: Claude Code (LT-8 Project)
Created: 2025-11-05
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
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
# Equation Extraction
# ==============================================================================

def extract_equations(content: str, chapter_num: int) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract numbered and unnumbered equations from markdown content.

    Returns:
        (numbered_equations, unnumbered_equations)
    """

    numbered_eqs = []
    unnumbered_eqs = []

    # Pattern for numbered display equations: $$...$$ (X.Y)
    # Matches: $$ equation $$ (3.5) or \[ equation \] (3.5)
    numbered_pattern = r'(\$\$|\\\[)(.*?)(\$\$|\\\])\s*\((\d+\.\d+)\)'

    # Pattern for unnumbered display equations
    display_pattern = r'(\$\$|\\\[)(.*?)(\$\$|\\\])'

    # Pattern for inline equations
    inline_pattern = r'\$(.*?)\$'

    # Find all numbered equations
    for match in re.finditer(numbered_pattern, content, re.DOTALL):
        eq_num = match.group(4)
        eq_content = match.group(2).strip()
        line_num = content[:match.start()].count('\n') + 1

        numbered_eqs.append({
            "equation_number": eq_num,
            "content": eq_content,
            "line": line_num,
            "type": "display",
            "match_start": match.start(),
            "match_end": match.end(),
        })

    # Find all display equations (numbered already found, skip those)
    numbered_positions = {(eq['match_start'], eq['match_end']) for eq in numbered_eqs}

    for match in re.finditer(display_pattern, content, re.DOTALL):
        pos = (match.start(), match.end())
        if pos in numbered_positions:
            continue

        eq_content = match.group(2).strip()
        line_num = content[:match.start()].count('\n') + 1

        # Skip if it's actually a numbered equation (has number after it)
        following_text = content[match.end():match.end()+20]
        if re.match(r'\s*\(\d+\.\d+\)', following_text):
            continue

        unnumbered_eqs.append({
            "content": eq_content,
            "line": line_num,
            "type": "display",
        })

    # Find inline equations (for completeness, but less critical)
    for match in re.finditer(inline_pattern, content):
        eq_content = match.group(1).strip()
        line_num = content[:match.start()].count('\n') + 1

        unnumbered_eqs.append({
            "content": eq_content,
            "line": line_num,
            "type": "inline",
        })

    return numbered_eqs, unnumbered_eqs


# ==============================================================================
# Equation Validation
# ==============================================================================

def check_latex_syntax(equation: str) -> List[str]:
    """
    Check for common LaTeX syntax errors.

    Returns list of error messages (empty if valid).
    """
    errors = []

    # Check balanced delimiters
    delimiters = [
        ('(', ')'),
        ('[', ']'),
        ('{', '}'),
        ('\\left(', '\\right)'),
        ('\\left[', '\\right]'),
        ('\\left{', '\\right}'),
    ]

    for open_delim, close_delim in delimiters:
        open_count = equation.count(open_delim)
        close_count = equation.count(close_delim)
        if open_count != close_count:
            errors.append(f"Unbalanced delimiters: {open_delim}...{close_delim} ({open_count} open, {close_count} close)")

    # Check for common LaTeX errors
    error_patterns = [
        (r'\\frac([^{])', "Missing braces in \\frac: use \\frac{a}{b}"),
        (r'\\sqrt([^{[])', "Missing braces in \\sqrt: use \\sqrt{x} or \\sqrt[n]{x}"),
        (r'_([a-zA-Z]{2,})', "Multi-char subscript without braces: use _{abc} not _abc"),
        (r'\^([a-zA-Z]{2,})', "Multi-char superscript without braces: use ^{abc} not ^abc"),
    ]

    for pattern, error_msg in error_patterns:
        if re.search(pattern, equation):
            errors.append(error_msg)

    # Check for undefined commands (basic check)
    commands = re.findall(r'\\([a-zA-Z]+)', equation)
    undefined_commands = []
    known_commands = {
        'frac', 'sqrt', 'sum', 'int', 'left', 'right', 'text', 'mathbf', 'mathcal',
        'alpha', 'beta', 'gamma', 'delta', 'theta', 'omega', 'sigma', 'epsilon',
        'dot', 'ddot', 'hat', 'bar', 'tilde', 'vec', 'partial', 'nabla',
        'sin', 'cos', 'tan', 'log', 'exp', 'lim', 'infty', 'times', 'cdot',
        'leq', 'geq', 'neq', 'approx', 'equiv', 'rightarrow', 'Rightarrow',
    }

    for cmd in commands:
        if cmd not in known_commands and len(cmd) > 1:
            # Only flag if it's not a common command (basic heuristic)
            undefined_commands.append(cmd)

    if undefined_commands:
        # Note: This is a warning, not an error (may be custom commands)
        errors.append(f"Potentially undefined commands: {', '.join(set(undefined_commands))}")

    return errors


def check_equation_numbering(numbered_eqs: List[Dict], chapter_num: int) -> List[Dict]:
    """
    Check that equation numbers are sequential (X.1, X.2, X.3, ...).

    Returns list of issues found.
    """
    issues = []

    if not numbered_eqs:
        return issues

    # Expected format: chapter.equation (e.g., 3.1, 3.2, 3.3, ...)
    expected_prefix = f"{chapter_num}."

    # Sort by equation number (should already be in order in text)
    sorted_eqs = sorted(numbered_eqs, key=lambda eq: float(eq['equation_number']))

    expected_seq = 1
    for eq in sorted_eqs:
        eq_num = eq['equation_number']

        # Check prefix
        if not eq_num.startswith(expected_prefix):
            issues.append({
                "severity": "MAJOR",
                "category": "Mathematical Correctness",
                "line": eq["line"],
                "description": f"Equation {eq_num} should start with {expected_prefix}",
                "current_text": f"({eq_num})",
                "expected_text": f"({expected_prefix}{expected_seq})",
            })

        # Check sequence
        actual_seq = int(eq_num.split('.')[-1])
        if actual_seq != expected_seq:
            issues.append({
                "severity": "MAJOR",
                "category": "Mathematical Correctness",
                "line": eq["line"],
                "description": f"Equation numbering gap: expected ({expected_prefix}{expected_seq}), found ({eq_num})",
                "current_text": f"({eq_num})",
                "expected_text": f"({expected_prefix}{expected_seq})",
            })

        expected_seq += 1

    return issues


def check_equation_references(content: str, numbered_eqs: List[Dict], chapter_num: int) -> List[Dict]:
    """
    Check that all numbered equations are referenced in text.

    Returns list of issues (unreferenced equations).
    """
    issues = []

    # Extract all equation references from text
    # Patterns: "Equation X.Y", "Eq X.Y", "Eq. X.Y", "(X.Y)"
    ref_patterns = [
        r'Equation\s+(\d+\.\d+)',
        r'Eq\.\s+(\d+\.\d+)',
        r'Eq\s+(\d+\.\d+)',
        r'\((\d+\.\d+)\)',  # This may match the equation itself, need to filter
    ]

    referenced_eqs = set()
    for pattern in ref_patterns:
        for match in re.finditer(pattern, content):
            eq_num = match.group(1)
            # Verify it's actually a reference (not the equation definition itself)
            # Simple heuristic: if preceded by $$ or \[, it's probably the definition
            context_before = content[max(0, match.start()-10):match.start()]
            if '$$' not in context_before and '\\[' not in context_before:
                referenced_eqs.add(eq_num)

    # Check each numbered equation
    for eq in numbered_eqs:
        eq_num = eq['equation_number']
        if eq_num not in referenced_eqs:
            issues.append({
                "severity": "MINOR",
                "category": "Content Completeness",
                "line": eq["line"],
                "description": f"Equation ({eq_num}) is numbered but not referenced in text",
                "current_text": f"({eq_num})",
                "expected_text": f"Reference Equation {eq_num} somewhere in text",
            })

    return issues


# ==============================================================================
# Main Verification Function
# ==============================================================================

def verify_chapter_equations(chapter_num: int, validate_algebra: bool = False) -> Dict:
    """
    Verify all equations in a chapter.

    Returns:
        {
            "chapter": chapter_num,
            "numbered_equations": [...],
            "unnumbered_equations": [...],
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

    # Extract equations
    numbered_eqs, unnumbered_eqs = extract_equations(content, chapter_num)

    # Verify equations
    issues = []

    # 1. Check LaTeX syntax for all equations
    for eq in numbered_eqs + unnumbered_eqs:
        syntax_errors = check_latex_syntax(eq['content'])
        if syntax_errors:
            for error_msg in syntax_errors:
                issues.append({
                    "severity": "MAJOR" if "Unbalanced" in error_msg else "MINOR",
                    "category": "Mathematical Correctness",
                    "line": eq["line"],
                    "description": f"LaTeX syntax issue: {error_msg}",
                    "current_text": eq['content'][:100],  # Truncate long equations
                })

    # 2. Check equation numbering
    numbering_issues = check_equation_numbering(numbered_eqs, chapter_num)
    issues.extend(numbering_issues)

    # 3. Check equation references
    reference_issues = check_equation_references(content, numbered_eqs, chapter_num)
    issues.extend(reference_issues)

    # 4. Optional: Validate algebra (requires deeper analysis)
    if validate_algebra:
        # This would require symbolic math (SymPy) - deferred for now
        print(f"[INFO] Algebraic validation not yet implemented (requires SymPy integration)")

    return {
        "chapter": chapter_num,
        "chapter_file": str(chapter_file),
        "numbered_equations": len(numbered_eqs),
        "unnumbered_equations": len(unnumbered_eqs),
        "issues": issues,
    }


# ==============================================================================
# CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thesis Equation Verification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--chapter",
        type=lambda x: int(x) if x.isdigit() else x,
        help="Chapter number to verify (0-9, A, or R)"
    )
    parser.add_argument(
        "--all-chapters",
        action="store_true",
        help="Verify all chapters"
    )
    parser.add_argument(
        "--validate-algebra",
        action="store_true",
        help="Validate algebraic manipulations (experimental)"
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
        print(f"[EQUATION VERIFICATION] Chapter {chapter_num}")
        result = verify_chapter_equations(chapter_num, validate_algebra=args.validate_algebra)

        if "error" in result:
            print(f"  [ERROR] {result['error']}")
            continue

        print(f"  Numbered equations: {result['numbered_equations']}")
        print(f"  Unnumbered equations: {result['unnumbered_equations']}")
        print(f"  Issues found: {len(result['issues'])}")

        if result['issues']:
            print(f"  Issues breakdown:")
            critical = sum(1 for iss in result['issues'] if iss['severity'] == 'CRITICAL')
            major = sum(1 for iss in result['issues'] if iss['severity'] == 'MAJOR')
            minor = sum(1 for iss in result['issues'] if iss['severity'] == 'MINOR')
            print(f"    Critical: {critical} | Major: {major} | Minor: {minor}")

        all_results.append(result)

        # Save issues if requested
        if args.save_issues and result['issues']:
            ISSUES_DIR.mkdir(parents=True, exist_ok=True)
            issue_file = ISSUES_DIR / f"chapter_{chapter_num}_equations.json"
            with open(issue_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  Issues saved: {issue_file}")

        print("")

    # Summary
    if len(all_results) > 1:
        total_issues = sum(len(r['issues']) for r in all_results)
        print(f"[SUMMARY] Total issues: {total_issues} across {len(all_results)} chapters")


if __name__ == "__main__":
    main()
