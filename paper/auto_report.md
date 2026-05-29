# MolTrustBench Auto Report

## Executive Summary

MolTrustBench audits molecular benchmark trustworthiness through observable
public-exposure lower bounds, exposure-adjusted evaluation, assay provenance,
and benchmark trust cards. This report is based on real ChEMBL24/27/30/33/36
`chemreps.txt.gz` release-index artifacts, ChEMBL36 SQLite assay-provenance
tables, and integrated GPU outputs synced after the completed GPU0-7 run wave.

Current paper-facing integration includes the overnight endpoint
SMILES-Transformer add-on, the original train-label-shuffle null-control run,
the CYP1A2/CYP2C19 sequence extension, the CYP label-shuffle integration,
the CYP-specific MolFormer run, the 20-seed MolFormer expansion, a second
safetensors-compatible ChemBERTa-100M frozen-embedding wrapper, and a
DILI/hepatotoxicity ChEMBL36 assay-provenance endpoint. GPU0/GPU5 low-value
tail processes were stopped after rescue coverage had already been integrated;
they are not counted as paper-facing evidence.

## Claim-By-Claim Evidence Status

- C1 supported: real ChEMBL release-index artifacts and four-task exposure
  coverage are available for BBBP, ClinTox, BACE, and Tox21.
- C2 supported: exact, scaffold, and nearest-neighbor public exposure are
  reported separately, with NN-threshold sensitivity outputs.
- C3 supported: classification and sequence-family exposure-adjusted metrics
  cover BBBP, ClinTox, BACE, and Tox21; ESOL adds regression robustness; and
  endpoint-native ChEMBL hERG/CYP tasks add temporal validity evidence. The
  endpoint SMILES-Transformer add-on, CYP1A2/CYP2C19 sequence baselines, and
  train-label-shuffle null controls add model-family and negative-control
  evidence. Frozen FM evidence now includes 1140 MolFormer rows and 150
  ChemBERTa-100M rows as checkpoint-light wrapper checks. This is not yet
  `strong` because some exposure-removed and temporal-future subsets remain limited or
  class-degenerate, and the FM evidence is wrapper applicability evidence rather
  than model-specific pretraining-exposure evidence.
- C4 supported: ChEMBL36 SQLite assay-provenance extraction generated
  molecule-level and task-level conflict summaries, including endpoint-native
  ChEMBL-derived hERG, CYP1A2, CYP2C19, and DILI/hepatotoxicity evidence.
- C5 supported: workflow schematic, plotted trust-card examples, reporting
  checks, CI tables, reviewer preflight, expected-limitation accounting, and a
  conservative model pretraining registry are generated.

## Exposure Audit Summary

| source_name | task_name | cutoff_release | n_molecules | exact_exposure_rate | scaffold_exposure_rate | nn_exposure_rate_08 | exact_unobserved_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| moleculenet | BBBP | CHEMBL30 | 2039 | 0.8377 | 0.8779 | 0.8892 | 331 |
| moleculenet | ClinTox | CHEMBL30 | 1480 | 0.4736 | 0.7372 | 0.5993 | 779 |
| moleculenet | BACE | CHEMBL30 | 1513 | 0.2974 | 0.4270 | 0.3939 | 1063 |
| moleculenet | Tox21 | CHEMBL30 | 7258 | 0.9208 | 0.7530 | 0.9585 | 575 |

Interpretation: public exposure is measurable across all four completed tasks,
but the profile is heterogeneous. BACE has a larger exact-unobserved subset, while
Tox21 is already highly exact-exposed by CHEMBL30. This supports benchmark
trust cards rather than a one-size-fits-all leaderboard interpretation.

Primary artifacts: `results/tables/benchmark_coverage_exposure_summary.csv`,
`results/figures/exposure_heatmap_coverage.pdf`, and
`results/report_cards/*_card.json`.

## Exposure-Adjusted Evaluation Summary

The first BBBP/ClinTox baselines show that standard and exact-removed scores can
diverge in task-dependent directions. BBBP classical AUROC increased on
exact-removed subsets, while ClinTox decreased. This is score-sensitivity
evidence under exposure-adjusted evaluation, not proof of model-specific
training exposure.

