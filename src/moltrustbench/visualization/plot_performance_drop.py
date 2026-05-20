"""Plot standard vs exposure-removed performance."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from moltrustbench.io import ensure_parent


def plot_performance_drop(metrics: pd.DataFrame, output_path: str | Path = "results/figures/performance_drop.pdf") -> Path:
    out = ensure_parent(output_path)
    if metrics.empty:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "No metrics", ha="center", va="center")
        ax.axis("off")
        fig.savefig(out)
        plt.close(fig)
        return out
    score_col = "auroc" if "auroc" in metrics.columns else "primary_score"
    pivot = metrics.pivot_table(index=["source_name", "task_name", "model_id"], columns="split_name", values=score_col, aggfunc="mean").reset_index()
    pivot["label"] = pivot["source_name"] + ":" + pivot["task_name"] + "\n" + pivot["model_id"]
    x = range(len(pivot))
    fig, ax = plt.subplots(figsize=(max(7, 0.9 * len(pivot)), 4))
    ax.bar([i - 0.18 for i in x], pivot.get("standard", pd.Series([0] * len(pivot))), width=0.36, label="standard", color="#3b6ea8")
    ax.bar([i + 0.18 for i in x], pivot.get("exact_removed", pd.Series([0] * len(pivot))), width=0.36, label="exact removed", color="#d9822b")
    ax.set_xticks(list(x), pivot["label"], rotation=45, ha="right")
    ax.set_ylabel(score_col.upper())
    ax.set_title("Performance under public-exposure removal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out
