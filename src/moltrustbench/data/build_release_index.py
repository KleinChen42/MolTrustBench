"""Build earliest-public-release indexes from ChEMBL releases."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from moltrustbench import __version__
from moltrustbench.chem import rdkit_available
from moltrustbench.constants import CHEMBL_RELEASES
from moltrustbench.data.standardize import standardize_dataframe
from moltrustbench.io import dataframe_manifest_id, ensure_dir, file_sha256, write_dataframe, write_json


def read_chembl_sqlite(sqlite_path: str | Path) -> pd.DataFrame:
    path = Path(sqlite_path)
    with sqlite3.connect(path) as conn:
        columns = pd.read_sql_query("PRAGMA table_info(compound_structures)", conn)
        names = set(columns["name"].tolist())
        smiles_col = "canonical_smiles" if "canonical_smiles" in names else "molfile"
        inchikey_col = "standard_inchi_key" if "standard_inchi_key" in names else None
        select = f"SELECT molregno, {smiles_col} AS smiles"
        if inchikey_col:
            select += f", {inchikey_col} AS source_inchikey"
        select += " FROM compound_structures WHERE smiles IS NOT NULL"
        return pd.read_sql_query(select, conn)


def build_release_indexes(
    release_frames: dict[str, pd.DataFrame],
    *,
    allow_fallback: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    compound_rows: list[pd.DataFrame] = []
    rejected_rows: list[pd.DataFrame] = []
    count_rows: list[dict] = []

    for release_id, frame in release_frames.items():
        if release_id not in CHEMBL_RELEASES:
            raise ValueError(f"Unknown release id: {release_id}")
        info = CHEMBL_RELEASES[release_id]
        standardized, rejected, _ = standardize_dataframe(
            frame,
            smiles_col="smiles",
            source_name="chembl",
            task_name=release_id,
            allow_fallback=allow_fallback,
        )
        standardized["chembl_release"] = release_id
        standardized["release_order"] = info.order
        standardized["release_date"] = info.date
        standardized["release_doi"] = info.doi
        standardized["source_name"] = "chembl"
        standardized["task_name"] = release_id
        standardized["input_manifest_id"] = dataframe_manifest_id(frame, prefix=f"{release_id.lower()}-")
        standardized["row_count"] = int(len(standardized))
        compound_rows.append(standardized)
        rejected_rows.append(rejected)
        count_rows.append(
            {
                "chembl_release": release_id,
                "release_date": info.date,
                "release_doi": info.doi,
                "input_rows": int(len(frame)),
                "standardized_rows": int(len(standardized)),
                "unique_standard_inchikey": int(standardized["standard_inchikey"].nunique()),
                "unique_scaffold": int(standardized["murcko_scaffold_smiles"].nunique()),
                "rejected_rows": int(len(rejected)),
            }
        )

    all_compounds = pd.concat(compound_rows, ignore_index=True) if compound_rows else pd.DataFrame()
    rejected_all = pd.concat(rejected_rows, ignore_index=True) if rejected_rows else pd.DataFrame(columns=["source_name", "task_name", "row_id", "input_smiles", "reason"])
    counts = pd.DataFrame.from_records(count_rows)

    if all_compounds.empty:
        return all_compounds, pd.DataFrame(), counts, rejected_all

    sorted_compounds = all_compounds.sort_values(["standard_inchikey", "release_order"])
    first_compounds = sorted_compounds.groupby("standard_inchikey", as_index=False).first()
    observed = (
        sorted_compounds.groupby("standard_inchikey")["chembl_release"]
        .apply(lambda values: "|".join(sorted(set(values), key=lambda value: CHEMBL_RELEASES[value].order)))
        .reset_index(name="observed_releases")
    )
    compound_index = first_compounds.merge(observed, on="standard_inchikey", how="left")
    compound_index = compound_index.rename(
        columns={
            "chembl_release": "first_seen_release",
            "release_date": "first_seen_date",
            "release_order": "first_seen_order",
        }
    )
    compound_index["chembl_release"] = compound_index["first_seen_release"]
    compound_index["cutoff_release"] = ""
    compound_index["moltrustbench_version"] = __version__

    scaffold_source = all_compounds[all_compounds["murcko_scaffold_smiles"].fillna("") != ""].copy()
    scaffold_sorted = scaffold_source.sort_values(["murcko_scaffold_smiles", "release_order"])
    scaffold_index = scaffold_sorted.groupby("murcko_scaffold_smiles", as_index=False).first()
    scaffold_index = scaffold_index.rename(
        columns={
            "chembl_release": "first_seen_release",
            "release_date": "first_seen_date",
            "release_order": "first_seen_order",
        }
    )
    scaffold_index["chembl_release"] = scaffold_index["first_seen_release"]
    scaffold_index["moltrustbench_version"] = __version__
    return compound_index, scaffold_index, counts, rejected_all


def write_release_outputs(
    compound_index: pd.DataFrame,
    scaffold_index: pd.DataFrame,
    counts: pd.DataFrame,
    rejected: pd.DataFrame,
    *,
    output_dir: str | Path = "results/release_index",
    tables_dir: str | Path = "results/tables",
    rejected_path: str | Path = "data/processed/rejected_molecules.csv",
) -> None:
    ensure_dir(output_dir)
    ensure_dir(tables_dir)
    write_dataframe(compound_index, Path(output_dir) / "compound_release_index.parquet")
    write_dataframe(scaffold_index, Path(output_dir) / "scaffold_release_index.parquet")
    write_dataframe(counts, Path(tables_dir) / "chembl_release_counts.csv")
    write_dataframe(rejected, rejected_path)


def fixture_release_frames() -> dict[str, pd.DataFrame]:
    return {
        "CHEMBL24": pd.DataFrame({"smiles": ["CCO", "CCN", "c1ccccc1", "CCCl", "CCCO"]}),
        "CHEMBL27": pd.DataFrame({"smiles": ["CC(=O)O", "c1ccncc1", "CCBr", "CC(C)O"]}),
        "CHEMBL30": pd.DataFrame({"smiles": ["CCOC", "CC(C)N", "O=C=O", "CC(C)C"]}),
        "CHEMBL33": pd.DataFrame({"smiles": ["CCCN", "CC(C)(C)O", "c1ccccc1O", "CCS"]}),
        "CHEMBL36": pd.DataFrame({"smiles": ["CCCCC", "CCN(CC)CC", "COC(=O)N"]}),
    }


def build_fixture_release_index(*, allow_fallback: bool = True) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return build_release_indexes(fixture_release_frames(), allow_fallback=allow_fallback)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-sqlite", action="append", default=[], help="Mapping like CHEMBL24=path/to/chembl_24.db")
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--allow-fallback-standardizer", action="store_true")
    parser.add_argument("--output-dir", default="results/release_index")
    parser.add_argument("--tables-dir", default="results/tables")
    args = parser.parse_args(argv)

    if args.fixture:
        frames = fixture_release_frames()
        manifests = {}
    else:
        if args.allow_fallback_standardizer:
            raise SystemExit("Fallback standardization is only allowed for fixtures; install RDKit for real ChEMBL indexing.")
        if not rdkit_available():
            raise SystemExit("RDKit is required for real ChEMBL indexing. Use the conda environment from environment.yml.")
        frames = {}
        manifests = {}
        for item in args.release_sqlite:
            release_id, raw_path = item.split("=", 1)
            frames[release_id] = read_chembl_sqlite(raw_path)
            manifests[release_id] = {"sqlite_path": raw_path, "sha256": file_sha256(raw_path)}
        if not frames:
            raise SystemExit("Provide --release-sqlite CHEMBLxx=path or --fixture")

    compound_index, scaffold_index, counts, rejected = build_release_indexes(
        frames,
        allow_fallback=args.allow_fallback_standardizer,
    )
    write_release_outputs(compound_index, scaffold_index, counts, rejected, output_dir=args.output_dir, tables_dir=args.tables_dir)
    for release_id, manifest in manifests.items():
        manifest.update({"release_id": release_id, "moltrustbench_version": __version__})
        write_json(manifest, Path("data/manifests") / f"chembl_{release_id.lower()}.json")
    print(f"Wrote {len(compound_index)} compound rows and {len(scaffold_index)} scaffold rows.")


if __name__ == "__main__":
    main()