Primary artifacts: `results/tables/slice_metrics.csv`,
`results/tables/density_matched_slice_metrics.csv`,
`results/tables/temporal_metrics.csv`, `results/figures/performance_drop.pdf`,
and `results/figures/temporal_decay.pdf`.

## Model-Family And Delta-CI Summary

BACE/Tox21 sequence-family integration retained 1200/1200 expected unique run
IDs across SMILES-CNN, SMILES-GRU, and SMILES-Transformer baselines, two hidden
dimensions, 20 seeds, and five exposure-aware splits. Duplicate raw metric rows
were audited and removed by `run_id`.

Paired CI artifacts:

- `results/tables/exposure_delta_ci.csv`
- `results/tables/sequence_delta_ci.csv`
- `results/figures/exposure_delta_ci.pdf`
- `results/figures/sequence_delta_ci.pdf`

Interpretation: most BACE/Tox21 sequence-family deltas have bootstrap intervals
excluding zero, but some Tox21 SMILES-GRU deltas cross zero. The manuscript
should therefore state that exposure-adjusted evaluation changes performance
interpretation in a task- and model-family-dependent way.

## Regression Expansion

The ESOL/Lipophilicity regression expansion was integrated from five remote run
roots after all GPUs became idle.

- Metric tables: 18
- Unique metric rows after `run_id` deduplication: 1200
- Failure rows: 4160
- Expected-limitation rows: 4160
- Critical failure rows: 0
- Valid regression CI task: ESOL

ESOL generated 960 paired standard-vs-exposure-aware regression deltas and 24
summary rows across SMILES-CNN, SMILES-GRU, and SMILES-Transformer. Twenty-two
of the 24 RMSE intervals exclude zero. Lipophilicity produced standard-split
metrics, but exposure-aware slices were too small or absent under the
current cutoff and are recorded as expected limitations.

Primary artifacts: `results/tables/regression_sequence_slice_metrics.csv`,
`results/tables/regression_sequence_expected_limitations.csv`,
`results/tables/regression_sequence_critical_failures.csv`,
`results/tables/regression_delta_ci.csv`, and
`results/figures/regression_delta_ci.pdf`.

## Endpoint-Native ChEMBL Temporal Wave

The ChEMBL endpoint-temporal wave was synced from
`/mnt/data1/zetyun/MolTrustBench/runs/bib_wave_gpu1_7_endpoint_temporal_20260526T050048Z`
and integrated from the archived local source
`results/remote_runs/bib_wave_gpu1_7_endpoint_temporal_20260526T050048Z_full.tgz`.

- Valid metric rows: 840
- Summary rows: 108
- Expected-limitation rows: 180
- Critical failure rows: 0
- Tasks: hERG, CYP3A4, CYP2D6, and CYP2C9 endpoint-native temporal tasks
- Models: SMILES-CNN and SMILES-GRU

The 180 expected-limitation rows come from CYP2C9 one-class exposure-removed subsets after
strict exposure filtering. This is a useful audit result: MolTrustBench
does not hide failed exposure-removed slice construction, and it distinguishes temporal
validity evidence from endpoint-specific sample-size limits.

Primary artifacts: `results/tables/chembl_endpoint_temporal_metrics.csv`,
`results/tables/chembl_endpoint_temporal_summary.csv`,
`results/tables/chembl_endpoint_temporal_expected_limitations.csv`,
`results/tables/chembl_endpoint_temporal_critical_failures.csv`, and
`results/tables/chembl_endpoint_temporal_integration_summary.json`.

## Endpoint Transformer And Null-Control Add-On

The overnight GPU0-7 wave added a SMILES-Transformer endpoint-native temporal
extension and train-label-shuffle null controls.

Endpoint SMILES-Transformer:

- Valid metric rows: 420
- Summary rows: 42
- Expected-limitation rows: 60
- Critical failure rows: 0
- Tasks: hERG, CYP3A4, CYP2D6, and CYP2C9 endpoint-native temporal tasks

Train-label-shuffle null controls:

- Valid metric rows: 360
- Summary rows: 36
- Expected-limitation rows: 180
- Critical failure rows: 0
- Valid tasks: Tox21, hERG, CYP3A4, CYP2D6, and CYP2C9

