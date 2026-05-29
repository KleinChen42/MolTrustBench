# Main Figure Captions v1

Target journal: Briefings in Bioinformatics

Caption rule: each caption states the evidence role and the limitation boundary.
Terminology remains conservative: public exposure, observable exposure lower
bound, temporal validity, exposure-adjusted evaluation, assay provenance, and
benchmark trust card.

## Fig. 1. MolTrustBench Workflow

MolTrustBench workflow for auditing molecular benchmark trustworthiness under
public observability. Benchmark molecules are deterministically standardized,
linked to ChEMBL release-time compound and scaffold indexes, annotated for
exact/scaffold/nearest-neighbor public exposure, evaluated under
exposure-adjusted splits, and summarized in benchmark trust cards. ChEMBL
release dates are treated as public observability dates, not as evidence that a
specific model used ChEMBL during pretraining.

Artifact: `results/figures/workflow_schematic.pdf`

## Fig. 2. ChEMBL Release-Time Index

ChEMBL24/27/30/33/36 define a reproducible timeline for observable public
exposure. The release index records first-seen compound and scaffold
observability after deterministic molecule standardization, enabling benchmark
test molecules to be audited against a fixed release cutoff. These dates support
public-exposure lower bounds rather than model-specific pretraining cutoffs.

Artifact: `results/figures/release_histogram.pdf`

## Fig. 3. Multi-Level Public-Exposure Landscape

Exact, scaffold, and nearest-neighbor exposure rates vary across MoleculeNet
BBBP, ClinTox, BACE, and Tox21 at the CHEMBL30 cutoff. The heatmap shows that
exact molecule occurrence is only one exposure view: scaffold and NN exposure
can reveal additional observable exposure lower bounds, while some tasks such
as Tox21 are already highly exact-exposed. Denominators are the audited
benchmark molecule counts. The result motivates per-benchmark trust cards
instead of a single universal exposure label.

Artifact: `results/figures/exposure_heatmap_coverage.pdf`

## Fig. 4. Exposure-Adjusted Score Deltas

Exposure-adjusted evaluation changes performance interpretation across tasks,
splits, and model families. Deltas are computed as standard-score minus
comparison-score for matched standard and exposure-aware slices and include
bootstrap/seed-level uncertainty where available. The figure is evidence of
benchmark score sensitivity under public-exposure auditing; it does not prove
model-specific training exposure or label recall.

Artifact: `results/figures/exposure_delta_ci.pdf`

## Fig. 5. Sequence-Family Exposure Sensitivity

BACE/Tox21 sequence-family baselines show that exposure-adjusted score changes
are architecture- and task-dependent. The integrated sweep covers SMILES-CNN,
SMILES-GRU, and SMILES-Transformer baselines across 1,200 expected unique runs
after `run_id` deduplication. These models are sequence baselines for
exposure-adjusted evaluation, not foundation-model pretraining evidence.

Artifact: `results/figures/bace_tox21_sequence_model_family.pdf`

## Fig. 6. Assay-Provenance Heterogeneity Map

ChEMBL36 SQLite assay provenance reveals duplicate activity records, unit
heterogeneity, threshold sensitivity, and derived-label discordance for
benchmark molecules with public assay records. BBBP and ClinTox rows represent
public ChEMBL assay heterogeneity among overlapping molecules, while hERG,
CYP1A2, CYP2C19, and DILI/hepatotoxicity are endpoint-native ChEMBL-derived
provenance cases. Denominators are molecules with matched public activity
records, and flag definitions are given in Table S26. The figure supports
label-source reliability auditing, not a claim that original benchmark labels
are simply wrong.

Artifact: `results/figures/assay_conflict_map.pdf`

## Fig. 7. Benchmark Trust-Card Examples

Benchmark trust cards summarize public-exposure rates, exposure-removed subset
sizes, exposure-adjusted score evidence, assay-provenance availability, and
audit caveats for individual benchmark tasks. The card format turns
MolTrustBench outputs into a reporting standard so benchmark users can inspect
temporal-validity and provenance limitations before interpreting leaderboard
scores as prospective generalization. Machine-readable schema and JSON
examples are provided in Table S28 and the supplement trust-card directory.

Artifact: `results/figures/trust_card_examples.pdf`

## Supplementary Captions

Fig. S1. Temporal-future evaluation boundaries. Observable temporal-future
splits provide an initial temporal-validity check but remain small or invalid
for some tasks; sample sizes should be printed or reported alongside scores.

