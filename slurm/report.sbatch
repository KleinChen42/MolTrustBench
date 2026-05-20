#!/usr/bin/env bash
#SBATCH --job-name=moltrust-report
#SBATCH --output=results/logs/report_%j.out
#SBATCH --gres=gpu:0
python -m moltrustbench.smoke --allow-fallback-standardizer
