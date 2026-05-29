# MolTrustBench Supplementary Tables

This supplement is organized as an audit-ready evidence package for Briefings in Bioinformatics. It maps compact source-data tables to claims C1-C5 and risk controls R1-R10. Large generated tables and raw-size artifacts are referenced through the data-freeze archive rather than duplicated here.

Terminology: public exposure, observable exposure lower bound, temporal validity, exposure-adjusted evaluation, assay provenance, train-label-shuffle null control, and expected exposure-removed slice limitations.

## Table Map

| Table | Title | Claim | Reviewer role | Rows | Supplement file |
| --- | --- | --- | --- | ---: | --- |
| Table_S1 | ChEMBL release-index summary | C1/C2 | R4/R9 | 5 | `tables/Table_S1_chembl_release_counts.csv` |
| Table_S2 | Benchmark exposure summary across audited tasks | C1/C2 | R1/R2 | 4 | `tables/Table_S2_benchmark_coverage_exposure_summary.csv` |
| Table_S3 | Core BBBP/ClinTox exposure-adjusted baseline metrics | C3 | R6/R8 | 16 | `tables/Table_S3_slice_metrics.csv` |
| Table_S4 | BACE/Tox21 C3 expansion metrics | C3 | R6/R8 | 30 | `tables/Table_S4_bace_tox21_c3_summary.csv` |
| Table_S5 | BACE/Tox21 sequence-family metrics | C3/C5 | R6/R8 | 60 | `tables/Table_S5_bace_tox21_sequence_summary.csv` |
| Table_S6 | Exposure-adjusted CI summary | C3 | R2/R6 | 80 | `tables/Table_S6_exposure_delta_ci.csv` |
| Table_S7 | Sequence-family CI summary | C3 | R2/R6 | 24 | `tables/Table_S7_sequence_delta_ci.csv` |
| Table_S8 | ESOL/Lipophilicity regression CI summary | C3 | R8 | 24 | `tables/Table_S8_regression_delta_ci.csv` |
| Table_S9 | Endpoint-native ChEMBL temporal metrics | C3/C4 | R4/R8/R10 | 108 | `tables/Table_S9_chembl_endpoint_temporal_summary.csv` |
| Table_S10 | Endpoint SMILES-Transformer add-on metrics | C3 | R6/R8 | 42 | `tables/Table_S10_chembl_endpoint_transformer_summary.csv` |
| Table_S11 | Train-label-shuffle null-control comparisons | C3 | R2/R6 | 22 | `tables/Table_S11_label_shuffle_null_control_comparison.csv` |
| Table_S12 | CYP label-shuffle rescue null summary | C3 | R2/R6/R8 | 3 | `tables/Table_S12_cyp_extension_label_shuffle_null_summary.csv` |
| Table_S13 | Frozen MolFormer embedding summary | C3 | R5/R7 | 57 | `tables/Table_S13_fm_embedding_summary.csv` |
| Table_S14 | Frozen ChemBERTa-100M embedding summary | C3 | R5/R7 | 30 | `tables/Table_S14_chemberta_100m_fm_summary.csv` |
| Table_S15 | Assay-provenance task summary with DILI/hepatotoxicity | C4 | R10 | 6 | `tables/Table_S15_assay_provenance_task_summary_with_dili.csv` |
| Table_S16 | CYP1A2/CYP2C19 assay-provenance summary | C4 | R10 | 2 | `tables/Table_S16_cyp_endpoint_extension_assay_provenance_summary.csv` |
| Table_S17 | DILI/hepatotoxicity split and provenance boundary | C4 | R8/R10 | 6 | `tables/Table_S17_dili_hepatotoxicity_split_summary.csv` |
| Table_S18 | DILI/hepatotoxicity sequence summary | C3/C4 | R8/R10 | 12 | `tables/Table_S18_dili_hepatotoxicity_sequence_summary.csv` |
| Table_S19 | Model pretraining registry | C5 | R5 | 12 | `tables/Table_S19_model_pretraining_registry.csv` |
| Table_S20 | Current reviewer controls and reporting checklist | C5 | R1-R10 | 10 | `tables/Table_S20_required_controls.csv` |
| Table_S21 | Trust-card example source data | C5 | R6 | 4 | `tables/Table_S21_trust_card_examples.csv` |
| Table_S22 | Workflow artifact map | C5 | R6 | 7 | `tables/Table_S22_workflow_artifact_map.csv` |
| Table_S23 | Expected limitation and critical-failure accounting | C3/C5 | R8 | 6 | `tables/Table_S23_expected_limitations_summary.csv` |
| Table_S24 | Slice-validity master table | C3 | R8 | 12626 | `tables/Table_S24_slice_validity_master.csv` |
| Table_S25 | Standardization audit summary | C1/C2 | R9 | 10 | `tables/Table_S25_standardization_audit.csv` |
| Table_S26 | Assay-provenance flag dictionary | C4 | R10 | 6 | `tables/Table_S26_assay_flag_dictionary.csv` |
| Table_S27 | Assay-provenance example rows | C4 | R10 | 22 | `tables/Table_S27_assay_provenance_examples.csv` |
| Table_S28 | Machine-readable trust-card schema | C5 | R6 | 11 | `tables/Table_S28_trust_card_schema.csv` |
| Table_S29 | Figure source-data map | C5 | R6 | 9 | `tables/Table_S29_figure_source_data_map.csv` |

## Reviewer-Use Notes

- Tables S1-S2 support public-exposure claims and should be read as observability lower bounds, not direct model-training evidence.
- Tables S3-S12 support exposure-adjusted evaluation, CI stability checks, and train-label-shuffle null controls. They do not prove causality.
- Tables S13-S14 are supplement-only frozen foundation-model wrapper checks. They do not imply that MolFormer or ChemBERTa-100M used ChEMBL during pretraining.
- Tables S15-S18 support assay-provenance and DILI/hepatotoxicity evidence. DILI exact/NN/temporal/density exposure-removed slices are expected one-class limitations.
- Table S23 is the expected-limitation boundary table: expected limitations are audit outputs, while critical-failure rows should remain zero for paper-facing claims.
- Table S24 is the slice-validity master table and should be used whenever a score delta is interpreted.
- Table S25 documents standardization assumptions and row accounting for R9.
- Tables S26-S27 define assay-provenance flags and give compact record-derived examples for R10.
- Table S28 and `trust_cards/` provide the machine-readable trust-card schema and examples behind the plotted cards.
- Table S29 maps each main figure to its compact source-data table.

## Data-Freeze Pointer

- Current local freeze archive: `moltrustbench_data_freeze_20260529_161700.tgz`
- Manifest: `moltrustbench_data_freeze_20260529_161700_manifest.csv`
- SHA256: `beb779864151105b3c8cd13507df8f0779bfc53e2d6a4f6a792d82f91e34b2df`
- File count: `3389`

If a newer freeze archive is created after this supplement, regenerate the package with `python scripts/make_bib_supplement_package.py`.
