# MolTrustBench Deposit README

Purpose: make the Briefings in Bioinformatics submission auditable without
redistributing raw ChEMBL dumps or third-party checkpoints.

## Upload To DOI Repository

Upload these artifacts together to Zenodo, Figshare, OSF, or Harvard Dataverse:

- `results/archive/moltrustbench_data_freeze_20260529_161700.tgz`
- `results/archive/moltrustbench_data_freeze_20260529_161700_manifest.csv`
- `results/archive/moltrustbench_data_freeze_20260529_161700_summary.json`
- latest `paper/supplement/MolTrustBench_BIB_supplement_package_*.zip`
- final Overleaf/OUP LaTeX bundle from `paper/latex_compile_bundle/`
- final compiled manuscript PDF, if the repository allows manuscript previews
- tagged GitHub code snapshot or a Zenodo-linked GitHub release archive

## Include In The Deposited README

- Archive SHA256:
  `beb779864151105b3c8cd13507df8f0779bfc53e2d6a4f6a792d82f91e34b2df`
- GitHub repository URL and release tag or commit SHA.
- DOI/accession assigned by the repository.
- License for generated evidence tables and code snapshot.
- Access date for ChEMBL releases, benchmark datasets, and public checkpoints.
- Python, RDKit, pandas, scikit-learn, PyTorch, and plotting environment notes.
- Command to regenerate supplement tables:
  `python scripts/make_bib_supplement_package.py`
- Command to rerun paper-facing sanity checks:
  `python -m moltrustbench.evaluation.sanity_checks --fail-on-critical`
- Statement that ChEMBL release dates are public-observability dates, not
  model-specific pretraining dates.

## Do Not Upload

- raw ChEMBL SQLite, MySQL, PostgreSQL, SDF, or chemreps dumps;
- `.env`, `.env.local`, SSH keys, tokens, or remote host credentials;
- Hugging Face or other public model checkpoints unless the license explicitly
  permits redistribution;
- transient GPU logs that contain local paths but no paper-facing source data;
- cache directories.

## DOI Placeholder Replacement Checklist

Before submission, replace placeholders in:

- `paper/latex/moltrustbench_main.tex`
- `paper/data_availability_bib.md`
- `paper/supplement/data_availability_statement.md`
- `paper/supplement/README.md`, if a DOI-specific note is added

Search these exact placeholders and replace them only after deposit/release:

- `[repository DOI/accession to be inserted]`
- `[GitHub URL and commit SHA to be inserted]`
- `DOI added during production`
- `Date added during production`
- `Author One`, `Author Two`, `MolTrustBench Consortium`
- `author@example.com`
- funding, acknowledgment, conflict-of-interest, and affiliation placeholders

Use DataCite-style citations for deposited evidence and cite ChEMBL,
benchmark datasets, and public checkpoints through their original sources.
