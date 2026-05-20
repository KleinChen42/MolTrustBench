"""Annotate benchmark molecules with public-exposure columns."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from moltrustbench import __version__
from moltrustbench.audit.exposure_card import write_exposure_card
from moltrustbench.audit.nearest_neighbor_exposure import add_nn_exposure_columns
from moltrustbench.audit.scaffold_exposure import add_scaffold_exposure_columns
from moltrustbench.audit.trust_score import exposure_category, exposure_risk_score
from moltrustbench.constants import CHEMBL_RELEASES, EXPOSURE_THRESHOLDS
from moltrustbench.io import dataframe_manifest_id, read_dataframe, write_dataframe


def annotate_exposure(
    benchmark_df: pd.DataFrame,
    compound_index: pd.DataFrame,
    scaffold_index: pd.DataFrame,
    *,
    cutoff_release: str,
    allow_fallback: bool = False,
) -> pd.DataFrame:
    if cutoff_release not in CHEMBL_RELEASES:
        raise ValueError(f"Unknown cutoff release: {cutoff_release}")
    cutoff_order = CHEMBL_RELEASES[cutoff_release].order
    exact_cols = [
        "standard_inchikey",
        "standard_smiles",
        "first_seen_release",
        "first_seen_date",
        "first_seen_order",
    ]
    exact_index = compound_index[exact_cols].drop_duplicates("standard_inchikey")
    annotated = benchmark_df.merge(
        exact_index.rename(
            columns={
                "first_seen_release": "earliest_exact_release",
                "first_seen_date": "earliest_exact_date",
                "first_seen_order": "earliest_exact_order",
                "standard_smiles": "release_index_standard_smiles",
            }
        ),
        on="standard_inchikey",
        how="left",
    )
    annotated["exact_exposed"] = annotated["earliest_exact_order"].fillna(10**9) <= cutoff_order
    annotated = add_scaffold_exposure_columns(annotated, scaffold_index, cutoff_order=cutoff_order)
    public_index = compound_index[compound_index["first_seen_order"] <= cutoff_order]
    annotated = add_nn_exposure_columns(
        annotated,
        public_index,
        thresholds=EXPOSURE_THRESHOLDS,
        allow_fallback=allow_fallback,
    )
    annotated["exposure_category"] = annotated.apply(exposure_category, axis=1)
    annotated["exposure_risk_score"] = annotated.apply(exposure_risk_score, axis=1)
    annotated["cutoff_release"] = cutoff_release
    annotated["cutoff_order"] = cutoff_order
    annotated["moltrustbench_version"] = __version__
    annotated["input_manifest_id"] = dataframe_manifest_id(benchmark_df, prefix="exposure-input-")
    annotated["row_count"] = int(len(annotated))
    return annotated


def exposure_summary(annotated_frames: list[pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for frame in annotated_frames:
        if frame.empty:
            continue
        source = frame["source_name"].iloc[0]
        task = frame["task_name"].iloc[0]
        cutoff = frame["cutoff_release"].iloc[0]
        total = len(frame)
        rows.append(
            {
                "source_name": source,
                "task_name": task,
                "cutoff_release": cutoff,
                "n_molecules": int(total),
                "exact_exposure_rate": float(frame["exact_exposed"].mean()),
                "scaffold_exposure_rate": float(frame["scaffold_exposed"].mean()),
                "nn_exposure_rate_06": float(frame["nn_exposed_06"].mean()),
                "nn_exposure_rate_07": float(frame["nn_exposed_07"].mean()),
                "nn_exposure_rate_08": float(frame["nn_exposed_08"].mean()),
                "nn_exposure_rate_09": float(frame["nn_exposed_09"].mean()),
                "median_exposure_risk_score": float(frame["exposure_risk_score"].median()),
                "clean_exact_count": int((~frame["exact_exposed"]).sum()),
            }
        )
    return pd.DataFrame.from_records(rows)


def write_exposure_outputs(
    annotated: pd.DataFrame,
    *,
    output_dir: str | Path = "results/benchmark_annotations",
    card_dir: str | Path = "results/report_cards",
) -> tuple[Path, Path]:
    source = annotated["source_name"].iloc[0]
    task = annotated["task_name"].iloc[0]
    cutoff = annotated["cutoff_release"].iloc[0]
    out = Path(output_dir) / f"{source}_{task}_exposure.parquet"
    card = Path(card_dir) / f"{source}_{task}_card.json"
    write_dataframe(annotated, out)
    write_exposure_card(annotated, cutoff_release=cutoff, output_path=card)
    return out, card


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--compound-index", default="results/release_index/compound_release_index.parquet")
    parser.add_argument("--scaffold-index", default="results/release_index/scaffold_release_index.parquet")
    parser.add_argument("--cutoff-release", default="CHEMBL30")
    parser.add_argument("--allow-fallback-standardizer", action="store_true")
    args = parser.parse_args(argv)

    benchmark = read_dataframe(args.benchmark)
    compound = read_dataframe(args.compound_index)
    scaffold = read_dataframe(args.scaffold_index)
    annotated = annotate_exposure(
        benchmark,
        compound,
        scaffold,
        cutoff_release=args.cutoff_release,
        allow_fallback=args.allow_fallback_standardizer,
    )
    out, card = write_exposure_outputs(annotated)
    print(f"Wrote {out} and {card}")


if __name__ == "__main__":
    main()
