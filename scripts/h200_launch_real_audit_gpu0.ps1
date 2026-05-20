param(
    [string]$RemoteDir = "/data/EAAI_PROJECT/MolTrustBench",
    [string]$RemoteScript = "scripts/run_real_audit_gpu0.sh",
    [string]$LogPath = "results/logs/real_audit_gpu0/launcher.log"
)

$ErrorActionPreference = "Stop"

powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\h200_launch_detached.ps1" `
    -RemoteDir $RemoteDir `
    -RemoteScript $RemoteScript `
    -LogPath $LogPath
