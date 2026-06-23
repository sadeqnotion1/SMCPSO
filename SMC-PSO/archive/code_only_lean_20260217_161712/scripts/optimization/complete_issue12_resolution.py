#==========================================================================================\\\
#=================== scripts/optimization/complete_issue12_resolution.py =================\\\
#==========================================================================================\\\

"""
Complete Issue #12 Resolution - Automated Workflow

Orchestrates the complete PSO optimization workflow for Issue #12 chattering reduction:
1. Monitor current PSO (classical_smc)
2. Launch remaining controllers in parallel
3. Validate all optimized gains
4. Update config.yaml with results
5. Generate resolution summary

Usage:
    python scripts/optimization/complete_issue12_resolution.py
    python scripts/optimization/complete_issue12_resolution.py --skip-classical  # If already complete
"""

import argparse
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import yaml


def check_pso_status(controller: str) -> str:
    """Check PSO optimization status."""
    from src.utils.infrastructure.logging.paths import PSO_LOG_DIR
    log_file = PSO_LOG_DIR / f"pso_{controller}.log"
    gain_file = f"gains_{controller}_chattering.json"

    if Path(gain_file).exists():
        return "complete"

    if Path(log_file).exists():
        with open(log_file) as f:
            log_content = f.read()
            if "Optimization completed" in log_content:
                return "complete"
            elif "ERROR" in log_content or "FAILED" in log_content:
                return "failed"
            else:
                return "running"

    return "not_started"


def wait_for_pso(controller: str, check_interval: int = 60):
    """Wait for PSO optimization to complete."""
    print(f"Waiting for {controller} PSO to complete...")
    print(f"Checking every {check_interval} seconds...")
    print()

    while True:
        status = check_pso_status(controller)

        if status == "complete":
            print(f"✓ {controller} PSO completed!")
            return True
        elif status == "failed":
            print(f"✗ {controller} PSO failed!")
            return False
        elif status == "running":
            print(f"  [{time.strftime('%H:%M:%S')}] {controller} still running...")
            time.sleep(check_interval)
        else:
            print(f"? {controller} PSO not started yet")
            time.sleep(check_interval)


def launch_remaining_controllers():
    """Launch PSO for remaining 3 controllers in parallel."""
    print("\n" + "="*60)
    print("Launching PSO for Remaining Controllers")
    print("="*60)

    remaining = ['adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']

    cmd = [
        sys.executable,
        "scripts/optimization/run_pso_parallel.py",
        "--controllers"
    ] + remaining

    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    return result.returncode == 0


def validate_all_gains():
    """Run validation for all optimized gains."""
    print("\n" + "="*60)
    print("Validating All Optimized Gains")
    print("="*60)

    cmd = [
        sys.executable,
        "scripts/optimization/validate_optimized_gains.py",
        "--all"
    ]

    result = subprocess.run(cmd)

    return result.returncode == 0


def update_config_with_gains():
    """Update config.yaml with optimized gains."""
    print("\n" + "="*60)
    print("Updating config.yaml with Optimized Gains")
    print("="*60)

    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']

    # Load current config
    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    # Update each controller
    updated = {}
    for ctrl in controllers:
        gain_file = Path(f"gains_{ctrl}_chattering.json")
        if not gain_file.exists():
            print(f"  ✗ {ctrl}: Gains file not found")
            continue

        with open(gain_file) as f:
            data = json.load(f)

        gains = data.get('optimized_gains')
        chattering = data.get('chattering_index')

        if gains:
            # Update config
            if ctrl not in config['controllers']:
                config['controllers'][ctrl] = {}

            config['controllers'][ctrl]['gains'] = gains

            updated[ctrl] = {
                'gains': gains,
                'chattering': chattering
            }

            print(f"  ✓ {ctrl}: Updated with gains {gains}")
            print(f"    Chattering: {chattering:.3f}")
        else:
            print(f"  ✗ {ctrl}: No gains found in file")

    if updated:
        # Backup original config
        backup_file = f".archive/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        Path(backup_file).parent.mkdir(parents=True, exist_ok=True)

        with open('config.yaml') as f:
            with open(backup_file, 'w') as bf:
                bf.write(f.read())

        print(f"\n  Backup saved: {backup_file}")

        # Write updated config
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"  ✓ config.yaml updated with {len(updated)} controllers")

        return True
    else:
        print("  ✗ No controllers updated")
        return False


