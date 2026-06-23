#======================================================================================\\\
#============ scripts/documentation/tag_conceptual_examples.py ========================\\\
#======================================================================================\\\

"""Automatically tag conceptual code examples with metadata.

This script reads the extracted examples catalog, identifies conceptual examples,
and adds metadata tags to distinguish them from runnable examples.

Usage:
    python scripts/documentation/tag_conceptual_examples.py [--dry-run]

Metadata Format:
    # example-metadata:
    # runnable: false
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import argparse


def load_examples_catalog(catalog_path: Path) -> List[Dict[str, Any]]:
    """Load extracted examples catalog.

    Args:
        catalog_path: Path to extracted_examples.json

    Returns:
        List of example dictionaries
    """
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_code_block_position(content: str, code: str, index: int) -> Tuple[int, int]:
    """Find the exact position of a code block in markdown content.

    Args:
        content: Full markdown file content
        code: The code to find
        index: The 1-based index of the code block

    Returns:
        Tuple of (start_pos, end_pos) of the code block including backticks
    """
    # Find all Python code blocks
    pattern = r'```python\n(.*?)```'
    matches = list(re.finditer(pattern, content, re.DOTALL))

    if index > len(matches):
        raise ValueError(f"Code block index {index} not found (only {len(matches)} blocks)")

    # Get the match for this specific index (1-based)
    match = matches[index - 1]

    # Verify the code matches
    found_code = match.group(1).strip()
    if found_code != code.strip():
        # Try fuzzy match (in case of whitespace differences)
        if found_code.replace(' ', '').replace('\n', '') != code.strip().replace(' ', '').replace('\n', ''):
            raise ValueError(f"Code block content mismatch at index {index}")

    return match.start(), match.end()


def add_metadata_to_code_block(content: str, start_pos: int, end_pos: int) -> str:
    """Add metadata header to a code block.

    Args:
        content: Full markdown content
        start_pos: Start position of the code block
        end_pos: End position of the code block

    Returns:
        Updated content with metadata added
    """
    # Extract the code block
    before = content[:start_pos]
    code_block = content[start_pos:end_pos]
    after = content[end_pos:]

    # Check if metadata already exists
    if '# example-metadata:' in code_block:
        return content  # Already tagged

    # Parse the code block
    if not code_block.startswith('```python\n'):
        raise ValueError("Invalid code block format")

    # Add metadata at the start of the code
    metadata = "# example-metadata:\n# runnable: false\n\n"
    updated_block = code_block.replace('```python\n', f'```python\n{metadata}', 1)

    return before + updated_block + after


def tag_file(file_path: Path, examples: List[Dict[str, Any]], dry_run: bool = False) -> int:
    """Tag all conceptual examples in a file.

    Args:
        file_path: Path to markdown file
        examples: List of examples to tag in this file
        dry_run: If True, don't modify files

    Returns:
        Number of examples tagged
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        tagged_count = 0

        # Sort examples by index in reverse order to avoid position shifts
        sorted_examples = sorted(examples, key=lambda x: x['index'], reverse=True)

        for example in sorted_examples:
            try:
                start_pos, end_pos = find_code_block_position(
                    content, example['code'], example['index']
                )
                content = add_metadata_to_code_block(content, start_pos, end_pos)

                # Check if content actually changed
                if content != original_content:
                    tagged_count += 1
                    original_content = content

            except ValueError as e:
                print(f"  [!] Warning: Could not tag example {example['index']} in {file_path.name}: {e}")
                continue

        # Write updated content
        if tagged_count > 0 and not dry_run:
            file_path.write_text(content, encoding='utf-8')
            print(f"  [+] Tagged {tagged_count} examples in {file_path.name}")
        elif dry_run and tagged_count > 0:
            print(f"  [DRY-RUN] Would tag {tagged_count} examples in {file_path.name}")

        return tagged_count

    except Exception as e:
        print(f"  [!] Error processing {file_path}: {e}")
        return 0


def main():
    """Main tagging workflow."""
    parser = argparse.ArgumentParser(
        description='Tag conceptual code examples with metadata'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be tagged without modifying files'
    )
    args = parser.parse_args()

    print("=" * 80)
    print("Conceptual Example Tagging Script")
    print("=" * 80)

    if args.dry_run:
        print("\n[*] DRY-RUN MODE: No files will be modified\n")

    # Load examples catalog
    catalog_path = Path('.test_artifacts/doc_examples/extracted_examples.json')

    if not catalog_path.exists():
        print(f"[!] Error: Catalog not found at {catalog_path}")
        print("    Run extract_doc_examples.py first")
        return 1

    print(f"[*] Loading examples catalog from {catalog_path}")
    examples = load_examples_catalog(catalog_path)

    # Filter conceptual examples
    conceptual = [ex for ex in examples if not ex['is_runnable']]

    print(f"\n[*] Found {len(conceptual)} conceptual examples to tag")
    print(f"    (out of {len(examples)} total examples)")

    # Group by file
    files_to_tag: Dict[str, List[Dict[str, Any]]] = {}
    for example in conceptual:
        file_path = example['file']
        if file_path not in files_to_tag:
            files_to_tag[file_path] = []
        files_to_tag[file_path].append(example)

    print(f"\n[*] Tagging {len(files_to_tag)} files...")

    total_tagged = 0
    files_modified = 0

    for file_path_str, file_examples in files_to_tag.items():
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"  [!] Warning: File not found: {file_path}")
            continue

        tagged = tag_file(file_path, file_examples, dry_run=args.dry_run)
        if tagged > 0:
            total_tagged += tagged
            files_modified += 1

    print(f"\n[*] Tagging Summary:")
    print(f"  Files modified: {files_modified}")
    print(f"  Examples tagged: {total_tagged}")
    print(f"  Examples already tagged: {len(conceptual) - total_tagged}")

    if args.dry_run:
        print(f"\n[*] DRY-RUN complete. Run without --dry-run to apply changes.")
    else:
        print(f"\n[+] Tagging complete!")
        print(f"   Next step: Re-run extractor to verify")
        print(f"   Command: python scripts/documentation/extract_doc_examples.py")

    return 0


if __name__ == '__main__':
    exit(main())
