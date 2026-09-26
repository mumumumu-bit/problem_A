# Final single-core metrics (C)

Base: `fullrun/stable-v1@34d0a42`. Tools branch: `analysis/final-metrics-v1`.
These tools do not run multiseed, VNS or SA. The existing solver, fullrun
configuration, runner and old `singlecore_baselines.py` remain unchanged.

## Tests and smoke (PowerShell, repository root)

```powershell
$pytestTmp = Join-Path $env:TEMP ('final_metrics_pytest_' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q --basetemp=$pytestTmp -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\singlecore_full100.py --cases case_001 --output results\final_metrics_smoke\singlecore
.\.venv\Scripts\python.exe scripts\p3_singlecore_l2.py --cases case_001 --output results\final_metrics_smoke\p3
```

Case 001 reference smoke: official singlecore = 233110 cycles; P2 N1 = 233110;
P3 N1 = 233110; L2 speedup = 1; cache hit rate = 0.

## Full runs, sequentially

```powershell
.\.venv\Scripts\python.exe scripts\singlecore_full100.py
# Continue only after successful completion of the first command.
.\.venv\Scripts\python.exe scripts\p3_singlecore_l2.py
```

Default cases are exactly `case_001` through `case_100`. Both commands read
`data/config.txt`; neither overwrites any old development results.

Outputs:

- `results/singlecore_full100/manifest.json` and `singlecore.csv`.
- `results/p3_singlecore_full100/manifest.json` and `p3_n1_l2.csv`.

Singlecore uses the same `OfficialEvaluator.singlecore()` path as the original
singlecore script. P3 N1 constructs the official `build_singlecore_plan()` once,
passes that same object to `OfficialEvaluator.raw()` with problem 2 and then 3,
and verifies that neither call mutated it. The CSV records its SHA-256.
P2 is the no-L2 control; P3 uses the official read-only cache settings.
The L2 speedup is the per-case P2/P3 makespan ratio, not a ratio between
independently optimized plans. N1 results are fixed-plan baselines, not optimized
single-core schedules.

## Resume and provenance

Rerun the exact same command after interruption. Completed valid CSV rows are
skipped; an interrupted case is recomputed. CSV replacement is atomic after each
completed case. Keep smoke and full outputs separate. Run only one process per
output directory.

Manifests fingerprint cases, graph files, hardware config, official source,
project source and metric tools. Changed inputs/tools/case lists are refused for
an existing output directory. Use a new directory for a changed experiment.
Malformed rows, duplicates and invalid numeric values also stop the run rather
than silently treating bad data as complete. Unknown old output directories
are never overwritten. `seconds` is wall time and is not expected to reproduce
bit for bit. Manifests record the producing Git commit and environment.

## Acceptance and archive

Each output must have 100 unique cases with the exact expected case set,
positive makespans and finite metrics. P3 speedup must equal no-L2/L2 and cache
hit rate must be in [0,1]. Keep the paired-plan hashes and manifests.

Commit only scripts/tests/this document on the tools branch. Archive full results
separately on `results/final-metrics`; do not add unrelated full100 jobs or zips.
The tools perform official in-process evaluation, not independent CLI rechecks.
