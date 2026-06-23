#!/usr/bin/env python3
r"""
===========================================================================================
Fix Transition-Induced Header Hierarchy Issues - Sphinx Phase 9D
===========================================================================================

This script removes transitions (---) that reset header hierarchy context in MyST/Sphinx.

Problem:
    MyST/Sphinx treats `---` as a context reset, breaking header hierarchy:

    ## Classes        (H2)
    ### ClassA       (H3)
    ---              (RESET - causes warning!)
    ### ClassB       (H3 - now treated as H1, causing "H1 to H3" warning)

Solution:
    - Remove `---` between same-level headers (H3+) within sections
    - Preserve `---` between major H2 section separators
    - Maintain proper spacing without transitions

Usage:
    python fix_transition_hierarchy.py --dry-run --target reference/  # Preview
    python fix_transition_hierarchy.py --target reference/            # Apply
    python fix_transition_hierarchy.py --files file1.md file2.md     # Specific files

Author: Claude Code (Sphinx Documentation Cleanup - Phase 9D)
Date: 2025-10-11
===========================================================================================
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional


class TransitionHierarchyFixer:
    """Remove transitions that cause header hierarchy resets."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_processed = 0
        self.files_modified = 0
        self.transitions_removed = 0

    def get_header_level(self, line: str) -> Optional[int]:
        """
        Get header level from a line.

        Returns:
            Header level (1-6) or None if not a header
        """
        stripped = line.strip()
        if not stripped.startswith('#'):
            return None

        # Count leading # symbols
        match = re.match(r'^(#{1,6})\s+', stripped)
        if match:
            return len(match.group(1))
        return None

    def is_transition(self, line: str) -> bool:
        """Check if line is a transition (---,  ***, ___)."""
        stripped = line.strip()
        # Match 3+ dashes, asterisks, or underscores
        return bool(re.match(r'^(-{3,}|\*{3,}|_{3,})$', stripped))

    def should_remove_transition(
        self,
        prev_header_level: Optional[int],
        next_header_level: Optional[int]
    ) -> bool:
        """
        Determine if transition should be removed.

        Remove transition if:
        - Both surrounding headers are H3+ (class/method level)
        - This indicates transition is between same-level content

        Keep transition if:
        - Between H2 sections (major section separators)
        - At document boundaries
        - Between different content types
        """
        if prev_header_level is None or next_header_level is None:
            # Keep transitions at boundaries or without clear context
            return False

        # Remove if both headers are H3+ (within same section)
        if prev_header_level >= 3 and next_header_level >= 3:
            return True

        # Keep transitions between H2 sections
        return False

    def fix_file(self, filepath: Path) -> bool:
        """
        Fix transition-induced hierarchy issues in a file.

        Returns:
            True if file was modified, False otherwise.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"[ERROR] Failed to read {filepath}: {e}")
            return False

        # Track changes
        modified = False
        new_lines = []

        # Track previous header level for context
        prev_header_level = None
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if current line is a transition
            if self.is_transition(line):
                # Look backward for previous header
                prev_header_level = None
                for j in range(i - 1, max(-1, i - 10), -1):
                    if j < 0:
                        break
                    level = self.get_header_level(lines[j])
                    if level is not None:
                        prev_header_level = level
                        break

                # Look forward for next header
                next_header_level = None
                for j in range(i + 1, min(len(lines), i + 10)):
                    level = self.get_header_level(lines[j])
                    if level is not None:
                        next_header_level = level
                        break

                # Decide whether to remove transition
                if self.should_remove_transition(prev_header_level, next_header_level):
                    # Remove transition (skip adding to new_lines)
                    # Also remove surrounding blank lines to avoid double spacing
                    if new_lines and new_lines[-1].strip() == '':
                        new_lines.pop()

                    modified = True
                    self.transitions_removed += 1

                    if self.dry_run:
                        print(f"  Line {i+1}: Would remove transition between "
                              f"H{prev_header_level} and H{next_header_level}")

                    # Skip to next line
                    i += 1
                    continue

            # Keep line
            new_lines.append(line)

            # Track header levels for context
            level = self.get_header_level(line)
            if level is not None:
                prev_header_level = level

            i += 1

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

            if filepath.suffix != '.md':
                print(f"[WARNING] Skipping non-Markdown file: {filepath}")
                continue

            self.files_processed += 1

            if self.fix_file(filepath):
                self.files_modified += 1
                status = "[DRY-RUN]" if self.dry_run else "[OK]"
                print(f"{status} Fixed transition hierarchy in: {filepath.name}")

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
        print(f"Files processed:       {self.files_processed}")
        print(f"Files modified:        {self.files_modified}")
        print(f"Transitions removed:   {self.transitions_removed}")

        if self.dry_run:
            print("\n[DRY-RUN MODE] No files were actually modified")
            print("Run without --dry-run to apply changes")
        else:
            print(f"\n[OK] Successfully fixed {self.files_modified} files")
            print(f"[OK] Removed {self.transitions_removed} hierarchy-breaking transitions")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix transition-induced header hierarchy issues (Sphinx Phase 9D)"
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
    fixer = TransitionHierarchyFixer(dry_run=args.dry_run)

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
