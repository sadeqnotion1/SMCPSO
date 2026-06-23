#!/usr/bin/env python3
"""Sync educational materials from .project/ai/edu/ to docs/learning/ for Sphinx build.

This script copies educational content to make it accessible to Sphinx documentation,
rewriting relative links to match the new location.

Usage:
    python scripts/sync_educational_content.py

Author: Claude Code AI Assistant
Last Updated: 2025-11-11
"""

from pathlib import Path
import shutil
import re
from datetime import datetime
from typing import Tuple

# Directory paths
SRC_DIR = Path('.project/ai/edu')
DEST_DIR = Path('docs/learning')

# Generation header template
HEADER_TEMPLATE = """<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: {source_path} -->
<!-- Generated: {timestamp} -->

"""


def rewrite_links(content: str, source_file: Path) -> Tuple[str, int]:
    """Rewrite relative links for new location in docs/learning/.

    Args:
        content: File content to process
        source_file: Original source file path (for context)

    Returns:
        Tuple of (modified_content, link_count)
    """
    original_content = content
    modifications = 0

    # Pattern 1: ../../docs/ -> ../ (most common in beginner-roadmap.md)
    pattern1 = r'\.\./\.\./docs/'
    replacement1 = '../'
    content, count1 = re.subn(pattern1, replacement1, content)
    modifications += count1

    # Pattern 2: ../../ (but NOT ../../docs/) -> stays as ../../
    # This handles links to root-level files like README.md
    # No changes needed for these

    # Pattern 3: Verify we don't have any remaining broken paths
    # Check for any remaining .project references (shouldn't exist, but safety check)
    pattern3 = r'\.\./\.\.\.project/'
    if re.search(pattern3, content):
        print(f"[WARNING] Found unexpected .project reference in {source_file}")

    return content, modifications


def sync_file(src: Path, dest: Path) -> int:
    """Copy file with link rewriting and header injection.

    Args:
        src: Source file path
        dest: Destination file path

    Returns:
        Number of links rewritten
    """
    # Read source content
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()

    # Rewrite links
    modified_content, link_count = rewrite_links(content, src)

    # Compute relative path from SRC_DIR for header
    relative_path = src.relative_to(SRC_DIR)

    # Generate header
    header = HEADER_TEMPLATE.format(
        source_path=f".project/ai/edu/{relative_path.as_posix()}",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Combine header + content
    final_content = header + modified_content

    # Ensure destination directory exists
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Write to destination
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(final_content)

    return link_count


def main():
    """Main sync workflow."""
    print(f"[INFO] Syncing educational content: {SRC_DIR} -> {DEST_DIR}")
    print(f"[INFO] Working directory: {Path.cwd()}")

    # Verify source directory exists
    if not SRC_DIR.exists():
        print(f"[ERROR] Source directory not found: {SRC_DIR}")
        return 1

    # Create destination directory (clean slate)
    if DEST_DIR.exists():
        print(f"[INFO] Removing existing {DEST_DIR}")
        shutil.rmtree(DEST_DIR)

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Created {DEST_DIR}")

    # Find all .md files in source
    md_files = list(SRC_DIR.rglob('*.md'))

    if not md_files:
        print(f"[ERROR] No markdown files found in {SRC_DIR}")
        return 1

    print(f"[INFO] Found {len(md_files)} markdown files to sync")

    # Sync each file
    total_links_rewritten = 0
    files_synced = 0

    for src_file in md_files:
        # Compute destination path (preserve directory structure)
        relative_path = src_file.relative_to(SRC_DIR)
        dest_file = DEST_DIR / relative_path

        # Sync file
        try:
            link_count = sync_file(src_file, dest_file)
            total_links_rewritten += link_count
            files_synced += 1

            status = f"[OK] {relative_path}"
            if link_count > 0:
                status += f" ({link_count} links rewritten)"
            print(status)

        except Exception as e:
            print(f"[ERROR] Failed to sync {relative_path}: {e}")
            return 1

    # Summary
    print()
    print(f"[OK] Sync complete:")
    print(f"     - Files synced: {files_synced}")
    print(f"     - Links rewritten: {total_links_rewritten}")
    print(f"     - Destination: {DEST_DIR}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
