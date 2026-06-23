"""
Heading Hierarchy Fixer for Markdown Files
==========================================

Fixes heading hierarchy gaps by inserting intermediate headers.

Screen readers and accessibility tools require proper heading hierarchy:
- H1 should be followed by H2 (not H3 or deeper)
- H2 should be followed by H2 or H3 (not H4 or deeper)
- No skipping levels

This script auto-inserts missing intermediate headers with contextual text.

Usage:
    python scripts/docs/heading_hierarchy_fixer.py --file README.md --backup
    python scripts/docs/heading_hierarchy_fixer.py --all --dry-run

Author: Claude Code (Automated QA Script)
Date: November 2025
"""

import re
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


def parse_heading(line: str) -> Tuple[int, str]:
    """
    Parse a markdown heading line.

    Args:
        line: Input line

    Returns:
        Tuple of (level, text) or (0, "") if not a heading
    """
    match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
    if match:
        return len(match.group(1)), match.group(2)
    return 0, ""


def generate_intermediate_header(from_level: int, to_level: int, context: str = "") -> str:
    """
    Generate text for an intermediate header.

    Args:
        from_level: Previous heading level
        to_level: Target heading level
        context: Context from surrounding headings

    Returns:
        Header text
    """
    # Default headers for different levels
    defaults = {
        2: "Overview",
        3: "Details",
        4: "Implementation",
        5: "Specifics",
        6: "Additional Information"
    }

    # Try to generate contextual text
    if context:
        # Extract key words from context
        words = re.findall(r'\b[A-Z][a-z]+\b', context)
        if words and len(words) <= 3:
            return " ".join(words)

    # Use default
    level_to_insert = from_level + 1
    return defaults.get(level_to_insert, "Section")


def fix_heading_hierarchy(text: str, dry_run: bool = False) -> Tuple[str, Dict]:
    """
    Fix heading hierarchy in markdown text.

    Args:
        text: Input markdown text
        dry_run: If True, just report gaps without fixing

    Returns:
        Tuple of (fixed_text, statistics)
    """
    lines = text.splitlines(keepends=True)
    fixed_lines = []
    stats = {
        'gaps_found': 0,
        'headers_inserted': 0,
        'gaps': []
    }

    last_level = 0
    last_heading_text = ""

    for i, line in enumerate(lines, start=1):
        level, heading_text = parse_heading(line)

        if level > 0:
            # Check for gap
            if last_level > 0 and level > last_level + 1:
                gap_size = level - last_level - 1
                stats['gaps_found'] += 1
                stats['gaps'].append({
                    'line': i,
                    'from_level': last_level,
                    'to_level': level,
                    'gap_size': gap_size
                })

                # Insert intermediate headers
                if not dry_run:
                    for insert_level in range(last_level + 1, level):
                        intermediate_text = generate_intermediate_header(
                            last_level,
                            level,
                            last_heading_text
                        )
                        intermediate_header = '#' * insert_level + ' ' + intermediate_text + '\n\n'
                        fixed_lines.append(intermediate_header)
                        stats['headers_inserted'] += 1

            last_level = level
            last_heading_text = heading_text

        fixed_lines.append(line)

    return ''.join(fixed_lines), stats


def process_file(file_path: Path, create_backup: bool = True, dry_run: bool = False) -> Dict:
    """
    Process a single file to fix heading hierarchy.

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

    # Fix heading hierarchy
    fixed_text, stats = fix_heading_hierarchy(original_text, dry_run=dry_run)

    # Report only (dry run)
    if dry_run:
        return {
            'status': 'dry_run',
            'file': str(file_path),
            'stats': stats,
            'message': f"Would insert {stats['headers_inserted']} header(s) to fix {stats['gaps_found']} gap(s)"
        }

    # No changes needed
    if stats['headers_inserted'] == 0:
        return {
            'status': 'unchanged',
            'file': str(file_path),
            'stats': stats,
            'message': "No heading hierarchy gaps found"
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
            'backup_created': create_backup,
            'message': f"Inserted {stats['headers_inserted']} header(s) to fix {stats['gaps_found']} gap(s)"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to write file: {e}",
            'stats': stats
        }


def main():
    parser = argparse.ArgumentParser(
        description='Fix heading hierarchy gaps in markdown files by inserting intermediate headers'
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
    print(f"\n[INFO] Heading Hierarchy Fixer - Processing {len(files_to_process)} file(s)")
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
            if result.get('backup_created'):
                print(f"  [INFO] Backup created: {file_path}.bak")
            stats = result['stats']
            if stats['gaps']:
                print(f"  [INFO] Fixed gaps at lines:")
                for gap in stats['gaps'][:5]:  # Show first 5
                    print(f"      - Line {gap['line']}: H{gap['from_level']} -> H{gap['to_level']} (inserted {gap['gap_size']} header(s))")
        elif result['status'] == 'unchanged':
            print(f"  [INFO] {result['message']}")
        elif result['status'] == 'dry_run':
            print(f"  [DRY_RUN] {result['message']}")
            stats = result['stats']
            if stats['gaps']:
                print(f"  [INFO] Would fix gaps at lines:")
                for gap in stats['gaps'][:5]:
                    print(f"      - Line {gap['line']}: H{gap['from_level']} -> H{gap['to_level']} (gap size: {gap['gap_size']})")
        elif result['status'] == 'error':
            print(f"  [ERROR] {result['message']}")

        print()

    # Summary
    total_gaps = sum(r.get('stats', {}).get('gaps_found', 0) for r in results)
    total_inserted = sum(r.get('stats', {}).get('headers_inserted', 0) for r in results)
    successful = sum(1 for r in results if r['status'] == 'success')
    errors = sum(1 for r in results if r['status'] == 'error')

    print("=" * 60)
    print(f"[SUMMARY] Heading Hierarchy Fixer Complete")
    print(f"  Files processed: {len(files_to_process)}")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print(f"  Total gaps found: {total_gaps}")
    print(f"  Total headers inserted: {total_inserted}")
    print("=" * 60)

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    exit(main())
