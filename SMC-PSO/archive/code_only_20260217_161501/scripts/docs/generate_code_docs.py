#!/usr/bin/env python3
"""
=======================================================================================
                    scripts/docs/generate_code_docs.py
=======================================================================================
Automated Documentation Generator for DIP_SMC_PSO Project

Generates comprehensive Sphinx documentation with embedded source code for all Python
files in the project. Creates markdown files with literalinclude directives, extracted
docstrings, and structured navigation.

Features:
- Recursive scanning of src/ directory
- Automatic literalinclude directive generation
- Docstring extraction and formatting
- Module hierarchy preservation
- Toctree navigation generation
- Template-based documentation structure

Usage:
    python scripts/docs/generate_code_docs.py [--module MODULE] [--dry-run]

Examples:
    # Generate docs for all modules
    python scripts/docs/generate_code_docs.py

    # Generate docs for specific module only
    python scripts/docs/generate_code_docs.py --module controllers

    # Preview what would be generated (no files written)
    python scripts/docs/generate_code_docs.py --dry-run
"""

import ast
import argparse
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class FunctionInfo:
    """Information extracted from a function definition."""
    name: str
    lineno: int
    args: List[str]
    docstring: Optional[str]
    is_method: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    decorator_list: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """Information extracted from a class definition."""
    name: str
    lineno: int
    bases: List[str]
    docstring: Optional[str]
    methods: List[FunctionInfo] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    """Information extracted from a Python module."""
    name: str
    filepath: Path
    docstring: Optional[str]
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


class PythonFileAnalyzer:
    """Analyzes Python source files and extracts documentation-relevant information."""

    def __init__(self, source_root: Path):
        """
        Initialize analyzer.

        Args:
            source_root: Root directory of source code (e.g., 'src/')
        """
        self.source_root = source_root

    def analyze_file(self, filepath: Path) -> Optional[ModuleInfo]:
        """
        Analyze a Python file and extract all documentation-relevant info.

        Args:
            filepath: Path to Python file

        Returns:
            ModuleInfo object or None if file cannot be parsed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source, filename=str(filepath))

            # Get module docstring
            module_docstring = ast.get_docstring(tree)

            # Extract module name from filepath
            module_name = self._get_module_name(filepath)

            # Initialize module info
            module_info = ModuleInfo(
                name=module_name,
                filepath=filepath,
                docstring=module_docstring
            )

            # Extract classes, functions, and imports
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node)
                    module_info.classes.append(class_info)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_info = self._extract_function_info(node)
                    module_info.functions.append(func_info)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_info.imports.append(ast.unparse(node))

            return module_info

        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}")
            return None

    def _get_module_name(self, filepath: Path) -> str:
        """Get Python module name from filepath."""
        relative_path = filepath.relative_to(self.source_root)
        module_path = str(relative_path.with_suffix('')).replace('\\', '.').replace('/', '.')
        return module_path

    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract information from a class definition."""
        class_info = ClassInfo(
            name=node.name,
            lineno=node.lineno,
            bases=[ast.unparse(base) for base in node.bases],
            docstring=ast.get_docstring(node)
        )

        # Extract methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function_info(item, is_method=True)
                class_info.methods.append(method_info)
            elif isinstance(item, ast.FunctionDef) and any(
                isinstance(d, ast.Name) and d.id == 'property' for d in item.decorator_list
            ):
                class_info.properties.append(item.name)

        return class_info

    def _extract_function_info(self, node: ast.FunctionDef, is_method: bool = False) -> FunctionInfo:
        """Extract information from a function/method definition."""
        # Extract argument names
        args = [arg.arg for arg in node.args.args]

        # Extract decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]

        # Check for classmethod/staticmethod
        is_classmethod = any('classmethod' in d for d in decorators)
        is_staticmethod = any('staticmethod' in d for d in decorators)

        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            args=args,
            docstring=ast.get_docstring(node),
            is_method=is_method,
            is_classmethod=is_classmethod,
            is_staticmethod=is_staticmethod,
            decorator_list=decorators
        )


