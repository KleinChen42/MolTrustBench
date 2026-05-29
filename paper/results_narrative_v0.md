# Results Narrative v0

Target style: Briefings in Bioinformatics resource/method article.

Core wording rule: this section reports public exposure, potential exposure,
observable exposure lower bounds, temporal validity, exposure-adjusted
evaluation, assay provenance, and benchmark trustworthiness. It does not claim
direct model-specific training exposure, model misconduct, or label recall.

## Compact Results Outline

1. MolTrustBench builds a release-time index for observable public exposure.
2. Public exposure is measurable across benchmark tasks, but its pattern is
   task-dependent.
3. Exact matching underestimates benchmark exposure risk in some tasks; scaffold
   and nearest-neighbor exposure add distinct temporal-validity information.
4. Exposure-adjusted evaluation changes performance interpretation, although the
   direction of the change depends on task, split, and model family.
5. Assay provenance shows that benchmark trustworthiness also depends on label
   source stability, not only molecule occurrence.
6. Trust cards turn these audits into a reusable reporting layer for benchmark
   users and model developers.

## Figure And Table Callouts

| Result block | Main message | Primary artifacts | Suggested display |
| --- | --- | --- | --- |
| Framework | MolTrustBench connects public observability, exposure annotation, exposure-adjusted evaluation, assay provenance, and trust cards. | `results/figures/workflow_schematic.pdf`, `results/tables/workflow_artifact_map.csv` | Fig. 1 workflow schematic |
| Release-time index | ChEMBL releases provide a reproducible public-observability timeline. | `results/tables/chembl_release_counts.csv`, `results/release_index/*_release_index.parquet` | Fig. 2 release histogram; Table 2 release summary |
| Exposure landscape | Public exposure is measurable across four real MoleculeNet tasks. | `results/tables/benchmark_coverage_exposure_summary.csv` | Fig. 3 coverage heatmap; Table 4 exposure summary |
| Exposure levels | Exact, scaffold, and NN exposure capture different audit risks. | `results/benchmark_annotations/*_exposure.parquet`, trust cards | Fig. 3 plus trust-card inset |
| Exposure-adjusted evaluation | Standard and exposure-adjusted scores can differ substantially. | `results/tables/slice_metrics.csv`, `results/tables/model_family_exposure_sensitivity.csv`, `results/tables/bace_tox21_sequence_slice_metrics.csv` | Fig. 4 performance delta; Fig. 5 model-family sensitivity |
| Regression robustness | Non-classification exposure-adjusted evaluation is feasible for ESOL, while Lipophilicity exposes exposure-aware slice limits. | `results/tables/regression_sequence_slice_metrics.csv`, `results/tables/regression_delta_ci.csv`, `results/tables/regression_sequence_expected_limitations.csv` | Fig. S5 regression delta CI; Supplementary limitation table |
| Temporal validity controls | Observable temporal-future splits are feasible but currently small. | `results/tables/temporal_metrics.csv`, `results/tables/temporal_split_summary.csv` | Fig. 5 temporal decay; Supplementary table |
| Endpoint-native temporal evaluation | ChEMBL-derived hERG/CYP endpoints provide a more direct temporal-validity check and expose endpoint-specific exposure-removed slice limits. | `results/tables/chembl_endpoint_temporal_metrics.csv`, `results/tables/chembl_endpoint_transformer_metrics.csv`, `results/tables/chembl_endpoint_temporal_expected_limitations.csv`, `results/tables/chembl_endpoint_transformer_expected_limitations.csv` | Supplementary endpoint-temporal table; optional Fig. S6 |
| Frozen FM wrapper case study | MolFormer and ChemBERTa-100M frozen embeddings test whether the framework can run staged safetensors molecular FM checkpoints without implying ChEMBL pretraining exposure. | `results/tables/fm_embedding_slice_metrics.csv`, `results/tables/fm_embedding_summary.csv`, `results/tables/cyp_extension_molformer_fm_metrics.csv`, `results/tables/molformer_fm_20seed_metrics.csv`, `results/tables/chemberta_100m_fm_slice_metrics.csv` | Supplementary Table Sz or short Results limitation paragraph |
| Train-label-shuffle negative control | Exposure-adjusted deltas are compared against shuffled-label baselines to test whether observed deltas are plausibly larger than a null training-label control. | `results/tables/label_shuffle_null_control_comparison.csv`, `results/tables/cyp_extension_label_shuffle_rescue_metrics.csv`, `results/tables/cyp_extension_label_shuffle_null_pairs.csv`, `results/figures/label_shuffle_null_control.pdf` | Supplement-first null-control figure; Results limitation paragraph; Supplementary Table Sb |
| Assay provenance | Public assay records reveal duplicate, derived-label discordance, and threshold-sensitive labels, now including endpoint-native hERG plus CYP1A2/CYP2C19 extensions. | `results/tables/assay_provenance_task_summary.csv`, `results/tables/cyp_endpoint_extension_assay_provenance_summary.csv` | Fig. 6 assay-provenance heterogeneity map; Supplementary CYP endpoint table |
| Reporting standard | Trust cards and sanity reports make benchmark limitations inspectable. | `results/figures/trust_card_examples.pdf`, `results/tables/trust_card_examples.csv`, `results/report_cards/*_card.json`, `paper/auto_report.md`, `results/tables/sanity_report.csv` | Fig. 7 trust-card examples; Table 6 checklist |

