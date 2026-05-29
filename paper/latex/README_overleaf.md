# MolTrustBench OUP/BIB LaTeX Bundle

This folder is prepared for Overleaf compilation of the MolTrustBench manuscript.

## Main File

- Compile `moltrustbench_main.tex`.

## Intended Overleaf Settings

- Compiler: `pdfLaTeX` preferred.
- Bibliography: BibTeX.
- Main file: `moltrustbench_main.tex`.

## Template Notes

- The OUP class is called with explicit BIB/OUP-style options:
  `unnumsec, webpdf, contemporary, large, numbered`.
- The manuscript type is set to `Problem Solving Protocol`.
- The highlighted box uses `Key Points`.
- References use the numeric OUP bibliography style `oup-plain`.
- Long artifact paths were shortened or made breakable to reduce column overflow risk.

## Figure Assets

All manuscript figure PDFs are in `figures/`.

- `workflow_schematic.pdf`
- `release_histogram.pdf`
- `exposure_heatmap_coverage.pdf`
- `exposure_delta_ci.pdf`
- `bace_tox21_sequence_model_family.pdf`
- `assay_conflict_map.pdf`
- `trust_card_examples.pdf`
- `label_shuffle_null_control.pdf` is included for supplement-first null-control reuse

## Conservative Interpretation

The manuscript uses public exposure, observable exposure lower bound, temporal validity,
assay provenance, exposure-adjusted evaluation, and benchmark trust cards. It does
not make model-specific training-exposure or memorization claims.
