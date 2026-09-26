# 第三轮交接文档：问题3补齐 & 国赛冲刺

**目标**：国赛一等奖  
**状态**：P1/P2 已跑通15 case，P3 仅4/15 case，100 case全量未跑  
**交接日期**：2026-09-25

---

## 一、当前最大问题（论文写作前就应该做的）

### 1. 问题3 只跑了 4/15 case，缺 11 个

**已有（competition_p3）**：case_001, 005, 014, 019  
**缺失**：025, 035, 047, 050, 054, 060, 069, 085, 087, 093, 100

虽然 P3 代码完整（评估器、求解器、runner 全支持），但竞赛实验没跑完。论文里 P3 表格是空的——评委一眼就能看到。

### 2. 100 个全量 case 一个都没跑

目前所有实验都在 15 个代表 case 上。国赛一等奖通常要求全量 100 case 结果。配置 `configs/competition.yaml` 已经是竞赛预设（300s/64 evals），只需要跑。

### 3. 当前结果质量：不够国一水准

| 指标 | 当前值 | 国一预期 |
|---|---|---|
| P1 N4 加速比 | 2.48x | 3.0x+ |
| P2 N4 加速比 | 2.75x | 3.0x+ |
| 平均改善率 | 26.5% | 35%+ |
| VNS 有效比例 | 38/60 (63%) | 80%+ |
| Memory/Cache 建模 | 权重=0（未启用） | 已启用并验证 |
| 全局优化 | 无（纯局部 VNS） | SA/GA 至少一个 |

**问题本质**：当前 VNS 是纯局部下降——一旦 Multi-seed 陷入局部最优，VNS 完全无能为力（22/60 组 VNS 增益=0）。这对冲国一是不够的。

---

## 二、100 Case 三分方案

将 100 个 case 按文件大小（计算量）均匀分给三人，每人跑 P1/P2/P3。跑完后合并。

### 队友 A（小型case为主，跑得快）

```
case_001 case_002 case_003 case_004 case_005 case_006 case_007 case_008
case_009 case_010 case_011 case_012 case_013 case_014 case_015 case_016
case_017 case_018 case_019 case_020 case_021 case_022 case_023 case_024
case_025 case_026 case_027 case_028 case_029 case_030 case_031 case_032
case_033
```

命令：
```bash
cd /d/BAKFILE/9017530/huawei_cup_2026/problem_A

python scripts/run_all.py \
  --output results/full100_teammate_A \
  --problem 1 2 3 \
  --cases case_001 case_002 case_003 case_004 case_005 case_006 case_007 case_008 \
          case_009 case_010 case_011 case_012 case_013 case_014 case_015 case_016 \
          case_017 case_018 case_019 case_020 case_021 case_022 case_023 case_024 \
          case_025 case_026 case_027 case_028 case_029 case_030 case_031 case_032 \
          case_033 \
  --config data/config.txt \
  --workers 2 \
  --time-budget 300 \
  --max-evaluations 64 \
  --skip-cli-verification
```

### 队友 B（中等case）

```
case_034 case_035 case_036 case_037 case_038 case_039 case_040 case_041
case_042 case_043 case_044 case_045 case_046 case_047 case_048 case_049
case_050 case_051 case_052 case_053 case_054 case_055 case_056 case_057
case_058 case_059 case_060 case_061 case_062 case_063 case_064 case_065
case_066
```

命令：
```bash
cd /d/BAKFILE/9017530/huawei_cup_2026/problem_A

python scripts/run_all.py \
  --output results/full100_teammate_B \
  --problem 1 2 3 \
  --cases case_034 case_035 case_036 case_037 case_038 case_039 case_040 case_041 \
          case_042 case_043 case_044 case_045 case_046 case_047 case_048 case_049 \
          case_050 case_051 case_052 case_053 case_054 case_055 case_056 case_057 \
          case_058 case_059 case_060 case_061 case_062 case_063 case_064 case_065 \
          case_066 \
  --config data/config.txt \
  --workers 2 \
  --time-budget 300 \
  --max-evaluations 64 \
  --skip-cli-verification
```

### 队友 C（大型case为主，耗时最长）

```
case_067 case_068 case_069 case_070 case_071 case_072 case_073 case_074
case_075 case_076 case_077 case_078 case_079 case_080 case_081 case_082
case_083 case_084 case_085 case_086 case_087 case_088 case_089 case_090
case_091 case_092 case_093 case_094 case_095 case_096 case_097 case_098
case_099 case_100
```

