# Briefings in Bioinformatics Reviewer Preflight

Date: 2026-05-28

Purpose: convert the current MolTrustBench evidence package into a submission-clean plan for **Briefings in Bioinformatics**. This is a preflight, not a claim expansion. Terminology remains conservative: public exposure, potential exposure, observable exposure lower bound, temporal validity, benchmark trustworthiness, exposure-adjusted evaluation, assay provenance, and benchmark trust card.

## Novelty Boundary

MolTrustBench should be positioned as a benchmark trustworthiness audit framework, not an ADMET leaderboard and not a molecular OOD benchmark. Existing ADMET/OOD work asks whether models handle scarcity, imbalance, activity cliffs, bRo5 chemistry, and distribution shift. MolTrustBench asks a different question: whether benchmark molecules, scaffolds, close chemical neighbors, and assay-derived labels were publicly observable before a release or evaluation cutoff, and whether reported performance changes under exposure-aware slices. The novelty is the combination of release-time public-exposure indexing, exposure-adjusted evaluation, assay-provenance diagnosis, and benchmark trust cards.

## Claim Sufficiency

| Claim | Current status | Evidence sufficiency for BIB | Main limitation to state |
| --- | --- | --- | --- |
| C1 measurable public exposure | supported | Four real MoleculeNet tasks plus ChEMBL24/27/30/33/36 release index. | Broader task panel still desirable before final submission. |
| C2 exact is not enough | supported | Exact/scaffold/NN annotations and NN-threshold sensitivity. | Fast coverage expansion uses a same-scaffold NN lower-bound search. |
| C3 exposure-adjusted scores differ | supported | BBBP/ClinTox classical and model-family results; BACE/Tox21 classical, MLP, and sequence-family coverage; ESOL regression sequence coverage; endpoint-native ChEMBL hERG/CYP temporal evaluation; endpoint SMILES-Transformer add-on; CYP1A2/CYP2C19 sequence baselines; CI tables; train-label-shuffle null controls; MolFormer and ChemBERTa-100M frozen embeddings provide checkpoint-light FM wrapper case studies. | Temporal-future subsets remain small or invalid for some tasks; Lipophilicity exposure-aware regression slices, CYP2C9 one-class exposure-removed slices, DILI one-class exposure-removed/temporal slices, BACE label-shuffle one-class standard split, four null-sensitive observed-vs-null comparisons, and CYP1A2 missing paired temporal-delta rows are expected limitations under the current cutoff. FM evidence remains wrapper-level, not model-specific pretraining evidence. |
| C4 assay provenance matters | supported | ChEMBL36 SQLite extraction, endpoint-native hERG pilot, CYP1A2/CYP2C19 endpoint-native assay summaries, and a DILI/hepatotoxicity text-evidence endpoint with assay provenance. | DILI exact/NN/temporal/density exposure-removed subsets are too small for performance claims and should be reported as expected limitations, not hidden. |
| C5 reusable trust cards/reporting | supported | Trust cards, workflow schematic, auto report, sanity checks, model registry, coverage diagnostics, plotted trust-card examples, supplement Tables S24-S29, and machine-readable trust-card JSON schema/examples. | DOI/accession and GitHub release placeholders must be replaced before submission. |

## Reviewer Attack Readiness

| Risk | Readiness | Current defense | What not to overclaim |
| --- | --- | --- | --- |
| R1 no direct model-specific exposure proof | ready | Text consistently says observable lower bound and public exposure. | Do not write model-specific exposure or molecule-recall claims. |
| R2 exposure is density | mostly ready | Density-matched controls, NN thresholds, CI tables, train-label-shuffle null controls, and CYP rescue temporal-delta pairs. | Do not claim density is fully ruled out or that null controls prove causality. |
| R3 duplicates ADMET/OOD benchmarks | ready | Novelty boundary is temporal validity and benchmark auditability. | Do not frame as a better ADMET leaderboard. |
| R4 release date is not training date | ready | ChEMBL release is treated as observability date. | Do not equate release cutoff with model pretraining cutoff. |
| R5 models may not use ChEMBL | mostly ready | Pretraining registry separates unknown corpora from observable public data, and MolFormer/ChemBERTa-100M are framed as wrapper applicability evidence rather than model-specific ChEMBL-use evidence. | Do not imply ChEMBL use by ChemBERTa/MolFormer without metadata. |
| R6 just data cleaning | ready | Exposure-adjusted scores, CI deltas, endpoint-native temporal evaluation, CYP1A2/CYP2C19 sequence baselines, train-label-shuffle null controls, trust cards, assay provenance. | Do not bury evaluation outputs in supplement only. |
| R7 FM wrappers incomplete | ready for current scope | MolFormer safetensors runs as a 1140-row frozen-embedding case study, and ChemBERTa-100M safetensors adds 150 rows with zero failures. Prior blocked artifacts are archived rather than hidden. | Do not generalize from two wrappers to all molecular foundation models or imply model-specific ChEMBL pretraining exposure. |
| R8 exposure-removed subsets too small | ready for current scope | Sanity checks, Table S24 slice-validity master, test-size reporting, Lipophilicity expected-limitation accounting, CYP2C9 one-class slice accounting, and BACE label-shuffle one-class standard-split accounting. | Do not hide ClinTox temporal `n=8`, Tox21 NN slice-size limits, Lipophilicity empty exposure-aware slices, CYP2C9 exposure-removed exclusions, or BACE label-shuffle exclusions. |
| R9 standardization dependence | ready | RDKit reports, official ChEMBL standard InChIKeys, rejected-molecule logs, and Table S25 standardization audit. | Do not claim molecule standardization is uniquely correct. |
| R10 assay labels noisy | ready | SQLite provenance, discordant derived-label calls, units, threshold sensitivity, endpoint-native hERG, CYP1A2/CYP2C19, DILI/hepatotoxicity text-evidence summaries, Table S26 flag dictionary, and Table S27 examples. | Do not treat ChEMBL-overlap assay records as the original MoleculeNet label source; DILI exposure-removed/temporal slices are expected limitations. |

