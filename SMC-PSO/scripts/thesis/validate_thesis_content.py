#!/usr/bin/env python3
"""
Thesis Content Validation Script
Validates existing thesis chapters for common issues:
- Citation completeness
- Figure references
- Math notation consistency
- Section structure
- Common errors
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set


class ThesisValidator:
    """Validate thesis content for common issues."""

    def __init__(self, thesis_dir: Path):
        self.thesis_dir = Path(thesis_dir)
        self.issues = defaultdict(list)
        self.stats = defaultdict(dict)

    def validate_all_chapters(self) -> Dict:
        """Run all validation checks on all chapters."""
        print(f"[VALIDATING] Thesis chapters in: {self.thesis_dir}\n")

        # Find all markdown files
        chapters = sorted(self.thesis_dir.glob("*.md"))

        if not chapters:
            print(f"[ERROR] No markdown files found in {self.thesis_dir}")
            return {}

        print(f"Found {len(chapters)} chapter files:\n")

        for chapter_file in chapters:
            print(f"[FILE] Validating: {chapter_file.name}")
            self.validate_chapter(chapter_file)
            print()

        # Generate report
        self.print_summary()
        return self.stats

    def validate_chapter(self, chapter_path: Path):
        """Validate a single chapter file."""
        content = chapter_path.read_text(encoding='utf-8')
        filename = chapter_path.name

        # Basic stats
        lines = content.split('\n')
        word_count = len(content.split())
        self.stats[filename]['word_count'] = word_count
        self.stats[filename]['line_count'] = len(lines)
        self.stats[filename]['char_count'] = len(content)

        # Run checks
        self._check_citations(filename, content)
        self._check_figures(filename, content)
        self._check_math_notation(filename, content)
        self._check_headings(filename, content)
        self._check_common_errors(filename, content)

        # Print chapter stats
        print(f"  [STATS] {word_count:,} words | {len(lines):,} lines")
        print(f"  [OK] Validations complete")

    def _check_citations(self, filename: str, content: str):
        """Check citation consistency."""
        # Find all citation references [Author Year]
        citation_refs = re.findall(r'\[([A-Z][a-z]+(?:\s+et\s+al\.)?\s+\d{4}[a-z]?)\]', content)
        # Find all citation definitions (usually at end)
        citation_defs = re.findall(r'^\s*-\s+([A-Z][a-z]+.*?\d{4})', content, re.MULTILINE)

        refs_set = set(citation_refs)
        defs_set = set(citation_defs)

        self.stats[filename]['citations_referenced'] = len(refs_set)
        self.stats[filename]['citations_defined'] = len(defs_set)

        # Check for missing definitions
        missing_defs = refs_set - defs_set
        if missing_defs:
            for ref in missing_defs:
                self.issues[filename].append(f"Citation referenced but not defined: [{ref}]")

    def _check_figures(self, filename: str, content: str):
        """Check figure references."""
        # Find figure references
        fig_refs = re.findall(r'[Ff]igure\s+(\d+(?:\.\d+)?)', content)
        fig_refs_set = set(fig_refs)

        # Find figure definitions (captions or image tags)
        fig_defs = re.findall(r'!\[.*?\]\(.*?\)|Figure\s+(\d+(?:\.\d+)?)\s*:', content)
        fig_defs_set = set(f for f in fig_defs if f)  # Filter empty matches

        self.stats[filename]['figures_referenced'] = len(fig_refs_set)
        self.stats[filename]['figures_defined'] = len(fig_defs_set)

        # Check for missing figures
        missing_figs = fig_refs_set - fig_defs_set
        if missing_figs:
            for fig in sorted(missing_figs, key=lambda x: float(x)):
                self.issues[filename].append(f"Figure referenced but not defined: Figure {fig}")

    def _check_math_notation(self, filename: str, content: str):
        """Check mathematical notation consistency."""
        # Check for inline math
        inline_math = re.findall(r'\$[^$]+\$', content)
        # Check for display math
        display_math = re.findall(r'\$\$[^$]+\$\$', content)

        self.stats[filename]['inline_math_count'] = len(inline_math)
        self.stats[filename]['display_math_count'] = len(display_math)

        # Check for common LaTeX errors
        unmatched_dollars = content.count('$') % 2
        if unmatched_dollars:
            self.issues[filename].append("Unmatched $ symbols (odd count) - check math notation")

        # Check for common notation inconsistencies
        if '\\theta' in content and 'θ' in content:
            self.issues[filename].append("Mixed theta notation: both \\theta and θ found")

    def _check_headings(self, filename: str, content: str):
        """Check heading structure."""
        # Find all markdown headings
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)

        self.stats[filename]['heading_count'] = len(headings)

        if not headings:
            self.issues[filename].append("No headings found - check chapter structure")
            return

        # Check heading hierarchy
        prev_level = 0
        for level_str, heading_text in headings:
            level = len(level_str)
            if level - prev_level > 1:
                self.issues[filename].append(
                    f"Heading hierarchy skip: {level_str} {heading_text} "
                    f"(jumped from level {prev_level} to {level})"
                )
            prev_level = level

    def _check_common_errors(self, filename: str, content: str):
        """Check for common thesis writing errors."""
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for double spaces
            if '  ' in line and not line.strip().startswith('```'):
                self.issues[filename].append(f"Line {i}: Double spaces found")

            # Check for TODO/FIXME
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                self.issues[filename].append(f"Line {i}: TODO/FIXME marker found")

            # Check for placeholder text
            if '[INSERT' in line.upper() or 'PLACEHOLDER' in line.upper():
                self.issues[filename].append(f"Line {i}: Placeholder text found")

    def print_summary(self):
        """Print validation summary report."""
        print("\n" + "="*80)
        print("[SUMMARY] THESIS VALIDATION SUMMARY")
        print("="*80 + "\n")

        # Total stats
        total_words = sum(s.get('word_count', 0) for s in self.stats.values())
        total_citations = sum(s.get('citations_referenced', 0) for s in self.stats.values())
        total_figures = sum(s.get('figures_referenced', 0) for s in self.stats.values())

        print(f"[STATS] Overall Statistics:")
        print(f"  Total chapters: {len(self.stats)}")
        print(f"  Total words: {total_words:,}")
        print(f"  Total citations: {total_citations}")
        print(f"  Total figures referenced: {total_figures}")
        print()

        # Issue summary
        total_issues = sum(len(issues) for issues in self.issues.values())

        if total_issues == 0:
            print("[OK] No issues found! Thesis validation passed.\n")
        else:
            print(f"[WARNING] Found {total_issues} issues across {len(self.issues)} files:\n")

            for filename, file_issues in sorted(self.issues.items()):
                if file_issues:
                    print(f"[FILE] {filename} ({len(file_issues)} issues):")
                    for issue in file_issues[:5]:  # Show first 5
                        print(f"  - {issue}")
                    if len(file_issues) > 5:
                        print(f"  ... and {len(file_issues) - 5} more")
                    print()

        # Per-chapter stats table
        print("\n" + "="*80)
        print("[STATS] PER-CHAPTER STATISTICS")
        print("="*80 + "\n")
        print(f"{'Chapter':<35} {'Words':>8} {'Cites':>6} {'Figs':>5} {'Issues':>7}")
        print("-" * 80)

        for filename in sorted(self.stats.keys()):
            stats = self.stats[filename]
            issues_count = len(self.issues.get(filename, []))
            print(f"{filename:<35} {stats.get('word_count', 0):>8,} "
                  f"{stats.get('citations_referenced', 0):>6} "
                  f"{stats.get('figures_referenced', 0):>5} "
                  f"{issues_count:>7}")

        print("-" * 80)
        print(f"{'TOTAL':<35} {total_words:>8,} {total_citations:>6} {total_figures:>5} {total_issues:>7}")
        print()


def main():
    """Run thesis validation."""
    if len(sys.argv) > 1:
        thesis_dir = Path(sys.argv[1])
    else:
        # Default to docs/presentation
        thesis_dir = Path(__file__).parent.parent.parent / "docs" / "presentation"

    if not thesis_dir.exists():
        print(f"[ERROR] Directory not found: {thesis_dir}")
        sys.exit(1)

    validator = ThesisValidator(thesis_dir)
    validator.validate_all_chapters()

    # Return exit code based on critical issues
    critical_issues = sum(
        1 for file_issues in validator.issues.values()
        for issue in file_issues
        if 'TODO' in issue or 'PLACEHOLDER' in issue or 'not defined' in issue
    )

    if critical_issues > 0:
        print(f"\n[WARNING] {critical_issues} critical issues found. Review recommended.")
        sys.exit(1)
    else:
        print("\n[OK] Thesis validation passed! No critical issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
