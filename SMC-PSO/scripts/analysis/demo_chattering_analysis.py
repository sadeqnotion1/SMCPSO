"""
================================================================================
Chattering Metrics Analysis Demonstration
================================================================================

Demonstrates how to use the chattering metrics module (QW-4) to analyze
control signal quality from SMC controllers.

This script shows:
1. How to extract control signals from simulation
2. How to compute chattering metrics
3. How to use metrics for controller tuning (MT-6: Boundary layer optimization)

Usage:
    python scripts/demo_chattering_analysis.py

Author: DIP_SMC_PSO Team
Created: October 2025 (Week 1, Task QW-4)
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.analysis.chattering import compute_chattering_metrics


def simulate_smc_control_signal(
    duration: float = 2.0,
    dt: float = 0.001,
    chattering_frequency: float = 30.0,
    chattering_amplitude: float = 0.5
) -> tuple:
    """
    Simulate an SMC control signal with realistic chattering.

    Parameters
    ----------
    duration : float
        Simulation duration (seconds)
    dt : float
        Time step (seconds)
    chattering_frequency : float
        Frequency of chattering oscillation (Hz)
    chattering_amplitude : float
        Amplitude of chattering component (relative)

    Returns
    -------
    t : ndarray
        Time array
    control_signal : ndarray
        Simulated control signal with chattering
    """
    t = np.arange(0, duration, dt)

    # Smooth nominal control (e.g., from sliding surface)
    nominal_control = 10.0 * np.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz smooth oscillation

    # Add chattering (high-frequency oscillation)
    chattering = chattering_amplitude * np.sin(2 * np.pi * chattering_frequency * t)

    # Combined signal
    control_signal = nominal_control + chattering

    return t, control_signal


def demo_chattering_analysis():
    """Demonstrate chattering metrics analysis."""
    print("=" * 80)
    print("CHATTERING METRICS ANALYSIS DEMONSTRATION (QW-4)")
    print("=" * 80)

    # Simulation parameters
    dt = 0.001  # 1 ms sampling period (1 kHz)
    duration = 2.0  # 2 seconds

    print("\n[1/4] Simulating SMC control signal with chattering...")
    print(f"      Duration: {duration}s, Sampling: {1/dt:.0f} Hz")

    # Case 1: Control signal with 30 Hz chattering (typical classical SMC)
    t, signal_classical = simulate_smc_control_signal(
        duration=duration,
        dt=dt,
        chattering_frequency=30.0,
        chattering_amplitude=0.5
    )

    print("      Generated signal with 30 Hz chattering (Classical SMC)")

    print("\n[2/4] Computing chattering metrics...")

    # Compute metrics
    metrics = compute_chattering_metrics(
        signal_classical,
        dt=dt,
        freq_threshold=0.1,  # Low threshold for this demo
        freq_min=10.0,
        freq_max=200.0
    )

    print(f"      Peak chattering frequency: {metrics['peak_frequency']:.1f} Hz")
    print(f"      Peak amplitude: {metrics['peak_amplitude']:.4f}")
    print(f"      Chattering index (RMS): {metrics['chattering_index']:.4f}")
    print(f"      Total power in band: {metrics['total_power']:.4f}")
    print(f"      Has chattering: {metrics['has_chattering']}")

    # Case 2: Control signal with lower chattering (optimized boundary layer)
    print("\n[3/4] Comparing with optimized control (lower chattering)...")

    t, signal_optimized = simulate_smc_control_signal(
        duration=duration,
        dt=dt,
        chattering_frequency=30.0,
        chattering_amplitude=0.2  # Reduced amplitude
    )

    metrics_opt = compute_chattering_metrics(
        signal_optimized,
        dt=dt,
        freq_threshold=0.05,
        freq_min=10.0,
        freq_max=200.0
    )

    print(f"      Peak chattering frequency: {metrics_opt['peak_frequency']:.1f} Hz")
    print(f"      Peak amplitude: {metrics_opt['peak_amplitude']:.4f}")
    print(f"      Chattering index (RMS): {metrics_opt['chattering_index']:.4f}")
    print(f"      Total power in band: {metrics_opt['total_power']:.4f}")

    # Compute improvement
    if metrics['chattering_index'] > 0:
        reduction = (1 - metrics_opt['chattering_index'] / metrics['chattering_index']) * 100
        print(f"\n      Chattering reduction: {reduction:.1f}%")

    # Application to boundary layer optimization
    print("\n[4/4] Application to MT-6 (Boundary Layer Optimization)...")
    print("""
    The chattering metrics can be used to:

    1. Establish baseline: Measure original control signal chattering
    2. Optimize boundary layer: Adjust eps or boundary width
    3. Quantify improvement: Compare metrics before/after optimization
    4. Validate design: Ensure chattering reduction >= 30% target

    Key metrics for MT-6:
    - Peak frequency: Identifies dominant oscillation
    - Chattering index: Quantifies overall high-frequency power
    - Total power: Used for energy-based optimization

    Next steps:
    - Apply adaptive boundary layer in MT-6
    - Measure metrics at different boundary layer values
    - Find optimal eps that minimizes chattering index
    """)

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    demo_chattering_analysis()
