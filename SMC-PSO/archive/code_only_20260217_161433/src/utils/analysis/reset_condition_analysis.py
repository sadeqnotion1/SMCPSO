#======================================================================================
#==================== src/utils/analysis/reset_condition_analysis.py ==================
#======================================================================================

"""
Statistical Analysis of Emergency Resets for Hybrid Adaptive STA-SMC.

This script runs a batch of simulations with randomized initial conditions to
empirically determine the primary causes of controller failure. It categorizes
failures into:
1. Force Saturation (Control Authority Limit)
2. State Explosion (Instability)
3. Surface Divergence (Sliding Mode Failure)
4. Numerical Instability (NaN/Inf)

This data supports the "Fundamental Incompatibility" hypothesis for Phase 2 research.
"""

import sys
import numpy as np
import argparse
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.core.simulation_context import SimulationContext
from src.core.simulation_runner import run_simulation
from src.controllers.smc.core.sliding_surface import LinearSlidingSurface

@dataclass
class FailureStats:
    total_runs: int = 0
    successes: int = 0
    failures: int = 0
    
    # Failure Modes
    force_saturation: int = 0
    state_explosion: int = 0
    surface_divergence: int = 0
    numerical_instability: int = 0
    unknown_cause: int = 0

    # Detailed Stats
    saturation_times: List[float] = None
    divergence_values: List[float] = None
    
    def __post_init__(self):
        self.saturation_times = []
        self.divergence_values = []

def analyze_run(t: np.ndarray, x: np.ndarray, u: np.ndarray, 
                gains: List[float], duration: float) -> List[str]:
    """
    Analyze a single simulation run to determine ALL termination reasons.
    
    Returns a list of failure modes occurred: ["SATURATION", "EXPLOSION", "DIVERGENCE", "NUMERICAL"]
    Returns ["SUCCESS"] if no failures occurred.
    """
    failures = []
    
    # 1. Check for Numerical Instability
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(u)):
        failures.append("NUMERICAL")
        
    # 2. Check for State Explosion (Instability)
    # PSO Instability Criteria: Angle > pi/2 (approx 1.57) rad
    if np.any(np.abs(x[:, 1:3]) > 1.57):
        failures.append("EXPLOSION")
        
    # 3. Check for Surface Divergence
    # Reconstruct sliding surface
    try:
        theta1 = x[:, 1]
        theta2 = x[:, 2]
        theta1_dot = x[:, 4]
        theta2_dot = x[:, 5]
        
        k1, k2, lam1, lam2 = gains[:4]
        s = (k1 * theta1_dot + lam1 * theta1 + 
             k2 * theta2_dot + lam2 * theta2)
             
        if np.max(np.abs(s)) > 50.0:
            failures.append("DIVERGENCE")
    except Exception:
        pass
        
    # 4. Check for Force Saturation
    MAX_FORCE = 150.0
    if np.any(np.abs(u) >= (MAX_FORCE * 0.99)):
        failures.append("SATURATION")
    
    if not failures:
        # 5. Success check (only if no other failures)
        # Note: In strict analysis, if it finished but had saturation, it's still a failure count
        if t[-1] >= duration - 0.001: 
            return ["SUCCESS"]
        else:
            return ["UNKNOWN"] # Finished early but no specific error detected?
            
    return failures

def run_analysis(n_runs: int = 100, output_file: str = "reset_analysis.json"):
    print(f"Starting Reset Condition Analysis ({n_runs} runs)...")
    print("Controller: Hybrid Adaptive STA-SMC")
    print("Conditions: Robust Stress Test (Perturbations up to +/- 0.3 rad)")
    
    ctx = SimulationContext("config.yaml")
    config = ctx.get_config()
    
    # Force use of Hybrid Adaptive STA-SMC
    controller_name = "hybrid_adaptive_sta_smc"
    
    # Use specific gains from Set 3 Report (Phase 53 gains) to reproduce failure
    print("Using Set 3 Fixed Baseline Gains: [23.67, 14.29, 8.87, 3.55]")
    gains = [23.67, 14.29, 8.87, 3.55]
    
    # Override controller creation with these gains
    def create_controller_with_gains():
        return ctx.create_controller(controller_name, gains=gains)
        
    stats = FailureStats()
    stats.total_runs = n_runs
    
    # Simulation parameters
    dt = 0.01
    duration = 5.0
    
    # Robustness: Generate random initial conditions
    np.random.seed(42)
    
    for i in range(n_runs):
        # Generate initial state
        base_init = np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])
        
        # Perturbation: +/- 0.3 rad on angles
        rand_val = np.random.random()
        if rand_val < 0.2: scale = 0.05
        elif rand_val < 0.5: scale = 0.15
        else: scale = 0.30
            
        perturbation = np.random.uniform(-scale, scale, size=6)
        x0 = base_init + perturbation
        
        # Create fresh components
        dynamics = ctx.get_dynamics_model()
        controller = create_controller_with_gains()
        
        # Run Simulation
        t, x, u = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=duration,
            dt=dt,
            initial_state=x0
        )
        
        # Analyze Result
        results = analyze_run(t, x, u, gains, duration)
        
        if "SUCCESS" in results:
            stats.successes += 1
        else:
            stats.failures += 1
            for res in results:
                if res == "SATURATION": stats.force_saturation += 1
                elif res == "EXPLOSION": stats.state_explosion += 1
                elif res == "DIVERGENCE": stats.surface_divergence += 1
                elif res == "NUMERICAL": stats.numerical_instability += 1
                elif res == "UNKNOWN": stats.unknown_cause += 1
                
        # Progress bar
        if (i+1) % 10 == 0:
            print(f"Progress: {i+1}/{n_runs} | Failures: {stats.failures}")

    # Calculate percentages
    def pct(val): return (val / n_runs) * 100.0
    
    print("\n" + "="*50)
    print("FINAL ANALYSIS RESULTS")
    print("="*50)
    print(f"Total Runs: {n_runs}")
    print(f"Successes:  {stats.successes} ({pct(stats.successes):.1f}%)")
    print(f"Failures:   {stats.failures} ({pct(stats.failures):.1f}%)")
    print("-" * 30)
    print("FAILURE MODES BREAKDOWN:")
    print(f"1. Force Saturation:    {stats.force_saturation} ({pct(stats.force_saturation):.1f}%)")
    print(f"2. State Explosion:     {stats.state_explosion} ({pct(stats.state_explosion):.1f}%)")
    print(f"3. Surface Divergence:  {stats.surface_divergence} ({pct(stats.surface_divergence):.1f}%)")
    print(f"4. Numerical Instability:{stats.numerical_instability} ({pct(stats.numerical_instability):.1f}%)")
    print(f"5. Unknown Cause:       {stats.unknown_cause} ({pct(stats.unknown_cause):.1f}%)")
    print("="*50)
    
    # Save to JSON
    output_path = PROJECT_ROOT / output_file
    with open(output_path, 'w') as f:
        json.dump(asdict(stats), f, indent=2)
    print(f"Detailed stats saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run statistical analysis of simulation resets")
    parser.add_argument("--runs", type=int, default=100, help="Number of simulation runs")
    parser.add_argument("--output", type=str, default="reset_analysis.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    run_analysis(args.runs, args.output)
