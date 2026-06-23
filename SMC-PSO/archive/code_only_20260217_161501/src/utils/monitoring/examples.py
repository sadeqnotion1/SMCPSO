#!/usr/bin/env python
#======================================================================================\
#===================== src/utils/monitoring/examples.py =====================\
#======================================================================================\

"""
Usage examples for the performance monitoring system.

These examples demonstrate how to integrate the monitoring system
into simulation workflows, collect metrics, and generate reports.
"""

import numpy as np
from pathlib import Path

# Import monitoring components
from .metrics_collector_control import ControlMetricsCollector
from .visualization import PerformanceVisualizer, DataExporter
from .data_model import ComparisonData


def example_basic_monitoring():
    """
    Example 1: Basic monitoring for a single simulation run.

    Demonstrates:
    - Starting a run
    - Adding snapshots per time step
    - Computing summary metrics
    - Exporting results
    """
    print("[EXAMPLE 1] Basic Monitoring\n")

    # Initialize collector
    collector = ControlMetricsCollector(
        sampling_interval=1,  # Collect every step
        max_snapshots=10000
    )

    # Start a new run
    collector.start_run(
        run_id="test_run_001",
        controller_type="classical_smc",
        scenario="stabilization",
        config={'dt': 0.01, 'duration': 10.0}
    )

    # Simulate some data
    dt = 0.01
    duration = 10.0
    t = np.arange(0, duration, dt)

    for i, time_s in enumerate(t):
        # Simulate decaying oscillation
        theta1 = 0.2 * np.exp(-time_s/2) * np.cos(3*time_s)
        theta2 = 0.1 * np.exp(-time_s/3) * np.cos(2*time_s)
        theta1_dot = np.gradient([theta1])[0] / dt
        theta2_dot = np.gradient([theta2])[0] / dt

        state = np.array([theta1, theta2, theta1_dot, theta2_dot])

        # Simple control law
        control_output = -10*theta1 - 5*theta2 - 3*theta1_dot - 2*theta2_dot

        # Add snapshot
        collector.add_snapshot(
            state=state,
            control_output=control_output,
            time_step=i,
            timestamp_s=time_s,
            computation_time_ms=0.15  # Mock computation time
        )

    # End run and get summary
    completed_run = collector.end_run(success=True)

    print(f"Run ID: {completed_run.run_id}")
    print(f"Controller: {completed_run.controller}")
    print(f"Status: {completed_run.status.value}")
    print(f"Snapshots collected: {len(completed_run.snapshots)}\n")

    if completed_run.summary:
        print("Performance Summary:")
        print(f"  Settling Time: {completed_run.summary.settling_time_s:.2f} s")
        print(f"  Overshoot: {completed_run.summary.overshoot_pct:.1f} %")
        print(f"  Energy: {completed_run.summary.energy_j:.2f} J")
        print(f"  Score: {completed_run.summary.get_score():.1f} / 100\n")

    # Export results
    exporter = DataExporter(output_dir='.artifacts/monitoring_examples')

    csv_path = exporter.export_csv(completed_run)
    json_path = exporter.export_json(completed_run)
    report_path = exporter.export_summary_report(completed_run)

    print(f"Exported to:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Report: {report_path}\n")


def example_realtime_callbacks():
    """
    Example 2: Real-time monitoring with callbacks.

    Demonstrates:
    - Registering update callbacks
    - Real-time metric processing
    - Triggering alerts based on thresholds
    """
    print("[EXAMPLE 2] Real-Time Callbacks\n")

    collector = ControlMetricsCollector()

    # Define callback for real-time alerts
    def alert_callback(snapshot):
        """Alert if error exceeds threshold."""
        if snapshot.error_norm > 0.5:
            print(f"[ALERT] High error at t={snapshot.timestamp_s:.2f}s: {snapshot.error_norm:.4f} rad")

    # Register callback
    collector.register_update_callback(alert_callback)

    # Start run
    collector.start_run(
        run_id="realtime_test",
        controller_type="adaptive_smc",
        scenario="tracking"
    )

    # Simulate with occasional disturbance
    for i in range(100):
        t = i * 0.01
        # Inject disturbance at t=0.5s
        disturbance = 1.0 if 0.5 < t < 0.6 else 0.0

        state = np.array([0.1 * np.sin(t) + disturbance, 0.05 * np.cos(t), 0, 0])
        control = -state[0] - state[1]

        collector.add_snapshot(state, control, i, t)

    run = collector.end_run(success=True)
    print(f"\nRun complete. Total snapshots: {len(run.snapshots)}\n")