## Draft Results Text

### MolTrustBench Establishes A Release-Time Index For Public-Exposure Auditing

MolTrustBench first constructs a release-time index that converts public
chemical database history into an auditable benchmark timeline. We indexed five
ChEMBL releases spanning CHEMBL24, CHEMBL27, CHEMBL30, CHEMBL33, and CHEMBL36,
with release dates from May 2018 to July 2025 and standardized molecule counts
ranging from 1.82 million to 2.85 million records. For each release, the
pipeline records standard InChIKey, standardized SMILES, release metadata, and
Bemis-Murcko scaffold information, then collapses records into earliest
observable release indexes at the compound and scaffold levels. This design
intentionally treats ChEMBL release date as an observability date, not as proof
that any specific model used ChEMBL during pretraining.

Figure callout: Fig. 1 should show the full MolTrustBench workflow and artifact
chain; Fig. 2 should show the release-index growth and first-seen
distribution. Table 2 should list the five ChEMBL releases, release dates, DOI
strings, input rows, standardized rows, unique standard InChIKeys, and unique
scaffolds.

Evidence status: supported for ChEMBL-backed public observability. Limited for
model-specific pretraining exposure because checkpoint-level corpus cutoffs are
not yet known for most foundation models.

### Public Exposure Is Measurable Across Benchmark Tasks

The real-data audit finds measurable public exposure across all four completed
MoleculeNet tasks, supporting the claim that benchmark trustworthiness should be
audited before interpreting held-out molecules as future chemistry. At the
CHEMBL30 cutoff, exact exposure was 0.838 for BBBP, 0.474 for ClinTox, 0.297 for
BACE, and 0.921 for Tox21. The four-task audit covers 12,290 benchmark
molecules, with clean exact counts ranging from 331 in BBBP to 1,063 in BACE.
These values are not uniform across tasks: BACE contains a larger exact-unobserved
subset, whereas Tox21 is already highly exact-exposed under the same cutoff.
This heterogeneity is the point of the audit: a benchmark trust card should
report the public-exposure profile of each task rather than assuming that all
benchmark test sets carry the same temporal meaning.

Figure callout: Fig. 3 should include the coverage heatmap from
`results/figures/exposure_heatmap_coverage.pdf`. Table 4 should report exact,
scaffold, and nearest-neighbor exposure rates for BBBP, ClinTox, BACE, and
Tox21, plus clean exact counts.

Evidence status: supported for audit-only C1 across four MoleculeNet tasks.
Limited for broader benchmark generality because ESOL and Lipophilicity now
enter only through regression performance integration, while SIDER remains
deferred by the runtime guard and should be completed before submission.

### Scaffold And Nearest-Neighbor Exposure Extend Beyond Exact Matching

Exact molecule matching is only the most conservative exposure test, and the
scaffold and nearest-neighbor views reveal additional temporal-validity risks.
For BBBP, exact exposure at CHEMBL30 was 0.838, while scaffold exposure was
0.878 and nearest-neighbor exposure at Tanimoto >= 0.8 was 0.889. ClinTox showed
a larger gap between exact and structural exposure: exact exposure was 0.474,
but scaffold exposure reached 0.737 and NN@0.8 reached 0.599. BACE showed the
same ordering at lower absolute rates, with exact exposure of 0.297,
scaffold exposure of 0.427, and NN@0.8 exposure of 0.394. Tox21 is an important
counterexample rather than an inconvenience: exact exposure was already very
high at 0.921, while scaffold exposure was 0.753 and NN@0.8 was 0.959. The
this is evidence that public-exposure auditing is multi-level and
task-specific, not a single monotonic score.

