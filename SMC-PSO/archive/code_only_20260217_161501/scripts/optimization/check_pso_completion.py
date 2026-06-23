#==========================================================================================\\\
#================= scripts/optimization/check_pso_completion.py ===========================\\\
#==========================================================================================\\\

"""
PSO Completion Checker and Auto-Validator

Monitors PSO log files for completion and automatically triggers validation
when all optimizations are done. Part of Issue #12 automation workflow.
"""

import sys
from pathlib import Path
import re
import subprocess
from datetime import datetime

# Centralized log paths
from src.utils.infrastructure.logging.paths import PSO_LOG_DIR

def check_log_completion(log_file: Path) -> dict:
    """
    Check if PSO log file shows completion.

    Returns:
        dict with 'completed', 'current_iter', 'total_iters', 'best_cost'
    """
    if not log_file.exists():
        return {'completed': False, 'exists': False, 'current_iter': 0, 'total_iters': 150}

    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for iteration progress
        iter_matches = re.findall(r'(\d+)/(\d+),\s*best_cost=([0-9.e+]+)', content)

        if not iter_matches:
            return {'completed': False, 'exists': True, 'current_iter': 0,
                   'total_iters': 150, 'best_cost': None}

        # Get last iteration
        last_iter_str, total_str, best_cost_str = iter_matches[-1]
        current_iter = int(last_iter_str)
        total_iters = int(total_str)

        try:
            best_cost = float(best_cost_str)
        except (ValueError, TypeError):  # noqa: E722
            best_cost = None

        completed = current_iter >= total_iters

        return {
            'completed': completed,
            'exists': True,
            'current_iter': current_iter,
            'total_iters': total_iters,
            'best_cost': best_cost,
            'progress_pct': (current_iter / total_iters) * 100
        }

    except Exception as e:
        print(f"Error reading {log_file}: {e}")
        return {'completed': False, 'exists': True, 'error': str(e)}


def check_json_results(controller: str) -> bool:
    """Check if JSON results file exists for controller."""
    json_file = Path(f'gains_{controller}_chattering.json')
    return json_file.exists()


def main():
    print("=" * 80)
    print("PSO COMPLETION CHECKER - Issue #12")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    controllers = {
        'classical_smc': PSO_LOG_DIR / 'pso_classical.log',
        'adaptive_smc': PSO_LOG_DIR / 'pso_adaptive_smc.log',
        'sta_smc': PSO_LOG_DIR / 'pso_sta_smc.log'
    }

    status = {}
    all_completed = True

    for ctrl, log_path in controllers.items():
        log_file = Path(log_path)
        result = check_log_completion(log_file)
        status[ctrl] = result

        # Print status
        print(f"{ctrl:20s}:", end=' ')

        if not result.get('exists', False):
            print("[NO LOG]")
            all_completed = False
        elif result.get('error'):
            print(f"[ERROR] {result['error']}")
            all_completed = False
        elif result['completed']:
            print(f"[COMPLETE] {result['current_iter']}/{result['total_iters']}, " +
                 f"best_cost={result['best_cost']:.2e}" if result['best_cost'] else "[COMPLETE]")
        else:
            print(f"[RUNNING] {result['current_iter']}/{result['total_iters']} " +
                 f"({result['progress_pct']:.1f}%), best_cost={result['best_cost']:.2e}"
                 if result.get('best_cost') else
                 f"[RUNNING] {result['current_iter']}/{result['total_iters']}")
            all_completed = False

    print()
    print("=" * 80)

    # Check for JSON results
    print("JSON Results Files:")
    for ctrl in controllers.keys():
        has_json = check_json_results(ctrl)
        print(f"  {ctrl:20s}: {'[EXISTS]' if has_json else '[MISSING]'}")

    print()

    if all_completed:
        print("[OK] All PSO optimizations COMPLETE!")
        print()
        print("Next Steps:")
        print("1. Run validation:")
        print("   python scripts/optimization/validate_and_summarize.py")
        print()
        print("2. Update config if validation passes:")
        print("   python scripts/optimization/update_config_with_gains.py")

        # Optionally auto-trigger validation
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--auto-validate', action='store_true',
                          help='Automatically run validation when complete')
        args, _ = parser.parse_known_args()

        if args.auto_validate:
            print()
            print("=" * 80)
            print("AUTO-TRIGGERING VALIDATION...")
            print("=" * 80)
            print()

            result = subprocess.run(
                [sys.executable, 'scripts/optimization/validate_and_summarize.py'],
                capture_output=False
            )

            sys.exit(result.returncode)
    else:
        print("[WAITING] PSO optimization still in progress")
        print()

        # Estimate time remaining
        incomplete = [(ctrl, st) for ctrl, st in status.items()
                     if not st.get('completed', False) and st.get('exists', False)]

        if incomplete:
            print("Estimated Progress:")
            for ctrl, st in incomplete:
                current = st.get('current_iter', 0)
                total = st.get('total_iters', 150)
                remaining = total - current
                print(f"  {ctrl:20s}: {remaining} iterations remaining")

    print()
    print("=" * 80)

    return 0 if all_completed else 1


if __name__ == '__main__':
    sys.exit(main())