命令：
```bash
cd /d/BAKFILE/9017530/huawei_cup_2026/problem_A

python scripts/run_all.py \
  --output results/full100_teammate_C \
  --problem 1 2 3 \
  --cases case_067 case_068 case_069 case_070 case_071 case_072 case_073 case_074 \
          case_075 case_076 case_077 case_078 case_079 case_080 case_081 case_082 \
          case_083 case_084 case_085 case_086 case_087 case_088 case_089 case_090 \
          case_091 case_092 case_093 case_094 case_095 case_096 case_097 case_098 \
          case_099 case_100 \
  --config data/config.txt \
  --workers 2 \
  --time-budget 300 \
  --max-evaluations 64 \
  --skip-cli-verification
```

### 合并结果

三人跑完后，把 `results/full100_teammate_A/`、`results/full100_teammate_B/`、`results/full100_teammate_C/` 三个目录合并到一个 `results/full100_merged/` 目录，然后运行：

```bash
python scripts/report_results.py --input results/full100_merged --output results/full100_merged
```

这会生成统一的 benchmark.csv、summary.csv、加速比表格和图表。

---

## 三、代码改进优先级（冲国一必须补）

### P0：必须做，否则不可能国一

| # | 改进项 | 原因 | 实现难度 |
|---|---|---|---|
| 1 | **P3 全量实验** | 论文表格不能空 | 只需跑（代码已就绪） |
| 2 | **100 case 全量实验** | 国一标配 | 只需跑（三分方案见上） |
| 3 | **VNS 加入模拟退火接受准则** | 22/60 组卡在局部最优，核心瓶颈 | 中（改动 `src/npu_scheduler/search/vns.py`） |

### P1：显著提升竞争力

| # | 改进项 | 原因 | 实现难度 |
|---|---|---|---|
| 4 | **启用 Cache 感知切分** | P3 的核心区分点就是 Cache 命中率优化 | 中高（coarsening 阶段纳入 cache locality） |
| 5 | **启用 Memory 硬约束** | 当前 `memory_weight=0`，评分完全不考虑内存 | 中（估计器已有，加约束逻辑） |
| 6 | **Multi-seed 多样性增强** | 当前 4 种初解不够多样，导致 M 过早收敛 | 低（加扰动/随机排序变体） |

### P2：锦上添花

| # | 改进项 | 说明 |
|---|---|---|
| 7 | 核间通信估计精度提升 | 当前按 tensor×consumer 统计，改按 producer-core→consumer-core 对去重 |
| 8 | Coarsening 粒度自适应 | 当前固定 3 种粒度，改根据图深度/宽度自适应 |
| 9 | Pipe 负载均衡惩罚项 | P2/P3 场景 Pipe 不均衡导致 stall |
| 10 | 消融实验完整化 | 证明每个模块的独立贡献 |

---

## 四、P0 改进 #3 实现指引：VNS → SA-VNS

当前 `src/npu_scheduler/search/vns.py` 是纯变邻域下降（只接受严格改进）。
需要加入模拟退火：以概率 `exp(-Δ/T)` 接受劣解，温度 T 从 `T0` 指数衰减。

改动要点：
1. 在 `SolverConfig` (`src/npu_scheduler/config.py`) 加 3 个参数：
   ```python
   sa_enabled: bool = True
   sa_initial_temp: float = 100.0
   sa_cooling_rate: float = 0.95
   ```
2. 在 VNS 主循环中，当邻域产生劣解时，以 `random.random() < exp(-delta_makespan / temperature)` 接受
3. 每轮 `temperature *= sa_cooling_rate`
4. 全局最优解始终保留（best-so-far），不受 SA 影响

---

## 五、合并后分析脚本

队友跑完后，我需要一个脚本来自动分析全量结果。使用 `scripts/report_results.py`：

```bash
python scripts/report_results.py --input results/full100_merged --output results/full100_merged
```

这会生成：
- `benchmark.csv`：全量 benchmark 表
- `summary.csv`：按 problem/cores/algorithm 汇总
- `singlecore_speedup_summary.csv`：加速比汇总
- `benchmark_table.tex`：LaTeX 表格
- `figures/`：加速比分布图、改善率箱线图、消融图等

---

## 六、论文提醒

1. **问题3 的表格之前是空的**，跑完后用 `benchmark_table.tex` 填入
2. **加速比数字**：单核基准来自 `singlecore_evaluate.py` 的 Scene A 评估（对 P2/P3 也是同一个基准，因为单核无跨核通信）
3. **Cache 命中率**：P3 结果里有 `cache_stats.hit_rate` 字段，论文里要体现
4. **消融实验**：建议在 6 个开发 case 上做（Baseline vs Multi-seed vs VNS vs SA-VNS），章节放在"算法分析与消融实验"

---

## 七、紧急联系人

- 代码问题：看 `src/npu_scheduler/` 下的 config.py、vns.py、estimator.py
- 评估问题：看 `code/multicore_cut_evaluate_problem_3.py` 的 docstring
- 跑崩了：删掉对应 case 的 job 目录重跑（runner 会自动跳过已完成的 job.json）

---
*此文档在 AI 辅助下生成。目标：国赛一等奖。*