"""
Long Sentence Analyzer for Markdown Documentation
=================================================

Analyzes and reports long sentences (>30 words) in markdown files.

NOTE: This script REPORTS long sentences but does NOT auto-fix them.
Sentence splitting requires understanding context and is best done manually.

The script provides:
1. Detection of sentences >30 words
2. Word count for each long sentence
3. Line numbers and context
4. Suggestions for potential split points (conjunctions, semicolons)

Usage:
    python scripts/docs/sentence_analyzer.py --file README.md
    python scripts/docs/sentence_analyzer.py --all

Author: Claude Code (Automated QA Script)
Date: November 2025
"""

import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


def remove_emojis_for_display(text: str) -> str:
    """
    Remove emojis from text to make it safe for Windows terminal display.

    Args:
        text: Input text

    Returns:
        Text with emojis removed (replaced with [EMOJI])
    """
    # Unicode emoji ranges (comprehensive)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U00002600-\U000026FF"  # Miscellaneous Symbols
        "\U00002700-\U000027BF"  # Dingbats
        "]+",
        flags=re.UNICODE
    )

    return emoji_pattern.sub('[EMOJI]', text)


def is_code_block_line(line: str) -> bool:
    """Check if line is part of a code block."""
    stripped = line.strip()
    return (stripped.startswith('```') or
            stripped.startswith('    ') or  # Indented code
            stripped.startswith('\t'))      # Tab-indented code


def is_list_item(line: str) -> bool:
    """Check if line is a list item."""
    stripped = line.strip()
    return (stripped.startswith('- ') or
            stripped.startswith('* ') or
            stripped.startswith('+ ') or
            re.match(r'^\d+\.\s', stripped) is not None)


def is_heading(line: str) -> bool:
    """Check if line is a heading."""
    return line.strip().startswith('#')


def count_words(text: str) -> int:
    """Count words in text (excluding markdown syntax)."""
    # Remove markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove inline code `code`
    text = re.sub(r'`[^`]+`', '', text)
    # Remove markdown bold/italic **text** or *text*
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    # Count words
    words = text.split()
    return len(words)


def suggest_split_points(sentence: str) -> List[Tuple[str, int]]:
    """
    Suggest potential split points in a long sentence.

    Returns:
        List of (conjunction/punctuation, position) tuples
    """
    suggestions = []

    # Coordinating conjunctions (FANBOYS)
    conjunctions = ['and', 'but', 'or', 'nor', 'for', 'so', 'yet']
    for conj in conjunctions:
        pattern = r'\s+' + conj + r'\s+'
        for match in re.finditer(pattern, sentence, re.IGNORECASE):
            suggestions.append((conj, match.start()))

    # Semicolons (natural split points)
    for match in re.finditer(r';', sentence):
        suggestions.append((';', match.start()))

    # Em dashes (natural split points)
    for match in re.finditer(r'—', sentence):
        suggestions.append(('—', match.start()))

    # Sort by position
    suggestions.sort(key=lambda x: x[1])

    return suggestions


def analyze_paragraph(paragraph: str, start_line: int) -> List[Dict]:
    """
    Analyze a paragraph for long sentences.

    Args:
        paragraph: The paragraph text
        start_line: Starting line number

    Returns:
        List of long sentence reports
    """
    # Split into sentences (basic sentence detection)
    # This handles periods, exclamation marks, question marks
    sentences = re.split(r'(?<=[.!?])\s+', paragraph)

    reports = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        word_count = count_words(sentence)
        if word_count > 30:
            split_suggestions = suggest_split_points(sentence)
            reports.append({
                'line': start_line,
                'sentence': sentence,
                'word_count': word_count,
                'split_suggestions': split_suggestions[:3]  # Top 3 suggestions
            })

    return reports


