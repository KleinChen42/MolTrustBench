#!/usr/bin/env bash
#SBATCH --job-name=moltrust-audit
#SBATCH --output=results/logs/audit_%A_%a.out
#SBATCH --gres=gpu:0
python -m moltrustbench.audit.exact_exposure "$@"