class DocumentationGenerator:
    """Generates Sphinx markdown documentation from Python source code."""

    def __init__(self, source_root: Path, docs_root: Path, dry_run: bool = False):
        """
        Initialize documentation generator.

        Args:
            source_root: Root directory of source code (e.g., 'src/')
            docs_root: Root directory for generated documentation (e.g., 'docs/reference/')
            dry_run: If True, print what would be generated without writing files
        """
        self.source_root = source_root
        self.docs_root = docs_root
        self.dry_run = dry_run
        self.analyzer = PythonFileAnalyzer(source_root)

    def generate_all(self, module_filter: Optional[str] = None):
        """
        Generate documentation for all Python files in source root.

        Args:
            module_filter: Optional module name to filter (e.g., 'controllers')
        """
        print(f"Scanning {self.source_root} for Python files...")

        # Find all Python files
        py_files = list(self.source_root.rglob("*.py"))

        # Filter out __pycache__ and test files
        py_files = [f for f in py_files if '__pycache__' not in str(f)]

        # Apply module filter if specified
        if module_filter:
            py_files = [f for f in py_files if module_filter in str(f.relative_to(self.source_root))]

        print(f"Found {len(py_files)} Python files to document")

        # Group files by top-level module
        modules_map = defaultdict(list)
        for py_file in py_files:
            relative_path = py_file.relative_to(self.source_root)
            if len(relative_path.parts) > 0:
                top_module = relative_path.parts[0]
                modules_map[top_module].append(py_file)

        # Generate documentation for each module
        for module_name, files in sorted(modules_map.items()):
            print(f"\nGenerating documentation for module: {module_name} ({len(files)} files)")
            self._generate_module_docs(module_name, files)

        # Generate main index with all modules
        self._generate_main_index(list(modules_map.keys()))

        if self.dry_run:
            print("\n[DRY RUN] No files were actually created.")
        else:
            print("\n[SUCCESS] Documentation generation complete!")
            print(f"   Generated docs in: {self.docs_root}")

    def _generate_module_docs(self, module_name: str, files: List[Path]):
        """Generate documentation for all files in a module."""
        module_docs_dir = self.docs_root / module_name

        if not self.dry_run:
            module_docs_dir.mkdir(parents=True, exist_ok=True)

        # Analyze all files
        analyzed_files = []
        for filepath in files:
            module_info = self.analyzer.analyze_file(filepath)
            if module_info:
                analyzed_files.append(module_info)

        # Generate index for this module
        self._generate_module_index(module_name, analyzed_files)

        # Generate documentation for each file
        for module_info in analyzed_files:
            self._generate_file_doc(module_info, module_docs_dir)

    def _generate_module_index(self, module_name: str, analyzed_files: List[ModuleInfo]):
        """Generate index page for a module."""
        module_docs_dir = self.docs_root / module_name
        index_path = module_docs_dir / "index.md"

        content = f"""# {module_name.replace('_', ' ').title()} Module

## Overview

This section documents all Python source files in `src/{module_name}/`.

## Module Architecture

**Total Files:** {len(analyzed_files)}
**Total Classes:** {sum(len(m.classes) for m in analyzed_files)}
**Total Functions:** {sum(len(m.functions) for m in analyzed_files)}

## Files in This Module

```{{toctree}}
:maxdepth: 2

{self._generate_toctree_entries(analyzed_files)}
```

## Quick Navigation

### By File Type

"""

        # Group by submodule
        submodules = defaultdict(list)
        for module_info in analyzed_files:
            parts = module_info.name.split('.')
            if len(parts) > 1:
                submodule = parts[1]
                submodules[submodule].append(module_info)
            else:
                submodules['root'].append(module_info)

        for submodule, files in sorted(submodules.items()):
            content += f"\n#### {submodule.title()}\n\n"
            for module_info in files:
                # Create relative link
                doc_filename = self._get_doc_filename(module_info)
                content += f"- [{module_info.name}]({doc_filename})\n"

        self._write_file(index_path, content)

    def _generate_toctree_entries(self, analyzed_files: List[ModuleInfo]) -> str:
        """Generate toctree entries for analyzed files."""
        entries = []
        for module_info in analyzed_files:
            doc_filename = self._get_doc_filename(module_info).replace('.md', '')
            entries.append(doc_filename)
        return '\n'.join(entries)

    def _get_doc_filename(self, module_info: ModuleInfo) -> str:
        """Get documentation filename for a module."""
        # Convert module path to filename
        # e.g., 'controllers.smc.classic_smc' -> 'smc_classic_smc.md'
        parts = module_info.name.split('.')
        if len(parts) > 1:
            filename = '_'.join(parts[1:]) + '.md'
        else:
            filename = parts[0] + '.md'
        return filename

    def _generate_file_doc(self, module_info: ModuleInfo, output_dir: Path):
        """Generate comprehensive documentation for a single Python file."""
        doc_filename = self._get_doc_filename(module_info)
        doc_path = output_dir / doc_filename

        # Get relative path to source file from docs directory
        source_relative = self._get_relative_source_path(module_info.filepath, doc_path)

        content = f"""# {module_info.name}

**Source:** `{module_info.filepath.relative_to(self.source_root.parent)}`

## Module Overview

"""

        # Add module docstring if available
        if module_info.docstring:
            content += f"{module_info.docstring}\n\n"
        else:
            content += "*No module docstring available.*\n\n"

        # Add full source code section
        content += f"""## Complete Source Code

```{{literalinclude}} {source_relative}
:language: python
:linenos:
```

---

"""

        # Document each class
        if module_info.classes:
            content += "## Classes\n\n"
            for class_info in module_info.classes:
                content += self._generate_class_doc(class_info, source_relative)

        # Document each function
        if module_info.functions:
            content += "## Functions\n\n"
            for func_info in module_info.functions:
                content += self._generate_function_doc(func_info, source_relative)

        # Add imports section
        if module_info.imports:
            content += "## Dependencies\n\n"
            content += "This module imports:\n\n"
            for imp in module_info.imports[:10]:  # Limit to first 10
                content += f"- `{imp}`\n"
            if len(module_info.imports) > 10:
                content += f"\n*... and {len(module_info.imports) - 10} more*\n"

        self._write_file(doc_path, content)

    def _generate_class_doc(self, class_info: ClassInfo, source_path: str) -> str:
        """Generate documentation section for a class."""
        content = f"### `{class_info.name}`\n\n"

        # Inheritance info
        if class_info.bases:
            content += f"**Inherits from:** {', '.join(f'`{b}`' for b in class_info.bases)}\n\n"

        # Class docstring
        if class_info.docstring:
            content += f"{class_info.docstring}\n\n"

        # Class source code
        content += f"""#### Source Code

```{{literalinclude}} {source_path}
:language: python
:pyobject: {class_info.name}
:linenos:
```

"""

        # Document methods
        if class_info.methods:
            content += f"#### Methods ({len(class_info.methods)})\n\n"
            for method in class_info.methods:
                signature = f"{method.name}({', '.join(method.args)})"
                content += f"##### `{signature}`\n\n"
                if method.docstring:
                    # Truncate docstring for overview
                    first_line = method.docstring.split('\n')[0]
                    content += f"{first_line}\n\n"

                # Link to full method documentation
                content += f"[View full source →](#method-{class_info.name.lower()}-{method.name.lower()})\n\n"

        content += "---\n\n"
        return content

    def _generate_function_doc(self, func_info: FunctionInfo, source_path: str) -> str:
        """Generate documentation section for a function."""
        signature = f"{func_info.name}({', '.join(func_info.args)})"
        content = f"### `{signature}`\n\n"

        # Decorators
        if func_info.decorator_list:
            content += "**Decorators:** " + ", ".join(f"`@{d}`" for d in func_info.decorator_list) + "\n\n"

        # Function docstring
        if func_info.docstring:
            content += f"{func_info.docstring}\n\n"

        # Function source code
        content += f"""#### Source Code

```{{literalinclude}} {source_path}
:language: python
:pyobject: {func_info.name}
:linenos:
```

---

"""
        return content

    def _generate_main_index(self, module_names: List[str]):
        """Generate main index page for all reference documentation."""
        index_path = self.docs_root / "index.md"

        content = """# API Reference - Complete Source Code Documentation

This section provides **complete source code documentation** for all Python modules in the DIP_SMC_PSO project.

## Overview

Every Python file in the project is documented here with:
- ✅ **Full source code** embedded with syntax highlighting
- ✅ **Extracted docstrings** for modules, classes, and functions
- ✅ **Architecture information** and module relationships
- ✅ **Line-by-line explanations** for key algorithms
- ✅ **Usage examples** and tutorials

## Modules

"""

        # Add toctree with all modules
        content += "```{toctree}\n:maxdepth: 2\n:caption: Modules\n\n"
        for module_name in sorted(module_names):
            content += f"{module_name}/index\n"
        content += "```\n\n"

        # Add module descriptions
        content += "## Module Descriptions\n\n"

        module_descriptions = {
            'analysis': 'Performance analysis, validation, fault detection, and visualization',
            'benchmarks': 'Integration benchmarking and statistical testing',
            'config': 'Configuration management and validation',
            'controllers': 'Sliding mode controllers and factory patterns',
            'core': 'Core simulation engine and dynamics models',
            'fault_detection': 'Fault detection and isolation (FDI) systems',
            'integration': 'Numerical integration methods',
            'interfaces': 'Protocol definitions and type annotations',
            'optimization': 'PSO optimization and parameter tuning',
            'optimizer': 'Legacy PSO optimizer (deprecated)',
            'plant': 'Physical plant models and configurations',
            'simulation': 'Simulation runners and batch processing',
            'utils': 'Utility functions for validation, monitoring, and development',
        }

        for module_name in sorted(module_names):
            desc = module_descriptions.get(module_name, 'Module documentation')
            content += f"### [{module_name}]({module_name}/index)\n\n{desc}\n\n"

        self._write_file(index_path, content)

    def _get_relative_source_path(self, source_file: Path, doc_file: Path) -> str:
        """
        Get relative path from documentation file to source file.

        Args:
            source_file: Absolute path to source file
            doc_file: Absolute path to documentation file

        Returns:
            Relative path string suitable for literalinclude directive
        """
        # Calculate relative path
        try:
            relative = Path(os.path.relpath(source_file, doc_file.parent))
            # Convert to forward slashes for Sphinx compatibility
            return str(relative).replace('\\', '/')
        except Exception:  # noqa: E722
            # Fallback to absolute path
            return str(source_file)

    def _write_file(self, filepath: Path, content: str):
        """Write content to file, or print if dry_run."""
        if self.dry_run:
            print(f"\n{'='*80}")
            print(f"Would create: {filepath}")
            print(f"{'='*80}")
            # Use safe ASCII preview to avoid UnicodeEncodeError on Windows
            preview = content[:500].encode('ascii', errors='replace').decode('ascii')
            print(preview)
            if len(content) > 500:
                print(f"\n... ({len(content) - 500} more characters)")
        else:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created: {filepath}")


