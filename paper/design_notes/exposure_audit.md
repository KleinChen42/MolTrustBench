# Design Note: Exposure Audit

Paper claim: C1, C2, C5.

Reviewer objection: R1, R2, R4.

Output file proving success:
- `results/benchmark_annotations/<benchmark>_<task>_exposure.parquet`
- `results/report_cards/<benchmark>_<task>_card.json`
- `results/tables/exposure_summary.csv`

Sanity checks:
- Exposure cutoff is explicit.
- Exact exposure uses standardized molecule identifiers.
- Scaffold and nearest-neighbor exposure are reported separately.
- The report uses public-exposure language, not confirmed-leakage language.
