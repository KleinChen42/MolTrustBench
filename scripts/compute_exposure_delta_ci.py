"""Compute paired confidence intervals for exposure-adjusted score deltas.

This script is intentionally post hoc and model-free: it uses completed
per-run metric tables and estimates whether standard-minus-exposure-aware
AUROC deltas are stable across matched seeds / hidden dimensions.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


COMPARISON_SPLITS = ["exact_removed", "scaffold_removed", "nn08_removed", "density_matched_clean"]
DEFAULT_INPUTS = [
    ("bbbp_clintox_model_family", "results/tables/gpu_model_family_slice_metrics.csv"),
    ("bace_tox21_feature_mlp", "results/tables/bace_tox21_c3_slice_metrics.csv"),
    ("bace_tox21_sequence", "results/tables/bace_tox21_sequence_slice_metrics.csv"),
]


def _t_critical_975(df: int) -> float:
    table = {
        1: 12.706,
        2: 4.303,
        3: 3.182,
        4: 2.776,
        5: 2.571,
        6: 2.447,
        7: 2.365,
        8: 2.306,
        9: 2.262,
        10: 2.228,
        11: 2.201,
        12: 2.179,
        13: 2.160,
        14: 2.145,
        15: 2.131,
        16: 2.120,
        17: 2.110,
        18: 2.101,
        19: 2.093,
        20: 2.086,
        21: 2.080,
        22: 2.074,
        23: 2.069,
        24: 2.064,
        25: 2.060,
        26: 2.056,
        27: 2.052,
        28: 2.048,
        29: 2.045,
        30: 2.042,
        40: 2.021,
        60: 2.000,
        120: 1.980,
    }
    if df in table:
        return table[df]
    for key in sorted(table):
        if df < key:
            return table[key]
    return 1.96


def _sign_test_pvalue(values: np.ndarray) -> float:
    nonzero = values[values != 0]
    n = int(len(nonzero))
    if n == 0:
        return 1.0
    k = int(np.sum(nonzero > 0))
    lower = min(k, n - k)
    prob = sum(math.comb(n, i) for i in range(lower + 1)) / (2**n)
    return min(1.0, 2.0 * prob)


def _bootstrap_ci(values: np.ndarray, *, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    if len(values) == 1:
        return float("nan"), float("nan")
    samples = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    low, high = np.percentile(samples, [2.5, 97.5])
    return float(low), float(high)


def _load_inputs(inputs: list[tuple[str, Path]]) -> pd.DataFrame:
    frames = []
    for family, path in inputs:
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if frame.empty or "auroc" not in frame:
            continue
        frame = frame.copy()
        frame["metric_family"] = family
        if "source_name" not in frame:
            frame["source_name"] = "unknown"
        if "seed" not in frame:
            frame["seed"] = 0
        if "hidden_dim" not in frame:
            frame["hidden_dim"] = np.nan
        frame["hidden_dim_key"] = frame["hidden_dim"].fillna(-1).astype(float).astype(int)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()


def _paired_deltas(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    key_cols = ["metric_family", "source_name", "task_name", "model_id", "seed", "hidden_dim_key"]
    keep_cols = key_cols + ["split_name", "auroc", "test_n"]
    work = frame[keep_cols].dropna(subset=["task_name", "model_id", "split_name", "auroc"]).copy()
    standard = (
        work[work["split_name"] == "standard"][key_cols + ["auroc", "test_n"]]
        .rename(columns={"auroc": "standard_auroc", "test_n": "standard_test_n"})
    )
    rows = []
    for split_name in COMPARISON_SPLITS:
        comp = (
            work[work["split_name"] == split_name][key_cols + ["auroc", "test_n"]]
            .rename(columns={"auroc": "comparison_auroc", "test_n": "comparison_test_n"})
        )
        merged = standard.merge(comp, on=key_cols, how="inner")
        if merged.empty:
            continue
        merged["comparison_split"] = split_name
        merged["delta"] = merged["standard_auroc"] - merged["comparison_auroc"]
        rows.append(merged)
    return pd.concat(rows, ignore_index=True, sort=False) if rows else pd.DataFrame()


def _summarize_delta(pairs: pd.DataFrame, *, n_boot: int, seed: int) -> pd.DataFrame:
    if pairs.empty:
        return pd.DataFrame()
    rng = np.random.default_rng(seed)
    rows = []
    group_cols = ["metric_family", "source_name", "task_name", "model_id", "comparison_split"]
    for key, group in pairs.groupby(group_cols, dropna=False):
        values = group["delta"].astype(float).to_numpy()
        n = int(len(values))
        mean = float(np.mean(values))
        sd = float(np.std(values, ddof=1)) if n > 1 else 0.0
        sem = sd / math.sqrt(n) if n > 1 else 0.0
        tcrit = _t_critical_975(n - 1) if n > 1 else 0.0
        boot_low, boot_high = _bootstrap_ci(values, rng=rng, n_boot=n_boot)
        ci_available = n > 1 and np.isfinite(boot_low) and np.isfinite(boot_high)
        pos = int(np.sum(values > 0))
        neg = int(np.sum(values < 0))
        row = dict(zip(group_cols, key))
        row.update(
            {
                "n_pairs": n,
                "seed_count": int(group["seed"].nunique()),
                "hidden_dim_count": int(group["hidden_dim_key"].nunique()),
                "standard_test_n_median": float(group["standard_test_n"].median()),
                "comparison_test_n_median": float(group["comparison_test_n"].median()),
                "mean_delta": mean,
                "median_delta": float(np.median(values)),
                "sd_delta": sd,
                "sem_delta": sem,
                "seed_t_ci95_low": float(mean - tcrit * sem) if n > 1 else float("nan"),
                "seed_t_ci95_high": float(mean + tcrit * sem) if n > 1 else float("nan"),
                "bootstrap_ci95_low": boot_low,
                "bootstrap_ci95_high": boot_high,
                "positive_delta_n": pos,
                "negative_delta_n": neg,
                "zero_delta_n": int(np.sum(values == 0)),
                "sign_consistency": float(max(pos, neg) / n) if n else float("nan"),
                "sign_test_p": _sign_test_pvalue(values),
                "ci_available": bool(ci_available),
                "ci_excludes_zero": bool(ci_available and ((boot_low > 0 and boot_high > 0) or (boot_low < 0 and boot_high < 0))),
                "uncertainty_status": "repeated_ci_available" if ci_available else "single_run_no_interval",
                "direction": "standard_higher" if mean > 0 else "comparison_higher" if mean < 0 else "zero",
            }
        )
        rows.append(row)
    out = pd.DataFrame.from_records(rows)
    return out.sort_values(["metric_family", "task_name", "model_id", "comparison_split"]).reset_index(drop=True)


def _write_delta_figure(table: pd.DataFrame, path: Path, *, title: str, metric_family: str | None = None) -> None:
    if table.empty:
        return
    plot = table.copy()
    if metric_family is not None:
        plot = plot[plot["metric_family"] == metric_family].copy()
    if plot.empty:
        return
    import matplotlib.pyplot as plt

    comparisons = COMPARISON_SPLITS
    labels = sorted((plot["task_name"].astype(str) + " / " + plot["model_id"].astype(str)).unique())
    fig_height = max(4.5, 0.38 * len(labels) + 1.2)
    fig, axes = plt.subplots(1, len(comparisons), figsize=(14, fig_height), sharey=True)
    if len(comparisons) == 1:
        axes = [axes]
    y = np.arange(len(labels))
    for ax, comparison in zip(axes, comparisons):
        sub = plot[plot["comparison_split"] == comparison].copy()
        means, lows, highs, sigs, ci_available = [], [], [], [], []
        for label in labels:
            row = sub[(sub["task_name"].astype(str) + " / " + sub["model_id"].astype(str)) == label]
            if row.empty:
                means.append(np.nan)
                lows.append(np.nan)
                highs.append(np.nan)
                sigs.append(False)
                ci_available.append(False)
            else:
                r = row.iloc[0]
                means.append(float(r["mean_delta"]))
                lows.append(float(r["bootstrap_ci95_low"]))
                highs.append(float(r["bootstrap_ci95_high"]))
                sigs.append(bool(r["ci_excludes_zero"]))
                ci_available.append(bool(r.get("ci_available", False)))
        means_arr = np.array(means, dtype=float)
        lows_arr = np.array(lows, dtype=float)
        highs_arr = np.array(highs, dtype=float)
        colors = ["#2f6f9f" if sig else "#9aa0a6" for sig in sigs]
        ci_mask = np.array(ci_available, dtype=bool) & np.isfinite(means_arr) & np.isfinite(lows_arr) & np.isfinite(highs_arr)
        if np.any(ci_mask):
            xerr = np.vstack([means_arr[ci_mask] - lows_arr[ci_mask], highs_arr[ci_mask] - means_arr[ci_mask]])
            ax.errorbar(means_arr[ci_mask], y[ci_mask], xerr=xerr, fmt="none", ecolor="#505050", elinewidth=1, capsize=2)
        ax.scatter(means_arr, y, s=28, c=colors, zorder=3)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_title(comparison.replace("_", " "))
        ax.set_xlabel("AUROC delta\nstandard - comparison")
        ax.grid(axis="x", alpha=0.18)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(labels)
    fig.suptitle(title, y=1.01)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-boot", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260525)
    parser.add_argument("--output-table", default="results/tables/exposure_delta_ci.csv")
    parser.add_argument("--sequence-table", default="results/tables/sequence_delta_ci.csv")
    parser.add_argument("--figure", default="results/figures/exposure_delta_ci.pdf")
    parser.add_argument("--sequence-figure", default="results/figures/sequence_delta_ci.pdf")
    parser.add_argument("--summary-json", default="results/tables/exposure_delta_ci_summary.json")
    args = parser.parse_args()

    inputs = [(family, Path(path)) for family, path in DEFAULT_INPUTS]
    frame = _load_inputs(inputs)
    pairs = _paired_deltas(frame)
    table = _summarize_delta(pairs, n_boot=args.n_boot, seed=args.seed)
    sequence = table[table["metric_family"] == "bace_tox21_sequence"].copy()

    Path(args.output_table).parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output_table, index=False)
    sequence.to_csv(args.sequence_table, index=False)
    _write_delta_figure(table, Path(args.figure), title="Exposure-adjusted delta confidence intervals")
    _write_delta_figure(
        table,
        Path(args.sequence_figure),
        title="BACE/Tox21 sequence-family delta confidence intervals",
        metric_family="bace_tox21_sequence",
    )

    payload = {
        "status": "completed",
        "input_rows": int(len(frame)),
        "paired_delta_rows": int(len(pairs)),
        "summary_rows": int(len(table)),
        "sequence_summary_rows": int(len(sequence)),
        "n_boot": int(args.n_boot),
        "random_seed": int(args.seed),
        "outputs": {
            "exposure_delta_ci": args.output_table,
            "sequence_delta_ci": args.sequence_table,
            "exposure_delta_ci_figure": args.figure,
            "sequence_delta_ci_figure": args.sequence_figure,
        },
    }
    Path(args.summary_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
