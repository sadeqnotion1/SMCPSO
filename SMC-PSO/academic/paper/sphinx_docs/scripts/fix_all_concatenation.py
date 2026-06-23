#!/usr/bin/env python3
r"""
===========================================================================================
Fix All Concatenated Headers - Sphinx Phase 9C
===========================================================================================

This script fixes concatenated headers throughout entire Markdown files, not just line 1.

Problem:
    Auto-generated documentation files have multiple headers concatenated on single lines:

    Example:
        ## Classes ### `AnalysisStatus` **Inherits from:** `Enum` Status...

    Should be:
        ## Classes

        ### `AnalysisStatus`

        **Inherits from:** `Enum`

        Status...

Solution:
    - Scan entire file for lines with multiple header markers
    - Split concatenated headers into separate lines
    - Add proper blank line spacing between sections
    - Preserve all content

Usage:
    python fix_all_concatenation.py --dry-run                    # Preview changes
    python fix_all_concatenation.py --target reference/          # Fix all files
    python fix_all_concatenation.py --files file1.md file2.md   # Fix specific files

Author: Claude Code (Sphinx Documentation Cleanup - Phase 9C)
Date: 2025-10-11
===========================================================================================
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List


class ConcatenationFixer:
    """Fix concatenated headers throughout Markdown files."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_processed = 0
        self.files_modified = 0
        self.lines_split = 0

    def is_header(self, line: str) -> bool:
        """Check if line is a header (starts with #)."""
        stripped = line.strip()
        return bool(re.match(r'^#{1,6}\s+', stripped))

    def count_header_markers(self, line: str) -> int:
        """Count distinct header marker positions in line."""
        # Find all header markers (##, ###, ####, etc.)
        # Use word boundaries to avoid counting # inside text
        markers = re.findall(r'\s(#{2,6})\s', ' ' + line + ' ')
        return len(markers)

    def detect_multi_header_line(self, line: str) -> bool:
        """Detect if line has multiple header sections concatenated."""
        if not self.is_header(line):
            return False

        # Count header markers in the line
        # Need at least 2 to be concatenated
        return self.count_header_markers(line) >= 2

    def split_multi_header_line(self, line: str) -> List[str]:
        """
        Split line with multiple headers into separate lines with proper spacing.

        Example:
            Input:  "## Classes ### `AnalysisStatus` **Inherits from:** `Enum` Status..."
            Output: ["## Classes", "", "### `AnalysisStatus`", "",
                     "**Inherits from:** `Enum`", "", "Status..."]
        """
        result = []
        remaining = line

        # Process line iteratively, extracting one header at a time
        while remaining:
            remaining = remaining.strip()
            if not remaining:
                break

            # Check if starts with header marker
            header_match = re.match(r'^(#{2,6})\s+', remaining)
            if not header_match:
                # No more headers, append remaining content
                if remaining:
                    result.append(remaining)
                break

            header_level = header_match.group(1)
            remaining = remaining[len(header_match.group(0)):]  # Remove marker

            # Find the extent of this header section
            # It ends when we hit another header marker or end of line
            next_header_pos = self._find_next_header_marker(remaining)

            if next_header_pos == -1:
                # No more headers, this header section goes to end
                header_content = remaining.strip()
                if header_content:
                    result.append(f"{header_level} {header_content}")
                break
            else:
                # Extract this header section
                header_content = remaining[:next_header_pos].strip()
                if header_content:
                    result.append(f"{header_level} {header_content}")
                    result.append('')  # Blank line after header

                # Continue with rest of line
                remaining = remaining[next_header_pos:]

        return result

    def _find_next_header_marker(self, text: str) -> int:
        """Find position of next header marker (##, ###, etc.) in text."""
        # Look for space + header marker + space pattern
        match = re.search(r'\s(#{2,6})\s', text)
        if match:
            return match.start()
        return -1

    def fix_file(self, filepath: Path) -> bool:
        """
        Fix all concatenated headers in a file.

        Returns:
            True if file was modified, False otherwise.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"[ERROR] Failed to read {filepath}: {e}")
            return False

        # Process each line
        modified = False
        new_lines = []
        line_num = 0

        for line in lines:
            line_num += 1

            # Check if this line has concatenated headers
            if self.detect_multi_header_line(line):
                # Split the line
                split_lines = self.split_multi_header_line(line)

                # Add newlines back
                for split_line in split_lines:
                    new_lines.append(split_line + '\n' if split_line else '\n')

                modified = True
                self.lines_split += 1

                if self.dry_run:
                    print(f"  Line {line_num}: Would split concatenated headers")
                    print(f"    Original: {line.rstrip()[:80]}...")
                    print(f"    Split into {len(split_lines)} lines")
            else:
                # Keep line as-is
                new_lines.append(line)

        # Write file if modified and not dry-run
        if modified and not self.dry_run:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                return True
            except Exception as e:
                print(f"[ERROR] Failed to write {filepath}: {e}")
                return False

        return modified

    def process_files(self, files: List[Path]) -> None:
        """Process a list of files."""
        for filepath in files:
            if not filepath.exists():
                print(f"[WARNING] File not found: {filepath}")
                continue

            if not filepath.suffix == '.md':
                print(f"[WARNING] Skipping non-Markdown file: {filepath}")
                continue

            self.files_processed += 1

            if self.fix_file(filepath):
                self.files_modified += 1
                status = "[DRY-RUN]" if self.dry_run else "[OK]"
                print(f"{status} Fixed concatenated headers in: {filepath.name}")

    def process_directory(self, target_dir: Path, pattern: str = "**/*.md") -> None:
        """Process all Markdown files in a directory."""
        files = sorted(target_dir.glob(pattern))

        if not files:
            print(f"[WARNING] No Markdown files found in {target_dir}")
            return

        print(f"Found {len(files)} Markdown files in {target_dir}")
        if self.dry_run:
            print("[DRY-RUN MODE] No files will be modified\n")

        self.process_files(files)

    def print_summary(self) -> None:
        """Print summary statistics."""
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Files processed:  {self.files_processed}")
        print(f"Files modified:   {self.files_modified}")
        print(f"Lines split:      {self.lines_split}")

        if self.dry_run:
            print("\n[DRY-RUN MODE] No files were actually modified")
            print("Run without --dry-run to apply changes")
        else:
            print(f"\n[OK] Successfully fixed {self.files_modified} files")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix concatenated headers throughout Markdown files (Sphinx Phase 9C)"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--target',
        type=str,
        help='Target directory to process (e.g., reference/)'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific files to process'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.target and not args.files:
        print("[ERROR] Must specify either --target or --files")
        sys.exit(1)

    # Create fixer
    fixer = ConcatenationFixer(dry_run=args.dry_run)

    # Process files
    if args.files:
        # Process specific files
        files = [Path(f) for f in args.files]
        fixer.process_files(files)
    elif args.target:
        # Process directory
        target_dir = Path(args.target)
        if not target_dir.exists():
            print(f"[ERROR] Directory not found: {target_dir}")
            sys.exit(1)
        fixer.process_directory(target_dir)

    # Print summary
    fixer.print_summary()

    # Exit code
    sys.exit(0 if fixer.files_modified > 0 or args.dry_run else 1)


if __name__ == '__main__':
    main()
