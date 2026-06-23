"""
Automated Unicode Emoji Replacer for Documentation Files
=========================================================

Replaces Unicode emojis with ASCII text equivalents per CLAUDE.md CRITICAL RULE.

Windows terminal (cp1252 encoding) cannot display Unicode properly, causing crashes.
This script ensures all documentation uses ASCII text markers instead.

Usage:
    python scripts/docs/emoji_replacer.py --file README.md
    python scripts/docs/emoji_replacer.py --file CLAUDE.md --backup
    python scripts/docs/emoji_replacer.py --all  # Fix all 4 main entry points

Author: Claude Code (Automated QA Script)
Date: November 2025
"""

import re
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


# Comprehensive emoji replacement map (from QA-02 baseline analysis)
EMOJI_MAP = {
    # Status/validation emojis (most common)
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '⚠': '[WARNING]',
    'ℹ️': '[INFO]',
    'ℹ': '[INFO]',

    # Common markers
    '🚀': '[LAUNCH]',
    '🎯': '[TARGET]',
    '🔧': '[CONFIG]',
    '📚': '[DOCS]',
    '📖': '[READ]',
    '🎮': '[DEMO]',
    '📐': '[MATH]',
    '🔬': '[RESEARCH]',
    '🧪': '[TEST]',
    '🤖': '[AI]',

    # Architecture/structure emojis
    '🔵': '[BLUE]',
    '🟡': '[YELLOW]',
    '🟢': '[GREEN]',
    '🔴': '[RED]',
    '⚪': '[WHITE]',
    '⚫': '[BLACK]',
    '🟣': '[PURPLE]',
    '🟠': '[ORANGE]',

    # Directional/flow emojis
    '→': '->',
    '←': '<-',
    '↑': '^',
    '↓': 'v',
    '↔': '<->',
    '⇒': '=>',
    '⇐': '<=',
    '⇔': '<=>',

    # Special symbols
    '✓': '[DONE]',
    '✗': '[FAIL]',
    '⏸️': '[PAUSE]',
    '⏸': '[PAUSE]',
    '⏹️': '[STOP]',
    '⏹': '[STOP]',
    '▶️': '[PLAY]',
    '▶': '[PLAY]',
    '⏭️': '[SKIP]',
    '⏭': '[SKIP]',

    # Additional common emojis
    '💡': '[IDEA]',
    '🔥': '[HOT]',
    '⭐': '[STAR]',
    '📊': '[CHART]',
    '📈': '[GROWTH]',
    '📉': '[DECLINE]',
    '🔒': '[LOCKED]',
    '🔓': '[UNLOCKED]',
    '🔑': '[KEY]',
    '🏆': '[TROPHY]',
    '🎉': '[PARTY]',
    '👍': '[THUMBS_UP]',
    '👎': '[THUMBS_DOWN]',

    # Additional emojis found in docs
    '📋': '[CLIPBOARD]',
    '📦': '[PACKAGE]',
    '🏗️': '[CONSTRUCTION]',
    '🏗': '[CONSTRUCTION]',
    '🔨': '[HAMMER]',
    '🗺️': '[MAP]',
    '🗺': '[MAP]',
    '📜': '[SCROLL]',
    '🐍': '[PYTHON]',
    '🎨': '[ART]',
    '🎛️': '[CONTROLS]',
    '🎛': '[CONTROLS]',
}


def replace_emojis_in_text(text: str) -> Tuple[str, int]:
    """
    Replace all Unicode emojis with ASCII equivalents.

    Args:
        text: Input text containing emojis

    Returns:
        Tuple of (processed_text, replacement_count)
    """
    processed = text
    total_replacements = 0

    # Replace each emoji with its ASCII equivalent
    for emoji, ascii_replacement in EMOJI_MAP.items():
        count = processed.count(emoji)
        if count > 0:
            processed = processed.replace(emoji, ascii_replacement)
            total_replacements += count

    return processed, total_replacements


def emoji_to_safe_repr(emoji: str) -> str:
    """
    Convert emoji to safe string representation for Windows terminal.

    Args:
        emoji: Unicode emoji character

    Returns:
        Safe string representation (e.g., "U+1F4CB")
    """
    codepoints = [f"U+{ord(c):04X}" for c in emoji]
    return "+".join(codepoints)


