#==========================================================================================\\\
#========================= scripts/debug_pso_fitness.py =================================\\\
#==========================================================================================\\\

"""PSO Fitness Function Diagnostic Tool

Diagnoses potential issues with PSO cost function including:
- Excessive normalization from baseline
- Unbalanced cost weights
- Cost sensitivity problems
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config


def diagnose_normalization():
    """Diagnose normalization effects and cost function sensitivity"""
    config = load_config("config.yaml")

    # Create PSOTuner (triggers baseline normalization if configured)
    def dummy_factory(gains):
        from src.controllers.smc.classic_smc import ClassicalSMC
        return ClassicalSMC(gains=gains, max_force=100.0)

    try:
        tuner = PSOTuner(dummy_factory, config)
    except Exception as e:
        print(f"Error creating PSOTuner: {e}")
        return

    # Print normalization constants
    print("=" * 90)
    print("PSO NORMALIZATION DIAGNOSTIC")
    print("=" * 90)
    print("\nNormalization Constants:")
    print(f"  norm_ise:    {tuner.norm_ise:.6e}")
    print(f"  norm_u:      {tuner.norm_u:.6e}")
    print(f"  norm_du:     {tuner.norm_du:.6e}")
    print(f"  norm_sigma:  {tuner.norm_sigma:.6e}")

    print("\nCost Weights:")
    print(f"  state_error:     {tuner.weights.state_error}")
    print(f"  control_effort:  {tuner.weights.control_effort}")
    print(f"  control_rate:    {tuner.weights.control_rate}")
    print(f"  stability:       {tuner.weights.stability}")

    print(f"\nInstability Penalty: {tuner.instability_penalty:.6e}")
    print(f"Combine Weights: mean={tuner.combine_weights[0]}, max={tuner.combine_weights[1]}")

    # Simulate example cost computation
    print(f"\n{'=' * 90}")
    print("EXAMPLE COST COMPUTATION")
    print("=" * 90)

    # Example raw costs (typical good controller)
    ise_raw = 1.0      # Good tracking
    u_sq_raw = 50.0    # Moderate control effort
    du_sq_raw = 100.0  # Moderate slew rate
    sigma_sq_raw = 0.5 # Good sliding surface convergence

    # Normalize
    ise_n = ise_raw / tuner.norm_ise if tuner.norm_ise > 1e-12 else ise_raw
    u_n = u_sq_raw / tuner.norm_u if tuner.norm_u > 1e-12 else u_sq_raw
    du_n = du_sq_raw / tuner.norm_du if tuner.norm_du > 1e-12 else du_sq_raw
    sigma_n = sigma_sq_raw / tuner.norm_sigma if tuner.norm_sigma > 1e-12 else sigma_sq_raw

    print("\nRaw Costs:")
    print(f"  ISE:     {ise_raw:.4f}  ->  Normalized: {ise_n:.6e}")
    print(f"  U2:      {u_sq_raw:.4f}  ->  Normalized: {u_n:.6e}")
    print(f"  (DU)2:   {du_sq_raw:.4f}  ->  Normalized: {du_n:.6e}")
    print(f"  sigma2:  {sigma_sq_raw:.4f}  ->  Normalized: {sigma_n:.6e}")

    # Compute weighted cost
    J_components = {
        'state_error': tuner.weights.state_error * ise_n,
        'control_effort': tuner.weights.control_effort * u_n,
        'control_rate': tuner.weights.control_rate * du_n,
        'stability': tuner.weights.stability * sigma_n
    }

    J_total = sum(J_components.values())

    print("\nWeighted Cost Components:")
    for name, value in J_components.items():
        pct = (value / J_total * 100) if J_total > 0 else 0
        print(f"  {name:20s}: {value:.6e}  ({pct:.1f}%)")

    print(f"\nTotal Cost: {J_total:.6e}")

    print(f"\n{'=' * 90}")
    print("ASSESSMENT")
    print("=" * 90)

    # Assess normalization health
    issues_found = False

    if tuner.norm_ise > 100.0:
        print("WARNING: norm_ise is very large - may cause excessive normalization")
        issues_found = True

    if tuner.norm_u > 1000.0:
        print("WARNING: norm_u is very large - control effort may be over-normalized")
        issues_found = True

    if tuner.weights.state_error > 10.0:
        print(f"WARNING: state_error weight ({tuner.weights.state_error}) is very high - may dominate cost")
        issues_found = True

    if J_total < 1e-3:
        print("CRITICAL: Total cost is near zero - PSO cannot distinguish particles")
        print("         This will cause all PSO runs to converge to cost=0.0")
        issues_found = True

    # Check weight balance
    max_weight = max(tuner.weights.state_error, tuner.weights.control_effort,
                     tuner.weights.control_rate, tuner.weights.stability)
    min_weight = min(tuner.weights.state_error, tuner.weights.control_effort,
                     tuner.weights.control_rate, tuner.weights.stability)

    if max_weight / min_weight > 100:
        print(f"WARNING: Weights are highly unbalanced (ratio: {max_weight/min_weight:.1f}:1)")
        issues_found = True

    if not issues_found:
        print("OK: Cost function sensitivity appears reasonable")
        print("    No major issues detected")

    print("\n" + "=" * 90)
    print("RECOMMENDATIONS")
    print("=" * 90)

    if tuner.norm_ise > 100.0 or tuner.weights.state_error > 10.0 or J_total < 1e-3:
        print("\nConfiguration changes needed:")
        print("\n1. Remove or fix baseline normalization:")
        print("   # config.yaml")
        print("   # baseline:")
        print("   #   gains: []  # REMOVE THIS")
        print("\n2. Reduce state_error weight:")
        print("   weights:")
        print("     state_error: 1.0      # Reduce from current value")
        print("\n3. Add explicit normalization constants:")
        print("   norms:")
        print("     state_error: 10.0")
        print("     control_effort: 100.0")
        print("     control_rate: 1000.0")
        print("     sliding: 1.0")
    else:
        print("\nNo immediate configuration changes required.")
        print("Monitor PSO convergence for cost=0.0 issues.")


if __name__ == "__main__":
    diagnose_normalization()