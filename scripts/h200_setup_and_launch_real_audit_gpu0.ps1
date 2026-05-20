param(
    [string]$RemoteDir = "/data/EAAI_PROJECT/MolTrustBench"
)

$ErrorActionPreference = "Stop"
$cmd = @'
set -e
cd /data/EAAI_PROJECT/MolTrustBench
git pull --ff-only
chmod +x scripts/setup_h200_env.sh scripts/run_real_audit_gpu0.sh
export MOLTRUST_ENV_NAME=moltrustbench
scripts/setup_h200_env.sh
export MOLTRUST_PYTHON="/home/zetyun/miniconda3/bin/conda run -n moltrustbench python"
setsid -f bash scripts/run_real_audit_gpu0.sh > results/logs/real_audit_gpu0/launcher.log 2>&1 < /dev/null
echo LAUNCHED_REAL_AUDIT_GPU0
echo LOG=results/logs/real_audit_gpu0/launcher.log
'@

powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\invoke_h200_command.ps1" `
    -RemoteDir $RemoteDir `
    -RemoteCommand $cmd
