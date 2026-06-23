#!/usr/bin/env python3
"""
Targeted header hierarchy fix for remaining warnings.

Fixes specific patterns:
1. H2 -> H4 jumps (convert H4 to H3)
2. H1 -> H3 jumps (insert missing H2 or demote H1)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class AggressiveHeaderFixer:
    """More aggressive header hierarchy fixing."""

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root
        self.dry_run = dry_run
        self.fixes_applied = 0

    def fix_file_hierarchy(self, filepath: Path) -> bool:
        """Fix header hierarchy in a single file."""
        try:
            content = filepath.read_text(encoding='utf-8')
            original = content

            # Parse headers
            headers = self.parse_headers(content)
            if not headers:
                return False

            # Build fix map
            fix_map = self.build_fix_map(headers)
            if not fix_map:
                return False

            # Apply fixes from end to start (to preserve line positions)
            lines = content.splitlines()
            for line_num in sorted(fix_map.keys(), reverse=True):
                old_level, new_level, text = fix_map[line_num]
                old_header = '#' * old_level + ' ' + text
                new_header = '#' * new_level + ' ' + text

                if lines[line_num].strip() == old_header.strip():
                    lines[line_num] = lines[line_num].replace(old_header, new_header)
                    self.fixes_applied += 1

                    if not self.dry_run:
                        print(f"  [OK] {filepath.name}:{line_num+1} H{old_level}->H{new_level}")
                    else:
                        print(f"  [DRY] {filepath.name}:{line_num+1} H{old_level}->H{new_level}")

            if fix_map:
                new_content = '\n'.join(lines)
                if new_content != original and not self.dry_run:
                    filepath.write_text(new_content, encoding='utf-8')
                return True

            return False

        except Exception as e:
            print(f"[ERROR] {filepath}: {e}")
            return False

    def parse_headers(self, content: str) -> List[Tuple[int, int, str]]:
        """Parse headers: [(line_num, level, text), ...]"""
        headers = []
        in_code_block = False

        for i, line in enumerate(content.splitlines()):
            # Skip code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Skip ASCII headers
            if line.startswith('#===') or line.startswith('#---'):
                continue

            # Match markdown headers
            if line.startswith('#'):
                match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if match:
                    level = len(match.group(1))
                    text = match.group(2).strip()
                    headers.append((i, level, text))

        return headers

    def build_fix_map(self, headers: List[Tuple[int, int, str]]) -> dict:
        """Build map of line_num -> (old_level, new_level, text)."""
        fix_map = {}
        prev_level = 0

        for line_num, level, text in headers:
            new_level = level

            # Rule 1: No jumps > 1
            if prev_level > 0 and level > prev_level + 1:
                # Reduce to max allowed level
                new_level = prev_level + 1
                fix_map[line_num] = (level, new_level, text)

            # Rule 2: First header should be H1
            elif prev_level == 0 and level > 1:
                new_level = 1
                fix_map[line_num] = (level, new_level, text)

            prev_level = new_level if line_num in fix_map else level

        return fix_map

    def process_files(self, file_list: List[Path]) -> None:
        """Process multiple files."""
        print(f"\nProcessing {len(file_list)} files...")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n")

        for filepath in file_list:
            self.fix_file_hierarchy(filepath)

        print(f"\n{'[DRY RUN] Would apply' if self.dry_run else 'Applied'} {self.fixes_applied} fixes")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Fix remaining header hierarchy warnings')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--docs-root', type=Path, default=Path(__file__).parent.parent)
    parser.add_argument('files', nargs='*', help='Specific files to fix (optional)')

    args = parser.parse_args()

    fixer = AggressiveHeaderFixer(args.docs_root, dry_run=args.dry_run)

    if args.files:
        # Fix specific files
        file_list = [Path(f) for f in args.files]
    else:
        # Fix all markdown files with known issues
        problem_files = [
            'guides/api/simulation.md',
            'guides/getting-started-validation-report.md',
            'reference/analysis/core_interfaces.md',
            'reference/analysis/fault_detection_residual_generators.md',
            'reference/analysis/fault_detection_threshold_adapters.md',
            'reference/analysis/performance_robustness.md',
            'reference/benchmarks/core_trial_runner.md',
            'reference/benchmarks/metrics_constraint_metrics.md',
            'reference/benchmarks/metrics_stability_metrics.md',
            'reference/benchmarks/statistics_confidence_intervals.md',
            'reference/config/loader.md',
            'reference/config/logging.md',
            'reference/controllers/base_control_primitives.md',
            'reference/controllers/factory_core_validation.md',
            'reference/controllers/factory_legacy_factory.md',
        ]
        file_list = [args.docs_root / f for f in problem_files if (args.docs_root / f).exists()]

    fixer.process_files(file_list)

    return 0


if __name__ == '__main__':
    sys.exit(main())
