#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/fix_pygments_lexers.py
#==============================================================================
# Pygments Lexer Fixer - Phase 1, Day 2
#
# Automatically fixes invalid Pygments lexer names in code blocks.
# Invalid lexers cause "Pygments lexer name 'X' is not known" warnings.
#
# Strategy (Minimal):
#   - Simple find/replace for known invalid → valid mappings
#   - Regex-based substitution
#   - Ultra-fast, safe, and effective
#
# Known Invalid Lexers:
#   - python# → python (concatenated with option)
#   - pythonfrom → python (typo)
#   - mermaidgraph → mermaid (wrong name)
#   - yaml# → yaml (concatenated with option)
#
# Usage:
#     python scripts/docs/fix_pygments_lexers.py
#     python scripts/docs/fix_pygments_lexers.py --apply
#     python scripts/docs/fix_pygments_lexers.py --verbose
#==============================================================================
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict
from datetime import datetime


# Known invalid lexer names → correct replacements
LEXER_FIXES = {
    'python#': 'python',
    'pythonfrom': 'python',
    'mermaidgraph': 'mermaid',
    'yaml#': 'yaml',
    'json#': 'json',
    'bash#': 'bash',
    'text#': 'text',
}


def fix_lexers_in_file(
    filepath: Path,
    dry_run: bool = True,
    verbose: bool = False
) -> Dict:
    """
    Fix invalid lexer names in a single file.

    Args:
        filepath: Path to markdown file
        dry_run: If True, don't write changes
        verbose: If True, print detailed progress

    Returns:
        Dictionary with fix statistics
    """
    if verbose:
        print(f"\nProcessing: {filepath}")

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "file": str(filepath),
            "success": False,
            "error": str(e),
            "fixes_applied": 0
        }

    total_fixes = 0
    fixes_by_lexer = {}

    # Apply each fix
    for invalid_lexer, valid_lexer in LEXER_FIXES.items():
        # Pattern: ```invalid_lexer
        pattern = f'```{re.escape(invalid_lexer)}'
        replacement = f'```{valid_lexer}'

        # Count occurrences
        count = content.count(pattern)
        if count > 0:
            # Apply replacement
            content = content.replace(pattern, replacement)
            total_fixes += count
            fixes_by_lexer[invalid_lexer] = count

            if verbose:
                print(f"  Fixed {count} occurrence(s) of '```{invalid_lexer}'")

    # Write changes
    if not dry_run and total_fixes > 0:
        try:
            filepath.write_text(content, encoding='utf-8')
            if verbose:
                print(f"  [OK] Wrote changes to {filepath}")
        except Exception as e:
            return {
                "file": str(filepath),
                "success": False,
                "error": f"Failed to write: {e}",
                "fixes_applied": 0
            }
    elif dry_run and total_fixes > 0:
        if verbose:
            print(f"  [DRY RUN] Would fix {total_fixes} lexer(s)")

    return {
        "file": str(filepath),
        "success": True,
        "fixes_applied": total_fixes,
        "fixes_by_lexer": fixes_by_lexer,
        "dry_run": dry_run
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fix invalid Pygments lexer names in code blocks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default)
  python scripts/docs/fix_pygments_lexers.py

  # Apply fixes
  python scripts/docs/fix_pygments_lexers.py --apply

  # Verbose output
  python scripts/docs/fix_pygments_lexers.py --apply --verbose

Known invalid lexers that will be fixed:
  python# → python
  pythonfrom → python
  mermaidgraph → mermaid
  yaml# → yaml
        """
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory (default: docs)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply fixes (default is dry-run)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".artifacts/lexer_fix_report.json"),
        help="Output JSON report path"
    )

    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be written")
        print("=" * 70)
    else:
        print("=" * 70)
        print("APPLY MODE - Changes will be written to files")
        print("=" * 70)

    if not args.path.exists():
        print(f"ERROR: Path not found: {args.path}")
        return 1

    print(f"\nScanning directory: {args.path}")

    # Find all markdown files
    md_files = sorted(args.path.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")

    # Process all files
    results = []
    total_fixes = 0
    lexer_totals = {lexer: 0 for lexer in LEXER_FIXES.keys()}

    for md_file in md_files:
        result = fix_lexers_in_file(md_file, dry_run=dry_run, verbose=args.verbose)
        results.append(result)

        fixes = result.get('fixes_applied', 0)
        total_fixes += fixes

        # Aggregate lexer counts
        for lexer, count in result.get('fixes_by_lexer', {}).items():
            lexer_totals[lexer] += count

    # Generate report
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "docs_directory": str(args.path),
            "total_files_processed": len(md_files),
            "dry_run": dry_run
        },
        "summary": {
            "total_fixes": total_fixes,
            "files_with_fixes": sum(1 for r in results if r.get('fixes_applied', 0) > 0),
            "lexer_totals": lexer_totals
        },
        "results": results
    }

    # Save report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files processed:      {len(md_files)}")
    print(f"Total fixes:          {total_fixes}")
    print(f"Files with fixes:     {report['summary']['files_with_fixes']}")
    print()

    # Show lexer breakdown
    if any(count > 0 for count in lexer_totals.values()):
        print("Lexer fixes breakdown:")
        for lexer, count in sorted(lexer_totals.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                valid_lexer = LEXER_FIXES[lexer]
                print(f"  {lexer} -> {valid_lexer}: {count}")
        print()

    if dry_run:
        print("[INFO] This was a DRY RUN. Use --apply to write changes.")
    else:
        print("[OK] Fixes applied successfully!")

    print(f"\nDetailed report: {args.output}")

    # Show top files with fixes
    files_with_fixes = [r for r in results if r.get('fixes_applied', 0) > 0]
    if files_with_fixes:
        print("\nTop 10 files with most fixes:")
        for result in sorted(files_with_fixes, key=lambda x: x.get('fixes_applied', 0), reverse=True)[:10]:
            print(f"  {result['file']}: {result['fixes_applied']} fix(es)")

    return 0


if __name__ == "__main__":
    exit(main())
