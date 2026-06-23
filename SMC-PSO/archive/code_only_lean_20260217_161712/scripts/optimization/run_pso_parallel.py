#==========================================================================================\\\
#========================== scripts/optimization/run_pso_parallel.py =====================\\\
#==========================================================================================\\\

"""
Parallel PSO optimization launcher for multiple controllers.

Launches PSO optimization for multiple controllers simultaneously in background processes.
Monitors progress and collects results when complete.

Usage:
    python scripts/optimization/run_pso_parallel.py --controllers adaptive_smc sta_smc hybrid_adaptive_sta_smc
    python scripts/optimization/run_pso_parallel.py --all
"""

import subprocess
import argparse
import time
import sys
from pathlib import Path
from typing import Dict
import json

# Centralized log paths
from src.utils.infrastructure.logging.paths import PSO_LOG_DIR


def launch_pso(controller: str, n_particles: int = 30, iters: int = 150,
               seed: int = 42) -> subprocess.Popen:
    """Launch PSO optimization in background process."""
    output_file = f"gains_{controller}_chattering.json"
    log_file = PSO_LOG_DIR / f"pso_{controller}.log"

    cmd = [
        sys.executable,
        "scripts/optimization/optimize_chattering_direct.py",
        "--controller", controller,
        "--n-particles", str(n_particles),
        "--iters", str(iters),
        "--seed", str(seed),
        "--output", output_file
    ]

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'w') as log:
        process = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True
        )

    print(f"✓ Launched PSO for {controller}")
    print(f"  PID: {process.pid}")
    print(f"  Log: {log_file}")
    print(f"  Output: {output_file}")
    print()

    return process


def monitor_processes(processes: Dict[str, subprocess.Popen]):
    """Monitor background processes and report status."""
    print("Monitoring PSO processes...")
    print("Press Ctrl+C to check status (processes continue in background)")
    print()

    try:
        while any(p.poll() is None for p in processes.values()):
            time.sleep(30)

            print(f"\n[Status Update - {time.strftime('%H:%M:%S')}]")
            for ctrl, proc in processes.items():
                if proc.poll() is None:
                    print(f"  {ctrl:25s}: Running (PID {proc.pid})")
                else:
                    returncode = proc.returncode
                    status = "✓ Complete" if returncode == 0 else f"✗ Failed (code {returncode})"
                    print(f"  {ctrl:25s}: {status}")
            print()

    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted (processes still running in background)")
        print(f"Check logs: tail -f {PSO_LOG_DIR}/pso_*.log")
        print()
        for ctrl, proc in processes.items():
            if proc.poll() is None:
                print(f"  {ctrl}: PID {proc.pid} - {PSO_LOG_DIR}/pso_{ctrl}.log")
        sys.exit(0)

    print("\n" + "="*60)
    print("All PSO processes completed!")
    print("="*60)

    # Report results
    for ctrl, proc in processes.items():
        returncode = proc.returncode
        if returncode == 0:
            output_file = f"gains_{ctrl}_chattering.json"
            if Path(output_file).exists():
                with open(output_file) as f:
                    data = json.load(f)
                chattering = data.get('chattering_index', 'N/A')
                print(f"✓ {ctrl:25s}: chattering_index = {chattering}")
            else:
                print(f"? {ctrl:25s}: Completed but output file not found")
        else:
            print(f"✗ {ctrl:25s}: Failed with return code {returncode}")


def main():
    parser = argparse.ArgumentParser(
        description="Launch parallel PSO optimization for multiple controllers"
    )
    parser.add_argument(
        '--controllers',
        nargs='+',
        choices=['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc'],
        help='Controllers to optimize'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Optimize all 4 controllers'
    )
    parser.add_argument(
        '--n-particles',
        type=int,
        default=30,
        help='Number of PSO particles (default: 30)'
    )
    parser.add_argument(
        '--iters',
        type=int,
        default=150,
        help='Number of PSO iterations (default: 150)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )

    args = parser.parse_args()

    if args.all:
        controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']
    elif args.controllers:
        controllers = args.controllers
    else:
        parser.error("Must specify --controllers or --all")

    print("="*60)
    print("PSO Parallel Optimization Launcher")
    print("="*60)
    print(f"Controllers: {', '.join(controllers)}")
    print(f"Particles:   {args.n_particles}")
    print(f"Iterations:  {args.iters}")
    print(f"Seed:        {args.seed}")
    print()

    # Launch all processes
    processes = {}
    for ctrl in controllers:
        proc = launch_pso(ctrl, args.n_particles, args.iters, args.seed)
        processes[ctrl] = proc
        time.sleep(2)  # Stagger launches slightly

    print("="*60)
    print(f"Launched {len(processes)} PSO processes")
    print("="*60)
    print()

    # Monitor until completion
    monitor_processes(processes)


if __name__ == '__main__':
    main()