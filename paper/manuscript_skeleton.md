# Manuscript Skeleton

Title: Benchmarking without Time Travel: Public-Exposure Auditing and Temporal Generalization in Molecular AI

## Abstract

Molecular AI benchmarks often assume that held-out molecules represent unseen future chemistry. In the foundation model era, this assumption can fail because molecules, scaffolds, close neighbors, and assay-derived labels may already be publicly observable before model pretraining or benchmark evaluation. MolTrustBench provides a reproducible framework for public-exposure auditing, exposure-aware evaluation, temporal split construction, assay-provenance diagnosis, and benchmark trust cards.

## Introduction

1. Molecular benchmarks guide model selection for drug discovery and toxicology.
2. Recent ADMET and OOD benchmarks test reliability under data scarcity, imbalance, bRo5 chemistry, activity cliffs, and distribution shift.
3. A different validity question remains: did the test chemistry or labels already exist in public chemical corpora?
4. MolTrustBench audits this temporal-validity assumption without claiming confirmed leakage.

## Methods

- ChEMBL release-time index.
- Deterministic molecule standardization.
- Exact, scaffold, and nearest-neighbor public-exposure annotation.
- Exposure-aware splits and exposure-adjusted evaluation.
- Benchmark trust cards.
- Assay-provenance extension.

## Results

- C1: Public exposure exists at multiple levels.
- C2: Scaffold and NN exposure exceed exact molecule exposure.
- C3: Standard and clean/exposure-removed performance can differ.
- C4: Assay provenance identifies label instability risks.
- C5: Trust cards provide benchmark reporting standards.

## Discussion

The central claim is not that models cheated or memorized. The claim is that benchmark users need observable public-exposure lower bounds, temporal-future subsets, and assay provenance before interpreting leaderboard scores as prospective generalization.
