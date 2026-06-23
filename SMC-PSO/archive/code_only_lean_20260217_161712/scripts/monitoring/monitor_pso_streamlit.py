#!/usr/bin/env python3
"""
Real-Time PSO Optimization Monitoring Dashboard

Monitors PSO gain tuning progress via Streamlit web interface.
Parses log file and result JSON files to display:
- Current optimization status (which controller running)
- Live progress bars and iteration counts
- PSO convergence curves (updated in real-time)
- Best gains found so far
- Estimated time remaining

Usage:
    # Terminal 1: Start PSO optimization
    python scripts/lt7_robust_pso_tuning.py --all

    # Terminal 2: Launch monitoring dashboard
    streamlit run scripts/monitor_pso_streamlit.py

    # Opens browser at http://localhost:8501
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "optimization_results" / "lt7_robust_tuning.log"
RESULTS_DIR = PROJECT_ROOT / "optimization_results"

# Controller names
CONTROLLERS = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']


@dataclass
class ControllerStatus:
    """Status of a single controller optimization."""
    name: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    current_iteration: int
    total_iterations: int
    best_cost: Optional[float]
    best_gains: Optional[List[float]]
    gain_names: Optional[List[str]]
    convergence_history: List[float]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    optimization_time_minutes: Optional[float]


def parse_log_file(log_path: Path) -> Dict[str, ControllerStatus]:
    """
    Parse PSO log file to extract current status of all controllers.

    Returns:
        Dictionary mapping controller name to ControllerStatus
    """
    if not log_path.exists():
        return {ctrl: ControllerStatus(
            name=ctrl, status='pending', current_iteration=0, total_iterations=200,
            best_cost=None, best_gains=None, gain_names=None, convergence_history=[],
            start_time=None, end_time=None, optimization_time_minutes=None
        ) for ctrl in CONTROLLERS}

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    statuses = {}

    for ctrl in CONTROLLERS:
        status = ControllerStatus(
            name=ctrl,
            status='pending',
            current_iteration=0,
            total_iterations=200,
            best_cost=None,
            best_gains=None,
            gain_names=None,
            convergence_history=[],
            start_time=None,
            end_time=None,
            optimization_time_minutes=None
        )

        # Check if controller optimization started
        start_pattern = rf"Starting Robust PSO Tuning: {ctrl}"
        if re.search(start_pattern, log_content):
            status.status = 'running'

            # Extract start time
            start_match = re.search(rf"(\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}}),\d{{3}} - INFO - .*{start_pattern}", log_content)
            if start_match:
                status.start_time = datetime.strptime(start_match.group(1), "%Y-%m-%d %H:%M:%S")

        # Check if controller optimization completed
        complete_pattern = rf"PSO Optimization Complete!.*?Best cost: ([\d.]+).*?Best gains:"
        complete_match = re.search(complete_pattern, log_content, re.DOTALL)
        if complete_match:
            status.status = 'completed'
            status.best_cost = float(complete_match.group(1))

            # Extract end time
            end_match = re.search(rf"(\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}}),\d{{3}} - INFO - .*PSO Optimization Complete!", log_content)
            if end_match:
                status.end_time = datetime.strptime(end_match.group(1), "%Y-%m-%d %H:%M:%S")

        # Check if failed
        fail_pattern = rf"Failed to optimize {ctrl}"
        if re.search(fail_pattern, log_content):
            status.status = 'failed'

        # Extract total iterations
        iter_pattern = rf"({ctrl}).*?(\d+) particles, (\d+) iterations"
        iter_match = re.search(iter_pattern, log_content)
        if iter_match:
            status.total_iterations = int(iter_match.group(3))

        # Extract current iteration from PySwarms verbose output
        # PySwarms prints: "Iteration 125/200 | cost: 12.345"
        iter_progress_pattern = rf"Iteration (\d+)/{status.total_iterations}"
        iter_matches = re.findall(iter_progress_pattern, log_content)
        if iter_matches:
            status.current_iteration = int(iter_matches[-1])  # Most recent

        statuses[ctrl] = status

    return statuses


def load_result_json(controller: str) -> Optional[Dict]:
    """Load saved JSON results for a controller if available."""
    # Try standard filename first
    json_path = RESULTS_DIR / f"lt7_{controller}_robust_gains.json"
    if json_path.exists():
        with open(json_path, 'r') as f:
            return json.load(f)

    # Try timestamped filenames
    json_files = list(RESULTS_DIR.glob(f"lt7_{controller}_robust_*.json"))
    if json_files:
        # Get most recent
        latest = max(json_files, key=lambda p: p.stat().st_mtime)
        with open(latest, 'r') as f:
            return json.load(f)

    return None


def update_status_from_json(status: ControllerStatus) -> ControllerStatus:
    """Update status with data from saved JSON results."""
    result = load_result_json(status.name)
    if result:
        status.best_cost = result.get('best_cost')
        status.best_gains = result.get('best_gains')
        status.gain_names = result.get('gain_names')
        status.convergence_history = result.get('cost_history', [])
        status.optimization_time_minutes = result.get('optimization_time_minutes')
        if status.status == 'running':
            status.status = 'completed'  # JSON exists means it completed

    return status


def plot_convergence(history: List[float], controller_name: str) -> plt.Figure:
    """Generate PSO convergence plot."""
    fig, ax = plt.subplots(figsize=(10, 5))

    if history:
        ax.plot(history, 'b-', linewidth=2, label='Global best cost')
        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Cost', fontsize=12)
        ax.set_title(f'PSO Convergence - {controller_name}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_yscale('log')
    else:
        ax.text(0.5, 0.5, 'No convergence data yet',
                ha='center', va='center', fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    plt.tight_layout()
    return fig


def estimate_time_remaining(status: ControllerStatus) -> Optional[str]:
    """Estimate time remaining for current controller."""
    if status.status != 'running' or status.current_iteration == 0:
        return None

    if not status.start_time:
        return None

    elapsed = (datetime.now() - status.start_time).total_seconds()
    iter_time = elapsed / status.current_iteration  # seconds per iteration
    remaining_iters = status.total_iterations - status.current_iteration
    remaining_seconds = iter_time * remaining_iters

    return str(timedelta(seconds=int(remaining_seconds)))


def main():
    st.set_page_config(
        page_title="PSO Optimization Monitor",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🔧 PSO Gain Tuning Monitor")
    st.markdown("**Real-time monitoring of controller gain optimization (LT-7)**")

    # Sidebar controls
    st.sidebar.header("Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 3)

    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()

    # Parse log file
    statuses = parse_log_file(LOG_FILE)

    # Update with JSON results if available
    for ctrl, status in statuses.items():
        statuses[ctrl] = update_status_from_json(status)

    # Overall progress
    st.header("📈 Overall Progress")

    completed = sum(1 for s in statuses.values() if s.status == 'completed')
    running = sum(1 for s in statuses.values() if s.status == 'running')
    failed = sum(1 for s in statuses.values() if s.status == 'failed')
    pending = sum(1 for s in statuses.values() if s.status == 'pending')

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✅ Completed", completed)
    col2.metric("▶️ Running", running)
    col3.metric("❌ Failed", failed)
    col4.metric("⏳ Pending", pending)

    overall_progress = completed / len(CONTROLLERS)
    st.progress(overall_progress, text=f"{completed}/{len(CONTROLLERS)} controllers optimized")

    # Individual controller status
    st.header("🎯 Controller Status")

    for ctrl, status in statuses.items():
        with st.expander(f"**{ctrl}** - {status.status.upper()}", expanded=(status.status == 'running')):

            # Status indicators
            if status.status == 'completed':
                st.success("✅ Optimization completed")
            elif status.status == 'running':
                st.info("▶️ Optimization in progress...")
            elif status.status == 'failed':
                st.error("❌ Optimization failed")
            else:
                st.warning("⏳ Waiting to start...")

            # Progress bar
            if status.total_iterations > 0:
                progress = status.current_iteration / status.total_iterations
                st.progress(progress, text=f"Iteration {status.current_iteration}/{status.total_iterations}")

            # Time estimates
            if status.status == 'running':
                time_remaining = estimate_time_remaining(status)
                if time_remaining:
                    st.metric("⏱️ Estimated Time Remaining", time_remaining)

            if status.optimization_time_minutes:
                st.metric("⏱️ Total Optimization Time", f"{status.optimization_time_minutes:.1f} minutes")

            # Best cost
            if status.best_cost is not None:
                st.metric("🏆 Best Cost", f"{status.best_cost:.6f}")

            # Best gains
            if status.best_gains and status.gain_names:
                st.subheader("🎛️ Optimized Gains")
                gains_df = pd.DataFrame({
                    'Parameter': status.gain_names,
                    'Value': [f"{g:.4f}" for g in status.best_gains]
                })
                st.dataframe(gains_df, use_container_width=True, hide_index=True)

            # Convergence plot
            if status.convergence_history:
                st.subheader("📉 Convergence Curve")
                fig = plot_convergence(status.convergence_history, ctrl)
                st.pyplot(fig)
                plt.close(fig)

    # Log file preview
    with st.expander("📄 Log File (Last 50 Lines)"):
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            st.text("".join(lines[-50:]))
        else:
            st.warning("Log file not found")

    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
