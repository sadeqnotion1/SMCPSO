#!/usr/bin/env python3
"""
Fix standalone horizontal rules in Markdown files.

Removes standalone horizontal rules (---, ___, ***) that cause Sphinx build
failures while preserving table separators (|---|---|) and other valid uses.

Usage:
    python scripts/fix_horizontal_rules.py --scan       # Preview changes
    python scripts/fix_horizontal_rules.py --fix        # Apply fixes
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def is_table_separator(line: str) -> bool:
    """Check if line is a table separator (valid)."""
    stripped = line.strip()
    # Table separators have pipes and dashes: |---|---|
    return '|' in stripped and re.match(r'^\|[-:\s|]+\|$', stripped) is not None


def is_standalone_hr(line: str, prev_line: str, next_line: str, in_code_block: bool) -> bool:
    """
    Check if line is a standalone horizontal rule (to be removed).

    A standalone HR is:
    - A line containing only ---, ___, ***, or === (3+ repetitions)
    - NOT part of a table separator
    - NOT inside a code block
    - Used as a section separator (typically surrounded by blank lines)
    """
    stripped = line.strip()

    # Not a horizontal rule at all
    if not stripped:
        return False

    # Inside code block - keep it
    if in_code_block:
        return False

    # Table separator - keep it
    if is_table_separator(line):
        return False

    # Check for HR patterns: ---, ___, ***, ===
    hr_patterns = [
        r'^-{3,}$',   # Three or more dashes
        r'^_{3,}$',   # Three or more underscores
        r'^\*{3,}$',  # Three or more asterisks
        r'^={3,}$',   # Three or more equals signs
    ]

    for pattern in hr_patterns:
        if re.match(pattern, stripped):
            return True

    return False


def process_file(
    file_path: Path,
    dry_run: bool = True
) -> Tuple[int, List[str]]:
    """
    Process a markdown file to remove standalone horizontal rules.

    Args:
        file_path: Path to markdown file
        dry_run: If True, only report changes without modifying file

    Returns:
        Tuple of (num_removed, preview_lines)
    """
    lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)

    removed_count = 0
    preview_lines = []
    new_lines = []

    in_code_block = False
    i = 0
    while i < len(lines):
        current_line = lines[i]
        prev_line = lines[i - 1] if i > 0 else ""
        next_line = lines[i + 1] if i < len(lines) - 1 else ""

        # Track code block state
        if current_line.strip().startswith('```'):
            in_code_block = not in_code_block

        if is_standalone_hr(current_line, prev_line, next_line, in_code_block):
            # Found a standalone HR to remove
            removed_count += 1
            preview_lines.append(f"  Line {i + 1}: {current_line.rstrip()}")

            # Skip this line (don't add to new_lines)
            # Also clean up extra blank lines
            if next_line.strip() == "" and prev_line.strip() == "":
                # Remove extra blank line after HR
                if i + 1 < len(lines) - 1:
                    i += 1  # Skip next blank line too
        else:
            new_lines.append(current_line)

        i += 1

    # Apply changes if not dry run
    if not dry_run and removed_count > 0:
        file_path.write_text(''.join(new_lines), encoding='utf-8')

    return removed_count, preview_lines


def scan_directory(directory: Path) -> None:
    """Scan directory and report horizontal rule issues."""
    print(f"Scanning: {directory}")
    print("=" * 80)

    total_removed = 0
    files_affected = 0

    for md_file in sorted(directory.glob("*.md")):
        removed_count, preview_lines = process_file(md_file, dry_run=True)

        if removed_count > 0:
            files_affected += 1
            total_removed += removed_count

            print(f"\n{md_file.name}:")
            print(f"  {removed_count} standalone horizontal rules to remove:")
            for preview_line in preview_lines:
                print(preview_line)

    print("\n" + "=" * 80)
    print(f"Summary: {files_affected} files, {total_removed} HRs to remove")
    print("=" * 80)


def fix_directory(directory: Path) -> None:
    """Fix horizontal rule issues in directory."""
    print(f"Fixing: {directory}")
    print("=" * 80)

    total_removed = 0
    files_affected = 0

    for md_file in sorted(directory.glob("*.md")):
        removed_count, preview_lines = process_file(md_file, dry_run=False)

        if removed_count > 0:
            files_affected += 1
            total_removed += removed_count

            print(f"\n{md_file.name}:")
            print(f"  [OK] Removed {removed_count} standalone horizontal rules")

    print("\n" + "=" * 80)
    print(f"Summary: Fixed {files_affected} files, removed {total_removed} HRs")
    print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) < 2 or sys.argv[1] not in ('--scan', '--fix'):
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    directory = Path("docs/for_reviewers")

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    if mode == '--scan':
        scan_directory(directory)
    elif mode == '--fix':
        print("WARNING: This will modify files in place!")
        response = input("Continue? [y/N]: ")
        if response.lower() == 'y':
            fix_directory(directory)
        else:
            print("Cancelled.")


if __name__ == '__main__':
    main()
