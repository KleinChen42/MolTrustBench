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
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle


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
SPLIT_COLOR = {
    "exact_removed": "#2c6f9e",
    "scaffold_removed": "#28745a",
    "nn08_removed": "#7b61a8",
    "density_matched_clean": "#b06b2c",
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


def bool_series(values: pd.Series) -> pd.Series:
    return values.astype(str).str.lower().isin({"true", "1", "yes"})


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


def build_fig3_validity_tiles(summary: pd.DataFrame, retained: pd.DataFrame) -> pd.DataFrame:
    """Build compact slice-validity tiles from S24 when available.

    The figure can be regenerated before S24 exists; in that case the tile strip
    falls back to CI/source-table sample sizes and marks class balance as not
    shown in the main panel.
    """

    s24_path = Path("paper/supplement/tables/Table_S24_slice_validity_master.csv")
    task_order = ["BBBP", "ClinTox", "BACE", "Tox21"]
    rows: list[dict[str, object]] = []
    s24 = pd.read_csv(s24_path) if s24_path.exists() else pd.DataFrame()
    for task in task_order:
        for split in SPLIT_ORDER:
            summ = summary[(summary["task_name"] == task) & (summary["comparison_split"] == split)]
            ret = retained[(retained["task_name"] == task) & (retained["comparison_split"] == split)]
            test_n = ""
            if not summ.empty:
                test_n = int(round(float(summ.iloc[0]["comparison_test_n_median"])))
            elif not ret.empty:
                test_n = int(round(float(ret["comparison_test_n_median"].median())))

            one_class = False
            low_minority = False
            caution = False
            min_class_n = ""
            if not s24.empty:
                block_filter = s24["source_block"].astype(str).isin(
                    ["core_slice_metrics", "bace_tox21_classical_metrics", "bace_tox21_sequence_metrics"]
                )
                sub = s24[
                    block_filter
                    & s24["task_name"].astype(str).eq(task)
                    & s24["split_name"].astype(str).eq(split)
                ].copy()
                if not sub.empty:
                    one_class = bool(bool_series(sub["one_class_flag"]).any())
                    status = sub["interpretation_status"].astype(str)
                    low_minority = bool(status.str.contains("low_minority_class_boundary", na=False).any())
                    caution = bool(status.str.contains("small_minority_class_caution", na=False).any())
                    numeric_min = pd.to_numeric(sub["min_class_n"], errors="coerce").dropna()
                    if len(numeric_min):
                        min_class_n = int(numeric_min.min())
                    numeric_test = pd.to_numeric(sub["test_n"], errors="coerce").dropna()
                    if len(numeric_test):
                        test_n = int(numeric_test.median())

            ci_available = not summ.empty
            if one_class:
                status = "one-class"
                tile_color = "#f2c4bf"
            elif low_minority:
                status = "low minority"
                tile_color = "#f4d6a5"
            elif caution:
                status = "minority caution"
                tile_color = "#f6e7b5"
            elif ci_available:
                status = "interval"
                tile_color = "#cfe8d8"
            else:
                status = "source only"
                tile_color = "#e5e7eb"
            rows.append(
                {
                    "task_name": task,
                    "comparison_split": split,
                    "comparison_test_n_median": test_n,
                    "one_class_flag": one_class,
                    "low_minority_class_flag": low_minority,
                    "small_minority_class_caution": caution,
                    "min_class_n": min_class_n,
                    "ci_available": ci_available,
                    "interpretation_status": status,
                    "tile_color": tile_color,
                }
            )
    return pd.DataFrame(rows)


def make_fig4() -> dict[str, object]:
    ci = pd.read_csv(TABLE_DIR / "exposure_delta_ci.csv")
    ci = ci[ci["comparison_split"].isin(SPLIT_ORDER)].copy()
    include = ci[
        ci["metric_family"].isin(["bbbp_clintox_model_family", "bace_tox21_feature_mlp"])
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
    include["n_pairs_numeric"] = pd.to_numeric(include["n_pairs"], errors="coerce").fillna(0)
    include["sd_delta_numeric"] = pd.to_numeric(include["sd_delta"], errors="coerce").fillna(0)
    include["ci_available_bool"] = bool_series(include["ci_available"])
    task_order = ["BBBP", "ClinTox", "BACE", "Tox21"]
    row_order: list[tuple[str, str]] = []
    full = include[include["n_pairs_numeric"] >= 1].copy()
    for task in task_order:
        models = (
            full[full["task_name"] == task][["model_id", "model_order"]]
            .drop_duplicates()
            .sort_values("model_order")["model_id"]
            .tolist()
        )
        row_order.extend((task, model) for model in models)

    full_source = full[
        full.apply(lambda r: (r["task_name"], r["model_id"]) in row_order, axis=1)
    ].copy()
    full_source.to_csv(TABLE_DIR / "figS3_exposure_delta_full_source.csv", index=False)

    retained = full_source[
        (full_source["n_pairs_numeric"] >= 5)
        & full_source["ci_available_bool"]
        & full_source["uncertainty_status"].astype(str).eq("seed_replicate_ci_available")
        & (full_source["sd_delta_numeric"] > 0)
    ].copy()
    retained.to_csv(TABLE_DIR / "fig3_exposure_delta_ci_source.csv", index=False)

    summary_rows = []
    for task in task_order:
        for split in SPLIT_ORDER:
            sub = retained[(retained["task_name"] == task) & (retained["comparison_split"] == split)].copy()
            if sub.empty:
                continue
            deltas = pd.to_numeric(sub["median_delta"], errors="coerce").dropna()
            if deltas.empty:
                continue
            summary_rows.append(
                {
                    "task_name": task,
                    "comparison_split": split,
                    "median_delta_across_model_families": float(deltas.median()),
                    "iqr_low": float(deltas.quantile(0.25)),
                    "iqr_high": float(deltas.quantile(0.75)),
                    "retained_model_rows": int(len(sub)),
                    "retained_model_families": ";".join(sorted(sub["model_id"].astype(str).unique())),
                    "comparison_test_n_median": float(pd.to_numeric(sub["comparison_test_n_median"], errors="coerce").median()),
                    "n_pairs_min": int(pd.to_numeric(sub["n_pairs"], errors="coerce").min()),
                    "uncertainty_status": "seed_replicate_ci_available",
                }
            )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(TABLE_DIR / "fig3_exposure_delta_summary_source.csv", index=False)
    validity = build_fig3_validity_tiles(summary, full_source)
    validity.to_csv(TABLE_DIR / "fig3_slice_validity_source.csv", index=False)

    # Supplementary full matrix, retained for auditability.
    fig_s, ax_s = plt.subplots(figsize=(7.4, 6.4))
    im_s = draw_delta_heatmap(
        ax_s,
        full_source,
        row_order,
        title="Fig. S3 | Full exposure-adjusted AUROC delta matrix",
        vlim=0.42,
    )
    ax_s.set_xlabel("Exposure-aware comparison split")
    cbar_s = fig_s.colorbar(im_s, ax=ax_s, shrink=0.84, pad=0.025)
    cbar_s.set_label("AUROC delta: standard - comparison")
    ax_s.legend(
        handles=[
            Patch(facecolor="#f1f3f5", edgecolor="#c5cbd3", label="Not evaluable"),
            Patch(facecolor="white", edgecolor="white", label="o: interval excludes 0"),
            Patch(facecolor="white", edgecolor="white", label="x: source-table-only or interval overlaps 0"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=3,
    )
    fig_s.tight_layout(rect=(0, 0.04, 1, 1))
    supp_stem = FIG_DIR / "figS3_exposure_delta_full_heatmap_bib"
    supp_paths = export_figure(fig_s, supp_stem)
    supp_paths.extend(duplicate_exports(supp_stem, FIG_DIR / "figS3_exposure_delta_full_heatmap"))
    plt.close(fig_s)

    fig = plt.figure(figsize=(7.25, 5.15))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.12, 0.94], hspace=0.55)
    ax0 = fig.add_subplot(gs[0, 0])
    y_base = {task: i for i, task in enumerate(task_order)}
    offsets = {
        "exact_removed": -0.27,
        "scaffold_removed": -0.09,
        "nn08_removed": 0.09,
        "density_matched_clean": 0.27,
    }
    for split in SPLIT_ORDER:
        sub = summary[summary["comparison_split"] == split]
        for _, row in sub.iterrows():
            y = y_base[str(row["task_name"])] + offsets[split]
            median = float(row["median_delta_across_model_families"])
            lo = float(row["iqr_low"])
            hi = float(row["iqr_high"])
            ax0.plot([lo, hi], [y, y], color=SPLIT_COLOR[split], linewidth=1.6, solid_capstyle="round")
            ax0.scatter(median, y, s=34, color=SPLIT_COLOR[split], edgecolor="white", linewidth=0.55, zorder=3)
    ax0.axvline(0, color="#4b5563", linewidth=0.75, linestyle="--")
    ax0.set_yticks(np.arange(len(task_order)))
    ax0.set_yticklabels(task_order)
    ax0.set_ylim(len(task_order) - 0.5, -0.5)
    max_abs = max(
        0.12,
        float(np.nanmax(np.abs(summary[["iqr_low", "iqr_high", "median_delta_across_model_families"]].to_numpy())))
        if not summary.empty
        else 0.2,
    )
    ax0.set_xlim(-max_abs * 1.16, max_abs * 1.16)
    ax0.set_xlabel("AUROC delta: standard - exposure-aware comparison")
    ax0.set_title("A  Repeated-evidence exposure-adjusted score sensitivity", loc="left", fontweight="bold", pad=5)
    ax0.grid(axis="x", alpha=0.18)
    ax0.legend(
        handles=[
            Line2D([0], [0], marker="o", color=SPLIT_COLOR[split], label=SPLIT_LABEL[split].replace("\n", " "), linewidth=1.4)
            for split in SPLIT_ORDER
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.47),
        ncol=4,
        frameon=False,
    )

    ax1 = fig.add_subplot(gs[1, 0])
    for i, task in enumerate(task_order):
        for j, split in enumerate(SPLIT_ORDER):
            row = validity[(validity["task_name"] == task) & (validity["comparison_split"] == split)]
            if row.empty:
                color = "#e5e7eb"
                n_text = "n=NA"
                status = "source only"
            else:
                r = row.iloc[0]
                color = str(r["tile_color"])
                n_value = r["comparison_test_n_median"]
                n_text = f"n={int(n_value)}" if str(n_value) not in {"", "nan"} else "n=NA"
                status = str(r["interpretation_status"])
            status_label = {
                "low minority": "low min.",
                "minority caution": "caution",
                "one-class": "1-class",
                "source only": "source",
            }.get(status, status)
            ax1.add_patch(Rectangle((j - 0.48, i - 0.42), 0.96, 0.84, facecolor=color, edgecolor="white", linewidth=1.0))
            ax1.text(j, i - 0.09, n_text, ha="center", va="center", fontsize=6.0, color=PALETTE["text"])
            ax1.text(j, i + 0.17, status_label, ha="center", va="center", fontsize=5.2, color=PALETTE["text"])
    ax1.set_xlim(-0.5, len(SPLIT_ORDER) - 0.5)
    ax1.set_ylim(len(task_order) - 0.5, -0.5)
    ax1.set_xticks(np.arange(len(SPLIT_ORDER)))
    ax1.set_xticklabels([SPLIT_LABEL[s].replace("\n", " ") for s in SPLIT_ORDER])
    ax1.set_yticks(np.arange(len(task_order)))
    ax1.set_yticklabels(task_order)
    ax1.set_title("B  Comparison-slice validity boundary", loc="left", fontweight="bold", pad=5)
    ax1.tick_params(length=0)
    for spine in ax1.spines.values():
        spine.set_visible(False)
    fig.text(
        0.01,
        0.01,
        "Positive deltas mean the standard split score is higher; negative deltas mean the exposure-aware slice is higher. Panel A summarizes median and IQR across retained model-family rows.",
        fontsize=6.2,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    stem = FIG_DIR / "fig3_exposure_delta_ci_bib"
    paths = export_figure(fig, stem)
    paths.extend(duplicate_exports(stem, FIG_DIR / "exposure_delta_ci"))
    plt.close(fig)
    paths.extend(supp_paths)
    return {"figure": "Fig3", "rows": int(len(summary)), "retained_rows": int(len(retained)), "outputs": paths}


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
