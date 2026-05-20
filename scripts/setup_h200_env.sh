#!/usr/bin/env bash
set -euo pipefail

CONDA_BIN="${CONDA_BIN:-/home/zetyun/miniconda3/bin/conda}"
ENV_NAME="${MOLTRUST_ENV_NAME:-moltrustbench}"
CONDA_CHANNEL_ARGS="${CONDA_CHANNEL_ARGS:---override-channels -c conda-forge}"

if [ ! -x "$CONDA_BIN" ]; then
  echo "conda not found at $CONDA_BIN" >&2
  exit 2
fi

echo "[setup] creating/updating conda env: $ENV_NAME"
if "$CONDA_BIN" env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  # Keep the solver on one explicit channel set; inherited HPC configs often
  # add many mirrors and make RDKit environment resolution much slower.
  # shellcheck disable=SC2086
  "$CONDA_BIN" install -y -n "$ENV_NAME" $CONDA_CHANNEL_ARGS \
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
  # shellcheck disable=SC2086
  "$CONDA_BIN" create -y -n "$ENV_NAME" $CONDA_CHANNEL_ARGS \
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
