#======================================================================================\\\
#============== scripts/documentation/extract_doc_examples.py =========================\\\
#======================================================================================\\\

"""Extract and catalog Python code examples from documentation files.

This script scans all markdown files in the docs/ directory, extracts Python
code blocks, categorizes them, and generates a structured catalog for validation.

Usage:
    python scripts/documentation/extract_doc_examples.py

Output:
    - .test_artifacts/doc_examples/extracted_examples.json
    - Individual .py files for each example
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
import hashlib


def extract_examples_from_file(md_file: Path) -> List[Dict[str, Any]]:
    """Extract all Python code blocks from a markdown file.

    Args:
        md_file: Path to markdown file

    Returns:
        List of example dictionaries with metadata
    """
    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[!] Error reading {md_file}: {e}")
        return []

    examples = []

    # Pattern to match ```python code blocks
    pattern = r'```python\n(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)

    for idx, match in enumerate(matches, 1):
        code = match.group(1).strip()

        # Skip empty or very short snippets
        if len(code) < 10:
            continue

        # Generate unique ID
        code_hash = hashlib.md5(code.encode()).hexdigest()[:8]
        example_id = f"{md_file.stem}_{idx}_{code_hash}"

        # Check if example has metadata comments
        metadata = extract_metadata(code)

        # Determine if example is runnable
        # Metadata takes precedence over heuristics
        if metadata['runnable'] is not None:
            is_runnable = metadata['runnable']
        else:
            is_runnable = is_example_runnable(code)

        try:
            relative_path = str(md_file.relative_to(Path.cwd()))
        except ValueError:
            # If file is not relative to cwd, use absolute path
            relative_path = str(md_file)

        examples.append({
            'id': example_id,
            'file': relative_path,
            'index': idx,
            'code': code,
            'lines': len(code.splitlines()),
            'is_runnable': is_runnable,
            'metadata': metadata,
            'hash': code_hash
        })

    return examples


def extract_metadata(code: str) -> Dict[str, Any]:
    """Extract metadata from code comments.

    Looks for YAML-style comments at the top of the code block:
    # example-metadata:
    # runnable: true
    # requires: [numpy, scipy]
    """
    metadata = {
        'runnable': None,
        'requires': [],
        'timeout': 30,
        'expected_output': None
    }

    lines = code.splitlines()
    in_metadata = False

    for line in lines:
        stripped = line.strip()
        if stripped == '# example-metadata:':
            in_metadata = True
            continue

        if not in_metadata:
            break

        if not stripped.startswith('#'):
            break

        # Parse metadata line
        if ':' in stripped:
            key_value = stripped[1:].strip()  # Remove leading #
            if ':' in key_value:
                key, value = key_value.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key == 'runnable':
                    metadata['runnable'] = value.lower() == 'true'
                elif key == 'requires':
                    # Parse list: [numpy, scipy]
                    value = value.strip('[]')
                    metadata['requires'] = [v.strip() for v in value.split(',')]
                elif key == 'timeout':
                    metadata['timeout'] = int(value.rstrip('s'))
                elif key == 'expected_output':
                    metadata['expected_output'] = value.strip('"\'')

    return metadata


def is_example_runnable(code: str) -> bool:
    """Heuristically determine if a code example is runnable.

    Runnable examples:
    - Have imports
    - Have executable statements (not just definitions)
    - Don't have placeholder comments like # ... or # TODO

    Non-runnable examples:
    - Class/function definitions only
    - Conceptual snippets
    - Incomplete code with placeholders
    """
    lines = [l.strip() for l in code.splitlines() if l.strip()]

    # Check for placeholders
    placeholders = ['# ...', '# TODO', '# FIXME', 'pass  # implementation', '...']
    for placeholder in placeholders:
        if any(placeholder in line for line in lines):
            return False

    # Check for imports (good sign of runnable code)
    has_import = any(line.startswith('import ') or line.startswith('from ') for line in lines)

    # Check for executable statements (not just definitions)
    has_execution = any(
        not line.startswith(('def ', 'class ', '#', 'import ', 'from '))
        for line in lines
    )

    # Runnable if it has imports AND execution, or just execution for simple examples
    return (has_import and has_execution) or (not has_import and has_execution and len(lines) < 10)


def save_examples(examples: List[Dict[str, Any]], output_dir: Path):
    """Save extracted examples to JSON and individual .py files.

    Args:
        examples: List of example dictionaries
        output_dir: Directory to save examples
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON catalog
    catalog_file = output_dir / 'extracted_examples.json'
    with open(catalog_file, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2)

    print(f"[+] Saved catalog: {catalog_file}")

    # Save individual .py files
    for example in examples:
        example_file = output_dir / f"{example['id']}.py"
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write(f"# Example from: {example['file']}\n")
            f.write(f"# Index: {example['index']}\n")
            f.write(f"# Runnable: {example['is_runnable']}\n")
            f.write(f"# Hash: {example['hash']}\n\n")
            f.write(example['code'])

    print(f"[+] Saved {len(examples)} example files to: {output_dir}")


def main():
    """Main extraction workflow."""
    print("=" * 80)
    print("Documentation Code Example Extractor")
    print("=" * 80)

    # Find all markdown files with Python examples
    docs_dir = Path('docs')
    md_files = list(docs_dir.rglob('*.md'))

    print(f"\n[*] Scanning {len(md_files)} markdown files...")

    all_examples = []
    files_with_examples = 0

    for md_file in md_files:
        examples = extract_examples_from_file(md_file)
        if examples:
            all_examples.extend(examples)
            files_with_examples += 1
            print(f"  [+] {md_file.relative_to(docs_dir)}: {len(examples)} examples")

    print(f"\n[*] Extraction Summary:")
    print(f"  Files scanned: {len(md_files)}")
    print(f"  Files with examples: {files_with_examples}")
    print(f"  Total examples extracted: {len(all_examples)}")

    if all_examples:
        runnable = sum(1 for ex in all_examples if ex['is_runnable'])
        conceptual = len(all_examples) - runnable

        print(f"\n[*] Example Categorization:")
        print(f"  Runnable examples: {runnable} ({runnable/len(all_examples)*100:.1f}%)")
        print(f"  Conceptual examples: {conceptual} ({conceptual/len(all_examples)*100:.1f}%)")

        # Save results
        output_dir = Path('.test_artifacts/doc_examples')
        save_examples(all_examples, output_dir)

        print(f"\n[+] Extraction complete!")
        print(f"   Next step: Run validation test suite")
        print(f"   Command: pytest tests/test_documentation/test_code_examples.py -v")
    else:
        print("\n[!] No Python code examples found in documentation.")


if __name__ == '__main__':
    main()