## Delta-CI Interpretation

Artifacts:

- `results/tables/exposure_delta_ci.csv`
- `results/tables/sequence_delta_ci.csv`
- `results/tables/regression_delta_ci.csv`
- `results/figures/exposure_delta_ci.pdf`
- `results/figures/sequence_delta_ci.pdf`
- `results/figures/regression_delta_ci.pdf`

The CI analysis should be written as a stability check for exposure-adjusted score deltas. It supports the claim that some deltas are stable across seeds and hidden dimensions, especially BACE/Tox21 SMILES-CNN and many Tox21 SMILES-Transformer comparisons. It also shows important exceptions: Tox21 SMILES-GRU exact-removed and density-matched deltas have bootstrap intervals crossing zero. This is scientifically useful because it prevents the manuscript from claiming that exposure-removed subsets are always harder or that public exposure has one universal direction.

The regression extension adds a useful non-classification check. ESOL produces 960 paired standard-vs-exposure-aware regression deltas and 24 summary rows across SMILES-CNN, SMILES-GRU, and SMILES-Transformer. Twenty-two of the 24 RMSE intervals exclude zero, but the direction is not universal: ESOL SMILES-CNN temporal-future and ESOL SMILES-GRU scaffold-removed have lower RMSE than their matched standard runs, while many exact/NN/density comparisons have higher RMSE. Lipophilicity should be discussed only as an expected-limitation result because exposure-aware slices were too small or absent.

The endpoint-native ChEMBL temporal wave adds a more direct temporal-validity check for C3. It contributes 840 valid SMILES-CNN/GRU metrics across hERG, CYP3A4, CYP2D6, and CYP2C9, with standard, exposure-removed, density-matched, and temporal-future slices. The 180 failure rows are retained as expected limitations from CYP2C9 one-class exposure-removed subsets, and the integrated critical-failure table has zero rows. This should be framed as evidence that MolTrustBench can expose endpoint-specific temporal and exposure-removed slice limits, not as proof that every endpoint yields evaluable exposure-aware subsets.

The overnight endpoint SMILES-Transformer add-on contributes 420 additional
valid metrics over the same endpoint-native hERG/CYP task family. Its 60
failure rows are expected one-class exposure-removed slice limitations, and the integrated
critical-failure table has zero rows. This strengthens model-family sensitivity
without converting the result into foundation-model pretraining evidence.

The train-label-shuffle null-control run contributes 360 valid metrics across
Tox21 and the ChEMBL endpoint tasks, with 180 expected one-class limitations
dominated by the current BACE standard split. The null-control comparison table
contains 22 observed-vs-null comparisons: 18 show larger absolute observed
deltas than shuffled-label deltas, while four remain null-sensitive. The
CYP1A2/CYP2C19 label-shuffle integration adds 360 train-label-shuffle metrics,
1080 expected exposure-removed slice limitations, zero critical failures, and 120 CYP2C19
observed-vs-shuffled temporal-delta pairs. This is
a reviewer-defense result against noise-only interpretations, not causal proof
of public exposure effects.

The frozen FM embedding case studies now contribute two safetensors wrapper
checks. MolFormer contributes 1140 consolidated rows with zero failure rows:
240 CYP1A2/CYP2C19 rows plus a 900-row 20-seed expansion across MoleculeNet
and endpoint-native hERG/CYP tasks. ChemBERTa-100M contributes 150 additional
rows with zero failure rows across BACE, Tox21, BBBP, ClinTox, CYP1A2, and
CYP2C19. These runs should be framed as checkpoint-light wrapper applicability
controls for R7, not as evidence that either checkpoint used ChEMBL during
pretraining.

## Sentences That Are Safe

