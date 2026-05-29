# Submission Figure Map

Target journal: Briefings in Bioinformatics

Design rule: the main figures should tell the trustworthiness-audit story, not a leaderboard story. Temporal and threshold details can move to supplement when their sample-size limitations would distract from the main claim.

| Slot | Figure | Primary claim | Artifact | Status | Placement |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 | MolTrustBench workflow | Thesis/C5 | `results/figures/workflow_schematic.pdf`, `results/tables/workflow_artifact_map.csv` | available | Main |
| Fig. 2 | ChEMBL release timeline and first-seen distribution | C1 | `results/figures/release_histogram.pdf` | available | Main |
| Fig. 3 | Four-task exact/scaffold/NN exposure heatmap | C1/C2 | `results/figures/exposure_heatmap_coverage.pdf` | available | Main |
| Fig. 4 | Exposure-adjusted AUROC deltas with bootstrap CI | C3/R2/R8 | `results/figures/exposure_delta_ci.pdf` | available | Main |
| Fig. 5 | BACE/Tox21 sequence-family sensitivity | C3/C5 | `results/figures/bace_tox21_sequence_model_family.pdf` | available | Main |
| Fig. 6 | Assay-provenance heterogeneity map | C4/R10 | `results/figures/assay_conflict_map.pdf` | available | Main |
| Fig. 7 | Benchmark trust-card examples | C5 | `results/figures/trust_card_examples.pdf`, `results/tables/trust_card_examples.csv`, `results/report_cards/*_card.json` | available | Main |
| Fig. S7 | Train-label-shuffle null-control comparison | C3/R2/R6 negative-control check | `results/figures/label_shuffle_null_control.pdf`, `results/tables/label_shuffle_null_control_comparison.csv` | available | Supplement |
| Fig. S1 | Temporal-future decay | C3/R4 | `results/figures/temporal_decay.pdf` | available | Supplement |
| Fig. S2 | NN threshold sensitivity | C2/R2 | `results/figures/nn_threshold_sensitivity.pdf` | available | Supplement |
| Fig. S3 | BBBP/ClinTox model-family sensitivity | C3/C5 | `results/figures/model_family_exposure_sensitivity.pdf` | available | Supplement or main inset |
| Fig. S4 | BACE/Tox21 sequence delta CI | C3 statistical robustness | `results/figures/sequence_delta_ci.pdf` | available | Supplement |
| Fig. S5 | ESOL regression delta CI | C3 non-classification robustness / R8 boundary | `results/figures/regression_delta_ci.pdf` | available | Supplement |
| Fig. S6 or Table Sx | ChEMBL endpoint-native temporal evaluation | C3 endpoint-native temporal validity / R8 exposure-removed slice boundary | `results/tables/chembl_endpoint_temporal_metrics.csv`, `results/tables/chembl_endpoint_transformer_metrics.csv`, `results/tables/chembl_endpoint_temporal_expected_limitations.csv`, `results/tables/chembl_endpoint_transformer_expected_limitations.csv` | available | Supplement |
| Table Sz | Frozen FM embedding case studies | R5/R7 checkpoint-light FM wrapper boundary | `results/tables/fm_embedding_slice_metrics.csv`, `results/tables/fm_embedding_summary.csv`, `results/tables/cyp_fm_completed_integration_summary.json`, `results/tables/chemberta_100m_fm_slice_metrics.csv`, `results/tables/chemberta_100m_fm_completion_summary.json` | available | Supplement |
| Table Sa | CYP1A2/CYP2C19 endpoint extension | C4/R10 endpoint-native assay provenance breadth | `results/tables/cyp_endpoint_extension_split_summary.csv`, `results/tables/cyp_endpoint_extension_assay_provenance_summary.csv`, `results/tables/cyp_endpoint_extension_summary.json` | available | Supplement |
| Table Sc | DILI/hepatotoxicity endpoint extension | C4/R10 toxicology label provenance and exposure-removed slice limits | `results/tables/dili_tox_endpoint_candidate_screen.csv`, `results/tables/dili_hepatotoxicity_task_summary.csv`, `results/tables/dili_hepatotoxicity_split_summary.csv`, `results/tables/dili_hepatotoxicity_sequence_metrics.csv` | available | Supplement |
| Table Sb | CYP1A2/CYP2C19 sequence and label-shuffle rescue | C3/R2/R6 endpoint-native negative-control boundary | `results/tables/cyp_extension_sequence_metrics.csv`, `results/tables/cyp_extension_label_shuffle_rescue_metrics.csv`, `results/tables/cyp_extension_label_shuffle_null_summary.csv` | available | Supplement |

