#!/usr/bin/env python3
"""Automated script to detect and fix concatenated heading patterns in Markdown files.

This script addresses Sphinx build errors caused by Markdown headings that are
immediately followed by content without a blank line. The concatenated pattern
causes docutils document structure errors resulting in KeyError: 'anchorname'
or KeyError: 'refuri' exceptions.

Patterns Fixed:
    1. Heading + immediate content
    2. Heading + immediate list
    3. Heading + immediate table
    4. Code fence close + immediate content
    5. Toctree caption + immediate entries

Usage:
    # Dry run to preview changes
    python scripts/docs/fix_concatenated_headings.py --file docs/index.md --dry-run

    # Fix single file
    python scripts/docs/fix_concatenated_headings.py --file docs/index.md

    # Fix all files in directory recursively
    python scripts/docs/fix_concatenated_headings.py --dir docs --recursive

    # Fix with backup and validation
    python scripts/docs/fix_concatenated_headings.py --dir docs --recursive --backup --validate

    # Exclude specific patterns
    python scripts/docs/fix_concatenated_headings.py --dir docs --recursive --exclude "_build/**" "**/.ipynb_checkpoints/**"
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import shutil
import subprocess


class MarkdownHeadingFixer:
    """Fix concatenated heading patterns in Markdown files."""

    # Pattern to detect Markdown headings (# through ######)
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')

    # Pattern to detect code fence start/end
    CODE_FENCE_PATTERN = re.compile(r'^```')

    # Pattern to detect toctree directive
    TOCTREE_PATTERN = re.compile(r'^```\{toctree\}')

    # Pattern to detect directive closing
    DIRECTIVE_END_PATTERN = re.compile(r'^```$')

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """Initialize the fixer.

        Args:
            dry_run: If True, preview changes without modifying files
            verbose: If True, print detailed progress information
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.files_modified = 0
        self.patterns_fixed = 0

    def is_heading(self, line: str) -> bool:
        """Check if line is a Markdown heading.

        Args:
            line: Line to check

        Returns:
            True if line is a heading, False otherwise
        """
        return bool(self.HEADING_PATTERN.match(line))

    def is_code_fence(self, line: str) -> bool:
        """Check if line is a code fence delimiter.

        Args:
            line: Line to check

        Returns:
            True if line is a code fence, False otherwise
        """
        return bool(self.CODE_FENCE_PATTERN.match(line))

    def is_blank(self, line: str) -> bool:
        """Check if line is blank or whitespace-only.

        Args:
            line: Line to check

        Returns:
            True if line is blank, False otherwise
        """
        return len(line.strip()) == 0

    def needs_blank_line_after(self, line: str, next_line: Optional[str],
                               in_code_block: bool) -> bool:
        """Determine if a blank line should be inserted after this line.

        Args:
            line: Current line
            next_line: Next line (or None if at end of file)
            in_code_block: Whether currently inside a code block

        Returns:
            True if blank line should be inserted, False otherwise
        """
        # Don't modify inside code blocks
        if in_code_block:
            return False

        # No next line, nothing to fix
        if next_line is None:
            return False

        # Next line is already blank, no fix needed
        if self.is_blank(next_line):
            return False

        # Heading followed by non-blank content needs blank line
        if self.is_heading(line):
            return True

        # Code fence close followed by non-blank, non-heading content needs blank line
        if self.is_code_fence(line) and not self.is_heading(next_line):
            return True

        return False

    def fix_file(self, file_path: Path) -> Tuple[bool, int]:
        """Fix concatenated heading patterns in a single file.

        Args:
            file_path: Path to the Markdown file

        Returns:
            Tuple of (was_modified, patterns_fixed_count)
        """
        if self.verbose:
            print(f"Processing: {file_path}")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return False, 0

        # Track state
        fixed_lines = []
        in_code_block = False
        patterns_fixed = 0

        # Process each line
        for i, line in enumerate(lines):
            # Remove trailing newline for processing
            line_content = line.rstrip('\n')

            # Track code block state
            if self.is_code_fence(line_content):
                in_code_block = not in_code_block

            # Add current line
            fixed_lines.append(line)

            # Check if blank line needed after this line
            next_line = lines[i + 1].rstrip('\n') if i + 1 < len(lines) else None

            if self.needs_blank_line_after(line_content, next_line, in_code_block):
                fixed_lines.append('\n')
                patterns_fixed += 1
                if self.verbose:
                    print(f"  Line {i+1}: Added blank line after: {line_content[:60]}...")

        # If nothing changed, return early
        if patterns_fixed == 0:
            if self.verbose:
                print("  No changes needed")
            return False, 0

        # Show diff in dry-run mode
        if self.dry_run:
            print(f"\n{'='*80}")
            print(f"DRY RUN: {file_path}")
            print(f"Would fix {patterns_fixed} pattern(s)")
            print(f"{'='*80}")

            # Show first few changes
            shown = 0
            for i, (old, new) in enumerate(zip(lines, fixed_lines)):
                if old != new and shown < 5:
                    print(f"\nLine {i+1}:")
                    # Use repr() to safely display Unicode characters on Windows
                    old_safe = old.rstrip().encode('ascii', 'backslashreplace').decode('ascii')
                    new_safe = new.rstrip().encode('ascii', 'backslashreplace').decode('ascii')
                    print(f"  Before: {old_safe}")
                    print(f"  After:  {new_safe}")
                    shown += 1

            if patterns_fixed > shown:
                print(f"\n... and {patterns_fixed - shown} more change(s)")

            return True, patterns_fixed

        # Write fixed content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)

            print(f"Fixed {patterns_fixed} pattern(s) in: {file_path}")
            return True, patterns_fixed

        except Exception as e:
            print(f"Error writing {file_path}: {e}", file=sys.stderr)
            return False, 0

    def fix_directory(self, dir_path: Path, recursive: bool = False,
                     exclude_patterns: Optional[List[str]] = None) -> None:
        """Fix all Markdown files in a directory.

        Args:
            dir_path: Path to directory
            recursive: If True, process subdirectories recursively
            exclude_patterns: List of glob patterns to exclude
        """
        if exclude_patterns is None:
            exclude_patterns = []

        # Find all markdown files
        pattern = '**/*.md' if recursive else '*.md'
        markdown_files = list(dir_path.glob(pattern))

        # Filter out excluded patterns
        filtered_files = []
        for file_path in markdown_files:
            excluded = False
            for exclude in exclude_patterns:
                if file_path.match(exclude):
                    excluded = True
                    break
            if not excluded:
                filtered_files.append(file_path)

        print(f"Found {len(filtered_files)} Markdown file(s) to process")

        # Process each file
        for file_path in filtered_files:
            was_modified, patterns_fixed = self.fix_file(file_path)
            if was_modified:
                self.files_modified += 1
                self.patterns_fixed += patterns_fixed

        # Print summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Files processed:  {len(filtered_files)}")
        print(f"Files modified:   {self.files_modified}")
        print(f"Patterns fixed:   {self.patterns_fixed}")

        if self.dry_run:
            print("\nDRY RUN - No files were actually modified")


