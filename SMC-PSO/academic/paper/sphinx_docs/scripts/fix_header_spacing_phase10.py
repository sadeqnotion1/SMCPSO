#!/usr/bin/env python3
"""
Fix Header Spacing - Phase 10A

Fixes concatenated headers that cause MyST/Sphinx to misparse header hierarchy.

Problem:
    ### `ClassName` Description text on same line

Solution:
    ### `ClassName`

    Description text on separate line

This resolves H1→H3 and H2→H4 non-consecutive header warnings.

Usage:
    python fix_header_spacing_phase10.py --dry-run  # Preview changes
    python fix_header_spacing_phase10.py            # Apply changes
    python fix_header_spacing_phase10.py --path reference/analysis/  # Specific dir
"""

import re
import argparse
from pathlib import Path
from typing import List, Tuple


class HeaderSpacingFixer:
    """Fix concatenated header+description patterns."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_processed = 0
        self.files_modified = 0
        self.lines_fixed = 0

    def fix_file(self, file_path: Path) -> bool:
        """Fix header spacing in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"  [ERROR] Error reading {file_path}: {e}")
            return False

        modified_lines, changes = self._fix_header_spacing(lines)

        if changes == 0:
            return False  # No changes needed

        self.lines_fixed += changes

        if not self.dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(modified_lines))
                return True
            except Exception as e:
                print(f"  [ERROR] Error writing {file_path}: {e}")
                return False

        return True

    def _fix_header_spacing(self, lines: List[str]) -> Tuple[List[str], int]:
        """
        Fix header spacing issues.

        Patterns to fix:
        1. ### `ClassName` Description → ### `ClassName` \n\n Description
        2. #### Method Name Args → #### Method Name \n\n Args
        3. ### Title Text on same line → ### Title \n\n Text
        """
        modified = []
        changes = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            # Detect header with text on same line
            # Pattern: (###|####) followed by non-whitespace, then more text
            header_match = re.match(r'^(#{1,6})\s+(.+)', line)

            if header_match:
                header_level = header_match.group(1)
                rest_of_line = header_match.group(2)

                # Check if there's description text after the header title
                # We need to distinguish between:
                # ### `ClassName` (OK - just title)
                # ### `ClassName` Description of the class (BAD - has description)

                # Heuristics for detecting concatenated description:
                # 1. Contains multiple distinct parts (code + text)
                # 2. Has text after closing backtick or after **Inherits from:** pattern
                # 3. Has "**Inherits from:**" pattern
                # 4. Has descriptive text that's not just a title

                needs_splitting = False
                title_part = ""
                description_part = ""

                # Pattern 1: ### `ClassName` **Inherits from:** `Base` Description
                inherits_match = re.match(r'(.+?)\s+\*\*Inherits from:\*\*\s+(.+)', rest_of_line)
                if inherits_match:
                    title_part = inherits_match.group(1).strip()
                    description_part = f"**Inherits from:** {inherits_match.group(2).strip()}"
                    needs_splitting = True

                # Pattern 2: ### `ClassName` Some descriptive text
                elif '`' in rest_of_line:
                    # Has backticks - check if there's text after the last backtick
                    last_backtick_idx = rest_of_line.rfind('`')
                    after_backtick = rest_of_line[last_backtick_idx+1:].strip()

                    # If there's substantial text after backtick (not just punctuation)
                    if after_backtick and len(after_backtick) > 5 and not after_backtick.startswith('('):
                        title_part = rest_of_line[:last_backtick_idx+1].strip()
                        description_part = after_backtick
                        needs_splitting = True

                # Pattern 3: ### Title Text that continues (no backticks)
                elif ' ' in rest_of_line:
                    # Check if line is unusually long (likely concatenated)
                    words = rest_of_line.split()
                    if len(words) > 6:  # More than 6 words suggests description
                        # Split at reasonable point (after first few words)
                        title_part = ' '.join(words[:3])
                        description_part = ' '.join(words[3:])
                        needs_splitting = True

                if needs_splitting and title_part and description_part:
                    # Split the header from description
                    modified.append(f"{header_level} {title_part}")
                    modified.append("")  # Blank line
                    modified.append(description_part)
                    changes += 1
                    i += 1
                    continue

            # No change needed - keep line as-is
            modified.append(line)
            i += 1

        return modified, changes

    def process_directory(self, directory: Path):
        """Process all Markdown files in directory recursively."""
        md_files = sorted(directory.rglob('*.md'))

        print(f"\n[SCAN] Scanning {len(md_files)} Markdown files in {directory}...")

        for md_file in md_files:
            self.files_processed += 1

            # Skip certain directories
            if any(skip in str(md_file) for skip in ['_build', '.git', 'node_modules']):
                continue

            was_modified = self.fix_file(md_file)

            if was_modified:
                self.files_modified += 1
                status = "[DRY-RUN]" if self.dry_run else "[OK]"
                rel_path = md_file.relative_to(directory.parent) if directory.parent in md_file.parents else md_file
                print(f"  {status} {rel_path}")

    def print_summary(self):
        """Print processing summary."""
        print(f"\n{'='*70}")
        print("[SUMMARY] HEADER SPACING FIX SUMMARY")
        print(f"{'='*70}")
        print(f"Files processed: {self.files_processed}")
        print(f"Files modified:  {self.files_modified}")
        print(f"Lines fixed:     {self.lines_fixed}")

        if self.dry_run:
            print("\n[WARNING] DRY-RUN MODE - No files were actually modified")
            print("[INFO] Run without --dry-run to apply changes")
        else:
            print("\n[SUCCESS] Changes applied successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Fix header spacing issues in Sphinx/MyST documentation"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Directory to process (default: current directory)'
    )

    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"[ERROR] Path does not exist: {target_path}")
        return 1

    fixer = HeaderSpacingFixer(dry_run=args.dry_run)
    fixer.process_directory(target_path)
    fixer.print_summary()

    return 0


if __name__ == '__main__':
    exit(main())
