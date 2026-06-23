#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/apply_ai_pattern_fixes.py
#==============================================================================
# Automated batch processing to fix AI-ish patterns in documentation
#==============================================================================
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


# Safe automated replacements (no context needed)
SAFE_REPLACEMENTS = {
    # Hedge words - simple replacements
    r'\bleverage\s+the\s+': 'use the ',
    r'\bleverage\s+': 'use ',
    r'\bLeverage\s+the\s+': 'Use the ',
    r'\bLeverage\s+': 'Use ',
    r'\butilize\s+the\s+': 'use the ',
    r'\butilize\s+': 'use ',
    r'\bUtilize\s+the\s+': 'Use the ',
    r'\bUtilize\s+': 'Use ',

    # Enthusiasm - context-free removals
    r'\bseamless\s+': '',
    r'\bSeamless\s+': '',
    r'\bstate-of-the-art\s+': '',
    r'\bState-of-the-art\s+': '',
    r'\bbest-in-class\s+': '',
    r'\bBest-in-class\s+': '',
    r'\bindustry-leading\s+': '',
    r'\bIndustry-leading\s+': '',
    r'\brevolutionary\s+': 'novel ',
    r'\bRevolutionary\s+': 'Novel ',
    r'\bcutting-edge\s+': '',
    r'\bCutting-edge\s+': '',

    # Transitions - redundant phrases
    r'\bAs\s+we\s+can\s+see,\s*': '',
    r'\bAs\s+we\s+can\s+see\s+': '',
    r"It's\s+worth\s+noting\s+that\s+": '',
    r'It\s+is\s+worth\s+noting\s+that\s+': '',
}

# Context-sensitive replacements (require review)
CONTEXT_SENSITIVE = {
    r'\bcomprehensive\s+': 'REVIEW_NEEDED',  # May be technical
    r'\bpowerful\s+': 'REVIEW_NEEDED',  # May refer to computing
    r'\badvanced\s+capabilities\b': 'capabilities',  # Can simplify
    r'\badvanced\s+': 'REVIEW_NEEDED',  # May distinguish variants
}


def apply_safe_fixes(content: str) -> Tuple[str, int]:
    """
    Apply safe automated fixes that don't require context.

    Args:
        content: File content

    Returns:
        Tuple of (fixed_content, num_replacements)
    """
    fixed = content
    total_replacements = 0

    for pattern, replacement in SAFE_REPLACEMENTS.items():
        matches = len(re.findall(pattern, fixed, re.IGNORECASE))
        if matches > 0:
            fixed = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
            total_replacements += matches

    return fixed, total_replacements


def process_file(file_path: Path, dry_run: bool = False) -> Dict:
    """
    Process a single file to fix AI-ish patterns.

    Args:
        file_path: Path to markdown file
        dry_run: If True, don't write changes

    Returns:
        Dictionary with processing results
    """
    try:
        original_content = file_path.read_text(encoding='utf-8')
        fixed_content, num_fixes = apply_safe_fixes(original_content)

        if not dry_run and num_fixes > 0:
            file_path.write_text(fixed_content, encoding='utf-8')

        return {
            "file": str(file_path),
            "success": True,
            "replacements": num_fixes,
            "dry_run": dry_run
        }

    except Exception as e:
        return {
            "file": str(file_path),
            "success": False,
            "error": str(e),
            "dry_run": dry_run
        }


def process_file_list(file_list: List[Path], dry_run: bool = False) -> Dict:
    """
    Process multiple files.

    Args:
        file_list: List of file paths
        dry_run: If True, don't write changes

    Returns:
        Summary dictionary
    """
    results = []
    total_files = len(file_list)
    total_fixes = 0
    successful = 0
    failed = 0

    print(f"Processing {total_files} files...")
    print(f"Dry run: {dry_run}\n")

    for i, file_path in enumerate(file_list, 1):
        result = process_file(file_path, dry_run)
        results.append(result)

        if result["success"]:
            successful += 1
            total_fixes += result.get("replacements", 0)
            if result.get("replacements", 0) > 0:
                print(f"[{i}/{total_files}] OK {file_path.name}: {result['replacements']} fixes")
        else:
            failed += 1
            print(f"[{i}/{total_files}] FAIL {file_path.name}: {result.get('error', 'Unknown error')}")

    summary = {
        "total_files": total_files,
        "successful": successful,
        "failed": failed,
        "total_fixes": total_fixes,
        "dry_run": dry_run,
        "results": results
    }

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Apply automated fixes to AI-ish patterns in documentation"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON audit report with files to process"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=30,
        help="Process top N files by issue count (default: 30)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write changes, just report what would be done"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("D:/Projects/main/.artifacts/docs_audit/batch_fix_results.json"),
        help="Output JSON results path"
    )

    args = parser.parse_args()

    # Load audit report
    json_data = json.loads(args.input.read_text(encoding='utf-8'))

    # Get files with issues, sorted by issue count
    files_with_issues = [f for f in json_data['files'] if f.get('total_issues', 0) > 0]
    sorted_files = sorted(files_with_issues, key=lambda x: x.get('total_issues', 0), reverse=True)

    # Take top N
    top_files = sorted_files[:args.top_n]
    file_paths = [Path(f['file']) for f in top_files if Path(f['file']).exists()]

    print(f"Found {len(file_paths)} files to process (top {args.top_n} by issue count)")
    print("="*80)

    # Process files
    summary = process_file_list(file_paths, dry_run=args.dry_run)

    # Save results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    # Print summary
    print("\n" + "="*80)
    print("BATCH PROCESSING SUMMARY")
    print("="*80)
    print(f"Total files processed: {summary['total_files']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Total fixes applied: {summary['total_fixes']}")
    print(f"Dry run: {summary['dry_run']}")
    print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
