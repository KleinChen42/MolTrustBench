"""Make BIB-facing final versions of Fig. 3, Fig. 4, and Fig. S7.

The figures are regenerated from integrated result tables. They intentionally
show exposure-adjusted score sensitivity and negative-control diagnostics
without implying model-specific training exposure.
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch


FIG_DIR = Path("results/figures")
TABLE_DIR = Path("results/tables")

SPLIT_ORDER = ["exact_removed", "scaffold_removed", "nn08_removed", "density_matched_clean"]
SPLIT_LABEL = {
    "exact_removed": "Exact\nremoved",
    "scaffold_removed": "Scaffold\nremoved",
    "nn08_removed": "NN >= 0.8\nremoved",
    "density_matched_clean": "Density\nmatched",
}
MODEL_LABEL = {
    "morgan_logreg": "Morgan LR",
    "morgan_xgb": "Morgan XGB",
    "morgan_mlp_gpu": "Morgan MLP",
    "smiles_cnn": "SMILES-CNN",
    "smiles_gru": "SMILES-GRU",
    "smiles_transformer": "SMILES-Transformer",
}
MODEL_SHORT = {
    "smiles_cnn": "CNN",
    "smiles_gru": "GRU",
    "smiles_transformer": "Trf.",
}
SPLIT_SHORT = {
    "exact_removed": "Exact",
    "scaffold_removed": "Scaf.",
    "nn08_removed": "NN0.8",
    "density_matched_clean": "Dens.",
    "temporal_future": "Temp.",
}
TASK_LABEL = {
    "BBBP": "BBBP",
    "ClinTox": "ClinTox",
    "BACE": "BACE",
    "Tox21": "Tox21",
    "CYP2C9_pchembl5_temporal": "CYP2C9",
    "CYP2D6_pchembl5_temporal": "CYP2D6",
    "CYP3A4_pchembl5_temporal": "CYP3A4",
    "hERG_pchembl5_temporal": "hERG",
}

PALETTE = {
    "pos": "#2c6f9e",
    "neg": "#b86b43",
    "neutral": "#8a8f98",
    "grid": "#d9dee7",
    "text": "#1f2933",
    "support": "#28745a",
    "limited": "#b06b2c",
}


def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.4,
            "legend.fontsize": 6.3,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def export_figure(fig: plt.Figure, stem: Path) -> list[str]:
    stem.parent.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix, kwargs in [
        (".pdf", {"bbox_inches": "tight"}),
        (".svg", {"bbox_inches": "tight"}),
        (".png", {"dpi": 300, "bbox_inches": "tight"}),
        (".tiff", {"dpi": 600, "bbox_inches": "tight"}),
    ]:
        out = stem.with_suffix(suffix)
        fig.savefig(out, **kwargs)
        paths.append(str(out))
    return paths


def duplicate_exports(src_stem: Path, dst_stem: Path) -> list[str]:
    copied: list[str] = []
    for suffix in [".pdf", ".svg", ".png", ".tiff"]:
        src = src_stem.with_suffix(suffix)
        dst = dst_stem.with_suffix(suffix)
        if src.exists():
            shutil.copyfile(src, dst)
            copied.append(str(dst))
    return copied


def label_row(task: str, model: str) -> str:
    return f"{TASK_LABEL.get(task, task)} | {MODEL_LABEL.get(model, model)}"


def draw_delta_heatmap(
    ax: plt.Axes,
    table: pd.DataFrame,
    row_order: list[tuple[str, str]],
    *,
    title: str,
    show_y: bool = True,
    vlim: float | None = None,
) -> None:
    if vlim is None:
        finite = table["mean_delta"].replace([np.inf, -np.inf], np.nan).dropna().abs()
        vlim = max(0.12, float(np.nanpercentile(finite, 95)) if len(finite) else 0.2)
    matrix = np.full((len(row_order), len(SPLIT_ORDER)), np.nan)
    stable = np.full_like(matrix, False, dtype=bool)
    pairs = np.full_like(matrix, np.nan, dtype=float)
    for i, (task, model) in enumerate(row_order):
        for j, split in enumerate(SPLIT_ORDER):
            row = table[
                (table["task_name"] == task)
                & (table["model_id"] == model)
                & (table["comparison_split"] == split)
            ]
            if row.empty:
                continue
            r = row.iloc[0]
            matrix[i, j] = float(r["mean_delta"])
            stable[i, j] = bool(r.get("ci_available", False)) and float(r.get("n_pairs", 0)) >= 2 and bool(r["ci_excludes_zero"])
            pairs[i, j] = float(r["n_pairs"])

    cmap = mpl.colormaps["RdBu_r"].copy()
    cmap.set_bad("#f1f3f5")
    norm = TwoSlopeNorm(vmin=-vlim, vcenter=0, vmax=vlim)
    im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    ax.set_xticks(np.arange(len(SPLIT_ORDER)))
    ax.set_xticklabels([SPLIT_LABEL[s] for s in SPLIT_ORDER])
    if show_y:
        ax.set_yticks(np.arange(len(row_order)))
        ax.set_yticklabels([label_row(t, m) for t, m in row_order])
    else:
        ax.set_yticks(np.arange(len(row_order)))
        ax.set_yticklabels([])
    ax.set_title(title, loc="left", fontweight="bold", pad=6)
    ax.tick_params(axis="both", length=0)

    for i in range(len(row_order)):
        for j in range(len(SPLIT_ORDER)):
            if not np.isfinite(matrix[i, j]):
                ax.text(j, i, "NA", ha="center", va="center", color="#9aa0a6", fontsize=5.5)
                continue
            color = "white" if abs(matrix[i, j]) > vlim * 0.45 else PALETTE["text"]
            ax.text(j, i - 0.10, f"{matrix[i, j]:+.2f}", ha="center", va="center", color=color, fontsize=5.7)
            marker = "o" if stable[i, j] else "x"
            ax.text(j, i + 0.24, marker, ha="center", va="center", color=color, fontsize=5.5, fontweight="bold")
            if np.isfinite(pairs[i, j]) and pairs[i, j] <= 5:
                ax.text(j + 0.36, i - 0.35, f"n={int(pairs[i, j])}", ha="right", va="top", color=color, fontsize=4.7)

    ax.set_xticks(np.arange(-0.5, len(SPLIT_ORDER), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(row_order), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)
    return im


def make_fig4() -> dict[str, object]:
    ci = pd.read_csv(TABLE_DIR / "exposure_delta_ci.csv")
    ci = ci[ci["comparison_split"].isin(SPLIT_ORDER)].copy()
    include = ci[
        ci["metric_family"].isin(["bbbp_clintox_model_family", "bace_tox21_feature_mlp"])
    ].copy()
    include = include[
        (include["n_pairs"].fillna(0).astype(float) >= 5)
        & (include["ci_available"].astype(str).str.lower().isin({"true", "1"}))
    ].copy()
    include["model_order"] = include["model_id"].map(
        {
            "morgan_logreg": 0,
            "morgan_xgb": 1,
            "morgan_mlp_gpu": 2,
            "smiles_cnn": 3,
            "smiles_gru": 4,
            "smiles_transformer": 5,
        }
    )
    task_order = ["BBBP", "ClinTox", "BACE", "Tox21"]
    row_order: list[tuple[str, str]] = []
    for task in task_order:
        models = (
            include[include["task_name"] == task][["model_id", "model_order"]]
            .drop_duplicates()
            .sort_values("model_order")["model_id"]
            .tolist()
        )
        row_order.extend((task, model) for model in models)

    summary = include[
        include.apply(lambda r: (r["task_name"], r["model_id"]) in row_order, axis=1)
    ].copy()
    summary.to_csv(TABLE_DIR / "fig3_exposure_delta_ci_source.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    im = draw_delta_heatmap(
        ax,
        summary,
        row_order,
        title="Fig. 3 | Exposure-adjusted AUROC deltas across benchmark tasks",
        vlim=0.42,
    )
    ax.set_xlabel("Exposure-aware comparison split")
    cbar = fig.colorbar(im, ax=ax, shrink=0.84, pad=0.025)
    cbar.set_label("AUROC delta: standard - comparison")
    legend = [
        Patch(facecolor="#f1f3f5", edgecolor="#c5cbd3", label="Not evaluable"),
        Patch(facecolor="white", edgecolor="white", label="o: seed-replicate interval excludes 0"),
        Patch(facecolor="white", edgecolor="white", label="x: seed-replicate interval overlaps 0"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=3)
    fig.text(
        0.01,
        0.01,
        "Positive values mean the standard split score is higher; negative values mean the exposure-aware slice is higher.",
        fontsize=6.2,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    stem = FIG_DIR / "fig3_exposure_delta_ci_bib"
    paths = export_figure(fig, stem)
    paths.extend(duplicate_exports(stem, FIG_DIR / "exposure_delta_ci"))
    plt.close(fig)
    return {"figure": "Fig3", "rows": int(len(summary)), "outputs": paths}


def make_fig5() -> dict[str, object]:
    seq = pd.read_csv(TABLE_DIR / "sequence_delta_ci.csv")
    seq = seq[seq["comparison_split"].isin(SPLIT_ORDER)].copy()
    row_order = [(task, model) for task in ["BACE", "Tox21"] for model in ["smiles_cnn", "smiles_gru", "smiles_transformer"]]
    seq.to_csv(TABLE_DIR / "fig5_sequence_family_delta_source.csv", index=False)

    fig = plt.figure(figsize=(7.35, 4.8))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.34, 1.0], wspace=0.62)
    ax0 = fig.add_subplot(gs[0, 0])
    im = draw_delta_heatmap(
        ax0,
        seq,
        row_order,
        title="A  Sequence-family AUROC deltas",
        vlim=0.30,
    )
    ax0.set_xlabel("Exposure-aware comparison split")

    ax1 = fig.add_subplot(gs[0, 1])
    size_rows = []
    for task in ["BACE", "Tox21"]:
        for split in SPLIT_ORDER:
            sub = seq[(seq["task_name"] == task) & (seq["comparison_split"] == split)]
            if sub.empty:
                continue
            size_rows.append(
                {
                    "task_name": task,
                    "comparison_split": split,
                    "comparison_test_n_median": float(sub["comparison_test_n_median"].median()),
                    "standard_test_n_median": float(sub["standard_test_n_median"].median()),
                }
            )
    sizes = pd.DataFrame(size_rows)
    sizes.to_csv(TABLE_DIR / "fig5_sequence_family_comparison_size_source.csv", index=False)
    sizes.to_csv(TABLE_DIR / "fig5_sequence_family_clean_size_source.csv", index=False)
    y_labels = [f"{TASK_LABEL[t]} {SPLIT_SHORT.get(s, s)}" for t, s in zip(sizes["task_name"], sizes["comparison_split"])]
    y = np.arange(len(sizes))
    colors = [PALETTE["pos"] if t == "BACE" else PALETTE["neg"] for t in sizes["task_name"]]
    ax1.barh(y, sizes["comparison_test_n_median"], color=colors, alpha=0.82)
    for i, r in sizes.iterrows():
        ax1.text(r["comparison_test_n_median"] + max(sizes["comparison_test_n_median"]) * 0.025, i, f"{int(r['comparison_test_n_median'])}", va="center", fontsize=5.8)
    ax1.set_yticks(y)
    ax1.set_yticklabels(y_labels)
    ax1.tick_params(axis="y", labelsize=5.9, pad=2)
    ax1.invert_yaxis()
    ax1.set_xlabel("Median comparison test n")
    ax1.set_title("B  Exposure-removed slice-size boundary", loc="left", fontweight="bold", pad=6)
    ax1.grid(axis="x", alpha=0.18)
    ax1.set_xlim(0, max(sizes["comparison_test_n_median"]) * 1.25)

    cbar = fig.colorbar(im, ax=ax0, orientation="horizontal", shrink=0.66, pad=0.17)
    cbar.set_label("AUROC delta: standard - comparison")
    fig.text(
        0.01,
        0.015,
        "Dots mark bootstrap CIs excluding zero; x marks deltas whose CI overlaps zero. Bars show why strict exposure-removed slices need sample-size caveats.",
        fontsize=6.2,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    stem = FIG_DIR / "fig5_sequence_family_bib"
    paths = export_figure(fig, stem)
    paths.extend(duplicate_exports(stem, FIG_DIR / "bace_tox21_sequence_model_family"))
    plt.close(fig)
    return {"figure": "Fig5", "rows": int(len(seq)), "outputs": paths}


def make_figs7() -> dict[str, object]:
    comp = pd.read_csv(TABLE_DIR / "label_shuffle_null_control_comparison.csv").copy()
    comp["label"] = (
        comp["task_name"].map(TASK_LABEL).fillna(comp["task_name"])
        + " | "
        + comp["model_id"].map(MODEL_SHORT).fillna(comp["model_id"])
        + " | "
        + comp["comparison_split"].map(lambda s: SPLIT_SHORT.get(s, s))
    )
    comp = comp.sort_values("absolute_observed_delta", ascending=True).reset_index(drop=True)
    comp.to_csv(TABLE_DIR / "figS7_label_shuffle_source.csv", index=False)

    support = comp["paper_use"] == "supports_non-null_delta"
    support_n = int(support.sum())
    total_n = int(len(comp))
    mean_obs = float(comp["absolute_observed_delta"].mean())
    mean_shuffle = float(comp["absolute_shuffle_delta"].mean())

    fig = plt.figure(figsize=(7.8, 6.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.84, 1.58], wspace=0.78)
    ax0 = fig.add_subplot(gs[0, 0])
    colors = np.where(support, PALETTE["support"], PALETTE["limited"])
    ax0.scatter(
        comp["absolute_shuffle_delta"],
        comp["absolute_observed_delta"],
        c=colors,
        s=34,
        edgecolor="white",
        linewidth=0.45,
        zorder=3,
    )
    lim = max(comp["absolute_observed_delta"].max(), comp["absolute_shuffle_delta"].max()) * 1.08
    ax0.plot([0, lim], [0, lim], color="#6b7280", linewidth=0.9, linestyle="--")
    ax0.set_xlim(-lim * 0.035, lim)
    ax0.set_ylim(-lim * 0.035, lim)
    ax0.set_xlabel("|delta| after label shuffle")
    ax0.set_ylabel("|delta| with observed labels")
    ax0.set_title("A  Observed deltas vs null-control deltas", loc="left", fontweight="bold", pad=6)
    ax0.grid(alpha=0.16)
    ax0.text(
        0.96,
        0.05,
        f"{support_n}/{total_n} above null\nmean |obs|={mean_obs:.3f}\nmean |shuffle|={mean_shuffle:.3f}",
        transform=ax0.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.4,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cbd5e1", "linewidth": 0.6},
    )

    ax1 = fig.add_subplot(gs[0, 1])
    y = np.arange(len(comp))
    for i, row in comp.iterrows():
        c = PALETTE["support"] if row["paper_use"] == "supports_non-null_delta" else PALETTE["limited"]
        ax1.plot(
            [row["absolute_shuffle_delta"], row["absolute_observed_delta"]],
            [i, i],
            color=c,
            linewidth=1.4,
            alpha=0.82,
        )
        ax1.scatter(row["absolute_shuffle_delta"], i, c="#ffffff", edgecolor=c, s=22, linewidth=0.9, zorder=3)
        ax1.scatter(row["absolute_observed_delta"], i, c=c, edgecolor="white", s=30, linewidth=0.45, zorder=4)
    ax1.set_yticks(y)
    ax1.set_yticklabels(comp["label"])
    ax1.tick_params(axis="y", labelsize=5.5, pad=1)
    ax1.set_xlabel("Absolute AUROC delta")
    ax1.set_title("B  Paired null-control comparison", loc="left", fontweight="bold", pad=6)
    ax1.grid(axis="x", alpha=0.16)
    ax1.set_xlim(0, lim)
    ax1.legend(
        handles=[
            Patch(facecolor=PALETTE["support"], label="Observed > shuffled-label"),
            Patch(facecolor=PALETTE["limited"], label="Null-sensitive"),
            Patch(facecolor="white", edgecolor=PALETTE["support"], label="open: shuffled-label delta"),
        ],
        loc="lower right",
        frameon=False,
    )
    fig.text(
        0.01,
        0.012,
        "Train-label-shuffle is a negative control for exposure-adjusted deltas, not causal evidence of public exposure effects.",
        fontsize=6.2,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    stem = FIG_DIR / "figS7_label_shuffle_null_control_bib"
    paths = export_figure(fig, stem)
    paths.extend(duplicate_exports(stem, FIG_DIR / "label_shuffle_null_control"))
    plt.close(fig)
    return {"figure": "FigS7", "rows": int(len(comp)), "outputs": paths}


def main() -> None:
    setup_style()
    summaries = [make_fig4(), make_fig5(), make_figs7()]
    payload = {
        "status": "completed",
        "figure_contract": {
            "Fig3": "Exposure-adjusted AUROC deltas identify score-sensitive slices and uncertain deltas.",
            "Fig5": "BACE/Tox21 sequence-family effects are task- and architecture-dependent and require exposure-removed slice-size caveats.",
            "FigS7": "Train-label-shuffle controls are negative controls, not causal exposure evidence.",
        },
        "outputs": summaries,
    }
    out = TABLE_DIR / "bib_final_figure_summary.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
