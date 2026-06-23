#!/usr/bin/env python3
"""
Fix Sphinx documentation header warnings.

This script fixes two types of header issues:
1. Files starting with H2 (##) instead of H1 (#)
2. Files with non-consecutive header levels (H1→H3 jumps)

Usage:
    python scripts/docs/fix_sphinx_headers.py --dry-run
    python scripts/docs/fix_sphinx_headers.py --fix
"""

import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import sys


def extract_title_from_filename(filepath: Path) -> str:
    """Generate a title from filename."""
    name = filepath.stem
    # Convert underscores and hyphens to spaces
    title = name.replace('_', ' ').replace('-', ' ')
    # Capitalize words
    title = ' '.join(word.capitalize() for word in title.split())
    return title


def detect_first_header_level(content: str) -> Tuple[int, int]:
    """
    Detect the level of the first header in the content.

    Returns:
        Tuple of (header_level, line_number) or (0, -1) if no header found.
    """
    lines = content.split('\n')

    # Skip YAML frontmatter if present
    start_idx = 0
    if lines and lines[0].strip() == '---':
        try:
            end_idx = lines[1:].index('---') + 1
            start_idx = end_idx + 1
        except ValueError:
            pass

    for i, line in enumerate(lines[start_idx:], start=start_idx):
        line = line.strip()
        if line.startswith('#'):
            # Count the number of # symbols
            level = len(line) - len(line.lstrip('#'))
            return (level, i)

    return (0, -1)


def find_header_jumps(content: str) -> List[Tuple[int, int, int]]:
    """
    Find non-consecutive header level increases (e.g., H1 → H3).

    Returns:
        List of (line_number, from_level, to_level) tuples.
    """
    lines = content.split('\n')
    jumps = []
    last_level = 0

    # Skip YAML frontmatter if present
    start_idx = 0
    if lines and lines[0].strip() == '---':
        try:
            end_idx = lines[1:].index('---') + 1
            start_idx = end_idx + 1
        except ValueError:
            pass

    for i, line in enumerate(lines[start_idx:], start=start_idx):
        if line.strip().startswith('#'):
            level = len(line) - len(line.lstrip('#'))

            if last_level > 0 and level > last_level + 1:
                jumps.append((i, last_level, level))

            last_level = level

    return jumps


def fix_h2_start(content: str, filepath: Path) -> str:
    """
    Fix files starting with H2 by adding an appropriate H1 title.
    """
    lines = content.split('\n')

    # Skip YAML frontmatter if present
    start_idx = 0
    frontmatter = []
    if lines and lines[0].strip() == '---':
        try:
            end_idx = lines[1:].index('---') + 1
            frontmatter = lines[:end_idx + 1]
            start_idx = end_idx + 1
        except ValueError:
            pass

    # Find the first header
    first_header_level, first_header_line = detect_first_header_level(content)

    if first_header_level == 2:
        # Generate title from filename
        title = extract_title_from_filename(filepath)
        h1_line = f"# {title}\n"

        # Insert H1 before the existing content
        if frontmatter:
            result = frontmatter + [h1_line] + lines[start_idx:]
        else:
            result = [h1_line] + lines

        return '\n'.join(result)

    return content


def fix_header_jumps(content: str) -> str:
    """
    Fix non-consecutive header level increases by adjusting header levels.

    Strategy:
    - When we find H1 → H3, promote H3 → H2
    - When we find H2 → H4, promote H4 → H3
    - And so on...
    """
    lines = content.split('\n')
    jumps = find_header_jumps(content)

    if not jumps:
        return content

    # Build a map of line adjustments
    adjustments: Dict[int, int] = {}

    for line_no, from_level, to_level in jumps:
        # Calculate how many levels to reduce
        expected_level = from_level + 1
        reduction = to_level - expected_level

        # Mark this line for adjustment
        adjustments[line_no] = reduction

    # Apply adjustments
    for line_no, reduction in adjustments.items():
        line = lines[line_no]
        if line.strip().startswith('#'):
            # Count current level
            current_level = len(line) - len(line.lstrip('#'))
            new_level = current_level - reduction

            # Replace the header
            content_part = line.lstrip('#').strip()
            lines[line_no] = '#' * new_level + ' ' + content_part

    return '\n'.join(lines)


def process_file(filepath: Path, fix: bool = False) -> Dict[str, any]:
    """
    Process a single markdown file.

    Returns:
        Dictionary with analysis results and whether changes were made.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return {'error': str(e), 'changed': False}

    original_content = content
    changed = False
    issues = []

    # Check for H2 start
    first_level, first_line = detect_first_header_level(content)
    if first_level == 2:
        issues.append(f"Starts with H2 instead of H1 (line {first_line + 1})")
        if fix:
            content = fix_h2_start(content, filepath)
            changed = True

    # Check for header jumps
    jumps = find_header_jumps(content)
    if jumps:
        for line_no, from_level, to_level in jumps:
            issues.append(f"Header jump H{from_level}->H{to_level} at line {line_no + 1}")
        if fix:
            content = fix_header_jumps(content)
            changed = True

    # Write back if changed
    if fix and changed and content != original_content:
        filepath.write_text(content, encoding='utf-8')

    return {
        'issues': issues,
        'changed': changed,
        'first_level': first_level,
        'jumps': len(jumps)
    }


def main():
    parser = argparse.ArgumentParser(description='Fix Sphinx header warnings in markdown files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--fix', action='store_true', help='Apply fixes to files')
    parser.add_argument('--path', type=str, default='docs', help='Path to docs directory')

    args = parser.parse_args()

    if not args.dry_run and not args.fix:
        parser.error('Must specify either --dry-run or --fix')

    docs_path = Path(args.path)
    if not docs_path.exists():
        print(f"Error: Path {docs_path} does not exist", file=sys.stderr)
        return 1

    # Find all markdown files
    md_files = list(docs_path.rglob('*.md'))
    print(f"Found {len(md_files)} markdown files in {docs_path}")
    print()

    # Process files
    stats = {
        'total': 0,
        'h2_start': 0,
        'header_jumps': 0,
        'fixed': 0,
        'errors': 0
    }

    files_with_issues = []

    for filepath in sorted(md_files):
        result = process_file(filepath, fix=args.fix)

        if result.get('error'):
            stats['errors'] += 1
            print(f"ERROR {filepath}: {result['error']}")
            continue

        if result['issues']:
            stats['total'] += 1
            files_with_issues.append((filepath, result))

            if result['first_level'] == 2:
                stats['h2_start'] += 1

            if result['jumps'] > 0:
                stats['header_jumps'] += 1

            if result['changed']:
                stats['fixed'] += 1

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files with issues:     {stats['total']}")
    print(f"  - H2 start:          {stats['h2_start']}")
    print(f"  - Header jumps:      {stats['header_jumps']}")
    print(f"Files fixed:           {stats['fixed']}")
    print(f"Errors:                {stats['errors']}")
    print()

    if files_with_issues and args.dry_run:
        print("\nFiles with issues (use --fix to apply changes):")
        print("=" * 70)
        for filepath, result in files_with_issues[:20]:  # Show first 20
            rel_path = filepath.relative_to(docs_path)
            print(f"\n{rel_path}:")
            for issue in result['issues']:
                print(f"  - {issue}")

        if len(files_with_issues) > 20:
            print(f"\n... and {len(files_with_issues) - 20} more files")

    return 0


if __name__ == '__main__':
    sys.exit(main())