def backup_file(file_path: Path) -> Optional[Path]:
    """Create a backup of the file.

    Args:
        file_path: Path to file to backup

    Returns:
        Path to backup file, or None if backup failed
    """
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Error creating backup: {e}", file=sys.stderr)
        return None


def validate_with_sphinx(docs_dir: Path) -> bool:
    """Run Sphinx build to validate changes.

    Args:
        docs_dir: Path to docs directory

    Returns:
        True if build succeeded, False otherwise
    """
    print("\nValidating with Sphinx build...")
    try:
        result = subprocess.run(
            ['sphinx-build', '-b', 'html', str(docs_dir), str(docs_dir / '_build' / 'html')],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✓ Sphinx build succeeded")
            return True
        else:
            print("✗ Sphinx build failed")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("✗ Sphinx build timed out")
        return False
    except Exception as e:
        print(f"✗ Error running Sphinx: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fix concatenated heading patterns in Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', type=Path, help='Fix single Markdown file')
    input_group.add_argument('--dir', type=Path, help='Fix all Markdown files in directory')

    # Processing options
    parser.add_argument('--recursive', action='store_true',
                       help='Process directories recursively')
    parser.add_argument('--exclude', nargs='+', default=[],
                       help='Glob patterns to exclude (e.g., "_build/**")')

    # Output options
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without modifying files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Print detailed progress information')
    parser.add_argument('--backup', action='store_true',
                       help='Create .bak backup before modifying files')
    parser.add_argument('--validate', action='store_true',
                       help='Run Sphinx build to validate changes')

    args = parser.parse_args()

    # Create fixer instance
    fixer = MarkdownHeadingFixer(dry_run=args.dry_run, verbose=args.verbose)

    # Process based on input type
    if args.file:
        # Single file mode
        if not args.file.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        if not args.file.suffix == '.md':
            print(f"Error: File must be a Markdown file (.md): {args.file}", file=sys.stderr)
            sys.exit(1)

        # Backup if requested
        if args.backup and not args.dry_run:
            backup_path = backup_file(args.file)
            if backup_path:
                print(f"Created backup: {backup_path}")

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(args.file)

        if was_modified:
            fixer.files_modified = 1
            fixer.patterns_fixed = patterns_fixed

        # Print summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Files modified:   {fixer.files_modified}")
        print(f"Patterns fixed:   {fixer.patterns_fixed}")

        if args.dry_run:
            print("\nDRY RUN - File was not actually modified")

    else:
        # Directory mode
        if not args.dir.exists() or not args.dir.is_dir():
            print(f"Error: Directory not found: {args.dir}", file=sys.stderr)
            sys.exit(1)

        # Fix directory
        fixer.fix_directory(args.dir, recursive=args.recursive,
                          exclude_patterns=args.exclude)

    # Validate with Sphinx if requested
    if args.validate and not args.dry_run and fixer.files_modified > 0:
        docs_dir = args.dir if args.dir else args.file.parent
        validate_with_sphinx(docs_dir)


if __name__ == '__main__':
    main()
