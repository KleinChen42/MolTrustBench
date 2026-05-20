# Real-Data Exposure Gate

## Purpose

This gate turns the fixture smoke pipeline into the first paper-usable evidence
step. It follows the external `nature-writing`, `nature-figure`,
`nature-data`, and `academic-pipeline` guidance: claims must be supported by
inspectable artifacts, figures must carry distinct evidence, and manuscript
language must stay bounded by the data.

## Paper Claim Supported

- C1: measurable public-exposure risk at molecule, scaffold, and nearest-neighbor levels.
- C2: scaffold and nearest-neighbor exposure can reveal broader time-travel risk than exact molecule exposure.
- C5: reusable benchmark trust cards and reporting standards.

C3 remains preliminary until real baseline deltas are paired with density-matched
controls. C4 is not supported by this gate.

## Reviewer Objections Addressed

- R1: This does not prove confirmed leakage.
- R3: This duplicates ADMET reliability benchmarks.
- R4: ChEMBL release date is not model training date.
- R6: The work is just data cleaning.
- R8: Clean subsets are too small.
- R9: The conclusions depend on molecule standardization.

R2 remains open until density-matched controls are run.

## Proof Artifacts

- `results/release_index/compound_release_index.parquet`
- `results/release_index/scaffold_release_index.parquet`
- `results/tables/chembl_release_counts.csv`
- `results/benchmark_annotations/*_exposure.parquet`
- `results/report_cards/*_card.json`
- `results/tables/exposure_summary.csv`
- `results/figures/release_histogram.pdf`
- `results/figures/exposure_heatmap.pdf`
- `paper/auto_report.md`

## Sanity Checks

- `chembl_release_counts.csv` contains CHEMBL24, CHEMBL27, CHEMBL30, CHEMBL33, and CHEMBL36.
- At least two non-fixture benchmark tasks have exposure annotation parquet files.
- `exposure_summary.csv` has non-fixture task rows.
- Standardization reports record rejected molecules and deterministic identifiers.
- Sanity checker passes with no critical errors.
- `paper/auto_report.md` distinguishes real ChEMBL evidence from fixture smoke evidence.

## Figure Contract

- `release_histogram.pdf`: supports C1 by showing earliest public observability.
- `exposure_heatmap.pdf`: supports C1/C2 by separating exact, scaffold, and nearest-neighbor exposure.
- `performance_drop.pdf`: remains C3-preliminary unless paired with density-matched controls.

No figure should be described as proof of model memorization or confirmed leakage.
