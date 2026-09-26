param(
    [string]$OutputRoot = "results/sa_expansion"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
$Seed = 2026

if (-not [IO.Path]::IsPathRooted($OutputRoot)) {
    $OutputRoot = Join-Path $ProjectRoot $OutputRoot
}
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

# Frozen before the expansion run from historical full100 results. Do not change
# this set in response to expansion outcomes.
$Jobs = @(
    [pscustomobject]@{ Case = "case_054"; Problem = 2; Cores = 2; Reason = "large; historical multiseed=vns=510272 (stagnation)" },
    [pscustomobject]@{ Case = "case_058"; Problem = 1; Cores = 2; Reason = "large; historical multiseed=vns=2230995 (stagnation)" },
    [pscustomobject]@{ Case = "case_062"; Problem = 2; Cores = 4; Reason = "large; historical multiseed=vns=811802 (stagnation)" },
    [pscustomobject]@{ Case = "case_046"; Problem = 1; Cores = 4; Reason = "historical multiseed=vns=140604 (stagnation); P1/N4 coverage" },
    [pscustomobject]@{ Case = "case_039"; Problem = 1; Cores = 4; Reason = "historical VNS gain 12.35% (clearly effective)" },
    [pscustomobject]@{ Case = "case_065"; Problem = 2; Cores = 4; Reason = "historical VNS gain 14.17% (clearly effective)" },
    [pscustomobject]@{ Case = "case_053"; Problem = 1; Cores = 2; Reason = "large; historical VNS gain 7.92%" },
    [pscustomobject]@{ Case = "case_050"; Problem = 2; Cores = 2; Reason = "historical VNS gain 7.53%; Stage 1 SA tie" }
)
$Arms = @(
    [pscustomobject]@{ Name = "control"; Config = "configs/sa_expansion_control.yaml" },
    [pscustomobject]@{ Name = "sa"; Config = "configs/sa_expansion_sa.yaml" }
)

Write-Host "[Selected tasks]"
foreach ($Job in $Jobs) {
    Write-Host ("{0} P{1} N{2}: {3}" -f $Job.Case, $Job.Problem, $Job.Cores, $Job.Reason)
}

Push-Location $ProjectRoot
try {
    foreach ($Arm in $Arms) {
        foreach ($Job in $Jobs) {
            $taskName = "{0}_p{1}_n{2}" -f $Job.Case, $Job.Problem, $Job.Cores
            $taskOutput = Join-Path $OutputRoot ("{0}\{1}" -f $Arm.Name, $taskName)
            if (Test-Path -LiteralPath (Join-Path $taskOutput $taskName "job.json")) {
                Write-Host "Skipping completed task: seed=$Seed arm=$($Arm.Name) task=$taskName"
                continue
            }
            & $Python scripts/run_all.py `
                --output $taskOutput `
                --problem $Job.Problem `
                --cores $Job.Cores `
                --cases $Job.Case `
                --config data/config.txt `
                --solver-config $Arm.Config `
                --skip-cli-verification
            if ($LASTEXITCODE -ne 0) {
                throw "Expansion failed: seed=$Seed arm=$($Arm.Name) task=$taskName exit=$LASTEXITCODE"
            }
        }
    }
}
finally {
    Pop-Location
}

Write-Host "Expansion outputs: $OutputRoot"
Write-Host "Report command: $Python scripts/report_sa_expansion.py --run-root `"$OutputRoot`""
