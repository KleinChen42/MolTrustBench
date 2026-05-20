#!/usr/bin/env bash
set -euo pipefail
python -m moltrustbench.audit.exact_exposure "$@"
