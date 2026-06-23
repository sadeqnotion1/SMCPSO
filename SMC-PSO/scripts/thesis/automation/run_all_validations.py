#!/usr/bin/env python3
"""
run_all_validations.py - Master Automation Runner

Orchestrates all 8 thesis validation scripts in sequence:
1. validate_references.py - Cross-reference validation (5 min manual)
2. validate_statistics.py - Statistical claims (30 min manual)
3. extract_claims.py - Technical claims extraction (1 hour manual)
4. check_notation.py - Notation consistency (15 min manual)
5. verify_equations.py - Equation verification (1-2 hours manual)
6. align_code_theory.py - Code-theory alignment (1 hour manual)
7. assess_completeness.py - Research questions (30 min manual)
8. screen_proofs.py - Lyapunov proof screening (4-6 hours expert)

Total Automation: 74% | Total Manual: 1.5-2 hours (excluding proofs)

Created: November 5, 2025

Usage:
    # Set API key for claims extraction & completeness
    export ANTHROPIC_API_KEY="sk-ant-..."

    # Run all validations
    python run_all_validations.py [--config config.yaml] [--quick] [--phase 1|2]

    # Quick mode: Phase 1 only (4 quick win scripts)
    python run_all_validations.py --quick

    # Phase 1: Quick wins (Scripts 1-4)
    python run_all_validations.py --phase 1

    # Phase 2: Advanced automation (Scripts 5-8)
    python run_all_validations.py --phase 2
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import yaml


class ValidationRunner:
    """Master orchestrator for all validation scripts."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize runner."""
        self.config_path = config_path
        self.scripts_dir = Path(__file__).parent
        self.start_time = None
        self.results = {}

    def run_script(self, script_name: str, description: str, priority: int) -> bool:
        """Run a single validation script."""
        print("\n" + "="*70)
        print(f"[{priority}/8] {description}")
        print(f"Script: {script_name}")
        print("="*70)

        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            print(f"[ERROR] Script not found: {script_path}")
            self.results[script_name] = "ERROR: Script not found"
            return False

        # Run script
        cmd = f"{sys.executable} {script_path} --config {self.config_path}"
        start = time.time()

        try:
            ret = os.system(cmd)
            elapsed = time.time() - start

            if ret == 0:
                print(f"\n[OK] {script_name} completed in {elapsed:.1f}s")
                self.results[script_name] = f"SUCCESS ({elapsed:.1f}s)"
                return True
            else:
                print(f"\n[ERROR] {script_name} failed with exit code {ret}")
                self.results[script_name] = f"FAILED (exit {ret})"
                return False

        except Exception as e:
            print(f"\n[ERROR] Exception running {script_name}: {e}")
            self.results[script_name] = f"ERROR: {e}"
            return False

    def run_phase_1(self):
        """Run Phase 1: Quick Wins (Scripts 1-4)."""
        print("\n" + "#"*70)
        print("# PHASE 1: QUICK WINS (30 min automated, 50 min manual review)")
        print("#"*70)

        scripts = [
            ("validate_references.py", "Cross-Reference Validation", 1),
            ("validate_statistics.py", "Statistical Claims Validation", 2),
            ("extract_claims.py", "Technical Claims Extraction", 3),
            ("check_notation.py", "Notation Consistency Check", 4),
        ]

        for script, desc, priority in scripts:
            self.run_script(script, desc, priority)

    def run_phase_2(self):
        """Run Phase 2: Advanced Automation (Scripts 5-8)."""
        print("\n" + "#"*70)
        print("# PHASE 2: ADVANCED AUTOMATION (2-3 hours automated, 6-9 hours manual)")
        print("#"*70)

        scripts = [
            ("verify_equations.py", "Symbolic Math Verification", 5),
            ("align_code_theory.py", "Code-Theory Alignment", 6),
            ("assess_completeness.py", "Completeness Assessment", 7),
            ("screen_proofs.py", "Lyapunov Proof Screening", 8),
        ]

        for script, desc, priority in scripts:
            self.run_script(script, desc, priority)

    def generate_summary(self):
        """Generate final validation summary."""
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {time.time() - self.start_time:.1f}s")
        print(f"\nResults:")

        for script, result in self.results.items():
            status = "[OK]" if "SUCCESS" in result else "[ERROR]"
            print(f"  {status} {script}: {result}")

        # Check for API key if needed
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("\n[WARNING] ANTHROPIC_API_KEY not set")
            print("         Claims extraction & completeness may have failed")
            print("         Set with: export ANTHROPIC_API_KEY='sk-ant-...'")

        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Review reports in: .artifacts/thesis/reports/")
        print("2. Manual work required:")
        print("   - validate_references.py: 5 min review")
        print("   - validate_statistics.py: 30 min review")
        print("   - extract_claims.py: 1 hour review (validate 30% of claims)")
        print("   - check_notation.py: 15 min review")
        print("   - verify_equations.py: 1-2 hours review")
        print("   - align_code_theory.py: 1 hour spot-check")
        print("   - assess_completeness.py: 30 min review")
        print("   - screen_proofs.py: 4-6 hours EXPERT review")
        print("\n3. Total manual work: 1.5-2 hours (excluding proofs)")
        print("4. With proofs: 5.5-8 hours total")
        print("\nSee: scripts/thesis/automation/README.md for detailed instructions")
        print()

    def run(self, phase: str = "all", quick: bool = False):
        """Run validation workflow."""
        self.start_time = time.time()

        print("\n" + "#"*70)
        print("# AUTOMATED THESIS VALIDATION SYSTEM")
        print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#"*70)

        if quick or phase == "1":
            self.run_phase_1()
        elif phase == "2":
            self.run_phase_2()
        elif phase == "all":
            self.run_phase_1()
            self.run_phase_2()
        else:
            print(f"[ERROR] Invalid phase: {phase}. Use '1', '2', or 'all'")
            return

        self.generate_summary()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run all thesis validation scripts")
    parser.add_argument('--config', default='config.yaml', help='Configuration file')
    parser.add_argument('--quick', action='store_true', help='Run Phase 1 only (quick wins)')
    parser.add_argument('--phase', choices=['1', '2', 'all'], default='all', help='Which phase to run')
    args = parser.parse_args()

    runner = ValidationRunner(config_path=args.config)
    runner.run(phase=args.phase, quick=args.quick)


if __name__ == "__main__":
    main()
