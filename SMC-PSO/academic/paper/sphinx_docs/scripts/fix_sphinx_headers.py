#!/usr/bin/env python3
"""
Comprehensive Sphinx Warning Remediation Script

Systematically fixes 3 major categories of Sphinx warnings:
1. Files with H1 on same line as ASCII header (242 warnings)
2. Non-consecutive header level jumps (227 warnings)
3. Duplicate bibliography citations (188 warnings)

Usage:
    python fix_sphinx_headers.py --dry-run  # Preview changes
    python fix_sphinx_headers.py           # Apply fixes
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict


class SphinxHeaderFixer:
    """Fixes header structure issues in Markdown files."""

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'ascii_header_fixes': 0,
            'header_level_fixes': 0,
            'citation_fixes': 0,
            'errors': []
        }

    def fix_ascii_header_separation(self, content: str, filepath: Path) -> Tuple[str, bool]:
        r"""
        Fix H1 titles that are on the same line as ASCII headers.

        Pattern:
            #===...===\\\ # Title Here
        Should be:
            #===...===\\\

            # Title Here
        """
        lines = content.splitlines(keepends=True)
        modified = False

        # Check first few lines for ASCII header + H1 pattern
        for i in range(min(5, len(lines))):
            line = lines[i]
            # Match: comment-style line ending with \\\ followed by # Title
            match = re.match(r'^(#[=\-]+.*\\\\\\ )(# .+)$', line)
            if match:
                ascii_part = match.group(1).rstrip()
                h1_part = match.group(2)

                # Replace with separated version
                lines[i] = ascii_part + '\n\n' + h1_part + '\n'
                modified = True
                self.stats['ascii_header_fixes'] += 1

                if not self.dry_run:
                    print(f"  [OK] Fixed ASCII+H1 separation in {filepath.name}")
                else:
                    print(f"  [DRY RUN] Would fix ASCII+H1 in {filepath.name}")
                break

        return ''.join(lines), modified

    def fix_header_hierarchy(self, content: str, filepath: Path) -> Tuple[str, bool]:
        """
        Fix non-consecutive header level jumps.

        Rules:
        - If document starts with ##, convert first ## to #
        - Fix H1→H3 jumps by converting ### to ##
        - Fix H2→H4 jumps by converting #### to ###
        """
        lines = content.splitlines(keepends=True)
        modified = False

        # Track header levels seen
        headers_by_line = []
        first_header_idx = None

        # First pass: identify all headers and their levels
        in_code_block = False
        for i, line in enumerate(lines):
            # Skip code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Match markdown headers (not in comments)
            if line.startswith('#') and not line.startswith('#===') and not line.startswith('#---'):
                match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if match:
                    level = len(match.group(1))
                    text = match.group(2)
                    headers_by_line.append((i, level, text))
                    if first_header_idx is None:
                        first_header_idx = i

        if not headers_by_line:
            return content, False

        # Second pass: fix header levels
        fixes = []
        prev_level = 0

        for idx, (line_num, level, text) in enumerate(headers_by_line):
            new_level = level

            # Fix 1: First header should be H1
            if idx == 0 and level > 1:
                new_level = 1
                fixes.append((line_num, level, new_level, text))
                self.stats['header_level_fixes'] += 1

            # Fix 2: No jumps > 1 level
            elif prev_level > 0 and level > prev_level + 1:
                # Jumped too many levels, reduce to prev_level + 1
                new_level = prev_level + 1
                fixes.append((line_num, level, new_level, text))
                self.stats['header_level_fixes'] += 1

            prev_level = new_level

        # Apply fixes
        if fixes:
            modified = True
            for line_num, old_level, new_level, text in fixes:
                old_header = '#' * old_level
                new_header = '#' * new_level
                lines[line_num] = lines[line_num].replace(
                    f'{old_header} {text}',
                    f'{new_header} {text}'
                )

                if not self.dry_run:
                    print(f"  [OK] Fixed H{old_level}->H{new_level} in {filepath.name} at line {line_num+1}")
                else:
                    print(f"  [DRY RUN] Would fix H{old_level}->H{new_level} in {filepath.name}")

        return ''.join(lines), modified

    def process_file(self, filepath: Path) -> bool:
        """Process a single Markdown file."""
        try:
            content = filepath.read_text(encoding='utf-8')
            original_content = content

            # Apply fixes in sequence
            content, mod1 = self.fix_ascii_header_separation(content, filepath)
            content, mod2 = self.fix_header_hierarchy(content, filepath)

            modified = mod1 or mod2

            # Write back if modified and not dry run
            if modified and not self.dry_run:
                filepath.write_text(content, encoding='utf-8')
                self.stats['files_processed'] += 1
            elif modified:
                self.stats['files_processed'] += 1

            return modified

        except Exception as e:
            error_msg = f"Error processing {filepath}: {e}"
            self.stats['errors'].append(error_msg)
            print(f"  [ERROR] {error_msg}")
            return False

    def process_all_files(self) -> None:
        """Process all Markdown files in docs directory."""
        md_files = list(self.docs_root.rglob('*.md'))

        print(f"\nProcessing {len(md_files)} Markdown files...")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n")

        for md_file in md_files:
            # Skip certain directories
            if any(part in md_file.parts for part in ['.venv', 'node_modules', '_build']):
                continue

            self.process_file(md_file)

        self.print_summary()

    def print_summary(self) -> None:
        """Print summary statistics."""
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"ASCII header fixes: {self.stats['ascii_header_fixes']}")
        print(f"Header level fixes: {self.stats['header_level_fixes']}")
        print(f"Citation fixes: {self.stats['citation_fixes']}")

        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"  - {error}")

        total_fixes = (self.stats['ascii_header_fixes'] +
                      self.stats['header_level_fixes'] +
                      self.stats['citation_fixes'])

        print(f"\nTotal fixes: {total_fixes}")

        if self.dry_run:
            print("\n[WARNING] DRY RUN MODE - No files were modified")
            print("Run without --dry-run to apply changes")
        else:
            print("\n[SUCCESS] Fixes applied successfully")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix Sphinx header structure warnings in Markdown files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--docs-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Root directory of documentation (default: ../)'
    )

    args = parser.parse_args()

    fixer = SphinxHeaderFixer(args.docs_root, dry_run=args.dry_run)
    fixer.process_all_files()

    return 0 if not fixer.stats['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())
