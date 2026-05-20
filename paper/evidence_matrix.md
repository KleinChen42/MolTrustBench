# Evidence Matrix

| Claim | Scripts/modules | Outputs | Figures/tables | Status |
| --- | --- | --- | --- | --- |
| C1 | `src/moltrustbench/data/build_release_index.py`, `src/moltrustbench/audit/exact_exposure.py` | `results/benchmark_annotations/*_exposure.parquet`, `results/tables/exposure_summary.csv` | `results/figures/release_histogram.pdf`, `results/figures/exposure_heatmap.pdf` | preliminary |
| C2 | `src/moltrustbench/audit/scaffold_exposure.py`, `src/moltrustbench/audit/nearest_neighbor_exposure.py` | Exposure annotation columns `scaffold_exposed`, `nn_exposed_06`-`nn_exposed_09` | `results/figures/exposure_heatmap.pdf` | preliminary |
| C3 | `src/moltrustbench/splits/exposure_removed.py`, `src/moltrustbench/training/train.py`, `src/moltrustbench/evaluation/slice_metrics.py` | `results/tables/slice_metrics.csv`, `results/metrics/*.json` | `results/figures/performance_drop.pdf` | preliminary |
| C4 | `src/moltrustbench/audit/assay_provenance.py` | `results/tables/assay_provenance_summary.csv` | `results/figures/assay_conflict_map.pdf` | missing |
| C5 | `src/moltrustbench/audit/exposure_card.py`, `src/moltrustbench/reporting/make_manuscript_report.py` | `results/report_cards/*_card.json`, `paper/auto_report.md` | Table 6 reporting checklist | preliminary |

## Evidence Gates

- Fixture smoke outputs are engineering validation only; they do not promote C1
  or C2 beyond `preliminary`.
- Real ChEMBL24/27/30/33/36 artifacts plus zero critical sanity failures may
  promote C1/C2 to `supported`.
- Baseline performance deltas without density-matched controls keep C3 at
  `preliminary`, because R2 remains unresolved.
- Assay provenance must remain `missing` until real ChEMBL activity provenance
  extraction produces `assay_provenance_summary.csv`.
