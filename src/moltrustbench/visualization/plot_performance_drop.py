"""Plot standard vs exposure-removed performance."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from moltrustbench.io import ensure_parent


def _setup_style() -> None:
    mpl.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})


def plot_performance_drop(metrics: pd.DataFrame, output_path: str | Path = "results/figures/performance_drop.pdf") -> Path:
    out = ensure_parent(output_path)
    _setup_style()
    if metrics.empty:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "No metrics", ha="center", va="center")
        ax.axis("off")
        fig.savefig(out)
        plt.close(fig)
        return out
    score_col = "auroc" if "auroc" in metrics.columns else "primary_score"
    pivot = metrics.pivot_table(index=["source_name", "task_name", "model_id"], columns="split_name", values=score_col, aggfunc="mean").reset_index()
    model_names = {"morgan_logreg": "Morgan LR", "morgan_xgb": "Morgan XGB"}
    pivot["label"] = pivot["task_name"].astype(str) + " | " + pivot["model_id"].map(model_names).fillna(pivot["model_id"].astype(str))
    pivot = pivot.sort_values(["task_name", "model_id"]).reset_index(drop=True)
    y = list(range(len(pivot)))
    fig, ax = plt.subplots(figsize=(3.35, 2.45))
    standard = pivot.get("standard", pd.Series([0] * len(pivot)))
    exact = pivot.get("exact_removed", pd.Series([0] * len(pivot)))
    ax.barh([i + 0.17 for i in y], standard, height=0.30, label="standard", color="#3b6ea8")
    ax.barh([i - 0.17 for i in y], exact, height=0.30, label="exact removed", color="#d9822b")
    for i, (std, clean) in enumerate(zip(standard, exact)):
        ax.plot([std, clean], [i, i], color="#666666", linewidth=0.6, zorder=0)
    ax.set_yticks(y, pivot["label"], fontsize=6.5)
    ax.set_xlabel(score_col.upper())
    ax.set_xlim(0, 1.02)
    ax.set_title("Exposure-adjusted score sensitivity", fontsize=8, pad=6)
    ax.grid(axis="x", alpha=0.22)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
