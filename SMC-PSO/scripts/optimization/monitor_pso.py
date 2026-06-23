#!/usr/bin/env python
"""Live PSO monitoring dashboard."""
import re
import time
from pathlib import Path
from datetime import datetime, timedelta

# Centralized log paths
from src.utils.infrastructure.logging.paths import PSO_LOG_DIR

def parse_log(log_file):
    """Extract PSO progress from log file."""
    if not Path(log_file).exists():
        return None

    with open(log_file) as f:
        log = f.read()

    # Find iterations
    iters = re.findall(r'(\d+)/150', log)
    current = int(iters[-1]) if iters else 0

    # Find costs
    costs = re.findall(r'best_cost=(\d+\.?\d*[eE]?[+-]?\d*)', log)
    clean_costs = []
    for c in costs:
        try:
            val = float(c)
            if val < 1e5:  # Filter out failure costs
                clean_costs.append(val)
        except Exception:  # noqa: E722
            pass

    best_cost = clean_costs[-1] if clean_costs else 'FAIL'

    # Find start time
    start_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*PSO Optimization', log)
    start_time = None
    if start_match:
        start_time = datetime.strptime(start_match.group(1), '%Y-%m-%d %H:%M:%S')

    return {
        'current': current,
        'best_cost': best_cost,
        'start_time': start_time
    }

def main():
    controllers = [
        ('classical', PSO_LOG_DIR / 'pso_classical.log'),
        ('adaptive_smc', PSO_LOG_DIR / 'pso_adaptive_smc.log'),
        ('sta_smc', PSO_LOG_DIR / 'pso_sta_smc.log'),
        ('hybrid_adaptive_sta_smc', PSO_LOG_DIR / 'pso_hybrid_adaptive_sta_smc.log')
    ]

    print("\033[2J\033[H")  # Clear screen
    print("="*80)
    print("PSO OPTIMIZATION MONITOR - Issue #12 Chattering Reduction")
    print("="*80)
    print()

    try:
        while True:
            print("\033[8;1H")  # Move cursor to line 8
            print(f"Last update: {datetime.now().strftime('%H:%M:%S')}\n")

            all_done = True
            for ctrl, log_file in controllers:
                data = parse_log(log_file)

                if data is None:
                    print(f"{ctrl:30s}: Not started")
                    all_done = False
                    continue

                current = data['current']
                best_cost = data['best_cost']
                start_time = data['start_time']

                if current < 150:
                    all_done = False

                progress = current / 150 * 100
                bar_len = 30
                filled = int(bar_len * progress / 100)
                bar = '█' * filled + '░' * (bar_len - filled)

                # Calculate ETA
                if start_time and current > 0:
                    elapsed = datetime.now() - start_time
                    time_per_iter = elapsed.total_seconds() / current
                    remaining = (150 - current) * time_per_iter
                    eta = datetime.now() + timedelta(seconds=remaining)
                    eta_str = eta.strftime('%H:%M:%S')
                else:
                    eta_str = 'N/A'

                # Format best_cost
                if isinstance(best_cost, str):
                    cost_str = best_cost
                elif best_cost > 1000:
                    cost_str = f"{best_cost:.1e}"
                else:
                    cost_str = f"{best_cost:.1f}"

                print(f"{ctrl:30s} [{bar}] {progress:5.1f}% | cost: {cost_str:>8s} | ETA: {eta_str}")

            if all_done:
                print("\n" + "="*80)
                print("ALL PSO OPTIMIZATIONS COMPLETE!")
                print("="*80)
                break

            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped. PSO processes continue in background.")
        print(f"Logs: tail -f {PSO_LOG_DIR}/pso_*.log")

if __name__ == '__main__':
    main()