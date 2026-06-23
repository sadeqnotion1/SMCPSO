#!/usr/bin/env python3
r"""
Phase 9B: Fix Line 1 Header Concatenation

Fixes auto-generated documentation files where line 1 contains multiple
headers and sections concatenated together, causing header hierarchy warnings.

Pattern detected:
# analysis.core.interfaces **Source:** `src\...` ## Module Overview ... ### Details ...

Should be:
# analysis.core.interfaces

**Source:** `src\analysis\core\interfaces.py`

## Module Overview

Core interfaces for the analysis framework.

Usage:
    python fix_line1_concatenation.py --dry-run  # Preview changes
    python fix_line1_concatenation.py            # Apply fixes
"""

import re
import sys
from pathlib import Path


class Line1ConcatenationFixer:
    """Fix concatenated headers on line 1 of documentation files."""

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'lines_split': 0,
            'errors': []
        }

    def detect_concatenation(self, line: str) -> bool:
        """Detect if line 1 has concatenated headers.

        Patterns:
        - # Title ## Section
        - # Title **Source:** ... ## Section
        - Multiple ## or ### on same line
        """
        # Must start with H1
        if not line.startswith('# '):
            return False

        # Count header markers after the first one
        rest = line[2:]  # After "# "

        # Look for ## or ### later in the line
        if ' ## ' in rest or ' ### ' in rest:
            return True

        # Look for **Source:** pattern followed by more content
        if '**Source:**' in rest:
            source_pos = rest.find('**Source:**')
            after_source = rest[source_pos + 12:]  # After "**Source:**"
            # If there's substantial content after source, likely concatenated
            if len(after_source.strip()) > 50:
                return True

        return False

    def split_concatenated_line(self, line: str) -> list:
        """Split concatenated line 1 into properly formatted lines.

        Returns list of lines to replace line 1 with.
        """
        result = []

        # Extract H1 title (everything before first ** or ##)
        match_h1 = re.match(r'#\s+([^*#]+)', line)
        if match_h1:
            h1_title = match_h1.group(1).strip()
            result.append(f'# {h1_title}')
            result.append('')  # Blank line
            remaining = line[len(match_h1.group(0)):]
        else:
            # Fallback: just return original if we can't parse
            return [line]

        # Extract **Source:** if present
        source_match = re.search(r'\*\*Source:\*\*\s*`([^`]+)`', remaining)
        if source_match:
            source_path = source_match.group(1).strip()
            result.append(f'**Source:** `{source_path}`')
            result.append('')  # Blank line
            remaining = remaining[source_match.end():]

        # Split remaining by headers
        # Pattern: ## Header or ### Header
        parts = re.split(r'(\s*##\s+|\s*###\s+)', remaining)

        current_text = ''
        current_level = None

        for i, part in enumerate(parts):
            if part.strip() in ['##', '###']:
                # Header marker
                if current_text.strip():
                    result.append(current_text.strip())
                    result.append('')
                    current_text = ''
                current_level = part.strip()
            elif current_level:
                # Content after header marker
                header_text = part.split('.', 1)[0].split('**', 1)[0].strip()
                if header_text:
                    result.append(f'{current_level} {header_text}')
                    result.append('')
                    # Keep remaining content
                    rest_content = part[len(header_text):].strip()
                    if rest_content and not rest_content.startswith(('##', '###', '**')):
                        result.append(rest_content)
                        result.append('')
                current_level = None
            else:
                # Regular content
                current_text += part

        # Add any remaining content
        if current_text.strip():
            result.append(current_text.strip())
            result.append('')

        # Clean up: remove excessive blank lines
        cleaned = []
        prev_blank = False
        for line in result:
            if not line:
                if not prev_blank:
                    cleaned.append(line)
                prev_blank = True
            else:
                cleaned.append(line)
                prev_blank = False

        return cleaned

    def fix_file_line1(self, filepath: Path) -> bool:
        """Fix line 1 concatenation in a single file."""
        try:
            lines = filepath.read_text(encoding='utf-8').splitlines(keepends=False)
            if not lines:
                return False

            # Check if line 1 has concatenation issue
            if not self.detect_concatenation(lines[0]):
                return False

            # Split line 1
            new_lines = self.split_concatenated_line(lines[0])

            # Replace line 1 with split version, keep rest of file
            result = new_lines + lines[1:]

            if not self.dry_run:
                filepath.write_text('\n'.join(result) + '\n', encoding='utf-8')
                print(f"  [OK] {filepath.name}: Line 1 split into {len(new_lines)} lines")
            else:
                print(f"  [DRY RUN] {filepath.name}: Line 1 would be split into {len(new_lines)} lines")

            self.stats['files_processed'] += 1
            self.stats['lines_split'] += 1
            return True

        except Exception as e:
            error_msg = f"Error processing {filepath}: {e}"
            self.stats['errors'].append(error_msg)
            print(f"  [ERROR] {error_msg}")
            return False

    def process_all_files(self) -> None:
        """Process all Markdown files in docs directory."""
        # Focus on reference documentation (most likely to have this issue)
        md_files = list(self.docs_root.glob('reference/**/*.md'))

        print(f"\nScanning {len(md_files)} reference documentation files for line 1 concatenation...")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n")

        for md_file in md_files:
            self.fix_file_line1(md_file)

        self.print_summary()

    def print_summary(self) -> None:
        """Print summary statistics."""
        print("\n" + "="*70)
        print("LINE 1 CONCATENATION FIX SUMMARY")
        print("="*70)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Lines split: {self.stats['lines_split']}")

        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        if self.dry_run:
            print("\n[WARNING] DRY RUN MODE - No files were modified")
            print("Run without --dry-run to apply changes")
        else:
            print("\n[SUCCESS] Line 1 concatenations fixed successfully")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix line 1 header concatenation in documentation files'
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

    fixer = Line1ConcatenationFixer(args.docs_root, dry_run=args.dry_run)
    fixer.process_all_files()

    return 0 if not fixer.stats['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())
