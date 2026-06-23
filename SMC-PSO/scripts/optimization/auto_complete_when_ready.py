#==========================================================================================\\\
#=================== scripts/optimization/auto_complete_when_ready.py ====================\\\
#==========================================================================================\\\

"""
Auto-complete Issue #12 resolution when all PSO complete.

Polls for completion, then automatically validates and prepares commit.
"""

import time
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def check_pso_complete(controller):
    """Check if PSO is complete for a controller."""
    from src.utils.infrastructure.logging.paths import PSO_LOG_DIR
    log_map = {
        'classical_smc': PSO_LOG_DIR / 'pso_classical.log',
        'adaptive_smc': PSO_LOG_DIR / 'pso_adaptive_smc.log',
        'sta_smc': PSO_LOG_DIR / 'pso_sta_smc.log'
    }

    log_file = log_map.get(controller)
    if not log_file or not Path(log_file).exists():
        return False

    with open(log_file) as f:
        log = f.read()

    return 'Optimization completed' in log

def wait_for_all_complete():
    """Wait for all 3 PSO processes to complete."""
    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc']

    print("Waiting for all PSO optimizations to complete...")
    print("(This will run in the background)\n")

    while True:
        status = {}
        for ctrl in controllers:
            status[ctrl] = check_pso_complete(ctrl)

        all_done = all(status.values())

        # Print status
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] " +
              " | ".join([f"{c}: {'DONE' if s else 'RUNNING'}" for c,s in status.items()]),
              end='', flush=True)

        if all_done:
            print("\n\nAll PSO optimizations complete!")
            return True

        time.sleep(30)  # Check every 30 seconds

def extract_results():
    """Extract chattering results from all JSON files."""
    results = {}

    for ctrl in ['classical_smc', 'adaptive_smc', 'sta_smc']:
        json_file = Path(f'gains_{ctrl}_chattering.json') / f'gains_{ctrl}_chattering.json'

        if not json_file.exists():
            results[ctrl] = {'status': 'MISSING', 'chattering': None}
            continue

        try:
            with open(json_file) as f:
                data = json.load(f)

            chattering = data.get('chattering_index', 999)
            gains = data.get('optimized_gains', [])

            results[ctrl] = {
                'status': 'PASS' if chattering < 2.0 else 'FAIL',
                'chattering': chattering,
                'gains': gains
            }
        except Exception:  # noqa: E722
            results[ctrl] = {'status': 'ERROR', 'chattering': None}

    return results

def generate_summary(results):
    """Generate completion summary."""
    print("\n" + "="*80)
    print("ISSUE #12 - PSO OPTIMIZATION RESULTS")
    print("="*80)
    print()

    passed = 0
    for ctrl, data in results.items():
        status = data['status']
        chattering = data.get('chattering', 'N/A')

        if chattering != 'N/A':
            chatter_str = f"{chattering:.3f}"
            target_str = "< 2.0 TARGET" if chattering < 2.0 else ">= 2.0 FAIL"
        else:
            chatter_str = 'N/A'
            target_str = ''

        print(f"{ctrl:25s}: {status:8s} | Chattering: {chatter_str:>8s} {target_str}")

        if status == 'PASS':
            passed += 1

    print()
    print(f"Results: {passed}/3 controllers passed")
    print("="*80)

    return passed == 3

def main():
    print("="*80)
    print("AUTO-COMPLETION SCRIPT - Issue #12")
    print("="*80)
    print()

    # Step 1: Wait for completion
    wait_for_all_complete()

    # Step 2: Extract results
    print("\nExtracting results...")
    results = extract_results()

    # Step 3: Generate summary
    all_passed = generate_summary(results)

    # Step 4: Run validation
    print("\nRunning validation...")
    val_result = subprocess.run([
        sys.executable,
        'scripts/optimization/validate_optimized_gains.py',
        '--all'
    ])

    if val_result.returncode == 0:
        print("\n✓ Validation PASSED")
    else:
        print("\n✗ Validation FAILED")

    # Step 5: Instructions
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)

    if all_passed:
        print("\n✓✓✓ ALL CONTROLLERS OPTIMIZED SUCCESSFULLY ✓✓✓\n")
        print("1. Review results above")
        print("2. Update config.yaml manually with optimized gains")
        print("3. Commit results:")
        print("   git add gains_*_chattering.json config.yaml")
        print("   git commit -m 'RESOLVED: Issue #12 - Chattering Reduction (3/4 controllers)'")
        print("   git push origin main")
    else:
        print("\n⚠ Some controllers did not meet targets")
        print("1. Review results above")
        print("2. Consider re-running PSO with adjusted parameters")
        print("3. Or commit partial results with documentation")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted. PSO processes continue in background.")
        sys.exit(0)