Figure callout: Fig. 3 should annotate at least one high exact-exposure task
(Tox21), one scaffold/NN-amplified task (ClinTox), and one lower exposure task
(BACE). Fig. 7 can show example trust cards for high-risk and medium-risk
benchmark.

Evidence status: supported for C2 as an observable lower-bound audit. Limited
for chemical-neighbor completeness because the fast coverage expansion used a
same-scaffold lower-bound NN search; the original BBBP/ClinTox Milestone 1
annotations remain the stronger two-task NN evidence.

### Exposure-Adjusted Evaluation Changes Benchmark Interpretation

Exposure-adjusted evaluation shows that standard split scores and exposure-removed subset
scores can diverge enough to change how benchmark performance is interpreted.
On BBBP, Morgan-logistic regression achieved AUROC 0.879 on the standard split
and 0.946 on the exact-removed split; Morgan-XGB similarly changed from 0.885
to 0.976. ClinTox moved in the opposite direction: Morgan-logistic regression
changed from AUROC 0.836 on the standard split to 0.565 on the exact-removed
split, and Morgan-XGB changed from 0.784 to 0.370. These results should not be
written as a universal performance drop. The stronger and more defensible
claim is that exposure-aware subsets can produce different estimates of model
performance, and that the direction depends on task composition, label
structure, model class, and exposure-removed subset size.

Figure callout: Fig. 4 should show standard versus exact-removed performance
deltas for BBBP and ClinTox, with text explicitly noting that the audit
measures score sensitivity rather than proving a model-specific training-data
mechanism.
Table 5 should report standard score, clean score, exposed score when
available, and exposure delta.

Evidence status: supported for C3 across BBBP, ClinTox, BACE, and Tox21 exposure-adjusted evaluation. ESOL now adds regression robustness. Limited for broad benchmark claims because Lipophilicity exposure-aware regression slices are not evaluable under the current cutoff, SIDER and broader TDC ADMET tasks remain deferred, and temporal-future subsets for some tasks are too small for stable classification metrics.

### Density-Matched And Temporal-Future Controls Define The Current Evidence Boundary

The first controls address two reviewer risks: public exposure may be a proxy
for chemical-space density, and release dates are not model-specific training
dates. Density-matched exposure-removed controls now cover BBBP, ClinTox, BACE, and
Tox21, and they did not eliminate score differences across the evaluated
tasks. For BACE, Morgan-XGB AUROC changed from 0.767 on the standard split to
0.720 on exact-removed and 0.550 on the density-matched split. For
Tox21, Morgan-XGB changed from 0.707 on standard to 0.849 on exact-removed,
0.584 on scaffold-removed, and 0.849 on density-matched, while the
exposure-removed subsets were much smaller than the standard test set. Temporal-future
splits remain a narrower control: BBBP had 34 temporal-future test molecules,
ClinTox had only 8, and BACE/Tox21 temporal-future subsets were too small or
single-class for stable classification metrics. These controls support the
framework logic, while temporal-generalization evidence remains a current
boundary rather than a final deployment claim.

Figure callout: Fig. 5 should present temporal-future scores with test-set size
printed directly on the plot. Density-matched controls are better placed in a
main or supplementary table because the key message is sample-size-limited
interpretability.

Evidence status: supported as initial C3 controls. Limited because temporal
future sets are currently small, especially ClinTox.

### Endpoint-Native ChEMBL Temporal Tasks Strengthen The Temporal-Validity Check

The endpoint-native ChEMBL temporal wave adds a cleaner test of temporal
validity because the tasks are derived directly from ChEMBL bioactivity records
rather than mapped retrospectively from MoleculeNet labels. The integrated run
contains 840 valid SMILES-CNN and SMILES-GRU metric rows, plus a 420-row
SMILES-Transformer add-on, across hERG, CYP3A4, CYP2D6, and CYP2C9
endpoint-native tasks. The evaluated slices include standard, exact-removed,
scaffold-removed, NN@0.8-removed, density-matched, and temporal-future
subsets where valid. Coverage is complete for observed task/model/split groups:
each retained group has 10 observed seeds and zero missing seeds. The endpoint
wave records 180 expected-limitation rows, the Transformer add-on records 60
expected-limitation rows, and both integrations have zero critical failures.
These expected limitations come from one-class exposure-removed subsets after strict
exposure filtering, especially CYP2C9, which is precisely the kind of boundary a
benchmark trustworthiness audit should reveal rather than hide.

