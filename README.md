# MolTrustBench

**MolTrustBench** is a benchmark trustworthiness audit framework for molecular AI. The tool name is **MolLeakTrace**. The paper target is:

> Benchmarking without Time Travel: Public-Exposure Auditing and Temporal Generalization in Molecular AI

This repository is not another ADMET leaderboard. Its purpose is to measure whether benchmark molecules, scaffolds, close chemical neighbors, or assay-derived labels were publicly observable before a model pretraining or benchmark evaluation cutoff.

## Milestone 1 Scope

Milestone 1 builds the first paper-signal MVP:

- ChEMBL release index for CHEMBL24, CHEMBL27, CHEMBL30, CHEMBL33, and CHEMBL36.
- Benchmark ingestion for at least two tasks.
- Exact, scaffold, and nearest-neighbor public-exposure annotation.
- Standard and exact-exposure-removed splits.
- Two classical baselines.
- Exposure summary, slice metrics, three publication draft figures, sanity checks, and `paper/auto_report.md`.

## Terminology

Use conservative audit language:

- public exposure
- potential exposure
- observable exposure lower bound
- temporal validity
- benchmark trustworthiness
- exposure-adjusted evaluation
- assay provenance
- benchmark trust card

Avoid claims of confirmed leakage, cheating, memorization proof, or contaminated models unless directly proven.

## Quick Start

Install the package in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Run the deterministic smoke pipeline:

```bash
make smoke-test
```

On Windows without GNU Make:

```powershell
.\make.ps1 smoke-test
```

The smoke pipeline uses tiny fixtures so the exposure logic can be tested without downloading full ChEMBL releases. Full ChEMBL release indexing is implemented through `moltrustbench-build-release-index`.

## External Anchors

- ChEMBL release dates and DOIs: https://chembl.gitbook.io/chembl-interface-documentation/downloads
- MolE evidence that TDC test molecules can overlap supervised pretraining corpora: https://www.nature.com/articles/s41467-024-53751-y
- BOOM as the molecular OOD benchmark boundary: https://papers.nips.cc/paper_files/paper/2025/hash/b94263f7f98c9766ea9a09761ddd88ee-Abstract-Datasets_and_Benchmarks_Track.html
- Briefings in Bioinformatics positioning: https://academic.oup.com/bib/pages/about

## Paper Discipline

Every major module should have a design note under `paper/design_notes/` that states:

- paper claim supported
- reviewer objection addressed
- output file proving success
- sanity checks required
