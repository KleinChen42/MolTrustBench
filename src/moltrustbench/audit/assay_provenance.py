"""Assay-provenance audit interface for later MolTrustBench phases."""

from __future__ import annotations

import pandas as pd


ASSAY_PROVENANCE_COLUMNS = [
    "assay_id",
    "document_id",
    "target_id",
    "assay_type",
    "standard_type",
    "standard_relation",
    "standard_value",
    "standard_units",
    "pchembl_value",
    "confidence_score",
    "source_release",
]


def summarize_assay_provenance(activity_df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in ASSAY_PROVENANCE_COLUMNS if column not in activity_df.columns]
    if missing:
        raise ValueError(f"Missing assay provenance columns: {missing}")
    grouped = activity_df.groupby("standard_inchikey", dropna=False)
    rows = []
    for inchikey, group in grouped:
        rows.append(
            {
                "standard_inchikey": inchikey,
                "duplicate_activity_count": int(len(group)),
                "unique_assay_count": int(group["assay_id"].nunique()),
                "unique_document_count": int(group["document_id"].nunique()),
                "unit_inconsistency": bool(group["standard_units"].nunique(dropna=True) > 1),
                "source_release_count": int(group["source_release"].nunique(dropna=True)),
            }
        )
    return pd.DataFrame.from_records(rows)
