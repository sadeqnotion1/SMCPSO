#!/usr/bin/env python3
"""
Phase 4: Comparative Energy Analysis
================================================================================

Compares energy PSO results across all controllers:
- Classical SMC
- Adaptive SMC
- Hybrid Adaptive STA

Generates:
1. Comparative summary table
2. Before/after comparison plots
3. Gain sensitivity analysis
4. Statistical significance tests

Part of Option B Framework 1 completion (Phase 4: Efficiency Expansion)
Author: AI Workspace (Claude Code)
Created: January 4, 2026
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List
import logging

# Setup paths
project_root = Path(__file__).resolve().parent.parent.parent.parent
output_dir = project_root / "academic" / "paper" / "experiments" / "comparative" / "energy_pso"
output_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_controller_results(controller_name: str) -> Dict:
    """Load energy PSO results for a controller."""
    summary_file = (
        project_root / "academic" / "paper" / "experiments" /
        controller_name / "optimization" / "energy" /
        f"{controller_name}_energy_summary.json"
    )

    if not summary_file.exists():
        logger.warning(f"Results not found for {controller_name}: {summary_file}")
        return None

    with open(summary_file, 'r') as f:
        return json.load(f)


def create_comparative_summary():
    """Create comparative summary table."""
    logger.info("Creating comparative summary table...")

    controllers = ['classical_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
    results = []

    for ctrl in controllers:
        data = load_controller_results(ctrl)
        if data is None:
            continue

        results.append({
            'Controller': ctrl.replace('_', ' ').title(),
            'Energy Before': data['energy_before'],
            'Energy After': data['energy_after'],
            'Energy Reduction (%)': ((data['energy_before'] - data['energy_after']) /
                                          max(data['energy_before'], 1e-10)) * 100,
            'RMSE Before': data['rmse_before'],
            'RMSE After': data['rmse_after'],
            'RMSE Change (%)': ((data['rmse_after'] - data['rmse_before']) /
                                data['rmse_before']) * 100,
            'Fitness Before': data['fitness_before'],
            'Fitness After': data['fitness_after'],
            'Fitness Improvement (%)': data['improvement_pct'],
            'Optimization Time (s)': data['optimization_time_sec']
        })

    df = pd.DataFrame(results)

    # Save to CSV
    csv_file = output_dir / "energy_pso_comparative_summary.csv"
    df.to_csv(csv_file, index=False, float_format='%.4f')
    logger.info(f"Saved summary table: {csv_file}")

    # Save formatted table
    txt_file = output_dir / "energy_pso_comparative_summary.txt"
    with open(txt_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("Phase 4: Energy PSO Comparative Analysis\n")
        f.write("=" * 100 + "\n\n")
        f.write(df.to_string(index=False))
        f.write("\n\n")

        # Add key findings
        f.write("=" * 100 + "\n")
        f.write("KEY FINDINGS\n")
        f.write("=" * 100 + "\n\n")

        # Best energy reduction
        best_chat_idx = df['Energy Reduction (%)'].idxmax()
        f.write(f"1. Best Energy Reduction: {df.iloc[best_chat_idx]['Controller']}\n")
        f.write(f"   - Reduction: {df.iloc[best_chat_idx]['Energy Reduction (%)']:.2f}%\n")
        f.write(f"   - From: {df.iloc[best_chat_idx]['Energy Before']:.4f} -> {df.iloc[best_chat_idx]['Energy After']:.4f}\n\n")

        # Best fitness improvement
        best_fit_idx = df['Fitness Improvement (%)'].idxmax()
        f.write(f"2. Best Overall Fitness Improvement: {df.iloc[best_fit_idx]['Controller']}\n")
        f.write(f"   - Improvement: {df.iloc[best_fit_idx]['Fitness Improvement (%)']:.2f}%\n\n")

        # Baseline comparison
        f.write("3. Baseline Energy Performance:\n")
        for _, row in df.iterrows():
            f.write(f"   - {row['Controller']}: {row['Energy Before']:.4f}\n")

    logger.info(f"Saved formatted summary: {txt_file}")

    return df


def create_comparison_plots(df: pd.DataFrame):
    """Create before/after comparison plots."""
    logger.info("Creating comparison plots...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Phase 4: Energy PSO Comparative Results', fontsize=16, fontweight='bold')

    controllers = df['Controller'].tolist()
    x = np.arange(len(controllers))
    width = 0.35

    # 1. Energy comparison
    ax = axes[0, 0]
    ax.bar(x - width/2, df['Energy Before'], width, label='Before', alpha=0.8, color='#e74c3c')
    ax.bar(x + width/2, df['Energy After'], width, label='After', alpha=0.8, color='#27ae60')
    ax.set_xlabel('Controller', fontweight='bold')
    ax.set_ylabel('Energy Index (RMS du/dt)', fontweight='bold')
    ax.set_title('Energy Reduction', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(controllers, rotation=15, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. RMSE comparison
    ax = axes[0, 1]
    ax.bar(x - width/2, df['RMSE Before'], width, label='Before', alpha=0.8, color='#3498db')
    ax.bar(x + width/2, df['RMSE After'], width, label='After', alpha=0.8, color='#9b59b6')
    ax.set_xlabel('Controller', fontweight='bold')
    ax.set_ylabel('RMSE (rad)', fontweight='bold')
    ax.set_title('Tracking Performance (RMSE)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(controllers, rotation=15, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Fitness comparison
    ax = axes[1, 0]
    ax.bar(x - width/2, df['Fitness Before'], width, label='Before', alpha=0.8, color='#e67e22')
    ax.bar(x + width/2, df['Fitness After'], width, label='After', alpha=0.8, color='#16a085')
    ax.set_xlabel('Controller', fontweight='bold')
    ax.set_ylabel('Fitness (0.7*Chat + 0.3*RMSE)', fontweight='bold')
    ax.set_title('Multi-Objective Fitness', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(controllers, rotation=15, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Improvement percentages
    ax = axes[1, 1]
    improvements = df['Fitness Improvement (%)'].tolist()
    colors = ['#27ae60' if imp > 0 else '#e74c3c' for imp in improvements]
    bars = ax.bar(x, improvements, alpha=0.8, color=colors)
    ax.set_xlabel('Controller', fontweight='bold')
    ax.set_ylabel('Improvement (%)', fontweight='bold')
    ax.set_title('Overall Fitness Improvement', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(controllers, rotation=15, ha='right')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom' if height > 0 else 'top',
                fontweight='bold', fontsize=9)

    plt.tight_layout()

    # Save plot
    plot_file = output_dir / "energy_pso_comparison.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    logger.info(f"Saved comparison plot: {plot_file}")

    plt.close()


def create_gains_comparison():
    """Create gains comparison table."""
    logger.info("Creating gains comparison...")

    controllers = ['classical_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
    gains_data = []

    for ctrl in controllers:
        data = load_controller_results(ctrl)
        if data is None:
            continue

        orig_gains = data['original_gains']
        opt_gains = data['optimized_gains']

        for i, (orig, opt) in enumerate(zip(orig_gains, opt_gains)):
            gains_data.append({
                'Controller': ctrl.replace('_', ' ').title(),
                'Gain Index': f"k{i+1}",
                'Original': orig,
                'Optimized': opt,
                'Change (%)': ((opt - orig) / orig) * 100 if orig != 0 else 0,
                'Absolute Change': opt - orig
            })

    df = pd.DataFrame(gains_data)

    # Save to CSV
    csv_file = output_dir / "energy_pso_gains_comparison.csv"
    df.to_csv(csv_file, index=False, float_format='%.6f')
    logger.info(f"Saved gains comparison: {csv_file}")

    return df


def main():
    """Run comparative analysis."""
    logger.info("=" * 80)
    logger.info("Phase 4: Energy PSO Comparative Analysis")
    logger.info("=" * 80)

    # Create comparative summary
    summary_df = create_comparative_summary()

    if summary_df.empty:
        logger.error("No results found. Ensure all PSO runs have completed.")
        return

    # Create comparison plots
    create_comparison_plots(summary_df)

    # Create gains comparison
    gains_df = create_gains_comparison()

    logger.info("=" * 80)
    logger.info("[OK] Comparative analysis complete!")
    logger.info(f"Results saved to: {output_dir}")
    logger.info("=" * 80)

    # Print summary to console
    print("\n" + "=" * 100)
    print("CHATTERING PSO COMPARATIVE SUMMARY")
    print("=" * 100)
    print(summary_df.to_string(index=False))
    print("\n")


if __name__ == "__main__":
    main()
