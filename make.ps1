param(
    [string]$Target = "smoke-test"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
switch ($Target) {
    "smoke-test" {
        python -m pytest -q
        python -m moltrustbench.smoke --allow-fallback-standardizer
    }
    "test" {
        python -m pytest -q
    }
    "smoke" {
        python -m moltrustbench.smoke --allow-fallback-standardizer
    }
    "clean-fixtures" {
        python -m moltrustbench.smoke --clean
    }
    default {
        throw "Unknown target: $Target"
    }
}