def example_comparison_analysis():
    """
    Example 3: Multi-controller comparison.

    Demonstrates:
    - Collecting data from multiple controllers
    - Generating comparison plots
    - Ranking controllers by performance
    """
    print("[EXAMPLE 3] Multi-Controller Comparison\n")

    comparison = ComparisonData(comparison_id="benchmark_001")

    controllers = ['classical_smc', 'sta_smc', 'adaptive_smc']

    for ctrl in controllers:
        collector = ControlMetricsCollector()
        collector.start_run(f"run_{ctrl}", ctrl, "stabilization")

        # Simulate different performance profiles
        performance_factor = {'classical_smc': 1.0, 'sta_smc': 0.8, 'adaptive_smc': 0.9}[ctrl]

        for i in range(500):
            t = i * 0.01
            theta1 = 0.2 * performance_factor * np.exp(-t/2) * np.cos(3*t)
            theta2 = 0.1 * performance_factor * np.exp(-t/3) * np.cos(2*t)
            state = np.array([theta1, theta2, 0, 0])
            control = -10*theta1 - 5*theta2

            collector.add_snapshot(state, control, i, t)

        run = collector.end_run(success=True)
        comparison.add_run(run)

    # Get rankings
    print("Controller Rankings (by score):")
    for rank, (ctrl, score) in enumerate(comparison.get_ranking('score'), 1):
        print(f"  {rank}. {ctrl}: {score:.1f}")

    print("\nController Rankings (by settling time):")
    for rank, (ctrl, time_val) in enumerate(comparison.get_ranking('settling_time_s'), 1):
        print(f"  {rank}. {ctrl}: {time_val:.2f} s")

    # Generate comparison plot
    visualizer = PerformanceVisualizer()
    fig = visualizer.plot_controller_comparison(
        comparison,
        metric='score',
        save_path='.artifacts/monitoring_examples/comparison.png'
    )
    print("\nComparison plot saved to .artifacts/monitoring_examples/comparison.png\n")


def example_visualization():
    """
    Example 4: Creating visualizations.

    Demonstrates:
    - Time series plots
    - Performance summary plots
    - Interactive Plotly dashboards
    """
    print("[EXAMPLE 4] Visualization\n")

    # Collect some data
    collector = ControlMetricsCollector()
    collector.start_run("viz_test", "hybrid_adaptive_sta_smc", "stabilization")

    for i in range(1000):
        t = i * 0.01
        theta1 = 0.3 * np.exp(-t) * np.sin(5*t)
        theta2 = 0.15 * np.exp(-t*0.8) * np.cos(4*t)
        state = np.array([theta1, theta2, 0, 0])
        control = -15*theta1 - 8*theta2

        collector.add_snapshot(state, control, i, t)

    run = collector.end_run(success=True)

    # Create visualizer
    visualizer = PerformanceVisualizer()

    # 1. Time series plot
    fig1 = visualizer.plot_time_series(
        run,
        metrics=['angle1', 'angle2', 'control', 'error_norm'],
        save_path='.artifacts/monitoring_examples/timeseries.png'
    )
    print("Time series plot saved")

    # 2. Performance summary
    fig2 = visualizer.plot_performance_summary(
        run,
        save_path='.artifacts/monitoring_examples/summary.png'
    )
    print("Performance summary saved")

    # 3. Interactive plot (Plotly)
    fig3 = visualizer.create_interactive_plot(run)
    fig3.write_html('.artifacts/monitoring_examples/interactive.html')
    print("Interactive HTML dashboard saved\n")


def example_export_formats():
    """
    Example 5: Exporting data in multiple formats.

    Demonstrates:
    - CSV export for numerical analysis
    - JSON export for data exchange
    - Text summary reports
    """
    print("[EXAMPLE 5] Multiple Export Formats\n")

    collector = ControlMetricsCollector()
    collector.start_run("export_test", "mpc_controller", "tracking")

    # Simulate tracking scenario
    for i in range(500):
        t = i * 0.01
        setpoint = 0.1 * np.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz reference
        theta1 = setpoint + 0.02 * np.exp(-t) * np.sin(10*t)
        state = np.array([theta1, 0, 0, 0])
        control = 10 * (setpoint - theta1)

        collector.add_snapshot(state, control, i, t)

    run = collector.end_run(success=True)

    # Export to all formats
    exporter = DataExporter(output_dir='.artifacts/monitoring_examples/exports')

    csv_file = exporter.export_csv(run)
    json_file = exporter.export_json(run)
    report_file = exporter.export_summary_report(run)

    print(f"Exported to:")
    print(f"  CSV:    {csv_file}")
    print(f"  JSON:   {json_file}")
    print(f"  Report: {report_file}\n")


def run_all_examples():
    """Run all examples sequentially."""
    print("=" * 80)
    print("PERFORMANCE MONITORING SYSTEM - USAGE EXAMPLES")
    print("=" * 80)
    print()

    example_basic_monitoring()
    print("-" * 80)
    print()

    example_realtime_callbacks()
    print("-" * 80)
    print()

    example_comparison_analysis()
    print("-" * 80)
    print()

    example_visualization()
    print("-" * 80)
    print()

    example_export_formats()
    print("-" * 80)
    print()

    print("All examples completed successfully!")
    print("Check .artifacts/monitoring_examples/ for generated files.")


if __name__ == "__main__":
    run_all_examples()
