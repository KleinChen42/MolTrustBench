param(
    [string]$RemoteDir = "/data/EAAI_PROJECT"
)

$cmd = @'
echo ===DATE===
date
echo ===PWD===
pwd
echo ===GPU===
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
echo ===Q2G_OR_BENCH_PIDS===
pgrep -af 'EAAI_PROJECT|EAAI_PROJECT|eaai|run_matrix|run_single|python' || true
'@

powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\invoke_h200_command.ps1" `
    -RemoteDir $RemoteDir `
    -RemoteCommand $cmd
