#!/usr/bin/env python
"""
======================================================================================
FILE: scripts/migration/migrate_structure.py
PROJECT: Double Inverted Pendulum - SMC & PSO
DESCRIPTION: Automated migration script for scripts/ reorganization
AUTHOR: Claude Code
DATE: 2025-12-19
======================================================================================
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

# ====================================================================================
# MIGRATION RULES: Define where each file/directory should move
# ====================================================================================

# Files to KEEP at root (frequently used entry points)
ROOT_FILES = [
    "run_tests.sh",
    "run_tests.bat",
    "rebuild-docs.cmd",
    "README.md"
]

# Directory consolidation rules (merge duplicate directories)
CONSOLIDATE_DIRS = {
    "documentation": "docs",      # Merge documentation/ into docs/
    "docs_organization": "docs"   # Merge docs_organization/ into docs/
}

# File categorization rules (where to move root files)
FILE_MOVES = {
    # Documentation scripts
    "build_docs.py": "docs/",
    "categorize_docs.py": "docs/",
    "check_docs.py": "docs/",
    "find_orphaned_docs.py": "docs/",
    "fix_horizontal_rules.py": "docs/",
    "validate_documentation.py": "docs/",

    # Testing scripts
    "test_baseline_chattering.py": "testing/",
    "test_session_continuity.py": "testing/",

    # Validation scripts
    "check_coverage_gates.py": "validation/",
    "validate_memory_optimization.py": "validation/",
    "validate_memory_pool.py": "validation/",

    # Infrastructure/utilities
    "diagnose_pytest_unicode.py": "infrastructure/",

    # Research scripts
    "lt6_model_uncertainty.py": "research/",

    # Optimization scripts
    "debug_pso_fitness.py": "optimization/",
    "monitor_pso_streamlit.py": "monitoring/"
}

# New directories to create
NEW_DIRS = [
    "testing",
    "infrastructure",
    "utils"
]

# ====================================================================================
# PATH UPDATES: Files with hardcoded paths that need updating
# ====================================================================================

PATH_UPDATES = {
    "scripts/research/monitor_pso_progress.py": {
        'benchmarks/research/phase4_2/pso_optimization.log': '.logs/benchmarks/research/phase4_2/pso_optimization.log'
    },
    "scripts/research/mt6_boundary_layer/mt6_adaptive_boundary_layer_pso.py": {
        "'benchmarks/mt6_adaptive_optimization.log'": "'.logs/benchmarks/mt6_adaptive_optimization.log'"
    },
    "scripts/research/mt8_disturbances/mt8_robust_pso.py": {
        "'benchmarks/mt8_robust_pso.log'": "'.logs/benchmarks/mt8_robust_pso.log'"
    }
}

# Import path updates (fix broken cross-script imports)
IMPORT_UPDATES = {
    "scripts/research/mt8_disturbances/mt8_validate_robust_gains.py": {
        'from scripts.mt8_disturbance_rejection import': 'from scripts.research.mt8_disturbances.mt8_disturbance_rejection import'
    }
}

# ====================================================================================
# MIGRATION FUNCTIONS
# ====================================================================================

def generate_move_commands() -> List[str]:
    """Generate git mv commands for file migration."""
    commands = []

    # 1. Consolidate duplicate directories FIRST
    print("[INFO] Generating directory consolidation commands...")
    for old_dir, new_dir in CONSOLIDATE_DIRS.items():
        old_path = f"scripts/{old_dir}"
        new_path = f"scripts/{new_dir}"
        if os.path.exists(old_path):
            # Move all files from old directory to new directory
            files = list(Path(old_path).rglob("*.py"))
            for file in files:
                rel_path = file.relative_to(old_path)
                target = Path(new_path) / rel_path
                commands.append(f"git mv {file} {target}")
            commands.append(f"# Remove empty directory: {old_dir}")
            commands.append(f"rmdir scripts/{old_dir}")

    # 2. Create new directories
    print("[INFO] Generating new directory creation commands...")
    for new_dir in NEW_DIRS:
        commands.append(f"mkdir -p scripts/{new_dir}")

    # 3. Move individual files from root to categorized subdirectories
    print("[INFO] Generating file move commands...")
    for file, target_dir in FILE_MOVES.items():
        source = f"scripts/{file}"
        target = f"scripts/{target_dir}{file}"
        if os.path.exists(source):
            commands.append(f"git mv {source} {target}")

    return commands

def update_file_paths():
    """Update hardcoded paths in files."""
    print("\n[INFO] Updating hardcoded paths in files...")

    for file_path, replacements in PATH_UPDATES.items():
        if os.path.exists(file_path):
            print(f"  Updating {file_path}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                modified = False
                for old, new in replacements.items():
                    if old in content:
                        content = content.replace(old, new)
                        modified = True
                        print(f"    [OK] Replaced: {old} -> {new}")

                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  [OK] Updated {file_path}")
            except Exception as e:
                print(f"  [ERROR] Failed to update {file_path}: {e}")
        else:
            print(f"  [WARNING] File not found: {file_path}")

def update_imports():
    """Update broken cross-script imports."""
    print("\n[INFO] Updating cross-script imports...")

    for file_path, replacements in IMPORT_UPDATES.items():
        if os.path.exists(file_path):
            print(f"  Updating {file_path}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                modified = False
                for old, new in replacements.items():
                    if old in content:
                        content = content.replace(old, new)
                        modified = True
                        print(f"    [OK] Replaced: {old} -> {new}")

                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  [OK] Updated {file_path}")
            except Exception as e:
                print(f"  [ERROR] Failed to update {file_path}: {e}")
        else:
            print(f"  [WARNING] File not found: {file_path}")

def create_subdirectory_readmes():
    """Create README.md files for each subdirectory."""
    print("\n[INFO] Creating subdirectory README files...")

    readme_templates = {
        "testing": """# Testing Scripts

