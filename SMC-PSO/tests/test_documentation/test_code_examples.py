#======================================================================================\\\
#============ tests/test_documentation/test_code_examples.py ==========================\\\
#======================================================================================\\\

"""Validation test suite for Python code examples in documentation.

This module automatically tests all code examples extracted from documentation
to ensure they remain valid and executable as the codebase evolves.

Usage:
    pytest tests/test_documentation/test_code_examples.py -v
    pytest tests/test_documentation/test_code_examples.py -v -k runnable
    pytest tests/test_documentation/test_code_examples.py -v -k conceptual
"""

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
import pytest


# Load extracted examples catalog
ARTIFACTS_DIR = Path('.test_artifacts/doc_examples')
CATALOG_FILE = ARTIFACTS_DIR / 'extracted_examples.json'


def load_examples() -> List[Dict[str, Any]]:
    """Load extracted code examples from catalog."""
    if not CATALOG_FILE.exists():
        pytest.skip(
            f"Examples catalog not found: {CATALOG_FILE}",
            allow_module_level=True
        )

    with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
        examples = json.load(f)

    return examples


# Load examples once at module level
ALL_EXAMPLES = load_examples()
RUNNABLE_EXAMPLES = [ex for ex in ALL_EXAMPLES if ex['is_runnable']]
CONCEPTUAL_EXAMPLES = [ex for ex in ALL_EXAMPLES if not ex['is_runnable']]


# =====================================================================================
# Syntax Validation Tests
# =====================================================================================

@pytest.mark.parametrize('example', ALL_EXAMPLES, ids=lambda ex: ex['id'])
def test_example_syntax_valid(example: Dict[str, Any]):
    """Test that all code examples have valid Python syntax.

    This test parses the code using Python's AST to ensure syntax validity.
    """
    code = example['code']
    example_id = example['id']
    source_file = example['file']

    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(
            f"Syntax error in example {example_id}\n"
            f"Source: {source_file}\n"
            f"Error: {e}"
        )


@pytest.mark.parametrize('example', ALL_EXAMPLES, ids=lambda ex: ex['id'])
def test_example_no_common_issues(example: Dict[str, Any]):
    """Test that examples don't contain common anti-patterns or issues."""
    code = example['code']
    example_id = example['id']

    # Check for common issues
    issues = []

    # Issue 1: Using print() without context (likely debugging code left in)
    if code.count('print(') > 3 and 'example-metadata' not in code:
        issues.append("Excessive print() statements (possible debug code)")

    # Issue 2: Hardcoded absolute paths
    if any(path in code for path in ['C:\\', 'D:\\', '/home/', '/Users/']):
        issues.append("Contains hardcoded absolute paths")

    # Issue 3: Missing imports for standard library
    tree = ast.parse(code)
    used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    common_missing = ['np', 'plt', 'pd'] & used_names

    has_imports = any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))
    if common_missing and not has_imports:
        issues.append(f"Likely missing imports for: {common_missing}")

    if issues:
        pytest.fail(
            f"Code quality issues in example {example_id}:\n" +
            "\n".join(f"  - {issue}" for issue in issues)
        )


# =====================================================================================
# Runnable Example Tests
# =====================================================================================

