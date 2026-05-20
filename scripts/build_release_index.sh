#!/usr/bin/env bash
set -euo pipefail
python -m moltrustbench.data.build_release_index "$@"
