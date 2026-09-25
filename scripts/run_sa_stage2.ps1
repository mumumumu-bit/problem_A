param(
    [string]$OutputRoot = "results/sa_pilot_stage2"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }

if (-not [IO.Path]::IsPathRooted($OutputRoot)) {
    $OutputRoot = Join-Path $ProjectRoot $OutputRoot
}
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$Seeds = @(2026, 2027, 2028)
$Jobs = @(
    [pscustomobject]@{ Case = "case_005"; Problem = 1; Cores = 4 },
    [pscustomobject]@{ Case = "case_001"; Problem = 1; Cores = 2 }
)
$Arms = @(
    [pscustomobject]@{ Name = "control"; Config = "configs/pilot_stage2_control.yaml" },
    [pscustomobject]@{ Name = "sa"; Config = "configs/pilot_stage2_sa.yaml" }
)
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Get-SeedConfig {
    param(
        [int]$Seed,
        [string]$Arm,
        [string]$BaseConfig
    )
    $data = Get-Content -LiteralPath (Join-Path $ProjectRoot $BaseConfig) -Raw | ConvertFrom-Json
    $data.seed = $Seed
    $json = $data | ConvertTo-Json -Compress -Depth 10
    $configDir = Join-Path $OutputRoot ("seed_{0}\_configs" -f $Seed)
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    $configPath = Join-Path $configDir ("{0}.yaml" -f $Arm)
    if (Test-Path -LiteralPath $configPath) {
        $existing = (Get-Content -LiteralPath $configPath -Raw).Trim()
        if ($existing -ne $json) {
            throw "Existing derived config differs; refusing to overwrite: $configPath"
        }
    }
    else {
        [IO.File]::WriteAllText($configPath, $json + [Environment]::NewLine, $Utf8NoBom)
    }
    return $configPath
}

Push-Location $ProjectRoot
try {
    foreach ($Seed in $Seeds) {
        foreach ($Arm in $Arms) {
            $seedConfig = Get-SeedConfig -Seed $Seed -Arm $Arm.Name -BaseConfig $Arm.Config
            foreach ($Job in $Jobs) {
                $taskName = "{0}_p{1}_n{2}" -f $Job.Case, $Job.Problem, $Job.Cores
                $taskOutput = Join-Path $OutputRoot ("seed_{0}\{1}\{2}" -f $Seed, $Arm.Name, $taskName)
                if (Test-Path -LiteralPath (Join-Path $taskOutput "job.json")) {
                    Write-Host "Skipping completed task: seed=$Seed arm=$($Arm.Name) task=$taskName"
                    continue
                }
                & $Python scripts/run_all.py `
                    --output $taskOutput `
                    --problem $Job.Problem `
                    --cores $Job.Cores `
                    --cases $Job.Case `
                    --config data/config.txt `
                    --solver-config $seedConfig `
                    --skip-cli-verification
                if ($LASTEXITCODE -ne 0) {
                    throw "Stage 2 failed: seed=$Seed arm=$($Arm.Name) task=$taskName exit=$LASTEXITCODE"
                }
            }
        }
    }
}
finally {
    Pop-Location
}

Write-Host "Stage 2 outputs: $OutputRoot"
Write-Host "Report command: $Python scripts/report_sa_stage2.py --run-root `"$OutputRoot`""
