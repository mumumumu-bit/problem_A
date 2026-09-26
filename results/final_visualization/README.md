# Problem A 最终可视化 — 数据来源

## 代码基线
- fullrun stable commit: `34d0a42`
- 可视化脚本: `scripts/fig1_p1_speedup.py` ~ `scripts/fig6_stage_ablation.py`, `scripts/final_visualization.py`

## 结果 commit
- full100 A result: branch `results/full100-A`
- full100 B result: branch `results/full100-B`  
- full100 C result: branch `results/full100-C`
- full100 merged: branch `results/full100-merged`
- singlecore + P3 N1: branch `results/singlecore-full100`

## 数据文件
- `results/full100_merged/detail.csv` — 3600 rows (1200 jobs × 3 algorithms)
- `results/singlecore_full100/singlecore.csv` — 100 cases
- `results/p3_singlecore_full100/p3_n1_l2.csv` — 100 cases

## 覆盖率
- `check_full100_coverage.py`: 1200 / 1200 jobs

## 合并时间
- 2026-09-26

## 可视化脚本 commit
- `fullrun/stable-v1` @ 34d0a42