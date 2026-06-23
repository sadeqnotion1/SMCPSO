#==========================================================================================\\\
#===================== scripts/optimization/watch_pso.py ==================================\\\
#==========================================================================================\\\

"""
PSO Live Dashboard - Continuous monitoring with visual progress

Simple live dashboard that refreshes every 10 seconds showing PSO progress.

Usage:
    python scripts/optimization/watch_pso.py
    python scripts/optimization/watch_pso.py --interval 5
"""

import sys
from pathlib import Path
import time
import argparse
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Centralized log paths
from src.utils.infrastructure.logging.paths import PSO_LOG_DIR

from check_pso_completion import check_log_completion  # noqa: E402


def clear_screen():
    """Clear terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def draw_progress_bar(current, total, width=40):
    """Draw ASCII progress bar."""
    filled = int(width * current / total)
    bar = '=' * filled + '-' * (width - filled)
    pct = 100 * current / total
    return f"[{bar}] {current}/{total} ({pct:.1f}%)"


def print_dashboard(controllers):
    """Print live dashboard."""
    clear_screen()

    print("=" * 80)
    print(f"PSO LIVE DASHBOARD - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    print()

    total_current = 0
    total_max = 0
    all_complete = True

    for ctrl, log_path in controllers.items():
        result = check_log_completion(Path(log_path))

        if not result.get('exists', False):
            print(f"{ctrl:20s} : [NO LOG]")
            all_complete = False
            continue

        current = result.get('current_iter', 0)
        total = result.get('total_iters', 150)
        complete = result.get('completed', False)

        total_current += current
        total_max += total

        if not complete:
            all_complete = False

        # Status indicator
        status = "[DONE]" if complete else "[RUNNING]"

        # Progress bar
        progress = draw_progress_bar(current, total, width=30)

        # Best cost
        cost = result.get('best_cost')
        cost_str = f"cost={cost:.2e}" if cost else "cost=N/A"

        print(f"{ctrl:20s} {status:10s} {progress}  {cost_str}")

    print()
    print("=" * 80)

    # Overall progress
    # overall_pct =  # Unused 100 * total_current / total_max if total_max > 0 else 0
    overall_bar = draw_progress_bar(total_current, total_max, width=50)
    print(f"OVERALL: {overall_bar}")

    print("=" * 80)

    if all_complete:
        print()
        print("[OK] ALL PSO OPTIMIZATIONS COMPLETE!")
        print()
        print("Next step:")
        print("  python scripts/optimization/validate_and_summarize.py")
        print()
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description='PSO Live Dashboard')
    parser.add_argument(
        '--interval', type=int, default=10,
        help='Refresh interval in seconds (default: 10)'
    )
    args = parser.parse_args()

    controllers = {
        'classical_smc': PSO_LOG_DIR / 'pso_classical.log',
        'adaptive_smc': PSO_LOG_DIR / 'pso_adaptive_smc.log',
        'sta_smc': PSO_LOG_DIR / 'pso_sta_smc.log'
    }

    try:
        while True:
            complete = print_dashboard(controllers)

            if complete:
                return 0

            print(f"Refreshing in {args.interval} seconds... (Ctrl+C to stop)")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print()
        print()
        print("Dashboard stopped.")
        print()
        return 0


if __name__ == '__main__':
    sys.exit(main())