# 6 实验设置与评价指标

本章说明正式测试覆盖、固定评测参数、求解配置及统一统计口径，不在此比较各问题的结果表现。

## 6.1 测试实例与硬件参数

正式多核实验覆盖100个测试case、3个问题场景（P1、P2、P3）及核数 $N\in\{2,3,4,5\}$，共 $100\times3\times4=1200$ 个job。每个job记录Baseline、Multi-seed和VNS三个阶段，合计3600条阶段记录。该覆盖数由正式归档manifest及job JSON核对，不以当前merged CSV作为逐行读取来源。

评测使用 `data/config.txt` 中固定的配置。容量与带宽按配置字段原义列示；除字段名或评测代码明确给出的情况外，不为数值补充未确认的单位。

| 评测场景/参数 | 配置值 | 字段含义及单位说明 |
|---|---:|---|
| L1容量 | 524288 | `[capacity]`项；配置字段未显式标注单位 |
| UB容量 | 131072 | `[capacity]`项；配置字段未显式标注单位 |
| DDR带宽 | 60 | `[bandwidth]`项；评测器结果字段标为 `bandwidth_bytes_per_cycle`，对应字节/周期 |
| Scene A跨核等待 | 1000 | `task_cross_core_wait_cycles`，周期 |
| Scene A同核等待 | 100 | `task_same_core_wait_cycles`，周期 |
| Scene B跨核COPY延迟 | 500 | `cross_core_copy_delay_cycles`，周期 |
| P3共享只读L2 Cache容量 | 1048576 | `cache_capacity_bytes`，字节 |
| P3共享只读L2 Cache带宽 | 250 | `cache_bandwidth_bytes_per_cycle`，字节/周期 |

上述均为官方评测/硬件配置，不是求解算法的搜索超参数。P1、P2、P3各自遵循对应官方Evaluator的执行语义；P3在Scene B基础上使用共享只读L2 Cache，其访问更新和替换遵循FIFO规则。

<!-- Evidence: data/config.txt；code/evaluation_validation.py；code/multicore_cut_evaluate_problem_1.py；code/multicore_cut_evaluate_problem_2.py；code/multicore_cut_evaluate_problem_3.py；paper/EVIDENCE_MAP.md A、D -->

## 6.2 正式求解配置

正式full100配置绑定到source commit `34d0a423`。为区分算法结构与实验运行条件，配置分组列于表3。这里的“算法结构参数”指控制候选生成、候选筛选或VNS搜索流程的配置；运行预算、随机种子及并行worker数归入实验运行参数。

**表3 正式实验与求解配置**

| 参数 | 取值 | 作用 | 类别 |
|---|---:|---|---|
| source commit | `34d0a423` | 标识正式full100配置绑定的源码版本 | 实验来源标识 |
| candidate pool | 48 | VNS单轮邻域候选池上限 | 算法结构参数 |
| Top-K | 3 | 每轮按启发式排序后送官方Evaluator的候选上限 | 算法结构参数 |
| max rounds | 32 | VNS最大轮数 | 算法结构参数 |
| grains | `[4,12,32]` | Multi-seed主粒度候选生成设置 | 算法结构参数 |
| fine-grain | 2 | 额外候选生成设置；不是独立搜索阶段，也没有独立消融 | 算法结构参数 |
| adaptive_budget | `true` | 启用adaptive邻域选择/预算停止机制；没有独立消融 | 算法结构参数 |
| 基础stagnation threshold | 8 | adaptive停滞判定的基础阈值 | 算法结构参数 |
| cache_weight | 0 | 候选估计器中的Cache相关权重；正式配置未启用该权重项 | 候选排序配置 |
| memory_weight | 0 | 候选估计器中的memory相关权重；正式配置未启用该权重项 | 候选排序配置 |
| seed | 2026 | 正式求解随机种子 | 实验运行参数 |
| time budget | 300秒 | 单个job的时间预算；这是上限，不表示每个job均耗满预算 | 实验运行参数 |
| max evaluations | 64 | 单个job允许的官方评价次数上限 | 实验运行参数 |
| workers | 2 | 并行worker数 | 实验运行参数 |

candidate pool与Top-K适用于VNS邻域候选筛选，不适用于Multi-seed阶段；seed候选在预算允许时逐个接受官方评价。fine-grain=2确实属于正式候选生成配置，但不能据此声称其具有独立性能贡献。adaptive已在正式配置中启用，但没有单独消融，且不能仅凭配置断定某一job实际由停滞条件触发停止。由于 `cache_weight=0`、`memory_weight=0`，不得将正式solver描述为启用了Cache-aware partition或memory-aware optimization。

<!-- Evidence: configs/fullrun_stable.yaml；A/B/C正式full100 manifest；paper/EVIDENCE_MAP.md C、D、H -->

## 6.3 单核基准与Speedup定义

