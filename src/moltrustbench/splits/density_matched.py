"""Density-matched clean split construction.

This module supports reviewer risk R2: exposure effects may be confounded with
ordinary chemical-space density. The split keeps the original train/validation
rows and selects non-exact-exposed test molecules whose nearest-neighbor density
bins match the exposed test distribution as closely as available data permit.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from moltrustbench.io import read_dataframe, write_dataframe, write_json


def density_bins(df: pd.DataFrame, *, column: str = "max_nn_similarity_before_cutoff", bins: int = 5) -> pd.Series:
    """Return deterministic quantile bins for a density-like column."""

    if column not in df:
        raise KeyError(f"Missing density column: {column}")
    values = df[column].fillna(0.0)
    if values.nunique() <= 1:
        return pd.Series([0] * len(values), index=df.index)
    return pd.qcut(values.rank(method="first"), q=bins, labels=False, duplicates="drop")


def _train_rows(df: pd.DataFrame) -> list[int]:
    return df[df["split"].isin(["train", "valid", "validation"])]["row_id"].astype(int).tolist()


def _test_frame_with_bins(
    df: pd.DataFrame,
    *,
    density_column: str,
    bins: int,
) -> pd.DataFrame:
    required = {"row_id", "split", "exact_exposed", density_column}
    missing = sorted(required - set(df.columns))
    if missing:
        raise KeyError(f"Missing columns for density-matched split: {missing}")
    test = df[df["split"] == "test"].copy()
    if test.empty:
        raise ValueError("Cannot build density-matched split without test rows")
    test["_density_bin"] = density_bins(test, column=density_column, bins=bins).astype(int)
    return test


def density_matched_clean_split(
    df: pd.DataFrame,
    *,
    density_column: str = "max_nn_similarity_before_cutoff",
    bins: int = 5,
) -> dict[str, list[int]]:
    """Return train/test indices for a density-matched clean test subset.

    The selected test rows are non-exact-exposed molecules. Within each density
    bin, the function selects up to the number of exposed test molecules in that
    bin. Selection is deterministic by `row_id`.
    """

    test = _test_frame_with_bins(df, density_column=density_column, bins=bins)
    exposed = test[test["exact_exposed"].fillna(False)]
    clean = test[~test["exact_exposed"].fillna(False)]
    if clean.empty:
        raise ValueError("Cannot build density-matched split without clean test rows")

    selected: list[int] = []
    selected_set: set[int] = set()
    exposed_counts = exposed["_density_bin"].value_counts().sort_index()
    if exposed_counts.empty:
        selected = clean.sort_values("row_id")["row_id"].astype(int).tolist()
    else:
        for bin_id, exposed_count in exposed_counts.items():
            remaining = clean[~clean["row_id"].astype(int).isin(selected_set)].copy()
            candidates = remaining[remaining["_density_bin"] == int(bin_id)].sort_values("row_id")
            if candidates.empty and not remaining.empty:
                remaining["_bin_distance"] = (remaining["_density_bin"].astype(int) - int(bin_id)).abs()
                candidates = remaining.sort_values(["_bin_distance", "row_id"])
            if candidates.empty:
                continue
            chosen = candidates.head(int(exposed_count))["row_id"].astype(int).tolist()
            selected.extend(chosen)
            selected_set.update(chosen)

    if not selected:
        raise ValueError("Density-matched clean test subset is empty")
    return {"train": _train_rows(df), "test": selected}


def density_control_table(
    df: pd.DataFrame,
    *,
    selected_test_ids: list[int],
    density_column: str = "max_nn_similarity_before_cutoff",
    bins: int = 5,
) -> pd.DataFrame:
    """Summarize exposed, clean, and selected clean counts by density bin."""

    test = _test_frame_with_bins(df, density_column=density_column, bins=bins)
    selected = set(int(row_id) for row_id in selected_test_ids)
    records = []
    for bin_id, group in test.groupby("_density_bin", sort=True):
        clean = group[~group["exact_exposed"].fillna(False)]
        exposed = group[group["exact_exposed"].fillna(False)]
        records.append(
            {
                "density_bin": int(bin_id),
                "density_min": float(group[density_column].fillna(0.0).min()),
                "density_max": float(group[density_column].fillna(0.0).max()),
                "exposed_test_n": int(len(exposed)),
                "clean_test_n": int(len(clean)),
                "selected_clean_test_n": int(clean["row_id"].astype(int).isin(selected).sum()),
            }
        )
    return pd.DataFrame.from_records(records)


def write_density_matched_clean_split(
    df: pd.DataFrame,
    *,
    output_path: str | Path,
    control_table_path: str | Path | None = None,
    density_column: str = "max_nn_similarity_before_cutoff",
    bins: int = 5,
) -> dict:
    split = density_matched_clean_split(df, density_column=density_column, bins=bins)
    payload = {
        "split_name": "density_matched_clean",
        "density_column": density_column,
        "bins": bins,
        "indices": split,
    }
    write_json(payload, output_path)
    if control_table_path is not None:
        table = density_control_table(
            df,
            selected_test_ids=split["test"],
            density_column=density_column,
            bins=bins,
        )
        write_dataframe(table, control_table_path)
    return payload


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--control-table", default="results/tables/density_matched_controls.csv")
    parser.add_argument("--density-column", default="max_nn_similarity_before_cutoff")
    parser.add_argument("--bins", type=int, default=5)
    args = parser.parse_args(argv)

    frame = read_dataframe(args.annotations)
    payload = write_density_matched_clean_split(
        frame,
        output_path=args.output,
        control_table_path=args.control_table,
        density_column=args.density_column,
        bins=args.bins,
    )
    print(payload)


if __name__ == "__main__":
    main()
