#!/usr/bin/env python3
"""Find documentation files not included in any toctree.

This script analyzes Sphinx build warnings to identify orphaned documentation
files that exist but are not linked in the navigation structure.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

def parse_sphinx_log(log_file: Path) -> list[Path]:
    """Extract orphaned file paths from Sphinx build log."""
    orphaned = []

    if not log_file.exists():
        print(f"[ERROR] Log file not found: {log_file}")
        return orphaned

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Match pattern: "path/to/file.md: WARNING: document isn't included in any toctree"
            match = re.search(r'(.*\.md): WARNING: document isn\'t included in any toctree', line)
            if match:
                file_path = match.group(1)
                # Convert Windows backslashes to forward slashes
                file_path = file_path.replace('\\', '/')
                # Extract relative path from D:\Projects\main\docs\
                if 'docs/' in file_path:
                    rel_path = file_path.split('docs/')[-1]
                else:
                    rel_path = file_path
                orphaned.append(Path(rel_path))

    return orphaned

def categorize_orphaned_files(orphaned: list[Path]) -> dict[str, list[Path]]:
    """Categorize orphaned files by directory."""
    categories = defaultdict(list)

    for file_path in orphaned:
        # Get top-level directory
        parts = file_path.parts
        if len(parts) > 1:
            category = parts[0]
        else:
            category = 'root'
        categories[category].append(file_path)

    return dict(categories)

def main():
    # Paths
    repo_root = Path(__file__).parent.parent
    log_file = repo_root / 'docs' / 'sphinx_build.log'
    output_file = repo_root / '.claude' / 'mcp_debugging' / 'sphinx_reports' / 'orphaned_files.txt'

    print("[SEARCH] Analyzing Sphinx build log for orphaned documentation...")
    print(f"   Log file: {log_file}")

    # Parse log
    orphaned = parse_sphinx_log(log_file)

    if not orphaned:
        print("[OK] No orphaned files found!")
        return 0

    # Categorize
    categories = categorize_orphaned_files(orphaned)

    # Print summary
    print(f"\n[STATS] Found {len(orphaned)} orphaned documentation files\n")
    print("=" * 70)

    for category, files in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"\n{category}/ ({len(files)} files)")
        print("-" * 70)
        for file_path in sorted(files)[:10]:  # Show first 10
            print(f"  - {file_path}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")

    # Save detailed report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Orphaned Documentation Files Report\n")
        f.write(f"# Generated: {Path(__file__).name}\n")
        f.write(f"# Total: {len(orphaned)} files\n\n")

        for category, files in sorted(categories.items(), key=lambda x: -len(x[1])):
            f.write(f"\n## {category}/ ({len(files)} files)\n\n")
            for file_path in sorted(files):
                f.write(f"- {file_path}\n")

    print(f"\n[SAVE] Detailed report saved to: {output_file.relative_to(repo_root)}")
    print("\n" + "=" * 70)

    return 0

if __name__ == '__main__':
    sys.exit(main())