## Main-Text Table Map

| Table | Purpose | Artifact |
| --- | --- | --- |
| Table 1 | Dataset and task summary | derive from benchmark manifests and `results/tables/benchmark_coverage_exposure_summary.csv` |
| Table 2 | ChEMBL release summary | `results/tables/chembl_release_counts.csv` |
| Table 3 | Model/pretraining registry | `results/tables/model_pretraining_registry.csv` |
| Table 4 | Exposure rates by benchmark | `results/tables/benchmark_coverage_exposure_summary.csv` |
| Table 5 | Exposure-adjusted scores and CI | `results/tables/exposure_delta_ci.csv`, `results/tables/sequence_delta_ci.csv`, `results/tables/regression_delta_ci.csv` |
| Table 6 | Reporting checklist / trust card schema | `paper/bib_reviewer_preflight.md`, `results/report_cards/*_card.json` |
| Table Sx | Endpoint-native ChEMBL temporal task summary | `results/tables/chembl_endpoint_temporal_task_summary.csv`, `results/tables/chembl_endpoint_transformer_task_summary.csv`, `results/tables/chembl_endpoint_temporal_coverage.csv` |
| Table Sy | Train-label-shuffle null-control summary | `results/tables/label_shuffle_null_control_comparison.csv`, `results/tables/label_shuffle_limitation_summary.csv`, `results/tables/cyp_extension_label_shuffle_null_summary.csv` |
| Table Sz | Frozen FM embedding case-study summary | `results/tables/fm_embedding_summary.csv`, `results/tables/cyp_fm_completed_integration_summary.json`, `results/tables/chemberta_100m_fm_summary.csv`, with limitations from `results/tables/archived_fm_attempts/*` |
| Table Sa | CYP1A2/CYP2C19 endpoint extension summary | `results/tables/cyp_endpoint_extension_assay_provenance_summary.csv`, `results/tables/cyp_endpoint_extension_split_summary.csv` |
| Table Sb | CYP sequence and train-label-shuffle rescue summary | `results/tables/cyp_extension_sequence_metrics.csv`, `results/tables/cyp_extension_label_shuffle_rescue_metrics.csv`, `results/tables/cyp_extension_label_shuffle_null_pairs.csv` |

## Immediate Figure Tasks

1. Decide whether Fig. 4 should use the new CI plot directly or a polished derivative with fewer rows.
2. Move temporal decay to supplement unless additional temporal-future tasks are added.
3. Keep regression delta CI in supplement unless the editor asks for broader non-classification evidence in the main text.
4. Polish final captions so every figure states whether evidence is audit-only, performance-tested, endpoint-native, or a limitation boundary.
5. Keep the endpoint-native temporal wave in supplement unless a revised main-text Results section needs a compact temporal-validity panel; the main text should still cite its 1,260 valid endpoint-native sequence metrics, 240 expected limitations, and zero critical failures.
6. Keep train-label-shuffle as supplement-first Fig. S7, while stating that it is a negative-control check rather than a causal exposure-effect figure.
7. Keep MolFormer and ChemBERTa-100M frozen embeddings in the supplement or a short limitations paragraph; do not turn the 1290 combined frozen-FM rows into a foundation-model leaderboard.
8. Add CYP1A2/CYP2C19 to the assay-provenance supplement and add Table Sb for their sequence-baseline plus train-label-shuffle evidence; report expected exposure-removed slice limitations explicitly.
9. Add DILI/hepatotoxicity as Table Sc because it strengthens C4/R10 but its strict exposure-removed/temporal subsets are too small for a main performance claim.