@pytest.mark.parametrize('example', RUNNABLE_EXAMPLES, ids=lambda ex: ex['id'])
def test_runnable_example_executes(example: Dict[str, Any]):
    """Test that runnable examples execute without errors.

    This test runs each runnable example in a subprocess with proper
    environment setup.
    """
    example_id = example['id']
    example_file = ARTIFACTS_DIR / f"{example_id}.py"
    metadata = example['metadata']
    timeout = metadata.get('timeout', 30)

    # Skip if example requires unavailable dependencies
    required_deps = metadata.get('requires', [])
    for dep in required_deps:
        try:
            __import__(dep)
        except ImportError:
            pytest.skip(f"Required dependency not available: {dep}")

    # Run example in subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(example_file)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd()
        )

        # Check exit code
        if result.returncode != 0:
            pytest.fail(
                f"Example {example_id} failed with exit code {result.returncode}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        # Check expected output if specified
        expected_output = metadata.get('expected_output')
        if expected_output and expected_output not in result.stdout:
            pytest.fail(
                f"Example {example_id} did not produce expected output\n"
                f"Expected: {expected_output}\n"
                f"Got: {result.stdout}"
            )

    except subprocess.TimeoutExpired:
        pytest.fail(f"Example {example_id} timed out after {timeout}s")


# =====================================================================================
# Import Validation Tests
# =====================================================================================

@pytest.mark.parametrize('example', ALL_EXAMPLES, ids=lambda ex: ex['id'])
def test_example_imports_valid(example: Dict[str, Any]):
    """Test that all imports in examples are valid or documented as conceptual."""
    code = example['code']
    example_id = example['id']

    try:
        tree = ast.parse(code)
    except SyntaxError:
        pytest.skip("Example has syntax errors (covered by other test)")
        return

    # Extract all imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # Skip if no imports
    if not imports:
        return

    # Check imports are either:
    # 1. Standard library
    # 2. Project modules (src.*)
    # 3. Known third-party deps
    known_deps = ['numpy', 'scipy', 'matplotlib', 'pytest', 'pandas', 'numba']

    invalid_imports = []
    for imp in imports:
        root_module = imp.split('.')[0]

        # Standard library check
        try:
            __import__(root_module)
            continue
        except ImportError:
            pass

        # Project module check
        if root_module == 'src':
            continue

        # Known dependency check
        if root_module in known_deps:
            continue

        # If runnable example, this is a real issue
        if example['is_runnable']:
            invalid_imports.append(imp)

    if invalid_imports:
        pytest.fail(
            f"Example {example_id} has invalid/unavailable imports:\n" +
            "\n".join(f"  - {imp}" for imp in invalid_imports)
        )


# =====================================================================================
# Statistical Summary Tests
# =====================================================================================

def test_examples_coverage_adequate():
    """Test that we have adequate code example coverage."""
    total = len(ALL_EXAMPLES)
    runnable = len(RUNNABLE_EXAMPLES)
    conceptual = len(CONCEPTUAL_EXAMPLES)

    # Assertions for documentation quality
    assert total > 100, f"Too few code examples: {total} (expected >100)"
    assert runnable / total >= 0.50, \
        f"Too few runnable examples: {runnable}/{total} = {runnable/total:.1%} (expected ≥50%)"

    print("\nCode Example Coverage:")
    print(f"  Total examples: {total}")
    print(f"  Runnable: {runnable} ({runnable/total:.1%})")
    print(f"  Conceptual: {conceptual} ({conceptual/total:.1%})")


def test_examples_distributed_across_docs():
    """Test that examples are distributed across documentation sections."""
    # Group by documentation section
    sections = {}
    for example in ALL_EXAMPLES:
        # Extract top-level directory
        parts = Path(example['file']).parts
        if len(parts) > 1 and parts[0] == 'docs':
            section = parts[1] if len(parts) > 1 else 'root'
        else:
            section = 'root'

        sections.setdefault(section, []).append(example)

    # Check key sections have examples
    required_sections = ['guides', 'api', 'controllers', 'optimization']
    missing = [sec for sec in required_sections if sec not in sections]

    assert not missing, \
        f"Missing code examples in key sections: {missing}"

    # Print distribution
    print("\nExample Distribution by Section:")
    for section, examples in sorted(sections.items(), key=lambda x: -len(x[1])):
        runnable_count = sum(1 for ex in examples if ex['is_runnable'])
        print(f"  {section}: {len(examples)} ({runnable_count} runnable)")


# =====================================================================================
# Example Metadata Tests
# =====================================================================================

def test_complex_examples_have_metadata():
    """Test that complex examples have metadata for proper validation."""
    # Complex = more than 50 lines or uses advanced features
    complex_examples = [
        ex for ex in RUNNABLE_EXAMPLES
        if ex['lines'] > 50
    ]

    examples_missing_metadata = []
    for example in complex_examples:
        metadata = example['metadata']

        # Check for metadata presence
        has_metadata = (
            metadata.get('runnable') is not None or
            metadata.get('requires') or
            metadata.get('timeout') != 30
        )

        if not has_metadata:
            examples_missing_metadata.append(example['id'])

    if examples_missing_metadata:
        print(
            f"\nWARNING: {len(examples_missing_metadata)} complex examples "
            f"missing metadata (recommended for better validation)"
        )


# =====================================================================================
# Main Test Suite Info
# =====================================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("Documentation Code Example Validation Suite")
    print("=" * 80)
    print(f"\nTotal Examples: {len(ALL_EXAMPLES)}")
    print(f"Runnable: {len(RUNNABLE_EXAMPLES)}")
    print(f"Conceptual: {len(CONCEPTUAL_EXAMPLES)}")
    print("\nRun with: pytest tests/test_documentation/test_code_examples.py -v")
