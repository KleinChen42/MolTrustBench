# MolTrustBench Auto Report

## Executive Summary

MolTrustBench audits benchmark trustworthiness through observable public-exposure lower bounds, exposure-adjusted evaluation, and paper-facing trust cards. Milestone 1 implements the release-index, exposure-annotation, baseline-evaluation, figure, and sanity-check spine.

Data provenance: This report is based on fixture smoke artifacts; it validates the pipeline but is not paper evidence from real ChEMBL releases.

## Claim-By-Claim Evidence Status

- C1 preliminary: exposure annotations and summary tables are generated.
- C2 preliminary: exact, scaffold, and nearest-neighbor exposure are separated.
- C3 preliminary: standard and exact-removed baseline metrics are generated.
- C4 missing: assay-provenance extraction remains a later-phase module.
- C5 preliminary: benchmark trust cards and reporting checks are generated.

## Exposure Audit Summary

| source_name | task_name | cutoff_release | n_molecules | exact_exposure_rate | scaffold_exposure_rate | nn_exposure_rate_06 | nn_exposure_rate_07 | nn_exposure_rate_08 | nn_exposure_rate_09 | median_exposure_risk_score | clean_exact_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tdc_admet | hERG | CHEMBL30 | 12 | 0.5833 | 0.9167 | 0.75 | 0.75 | 0.6667 | 0.5833 | 1 | 5 |
| moleculenet | BBBP | CHEMBL30 | 12 | 0.6667 | 0.9167 | 0.6667 | 0.6667 | 0.6667 | 0.6667 | 1 | 4 |

## Performance Delta Summary

| source_name | task_name | model_id | split_name | test_n | auroc | auprc | primary_score | exposure_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tdc_admet | hERG | morgan_logreg | standard | 6 | 0.2778 | 0.4444 | 0.2778 | 0.2778 |
| tdc_admet | hERG | morgan_logreg | exact_removed | 3 | 0 | 0.3333 | 0 | 0.2778 |
| moleculenet | BBBP | morgan_logreg | standard | 6 | 0.8889 | 0.9167 | 0.8889 | -0.1111 |
| moleculenet | BBBP | morgan_xgb | standard | 6 | 0.8333 | 0.75 | 0.8333 | -0.1667 |
| tdc_admet | hERG | morgan_xgb | standard | 6 | 0.3333 | 0.5 | 0.3333 | 0.08333 |
| moleculenet | BBBP | morgan_logreg | exact_removed | 2 | 1 | 1 | 1 | -0.1111 |
| tdc_admet | hERG | morgan_xgb | exact_removed | 3 | 0.25 | 0.3333 | 0.25 | 0.08333 |
| moleculenet | BBBP | morgan_xgb | exact_removed | 2 | 1 | 1 | 1 | -0.1667 |

## Benchmark Trust Cards

- moleculenet:BBBP cutoff CHEMBL30 - exact exposure 0.67, scaffold exposure 0.92, NN>=0.8 exposure 0.67, risk high.
- tdc_admet:hERG cutoff CHEMBL30 - exact exposure 0.58, scaffold exposure 0.92, NN>=0.8 exposure 0.67, risk high.

## Reviewer Risk Table

The core limitation is explicit: public exposure is an observable lower bound, not proof that a model trained on a molecule or memorized its label. Density-matched controls and assay-provenance diagnostics remain required before stronger causal claims.

## Sanity Check Summary

Critical/warning checks run: 19. Failed checks: 0.

## Next Experiments

- Replace fixture smoke data with full CHEMBL24/27/30/33/36 SQLite release indexes.
- Expand benchmark ingestion to more TDC ADMET, MoleculeNet selected tasks, and MoleculeACE.
- Add scaffold-removed, NN-removed, temporal-future, and density-matched clean splits.
- Implement assay-provenance extraction and conflict scoring for ChEMBL-derived endpoints.

## Target Journal Positioning

Primary target: Briefings in Bioinformatics as a reproducible bioinformatics resource and reporting standard. Patterns is appropriate for the benchmark-validity data-science framing. Archives of Toxicology becomes stronger after assay-provenance and ADMET/Tox label-conflict analyses are complete.
