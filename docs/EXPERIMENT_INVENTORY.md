# 实验库存清单
## 生成时间: 2026-09-25
## 依据: 仅基于磁盘文件核验，不基于论文或记忆

---

| # | Run Name | Source Commit | Config | Cases | N | Problems | Cores | time_budget | max_evals | seed | Total Jobs | Done | CLI Verified | Directory |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | competition | 7980b88 | competition.yaml | 15 | 15 | 1,2 | 2,4 | 300 | 64 | 2026 | 60 | 60 | 0 | results/competition/ |
| 2 | competition_p3 | 7980b88 | competition.yaml | 15(声明) | 4(实测) | 3 | 2,4 | 300 | 64 | 2026 | 30 | 8 | 0 | results/competition_p3/ |
| 3 | development_v1 | 7980b88 | default.yaml | 6 | 6 | 1,2,3 | 2,4 | 120 | 36 | 2026 | 36 | 36 | 36 | results/development_v1/ |
| 4 | development_v2 | 7980b88 | default.yaml | 6 | 6 | 1,2,3 | 2,4 | 120 | 36 | 2026 | 36 | 36 | 36 | results/development_v2/ |
| 5 | A0_v2_baseline | 7980b88 | default.yaml | 6 | 6 | 1,2 | 2,4 | 120 | 36 | 2026 | 24 | 24 | 0 | results/development_v3/A0_v2_baseline/ |
| 6 | A1_adaptive | 7980b88 | default.yaml | 6 | 6 | 1,2 | 2,4 | 120 | 36 | 2026 | 24 | 24 | 0 | results/development_v3/A1_adaptive/ |
| 7 | A2_final | 7980b88 | default.yaml | 6 | 6 | 1,2 | 2,4 | 120 | 36 | 2026 | 24 | 24 | 0 | results/development_v3/A2_final/ |
| 8 | A2_final_p3 | 7980b88 | default.yaml | 6 | 6 | 3 | 2,4 | 120 | 36 | 2026 | 12 | 12 | 0 | results/development_v3/A2_final_p3/ |
| 9 | A2_final_verified | 7980b88 | default.yaml | 6 | 6 | 1,2 | 2,4 | 120 | 36 | 2026 | 24 | 24 | 24 | results/development_v3/A2_final_verified/ |
| 10 | A2_full15 | 7980b88 | default.yaml | 15 | 15 | 1,2 | 2,4 | 120 | 36 | 2026 | 60 | 60 | 0 | results/development_v3/A2_full15/ |
| 11 | pilot_v1 | 7980b88 | default.yaml | 2 | 2 | 1,2,3 | 2,4 | 120 | 36 | 2026 | 12 | 12 | 12 | results/pilot_v1/ |
| 12 | locality_probe | 7980b88 | default.yaml | 1 | 1 | 1,2,3 | 2,4 | 120 | 36 | 2026 | 6 | 6 | 6 | results/locality_probe/ |

## 15个开发case清单 (来自 configs/development_cases.yaml)
case_001, case_005, case_014, case_019, case_025, case_035, case_047, case_050, case_054, case_060, case_069, case_085, case_087, case_093, case_100

## 100 Case 覆盖情况总结
| Problem | N=2 | N=4 | 说明 |
|---|---|---|---|
| P1 | 15/100 | 15/100 | 仅15个代表case |
| P2 | 15/100 | 15/100 | 仅15个代表case |
| P3 | 4/100 | 4/100 | 仅 case_001,005,014,019 |

**结论: 100个全量case一个都没有跑过。所有实验都在最多15个代表case上。**

## competition_p3 完成详情
已完成(8组): case_001(N2,N4), case_005(N2,N4), case_014(N2,N4), case_019(N2,N4)
部分(2组，无job.json): case_025(N2,N4)
未开始(20组): case_035 至 case_100