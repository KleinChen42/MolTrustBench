#!/usr/bin/env bash
set -euo pipefail

export CUDA_VISIBLE_DEVICES=0
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

RUN_DIR="results/logs/real_audit_gpu0"
mkdir -p "$RUN_DIR"
echo "$$" > "$RUN_DIR/pid"

exec > >(tee -a "$RUN_DIR/stdout.log") 2> >(tee -a "$RUN_DIR/stderr.log" >&2)

status() {
  local stage="$1"
  local state="$2"
  local detail="${3:-}"
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$stage" "$state" "$detail" >> "$RUN_DIR/status.tsv"
}

echo -e "timestamp\tstage\tstatus\tdetail" > "$RUN_DIR/status.tsv"
status "gpu0_policy" "started" "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"

if command -v nvidia-smi >/dev/null 2>&1; then
  for attempt in $(seq 1 24); do
    mem_used="$(nvidia-smi --id=0 --query-gpu=memory.used --format=csv,noheader,nounits | head -n 1 | tr -d ' ')"
    mem_used="${mem_used:-0}"
    if [ "$mem_used" -lt 20000 ]; then
      status "gpu0_policy" "available" "memory_used_mib=${mem_used}"
      break
    fi
    status "gpu0_policy" "waiting" "attempt=${attempt} memory_used_mib=${mem_used}"
    sleep 300
    if [ "$attempt" -eq 24 ]; then
      status "gpu0_policy" "failed" "GPU0 remained busy; no other GPU was used"
      exit 75
    fi
  done
else
  status "gpu0_policy" "warning" "nvidia-smi not found; continuing with CUDA_VISIBLE_DEVICES=0"
fi

PYTHON_BIN="${MOLTRUST_PYTHON:-python}"
status "real_audit" "started" "$PYTHON_BIN"

"$PYTHON_BIN" -m moltrustbench.real_audit \
  --release CHEMBL24 \
  --release CHEMBL27 \
  --release CHEMBL30 \
  --release CHEMBL33 \
  --release CHEMBL36 \
  --cutoff-release CHEMBL30 \
  --moleculenet-fallback ClinTox

status "real_audit" "completed" "summary=results/logs/real_audit_gpu0/summary.json"
