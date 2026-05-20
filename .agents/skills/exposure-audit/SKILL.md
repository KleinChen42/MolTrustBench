---
name: exposure-audit
description: Compute exact, scaffold, and nearest-neighbor public exposure for MolTrustBench benchmark molecules. Use for exposure annotations, report cards, exposure summary tables, trust scores, and exposure-adjusted benchmark splits.
---

# Exposure Audit

Required outputs:
- `results/benchmark_annotations/<benchmark>_<task>_exposure.parquet`
- `results/report_cards/<benchmark>_<task>_card.json`
- `results/tables/exposure_summary.csv`

Workflow:
1. Use exact standardized InChIKey exposure as the strict lower bound.
2. Use scaffold exposure and nearest-neighbor exposure to quantify broader time-travel risk.
3. Use cutoff releases explicitly.
4. Generate a trust card for every benchmark task.

Failure checks:
- Do not call exposure confirmed leakage.
- Empty clean subsets are critical for evaluation.
- NN exposure must report threshold and fingerprint method.