The train-label-shuffle controls preserve molecules, splits, and test labels
while permuting training labels. They are negative controls for R2/R6: they ask
whether exposure-adjusted deltas appear even when the training signal is broken.
The comparison table aligns 22 observed-label and train-label-shuffle deltas;
18 comparisons have larger observed absolute deltas than shuffle-control
absolute deltas, while four comparisons remain null-sensitive. BACE
label-shuffle controls are retained only as a limitation because the current
BACE exposure annotation has a one-class standard test split.

CYP label-shuffle integration:

- Rescue coverage: 80/80 unique CYP2C19 SMILES-GRU metric rows
- Integrated metric rows: 360
- Expected exposure-removed slice limitation rows: 1080
- Critical failure rows: 0
- Paired observed-vs-shuffled temporal-delta rows: 120
- Paired task coverage: CYP2C19; CYP1A2 has no paired temporal-delta rows in
  this snapshot and is retained as a coverage boundary.

Primary artifacts:
`results/tables/chembl_endpoint_transformer_metrics.csv`,
`results/tables/chembl_endpoint_transformer_expected_limitations.csv`,
`results/tables/label_shuffle_slice_metrics.csv`,
`results/tables/label_shuffle_null_control_comparison.csv`,
`results/tables/label_shuffle_limitation_summary.csv`,
`results/tables/cyp_extension_label_shuffle_rescue_metrics.csv`,
`results/tables/cyp_extension_label_shuffle_null_pairs.csv`,
`results/tables/cyp_extension_label_shuffle_null_summary.csv`,
`results/tables/overnight_gpu0_7_integration_summary.json`, and
`results/figures/label_shuffle_null_control.pdf`.

## Assay Provenance Summary

| source_name | task_name | benchmark_molecule_count | molecules_with_activity | activity_coverage_rate | duplicate_compound_count | conflicting_label_count | unit_inconsistency_count | threshold_sensitive_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| moleculenet | BBBP | 1971 | 1289 | 0.6540 | 1215 | 677 | 932 | 728 |
| moleculenet | ClinTox | 1455 | 654 | 0.4495 | 648 | 502 | 613 | 524 |
| chembl_bioactivity | hERG_pchembl5_pilot | 4999 | 4999 | 1.0000 | 1591 | 163 | 0 | 2646 |

The DILI/hepatotoxicity extension adds a text-evidence toxicology endpoint from
ChEMBL36: 528 labeled activity records, 513 benchmark molecules, 369 positive
and 144 negative molecules, 514 molecules with assay-provenance summaries, and
one provenance-level positive/no-evidence text-label conflict. Tied text-label
evidence is excluded from the final benchmark labels. Its standard
test split is evaluable (103 molecules; 29 negative and 74 positive), while
exact-removed, NN@0.8-removed, temporal-future, and density-matched
slices are expected exposure-removed slice limitations because they shrink to one-class
two-molecule tests; scaffold-removed remains evaluable with 12 test molecules.

Interpretation: C4 is supported because ChEMBL36 SQLite records reveal duplicate
measurements, unit heterogeneity, threshold sensitivity, and derived label
conflict risk. MoleculeNet overlap should be described as public assay
heterogeneity for overlapping molecules; hERG, CYP1A2, CYP2C19, and
DILI/hepatotoxicity are cleaner endpoint-native ChEMBL-derived provenance cases.

Primary artifacts: `results/tables/assay_provenance_activities.csv`,
`results/tables/assay_provenance_summary.csv`,
`results/tables/assay_provenance_task_summary.csv`,
`results/tables/dili_tox_endpoint_candidate_screen.csv`,
`results/tables/dili_hepatotoxicity_assay_provenance_summary.csv`,
`results/tables/dili_hepatotoxicity_task_summary.csv`, and
`results/figures/assay_conflict_map.pdf`.

## Foundation-Model Case Study Status

The frozen FM embedding case study now provides checkpoint-light wrapper checks
using staged safetensors checkpoints. MolFormer remains the larger case study;
ChemBERTa-100M is a second wrapper applicability check, not a ranking claim.