The task summaries show substantial endpoint-level temporal drops, and they are
interpreted as endpoint-specific temporal-validity evidence rather than a
universal model claim. For example, mean standard AUROC is around 0.89 for hERG
sequence models, while the mean temporal drop is 0.19 for SMILES-CNN and 0.28
for SMILES-GRU. CYP3A4 and CYP2D6 also show positive temporal drops across
sequence models, whereas CYP2C9 retains only standard, scaffold-removed, and
temporal-future groups because exact/NN/density exposure-removed slices become
class-degenerate. This strengthens C3 and R8 together: exposure-adjusted
evaluation can reveal performance changes, and the same framework records when
exposure-removed slice construction is not statistically usable.

Figure callout: keep endpoint-native temporal results in a supplementary table
or optional Fig. S6 unless the main Results needs a compact temporal-validity
panel. The main text should cite the 1,260 valid endpoint-native sequence
metrics, 240 expected limitations, and zero critical failures as an auditability
result.

Evidence status: supported for endpoint-native C3 temporal validity within
hERG/CYP tasks, now including CNN, GRU, and Transformer-style sequence
baselines. Limited because foundation-model checkpoint-level temporal cutoffs
remain unavailable and CYP2C9 exposure-removed slice degeneracy prevents all
exposure-aware slices from being evaluated.

### Train-Label-Shuffle Controls Provide A Negative-Control Check, Not A New Main Claim

Train-label-shuffle controls test whether exposure-adjusted deltas remain
larger than a null training-label baseline. This negative-control analysis asks
whether the observed-label exposure-adjusted deltas are plausibly larger
than deltas obtained after permuting training labels, rather than trying to
prove a causal exposure mechanism. The first overnight control run produced 360
valid null-control metric rows across Tox21 and the ChEMBL endpoint-native
tasks, with SMILES-CNN, SMILES-GRU, and SMILES-Transformer baselines where
applicable. It also produced 180 expected one-class limitation rows and zero
critical failures. BACE is retained only as an expected one-class standard-split
limitation under the submitted annotation configuration and should not be interpreted as
label-shuffle evidence.

The null-control comparison table summarizes 22 observed-vs-shuffle delta
comparisons. Eighteen comparisons have larger absolute observed deltas than
shuffled-label deltas, with a mean absolute observed delta of 0.163 versus a
mean absolute shuffled-label delta of 0.038. Four comparisons remain
null-sensitive, meaning the shuffled-label delta was not smaller than the
observed-label delta. This mixed result is useful for a BIB reviewer: it
supports the claim that many exposure-adjusted deltas are not merely a
noise-level artifact, while preventing the manuscript from overstating a
universal exposure effect.

A de-duplicated CYP label-shuffle integration adds endpoint-native negative
control evidence for CYP1A2/CYP2C19. The integrated run contributes 360
train-label-shuffle metrics, 1080 expected exposure-removed slice limitations,
and zero critical failures across CYP1A2/CYP2C19 sequence baselines. The paired
observed-vs-shuffled temporal-delta table contains 120 CYP2C19 rows across
SMILES-CNN, SMILES-GRU, and SMILES-Transformer families. CYP1A2 did not yield
paired temporal-delta rows in this snapshot and should be reported as a
coverage limitation rather than hidden.

Figure callout: `results/figures/label_shuffle_null_control.pdf` is retained
as a supplement-first null-control figure. Its caption states that
train-label-shuffle is a null-control boundary check for C3, not evidence of
model-specific public exposure or label recall.

Evidence status: supports C3 reviewer defense and R2/R6 robustness within the
observed tasks. Limited because the control is not causal, BACE is currently
class-degenerate under the local annotation, four observed-vs-null comparisons
remain null-sensitive in the first null-control table, and the CYP rescue
temporal-pair analysis currently forms pairs for CYP2C19 but not CYP1A2.

### Model-Family Sensitivity Shows That Exposure Effects Are Not Confined To One Baseline

