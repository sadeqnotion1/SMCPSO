#!/usr/bin/env python3
"""
Documentation validation script for split documentation projects.

Analyzes build output, categorizes warnings, and validates documentation health.

Usage:
    python scripts/check_docs.py                   # Check all projects
    python scripts/check_docs.py --project user    # Check user docs only
    python scripts/check_docs.py --baseline        # Save current counts as baseline
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Project definitions
PROJECTS = {
    'user': 'docs-user',
    'api': 'docs-api',
    'dev': 'docs-dev'
}

# Warning patterns (regex)
WARNING_PATTERNS = {
    'pygments_lexer': r"WARNING: Pygments lexer name '(.+?)' is not known",
    'cross_reference': r"WARNING:.*?cross-reference target not found",
    'mermaid_directive': r"WARNING: Unknown directive type: 'mermaid'",
    'header_structure': r"WARNING: Non-consecutive header level increase",
    'missing_equation': r"WARNING: equation not found: (.+)",
    'undefined_label': r"WARNING: undefined label:",
    'lexing_error': r"WARNING: Lexing literal_block",
    'unknown_document': r"WARNING: Unknown source document",
    'toc_not_included': r"WARNING:.*?isn't included in any toctree",
    'bibtex_missing': r"WARNING: could not find bibtex key",
}

def get_repo_root() -> Path:
    """Get repository root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.resolve()

def get_baseline_file() -> Path:
    """Get path to warning baseline file."""
    return get_repo_root() / '.artifacts' / 'warning_baseline.json'

def run_build_capture_output(project: str) -> Tuple[bool, str]:
    """
    Run Sphinx build and capture all output.

    Args:
        project: Project key ('user', 'api', 'dev')

    Returns:
        Tuple of (success, output_text)
    """
    repo_root = get_repo_root()
    project_dir = repo_root / PROJECTS[project]

    print(f"[i] Building {project} to capture warnings...")

    try:
        result = subprocess.run(
            ['sphinx-build', '-b', 'html', '.', '_build/html'],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False
        )

        return (result.returncode == 0, result.stdout + result.stderr)

    except Exception as e:
        print(f"[ERROR] Build failed: {e}")
        return (False, str(e))

def categorize_warnings(output: str) -> Dict[str, List[str]]:
    """
    Categorize warnings from Sphinx build output.

    Args:
        output: Build output text

    Returns:
        Dict mapping category to list of warning messages
    """
    warnings = defaultdict(list)

    for line in output.split('\n'):
        if 'WARNING:' not in line:
            continue

        # Try to match against known patterns
        categorized = False
        for category, pattern in WARNING_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                warnings[category].append(line.strip())
                categorized = True
                break

        # Uncategorized warning
        if not categorized and 'WARNING:' in line:
            warnings['other'].append(line.strip())

    return dict(warnings)

def validate_build_outputs(project: str) -> Dict[str, any]:
    """
    Validate that build produced expected outputs.

    Args:
        project: Project key ('user', 'api', 'dev')

    Returns:
        Dict with validation results
    """
    repo_root = get_repo_root()
    build_dir = repo_root / PROJECTS[project] / '_build' / 'html'

    checks = {}

    # Check critical files exist
    checks['index_exists'] = (build_dir / 'index.html').exists()
    checks['genindex_exists'] = (build_dir / 'genindex.html').exists()
    checks['static_exists'] = (build_dir / '_static').is_dir()
    checks['search_exists'] = (build_dir / 'search.html').exists()

    # Check index.html size
    if checks['index_exists']:
        index_size = (build_dir / 'index.html').stat().st_size
        checks['index_size'] = index_size
        checks['index_size_ok'] = index_size > 50_000  # At least 50 KB
    else:
        checks['index_size'] = 0
        checks['index_size_ok'] = False

    # Check for build artifacts
    checks['doctrees_exists'] = (repo_root / PROJECTS[project] / '_build' / '.doctrees').is_dir()

    return checks

