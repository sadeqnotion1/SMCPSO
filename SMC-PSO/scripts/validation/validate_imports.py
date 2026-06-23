"""
Import Validation Script

Validates that all imports in the codebase point to existing modules.
Detects broken imports after reorganizations.

Usage:
    python scripts/validation/validate_imports.py
    python scripts/validation/validate_imports.py --fix  # Auto-fix common issues
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple, Set

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class ImportValidator:
    """Validate Python imports across the codebase."""

    def __init__(self, src_dir: str = 'src'):
        self.src_dir = Path(src_dir)
        self.errors: List[Tuple[str, str]] = []
        self.warnings: List[Tuple[str, str]] = []
        self.deprecated_imports: List[Tuple[str, str, str]] = []

    def find_imports(self, file_path: Path) -> List[str]:
        """Extract all imports from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            self.warnings.append((str(file_path), f"Cannot parse: {e}"))
            return []

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def module_exists(self, module_path: str) -> Tuple[bool, str]:
        """
        Check if a module exists.

        Returns:
            (exists, reason) tuple
        """
        if not module_path.startswith('src.'):
            return True, "external"  # External package, assume exists

        # Convert module path to file path
        relative_path = module_path.replace('src.', '').replace('.', '/')

        # Check for module file
        module_file = self.src_dir / f"{relative_path}.py"
        if module_file.exists():
            return True, "file"

        # Check for package directory
        package_dir = self.src_dir / relative_path / '__init__.py'
        if package_dir.exists():
            return True, "package"

        # Check if it's a submodule (e.g., src.controllers.smc.classical_smc)
        parts = relative_path.split('/')
        for i in range(len(parts)-1, 0, -1):
            check_path = self.src_dir / '/'.join(parts[:i]) / '__init__.py'
            if check_path.exists():
                return True, "submodule"

        return False, "not_found"

    def check_deprecated(self, module_path: str) -> Tuple[bool, str]:
        """Check if module is in deprecated directory."""
        if 'deprecated' in module_path:
            # Suggest canonical path
            canonical = module_path.replace('.deprecated.', '.')
            canonical = canonical.replace('deprecated.', '')
            return True, canonical

        # Check for known deprecated patterns
        deprecated_patterns = {
            'src.controllers.classical_smc': 'src.controllers.smc.classical_smc',
            'src.controllers.adaptive_smc': 'src.controllers.smc.adaptive_smc',
            'src.controllers.sta_smc': 'src.controllers.smc.sta_smc',
            'src.controllers.mpc_controller': 'src.controllers.mpc.mpc_controller',
            'src.controllers.swing_up_smc': 'src.controllers.specialized.swing_up_smc',
            'src.optimizer.pso_optimizer': 'src.optimization.algorithms.pso_optimizer',
            'src.core.simulation_runner': 'src.simulation.engines.simulation_runner',
            'src.core.simulation_context': 'src.simulation.context.simulation_context',
            'src.fault_detection.fdi': 'src.analysis.fault_detection.fdi',
        }

        if module_path in deprecated_patterns:
            return True, deprecated_patterns[module_path]

        return False, ""

    def validate_file(self, file_path: Path):
        """Validate all imports in a single file."""
        imports = self.find_imports(file_path)

        for imp in imports:
            exists, reason = self.module_exists(imp)

            if not exists:
                self.errors.append((str(file_path), f"Import '{imp}' not found"))

            is_deprecated, canonical = self.check_deprecated(imp)
            if is_deprecated and exists:
                self.deprecated_imports.append(
                    (str(file_path), imp, canonical)
                )

    def validate_all(self):
        """Validate all Python files in src/ and tests/."""
        print("[INFO] Validating imports in src/ and tests/...")

        # Validate src/
        for py_file in self.src_dir.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            self.validate_file(py_file)

        # Validate tests/
        tests_dir = Path('tests')
        if tests_dir.exists():
            for py_file in tests_dir.rglob("*.py"):
                if '__pycache__' in str(py_file):
                    continue
                self.validate_file(py_file)

        # Validate root scripts
        for py_file in Path('.').glob("*.py"):
            self.validate_file(py_file)

    def print_report(self):
        """Print validation report."""
        print("\n" + "="*70)
        print("IMPORT VALIDATION REPORT")
        print("="*70)

        if self.errors:
            print(f"\n[ERROR] Found {len(self.errors)} broken imports:\n")
            for file_path, error in self.errors[:20]:  # Show first 20
                print(f"  {file_path}")
                print(f"    -> {error}")
            if len(self.errors) > 20:
                print(f"\n  ... and {len(self.errors)-20} more errors")

        if self.deprecated_imports:
            print(f"\n[WARNING] Found {len(self.deprecated_imports)} deprecated imports:\n")
            for file_path, old_import, canonical in self.deprecated_imports[:10]:
                print(f"  {file_path}")
                print(f"    -> {old_import}")
                print(f"       Suggested: {canonical}")
            if len(self.deprecated_imports) > 10:
                print(f"\n  ... and {len(self.deprecated_imports)-10} more deprecated imports")

        if self.warnings:
            print(f"\n[WARNING] Found {len(self.warnings)} files that couldn't be parsed:\n")
            for file_path, warning in self.warnings[:10]:
                print(f"  {file_path}: {warning}")

        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Broken imports: {len(self.errors)}")
        print(f"Deprecated imports: {len(self.deprecated_imports)}")
        print(f"Parse warnings: {len(self.warnings)}")

        if self.errors:
            print("\n[ERROR] Validation FAILED - Fix broken imports before proceeding")
            return 1
        elif self.deprecated_imports:
            print("\n[WARNING] Validation passed with warnings - Update deprecated imports")
            print(f"Scheduled removal: January 16, 2026 (see src/deprecated/README.md)")
            return 0
        else:
            print("\n[OK] All imports valid!")
            return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Python imports across the codebase"
    )
    parser.add_argument(
        '--src-dir',
        default='src',
        help='Source directory to validate (default: src)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to auto-fix deprecated imports (not implemented yet)'
    )

    args = parser.parse_args()

    validator = ImportValidator(src_dir=args.src_dir)
    validator.validate_all()
    exit_code = validator.print_report()

    if args.fix and validator.deprecated_imports:
        print("\n[INFO] Auto-fix not implemented yet.")
        print("       Manual migration required (see src/deprecated/README.md)")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
