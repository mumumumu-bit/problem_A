param(
    [string]$OutputRoot
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }

if (-not $OutputRoot) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $OutputRoot = Join-Path $ProjectRoot ("results\sa_pilot_" + $stamp)
}
elseif (-not [IO.Path]::IsPathRooted($OutputRoot)) {
    $OutputRoot = Join-Path $ProjectRoot $OutputRoot
}
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
if (Test-Path -LiteralPath $OutputRoot) {
    throw "Output directory already exists; refusing to overwrite: $OutputRoot"
}
New-Item -ItemType Directory -Path $OutputRoot | Out-Null

$Jobs = @(
    [pscustomobject]@{ Case = "case_001"; Problem = 1; Cores = 2 },
    [pscustomobject]@{ Case = "case_005"; Problem = 1; Cores = 4 },
    [pscustomobject]@{ Case = "case_025"; Problem = 2; Cores = 2 },
    [pscustomobject]@{ Case = "case_050"; Problem = 2; Cores = 2 }
)

function Invoke-PilotArm {
    param(
        [string]$Arm,
        [string]$SolverConfig
    )
    foreach ($Job in $Jobs) {
        $TaskName = "{0}_p{1}_n{2}" -f $Job.Case, $Job.Problem, $Job.Cores
        $TaskOutput = Join-Path (Join-Path $OutputRoot $Arm) $TaskName
        & $Python scripts/run_all.py `
            --output $TaskOutput `
            --problem $Job.Problem `
            --cores $Job.Cores `
            --cases $Job.Case `
            --config data/config.txt `
            --solver-config $SolverConfig `
            --skip-cli-verification
        if ($LASTEXITCODE -ne 0) {
            throw "$Arm task $TaskName failed with exit code $LASTEXITCODE"
        }
    }
}

Push-Location $ProjectRoot
try {
    Invoke-PilotArm -Arm "control" -SolverConfig "configs/pilot_vns_control.yaml"
    Invoke-PilotArm -Arm "sa" -SolverConfig "configs/pilot_sa_vns.yaml"
}
finally {
    Pop-Location
}

Write-Host "Pilot outputs: $OutputRoot"
Write-Host "Report command: $Python scripts/report_sa_pilot.py --run-root `"$OutputRoot`""
