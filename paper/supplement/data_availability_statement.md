# Data Availability Statement For BIB Submission

The data availability statement below is ready to paste after replacing the repository placeholder with a DOI or accession.

## Ready-To-Paste Draft

All processed data, exposure annotations, generated benchmark splits, summary tables, figure source data, supplementary tables, trust-card JSON examples, and analysis manifests needed to reproduce the results in this article are provided in the MolTrustBench evidence archive and supplement package: **[repository DOI/accession to be inserted]**. The local archive corresponding to this draft is `results/archive/moltrustbench_data_freeze_20260529_161700.tgz` (SHA256 `beb779864151105b3c8cd13507df8f0779bfc53e2d6a4f6a792d82f91e34b2df`; manifest `moltrustbench_data_freeze_20260529_161700_manifest.csv`). The supplement package under `paper/supplement/` includes Tables S1-S29, including slice validity, standardization audit, assay-flag definitions, provenance examples, trust-card schema, and figure source-data mapping. The archive excludes raw ChEMBL database dumps, local secrets, transient caches, and third-party model checkpoints. ChEMBL source releases are publicly available from the official ChEMBL downloads page, and benchmark datasets are available from their original public sources. Frozen foundation-model checkpoint artifacts are not redistributed in the archive; scripts record the staged checkpoint identifiers and reproduce embeddings when the corresponding public checkpoint is available under its own license. Code is available at the project repository **[GitHub URL and commit SHA to be inserted]**.

## Repository Actions Before Submission

- Deposit the current data-freeze archive, manifest, and BIB supplement package in a DOI-issuing repository such as Zenodo, Figshare, OSF, or Harvard Dataverse.
- Add the DOI/accession to the statement above and to `paper/latex/moltrustbench_main.tex`.
- Add the GitHub commit SHA or tagged release corresponding to the submitted manuscript.
- Include dataset citations in the reference list for ChEMBL and any third-party benchmark datasets used in the article.

## Placeholder Search Before Submission

- `[repository DOI/accession to be inserted]`
- `[GitHub URL and commit SHA to be inserted]`
- `DOI added during production`
- `Date added during production`
- `submission-metadata-required@example.invalid`
- author, affiliation, funding, acknowledgment, and conflict-of-interest placeholders

## Risk Flags

- Do not state that raw ChEMBL SQLite or raw ChEMBL release tarballs are redistributed unless their licensing and size are explicitly handled by the repository deposit.
- Do not use "available on request" for generated result tables; BIB requires a Data Availability statement and strongly encourages public availability where ethically feasible.
- Model checkpoints should be cited or linked through their original hosts, not republished inside the evidence archive unless license terms allow it.
