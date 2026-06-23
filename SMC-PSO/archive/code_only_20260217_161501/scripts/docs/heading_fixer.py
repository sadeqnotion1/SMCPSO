"""
Automated Markdown Heading Structure Fixer
==========================================

Fixes common heading structure issues in markdown documentation files.

Issues Fixed:
1. Trailing punctuation (periods, colons, semicolons)
2. Improper capitalization (converts to Title Case)
3. Inconsistent heading levels (detects gaps)

Usage:
    python scripts/docs/heading_fixer.py --file README.md
    python scripts/docs/heading_fixer.py --file CLAUDE.md --backup
    python scripts/docs/heading_fixer.py --all  # Fix all 4 main entry points

Author: Claude Code (Automated QA Script)
Date: November 2025
"""

import re
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


# Articles, conjunctions, and prepositions (should be lowercase in title case)
LOWERCASE_WORDS = {
    'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'from', 'in', 'into',
    'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'via', 'with', 'yet'
}


def to_title_case(text: str) -> str:
    """
    Convert text to proper Title Case.

    Rules:
    - Capitalize first and last words
    - Capitalize major words
    - Lowercase articles, conjunctions, prepositions (unless first/last)
    - Preserve ALL CAPS acronyms (e.g., SMC, PSO, HIL)

    Args:
        text: Input text

    Returns:
        Title-cased text
    """
    words = text.split()
    if not words:
        return text

    result = []
    for i, word in enumerate(words):
        # Preserve ALL CAPS acronyms (2+ uppercase letters)
        if re.match(r'^[A-Z]{2,}$', word):
            result.append(word)
        # Preserve code/technical terms in backticks
        elif word.startswith('`') and word.endswith('`'):
            result.append(word)
        # First or last word: always capitalize
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        # Lowercase words: keep lowercase (unless first/last)
        elif word.lower() in LOWERCASE_WORDS:
            result.append(word.lower())
        # All other words: capitalize
        else:
            result.append(word.capitalize())

    return ' '.join(result)


def fix_heading_line(line: str) -> Tuple[str, List[str]]:
    """
    Fix a single markdown heading line.

    Args:
        line: Input line (heading)

    Returns:
        Tuple of (fixed_line, list_of_issues_found)
    """
    # Not a heading
    if not line.strip().startswith('#'):
        return line, []

    issues = []
    original = line.rstrip()

    # Extract heading level and text
    match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
    if not match:
        return line, []

    level, heading_text = match.groups()

    # Issue 1: Trailing punctuation
    trailing_punct_pattern = r'[.;:!?]+\s*$'
    if re.search(trailing_punct_pattern, heading_text):
        heading_text = re.sub(trailing_punct_pattern, '', heading_text)
        issues.append('trailing_punctuation')

    # Issue 2: Improper capitalization (skip if heading is all uppercase or code)
    if not heading_text.isupper() and '`' not in heading_text:
        title_cased = to_title_case(heading_text)
        if title_cased != heading_text:
            heading_text = title_cased
            issues.append('capitalization')

    # Reconstruct heading
    fixed = f"{level} {heading_text}"

    # Preserve original indentation (if any)
    indent = len(original) - len(original.lstrip())
    fixed = ' ' * indent + fixed

    return fixed + '\n', issues


def fix_headings_in_text(text: str) -> Tuple[str, Dict]:
    """
    Fix all headings in markdown text.

    Args:
        text: Input markdown text

    Returns:
        Tuple of (fixed_text, statistics_dict)
    """
    lines = text.splitlines(keepends=True)
    fixed_lines = []
    stats = {
        'total_headings': 0,
        'headings_fixed': 0,
        'trailing_punctuation': 0,
        'capitalization': 0,
    }

    for line in lines:
        if line.strip().startswith('#'):
            stats['total_headings'] += 1
            fixed_line, issues = fix_heading_line(line)
            fixed_lines.append(fixed_line)

            if issues:
                stats['headings_fixed'] += 1
                for issue in issues:
                    stats[issue] = stats.get(issue, 0) + 1
        else:
            fixed_lines.append(line)

    return ''.join(fixed_lines), stats


def detect_heading_level_gaps(text: str) -> List[Dict]:
    """
    Detect gaps in heading hierarchy (e.g., # followed by ### skips ##).

    Args:
        text: Markdown text

    Returns:
        List of detected gaps with line numbers
    """
    gaps = []
    lines = text.splitlines()
    last_level = 0

    for i, line in enumerate(lines, start=1):
        match = re.match(r'^(#{1,6})\s+', line.strip())
        if match:
            current_level = len(match.group(1))

            # Check for gap (level jump > 1)
            if last_level > 0 and current_level > last_level + 1:
                gaps.append({
                    'line': i,
                    'from_level': last_level,
                    'to_level': current_level,
                    'gap_size': current_level - last_level - 1
                })

            last_level = current_level

    return gaps


