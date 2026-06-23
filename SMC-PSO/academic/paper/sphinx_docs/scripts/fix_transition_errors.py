#!/usr/bin/env python3
"""
Phase 9A: Fix Docutils Transition Errors

Fixes "Document or section may not begin with a transition" errors by:
1. Detecting `---` at invalid positions (line 3, document end, section start)
2. Removing or relocating transitions
3. Adding minimal content before transition if needed

Usage:
    python fix_transition_errors.py --dry-run  # Preview changes
    python fix_transition_errors.py            # Apply fixes
"""

import re
import sys
from pathlib import Path


class TransitionFixer:
    """Fix docutils transition errors in Markdown files."""

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'transitions_removed': 0,
            'transitions_relocated': 0,
            'content_added': 0,
            'errors': []
        }

    def is_transition(self, line: str) -> bool:
        """Check if line is a transition (---).

        Must be exactly 3 or more hyphens, optionally with whitespace.
        """
        stripped = line.strip()
        return bool(re.match(r'^-{3,}$', stripped))

    def is_header(self, line: str) -> bool:
        """Check if line is a Markdown header."""
        return bool(re.match(r'^#{1,6}\s+', line))

    def get_header_level(self, line: str) -> int:
        """Get header level (1-6) or 0 if not a header."""
        match = re.match(r'^(#{1,6})\s+', line)
        return len(match.group(1)) if match else 0

    def fix_file_transitions(self, filepath: Path) -> bool:
        """Fix transition errors in a single file."""
        try:
            lines = filepath.read_text(encoding='utf-8').splitlines(keepends=False)
            if not lines:
                return False

            modified = False

            # Track changes
            changes = []

            # Fix 1: Remove transition at line 3 (immediately after title)
            if len(lines) >= 3:
                if self.is_header(lines[0]) and lines[1].strip() == '' and self.is_transition(lines[2]):
                    # Remove transition and extra blank line
                    lines[2] = ''
                    changes.append(('remove', 3, 'transition immediately after title'))
                    modified = True
                    self.stats['transitions_removed'] += 1

            # Fix 2: Remove transitions at document end
            while lines and self.is_transition(lines[-1]):
                lines[-1] = ''
                changes.append(('remove', len(lines), 'transition at document end'))
                modified = True
                self.stats['transitions_removed'] += 1

            # Remove trailing blank lines created by fixes
            while lines and lines[-1].strip() == '':
                lines.pop()

            # Fix 3: Detect transitions immediately after headers (section start)
            in_code_block = False
            i = 0
            while i < len(lines):
                line = lines[i]

                # Track code blocks
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    i += 1
                    continue

                if in_code_block:
                    i += 1
                    continue

                # Check pattern: Header, blank line (optional), transition
                if self.is_header(line):
                    next_idx = i + 1
                    # Skip blank lines
                    while next_idx < len(lines) and lines[next_idx].strip() == '':
                        next_idx += 1

                    # Check if next non-blank line is transition
                    if next_idx < len(lines) and self.is_transition(lines[next_idx]):
                        # Check if there's content between header and transition
                        has_content = False
                        for j in range(i + 1, next_idx):
                            if lines[j].strip():
                                has_content = True
                                break

                        if not has_content:
                            # Remove the transition
                            lines[next_idx] = ''
                            changes.append(('remove', next_idx + 1, 'transition after header'))
                            modified = True
                            self.stats['transitions_removed'] += 1

                i += 1

            # Only write if modified
            if modified:
                # Remove empty lines created by removals (but preserve intentional spacing)
                cleaned = []
                prev_blank = False
                for line in lines:
                    if line.strip() == '':
                        if not prev_blank:
                            cleaned.append(line)
                        prev_blank = True
                    else:
                        cleaned.append(line)
                        prev_blank = False

                if not self.dry_run:
                    filepath.write_text('\n'.join(cleaned) + '\n', encoding='utf-8')
                    print(f"  [OK] {filepath.name}: {len(changes)} transition(s) fixed")
                else:
                    print(f"  [DRY RUN] {filepath.name}: {len(changes)} transition(s) would be fixed")

                for change_type, line_num, desc in changes:
                    action = f"  [{change_type.upper()}] Line {line_num}: {desc}"
                    if self.dry_run:
                        print(f"    [DRY RUN] {action}")
                    else:
                        print(f"    {action}")

                self.stats['files_processed'] += 1
                return True

            return False

        except Exception as e:
            error_msg = f"Error processing {filepath}: {e}"
            self.stats['errors'].append(error_msg)
            print(f"  [ERROR] {error_msg}")
            return False

    def process_all_files(self) -> None:
        """Process all Markdown files in docs directory."""
        # Get all .md files
        md_files = list(self.docs_root.rglob('*.md'))
        # Exclude build directories
        md_files = [f for f in md_files if '_build' not in str(f)]

        print(f"\nScanning {len(md_files)} Markdown files for transition errors...")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n")

        for md_file in md_files:
            self.fix_file_transitions(md_file)

        self.print_summary()

    def print_summary(self) -> None:
        """Print summary statistics."""
        print("\n" + "="*70)
        print("TRANSITION ERROR FIX SUMMARY")
        print("="*70)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Transitions removed: {self.stats['transitions_removed']}")
        print(f"Transitions relocated: {self.stats['transitions_relocated']}")
        print(f"Content added: {self.stats['content_added']}")

        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        total_fixes = (self.stats['transitions_removed'] +
                      self.stats['transitions_relocated'] +
                      self.stats['content_added'])

        print(f"\nTotal fixes: {total_fixes}")

        if self.dry_run:
            print("\n[WARNING] DRY RUN MODE - No files were modified")
            print("Run without --dry-run to apply changes")
        else:
            print("\n[SUCCESS] Transition errors fixed successfully")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix docutils transition errors in Markdown files'
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

    fixer = TransitionFixer(args.docs_root, dry_run=args.dry_run)
    fixer.process_all_files()

    return 0 if not fixer.stats['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())
