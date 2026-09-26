$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
$Cases = Get-Content -LiteralPath (Join-Path $ProjectRoot "configs/full100_C.txt") | Where-Object { $_.Trim() }

Push-Location $ProjectRoot
try {
    & $Python scripts/run_all.py --output results/full100_teammate_C `
        --problem 1 2 3 --cores 2 3 4 5 --cases $Cases `
        --config data/config.txt --solver-config configs/fullrun_stable.yaml `
        --workers 2 --time-budget 300 --max-evaluations 64 --skip-cli-verification
    if ($LASTEXITCODE -ne 0) { throw "Full run C failed with exit code $LASTEXITCODE" }
}
finally { Pop-Location }