def process_file(file_path: Path, create_backup: bool = True, dry_run: bool = False) -> Dict:
    """
    Process a single file to fix headings.

    Args:
        file_path: Path to the file to process
        create_backup: Whether to create .bak backup
        dry_run: If True, don't modify file (just report)

    Returns:
        Dictionary with processing statistics
    """
    if not file_path.exists():
        return {
            'status': 'error',
            'message': f"File not found: {file_path}",
            'stats': {}
        }

    # Read original content
    try:
        original_text = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to read file: {e}",
            'stats': {}
        }

    # Fix headings
    fixed_text, stats = fix_headings_in_text(original_text)

    # Detect heading level gaps
    gaps = detect_heading_level_gaps(fixed_text)

    # Report only (dry run)
    if dry_run:
        return {
            'status': 'dry_run',
            'file': str(file_path),
            'stats': stats,
            'gaps': gaps,
            'message': f"Would fix {stats['headings_fixed']} of {stats['total_headings']} headings"
        }

    # No changes needed
    if stats['headings_fixed'] == 0:
        return {
            'status': 'unchanged',
            'file': str(file_path),
            'stats': stats,
            'gaps': gaps,
            'message': "No heading issues found"
        }

    # Create backup if requested
    if create_backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)

    # Write modified content
    try:
        file_path.write_text(fixed_text, encoding='utf-8')
        return {
            'status': 'success',
            'file': str(file_path),
            'stats': stats,
            'gaps': gaps,
            'backup_created': create_backup,
            'message': f"Fixed {stats['headings_fixed']} of {stats['total_headings']} headings"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to write file: {e}",
            'stats': stats
        }


def main():
    parser = argparse.ArgumentParser(
        description='Fix heading structure issues in markdown documentation files'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Single file to process'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all 4 main entry points (README.md, CLAUDE.md, docs/index.md, guides/INDEX.md)'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create .bak backup files before modification'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Report what would be changed without modifying files'
    )

    args = parser.parse_args()

    # Determine files to process
    if args.all:
        files_to_process = [
            Path('README.md'),
            Path('CLAUDE.md'),
            Path('docs/index.md'),
            Path('docs/guides/INDEX.md')
        ]
    elif args.file:
        files_to_process = [args.file]
    else:
        parser.error("Must specify either --file or --all")

    # Process each file
    print(f"\n[INFO] Heading Fixer - Processing {len(files_to_process)} file(s)")
    print(f"[INFO] Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"[INFO] Backup: {'Enabled' if args.backup else 'Disabled'}\n")

    results = []
    for file_path in files_to_process:
        print(f"Processing: {file_path}")
        result = process_file(file_path, create_backup=args.backup, dry_run=args.dry_run)
        results.append(result)

        # Report result
        if result['status'] == 'success':
            print(f"  [OK] {result['message']}")
            stats = result['stats']
            if stats.get('trailing_punctuation', 0) > 0:
                print(f"      - Removed trailing punctuation: {stats['trailing_punctuation']}")
            if stats.get('capitalization', 0) > 0:
                print(f"      - Fixed capitalization: {stats['capitalization']}")
            if result.get('backup_created'):
                print(f"  [INFO] Backup created: {file_path}.bak")
            if result.get('gaps'):
                print(f"  [WARNING] Found {len(result['gaps'])} heading level gap(s):")
                for gap in result['gaps'][:3]:  # Show first 3
                    print(f"      - Line {gap['line']}: H{gap['from_level']} -> H{gap['to_level']} (gap: {gap['gap_size']})")
        elif result['status'] == 'unchanged':
            print(f"  [INFO] {result['message']}")
            if result.get('gaps'):
                print(f"  [WARNING] Found {len(result['gaps'])} heading level gap(s) (not auto-fixable)")
        elif result['status'] == 'dry_run':
            print(f"  [DRY_RUN] {result['message']}")
            stats = result['stats']
            if stats.get('trailing_punctuation', 0) > 0:
                print(f"      - Would remove trailing punctuation: {stats['trailing_punctuation']}")
            if stats.get('capitalization', 0) > 0:
                print(f"      - Would fix capitalization: {stats['capitalization']}")
            if result.get('gaps'):
                print(f"  [WARNING] Found {len(result['gaps'])} heading level gap(s) (not auto-fixable)")
        elif result['status'] == 'error':
            print(f"  [ERROR] {result['message']}")

        print()

    # Summary
    total_headings = sum(r.get('stats', {}).get('total_headings', 0) for r in results)
    total_fixed = sum(r.get('stats', {}).get('headings_fixed', 0) for r in results)
    successful = sum(1 for r in results if r['status'] == 'success')
    errors = sum(1 for r in results if r['status'] == 'error')

    print("=" * 60)
    print(f"[SUMMARY] Heading Fixer Complete")
    print(f"  Files processed: {len(files_to_process)}")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print(f"  Total headings: {total_headings}")
    print(f"  Headings fixed: {total_fixed}")
    print("=" * 60)

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    exit(main())
