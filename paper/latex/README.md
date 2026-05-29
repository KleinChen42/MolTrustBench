# MolTrustBench OUP LaTeX Draft

This directory contains the Oxford University Press authoring-template manuscript for
MolTrustBench.

Main manuscript:

- `moltrustbench_main.tex`
- `figures/` contains the main-text PDF figure assets plus the
  supplement-first label-shuffle negative-control asset.

Template files copied from `OUP_General_Template.zip`:

- `oup-authoring-template.cls`
- `oup-abbrvnat.bst`
- `oup-plain.bst`

The original extracted template remains under `oup-authoring-template/` for
reference.

Suggested build sequence when a LaTeX distribution is available:

```bash
pdflatex moltrustbench_main.tex
bibtex moltrustbench_main
pdflatex moltrustbench_main.tex
pdflatex moltrustbench_main.tex
```

The manuscript first reads figures from the local `figures/` directory and then
falls back to `../../results/figures/` if a local asset is missing. This keeps
the LaTeX folder portable for OUP/Overleaf while preserving local development
fallbacks.

Current local environment note: the Windows TeXLive installation in this session
is incomplete, so the latest update has been checked with static LaTeX hygiene
checks and figure-render QA rather than local PDF compilation. The bundle is
prepared for Overleaf compilation.
