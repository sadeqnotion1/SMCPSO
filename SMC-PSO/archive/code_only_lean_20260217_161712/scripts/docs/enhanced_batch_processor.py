#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/enhanced_batch_processor.py
#==============================================================================
# Enhanced Context-Aware Batch Processor for Documentation Cleanup
#
# Removes AI-ish language patterns while preserving technical accuracy.
#==============================================================================
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Context-aware replacement rules
REPLACEMENT_RULES = [
    # ========== COMPREHENSIVE PATTERNS ==========
    # Remove "comprehensive" when used as filler
    (r'\bcomprehensive\s+(documentation|framework|system|validation|testing|coverage|solution|approach|guide|analysis|review|assessment|report)\b',
     lambda m: m.group(1), re.IGNORECASE),

    # Keep "comprehensive" when backed by metrics (contains numbers or percentages)
    # This is handled by checking context in the replacement function

    # ========== EXCELLENT/AMAZING/INCREDIBLE PATTERNS ==========
    (r'\bExcellent\b', '', 0),  # Remove "Excellent" status markers
    (r'\bamazing\s+', '', re.IGNORECASE),
    (r'\bincredible\s+', '', re.IGNORECASE),
    (r'\bexciting\s+', '', re.IGNORECASE),

    # ========== MARKETING BUZZWORDS ==========
    (r'\bpowerful\s+', '', re.IGNORECASE),
    (r'\bseamless\s+', '', re.IGNORECASE),
    (r'\bcutting-edge\s+', '', re.IGNORECASE),
    (r'\bstate-of-the-art\s+', '', re.IGNORECASE),
    (r'\bbest-in-class\s+', '', re.IGNORECASE),
    (r'\bindustry-leading\s+', '', re.IGNORECASE),
    (r'\brevolutionary\s+', 'novel ', re.IGNORECASE),
    (r'\badvanced\s+capabilities\b', 'specific capabilities', re.IGNORECASE),
    (r'\bsuperior\s+performance\b', 'improved performance', re.IGNORECASE),

    # ========== HEDGE WORDS ==========
    (r'\bleverage\s+the\s+', 'use the ', re.IGNORECASE),
    (r'\bleverage\s+', 'use ', re.IGNORECASE),
    (r'\butilize\s+the\s+', 'use the ', re.IGNORECASE),
    (r'\butilize\s+', 'use ', re.IGNORECASE),
    (r'\bdelve\s+into\s+', 'examine ', re.IGNORECASE),
    (r'\bemploy\s+', 'use ', re.IGNORECASE),

    # ========== UNNECESSARY TRANSITIONS ==========
    (r'\bAs\s+we\s+can\s+see,\s*', '', re.IGNORECASE),
    (r'\bAs\s+we\s+can\s+see\s+', '', re.IGNORECASE),
    (r"\bIt's\s+worth\s+noting\s+that\s+", '', re.IGNORECASE),
    (r'\bIt\s+is\s+worth\s+noting\s+that\s+', '', re.IGNORECASE),
    (r'\bAdditionally,\s+it\s+should\s+be\s+mentioned\s+that\s+', 'Additionally, ', re.IGNORECASE),
    (r'\bFurthermore,\s+we\s+observe\s+that\s+', 'Furthermore, ', re.IGNORECASE),

    # ========== GREETING PATTERNS ==========
    (r"\bLet's\s+explore\s+", '', re.IGNORECASE),
    (r"\bLet\s+us\s+examine\s+", 'This section examines ', re.IGNORECASE),
    (r"\bWe\s+will\s+", 'This document covers ', re.IGNORECASE),
    (r"\bWelcome!\s*", '', 0),
    (r"\bIn\s+this\s+section\s+we\s+will\s+", 'This section covers ', re.IGNORECASE),

    # ========== CLEANUP ==========
    (r'\s{2,}', ' ', 0),  # Clean up multiple spaces
    (r'\n{3,}', '\n\n', 0),  # Clean up excessive newlines
]

# Technical terms to KEEP (whitelist)
TECHNICAL_WHITELIST = [
    r'\brobust\s+control\b',
    r'\brobustness\s+margin\b',
    r'\brobust\s+stability\b',
    r'\badvanced\s+MPC\b',
    r'\benable\s+(flag|option|logging|the|this)\b',
    r'\bcomprehensive\s+.*?(\d+%|\d+\.\d+)',  # Metric-backed comprehensive
]


def is_whitelisted(text: str, start: int, end: int) -> bool:
    """Check if match is in a whitelisted technical context."""
    context = text[max(0, start-50):min(len(text), end+50)]
    for pattern in TECHNICAL_WHITELIST:
        if re.search(pattern, context, re.IGNORECASE):
            return True
    return False


