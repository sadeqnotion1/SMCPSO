#!/usr/bin/env python
"""
Update hardcoded benchmark paths after reorganization.

Updates:
1. Python imports: from benchmarks.X -> from src.benchmarks.X
2. Data file paths: benchmarks/X.csv -> benchmarks/raw/MT-Y/X.csv
3. Documentation references (optional)
"""

import re
from pathlib import Path
from typing import Dict, List

# Import mappings (old -> new)
IMPORT_MAPPINGS = {
    'from src.benchmarks.analysis import': 'from src.benchmarks.analysis import',
    'from src.benchmarks.benchmark import': 'from src.benchmarks.benchmark import',
    'from src.benchmarks.comparison import': 'from src.benchmarks.comparison import',
    'from src.benchmarks.integration import': 'from src.benchmarks.integration import',
    'from src.benchmarks.examples import': 'from src.benchmarks.examples import',
}

# Path mappings for data files (old -> new)
PATH_MAPPINGS = {
    'benchmarks/raw/MT-5_comprehensive/comprehensive_benchmark.csv': 'benchmarks/raw/MT-5_comprehensive/comprehensive_benchmark.csv',
    'benchmarks/raw/MT-5_comprehensive/comprehensive_benchmark.json': 'benchmarks/raw/MT-5_comprehensive/comprehensive_benchmark.json',
    'benchmarks/raw/baselines/baseline_performance.csv': 'benchmarks/raw/baselines/baseline_performance.csv',
    'benchmarks/raw/baselines/baseline_integration.csv': 'benchmarks/raw/baselines/baseline_integration.csv',
    'benchmarks/raw/baselines/baseline_integration_template.csv': 'benchmarks/raw/baselines/baseline_integration_template.csv',
    # Reports
    'benchmarks/reports/LT4_COMPLETION_SUMMARY.md': 'benchmarks/reports/LT4_COMPLETION_SUMMARY.md',
    'benchmarks/reports/MT5_ANALYSIS_SUMMARY.md': 'benchmarks/reports/MT5_ANALYSIS_SUMMARY.md',
    # Logs
    '.logs/benchmarks/mt8_disturbance_rejection.log': '.logs/benchmarks/mt8_disturbance_rejection.log',
    '.logs/benchmarks/mt7_robustness.log': '.logs/benchmarks/mt7_robustness.log',
}


def update_imports(file_path: Path) -> int:
    """Update module imports in Python files."""
    try:
        content = file_path.read_text(encoding='utf-8')
        updated = content
        changes = 0

        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in updated:
                updated = updated.replace(old_import, new_import)
                changes += 1

        if updated != content:
            file_path.write_text(updated, encoding='utf-8')
            return changes
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to update imports in {file_path}: {e}")
        return 0


def update_file_paths(file_path: Path) -> int:
    """Update data file paths in Python scripts."""
    try:
        content = file_path.read_text(encoding='utf-8')
        updated = content
        changes = 0

        for old_path, new_path in PATH_MAPPINGS.items():
            # Match both single and double quotes
            if f'"{old_path}"' in updated or f"'{old_path}'" in updated:
                updated = updated.replace(f'"{old_path}"', f'"{new_path}"')
                updated = updated.replace(f"'{old_path}'", f"'{new_path}'")
                changes += 1

        if updated != content:
            file_path.write_text(updated, encoding='utf-8')
            return changes
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to update paths in {file_path}: {e}")
        return 0


def process_directory(directory: Path, pattern: str = "*.py") -> Dict[str, int]:
    """Process all files matching pattern in directory tree."""
    stats = {"files_scanned": 0, "imports_updated": 0, "paths_updated": 0, "files_modified": 0}

    for file_path in directory.rglob(pattern):
        if '__pycache__' in str(file_path) or '.git' in str(file_path):
            continue

        stats["files_scanned"] += 1

        import_changes = update_imports(file_path)
        path_changes = update_file_paths(file_path)

        if import_changes > 0:
            stats["imports_updated"] += import_changes
            stats["files_modified"] += 1
            print(f"[OK] Updated {import_changes} import(s) in {file_path}")

        if path_changes > 0:
            stats["paths_updated"] += path_changes
            if import_changes == 0:  # Don't double-count
                stats["files_modified"] += 1
            print(f"[OK] Updated {path_changes} path(s) in {file_path}")

    return stats


def main():
    root = Path(__file__).parent.parent.parent  # Go to repository root
    print(f"[INFO] Repository root: {root}")
    print(f"[INFO] Starting benchmark path migration...")
    print()

    # Update Python files in key directories
    directories_to_update = [
        root / "scripts",
        root / "tests",
        root / "src" / "benchmarks",  # Update examples that may reference old paths
    ]

    total_stats = {"files_scanned": 0, "imports_updated": 0, "paths_updated": 0, "files_modified": 0}

    for directory in directories_to_update:
        if not directory.exists():
            print(f"[WARNING] Directory not found: {directory}")
            continue

        print(f"[INFO] Processing {directory}...")
        stats = process_directory(directory)

        for key in total_stats:
            total_stats[key] += stats[key]

        print(f"       Scanned: {stats['files_scanned']}, Modified: {stats['files_modified']}")
        print()

    print("[INFO] Migration complete!")
    print(f"[SUMMARY] Files scanned: {total_stats['files_scanned']}")
    print(f"[SUMMARY] Files modified: {total_stats['files_modified']}")
    print(f"[SUMMARY] Import statements updated: {total_stats['imports_updated']}")
    print(f"[SUMMARY] File paths updated: {total_stats['paths_updated']}")


if __name__ == '__main__':
    main()
