# 项目交接记录

更新时间：2026-09-24（Asia/Shanghai）

## Checkpoint

- 分支：`main`
- 本轮开始时的当前提交：`6dcc53eaa309ee1e34804dcd7e41d99aad9b875d`
- 本文件随本次 checkpoint commit 提交；最终 checkpoint hash 以 `git log -1 --oneline` 为准。
- 官方 `code/*.py`、`data/config.txt` 和 `data/case_*.json` 未修改。

## 已完成工作

- 建立 `src/npu_scheduler` 工程，包括 GraphData、方案类型、配置、coarsening、多初解、核分配、估计器、VNS、官方 evaluator 适配、持久缓存、实验记录和绘图。
- GraphData 已审计全部100例：原图规模766～38,666个操作，总计699,118个操作；审计结果见 `results/dataset_audit.csv`。没有进行100例算法优化。
- 完成四类初解：load-balanced、affinity-aware、critical-path-aware、pipe-aware，并支持多种粒度。
- 完成N1～N8八类邻域及top-K官方评估驱动的确定性变邻域下降。
- 最终选择目标为官方 `(makespan, added_copy_bytes)` 字典序；内存和Cache估计只用于诊断，默认权重均为0。
- 完成固定6例开发集（small 001/019、medium 005/050、large 025/085），问题1/2/3，N=2/4，共36组；每组保存Baseline、Multi-seed、VNS检查点。
- 36/36个最终方案通过官方CLI独立复核。结果、manifest、方案和逐候选日志位于 `results/development_v2/`。
- 已生成逐例报告、CSV、LaTeX表格以及300dpi PNG/矢量PDF图表。
- Windows已实测 editable 安装和从项目外目录调用；Linux尚未实测。
- 未实现或采用CP-SAT、SA、GA；第一轮没有证据支持加入这些模块。

## 当前最佳算法

开发集当前默认组合是 development_v2 的“四族多粒度初解 + HEFT/list-scheduling风格核分配 + top-K evaluator-guided VNS”。默认配置见 `configs/default.yaml`：seed=2026，软时间预算120秒，最多36次评估；大图由规模策略进一步限制评估次数。大于10,000个非COPY操作时不常规评估昂贵整图种子；四个种子族得到覆盖后，种子阶段若达到45%时间预算即转入VNS。

该组合只是在当前6例开发集上的默认最佳，不是逐例最优，也不是已冻结的竞赛方案。相对development_v1，development_v2在36组中16组改善、16组持平、4组回退，平均逐组Makespan改善4.45%。

## 测试状态

- 最近命令：`.\.venv\Scripts\python.exe -m pytest -q`
- 结果：`41 passed in 0.66s`（2026-09-24）。
- 覆盖输入和DAG、分区完整唯一、核顺序、方案序列化、确定性、缓存失效、三个官方评估器、N1～N8合法性，以及问题2/3全局等待环拒绝。

## development_v2 结果

- 范围：6例 × 3问题 × 2核数 = 36组，`benchmark.csv`共108行阶段指标。
- VNS相对Baseline平均逐组Makespan降低18.79%。
- VNS相对Multi-seed平均降低2.38%；25/36组严格改善。
- 官方评估调用943次，运行内缓存命中11次，不可执行候选0。
- 36/36最终方案通过官方CLI复核。
- 各任务求解时间相加1795.76秒，其中官方评估累计1704.81秒；单组最大128.11秒。120秒预算是调用间软截止。
- 相对独立官方单核的平均加速比：P1/N2=1.541、P1/N4=2.416、P2/N2=1.723、P2/N4=2.891。
- 同一P3方案下的L2平均加速比：N2=1.000072、N4=1.004360；Cache命中率不能直接视为同幅度Makespan收益。
- 完整逐例结果：`results/development_v2/REPORT.md`；原始指标：`benchmark.csv`；版本比较：`version_comparison.csv`；同方案L2对照：`l2_same_plan.csv`。

## 已知 regression

development_v2相对development_v1共有4组回退，全部集中在case_019：

| 场景 | v1 Makespan | v2 Makespan | v2变化 |
|---|---:|---:|---:|
| P1/N2 | 40,506 | 44,825 | +10.66% |
| P1/N4 | 26,739 | 27,204 | +1.74% |
| P2/N2 | 37,836 | 38,711 | +2.31% |
| P3/N2 | 37,836 | 38,711 | +2.31% |

后续改动必须保留case_019作为回归门槛。不要把v1/v2逐例最优拼接后宣称为单一算法成绩。v1运行期间还有单核与profile任务并发，跨版本墙钟时间不是严格受控比较。

## N1～N8统计

统计来自development_v2的逐候选记录；evaluated包含运行内缓存命中记录，不能当作独立样本。

| 邻域 | evaluated | improved | evaluator seconds |
|---|---:|---:|---:|
| N1 核移动 | 236 | 50 | 378.119 |
| N2 核间交换 | 128 | 23 | 198.328 |
| N3 独立块换序 | 78 | 0 | 136.404 |
| N4 相邻块合并 | 71 | 13 | 90.668 |
| N5 重块分裂 | 40 | 8 | 32.415 |
| N6 边界移动 | 18 | 2 | 1.260 |
| N7 强连接块联合放置 | 2 | 0 | 0.137 |
| N8 关键路径移动 | 13 | 0 | 2.733 |

N3消耗明显且本轮未产生改善，下一轮应先做预算缩减消融。N7/N8样本过少，不能据此判定无效。原始汇总见 `results/development_v2/neighborhood_diagnostics.json`。

## competition.yaml 状态

`configs/competition.yaml`尚未冻结，只是300秒、64次评估的研究预算预设。没有完成10～20例扩大开发集、N=3/5、完整A0～A4消融、Linux验证或100例正式实验，因此不得把它标为最终竞赛配置。

## 下一步任务

1. 先复现当前状态：安装editable包并运行41项测试；阅读 `docs/first_round_report.md`、本文件和development_v2报告。
2. 在不启动全100例的前提下，把固定开发集扩大到10～20例，并把case_019四个回退场景设为强制回归检查。
3. 做受控的邻域预算/顺序消融，优先验证减少N3预算是否改善质量—时间权衡；继续记录N7/N8样本，避免提前删除。
4. 对内存/Spill和Cache代理做独立消融，只有官方Makespan稳定改善才启用非零权重。
5. 配置冻结后再补N=3/5和100例正式实验；不要在冻结前运行完整100例优化。
6. 只有局部搜索在扩大开发集上仍稳定停滞时，才评估小窗口精确方法；当前不应直接加入GA。

队友接手后首先执行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

如需要在新环境重建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```
