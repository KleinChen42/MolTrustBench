"""Publication table generation helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from moltrustbench.io import write_dataframe


def make_dataset_summary(annotation_paths: list[str | Path], output_path: str | Path = "results/tables/dataset_summary.csv") -> pd.DataFrame:
    rows = []
    for path in annotation_paths:
        frame = pd.read_parquet(path)
        rows.append(
            {
                "source_name": frame["source_name"].iloc[0],
                "task_name": frame["task_name"].iloc[0],
                "n_molecules": int(len(frame)),
                "train_n": int((frame["split"] == "train").sum()),
                "test_n": int((frame["split"] == "test").sum()),
                "positive_rate": float(frame["label"].mean()),
            }
        )
    table = pd.DataFrame.from_records(rows)
    write_dataframe(table, output_path)
    return table
