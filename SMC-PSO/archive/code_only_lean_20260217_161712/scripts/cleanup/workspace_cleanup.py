#!/usr/bin/env python3
"""
Workspace Cleanup Automation Script
====================================

Automated cleanup script for maintaining workspace organization standards.
Run this before every commit to ensure clean repository state.

Usage:
    python scripts/cleanup/workspace_cleanup.py [--dry-run] [--verbose]

Standards:
    - Root directory: ≤15 visible items
    - No __pycache__ directories
    - No .pyc/.pyo files
    - Cache directories removed
    - Logs properly organized
"""

import shutil
import argparse
from pathlib import Path
from typing import List, Tuple


class WorkspaceCleanup:
    """Automated workspace cleanup following project standards."""

    def __init__(self, root_dir: Path, dry_run: bool = False, verbose: bool = False):
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.verbose = verbose
        self.cleanup_stats = {
            "pycache_removed": 0,
            "pyc_removed": 0,
            "cache_dirs_removed": 0,
            "bytes_freed": 0,
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode enabled."""
        if self.verbose or level == "ERROR":
            prefix = "[DRY-RUN] " if self.dry_run else ""
            print(f"{prefix}[{level}] {message}")

    def get_dir_size(self, path: Path) -> int:
        """Calculate directory size in bytes."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except (PermissionError, OSError):
            pass
        return total

    def remove_pycache_dirs(self):
        """Remove all __pycache__ directories."""
        self.log("Removing __pycache__ directories...")
        for pycache in self.root_dir.rglob("__pycache__"):
            if pycache.is_dir():
                size = self.get_dir_size(pycache)
                self.log(f"  Removing {pycache} ({size / 1024:.1f} KB)")
                if not self.dry_run:
                    shutil.rmtree(pycache, ignore_errors=True)
                self.cleanup_stats["pycache_removed"] += 1
                self.cleanup_stats["bytes_freed"] += size

    def remove_pyc_files(self):
        """Remove all .pyc and .pyo files."""
        self.log("Removing .pyc/.pyo files...")
        patterns = ["*.pyc", "*.pyo"]
        for pattern in patterns:
            for pyc_file in self.root_dir.rglob(pattern):
                if pyc_file.is_file():
                    size = pyc_file.stat().st_size
                    self.log(f"  Removing {pyc_file}")
                    if not self.dry_run:
                        pyc_file.unlink()
                    self.cleanup_stats["pyc_removed"] += 1
                    self.cleanup_stats["bytes_freed"] += size

    def remove_cache_dirs(self):
        """Remove common cache directories."""
        cache_dirs = [
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            ".hypothesis",
            ".benchmarks",
            ".htmlcov",
            ".tox",
        ]
        self.log("Removing cache directories...")
        for cache_name in cache_dirs:
            cache_path = self.root_dir / cache_name
            if cache_path.exists():
                size = self.get_dir_size(cache_path)
                self.log(f"  Removing {cache_path} ({size / 1024 / 1024:.1f} MB)")
                if not self.dry_run:
                    shutil.rmtree(cache_path, ignore_errors=True)
                self.cleanup_stats["cache_dirs_removed"] += 1
                self.cleanup_stats["bytes_freed"] += size

    def remove_os_specific_files(self):
        """Remove OS-specific cache files."""
        self.log("Removing OS-specific files...")
        patterns = ["desktop.ini", "Thumbs.db", ".DS_Store"]
        for pattern in patterns:
            for os_file in self.root_dir.rglob(pattern):
                if os_file.is_file():
                    self.log(f"  Removing {os_file}")
                    if not self.dry_run:
                        os_file.unlink()

    def check_root_directory(self) -> Tuple[int, List[str]]:
        """Check root directory item count."""
        root_items = [item for item in self.root_dir.iterdir()
                     if not item.name.startswith('.')]
        return len(root_items), [item.name for item in root_items]

    def print_summary(self):
        """Print cleanup summary."""
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)
        print(f"__pycache__ directories removed: {self.cleanup_stats['pycache_removed']}")
        print(f".pyc/.pyo files removed:          {self.cleanup_stats['pyc_removed']}")
        print(f"Cache directories removed:        {self.cleanup_stats['cache_dirs_removed']}")
        print(f"Total space freed:                {self.cleanup_stats['bytes_freed'] / 1024 / 1024:.2f} MB")

        # Check root directory compliance
        count, items = self.check_root_directory()
        status = "PASS" if count <= 15 else "FAIL"
        print(f"\nRoot directory items:             {count}/15 [{status}]")
        if count > 15:
            print("  Visible items:")
            for item in sorted(items):
                print(f"    - {item}")
        print("=" * 60)

    def run(self):
        """Execute all cleanup operations."""
        self.log("Starting workspace cleanup...", "INFO")

        self.remove_pycache_dirs()
        self.remove_pyc_files()
        self.remove_cache_dirs()
        self.remove_os_specific_files()

        self.print_summary()

        if self.dry_run:
            print("\n[DRY-RUN] No changes were made. Run without --dry-run to apply.")


def main():
    parser = argparse.ArgumentParser(
        description="Automated workspace cleanup following project standards"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Project root directory (default: auto-detect)"
    )

    args = parser.parse_args()

    cleanup = WorkspaceCleanup(
        root_dir=args.root,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    cleanup.run()


if __name__ == "__main__":
    main()
