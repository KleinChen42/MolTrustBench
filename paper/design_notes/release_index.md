# Design Note: ChEMBL Release Index

Paper claim: C1, C2.

Reviewer objection: R4, R9.

Output file proving success:
- `results/release_index/compound_release_index.parquet`
- `results/release_index/scaffold_release_index.parquet`
- `results/tables/chembl_release_counts.csv`

Sanity checks:
- Every release has a date and DOI.
- Every standardized molecule has a deterministic identifier.
- Earliest release is stable across repeated runs.
- Rejected molecules are reported, not silently dropped.