Scripts for validating system behavior and test infrastructure.

## Files
- `test_baseline_chattering.py` - Baseline chattering tests
- `test_session_continuity.py` - Session continuity validation

See also: `tests/` directory for pytest test suites.
""",
        "infrastructure": """# Infrastructure Scripts

System-level utilities for environment setup and diagnostics.

## Files
- `diagnose_pytest_unicode.py` - Unicode encoding diagnostics for pytest

See also: `.project/tools/` for development tools.
""",
        "utils": """# Utility Scripts

Miscellaneous standalone utility scripts.

See also: `src/utils/` for reusable utility modules.
"""
    }

    for dir_name, readme_content in readme_templates.items():
        readme_path = f"scripts/{dir_name}/README.md"
        os.makedirs(os.path.dirname(readme_path), exist_ok=True)
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"  [OK] Created {readme_path}")

def save_move_commands(commands: List[str], output_file: str):
    """Save git mv commands to shell script."""
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write("#!/bin/bash\n")
        f.write("# Auto-generated migration commands for scripts reorganization\n")
        f.write("# Generated: 2025-12-19\n\n")
        f.write("set -e  # Exit on first error\n\n")
        for cmd in commands:
            f.write(cmd + "\n")
    print(f"\n[OK] Migration commands saved to {output_file}")

# ====================================================================================
# MAIN EXECUTION
# ====================================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("SCRIPTS REORGANIZATION MIGRATION")
    print("=" * 80)

    # Phase 1: Generate move commands
    print("\n[1/4] Generating git mv commands...")
    commands = generate_move_commands()
    save_move_commands(commands, "scripts/migration/move_commands.sh")
    print(f"  Generated {len(commands)} commands")

    # Phase 2: Update hardcoded paths (do BEFORE moving files)
    print("\n[2/4] Updating hardcoded paths in files...")
    update_file_paths()

    # Phase 3: Update imports (do BEFORE moving files)
    print("\n[3/4] Updating cross-script imports...")
    update_imports()

    # Phase 4: Create subdirectory READMEs
    print("\n[4/4] Creating subdirectory README files...")
    create_subdirectory_readmes()

    print("\n" + "=" * 80)
    print("[OK] Migration preparation complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review move_commands.sh for correctness")
    print("  2. Execute: bash scripts/migration/move_commands.sh")
    print("  3. Validate: git status && python -m pytest tests/ -x")
    print("=" * 80)
