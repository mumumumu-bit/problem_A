$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }

Push-Location $ProjectRoot
try {
    & $Python scripts/run_all.py `
        --output results/smoke_n35 `
        --problem 1 2 3 `
        --cores 3 5 `
        --cases case_001 case_019 `
        --config data/config.txt `
        --solver-config configs/fullrun_stable.yaml `
        --workers 1 `
        --time-budget 30 `
        --max-evaluations 12 `
        --skip-cli-verification
    if ($LASTEXITCODE -ne 0) { throw "Smoke run failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