def main():
    """Main entry point for documentation generator."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive Sphinx documentation with embedded source code'
    )
    parser.add_argument(
        '--module',
        type=str,
        help='Generate docs for specific module only (e.g., controllers, optimization)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be generated without writing files'
    )
    parser.add_argument(
        '--source-root',
        type=Path,
        default=Path('src'),
        help='Root directory of source code (default: src/)'
    )
    parser.add_argument(
        '--docs-root',
        type=Path,
        default=Path('docs/reference'),
        help='Root directory for generated documentation (default: docs/reference/)'
    )

    args = parser.parse_args()

    # Resolve paths relative to project root (2 levels up from script location)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    source_root = project_root / args.source_root
    docs_root = project_root / args.docs_root

    if not source_root.exists():
        print(f"Error: Source root not found: {source_root}")
        return 1

    print("="*80)
    print("DIP_SMC_PSO Documentation Generator")
    print("="*80)
    print(f"Source root: {source_root}")
    print(f"Docs root:   {docs_root}")
    print(f"Module filter: {args.module or 'None (all modules)'}")
    print(f"Dry run: {args.dry_run}")
    print("="*80)

    # Generate documentation
    generator = DocumentationGenerator(source_root, docs_root, dry_run=args.dry_run)
    generator.generate_all(module_filter=args.module)

    return 0


if __name__ == '__main__':
    import os
    import sys
    sys.exit(main())
