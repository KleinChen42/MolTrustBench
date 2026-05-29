"""Plot assay-provenance heterogeneity summaries."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from moltrustbench.io import ensure_parent


def _setup_style() -> None:
    mpl.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})


def plot_assay_conflict(
    task_summary: pd.DataFrame,
    output_path: str | Path = "results/figures/assay_conflict_map.pdf",
) -> Path:
    """Create a compact assay-provenance heterogeneity map from task summaries."""

    out = ensure_parent(output_path)
    _setup_style()
    fig, ax = plt.subplots(figsize=(8.0, 4.4), constrained_layout=True)
    if task_summary.empty:
        ax.text(0.5, 0.5, "No assay provenance records", ha="center", va="center")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(out)
        plt.close(fig)
        return out

    frame = task_summary.copy()
    def _short_label(row: pd.Series) -> str:
        task = str(row.get("task_name", ""))
        task_lower = task.lower()
        if "herg" in task_lower:
            return "hERG pilot"
        if "cyp1a2" in task_lower:
            return "CYP1A2"
        if "cyp2c19" in task_lower:
            return "CYP2C19"
        if "dili" in task_lower or "hepatotoxicity" in task_lower:
            return "DILI/hepatotox"
        return task or str(row.get("source_name", "task"))

    frame["task_label"] = frame.apply(_short_label, axis=1)
    metrics = [
        "duplicate_compound_count",
        "conflicting_label_count",
        "unit_inconsistency_count",
        "threshold_sensitive_count",
    ]
    for metric in metrics:
        if metric not in frame:
            frame[metric] = 0

    matrix = frame.set_index("task_label")[metrics].astype(float)
    denominators = frame.set_index("task_label")["molecules_with_activity"].replace(0, pd.NA).astype(float)
    matrix = matrix.div(denominators, axis=0).fillna(0.0)

    image = ax.imshow(
        matrix.to_numpy(),
        cmap="YlOrRd",
        vmin=0,
        vmax=max(0.01, float(matrix.max().max())),
        aspect="auto",
    )
    metric_labels = [
        "Duplicate",
        "Discordance",
        "Units",
        "Threshold",
    ]
    ax.set_xticks(range(len(metrics)), metric_labels)
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    for label in ax.get_xticklabels():
        label.set_rotation(25)
        label.set_horizontalalignment("right")
        label.set_rotation_mode("anchor")
    ax.set_title("Assay-provenance heterogeneity rates", pad=10)
    for y, (_, row) in enumerate(matrix.iterrows()):
        for x, value in enumerate(row):
            color = "white" if value >= 0.55 else "black"
            ax.text(x, y, f"{value:.2f}", ha="center", va="center", fontsize=8, color=color)
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02, label="fraction of molecules with activity")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
