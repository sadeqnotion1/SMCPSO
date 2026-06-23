#!/usr/bin/env python3
"""
Quick Coverage Runner Script

Fixes Windows Unicode issues by using HTML/JSON reports only.

Usage:
    python run_coverage.py               # Run tests + generate reports
    python run_coverage.py --quick       # Use existing coverage data
    python run_coverage.py --check       # Check coverage gates (CI mode)
"""

import subprocess
import sys
from pathlib import Path

def main():
    quick = "--quick" in sys.argv
    check_gates = "--check" in sys.argv

    print("[AI] Coverage Measurement Fix - Windows Unicode Compatible")
    print("=" * 70)

    if not quick:
        print("\n[1/3] Running tests with coverage (HTML + JSON only)...")
        cmd = [
            "pytest",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=json",
            "-q",  # Quiet mode to reduce output
            "--tb=short"  # Short traceback format
        ]

        print(f"Command: {' '.join(cmd)}\n")

        try:
            result = subprocess.run(cmd, cwd=Path("."), timeout=600)

            if result.returncode == 0:
                print("\n[OK] Tests passed")
            else:
                print(f"\n[WARNING] Some tests failed (exit code {result.returncode})")
                print("[INFO] Coverage data still generated")

        except subprocess.TimeoutExpired:
            print("[ERROR] Test execution timed out (10 minutes)")
            sys.exit(1)
        except FileNotFoundError:
            print("[ERROR] pytest not found. Install: pip install pytest pytest-cov")
            sys.exit(1)

    print("\n[2/3] Generating coverage analysis...")
    try:
        subprocess.run(
            ["python", "scripts/coverage/check_coverage.py"],
            cwd=Path("."),
            check=False
        )
    except FileNotFoundError:
        print("[WARNING] scripts/coverage/check_coverage.py not found")

    if check_gates:
        print("\n[3/3] Checking coverage gates (CI mode)...")
        try:
            result = subprocess.run(
                ["python", "scripts/coverage/check_coverage.py", "--ci"],
                cwd=Path("."),
            )
            sys.exit(result.returncode)
        except FileNotFoundError:
            print("[ERROR] scripts/coverage/check_coverage.py not found")
            sys.exit(1)
    else:
        print("\n[3/3] Coverage reports generated:")
        print(f"  HTML Report: .htmlcov/index.html")
        print(f"  JSON Report: coverage.json")
        print()
        print("[INFO] Open .htmlcov/index.html in browser to view detailed coverage")
        print()

if __name__ == "__main__":
    main()