def find_remaining_emojis(text: str) -> List[str]:
    """
    Find any remaining Unicode emojis not in the replacement map.

    Uses regex to detect Unicode emoji ranges.

    Args:
        text: Text to search for emojis

    Returns:
        List of unique emojis found
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

    found = emoji_pattern.findall(text)
    return list(set(found))  # Unique emojis


def process_file(file_path: Path, create_backup: bool = True, dry_run: bool = False) -> Dict:
    """
    Process a single file to replace emojis.

    Args:
        file_path: Path to the file to process
        create_backup: Whether to create .bak backup
        dry_run: If True, don't modify file (just report)

    Returns:
        Dictionary with processing statistics
    """
    if not file_path.exists():
        return {
            'status': 'error',
            'message': f"File not found: {file_path}",
            'replacements': 0
        }

    # Read original content
    try:
        original_text = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to read file: {e}",
            'replacements': 0
        }

    # Replace emojis
    processed_text, replacement_count = replace_emojis_in_text(original_text)

    # Find any remaining emojis
    remaining = find_remaining_emojis(processed_text)

    # Report only (dry run)
    if dry_run:
        return {
            'status': 'dry_run',
            'file': str(file_path),
            'replacements': replacement_count,
            'remaining_emojis': remaining,
            'message': f"Would replace {replacement_count} emojis"
        }

    # No changes needed
    if replacement_count == 0 and not remaining:
        return {
            'status': 'unchanged',
            'file': str(file_path),
            'replacements': 0,
            'message': "No emojis found"
        }

    # Create backup if requested
    if create_backup and replacement_count > 0:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)

    # Write modified content
    try:
        file_path.write_text(processed_text, encoding='utf-8')
        return {
            'status': 'success',
            'file': str(file_path),
            'replacements': replacement_count,
            'remaining_emojis': remaining,
            'backup_created': create_backup and replacement_count > 0,
            'message': f"Replaced {replacement_count} emojis"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to write file: {e}",
            'replacements': replacement_count
        }


def main():
    parser = argparse.ArgumentParser(
        description='Replace Unicode emojis with ASCII text equivalents in documentation files'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Single file to process'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all 4 main entry points (README.md, CLAUDE.md, docs/index.md, guides/INDEX.md)'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create .bak backup files before modification'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Report what would be changed without modifying files'
    )

    args = parser.parse_args()

    # Determine files to process
    if args.all:
        files_to_process = [
            Path('README.md'),
            Path('CLAUDE.md'),
            Path('docs/index.md'),
            Path('docs/guides/INDEX.md')
        ]
    elif args.file:
        files_to_process = [args.file]
    else:
        parser.error("Must specify either --file or --all")

    # Process each file
    print(f"\n[INFO] Emoji Replacer - Processing {len(files_to_process)} file(s)")
    print(f"[INFO] Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"[INFO] Backup: {'Enabled' if args.backup else 'Disabled'}\n")

    results = []
    for file_path in files_to_process:
        print(f"Processing: {file_path}")
        result = process_file(file_path, create_backup=args.backup, dry_run=args.dry_run)
        results.append(result)

        # Report result
        if result['status'] == 'success':
            print(f"  [OK] {result['message']}")
            if result.get('backup_created'):
                print(f"  [INFO] Backup created: {file_path}.bak")
            if result.get('remaining_emojis'):
                safe_repr = [emoji_to_safe_repr(e) for e in result['remaining_emojis']]
                print(f"  [WARNING] {len(result['remaining_emojis'])} unknown emojis remain: {safe_repr}")
        elif result['status'] == 'unchanged':
            print(f"  [INFO] {result['message']}")
        elif result['status'] == 'dry_run':
            print(f"  [DRY_RUN] {result['message']}")
            if result.get('remaining_emojis'):
                safe_repr = [emoji_to_safe_repr(e) for e in result['remaining_emojis']]
                print(f"  [WARNING] {len(result['remaining_emojis'])} unknown emojis detected: {safe_repr}")
        elif result['status'] == 'error':
            print(f"  [ERROR] {result['message']}")

        print()

    # Summary
    total_replacements = sum(r.get('replacements', 0) for r in results)
    successful = sum(1 for r in results if r['status'] == 'success')
    errors = sum(1 for r in results if r['status'] == 'error')

    print("=" * 60)
    print(f"[SUMMARY] Emoji Replacer Complete")
    print(f"  Files processed: {len(files_to_process)}")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print(f"  Total replacements: {total_replacements}")
    print("=" * 60)

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    exit(main())