The model-family sweep extends exposure-adjusted evaluation beyond classical
fingerprint models while keeping the interpretation conservative. Across BBBP
and ClinTox, the current artifacts include Morgan logistic regression,
Morgan-XGB, Morgan MLP, SMILES-CNN, SMILES-GRU, and SMILES-Transformer results
under standard, exact-removed, scaffold-removed, NN-removed, density-matched,
and temporal-future slices. On BBBP, SMILES-CNN AUROC changed from 0.914 on the
standard split to 0.950 on exact-removed, 0.863 on scaffold-removed, and 0.947
on NN@0.8-removed. On ClinTox, SMILES-CNN AUROC changed from 0.905 on standard
to 0.921 on exact-removed, 0.884 on scaffold-removed, and 0.930 on
NN@0.8-removed. These two-task results establish the first model-family
sensitivity layer, but the stronger manuscript-ready artifact is now the
BACE/Tox21 sequence-family integration.

For BACE and Tox21, the integration reads distributed raw metric JSON files and
deduplicates by `run_id`, yielding 1,200 unique sequence runs with zero missing
expected rows: two tasks, three sequence architectures, two hidden dimensions,
20 seeds, and five exposure-aware splits. This gives the BACE/Tox21 C3
expansion a matching sequence-neural counterpart. BACE shows positive
standard-minus-clean deltas for SMILES-CNN and SMILES-GRU under exact,
scaffold, and NN@0.8 removal, whereas the SMILES-Transformer has negative
exact/scaffold/NN deltas but a positive density-matched delta. Tox21 shows
larger positive deltas for SMILES-CNN and SMILES-Transformer, while SMILES-GRU
has near-zero exact/density deltas and a negative NN@0.8 delta. This pattern is
useful for the paper because it argues against a simplistic "clean is always
harder" story; exposure-adjusted evaluation changes interpretation in a
task- and model-family-dependent way.

The paired delta-CI analysis provides the statistical credibility layer needed
for a C3 claim. Across completed metric tables, the analysis
forms 2,328 matched standard-vs-exposure-aware deltas and summarizes 80
task/model/split comparisons. For the BACE/Tox21 sequence-family subset, 24
comparisons are summarized from 1,200 runs. Most sequence-family deltas exclude
zero under bootstrap confidence intervals, including BACE SMILES-CNN and
Tox21 SMILES-CNN/Transformer comparisons. However, Tox21 SMILES-GRU
exact-removed and density-matched deltas cross zero. This should be presented
as strength rather than embarrassment: the framework detects when
exposure-adjusted score changes are stable and when they are not.

Figure callout: Fig. 5 should combine the existing BBBP/ClinTox model-family
sensitivity plot with `results/figures/bace_tox21_sequence_model_family.pdf`,
or present the BACE/Tox21 sequence-family plot as a separate panel. The caption
should say that these are sequence-neural baselines and not
foundation-model pretraining evidence.
`results/figures/exposure_delta_ci.pdf` can be used as the main Fig. 4
statistical-credibility panel, while `results/figures/sequence_delta_ci.pdf`
is better suited for supplement unless the main text has space for detailed
per-model intervals.

Evidence status: supported for C3/C5 model-family sensitivity across four
tasks, with complete BACE/Tox21 sequence-family coverage in
`results/tables/bace_tox21_sequence_coverage.csv`. Limited for
foundation-model conclusions until checkpoint-specific pretraining metadata
and wrappers are added.

### Frozen FM Embeddings Provide A Checkpoint-Light Wrapper Boundary

The frozen molecular foundation-model case study addresses a likely BIB
submission concern: a benchmark-trustworthiness framework should be able to run
checkpoint-light FM-style wrappers, while not turning those wrappers into
claims about model-specific ChEMBL exposure. The staged MolFormer safetensors
workflow contributes 1140 consolidated frozen-embedding metric rows with zero
failure rows. A second staged safetensors wrapper, ChemBERTa-100M, adds 150
frozen-embedding metric rows with zero failure rows across BACE, Tox21, BBBP,
ClinTox, CYP1A2, and CYP2C19. This is useful R7 evidence because it
demonstrates that MolTrustBench outputs can be applied to more than one frozen
FM embedding workflow under the same exposure-aware split contracts.

