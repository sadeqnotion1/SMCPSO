#!/usr/bin/env python3
"""
Simple thesis checker - Windows compatible (ASCII only)
Checks word counts, citations, figures, and basic issues
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


def count_words(text):
    """Count words in text."""
    return len(text.split())


def find_citations(text):
    """Find citation references like [Author 2020]."""
    # Simple pattern: [Word Year]
    refs = re.findall(r'\[([A-Z][a-z]+(?:\s+et\s+al\.)?\s+\d{4}[a-z]?)\]', text)
    return len(set(refs))


def find_figures(text):
    """Find figure references."""
    refs = re.findall(r'[Ff]igure\s+(\d+(?:\.\d+)?)', text)
    return len(set(refs))


def check_todos(text):
    """Check for TODO/FIXME markers."""
    return text.upper().count('TODO') + text.upper().count('FIXME')


def check_placeholders(text):
    """Check for placeholder text."""
    count = text.upper().count('[INSERT')
    count += text.upper().count('PLACEHOLDER')
    count += text.upper().count('TBD')
    return count


def validate_chapter(file_path):
    """Validate a single chapter."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return None, f"Error reading file: {e}"

    stats = {
        'file': file_path.name,
        'words': count_words(content),
        'lines': len(content.split('\n')),
        'citations': find_citations(content),
        'figures': find_figures(content),
        'todos': check_todos(content),
        'placeholders': check_placeholders(content),
    }

    issues = []
    if stats['todos'] > 0:
        issues.append(f"{stats['todos']} TODO/FIXME markers found")
    if stats['placeholders'] > 0:
        issues.append(f"{stats['placeholders']} placeholder texts found")

    return stats, issues


def main():
    """Run thesis validation."""
    if len(sys.argv) > 1:
        thesis_dir = Path(sys.argv[1])
    else:
        thesis_dir = Path("docs/presentation")

    if not thesis_dir.exists():
        print(f"[ERROR] Directory not found: {thesis_dir}")
        sys.exit(1)

    print(f"[CHECK] Validating thesis in: {thesis_dir}")
    print()

    # Find all markdown files
    chapters = sorted(thesis_dir.glob("*.md"))

    if not chapters:
        print("[ERROR] No markdown files found")
        sys.exit(1)

    print(f"Found {len(chapters)} chapter files")
    print("="*80)

    all_stats = []
    all_issues = []

    for chapter_file in chapters:
        stats, issues = validate_chapter(chapter_file)

        if stats is None:
            print(f"[ERROR] {chapter_file.name}: {issues}")
            continue

        all_stats.append(stats)

        if issues:
            all_issues.append((chapter_file.name, issues))

    # Print summary
    print()
    print("="*80)
    print("[SUMMARY] THESIS VALIDATION RESULTS")
    print("="*80)
    print()

    total_words = sum(s['words'] for s in all_stats)
    total_citations = sum(s['citations'] for s in all_stats)
    total_figures = sum(s['figures'] for s in all_stats)
    total_todos = sum(s['todos'] for s in all_stats)
    total_placeholders = sum(s['placeholders'] for s in all_stats)

    print(f"Total chapters: {len(all_stats)}")
    print(f"Total words: {total_words:,}")
    print(f"Total citations: {total_citations}")
    print(f"Total figures: {total_figures}")
    print(f"TODOs/FIXMEs: {total_todos}")
    print(f"Placeholders: {total_placeholders}")
    print()

    # Per-chapter table
    print("="*80)
    print("[STATS] PER-CHAPTER BREAKDOWN")
    print("="*80)
    print()
    print(f"{'Chapter':<40} {'Words':>8} {'Cites':>6} {'Figs':>5}")
    print("-"*80)

    for stats in sorted(all_stats, key=lambda x: x['file']):
        print(f"{stats['file']:<40} {stats['words']:>8,} "
              f"{stats['citations']:>6} {stats['figures']:>5}")

    print("-"*80)
    print(f"{'TOTAL':<40} {total_words:>8,} {total_citations:>6} {total_figures:>5}")
    print()

    # Issues
    if all_issues:
        print("="*80)
        print("[ISSUES] FOUND IN FILES")
        print("="*80)
        print()
        for filename, issues in all_issues:
            print(f"[FILE] {filename}:")
            for issue in issues:
                print(f"  - {issue}")
            print()

        print(f"\n[WARNING] {len(all_issues)} files have issues")
        sys.exit(1)
    else:
        print("[OK] No critical issues found!")
        print()
        sys.exit(0)


if __name__ == "__main__":
    # Force UTF-8 output for Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    main()
