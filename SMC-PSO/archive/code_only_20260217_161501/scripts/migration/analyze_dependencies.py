#!/usr/bin/env python
"""
======================================================================================
FILE: scripts/migration/analyze_dependencies.py
PROJECT: Double Inverted Pendulum - SMC & PSO
DESCRIPTION: Analyzes script dependencies before reorganization migration
AUTHOR: Claude Code
DATE: 2025-12-19
======================================================================================
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set

def scan_python_files(base_dir: str) -> List[Path]:
    """Recursively find all Python files in directory."""
    base_path = Path(base_dir)
    return list(base_path.rglob("*.py"))

def analyze_file_dependencies(file_path: Path) -> Dict:
    """Analyze a single file for dependency patterns."""
    findings = {
        "sys_path_appends": [],
        "relative_imports": [],
        "hardcoded_paths": [],
        "old_benchmarks_refs": [],
        "other_script_imports": []
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        findings["error"] = str(e)
        return findings

    # Pattern 1: sys.path.append patterns
    sys_path_pattern = r'sys\.path\.append\s*\(\s*["\']([^"\']+)["\']\s*\)'
    for i, line in enumerate(lines, 1):
        matches = re.findall(sys_path_pattern, line)
        for match in matches:
            findings["sys_path_appends"].append({
                "line": i,
                "path": match,
                "content": line.strip()
            })

    # Pattern 2: Relative imports (from .. import, from ... import)
    relative_import_pattern = r'from\s+(\.+[\w\.]*)\s+import'
    for i, line in enumerate(lines, 1):
        matches = re.findall(relative_import_pattern, line)
        for match in matches:
            if match.startswith('.'):
                findings["relative_imports"].append({
                    "line": i,
                    "import": match,
                    "content": line.strip()
                })

    # Pattern 3: Hardcoded relative paths in strings
    path_patterns = [
        r'["\'](\.\./[^"\']+)["\']',           # '../something'
        r'["\'](\.\./\.\./[^"\']+)["\']',      # '../../something'
        r'["\']([^"\']*\.\.[\\/][^"\']+)["\']' # Any path with ..
    ]
    for i, line in enumerate(lines, 1):
        for pattern in path_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if '..' in match:
                    findings["hardcoded_paths"].append({
                        "line": i,
                        "path": match,
                        "content": line.strip()
                    })

    # Pattern 4: Old benchmarks/ references (pre-Dec 18 reorganization)
    old_benchmarks_patterns = [
        r'benchmarks/analysis',
        r'benchmarks/benchmark',
        r'benchmarks/comparison',
        r'benchmarks/.*\.log'  # Log files should be in .logs/ now
    ]
    for i, line in enumerate(lines, 1):
        for pattern in old_benchmarks_patterns:
            if re.search(pattern, line):
                findings["old_benchmarks_refs"].append({
                    "line": i,
                    "pattern": pattern,
                    "content": line.strip()
                })

    # Pattern 5: Imports from other scripts (from scripts.* import)
    script_import_pattern = r'from\s+scripts\.([^\s]+)\s+import'
    for i, line in enumerate(lines, 1):
        matches = re.findall(script_import_pattern, line)
        for match in matches:
            findings["other_script_imports"].append({
                "line": i,
                "module": match,
                "content": line.strip()
            })

    return findings

def generate_dependency_report(base_dir: str, output_file: str):
    """Generate comprehensive dependency report."""
    print("[INFO] Scanning Python files...")
    python_files = scan_python_files(base_dir)
    print(f"[INFO] Found {len(python_files)} Python files")

    report = {
        "scan_date": "2025-12-19",
        "base_directory": base_dir,
        "total_files": len(python_files),
        "files_analyzed": {},
        "summary": {
            "files_with_sys_path": 0,
            "files_with_relative_imports": 0,
            "files_with_hardcoded_paths": 0,
            "files_with_old_benchmarks": 0,
            "files_with_script_imports": 0,
            "total_issues": 0
        }
    }

    for file_path in python_files:
        rel_path = file_path.relative_to(Path(base_dir).parent)
        print(f"[INFO] Analyzing {rel_path}...")

        findings = analyze_file_dependencies(file_path)

        # Count findings
        has_issues = any([
            findings["sys_path_appends"],
            findings["relative_imports"],
            findings["hardcoded_paths"],
            findings["old_benchmarks_refs"],
            findings["other_script_imports"]
        ])

        if has_issues:
            report["files_analyzed"][str(rel_path)] = findings

            if findings["sys_path_appends"]:
                report["summary"]["files_with_sys_path"] += 1
            if findings["relative_imports"]:
                report["summary"]["files_with_relative_imports"] += 1
            if findings["hardcoded_paths"]:
                report["summary"]["files_with_hardcoded_paths"] += 1
            if findings["old_benchmarks_refs"]:
                report["summary"]["files_with_old_benchmarks"] += 1
            if findings["other_script_imports"]:
                report["summary"]["files_with_script_imports"] += 1

            report["summary"]["total_issues"] += 1

    # Write report to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Dependency report saved to {output_file}")
    print(f"\n=== SUMMARY ===")
    print(f"Total files scanned: {report['total_files']}")
    print(f"Files with issues: {report['summary']['total_issues']}")
    print(f"  - sys.path.append: {report['summary']['files_with_sys_path']}")
    print(f"  - Relative imports: {report['summary']['files_with_relative_imports']}")
    print(f"  - Hardcoded paths: {report['summary']['files_with_hardcoded_paths']}")
    print(f"  - Old benchmarks refs: {report['summary']['files_with_old_benchmarks']}")
    print(f"  - Cross-script imports: {report['summary']['files_with_script_imports']}")

if __name__ == "__main__":
    base_dir = "scripts"
    output_file = "scripts/migration/dependency_report.json"

    generate_dependency_report(base_dir, output_file)
