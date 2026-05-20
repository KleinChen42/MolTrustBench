#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <annotation.parquet> <output-split.json> [control-table.csv]" >&2
  exit 2
fi

annotation_path="$1"
output_split="$2"
control_table="${3:-results/tables/density_matched_controls.csv}"

python -m moltrustbench.splits.density_matched \
  --annotations "$annotation_path" \
  --output "$output_split" \
  --control-table "$control_table"
