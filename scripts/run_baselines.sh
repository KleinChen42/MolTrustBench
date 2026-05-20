#!/usr/bin/env bash
set -euo pipefail
python -m moltrustbench.training.train "$@"
