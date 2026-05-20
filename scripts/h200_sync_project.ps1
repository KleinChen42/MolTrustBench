param(
    [string]$RemoteDir = "/data/EAAI_PROJECT/MolTrustBench"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Archive = "C:\tmp\moltrustbench_sync.tar.gz"

if (Test-Path $Archive) {
    Remove-Item -LiteralPath $Archive -Force
}

tar `
    --exclude ".env.local" `
    --exclude ".git" `
    --exclude ".venv" `
    --exclude "__pycache__" `
    --exclude ".pytest_cache" `
    --exclude "pytest-cache-files-*" `
    --exclude "data/raw/chembl" `
    --exclude "results/predictions" `
    --exclude "results/metrics" `
    --exclude "results/figures" `
    --exclude "results/benchmark_annotations" `
    -czf $Archive `
    -C $ProjectRoot .

$remotePrep = "mkdir -p '$RemoteDir'"
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\invoke_h200_command.ps1" `
    -RemoteDir "" `
    -NoCD `
    -RemoteCommand $remotePrep

$RemoteUser = "zetyun"
$RemoteHost = "183.166.183.2"
$RemotePort = "60071"
$SshKeyName = "hd03-tenant13-research-20260405"
$KeyPath = Join-Path $HOME ".ssh\$SshKeyName"
$ScpExe = "C:\Windows\System32\OpenSSH\scp.exe"
if (!(Test-Path $ScpExe)) {
    $found = Get-Command scp -ErrorAction SilentlyContinue
    if ($found) { $ScpExe = $found.Source }
    else { throw "scp.exe not found. Enable Windows OpenSSH Client." }
}

$AskPassCmd = Join-Path $PSScriptRoot "ssh_askpass.cmd"
$LocalEnvPath = Join-Path $ProjectRoot ".env.local"
if (Test-Path $LocalEnvPath) {
    Get-Content $LocalEnvPath | ForEach-Object {
        $line = $_.Trim()
        if (!$line -or $line.StartsWith("#") -or !$line.Contains("=")) { return }
        $parts = $line.Split("=", 2)
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim().Trim('"').Trim("'"), "Process")
    }
}
$env:SSH_ASKPASS = $AskPassCmd
$env:SSH_ASKPASS_REQUIRE = "force"
$env:DISPLAY = ":0"

& $ScpExe -o StrictHostKeyChecking=accept-new -i $KeyPath -P $RemotePort $Archive "${RemoteUser}@${RemoteHost}:${RemoteDir}/moltrustbench_sync.tar.gz"

$remoteExtract = "cd '$RemoteDir' && tar -xzf moltrustbench_sync.tar.gz && rm -f moltrustbench_sync.tar.gz && chmod +x scripts/run_real_audit_gpu0.sh"
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\invoke_h200_command.ps1" `
    -RemoteDir "" `
    -NoCD `
    -RemoteCommand $remoteExtract

Write-Host "[h200] synced project to $RemoteDir"