The result should remain a boundary claim. It does not show that MolFormer or
ChemBERTa used ChEMBL during pretraining, and it does not generalize to all
molecular foundation models. Prior blocked ChemBERTa attempts are retained as
artifact-format/runtime limitations rather than scientific negative results;
the new ChemBERTa-100M run is included only because a safetensors checkpoint
could be staged and loaded safely. These rows belong in the Supplement as
wrapper applicability evidence, while any model-specific exposure claim remains
explicitly out of scope.

Figure callout: use a supplementary table rather than a new main figure unless
the main Results needs a one-sentence R7 defense. The caption should say that
the MolFormer and ChemBERTa-100M tables support wrapper completeness and R5
wording discipline, not model-specific public exposure or a foundation-model
leaderboard.

Evidence status: supported for two staged safetensors FM wrappers. Limited for
broader FM claims because pretraining cutoffs remain unknown and the rows are
frozen-embedding wrapper checks, not model-specific pretraining audits.

### Regression Expansion Adds A Non-Classification Check And An Exposure-Aware Slice Boundary

The regression extension addresses a likely BIB scope concern that the
performance package could otherwise look classification- and toxicology-heavy.
Distributed GPU runs across ESOL and Lipophilicity were integrated from raw
metric tables, deduplicated by `run_id`, and reconciled into 1,200 unique
sequence-regression metric rows. The integration deliberately retains 4,160
expected-limitation rows and zero critical failures. This accounting matters:
ESOL produced complete standard and exposure-aware sequence-regression slices,
whereas Lipophilicity produced standard-split metrics but exposure-aware
slices were too small or absent under the current cutoff.

For ESOL, the paired regression CI analysis forms 960 matched
standard-vs-exposure-aware deltas and 24 task/model/split summaries across
SMILES-CNN, SMILES-GRU, and SMILES-Transformer with two hidden dimensions and
20 seeds. Twenty-two of the 24 RMSE intervals exclude zero, but the direction
is not uniform. Many exact, nearest-neighbor, and density-matched slices have
higher RMSE than matched standard runs, while ESOL SMILES-CNN temporal-future
and ESOL SMILES-GRU scaffold-removed show lower RMSE than standard. This is
the right kind of evidence for MolTrustBench: it shows that exposure-adjusted
evaluation changes interpretation beyond classification AUROC, while also
forcing the manuscript to report where exposure-aware subsets are not large enough for
a fair comparison.

Figure callout: `results/figures/regression_delta_ci.pdf` should be a
supplementary robustness figure unless the main text needs a compact
non-classification panel. The Lipophilicity expected-limitation table should
be cited in the Results or Supplement to show that invalid exposure-aware subsets were
not hidden.

Evidence status: supported as an ESOL regression robustness check. Limited
for regression generality because Lipophilicity exposure-aware slices
are not evaluable under the current cutoff.

### Assay Provenance Reveals Label-Reliability Risk Beyond Molecule Exposure

MolTrustBench also audits whether the molecules underlying benchmark labels
have heterogeneous public assay records. ChEMBL36 SQLite extraction identified
activity records for 1,289 BBBP molecules and 654 ClinTox molecules, with high
duplicate and conflict counts among molecules with public activity records.
For BBBP, the assay-provenance summary recorded 1,215 duplicated compounds,
677 molecules with conflicting derived label calls, 932 molecules with unit
inconsistency, and 728 threshold-sensitive molecules. For ClinTox, the
corresponding counts were 648 duplicated compounds, 502 conflicting label
calls, 613 unit inconsistencies, and 524 threshold-sensitive molecules. The
endpoint-native hERG pilot provides a cleaner assay-provenance case study:
4,999 ChEMBL-derived hERG molecules had activity coverage, with 1,591 duplicate
compounds, 163 conflicting label calls, and 2,646 threshold-sensitive molecules.
The CYP1A2/CYP2C19 extension adds two additional ChEMBL-derived endpoints with
nonempty provenance summaries and temporal split manifests. These CYP endpoints
now connect assay provenance to endpoint-native sequence baselines: the
observed-label sequence run contributes 360 metrics, 1080 expected exposure-removed slice
limitations, and zero critical failures, while the train-label-shuffle rescue
adds a matched negative-control layer. Together, these results support the C4
claim that benchmark trustworthiness is not only a
molecule-exposure problem; it also depends on assay source, measurement units,
censoring relations, thresholding choices, and document provenance.