def print_project_report(project: str, warnings: Dict[str, List[str]], validation: Dict[str, any]):
    """Print health report for a single project."""
    print("\n" + "="*80)
    print(f"Documentation Health Report: {project.upper()}")
    print("="*80)

    # Build status
    all_checks_pass = all(v for k, v in validation.items() if k.endswith('_ok') or k.endswith('_exists'))
    status = "[OK]" if all_checks_pass else "[WARN]"
    print(f"\nBuild Validation: {status}")
    print(f"  index.html: {'✓' if validation['index_exists'] else '✗'} ({validation.get('index_size', 0) / 1024:.1f} KB)")
    print(f"  genindex.html: {'✓' if validation['genindex_exists'] else '✗'}")
    print(f "  _static/: {'✓' if validation['static_exists'] else '✗'}")
    print(f"  search.html: {'✓' if validation['search_exists'] else '✗'}")

    # Warning summary
    total_warnings = sum(len(w) for w in warnings.values())
    print(f"\nWarnings: {total_warnings} total")

    if warnings:
        print("\nWarning Breakdown:")
        sorted_categories = sorted(warnings.items(), key=lambda x: len(x[1]), reverse=True)
        for category, warning_list in sorted_categories:
            count = len(warning_list)
            percentage = (count / total_warnings * 100) if total_warnings > 0 else 0
            print(f"  {category:20s}: {count:4d} warnings ({percentage:5.1f}%)")

        # Show sample warnings for top category
        if sorted_categories:
            top_category, top_warnings = sorted_categories[0]
            print(f"\nSample {top_category} warnings (first 3):")
            for warning in top_warnings[:3]:
                # Truncate long warnings
                if len(warning) > 100:
                    warning = warning[:97] + "..."
                print(f"  - {warning}")

    print("="*80)

def save_baseline(baseline_data: Dict[str, Dict[str, int]]):
    """Save warning counts as baseline for trend tracking."""
    baseline_file = get_baseline_file()
    baseline_file.parent.mkdir(parents=True, exist_ok=True)

    with open(baseline_file, 'w') as f:
        json.dump(baseline_data, f, indent=2)

    print(f"\n[i] Baseline saved to {baseline_file}")

def load_baseline() -> Dict[str, Dict[str, int]]:
    """Load baseline warning counts."""
    baseline_file = get_baseline_file()

    if not baseline_file.exists():
        return {}

    with open(baseline_file, 'r') as f:
        return json.load(f)

def compare_to_baseline(project: str, current_warnings: Dict[str, List[str]]):
    """Compare current warnings to baseline."""
    baseline = load_baseline()

    if not baseline or project not in baseline:
        print(f"\n[i] No baseline found for {project}. Run with --baseline to create one.")
        return

    print(f"\n{'='*80}")
    print(f"Trend Analysis: {project.upper()}")
    print(f"{'='*80}")

    baseline_total = baseline[project].get('total', 0)
    current_total = sum(len(w) for w in current_warnings.values())
    diff = current_total - baseline_total
    change_pct = (diff / baseline_total * 100) if baseline_total > 0 else 0

    status = "[OK]" if diff <= 0 else "[REGR]" if diff > baseline_total * 0.1 else "[WARN]"
    print(f"Total warnings: {current_total} (baseline: {baseline_total}, Δ{diff:+d}, {change_pct:+.1f}%)")
    print(f"Status: {status}")

    if diff > baseline_total * 0.1:
        print("\n[!] WARNING: Warnings increased by >10% since baseline!")
        print("    Consider investigating and fixing new issues.")

    print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description='Check documentation build health',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/check_docs.py                   # Check all projects
  python scripts/check_docs.py --project user    # Check user docs only
  python scripts/check_docs.py --baseline        # Save current as baseline

Baseline Tracking:
  The --baseline flag saves current warning counts to .artifacts/warning_baseline.json
  Subsequent runs will compare against this baseline to detect regressions.
        """
    )

    parser.add_argument(
        '--project',
        choices=['user', 'api', 'dev'],
        help='Check specific project only'
    )
    parser.add_argument(
        '--baseline',
        action='store_true',
        help='Save current warning counts as baseline'
    )

    args = parser.parse_args()

    # Determine which projects to check
    projects = [args.project] if args.project else ['user', 'api', 'dev']

    # Collect data
    all_warnings = {}
    all_validations = {}

    for project in projects:
        success, output = run_build_capture_output(project)

        if not success:
            print(f"[ERROR] Build failed for {project}")
            continue

        warnings = categorize_warnings(output)
        validation = validate_build_outputs(project)

        all_warnings[project] = warnings
        all_validations[project] = validation

    # Print reports
    for project in projects:
        if project in all_warnings:
            print_project_report(project, all_warnings[project], all_validations[project])

            # Compare to baseline if available
            if not args.baseline:
                compare_to_baseline(project, all_warnings[project])

    # Save baseline if requested
    if args.baseline:
        baseline_data = {}
        for project, warnings in all_warnings.items():
            baseline_data[project] = {
                'total': sum(len(w) for w in warnings.values()),
                **{cat: len(warnings[cat]) for cat in warnings}
            }
        save_baseline(baseline_data)

    # Summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    total_warnings = sum(sum(len(w) for w in warnings.values()) for warnings in all_warnings.values())
    print(f"Total warnings across {len(projects)} project(s): {total_warnings}")
    print("="*80)

if __name__ == '__main__':
    main()
