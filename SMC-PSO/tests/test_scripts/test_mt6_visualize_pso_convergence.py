from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mt6_visualize_pso_convergence as mt6_viz


def test_load_pso_history_reads_csv(tmp_path):
    df = pd.DataFrame(
        {
            "iteration": [0, 1, 2],
            "epsilon_min": [0.02, 0.018, 0.015],
            "alpha": [0.5, 0.55, 0.6],
            "best_fitness": [1.0, 0.7, 0.5],
            "mean_fitness": [1.2, 0.8, 0.6],
        }
    )
    csv_path = tmp_path / "history.csv"
    df.to_csv(csv_path, index=False)

    loaded = mt6_viz.load_pso_history(csv_path)

    assert list(loaded.columns) == list(df.columns)
    assert len(loaded) == len(df)


def test_plot_mt6_pso_convergence_creates_artifact(tmp_path):
    iterations = np.arange(6)
    history = pd.DataFrame(
        {
            "iteration": iterations,
            "best_fitness": np.linspace(1.0, 0.2, len(iterations)),
            "epsilon_min": np.linspace(0.02, 0.01, len(iterations)),
            "alpha": np.linspace(0.5, 0.9, len(iterations)),
            "mean_fitness": np.linspace(1.1, 0.3, len(iterations)),
        }
    )

    output = tmp_path / "plot.png"
    mt6_viz.plot_mt6_pso_convergence(history, save_path=output, show=False)

    assert output.exists()
    assert output.stat().st_size > 0
    assert plt.get_fignums() == []
