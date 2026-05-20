# Design Note: Exposure-Sliced Evaluation

Paper claim: C3, C5.

Reviewer objection: R2, R6, R8.

Output file proving success:
- `results/tables/slice_metrics.csv`
- `results/figures/performance_drop.pdf`

Sanity checks:
- Standard and exact-removed test subsets have sample counts.
- Metrics are finite.
- Clean subset size is reported and warning-gated.
- Model comparisons are framed as benchmark-validity probes, not final leaderboard claims.
