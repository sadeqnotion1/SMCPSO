"""
scripts/generate_advisor_figures.py
====================================
Generate all publication-quality figures for academic/paper/advisor_progress_report.tex.

Figures produced
----------------
fig01_trajectory_angles.png     -- theta1, theta2 time-domain, all controllers
fig02_trajectory_control.png    -- control signal u(t), all controllers (chattering)
fig03_sliding_surface.png       -- sliding surface sigma(t), classical vs STA
fig04_boundary_layer.png        -- fixed vs adaptive boundary layer comparison
fig05_pso_seed_variance.png     -- MT-7 PSO chattering index per seed
fig06_disturbance_effort.png    -- control effort increase under disturbances
fig07_radar_comparison.png      -- spider chart, 5 metrics, all controllers
fig08_mc_chattering.png         -- MT-6 chattering: fixed vs adaptive bar chart
fig09_generalization_gap.png    -- MT-6 vs MT-7 chattering comparison (bar)

Run from repo root:
    python scripts/generate_advisor_figures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT_DIR = REPO_ROOT / "academic" / "paper" / "experiments" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- color palette ---
COLORS = {
    "classical_smc": "#1f77b4",
    "sta_smc":        "#ff7f0e",
    "adaptive_smc":   "#2ca02c",
    "hybrid":         "#d62728",
}
LABELS = {
    "classical_smc": "Classical SMC",
    "sta_smc":        "STA-SMC",
    "adaptive_smc":   "Adaptive SMC",
    "hybrid":         "Hybrid Adaptive STA",
}

DPI = 300
FONT = {"family": "serif", "size": 9}
matplotlib.rc("font", **FONT)
matplotlib.rc("axes", titlesize=9, labelsize=8)
matplotlib.rc("xtick", labelsize=7)
matplotlib.rc("ytick", labelsize=7)
matplotlib.rc("legend", fontsize=7)


# ===========================================================================
# Helpers
# ===========================================================================

def _save(fig: plt.Figure, name: str) -> None:
    path = OUT_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {name}")


def _load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _load_gains(ctrl_key: str) -> list:
    """Load MT-8 robust gains for a controller."""
    exp = REPO_ROOT / "academic" / "paper" / "experiments"
    dirs = {
        "classical_smc": exp / "classical_smc" / "optimization" / "active" / "mt8_repro_seed42_classical_smc.json",
        "sta_smc":        exp / "sta_smc" / "optimization" / "active" / "mt8_repro_seed42_sta_smc.json",
        "adaptive_smc":   exp / "adaptive_smc" / "optimization" / "active" / "mt8_repro_seed42_adaptive_smc.json",
        "hybrid":         exp / "hybrid_adaptive_sta" / "optimization" / "active" / "mt8_repro_seed42_hybrid_adaptive_sta_smc.json",
    }
    d = _load_json(dirs[ctrl_key])
    return d["gains"]


def _run_sim(ctrl_name: str, gains: list, ic: np.ndarray,
             duration: float = 5.0, dt: float = 0.01) -> tuple:
    """Run one simulation; returns (t, x, u) or None on failure."""
    try:
        from src.core.simulation_context import SimulationContext
        from src.core.simulation_runner import run_simulation

        ctx = SimulationContext(str(REPO_ROOT / "config.yaml"))
        # Pass gains directly at controller creation time
        ctrl = ctx.create_controller(ctrl_name, gains=gains)
        dyn = ctx.get_dynamics_model()
        t, x, u = run_simulation(
            controller=ctrl,
            dynamics_model=dyn,
            sim_time=duration,
            dt=dt,
            initial_state=ic,
        )
        return t, x, u
    except Exception as exc:
        print(f"[WARNING] simulation failed for {ctrl_name}: {exc}")
        return None


# ===========================================================================
# Figure 01: Time-domain angles
# ===========================================================================

def fig01_trajectory_angles() -> None:
    ic = np.array([0.0, 0.15, 0.0, 0.10, 0.0, 0.0])
    ctrl_map = {
        "classical_smc": "classical_smc",
        "sta_smc":        "sta_smc",
        "adaptive_smc":   "adaptive_smc",
        "hybrid":         "hybrid_adaptive_sta_smc",
    }

    fig, axes = plt.subplots(2, 1, figsize=(5.5, 4.5), sharex=True)
    ax1, ax2 = axes

    got_any = False
    for key, sim_name in ctrl_map.items():
        gains = _load_gains(key)
        res = _run_sim(sim_name, gains, ic)
        if res is None:
            continue
        t, x, _ = res
        theta1 = x[:, 1]
        theta2 = x[:, 3]
        ax1.plot(t, np.degrees(theta1), color=COLORS[key], label=LABELS[key], lw=0.9)
        ax2.plot(t, np.degrees(theta2), color=COLORS[key], lw=0.9)
        got_any = True

    if not got_any:
        plt.close(fig)
        print("[WARNING] fig01 skipped -- no simulations succeeded")
        return

    ax1.axhline(0, color="k", lw=0.5, ls="--")
    ax2.axhline(0, color="k", lw=0.5, ls="--")
    ax1.set_ylabel(r"$\theta_1$ (deg)")
    ax2.set_ylabel(r"$\theta_2$ (deg)")
    ax2.set_xlabel("Time (s)")
    ax1.set_title("Link angles from initial condition "
                  r"$\theta_1=0.15$, $\theta_2=0.10$ rad")
    ax1.legend(loc="upper right", ncol=2)
    ax1.grid(True, ls="--", alpha=0.4)
    ax2.grid(True, ls="--", alpha=0.4)
    fig.tight_layout(pad=0.5)
    _save(fig, "fig01_trajectory_angles.png")


# ===========================================================================
# Figure 02: Control signal (chattering)
# ===========================================================================

def fig02_trajectory_control() -> None:
    ic = np.array([0.0, 0.15, 0.0, 0.10, 0.0, 0.0])
    ctrl_map = {
        "classical_smc": "classical_smc",
        "sta_smc":        "sta_smc",
        "adaptive_smc":   "adaptive_smc",
        "hybrid":         "hybrid_adaptive_sta_smc",
    }

    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.5), sharex=True, sharey=True)
    axes_flat = axes.flatten()

    for idx, (key, sim_name) in enumerate(ctrl_map.items()):
        ax = axes_flat[idx]
        gains = _load_gains(key)
        res = _run_sim(sim_name, gains, ic)
        if res is None:
            ax.set_title(LABELS[key] + " [FAIL]")
            continue
        t, x, u = res
        # Align u length with t
        t_u = t[: len(u)]
        ax.plot(t_u, u, color=COLORS[key], lw=0.7)
        ax.set_title(LABELS[key], fontsize=8)
        ax.axhline(0, color="k", lw=0.4, ls="--")
        ax.grid(True, ls="--", alpha=0.35)

    for ax in axes[1]:
        ax.set_xlabel("Time (s)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Control force u (N)")

    fig.suptitle("Control signal u(t) -- chattering comparison", fontsize=9)
    fig.tight_layout(pad=0.5)
    _save(fig, "fig02_trajectory_control.png")


# ===========================================================================
# Figure 03: Sliding surface
# ===========================================================================

def fig03_sliding_surface() -> None:
    ic = np.array([0.0, 0.15, 0.0, 0.10, 0.0, 0.0])

    # Only classical and STA -- they have well-defined sigma
    ctrl_map = {
        "classical_smc": "classical_smc",
        "sta_smc":        "sta_smc",
    }

    fig, ax = plt.subplots(figsize=(5.0, 3.0))

    for key, sim_name in ctrl_map.items():
        gains = _load_gains(key)
        res = _run_sim(sim_name, gains, ic)
        if res is None:
            continue
        t, x, _ = res
        # Compute sigma = lambda1 * theta1 + theta1_dot + lambda2 * theta2 + theta2_dot
        # Use gains[2], gains[3] as lambda1, lambda2 (indices for classical/STA)
        lam1 = gains[2] if len(gains) > 2 else 5.0
        lam2 = gains[3] if len(gains) > 3 else 3.0
        sigma = lam1 * x[:, 1] + x[:, 2] + lam2 * x[:, 3] + x[:, 4]
        ax.plot(t, sigma, color=COLORS[key], label=LABELS[key], lw=0.9)

    ax.axhline(0, color="k", lw=0.5, ls="--")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Sliding surface $\sigma$")
    ax.set_title(r"Sliding surface convergence: $\sigma \to 0$")
    ax.legend()
    ax.grid(True, ls="--", alpha=0.4)
    fig.tight_layout(pad=0.5)
    _save(fig, "fig03_sliding_surface.png")


# ===========================================================================
# Figure 04: Boundary layer -- fixed vs adaptive (MT-6 data)
# ===========================================================================

def fig04_boundary_layer() -> None:
    # Data from MT6_fixed_baseline_summary.json and MT6_adaptive_summary.json
    categories = ["Fixed\n(eps=0.02)", "Adaptive\n(eps_min=0.0025, alpha=1.21)"]

    chattering_mean = [6.37, 2.14]
    chattering_ci   = [0.24, 0.027]   # half-width 95% CI
    overshoot_mean  = [5.36, 4.61]
    overshoot_ci    = [0.06, 0.09]

    x = np.arange(len(categories))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 3.0))

    bars1 = ax1.bar(x, chattering_mean, width, yerr=chattering_ci,
                    color=["#1f77b4", "#ff7f0e"], capsize=4, alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=7)
    ax1.set_ylabel("Chattering index")
    ax1.set_title("Chattering: fixed vs adaptive\nboundary layer (100 runs)")
    ax1.grid(True, ls="--", alpha=0.35, axis="y")

    ax1.annotate("p < 0.001\n(Cohen d = 5.29)", xy=(0.5, 0.88),
                 xycoords="axes fraction", ha="center", fontsize=7,
                 bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray", lw=0.5))

    bars2 = ax2.bar(x, overshoot_mean, width, yerr=overshoot_ci,
                    color=["#1f77b4", "#ff7f0e"], capsize=4, alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=7)
    ax2.set_ylabel(r"Overshoot $\theta_1$ (%)")
    ax2.set_title(r"Overshoot ($\theta_1$): fixed vs adaptive")
    ax2.grid(True, ls="--", alpha=0.35, axis="y")

    fig.tight_layout(pad=0.8)
    _save(fig, "fig04_boundary_layer.png")


# ===========================================================================
# Figure 05: MT-7 PSO seed variance
# ===========================================================================

def fig05_pso_seed_variance() -> None:
    path = (REPO_ROOT / "academic" / "paper" / "experiments" / "comparative" /
            "pso_robustness" / "MT7_robustness_summary.json")
    data = _load_json(path)

    seeds = sorted(data["per_seed_statistics"].keys(), key=int)
    means = [data["per_seed_statistics"][s]["mean"] for s in seeds]
    stds  = [data["per_seed_statistics"][s]["std"]  for s in seeds]

    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    xs = np.arange(len(seeds))
    ax.bar(xs, means, yerr=stds, color="#1f77b4", alpha=0.8, capsize=4,
           error_kw={"elinewidth": 0.8})
    ax.axhline(data["global_statistics"]["mean"], color="#d62728", lw=1.2,
               ls="--", label=f'Global mean = {data["global_statistics"]["mean"]:.1f}')
    ax.fill_between([-0.5, len(seeds) - 0.5],
                    data["global_statistics"]["p95"],
                    data["global_statistics"]["p95"],
                    alpha=0, label=f'p95 = {data["global_statistics"]["p95"]:.1f}')
    ax.set_xticks(xs)
    ax.set_xticklabels([f"Seed {s}" for s in seeds], rotation=30, ha="right")
    ax.set_ylabel("Chattering index (mean per seed)")
    ax.set_title("MT-7 PSO robustness: chattering index across 10 random seeds\n"
                 "(challenging ICs, +/-0.3 rad)")
    ax.legend(fontsize=7)
    ax.grid(True, ls="--", alpha=0.35, axis="y")
    fig.tight_layout(pad=0.5)
    _save(fig, "fig05_pso_seed_variance.png")


# ===========================================================================
# Figure 06: Disturbance rejection -- control effort increase (MT-8)
# ===========================================================================

def fig06_disturbance_effort() -> None:
    path = (REPO_ROOT / "academic" / "paper" / "experiments" / "comparative" /
            "disturbance_rejection" / "MT8_disturbance_rejection.json")
    data = _load_json(path)

    ctrl_names = ["classical_smc", "sta_smc", "adaptive_smc", "hybrid_adaptive_sta_smc"]
    dist_types = ["step", "impulse", "sinusoidal", "random"]
    ctrl_labels = ["Classical SMC", "STA-SMC", "Adaptive SMC", "Hybrid"]

    # Build matrix: rows = controllers, cols = disturbance types
    effort = np.zeros((len(ctrl_names), len(dist_types)))
    for entry in data["results"]:
        ci = ctrl_names.index(entry["controller_name"])
        di = dist_types.index(entry["disturbance_type"])
        effort[ci, di] = entry["control_effort_increase_pct"]

    x = np.arange(len(dist_types))
    width = 0.18
    offsets = np.linspace(-1.5 * width, 1.5 * width, len(ctrl_names))

    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    for i, (ctrl, lbl) in enumerate(zip(ctrl_names, ctrl_labels)):
        color = COLORS.get(ctrl, COLORS.get("hybrid", "#d62728"))
        ax.bar(x + offsets[i], effort[i], width, label=lbl,
               color=color, alpha=0.85)

    ax.axhline(0, color="k", lw=0.6, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in dist_types])
    ax.set_ylabel("Control effort increase (%)")
    ax.set_title("Control effort change under external disturbances (MT-8)")
    ax.legend(ncol=2, fontsize=7)
    ax.grid(True, ls="--", alpha=0.35, axis="y")
    fig.tight_layout(pad=0.5)
    _save(fig, "fig06_disturbance_effort.png")


# ===========================================================================
# Figure 07: Radar / spider chart
# ===========================================================================

def fig07_radar_comparison() -> None:
    """Multi-metric radar chart.

    Values are normalised so that 1.0 = best, 0.0 = worst for each metric.
    Source: document Section 5 tables (manually extracted).
    """
    categories = [
        "Settling\ntime",
        "Overshoot",
        "Chattering",
        "Energy\nefficiency",
        "Disturbance\nrejection",
    ]
    N = len(categories)

    # Raw values (lower is better for all raw metrics)
    # [settling_s, overshoot_pct, chattering_idx, energy_N2s, effort_inc_pct_step]
    raw = {
        "classical_smc": [2.15, 3.2,  2.80, 127.0,  64.4],
        "sta_smc":        [1.82, 2.8,  2.14, 189.0,   3.9],
        "adaptive_smc":   [1.96, 3.0,  2.18, 193.0,   3.9],
        "hybrid":         [2.03, 3.5, 12.50, 310.0, 136.0],
    }

    # Normalise: 1.0 = best (lowest raw), 0.0 = worst (highest raw)
    keys = list(raw.keys())
    arr = np.array([raw[k] for k in keys], dtype=float)  # shape (4, 5)
    col_min = arr.min(axis=0)
    col_max = arr.max(axis=0)
    normed = 1.0 - (arr - col_min) / np.where(col_max - col_min > 0, col_max - col_min, 1.0)

    # Angles for radar
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))

    ctrl_colors = [COLORS[k] for k in keys]
    ctrl_labels_list = [LABELS[k] for k in keys]

    for i, (key, lbl, col) in enumerate(zip(keys, ctrl_labels_list, ctrl_colors)):
        vals = normed[i].tolist() + [normed[i, 0]]
        ax.plot(angles, vals, color=col, lw=1.2, label=lbl)
        ax.fill(angles, vals, color=col, alpha=0.1)

    ax.set_thetagrids(np.degrees(angles[:-1]), categories)
    ax.set_ylim(0, 1)
    ax.set_title("Multi-metric comparison (normalised,\nhigher = better)", pad=14, fontsize=9)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=7)
    fig.tight_layout(pad=0.3)
    _save(fig, "fig07_radar_comparison.png")


# ===========================================================================
# Figure 08: Chattering bar chart -- MT-6 fixed vs adaptive
# ===========================================================================

def fig08_mc_chattering() -> None:
    """Bar chart for chattering index: fixed vs adaptive boundary layer."""
    labels = ["Fixed\nboundary layer", "Adaptive\nboundary layer"]
    means  = [6.37, 2.14]
    ci_lo  = [6.13, 2.11]
    ci_hi  = [6.61, 2.16]
    err    = [[m - lo for m, lo in zip(means, ci_lo)],
              [hi - m for m, hi in zip(means, ci_hi)]]

    fig, ax = plt.subplots(figsize=(3.8, 3.0))
    ax.bar([0, 1], means, yerr=err, color=["#1f77b4", "#ff7f0e"],
           capsize=5, alpha=0.85, error_kw={"elinewidth": 0.9})
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Chattering index (mean, 100 runs)")
    ax.set_title("MT-6 Boundary layer study:\n66.5% chattering reduction (p<0.001)")
    ax.annotate("66.5%\nreduction", xy=(0.5, 0.55), xycoords="axes fraction",
                ha="center", fontsize=9, color="darkred",
                arrowprops=None)
    ax.grid(True, ls="--", alpha=0.35, axis="y")
    fig.tight_layout(pad=0.5)
    _save(fig, "fig08_mc_chattering.png")


# ===========================================================================
# Figure 09: MT-6 vs MT-7 generalisation gap
# ===========================================================================

def fig09_generalization_gap() -> None:
    path = (REPO_ROOT / "academic" / "paper" / "experiments" / "comparative" /
            "pso_robustness" / "MT7_statistical_comparison.json")
    data = _load_json(path)

    cmp = data["comparison"]
    labels = ["MT-6 (easy ICs,\n+/-0.05 rad)", "MT-7 (challenging\n+/-0.30 rad)"]
    means  = [cmp["mt6_mean"], cmp["mt7_mean"]]
    ci_lo  = [cmp["mt6_ci_lower"], cmp["mt7_ci_lower"]]
    ci_hi  = [cmp["mt6_ci_upper"], cmp["mt7_ci_upper"]]
    err    = [[m - lo for m, lo in zip(means, ci_lo)],
              [hi - m for m, hi in zip(means, ci_hi)]]

    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.bar([0, 1], means, yerr=err, color=["#2ca02c", "#d62728"],
           capsize=5, alpha=0.85, error_kw={"elinewidth": 0.9})
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Chattering index")
    ax.set_title(f"PSO generalisation gap\n"
                 f"(50.4x degradation, p<0.001, Cohen d={abs(cmp['cohens_d']):.1f})")
    ax.grid(True, ls="--", alpha=0.35, axis="y")
    fig.tight_layout(pad=0.5)
    _save(fig, "fig09_generalization_gap.png")


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    print("Generating advisor report figures ...")
    print(f"Output: {OUT_DIR}\n")

    # Data-only figures first (no simulation needed)
    fig04_boundary_layer()
    fig05_pso_seed_variance()
    fig06_disturbance_effort()
    fig07_radar_comparison()
    fig08_mc_chattering()
    fig09_generalization_gap()

    # Simulation-dependent figures
    fig01_trajectory_angles()
    fig02_trajectory_control()
    fig03_sliding_surface()

    print("\nDone. Check academic/paper/experiments/figures/ for output files.")


if __name__ == "__main__":
    main()
