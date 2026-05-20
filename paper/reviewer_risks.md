# Reviewer Risks And Controls

| Risk | Reviewer attack | Mitigation experiment | Script path | Expected output | Current status |
| --- | --- | --- | --- | --- | --- |
| R1 | This does not prove confirmed leakage. | Use conservative terminology and define exposure as an observable lower bound. | `paper/manuscript_skeleton.md` | Terminology box and limitations paragraph | preliminary |
| R2 | Exposure is just chemical-space density. | Add nearest-neighbor baseline and density-matched clean controls. | `src/moltrustbench/splits/density_matched.py` | `results/tables/density_matched_controls.csv` | missing |
| R3 | This duplicates ADMET reliability benchmarks. | Position against ADMET/OOD work and focus on benchmark temporal validity. | `paper/target_journal_positioning.md` | Novelty boundary section | preliminary |
| R4 | ChEMBL release date is not model training date. | Report release cutoff as public observability, not model-specific proof. | `src/moltrustbench/audit/exposure_card.py` | Trust card auditability notes | preliminary |
| R5 | Models may not have used ChEMBL. | Separate ChEMBL exposure lower bound from model pretraining registry. | `configs/models/*.yaml` | Model registry table | missing |
| R6 | The work is just data cleaning. | Add exposure-adjusted scores, trust cards, and slice performance deltas. | `src/moltrustbench/evaluation/adjusted_scores.py` | `results/tables/slice_metrics.csv` | preliminary |
| R7 | Foundation model wrappers are incomplete. | Keep FMs as case studies, not Milestone 1 acceptance criteria. | `src/moltrustbench/models/fm_wrappers.py` | Wrapper registry | missing |
| R8 | Clean subsets are too small. | Sanity checker fails or warns on empty and low-size clean subsets. | `src/moltrustbench/evaluation/sanity_checks.py` | `results/tables/sanity_report.csv` | preliminary |
| R9 | Conclusions depend on molecule standardization. | Persist rejected molecules and standardization report. | `src/moltrustbench/data/standardize.py` | `data/processed/standardization_report.json` | preliminary |
| R10 | Assay labels are noisy and threshold-dependent. | Extract assay provenance and threshold sensitivity. | `src/moltrustbench/audit/assay_provenance.py` | `results/tables/assay_provenance_summary.csv` | missing |