单核基准来自 `results/singlecore_full100/singlecore.csv`，覆盖100个case。其评估由正式 `singlecore_evaluate.py` 为每个输入图构造单核plan（将全部非COPY操作放入一个子图并调度到core 0），再调用正式Scene A evaluator计算makespan；因此该基准是实际单核评测结果，不是由多核实验外推得到。

最终统计脚本对P1和P2均使用同一case对应的这份正式单核makespan作为参考基准。故P2的分母是统计口径共用的单核基准，不应称为另行生成的P2专属单核Scene B评测。

令 $T_{i,1}$ 为case $i$ 的正式单核基准makespan，$T_{i,N}$ 为同一case在问题场景及核数 $N$ 下VNS阶段的makespan，则逐case加速比定义为

$$
S_{i,N}=\frac{T_{i,1}}{T_{i,N}}.
$$

正式平均Speedup为100个逐case比值的算术平均：

$$
S_N=\frac{1}{M}\sum_{i=1}^{M}S_{i,N},\qquad M=100.
$$

因此，报告的平均加速比是“逐case比值的平均”，不是总单核makespan除以总多核makespan。N=1时按定义每个case的比值为1。

<!-- Evidence: code/singlecore_evaluate.py；results/singlecore_full100/singlecore.csv；scripts/final_visualization.py；paper/EVIDENCE_MAP.md F -->

## 6.4 P3共享L2 Cache比较口径

**N=1：逐case固定计划配对。** `results/p3_singlecore_full100/p3_n1_l2.csv`覆盖100个不同case且无重复、无缺失。根据正式配对记录，每个case的no-Cache评估与共享L2 Cache评估使用同一plan，paired-plan一致100/100、不一致0、缺失0；文件中的单个 `plan_sha256` 对应该case用于两种评估的固定计划。这里的“paired”是case内配对，不表示100个case共用同一个plan；文件中有99个不同plan hash，不同case使用不同plan是正常的。该文件记录的逐case `l2_speedup` 按 no-Cache makespan / 共享L2 Cache makespan 计算（已逐行核对），正式汇总使用该字段并对100个case求算术平均。

**N=2至5：正式VNS结果间比较，不是same-plan配对。** 每个case的no-Cache makespan取该核数下P2的VNS正式结果；共享L2 Cache makespan取对应P3的VNS正式结果。逐case比值为

$$
S^{\mathrm{P3/P2}}_{i,N}=\frac{T^{\mathrm{P2,VNS}}_{i,N}}{T^{\mathrm{P3,VNS}}_{i,N}},\qquad N\in\{2,3,4,5\},
$$

再对100个case求算术平均。P2 VNS与P3 VNS分别在各自问题场景下求解，证据不支持二者使用同一plan；因此此处是两组正式VNS结果的逐case对照，不能描述成只改变Cache且保持plan不变的控制实验。N=1使用文件中逐case固定plan的 `l2_speedup`；N=2至5按上述P2/P3 VNS结果比值统计。

<!-- Evidence: results/p3_singlecore_full100/p3_n1_l2.csv（只读核验：100行、100个case内plan hash一致）；scripts/final_visualization.py；paper/EVIDENCE_MAP.md G -->

## 6.5 评价指标

- **Makespan**：官方Evaluator返回的执行完成时间，是主要性能指标。
- **Added Copy**：官方Evaluator返回的新增COPY字节量，是正式候选比较字典序目标中的第二项；求解方案先比较Makespan，Makespan相同时再比较Added Copy。
- **Speedup**：按6.3节定义的逐case makespan 比值；均值按逐case比值的算术平均计算。
- **Cache Hit Rate**：P3官方Evaluator返回的Cache命中率，用于描述P3 Cache行为；它是分析指标，不是求解目标。
- **win / tie / loss**：用于Baseline→Multi-seed及Multi-seed→VNS阶段统计。对每个case分别比较相邻阶段的Makespan：后阶段严格更小记为win，完全相等记为tie，更大记为loss。该阶段计数不按Added Copy打破平局，也不使用百分比容差。

<!-- Evidence: src/npu_scheduler/types.py；src/npu_scheduler/search/vns.py；scripts/final_visualization.py；paper/EVIDENCE_MAP.md B、E、H -->

## 6.6 统计与结果复算原则

所有正式统计均基于冻结的full100实验归档，并按统一的case、问题、核数和阶段键关联。核心汇总由归档job结果独立统计，并与 `results/final_visualization/figure_numbers.md` 的正式统计核对一致；P1/P2加速比、P3 N=1配对统计及P3 N=2至5比较分别遵循本章对应口径。本文结果章节按这些固定口径报告，不从图像估读数据，也不将阶段快照解释为独立同预算求解器的因果对照。

<!-- Evidence: A/B/C正式manifest与归档job JSON；scripts/final_visualization.py；results/final_visualization/figure_numbers.md；paper/EVIDENCE_MAP.md“full100原始CSV与只读重建状态”、E、F、G、H。正式多核覆盖为1200 jobs/3600 stage records，来自manifest和job JSON的独立核对。 -->
