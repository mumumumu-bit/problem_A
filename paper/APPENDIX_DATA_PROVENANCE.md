# 附录数据来源审计

仅从冻结Git对象恢复；未运行实验或Evaluator。当前分支保持 paper/draft-v1。

| 数据块 | N范围 | 来源branch/文件 | stage | 行数 | 备注 |
|---|---|---|---|---:|---|
| P1 N1 | 1 | `origin/results/singlecore-full100:results/singlecore_full100/singlecore.csv` | 固定单核baseline | 100 | 正式Scene A基准 |
| P1 N2~5 | 2~5 | `origin/results/full100-A/B/C:results/full100_teammate_A/B/C/case_XXX_pP_nN/job.json` | vns | 400 | problem=1 |
| P2 N1 | 1 | `origin/results/singlecore-full100:results/singlecore_full100/singlecore.csv` | 固定单核baseline | 100 | 共用P1基准；不是独立Scene B单核评测 |
| P2 N2~5 | 2~5 | `origin/results/full100-A/B/C:results/full100_teammate_A/B/C/case_XXX_pP_nN/job.json` | vns | 400 | problem=2 |
| P3 no-L2 N1 | 1 | `origin/results/singlecore-full100:results/p3_singlecore_full100/p3_n1_l2.csv` | 固定计划paired | 100 | no_l2_makespan / added_copy_no_l2 |
| P3 Cache N1 | 1 | `origin/results/singlecore-full100:results/p3_singlecore_full100/p3_n1_l2.csv` | 固定计划paired | 100 | l2_makespan / added_copy_l2 / cache_hit_rate |
| P3 no-L2 N2~5 | 2~5 | `origin/results/full100-A/B/C:results/full100_teammate_A/B/C/case_XXX_pP_nN/job.json` | vns | 400 | problem=2，分别求解 |
| P3 Cache N2~5 | 2~5 | `origin/results/full100-A/B/C:results/full100_teammate_A/B/C/case_XXX_pP_nN/job.json` | vns | 400 | problem=3，分别求解 |

## 冻结引用

- `origin/results/full100-A` → `572d0d27fc532e0f73a549842825529af169ddf7`
- `origin/results/full100-B` → `6813d4690b99cbc6c7447cfce84ef01fb9da502e`
- `origin/results/full100-C` → `fcd250ed58f4037ccb20d867a25dc1bea4404d13`
- `origin/results/singlecore-full100` → `430fa62b8c1f4c9b5465fd875605df66bf2cd7be`
- `origin/results/final-visualization` → `3e1555a1e9c2b1b36cde5901b843491a395918ac`
- `origin/results/full100-merged` → `cc892887ad80d9390d095a1c1b1d6bb317f7f1cf`

## 核验与字段映射

- A/B/C manifest分别覆盖33/33/34个不重叠case；1200个job，3600条阶段记录，仅选1200条vns。每个job的有效配置与manifest及stable config.py的StrategySelector规则一致：max_evaluations按small/medium/large/extra-large分别封顶64/40/26/20，其余配置一致。
- full100 manifest源码标识 `34d0a423fd99639e2d9c4630cb7979871273a8a7`，git_dirty=true；不声称是干净源码快照。
- Makespan取makespan，Added Copy取added_copy_bytes（字节），不是spill_bytes；命中率为[0,1]比例，保持原始精度。
- 单核CSV与final-visualization分支同路径对象字节一致。
- P3 N1：100个唯一case，100个合法plan_sha256，99个不同hash。配对依据已审计Evidence Map、归档docs/FINAL_METRICS.md、manifest和与manifest SHA-256一致的scripts/final_metrics.py：同一plan先评估problem=2后评估problem=3，并核验plan未被修改。单个hash不是两份独立plan归档，不将此检查表述为重新评估。
- P3 N2~5：同case同N匹配P2/P3最终VNS；分别求解，不是same-plan，不支持纯Cache因果消融。
- 已检查full100-merged/final-visualization正式目录；merged CSV可读性问题沿用Evidence Map，不使用其不可解析数据，不声称文件级一致。
- 未用旧6/15-case、development、SA或multiseed/baseline多核记录替代正式结果。

## 逐行追溯

多核每一行的源文件可由case_id、问题号与n_cores定位；case所属分片如下。

- A: case_001, case_002, case_003, case_004, case_005, case_006, case_007, case_008, case_009, case_010, case_011, case_012, case_013, case_014, case_015, case_016, case_017, case_018, case_019, case_020, case_021, case_022, case_023, case_024, case_025, case_026, case_027, case_028, case_029, case_030, case_031, case_032, case_033
- B: case_034, case_035, case_036, case_037, case_038, case_039, case_040, case_041, case_042, case_043, case_044, case_045, case_046, case_047, case_048, case_049, case_050, case_051, case_052, case_053, case_054, case_055, case_056, case_057, case_058, case_059, case_060, case_061, case_062, case_063, case_064, case_065, case_066
- C: case_067, case_068, case_069, case_070, case_071, case_072, case_073, case_074, case_075, case_076, case_077, case_078, case_079, case_080, case_081, case_082, case_083, case_084, case_085, case_086, case_087, case_088, case_089, case_090, case_091, case_092, case_093, case_094, case_095, case_096, case_097, case_098, case_099, case_100
