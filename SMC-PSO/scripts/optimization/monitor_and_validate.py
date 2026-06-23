#==========================================================================================\\\
#================= scripts/optimization/monitor_and_validate.py ===========================\\\
#==========================================================================================\\\

"""
PSO Monitor and Auto-Validator

Continuously monitors PSO progress and automatically triggers validation
when all optimizations complete. Part of Issue #12 end-to-end automation.

Usage:
    python scripts/optimization/monitor_and_validate.py --interval 60

Options:
    --interval SECONDS    Check interval in seconds (default: 60)
    --max-wait MINUTES    Maximum wait time in minutes (default: 240 = 4 hours)
    --auto-update-config  Automatically update config.yaml if validation passes
"""

import sys
from pathlib import Path
import time
import argparse
import subprocess
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from check_pso_completion import check_log_completion  # noqa: E402


def print_status_header():
    """Print formatted status header."""
    print()
    print("=" * 80)
    print(f"PSO MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def print_controller_status(controllers: dict) -> tuple:
    """
    Print controller status.

    Returns:
        (all_complete, n_complete, n_total)
    """
    all_complete = True
    n_complete = 0
    n_total = len(controllers)

    for ctrl, log_path in controllers.items():
        result = check_log_completion(Path(log_path))

        print(f"{ctrl:20s}:", end=' ')

        if not result.get('exists', False):
            print("[NO LOG]")
            all_complete = False
        elif result.get('error'):
            print(f"[ERROR] {result['error']}")
            all_complete = False
        elif result['completed']:
            print(f"[DONE] {result['current_iter']}/{result['total_iters']}, " +
                 f"cost={result['best_cost']:.2e}" if result.get('best_cost') else "[DONE]")
            n_complete += 1
        else:
            current = result.get('current_iter', 0)
            total = result.get('total_iters', 150)
            pct = result.get('progress_pct', 0)
            print(f"[RUNNING] {current}/{total} ({pct:.1f}%)")
            all_complete = False

    print()
    print(f"Overall: {n_complete}/{n_total} controllers complete")

    return all_complete, n_complete, n_total


def run_validation() -> bool:
    """
    Run validation script.

    Returns:
        True if validation passes, False otherwise
    """
    print()
    print("=" * 80)
    print("RUNNING VALIDATION...")
    print("=" * 80)
    print()

    try:
        result = subprocess.run(
            [sys.executable, 'scripts/optimization/validate_and_summarize.py'],
            capture_output=False,
            cwd=project_root
        )

        success = result.returncode == 0

        print()
        print("=" * 80)
        print(f"VALIDATION: {'[PASS]' if success else '[FAIL]'}")
        print("=" * 80)

        return success

    except Exception as e:
        print(f"Error running validation: {e}")
        return False


def update_config() -> bool:
    """
    Update config.yaml with optimized gains.

    Returns:
        True if update successful, False otherwise
    """
    print()
    print("=" * 80)
    print("UPDATING CONFIG.YAML...")
    print("=" * 80)
    print()

    try:
        result = subprocess.run(
            [sys.executable, 'scripts/optimization/update_config_with_gains.py'],
            capture_output=False,
            cwd=project_root
        )

        success = result.returncode == 0

        print()
        print("=" * 80)
        print(f"CONFIG UPDATE: {'[SUCCESS]' if success else '[FAILED]'}")
        print("=" * 80)

        return success

    except Exception as e:
        print(f"Error updating config: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Monitor PSO and auto-validate when complete'
    )
    parser.add_argument(
        '--interval', type=int, default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--max-wait', type=int, default=240,
        help='Maximum wait time in minutes (default: 240 = 4 hours)'
    )
    parser.add_argument(
        '--auto-update-config', action='store_true',
        help='Automatically update config.yaml if validation passes'
    )

    args = parser.parse_args()

    from src.utils.infrastructure.logging.paths import PSO_LOG_DIR
    controllers = {
        'classical_smc': PSO_LOG_DIR / 'pso_classical.log',
        'adaptive_smc': PSO_LOG_DIR / 'pso_adaptive_smc.log',
        'sta_smc': PSO_LOG_DIR / 'pso_sta_smc.log'
    }

    print("=" * 80)
    print("PSO MONITORING AND AUTO-VALIDATION")
    print("=" * 80)
    print(f"Check interval: {args.interval} seconds")
    print(f"Max wait time: {args.max_wait} minutes")
    print(f"Auto-update config: {args.auto_update_config}")
    print("=" * 80)

    start_time = datetime.now()
    max_wait_td = timedelta(minutes=args.max_wait)
    check_count = 0

    while True:
        check_count += 1
        print_status_header()
        print(f"Check #{check_count}")
        print()

        all_complete, n_complete, n_total = print_controller_status(controllers)

        if all_complete:
            print()
            print("[OK] ALL PSO OPTIMIZATIONS COMPLETE!")
            print()

            # Run validation
            validation_passed = run_validation()

            if validation_passed and args.auto_update_config:
                # Update config
                config_updated = update_config()

                if config_updated:
                    print()
                    print("[SUCCESS] Config updated with optimized gains!")
                    print()
                    print("Next steps:")
                    print("1. Review changes: git diff config.yaml")
                    print("2. Test controllers: python simulate.py --ctrl classical_smc --plot")
                    print("3. Commit changes and close Issue #12")
                else:
                    print()
                    print("[WARNING] Config update failed, manual intervention required")

            elif validation_passed:
                print()
                print("Next steps:")
                print("1. Review validation results")
                print("2. Update config: python scripts/optimization/update_config_with_gains.py")
                print("3. Commit and close Issue #12")

            else:
                print()
                print("[FAIL] Validation failed - chattering targets not met")
                print()
                print("Recommended action:")
                print("Re-run with corrected fitness function:")
                print("  python scripts/optimization/optimize_chattering_focused.py --controller classical_smc")
                print("  python scripts/optimization/optimize_chattering_focused.py --controller adaptive_smc")
                print("  python scripts/optimization/optimize_chattering_focused.py --controller sta_smc")

            print()
            print("=" * 80)
            print("MONITORING COMPLETE")
            print("=" * 80)
            return 0

        # Check timeout
        elapsed = datetime.now() - start_time
        if elapsed > max_wait_td:
            print()
            print(f"[TIMEOUT] Maximum wait time ({args.max_wait} minutes) exceeded")
            print(f"Elapsed: {elapsed}")
            print()
            print(f"Progress: {n_complete}/{n_total} complete")
            print("PSO still running. Exiting monitor.")
            print()
            print("To resume monitoring:")
            print(f"  python scripts/optimization/monitor_and_validate.py --interval {args.interval}")
            return 1

        # Wait for next check
        print(f"Waiting {args.interval} seconds until next check...")
        print(f"Elapsed time: {elapsed}")
        remaining = max_wait_td - elapsed
        print(f"Time remaining: {remaining}")
        print("=" * 80)

        time.sleep(args.interval)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("MONITORING INTERRUPTED")
        print("=" * 80)
        print()
        print("To resume:")
        print("  python scripts/optimization/monitor_and_validate.py")
        sys.exit(130)