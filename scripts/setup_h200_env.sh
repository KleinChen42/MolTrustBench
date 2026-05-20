#!/usr/bin/env bash
set -euo pipefail

CONDA_BIN="${CONDA_BIN:-/home/zetyun/miniconda3/bin/conda}"
ENV_NAME="${MOLTRUST_ENV_NAME:-moltrustbench}"

if [ ! -x "$CONDA_BIN" ]; then
  echo "conda not found at $CONDA_BIN" >&2
  exit 2
fi

echo "[setup] creating/updating conda env: $ENV_NAME"
if "$CONDA_BIN" env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  "$CONDA_BIN" install -y -n "$ENV_NAME" -c conda-forge \
    python=3.10 \
    rdkit \
    pandas \
    pyarrow \
    numpy \
    scikit-learn \
    matplotlib \
    pyyaml \
    requests \
    pytest
else
  "$CONDA_BIN" create -y -n "$ENV_NAME" -c conda-forge \
    python=3.10 \
    rdkit \
    pandas \
    pyarrow \
    numpy \
    scikit-learn \
    matplotlib \
    pyyaml \
    requests \
    pytest
fi

echo "[setup] installing Python packages"
"$CONDA_BIN" run -n "$ENV_NAME" python -m pip install --upgrade pip
"$CONDA_BIN" run -n "$ENV_NAME" python -m pip install -e ".[dev]" PyTDC xgboost lightgbm

echo "[setup] verifying imports"
"$CONDA_BIN" run -n "$ENV_NAME" python -c "import rdkit, pandas, pyarrow, sklearn, tdc; print('ok', rdkit.__version__)"
