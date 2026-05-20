# GPU0 Overnight Morgan-MLP Baseline

## Purpose

Use the otherwise idle GPU0 window to run a bounded neural baseline after the
real-data exposure audit completes. This is not a foundation-model sweep. It is
a reviewer-facing control for whether exposure-adjusted performance deltas also
appear in a small GPU-trained neural model.

## Paper Claim Supported

- C3: standard, exposure-removed, and density-matched subsets can yield
  different model performance.

The output is preliminary until density-matched controls and sanity checks are
inspected on real benchmark tasks.

## Reviewer Objections Addressed

- R2: Exposure is just chemical-space density.
- R6: The work is just data cleaning.
- R7: Foundation model wrappers are incomplete.
- R8: Clean subsets are too small.

## Proof Artifacts

- `results/tables/gpu_mlp_slice_metrics.csv`
- `results/predictions/gpu-mlp-*.parquet`
- `results/logs/gpu0_nightly_mlp/status.tsv`
- `results/logs/gpu0_nightly_mlp/job_manifest.jsonl`
- `results/logs/gpu0_nightly_mlp/summary.json`

## Sanity Checks

- The job must run with `CUDA_VISIBLE_DEVICES=0`.
- The job must fail rather than silently run on CPU if CUDA is unavailable.
- It must wait for real exposure annotations before training.
- It must include `standard`, `exact_removed`, and `density_matched_clean`
  when clean subsets are available.
- It must preserve public-exposure terminology and avoid claims of confirmed
  leakage or memorization.