- "Public exposure is an observable lower bound on benchmark temporal-validity risk."
- "Exposure-adjusted evaluation changes performance interpretation in a task- and model-family-dependent manner."
- "ChEMBL release dates provide public observability dates, not model-specific pretraining dates."
- "Assay provenance reveals label conflict and threshold sensitivity risks that are underreported in benchmark summaries."
- "Trust cards make benchmark limitations inspectable before leaderboard scores are interpreted as prospective generalization."

## Sentences That Are Too Strong

- "These benchmarks prove model-specific exposure."
- "Foundation models recalled these molecules from pretraining."
- "Removing exposed molecules always reduces performance."
- "Density controls prove exposure is causal."
- "ChEMBL release date is the model training cutoff."
- "MoleculeNet labels are wrong."

## Submission Figure Map

| Slot | Figure | Evidence role | Artifact status | Placement |
| --- | --- | --- | --- | --- |
| Fig. 1 | MolTrustBench workflow | Framework and paper thesis | `results/figures/workflow_schematic.pdf`, `results/tables/workflow_artifact_map.csv` | Main |
| Fig. 2 | ChEMBL release timeline / release histogram | C1 observability timeline | `results/figures/release_histogram.pdf` | Main |
| Fig. 3 | Four-task exposure heatmap | C1/C2 exposure landscape | `results/figures/exposure_heatmap_coverage.pdf` | Main |
| Fig. 4 | Exposure-adjusted performance delta with CI | C3 score sensitivity | `results/figures/exposure_delta_ci.pdf` plus existing performance-drop plot | Main |
| Fig. 5 | BACE/Tox21 sequence-family sensitivity | C3/C5 model-family sensitivity | `results/figures/bace_tox21_sequence_model_family.pdf`, `results/figures/sequence_delta_ci.pdf` | Main |
| Fig. 6 | Assay conflict map | C4 assay provenance | `results/figures/assay_conflict_map.pdf` | Main |
| Fig. 7 | Benchmark trust-card examples | C5 reporting standard | `results/figures/trust_card_examples.pdf`, `results/tables/trust_card_examples.csv` | Main |
| Fig. S7 | Train-label-shuffle null controls | R2/R6 negative-control check | `results/figures/label_shuffle_null_control.pdf`, `results/tables/label_shuffle_null_control_comparison.csv` | Supplement |
| Fig. S1 | Temporal decay | Temporal validity boundary | `results/figures/temporal_decay.pdf` | Supplement |
| Fig. S2 | NN-threshold sensitivity | C2/R2 robustness | `results/figures/nn_threshold_sensitivity.pdf` | Supplement or short main inset |
| Fig. S3 | Full model-family sensitivity | Extended C3/C5 | `results/figures/model_family_exposure_sensitivity.pdf` | Supplement |
| Fig. S4 | Sequence delta CI | BACE/Tox21 stability details | `results/figures/sequence_delta_ci.pdf` | Supplement if Fig. 5 uses summary bars |
| Fig. S5 | ESOL regression delta CI | Non-classification C3 robustness and R8 boundary | `results/figures/regression_delta_ci.pdf` | Supplement |
| Fig. S6 | Endpoint Transformer add-on | Endpoint-native sequence-family C3 robustness | `results/tables/chembl_endpoint_transformer_metrics.csv` | Supplement |
| Fig. S7 or Table Sz | Frozen MolFormer embeddings | R5/R7 checkpoint-light FM wrapper boundary | `results/tables/fm_embedding_slice_metrics.csv`, `results/tables/cyp_fm_completed_integration_summary.json` | Supplement |
| Table Sa | CYP1A2/CYP2C19 endpoint extension | C4/R10 endpoint-native assay provenance breadth | `results/tables/cyp_endpoint_extension_assay_provenance_summary.csv`, `results/tables/cyp_endpoint_extension_split_summary.csv` | Supplement |
| Table Sb | CYP1A2/CYP2C19 sequence and label-shuffle rescue | C3/R2/R6 endpoint-native negative-control boundary | `results/tables/cyp_extension_sequence_metrics.csv`, `results/tables/cyp_extension_label_shuffle_rescue_metrics.csv`, `results/tables/cyp_extension_label_shuffle_null_summary.csv` | Supplement |

## Next Long Experiment Decision

The regression-task expansion, endpoint-native temporal wave, endpoint
SMILES-Transformer add-on, train-label-shuffle null controls, MolFormer frozen
embeddings, CYP1A2/CYP2C19 endpoint extension, and final Fig. 1/Fig. 7
generation have now been integrated. The current paper-facing pass tightens
R5/R7/R10 wording and places MolFormer plus CYP1A2/CYP2C19 in the supplement
map.

The CYP1A2/CYP2C19 sequence-baseline extension, GPU1-4/6/7 label-shuffle
rescue, ChemBERTa-100M safetensors wrapper, and DILI/hepatotoxicity
provenance endpoint are now integrated. The next compute-heavy experiment
should be launched only if a specific reviewer gap remains after the
paper/caption audit, such as a broader ADMET/Tox endpoint panel or an external
reproducibility rerun. Do not launch more sequence baselines merely to increase
leaderboard volume.
