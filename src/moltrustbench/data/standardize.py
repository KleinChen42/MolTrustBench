"""Deterministic molecule standardization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from moltrustbench import __version__
from moltrustbench.chem import StandardizationError, standardize_smiles
from moltrustbench.io import ensure_parent, read_dataframe, write_dataframe, write_json


STANDARD_COLUMNS = [
    "canonical_smiles",
    "standard_smiles",
    "standard_inchikey",
    "murcko_scaffold_smiles",
    "standardization_backend",
]
REJECT_COLUMNS = ["source_name", "task_name", "row_id", "input_smiles", "reason"]


def standardize_dataframe(
    df: pd.DataFrame,
    *,
    smiles_col: str = "smiles",
    source_name: str = "",
    task_name: str = "",
    allow_fallback: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    records: list[dict] = []
    rejects: list[dict] = []
    for idx, row in df.reset_index(drop=True).iterrows():
        try:
            std = standardize_smiles(row.get(smiles_col, ""), allow_fallback=allow_fallback)
        except StandardizationError as exc:
            rejects.append(
                {
                    "source_name": source_name,
                    "task_name": task_name,
                    "row_id": int(idx),
                    "input_smiles": row.get(smiles_col, ""),
                    "reason": str(exc),
                }
            )
            continue
        enriched = row.to_dict()
        enriched.update(
            {
                "row_id": int(idx),
                "canonical_smiles": std.canonical_smiles,
                "standard_smiles": std.standard_smiles,
                "standard_inchikey": std.standard_inchikey,
                "murcko_scaffold_smiles": std.murcko_scaffold_smiles,
                "standardization_backend": std.standardization_backend,
                "moltrustbench_version": __version__,
            }
        )
        records.append(enriched)

    standardized = pd.DataFrame.from_records(records)
    rejected = pd.DataFrame.from_records(rejects, columns=REJECT_COLUMNS)
    report = {
        "source_name": source_name,
        "task_name": task_name,
        "input_rows": int(len(df)),
        "standardized_rows": int(len(standardized)),
        "rejected_rows": int(len(rejected)),
        "allow_fallback": bool(allow_fallback),
        "backends": sorted(standardized["standardization_backend"].unique().tolist()) if not standardized.empty else [],
    }
    return standardized, rejected, report


def write_standardization_outputs(
    standardized: pd.DataFrame,
    rejected: pd.DataFrame,
    report: dict,
    *,
    output_path: str | Path,
    rejected_path: str | Path = "data/processed/rejected_molecules.csv",
    report_path: str | Path = "data/processed/standardization_report.json",
) -> None:
    write_dataframe(standardized, output_path)
    ensure_parent(rejected_path)
    if Path(rejected_path).exists():
        previous = pd.read_csv(rejected_path)
        rejected = pd.concat([previous, rejected], ignore_index=True)
    rejected.to_csv(rejected_path, index=False)
    write_json(report, report_path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--smiles-col", default="smiles")
    parser.add_argument("--source-name", default="")
    parser.add_argument("--task-name", default="")
    parser.add_argument("--allow-fallback-standardizer", action="store_true")
    args = parser.parse_args(argv)

    df = read_dataframe(args.input)
    standardized, rejected, report = standardize_dataframe(
        df,
        smiles_col=args.smiles_col,
        source_name=args.source_name,
        task_name=args.task_name,
        allow_fallback=args.allow_fallback_standardizer,
    )
    write_standardization_outputs(standardized, rejected, report, output_path=args.output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