Fig. S2. Nearest-neighbor threshold sensitivity. NN exposure rates and
exposure-adjusted scores are shown across Tanimoto thresholds to test whether
conclusions depend on a single neighbor cutoff.

Fig. S3. BBBP/ClinTox model-family sensitivity. Classical, fingerprint-neural,
and sequence-neural baselines show that exposure-adjusted evaluation is not
confined to one baseline family.

Fig. S4. BACE/Tox21 sequence delta confidence intervals. Paired delta intervals
separate stable exposure-adjusted changes from uncertain deltas and prevent
overclaiming that exposure-removed subsets are universally harder.

Fig. S5. ESOL regression delta confidence intervals. ESOL demonstrates that
exposure-adjusted evaluation can extend beyond classification, while
Lipophilicity exposure-aware slices are recorded as expected limitations
under the current cutoff.

Fig. S6 or Table Sx. Endpoint-native ChEMBL temporal evaluation. hERG, CYP3A4,
CYP2D6, and CYP2C9 ChEMBL-derived temporal tasks contribute 840 valid
SMILES-CNN/GRU metrics plus 420 valid SMILES-Transformer add-on metrics. The
240 expected-limitation rows arise from one-class exposure-removed slices under strict
exposure filtering, and the integrated critical-failure tables have zero rows.
CYP1A2 and CYP2C19 extend the endpoint-native evidence with 360 observed-label
sequence metrics, 1080 expected exposure-removed slice limitations, and zero critical
failures.

Table Sz. Frozen foundation-model embedding case studies. The
checkpoint-light MolFormer safetensors workflow contributes 1140 consolidated
frozen-embedding metrics with zero failure rows, and ChemBERTa-100M safetensors
adds 150 frozen-embedding rows with zero failure rows. This is
wrapper applicability evidence for foundation-model-style evaluation, not proof
of model-specific ChEMBL pretraining exposure or a foundation-model
leaderboard. Earlier blocked FM attempts are reported as artifact-format/runtime
limitations rather than scientific negative results.

Fig. S7. Train-label-shuffle null-control comparison. Observed-label
exposure-adjusted deltas are compared with deltas after permuting training
labels. The analysis contributes 360 valid null-control metrics and shows that
18 of 22 observed-vs-null comparisons have larger absolute observed deltas than
shuffled-label deltas, while four remain null-sensitive. This is a
negative control for exposure-adjusted evaluation, not proof of
model-specific public exposure or label recall.

Table Sb. CYP1A2/CYP2C19 sequence and train-label-shuffle integration summary. The
CYP endpoint extension contributes 360 observed-label sequence metrics, 360
train-label-shuffle metrics, 1080 expected exposure-removed slice limitations in
each run, zero critical failures, and 120 CYP2C19 observed-vs-shuffled
temporal-delta pairs. CYP1A2 lacks paired temporal-delta rows in this snapshot
and is reported as a coverage boundary.

Table Sc. DILI/hepatotoxicity endpoint provenance and exposure-removed slice boundary. The
ChEMBL36 text-evidence endpoint contributes 528 labeled activity records, 513
benchmark molecules, 514 molecule-level assay-provenance summaries, one binary
text-label conflict, and 60 standard/scaffold-removed sequence metrics with
zero failure rows. Exact-removed, NN@0.8-removed, temporal-future, and
density-matched slices shrink to one-class two-molecule tests and should
be reported as expected exposure-removed slice limitations.

Table S24. Slice-validity master table. Reports test n, positive/negative
counts when available, one-class flags, metric-validity flags, CI availability,
and reason codes for every paper-facing slice and expected limitation.

Table S25. Standardization audit summary. Records raw-to-standardized row
accounting, rejected-molecule policy, InChIKey/scaffold availability, and
standardization notes for R9.

Table S26. Assay-provenance flag dictionary. Defines duplicate, discordant
derived-label, unit mismatch, threshold sensitivity, provenance-level
discordance, and derived-label discordance score fields with denominators and limits.

Table S27. Assay-provenance examples. Gives compact record-derived examples
showing how provenance flags are derived from ChEMBL activity summaries.

Table S28. Trust-card schema. Defines machine-readable benchmark trust-card
fields, types, required/optional status, and example JSON cards.

Table S29. Figure source-data map. Maps each main figure to the compact source
data table used for plotting and review.
