#!/usr/bin/env bash
#SBATCH --job-name=moltrust-train
#SBATCH --output=results/logs/train_%A_%a.out
#SBATCH --gres=gpu:1
python -m moltrustbench.training.train "$@"