The DILI/hepatotoxicity extension strengthens the toxicology-facing C4/R10
story without turning it into a leaderboard. It screens ChEMBL36
DILI/hepatotoxicity/cytotoxicity candidates, then constructs a ChEMBL-derived
DILI/hepatotoxicity text-evidence endpoint with 528 labeled activity rows and
513 benchmark molecules after release-index merge. The label definition is
conservative: positive hepatotoxicity evidence records must outvote no-evidence
records, and tied molecules are excluded. The resulting benchmark contains 369
positive and 144 negative molecules, 514 molecules with assay-provenance
summaries, 14 duplicated compounds, and one provenance-level
positive-versus-no-evidence text-label conflict before final label filtering.
Sequence baselines add 60 evaluable metrics with zero
failure rows on standard and scaffold-removed splits. Exact-removed,
NN@0.8-removed, temporal-future, and density-matched splits shrink to
one-class two-molecule tests, so they should be reported as expected
exposure-removed slice limitations rather than performance evidence.

Figure callout: Fig. 6 should show the assay-provenance heterogeneity map with separate rows
for BBBP, ClinTox, hERG, CYP1A2, and CYP2C19. Supplementary Table Sa should
summarize CYP assay-provenance fields and Supplementary Table Sb should connect
CYP1A2/CYP2C19 sequence and label-shuffle rescue outputs. Add Supplementary
Table Sc for DILI/hepatotoxicity candidate screening, endpoint provenance,
standard/scaffold sequence metrics, and expected exposure-removed slice limitations. The
Results text should distinguish overlapping public assay records for
MoleculeNet molecules from endpoint-native ChEMBL-derived labels.

Evidence status: supported for C4 after endpoint-native hERG plus
CYP1A2/CYP2C19 and DILI/hepatotoxicity extensions. Limited for full ADMET/Tox
coverage because the DILI clean/temporal future subsets are intentionally
reported as expected limitations.

### Trust Cards Convert The Audit Into A Reusable Reporting Standard

The final result is a reporting layer that turns exposure annotations,
exposure-adjusted metrics, assay provenance, and sanity checks into benchmark
trust cards. For each audited task, MolTrustBench records exact exposure,
scaffold exposure, NN exposure at multiple thresholds, exposure-removed subset sizes,
cutoff release, assay-provenance availability, and audit caveats.
The report card framing is important because the paper is not proposing a new
ADMET leaderboard. Instead, it asks benchmark users to report whether their
test molecules and labels were publicly observable before a relevant cutoff and
whether performance estimates are stable under exposure-aware slices.

Figure callout: Fig. 7 should show benchmark trust-card examples for BBBP,
ClinTox, BACE, and Tox21. Table 6 should be a minimum reporting
checklist covering public-exposure cutoff, exact/scaffold/NN exposure rates,
exposure-removed subset size, assay provenance, model pretraining metadata, and
exposure-adjusted scores.

Evidence status: supported for C5 as a generated reporting framework. Limited
for community-standard claims until the schema is documented in the supplement
and applied to a broader task panel.

## Reverse Outline And Claim-Evidence Map