def analyze_file(file_path: Path) -> Dict:
    """
    Analyze a markdown file for long sentences.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with analysis results
    """
    if not file_path.exists():
        return {
            'status': 'error',
            'message': f"File not found: {file_path}",
            'reports': []
        }

    try:
        lines = file_path.read_text(encoding='utf-8').splitlines()
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to read file: {e}",
            'reports': []
        }

    reports = []
    in_code_block = False
    current_paragraph = ""
    paragraph_start_line = 0

    for i, line in enumerate(lines, start=1):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            # Process accumulated paragraph
            if current_paragraph:
                reports.extend(analyze_paragraph(current_paragraph, paragraph_start_line))
                current_paragraph = ""
            continue

        # Skip code blocks, list items, headings
        if (in_code_block or
            is_code_block_line(line) or
            is_list_item(line) or
            is_heading(line)):
            # Process accumulated paragraph
            if current_paragraph:
                reports.extend(analyze_paragraph(current_paragraph, paragraph_start_line))
                current_paragraph = ""
            continue

        # Empty line: end of paragraph
        if not line.strip():
            if current_paragraph:
                reports.extend(analyze_paragraph(current_paragraph, paragraph_start_line))
                current_paragraph = ""
            continue

        # Accumulate paragraph
        if not current_paragraph:
            paragraph_start_line = i
        current_paragraph += " " + line.strip()

    # Process final paragraph
    if current_paragraph:
        reports.extend(analyze_paragraph(current_paragraph, paragraph_start_line))

    return {
        'status': 'success',
        'file': str(file_path),
        'reports': reports,
        'total_long_sentences': len(reports)
    }


def main():
    parser = argparse.ArgumentParser(
        description='Analyze markdown files for long sentences (>30 words)'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Single file to analyze'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Analyze all 4 main entry points (README.md, CLAUDE.md, docs/index.md, guides/INDEX.md)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=30,
        help='Word count threshold for long sentences (default: 30)'
    )

    args = parser.parse_args()

    # Determine files to analyze
    if args.all:
        files_to_analyze = [
            Path('README.md'),
            Path('CLAUDE.md'),
            Path('docs/index.md'),
            Path('docs/guides/INDEX.md')
        ]
    elif args.file:
        files_to_analyze = [args.file]
    else:
        parser.error("Must specify either --file or --all")

    # Analyze each file
    print(f"\n[INFO] Long Sentence Analyzer")
    print(f"[INFO] Threshold: >{args.threshold} words")
    print(f"[INFO] Analyzing {len(files_to_analyze)} file(s)\n")

    all_results = []
    for file_path in files_to_analyze:
        print(f"{'=' * 70}")
        print(f"File: {file_path}")
        print(f"{'=' * 70}")

        result = analyze_file(file_path)
        all_results.append(result)

        if result['status'] == 'error':
            print(f"[ERROR] {result['message']}\n")
            continue

        reports = result['reports']
        if not reports:
            print("[OK] No long sentences found!\n")
            continue

        print(f"[WARNING] Found {len(reports)} long sentence(s)\n")

        for i, report in enumerate(reports, start=1):
            print(f"  [{i}] Line {report['line']}: {report['word_count']} words")

            # Show truncated sentence (first 80 chars, safe for Windows terminal)
            sentence = remove_emojis_for_display(report['sentence'])
            if len(sentence) > 80:
                print(f"      \"{sentence[:77]}...\"")
            else:
                print(f"      \"{sentence}\"")

            # Show split suggestions
            if report['split_suggestions']:
                print(f"      Suggested split points:")
                for punct, pos in report['split_suggestions']:
                    print(f"        - '{punct}' at position {pos}")
            print()

    # Summary
    total_long_sentences = sum(r.get('total_long_sentences', 0) for r in all_results)
    successful = sum(1 for r in all_results if r['status'] == 'success')
    errors = sum(1 for r in all_results if r['status'] == 'error')

    print("=" * 70)
    print(f"[SUMMARY] Long Sentence Analysis Complete")
    print(f"  Files analyzed: {len(files_to_analyze)}")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print(f"  Total long sentences (>{args.threshold} words): {total_long_sentences}")
    print("=" * 70)
    print("\n[NOTE] Sentence splitting requires manual review.")
    print("[NOTE] Use the suggested split points as guidance.\n")

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    exit(main())
