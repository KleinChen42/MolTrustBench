---
name: chembl-release-engineer
description: Build ChEMBL release manifests and earliest-public-release indexes for MolTrustBench. Use for ChEMBL SQLite downloads, molecule extraction, release manifests, hashing, and release count tables.
---

# ChEMBL Release Engineer

Required outputs:
- `data/manifests/chembl_<release>.json`
- `results/release_index/compound_release_index.parquet`
- `results/release_index/scaffold_release_index.parquet`
- `results/tables/chembl_release_counts.csv`

Workflow:
1. Preserve release id, date, DOI, source URL, and file hash.
2. Extract compound structures from SQLite without modifying source dumps.
3. Standardize molecules deterministically.
4. Compute earliest release per molecule and scaffold.
5. Write count tables for paper Table 2.

Failure checks:
- Missing release dates or hashes are critical.
- Duplicate standard InChIKeys across releases are expected, but earliest release must be stable.
- Empty standardized SMILES must be rejected and reported.