def generate_summary_report():
    """Generate final resolution summary."""
    print("\n" + "="*60)
    print("Generating Resolution Summary")
    print("="*60)

    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']

    report_lines = [
        "="*80,
        "Issue #12 - Chattering Reduction: RESOLUTION SUMMARY",
        "="*80,
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "OBJECTIVE: Reduce chattering from baseline ~69 to target < 2.0",
        "",
        "="*80,
        "OPTIMIZED CONTROLLER RESULTS",
        "="*80,
        ""
    ]

    all_passed = True
    results = []

    for ctrl in controllers:
        gain_file = Path(f"gains_{ctrl}_chattering.json")
        if not gain_file.exists():
            results.append(f"{ctrl:30s}: ✗ NO DATA")
            all_passed = False
            continue

        with open(gain_file) as f:
            data = json.load(f)

        gains = data.get('optimized_gains', [])
        chattering = data.get('chattering_index', 999)
        tracking = data.get('tracking_error_rms', 999)

        status = "✓ PASS" if chattering < 2.0 else "✗ FAIL"
        if chattering >= 2.0:
            all_passed = False

        results.append(f"{ctrl:30s}: {status}")
        results.append(f"  Chattering:     {chattering:.3f} {'< 2.0 ✓' if chattering < 2.0 else '>= 2.0 ✗'}")
        results.append(f"  Tracking Error: {tracking:.4f} rad")
        results.append(f"  Gains:          {gains}")
        results.append("")

    report_lines.extend(results)

    report_lines.extend([
        "="*80,
        "OVERALL STATUS",
        "="*80,
        ""
    ])

    if all_passed:
        report_lines.extend([
            "✓✓✓ ISSUE #12 RESOLVED ✓✓✓",
            "",
            "All 4 controllers successfully optimized with chattering < 2.0 target.",
            "Chattering reduced from baseline ~69 to < 2.0 (97% reduction).",
            "",
            "PRODUCTION READY: Optimized gains deployed to config.yaml",
            ""
        ])
    else:
        report_lines.extend([
            "✗✗✗ ISSUE #12 PARTIALLY RESOLVED ✗✗✗",
            "",
            "Some controllers did not meet chattering < 2.0 target.",
            "Additional optimization may be required.",
            ""
        ])

    report_lines.extend([
        "="*80,
        "NEXT STEPS",
        "="*80,
        "",
        "1. Review optimized gains in config.yaml",
        "2. Run full test suite: pytest tests/test_integration/",
        "3. Commit results: git add . && git commit -m 'RESOLVED Issue #12'",
        "4. Close Issue #12 on GitHub",
        ""
    ])

    report = "\n".join(report_lines)

    # Save report
    report_file = f"docs/issue_12_final_resolution_{datetime.now().strftime('%Y%m%d')}.md"
    Path(report_file).parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w') as f:
        f.write(report)

    print(report)
    print(f"\nReport saved: {report_file}")

    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Complete Issue #12 Resolution Workflow"
    )
    parser.add_argument(
        '--skip-classical',
        action='store_true',
        help='Skip waiting for classical_smc (already complete)'
    )

    args = parser.parse_args()

    print("="*80)
    print("Issue #12 - Chattering Reduction: AUTOMATED RESOLUTION")
    print("="*80)
    print()

    # Step 1: Check/wait for classical_smc
    if not args.skip_classical:
        classical_status = check_pso_status('classical_smc')
        print(f"classical_smc status: {classical_status}")

        if classical_status == "running":
            success = wait_for_pso('classical_smc')
            if not success:
                print("\n✗ classical_smc PSO failed. Aborting workflow.")
                sys.exit(1)
        elif classical_status == "not_started":
            print("\n✗ classical_smc PSO not started. Please launch first.")
            sys.exit(1)
        elif classical_status == "failed":
            print("\n✗ classical_smc PSO failed. Please debug first.")
            sys.exit(1)
    else:
        print("Skipping classical_smc wait (--skip-classical)")

    # Step 2: Launch remaining controllers
    print("\n" + "="*60)
    print("STEP 2: Launch Remaining Controllers")
    print("="*60)

    success = launch_remaining_controllers()
    if not success:
        print("\n✗ Failed to launch remaining controllers")
        sys.exit(1)

    # Step 3: Validate all gains
    print("\n" + "="*60)
    print("STEP 3: Validate All Gains")
    print("="*60)

    success = validate_all_gains()
    if not success:
        print("\n⚠ Some validations failed (see above)")

    # Step 4: Update config
    print("\n" + "="*60)
    print("STEP 4: Update config.yaml")
    print("="*60)

    update_config_with_gains()

    # Step 5: Generate summary
    print("\n" + "="*60)
    print("STEP 5: Generate Summary Report")
    print("="*60)

    all_passed = generate_summary_report()

    # Final status
    print("\n" + "="*80)
    print("WORKFLOW COMPLETE")
    print("="*80)

    if all_passed:
        print("\n✓ All controllers optimized successfully!")
        print("✓ Issue #12 can be marked as RESOLVED")
        sys.exit(0)
    else:
        print("\n⚠ Some controllers need attention")
        print("Review the summary report for details")
        sys.exit(1)


if __name__ == '__main__':
    main()