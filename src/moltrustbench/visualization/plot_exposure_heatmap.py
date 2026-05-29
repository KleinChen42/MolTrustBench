"""Plot benchmark exposure heatmap."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from moltrustbench.io import ensure_parent


def _setup_style() -> None:
    mpl.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})


def plot_exposure_heatmap(summary: pd.DataFrame, output_path: str | Path = "results/figures/exposure_heatmap.pdf") -> Path:
    out = ensure_parent(output_path)
    _setup_style()
    columns = ["exact_exposure_rate", "scaffold_exposure_rate", "nn_exposure_rate_08"]
    labels = ["Exact", "Scaffold", "NN >= 0.8"]
    matrix = summary[columns].to_numpy(dtype=float) if not summary.empty else np.zeros((1, len(columns)))
    ylabels = (summary["source_name"] + ":" + summary["task_name"]).tolist() if not summary.empty else ["none"]
    fig, ax = plt.subplots(figsize=(7, max(3, 0.6 * len(ylabels) + 1.5)))
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(labels)), labels)
    ax.set_yticks(range(len(ylabels)), ylabels)
    ax.set_title("Benchmark public-exposure rates")
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            ax.text(col, row, f"{matrix[row, col]:.2f}", ha="center", va="center", color="white" if matrix[row, col] > 0.55 else "black")
    fig.colorbar(im, ax=ax, label="Exposure rate")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out