- Metrics rows: 1140 consolidated rows
- CYP-specific MolFormer rows: 240
- 20-seed MolFormer expansion rows: 900
- ChemBERTa-100M rows: 150
- ChemBERTa-100M failure rows: 0
- MolFormer failure rows: 0
- Tasks: BACE, Tox21, BBBP, ClinTox, ESOL, hERG, CYP3A4, CYP2D6, CYP2C9,
  CYP1A2, and CYP2C19 for MolFormer; BACE, Tox21, BBBP, ClinTox, CYP1A2, and
  CYP2C19 for ChemBERTa-100M
- Splits: standard, exact-removed, scaffold-removed, NN>=0.8-removed,
  density-matched, and available temporal-future slices

Artifacts: `results/tables/fm_embedding_slice_metrics.csv`,
`results/tables/fm_embedding_summary.csv`,
`results/tables/cyp_extension_molformer_fm_metrics.csv`,
`results/tables/molformer_fm_20seed_metrics.csv`,
`results/tables/cyp_fm_completed_integration_summary.json`,
`results/tables/chemberta_100m_fm_slice_metrics.csv`, and
`results/tables/chemberta_100m_fm_completion_summary.json`.

Interpretation: this is R7 wrapper applicability evidence for two staged
safetensors wrappers, not model-specific pretraining-exposure evidence. The
prior zero-metric blocked FM attempts are preserved under
`results/tables/archived_fm_attempts/` as runtime/artifact-format limitations,
not as scientific negative results.

## CYP Endpoint Extension

The CYP endpoint extension adds endpoint-native ChEMBL36 evidence for CYP1A2
and CYP2C19.

- Annotation files: `data/processed/benchmarks/chembl_CYP1A2_pchembl5_temporal.parquet`
  and `data/processed/benchmarks/chembl_CYP2C19_pchembl5_temporal.parquet`
- Split summary rows: 12
- Assay provenance summary rows: 2
- Observed-label sequence metrics: 360
- Observed-label expected exposure-removed slice limitations: 1080
- Observed-label critical failures: 0
- Train-label-shuffle rescue metrics: 360
- Train-label-shuffle expected exposure-removed slice limitations: 1080
- Train-label-shuffle critical failures: 0

Primary artifacts: `results/tables/cyp_endpoint_extension_split_summary.csv`,
`results/tables/cyp_endpoint_extension_assay_provenance_summary.csv`,
`results/tables/cyp_endpoint_extension_summary.json`,
`results/tables/cyp_extension_sequence_metrics.csv`,
`results/tables/cyp_extension_label_shuffle_rescue_metrics.csv`, and
`results/tables/cyp_extension_label_shuffle_null_summary.csv`.

## DILI/Hepatotoxicity Endpoint Extension

The DILI/hepatotoxicity endpoint adds a broader toxicology-oriented C4/R10
case study from ChEMBL36 text evidence rather than pChEMBL potency values.

- Labeled activity rows: 528
- Benchmark molecules after release-index merge: 513
- Positive/negative molecules: 369/144
- Assay-provenance molecule summaries: 514
- Binary text-label conflict molecules: 1
- Evaluable sequence metrics: 60
- Sequence failure rows: 0
- Evaluable splits: standard and scaffold-removed
- Expected exposure-removed slice limitations: exact-removed, NN@0.8-removed,
  temporal-future, and density-matched shrink to one-class two-molecule
  tests and should not be overinterpreted.

Primary artifacts: `results/tables/dili_tox_endpoint_candidate_screen.csv`,
`data/processed/benchmarks/chembl_DILI_hepatotoxicity_binary_temporal.parquet`,
`results/tables/dili_hepatotoxicity_split_summary.csv`,
`results/tables/dili_hepatotoxicity_sequence_metrics.csv`, and
`results/tables/dili_hepatotoxicity_sequence_completion_summary.json`.

## Reviewer Risk Summary

The central limitation is explicit: public exposure is an observable lower
bound, not proof that a model trained on a molecule or recalled a label.
Density-matched controls, NN-threshold sensitivity, paired CI tables,
train-label-shuffle null controls, assay provenance, endpoint-native temporal
tasks, expected-limitation accounting, and a model pretraining registry now
defend the main BIB reviewer attacks.
Remaining vulnerable areas are checkpoint-level pretraining metadata and broader
temporal-future coverage across endpoints; small exposure-removed/temporal DILI slices are
explicitly reported as expected limitations.

