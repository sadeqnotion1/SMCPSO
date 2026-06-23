"""
Code Block Language Tag Fixer
==============================

Adds language tags to markdown code blocks that are missing them.

Markdown code blocks should specify the language for:
- Syntax highlighting
- Accessibility (screen readers can announce code type)
- Documentation clarity

This script detects the language from code content and adds appropriate tags.

Usage:
    python scripts/docs/code_block_fixer.py --file CLAUDE.md --backup
    python scripts/docs/code_block_fixer.py --all --dry-run

Author: Claude Code (Automated QA Script)
Date: November 2025
"""

import re
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Optional


def detect_code_language(code: str) -> Optional[str]:
    """
    Detect programming language from code content.

    Args:
        code: Code block content

    Returns:
        Language name or None if cannot detect
    """
    code_lower = code.lower().strip()

    # Python indicators
    if any(keyword in code_lower for keyword in ['import ', 'def ', 'class ', 'print(', 'from ', 'pip install']):
        return 'python'

    # Bash/shell indicators
    if any(keyword in code_lower for keyword in ['#!/bin/bash', '#!/bin/sh', 'echo ', 'export ', 'cd ', 'ls ', 'git ', 'npm ', 'python ', 'pytest ']):
        return 'bash'

    # YAML indicators
    if re.search(r'^\s*\w+:\s*$', code, re.MULTILINE) and not code.startswith('{'):
        if any(keyword in code_lower for keyword in ['version:', 'name:', 'dependencies:', 'config:']):
            return 'yaml'

    # JSON indicators
    if code.strip().startswith('{') or code.strip().startswith('['):
        if any(char in code for char in ['":', '", ']):
            return 'json'

    # Markdown indicators
    if code.strip().startswith('#') and not code.strip().startswith('#!/'):
        if any(marker in code for marker in ['**', '*', '[', '](']):
            return 'markdown'

    # TOML indicators
    if re.search(r'^\[.+\]$', code, re.MULTILINE):
        return 'toml'

    # INI indicators
    if re.search(r'^\[.+\]$', code, re.MULTILINE) and '=' in code:
        return 'ini'

    # Plain text indicators (very generic output)
    if all(char in '0123456789-: .\n' for char in code):
        return 'text'

    # Default: bash (most common for command-line examples)
    return 'bash'


def fix_code_blocks(text: str, dry_run: bool = False) -> tuple[str, Dict]:
    """
    Fix code blocks missing language tags.

    Args:
        text: Input markdown text
        dry_run: If True, just report issues without fixing

    Returns:
        Tuple of (fixed_text, statistics)
    """
    lines = text.split('\n')
    fixed_lines = []
    stats = {
        'total_code_blocks': 0,
        'blocks_without_tags': 0,
        'blocks_fixed': 0,
        'languages_detected': {}
    }

    in_code_block = False
    code_block_start_idx = -1
    code_block_content = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block start
        if line.strip().startswith('```'):
            if not in_code_block:
                # Entering code block
                in_code_block = True
                code_block_start_idx = i
                code_block_content = []
                stats['total_code_blocks'] += 1

                # Check if language tag exists
                tag = line.strip()[3:].strip()
                if not tag:
                    stats['blocks_without_tags'] += 1

                fixed_lines.append(line)
            else:
                # Exiting code block
                in_code_block = False

                # Check if we need to fix the opening tag
                opening_line = lines[code_block_start_idx]
                tag = opening_line.strip()[3:].strip()

                if not tag and not dry_run:
                    # Detect language
                    code_content = '\n'.join(code_block_content)
                    detected_lang = detect_code_language(code_content)

                    if detected_lang:
                        # Fix the opening tag
                        fixed_lines[code_block_start_idx] = '```' + detected_lang
                        stats['blocks_fixed'] += 1
                        stats['languages_detected'][detected_lang] = stats['languages_detected'].get(detected_lang, 0) + 1

                fixed_lines.append(line)
                code_block_content = []
        else:
            if in_code_block:
                code_block_content.append(line)
            fixed_lines.append(line)

        i += 1

    return '\n'.join(fixed_lines), stats


def process_file(file_path: Path, create_backup: bool = True, dry_run: bool = False) -> Dict:
    """
    Process a single file to fix code blocks.

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
            'stats': {}
        }

    # Read original content
    try:
        original_text = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to read file: {e}",
            'stats': {}
        }

    # Fix code blocks
    fixed_text, stats = fix_code_blocks(original_text, dry_run=dry_run)

    # Report only (dry run)
    if dry_run:
        return {
            'status': 'dry_run',
            'file': str(file_path),
            'stats': stats,
            'message': f"Would fix {stats['blocks_without_tags']} of {stats['total_code_blocks']} code block(s)"
        }

    # No changes needed
    if stats['blocks_fixed'] == 0:
        return {
            'status': 'unchanged',
            'file': str(file_path),
            'stats': stats,
            'message': f"All {stats['total_code_blocks']} code blocks already have language tags"
        }

    # Create backup if requested
    if create_backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)

    # Write modified content
    try:
        file_path.write_text(fixed_text, encoding='utf-8')
        return {
            'status': 'success',
            'file': str(file_path),
            'stats': stats,
            'backup_created': create_backup,
            'message': f"Fixed {stats['blocks_fixed']} of {stats['total_code_blocks']} code block(s)"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to write file: {e}",
            'stats': stats
        }


def main():
    parser = argparse.ArgumentParser(
        description='Add language tags to markdown code blocks'
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
    print(f"\n[INFO] Code Block Fixer - Processing {len(files_to_process)} file(s)")
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
            stats = result['stats']
            if stats.get('languages_detected'):
                print(f"  [INFO] Languages detected:")
                for lang, count in stats['languages_detected'].items():
                    print(f"      - {lang}: {count} block(s)")
        elif result['status'] == 'unchanged':
            print(f"  [INFO] {result['message']}")
        elif result['status'] == 'dry_run':
            print(f"  [DRY_RUN] {result['message']}")
            stats = result['stats']
            print(f"  [INFO] Total code blocks: {stats['total_code_blocks']}")
            print(f"  [INFO] Blocks without tags: {stats['blocks_without_tags']}")
        elif result['status'] == 'error':
            print(f"  [ERROR] {result['message']}")

        print()

    # Summary
    total_blocks = sum(r.get('stats', {}).get('total_code_blocks', 0) for r in results)
    total_fixed = sum(r.get('stats', {}).get('blocks_fixed', 0) for r in results)
    successful = sum(1 for r in results if r['status'] == 'success')
    errors = sum(1 for r in results if r['status'] == 'error')

    print("=" * 60)
    print(f"[SUMMARY] Code Block Fixer Complete")
    print(f"  Files processed: {len(files_to_process)}")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print(f"  Total code blocks: {total_blocks}")
    print(f"  Blocks fixed: {total_fixed}")
    print("=" * 60)

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    exit(main())