def smart_replace(text: str, pattern: str, replacement, flags=0) -> Tuple[str, int]:
    """
    Perform smart replacement with counter and whitelist checking.

    Args:
        text: Source text
        pattern: Regex pattern to match
        replacement: Replacement string or function
        flags: Regex flags

    Returns:
        Tuple of (modified_text, replacement_count)
    """
    if callable(replacement):
        result, count = [], 0
        last_end = 0
        for match in re.finditer(pattern, text, flags):
            # Check whitelist before replacing
            if is_whitelisted(text, match.start(), match.end()):
                result.append(text[last_end:match.end()])
                last_end = match.end()
                continue

            result.append(text[last_end:match.start()])
            replaced = replacement(match)
            if replaced != match.group(0):
                count += 1
            result.append(replaced)
            last_end = match.end()
        result.append(text[last_end:])
        return ''.join(result), count
    else:
        # Non-callable replacement
        result_text = text
        count = 0
        for match in re.finditer(pattern, text, flags):
            if not is_whitelisted(text, match.start(), match.end()):
                count += 1

        # Apply replacement only to non-whitelisted matches
        def replace_func(match):
            if is_whitelisted(text, match.start(), match.end()):
                return match.group(0)
            return replacement

        result_text = re.sub(pattern, replace_func, text, flags=flags)
        return result_text, count


def clean_file(file_path: Path, dry_run: bool = False) -> Dict:
    """
    Clean a single file of AI-ish patterns.

    Args:
        file_path: Path to markdown file
        dry_run: If True, don't write changes

    Returns:
        Dictionary with cleaning statistics
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        total_replacements = 0
        replacements_by_category = {}

        # Apply all replacement rules
        for rule in REPLACEMENT_RULES:
            if len(rule) == 2:
                pattern, replacement = rule
                flags = 0
            else:
                pattern, replacement, flags = rule

            content, count = smart_replace(content, pattern, replacement, flags)
            if count > 0:
                replacements_by_category[pattern[:50]] = count
                total_replacements += count

        # Write back if changed and not dry run
        if content != original_content and not dry_run:
            file_path.write_text(content, encoding='utf-8')
            status = 'cleaned'
        elif content != original_content:
            status = 'dry_run_changes_detected'
        else:
            status = 'no_changes'

        return {
            'file': str(file_path.relative_to(Path.cwd())),
            'status': status,
            'total_replacements': total_replacements,
            'replacements_by_category': replacements_by_category,
            'size_before': len(original_content),
            'size_after': len(content),
            'size_reduction': len(original_content) - len(content)
        }

    except Exception as e:
        return {
            'file': str(file_path),
            'status': 'error',
            'error': str(e),
            'total_replacements': 0,
            'size_reduction': 0,
            'replacements_by_category': {}
        }


def batch_clean(file_paths: List[Path], dry_run: bool = False) -> List[Dict]:
    """
    Batch clean multiple files.

    Args:
        file_paths: List of file paths to clean
        dry_run: If True, don't write changes

    Returns:
        List of cleaning results
    """
    results = []
    for i, file_path in enumerate(file_paths, 1):
        if not file_path.exists():
            results.append({
                'file': str(file_path),
                'status': 'not_found',
                'total_replacements': 0,
                'size_reduction': 0
            })
            print(f"[{i}/{len(file_paths)}] SKIP: {file_path.name} (not found)")
            continue

        result = clean_file(file_path, dry_run=dry_run)
        results.append(result)

        status_icon = "[OK]" if result['status'] == 'cleaned' else "[  ]"
        print(f"[{i}/{len(file_paths)}] {status_icon} {file_path.name}: "
              f"{result['total_replacements']} replacements "
              f"({result['size_reduction']} chars removed)")

    return results


def print_summary(results: List[Dict]):
    """Print summary statistics."""
    total_files = len(results)
    cleaned_files = len([r for r in results if r['status'] == 'cleaned'])
    total_replacements = sum(r.get('total_replacements', 0) for r in results)
    total_size_reduction = sum(r.get('size_reduction', 0) for r in results)

    print("\n" + "="*80)
    print("CLEANING SUMMARY")
    print("="*80)
    print(f"Total files processed: {total_files}")
    print(f"Files cleaned: {cleaned_files}")
    print(f"Files unchanged: {total_files - cleaned_files}")
    print(f"Total replacements: {total_replacements}")
    print(f"Total size reduction: {total_size_reduction:,} characters")
    print("="*80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced batch processor for documentation cleanup"
    )
    parser.add_argument(
        "--files",
        type=str,
        nargs="+",
        help="List of files to clean"
    )
    parser.add_argument(
        "--file-list",
        type=Path,
        help="JSON file containing list of files to clean"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing files"
    )

    args = parser.parse_args()

    # Get file list
    if args.file_list:
        file_list_data = json.loads(args.file_list.read_text(encoding='utf-8'))
        file_paths = [Path(f) for f in file_list_data]
    elif args.files:
        file_paths = [Path(f) for f in args.files]
    else:
        print("Error: Must provide either --files or --file-list")
        exit(1)

    print(f"Processing {len(file_paths)} files...")
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
    print("="*80)

    results = batch_clean(file_paths, dry_run=args.dry_run)
    print_summary(results)

    # Save results
    output_path = Path(".artifacts/docs_audit/enhanced_batch_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f"\nDetailed results saved to: {output_path}")