## Sanity Check Summary

Core real-data sanity checks pass with zero critical failures when run with:

`PYTHONPATH=src python -m moltrustbench.evaluation.sanity_checks --fail-on-critical`

The smoke-test target also passes in an isolated fixture directory:

`.\make.ps1 smoke-test`

## Submission Figure Closure

The final paper-facing C5 figures are now generated and mapped to artifacts.

- Fig. 1 workflow: `results/figures/workflow_schematic.pdf`,
  `results/figures/workflow_schematic.svg`, and
  `results/tables/workflow_artifact_map.csv`
- Fig. 7 trust-card examples: `results/figures/trust_card_examples.pdf`,
  `results/figures/trust_card_examples.svg`, and
  `results/tables/trust_card_examples.csv`
- Unified generation summary:
  `results/tables/submission_figure_summary.json`

The BIB-facing C3/R2 figure polish pass has also been completed:

- Fig. 4 exposure-adjusted AUROC deltas:
  `results/figures/fig4_exposure_delta_ci_bib.pdf` and canonical
  `results/figures/exposure_delta_ci.pdf`
- Fig. 5 BACE/Tox21 sequence-family sensitivity:
  `results/figures/fig5_sequence_family_bib.pdf` and canonical
  `results/figures/bace_tox21_sequence_model_family.pdf`
- Fig. S7 train-label-shuffle negative control:
  `results/figures/figS7_label_shuffle_null_control_bib.pdf` and canonical
  `results/figures/label_shuffle_null_control.pdf`
- Source-data tables:
  `results/tables/fig4_exposure_delta_ci_source.csv`,
  `results/tables/fig5_sequence_family_delta_source.csv`,
  `results/tables/fig5_sequence_family_clean_size_source.csv`, and
  `results/tables/fig8_label_shuffle_source.csv`
- Final figure generation summary:
  `results/tables/bib_final_figure_summary.json`

Interpretation: these artifacts convert MolTrustBench from a collection of
tables into a reviewer-inspectable reporting framework. They support C5 without
claiming model-specific training exposure. Fig. S7 is a negative-control
diagnostic, not causal evidence that public exposure
explains every observed delta.

## BIB Supplement And Data Availability Package

The BIB supplement package is generated under `paper/supplement/`.

- Supplement package:
  `paper/supplement/MolTrustBench_BIB_supplement_package_20260529_174251.zip`
- Supplement table map: `paper/supplement/supplementary_tables.md`
- Supplement manifest: `paper/supplement/supplement_manifest.csv`
- Data availability draft: `paper/supplement/data_availability_statement.md`
- Mapped supplement tables: 29
- New audit-ready supplement tables: S24 slice-validity master, S25
  standardization audit, S26 assay-flag dictionary, S27 provenance examples,
  S28 trust-card schema/JSON examples, and S29 figure source-data map.

The current data-freeze archive is
`results/archive/moltrustbench_data_freeze_20260529_161700.tgz` with SHA256
`beb779864151105b3c8cd13507df8f0779bfc53e2d6a4f6a792d82f91e34b2df`.
This archive includes the ChemBERTa-100M wrapper outputs,
DILI/hepatotoxicity endpoint artifacts, repaired assay-provenance figure, and
paper/supplement control files. The supplement package points to this freeze
and should be deposited or submitted separately from the raw evidence archive.

## Next Experiments

- Do not launch another GPU-heavy run for the current BIB draft unless a named
  reviewer objection requires it.
- Replace data DOI, GitHub commit SHA, author metadata, funding, and disclosure
  placeholders before submission.
- Keep ChemBERTa-100M supplement-only as R5/R7 wrapper applicability evidence.
- Keep DILI/hepatotoxicity as a C4/R10 provenance table plus short Results
  paragraph; do not promote the small exposure-removed/temporal slices to main performance
  claims.
- Add SIDER or a third FM wrapper only if coauthor/reviewer feedback asks for
  more breadth.

## Target Journal Positioning

Primary target: Briefings in Bioinformatics as a reproducible bioinformatics
resource and reporting standard. Patterns remains appropriate for the
benchmark-validity data-science framing. Archives of Toxicology becomes
stronger as assay-provenance and endpoint-native ADMET/Tox analyses expand.