| Paragraph block | Topic sentence role | Claim | Evidence | Status |
| --- | --- | --- | --- | --- |
| Release-time index | Establishes the audit timeline. | C1, C5 | Five ChEMBL release indexes and count table. | supported |
| Public exposure landscape | Shows measurable public exposure across tasks. | C1 | Four-task coverage summary, 12,290 molecules. | supported |
| Exposure levels | Explains why exact matching is insufficient. | C2 | Exact/scaffold/NN rates for BBBP, ClinTox, BACE, Tox21. | supported |
| Exposure-adjusted evaluation | Shows score sensitivity under exposure-removed subsets. | C3 | `slice_metrics.csv` for BBBP/ClinTox, `bace_tox21_c3_slice_metrics.csv`, and `bace_tox21_sequence_slice_metrics.csv` for BACE/Tox21. | supported, four-task scope for core exposure-adjusted slices |
| Density/temporal controls | Defines audit evidence boundaries. | C3, R2, R4 | Density-matched and temporal-future metrics. | preliminary-to-supported controls |
| Endpoint-native temporal tasks | Adds ChEMBL-derived hERG/CYP temporal evidence and exposes endpoint-specific exposure-removed slice limits. | C3, R8 | Endpoint-temporal metrics, Transformer add-on metrics, expected one-class exposure-removed slice limitations, zero critical failures. | supported, endpoint-specific scope |
| Frozen FM embeddings | Demonstrates staged checkpoint-light FM wrapper compatibility without asserting ChEMBL pretraining exposure. | R5, R7 | 1140 consolidated MolFormer rows plus 150 ChemBERTa-100M rows, zero failure rows for both safetensors wrappers; archived blocked attempts remain runtime limitations. | supported for two FM wrappers |
| Train-label-shuffle controls | Tests whether observed exposure-adjusted deltas exceed a null training-label baseline. | C3, R2, R6 | Original 360 valid null-control metrics with 18/22 observed-vs-null comparisons; CYP rescue adds 360 metrics, 1080 expected limitations, 0 critical failures, and 120 CYP2C19 temporal-delta pairs. | supported as a null-control boundary check, not causal evidence |
| Model-family sensitivity | Extends evaluation beyond one baseline family. | C3, C5 | CNN, GRU, Transformer, MLP sensitivity tables, with 1200/1200 expected BACE/Tox21 sequence-family rows and paired delta-CI tables. | supported, limited scope |
| Regression robustness | Extends exposure-adjusted evaluation beyond classification. | C3, R8 | ESOL regression sequence metrics and delta CIs; Lipophilicity expected limitations. | supported for ESOL, limited for Lipophilicity |
| Assay provenance | Adds label-source reliability evidence. | C4 | ChEMBL36 SQLite provenance, hERG pilot, CYP1A2/CYP2C19 summaries, and DILI/hepatotoxicity text-evidence endpoint with sequence baseline and expected-limitation accounting. | supported |
| Trust cards | Converts outputs into reporting standards. | C5 | Trust cards, auto report, sanity report. | supported |

## Submission-Facing Limitations To Keep In The Results

- Public exposure is an observable lower bound, not proof that any model trained
  on a specific molecule or recalled its label.
- ChEMBL release date is a public observability date, not a model pretraining
  cutoff.
- The four-task exposure audit now has matching four-task performance coverage for standard and exposure-removed slices, BACE/Tox21 has sequence-family coverage for the planned standard/exact/scaffold/NN@0.8/density-matched slices, ESOL adds a regression robustness layer, and endpoint-native hERG/CYP plus DILI/hepatotoxicity tasks add temporal-validity and assay-provenance evidence. Temporal-future evidence, CYP2C9 one-class exposure-removed slices, DILI one-class exposure-removed/temporal slices, BACE label-shuffle one-class standard-split rows, and Lipophilicity exposure-aware subsets remain smaller or invalid and must be reported as limitations.
- Train-label-shuffle controls are negative controls for reviewer defense, not causal proof that public exposure changed model behavior.
- Four of 22 observed-vs-null delta comparisons remain null-sensitive and
  should be named in the Results or Supplement.
- The CYP label-shuffle rescue forms 120 observed-vs-shuffled temporal-delta
  pairs for CYP2C19 but not CYP1A2; this is a coverage boundary, not a reason
  to discard the negative-control table.
- NN exposure in the fast coverage expansion is a same-scaffold lower-bound
  search; the full two-task Milestone 1 annotations remain the stronger NN
  evidence.
- Temporal-future subsets are currently small, especially ClinTox with 8 test
  molecules.
- MoleculeNet assay-provenance lookup shows public ChEMBL assay heterogeneity
  for overlapping molecules; hERG, CYP1A2, CYP2C19, and DILI/hepatotoxicity
  are cleaner endpoint-native ChEMBL-derived label provenance results.

## Self-Review Checklist

- Clarity: each subsection starts with one message and then gives numbers.
- Flow: the narrative moves from public observability to exposure levels,
  exposure-adjusted evaluation, assay provenance, and reporting standards.
- Terminology: the text uses public exposure and observable lower bound, not
  direct model-specific training exposure or label recall claims.
- Unsupported claims: no paragraph claims that exposure-removed subsets are universally
  harder, that ChEMBL release dates equal pretraining dates, or that a model used
  ChEMBL.
- Missing evidence: broader task performance, SIDER coverage, and
  checkpoint-specific foundation-model metadata remain next experiments before
  a strong final manuscript claim. MolFormer and ChemBERTa-100M are now valid
  frozen-embedding wrapper checks, while blocked FM attempts remain
  artifact-format limitations and should not be described as scientific
  failures.
