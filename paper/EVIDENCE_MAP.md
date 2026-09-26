# 论文证据地图 Evidence Map

本文件只建立“论文内容/结论—仓库证据”的对应关系，不写论文正文，不阅读参考论文。证据优先级为：当前正式结果与生成脚本 > 正式配置与正式源码 > 最新交接文档 > 旧交接文档。

## 证据等级

- **A**：官方赛题/正式源码/正式配置/当前正式结果直接支持。
- **B**：当前正式结果的汇总Markdown、最终统计文件或生成脚本支持，但原始结果尚未完成独立复核。
- **C**：交接文档或分析推断支持，正文只能谨慎表述。
- **D**：证据不足，不得进入正式正文。
- 任何无法由官方题目、正式源码、正式配置或正式结果确认的信息标记为 **[TBD-VERIFY]**。

## 当前总风险

`results/final_visualization/README.md` 和 `figure_numbers.md`把当前数据标记为 full100；旧版 `HANDOFF_ROUND4.md` 的“100个全量case一个都没跑”属于更早阶段记录，不作为当前正式结果。当前 `results/full100_merged/detail.csv`、`summary.csv`及最终表格CSV在字节层均不是可解析CSV：首字节序列相同，UTF-8 解码失败，换用常见编码、delimiter、quoting、BOM和换行方式也不能得到表头/行结构；未修改这些正式文件。只读读取 A/B/C 正式归档分支的 manifest 与 job JSON 后，已独立重建 1200 jobs、3600 stage rows，并与 `figure_numbers.md` 的核心统计一致。因此：full100 结果数值的归档证据已闭环，但正式 CSV 文件本身的可读性仍是独立的 [TBD-VERIFY]，不应声称已由该 CSV 逐行解析复核。

### full100 原始 CSV 与只读重建状态

- `detail.csv`：文件存在，但不是可解析文本 CSV；不能可靠给出其列名、problem/N/stage 分布或逐行 case 统计。
- `summary.csv` 与 `results/final_visualization/tables/*.csv`：同样存在相同的二进制字节头，不能按 CSV 读取；禁止通过改写文件来“修复”。
- 正式归档证据：`origin/results/full100-A/B/C` 的 manifest 分别覆盖 33/33/34 个不重叠 case，合计 100 case；job JSON 合计 1200 个，每个 job 含 baseline、multiseed、vns 三行，合计 3600 行。
- 独立复算：从上述 job JSON 只读重建的 P1/P2 speedup、P3 N=2~5 L2 对比和全部阶段统计与 `figure_numbers.md` 一致；因此核心数值可按“归档 job JSON + manifest + 统计脚本”作为 A 级结果证据，但“原始 merged CSV 可解析性”仍单独保留 TBD。

## A. 赛题与场景定义

| 论文内容/结论 | 真实证据来源 | 已确认事实 | 可否进入正文 | 风险/限制 |
|---|---|---|---|---|
| 原始计算图 | `data/case_001.json`至`case_100.json`；`src/npu_scheduler/graph.py`；`code/evaluation_validation.py` | 图由ops、tensors、edges组成；求解器图视图排除COPY_IN/COPY_OUT，再将其作为边界机制交给官方评估器。 | 是，A | 具体某个case的规模应引用对应数据文件，不引用旧论文数字。 |
| P1 / Scene A | `code/multicore_cut_evaluate_problem_1.py` | 每个子图封装为独立Task；Task边界插入DDR COPY；跨Task依赖使用跨核等待；官方返回makespan和数据搬运。 | 是，A | 不应把P1描述成“仅核内调度”或忽略边界COPY。 |
| P2 / Scene B | `code/multicore_cut_evaluate_problem_2.py` | 每核合并为一个Task；同核tensor片上直接通信；跨核边插入COPY_OUT/COPY_IN；跨核COPY等待来自`data/config.txt`。 | 是，A | 具体COPY字节数必须来自正式结果。 |
| P3相对P2的增加 | `code/multicore_cut_evaluate_problem_3.py`；`docs/多核并行模拟执行算法.md` | P3在Scene B执行模型上增加只读 FIFO Cache；只有COPY_IN可查询Cache；命中使用Cache带宽，未命中从DDR读取；命中不会改变FIFO顺序。 | 是，A | “FIFO Cache”和代码中的`read_only` Cache是实现/正式说明中的名称；“共享只读L2”或“readonly L2”是论文/团队概括性称呼，不应写成官方原词或额外硬件断言。 |
| 私有L1/UB与DDR | `data/config.txt`；`code/evaluation_validation.py` | `[capacity]`明确要求L1、UB；当前值为L1=524288、UB=131072；图数据中的tensor位置允许DDR/L1/UB。 | 是，A | “私有”若非官方题面原词，需用“每Task/每核评估中的容量配置”谨慎表述。 |
| P3 Cache容量/带宽 | `data/config.txt`；`code/multicore_cut_evaluate_problem_3.py` | Cache容量=1048576 bytes；Cache带宽=250 bytes/cycle。 | 是，A | 当前文件未给出独立“L2”字段，正文应说明这是P3只读Cache参数。 |
| COPY机制 | 三个官方评估器；`src/npu_scheduler/evaluator/official_adapter.py` | 方案转换为官方plan后由官方评估器计算makespan、added_copy_bytes、spill_bytes、cache_hit_rate。 | 是，A | 不能以solver估计器替代官方评估结果。 |
| Task组织 | P1/P2/P3官方评估器中的`_build_*_tasks` | P1按子图封装Task；P2/P3按核组织Task并补跨核COPY。 | 是，A | 需要在正文区分“子图Task”和“每核Task”。 |

## B. 数学目标和评价指标

| 论文内容/结论 | 真实证据来源 | 已确认事实 | 可否进入正文 | 风险/限制 |
|---|---|---|---|---|
| Makespan | `src/npu_scheduler/types.py`；官方评估器返回值 | `Evaluation.makespan`为官方执行模拟返回的makespan；P1/P2/P3官方函数均以完成时间作为核心结果。 | 是，A | 不要自行把makespan改写成加权目标。 |
| Added Copy | `src/npu_scheduler/evaluator/official_adapter.py`；官方评估器结果字段 | `added_copy_bytes`取自官方返回的`data_movement_bytes.added_copy_bytes`。 | 是，A | `spill_bytes`是单独字段，不能与Added Copy混写。 |
| Cache Hit Rate | P3官方评估器；`results/p3_singlecore_full100/p3_n1_l2.csv`；归档 job JSON | P3返回`cache_stats.hit_rate`，正式结果字段名为`cache_hit_rate`；N=2~5的归档 job JSON 可独立复算均值。 | 是，A | merged detail.csv本身仍不可解析，但这不影响基于正式归档 job JSON 的独立核对。 |
| Solver comparison | `src/npu_scheduler/types.py`、`src/npu_scheduler/search/vns.py` | 有效解比较为字典序`(makespan, added_copy_bytes)`；先比较makespan，再比较Added Copy。 | 是，A | 这是解比较逻辑，不等同于人为构造的加权目标函数。 |
| 正式objective | `src/npu_scheduler/types.py`；`official_adapter.py` | 正式解接受条件为官方Evaluation有效且`result.objective < value.objective`。 | 是，A | 不得自行写成`a*makespan+b*copy`。 |
| 是否为主次/字典序 | 上述源码 | 是字典序：`(makespan, added_copy_bytes)`；非加权和。 | 是，A | 需保持“Makespan优先，Added Copy次序决胜”的准确表述。 |

## C. 正式算法

| 论文内容/结论 | 真实证据来源 | 已确认事实 | 可否进入正文 | 风险/限制 |
|---|---|---|---|---|
| 正式流水线 | `src/npu_scheduler/search/vns.py`；`initial_partition.py`；`coarsening.py`；`core_assignment.py`；`official_adapter.py` | 生成种子/初解 → 估计器排序候选 → 官方Evaluator评价 → 对VNS候选进行阶段搜索；结果采用官方评估器。 | 是，A | 正文需以实际启用配置描述，不把历史SA方案写入。 |
| Baseline | `initial_partition.py` | baseline为中间grain的balanced粗化后HEFT风格核分配。 | 是，A | baseline是阶段基线，不是独立完整算法对决。 |
| Multi-seed | `initial_partition.py`；`vns.py` | 代码含balanced、affinity、critical、pipe四个主要族；另有whole图和fine-grain变体；由portfolio_size截断。 | 是，A | “4族×3 grain”是概括，实际还存在whole与fine-grain变体；不要只写成恰好12个候选。 |
| seed family数量 | `initial_partition.py` | 主要族为balanced、affinity、critical、pipe；baseline单独先评估；whole为结构性兜底/候选。 | 是，A | 具体每次实际评估数量受portfolio_size、时间预算、图规模和去重影响。 |
| grains / fine-grain | `coarsening.py`；A/B/C full100 manifest；full100 job JSON | 正式配置为`grains=[4,12,32]`且`fine_grain=2`；job JSON 中可见 `balanced-2`、`affinity-2`、`critical-2`、`pipe-2` 等来源，说明 fine-grain=2 确实进入 full100 的 Multi-seed 候选生成并可能被选择。 | 是，A | 它是启用的候选变体，不是独立的第四阶段或独立收益消融；不得据此声称 fine-grain=2 的单独效果。 |
| 图粗化 | `src/npu_scheduler/partition/coarsening.py` | 按balanced/critical/locality顺序形成atomic units，再按工作预算聚合成blocks；保证DAG商图约束。 | 是，A | 不得称为任意图收缩或保证全局最优。 |
| 核分配 | `src/npu_scheduler/schedule/core_assignment.py` | ready-list/HEFT风格排序；估计最早完成，affinity和pipe balance影响候选评分。 | 是，A | 这是启发式分配，不是精确优化器。 |
| candidate ranking | `src/npu_scheduler/search/vns.py`；`estimator.py` | 候选按估计器score及digest排序，取前`top_k`送官方Evaluator；估计器是排序信号，不替代官方分数。 | 是，A | 正式正文不要把估计score当makespan。 |
| candidate pool / top-K | `configs/fullrun_stable.yaml`；A/B/C full100 manifest；`vns.py` | full100实际配置为candidate_pool=48、top_k=3；代码先生成候选、去重、排序，再评估前3个。 | 是，A | 仍需区分候选池大小与实际因去重/预算而完成的评价次数。 |
| VNS邻域数量 | `src/npu_scheduler/search/local_search.py` | N1 Move、N2 Swap、N3 adjacent independent reorder、N4 adjacent merge、N5 Split、N6 shift boundary、N7 connected pair placement、N8 critical move，共8种。 | 是，A | 不得把N8描述为全局跳出。 |
| VNS接受准则 | `src/npu_scheduler/search/vns.py` | 仅当官方Evaluation objective严格改善时接受；保持单调incumbent。 | 是，A | 这是strict descent，不是模拟退火。 |
| global best | `vns.py`中的`incumbent/value/snapshots` | 当前incumbent保存截至当前评估的最好有效解；`snapshots`记录baseline/multiseed/vns阶段。 | 是，A | “global best”只能指搜索过程中best-so-far，不是全局最优证明。 |
| early stopping / adaptive | `vns.py`；A/B/C full100 manifest；`configs/fullrun_stable.yaml` | full100实际配置开启`adaptive_budget=true`，`min_neighbourhood_trials=3`、`stagnation_patience=8`；代码在停滞达到阈值或预算限制时可提前停止。 | 是，A | 正文只能说“配置开启并允许自适应提前停止”，不能把每个 job 的实际停止原因都推定为停滞。 |
| cache/memory heuristic | `estimator.py`；`config.py` | `memory_weight=0.0`、`cache_weight=0.0`；相关估计代码存在，但正式配置未启用奖励/惩罚。 | 是，A | 不得声称solver已启用Cache感知切分或Memory硬约束。 |
| 历史探索机制 | `experiment/sa-vns-v1/analysis/sa_experiments_summary.md`；SA分支代码/配置；full100 manifest | SA-VNS 确有真实实现，并做过 Stage 1 pilot、Stage 2 multi-seed 和 8任务 expansion；实验总结结论是收益局部且有 Added Copy 代价，因此未并入 stable solver，也未进入 full100。 | 是，A/C | 不得写“SA未实现”；应写“已进行探索性实现/实验，但未采用为最终稳定求解器”。 |

## D. 正式实验配置

| 参数/覆盖 | 真实证据来源 | 当前记录 | 可否进入正文 | 风险/限制 |
|---|---|---|---|---|
| hardware config | `data/config.txt` | seed不在此文件；L1=524288，UB=131072，bandwidth=60，Scene A跨核等待=1000、同核等待=100，Scene B跨核COPY delay=500，P3 Cache=1048576、Cache bandwidth=250。 | 是，A | 这些是官方评估参数，不是solver搜索参数。 |
| solver seed | A/B/C full100 manifest；`configs/fullrun_stable.yaml` | full100实际 seed=2026。 | 是，A | 三份 manifest 的 `git_dirty=true`，因此 commit 是来源标识，不等于运行时工作树完全干净。 |
| source commit | A/B/C full100 manifest；`results/final_visualization/README.md` | 三份正式 full100 manifest 均记录 `34d0a423fd99639e2d9c4630cb7979871273a8a7`（短哈希 `34d0a42`）。 | 是，A | manifest同时记录 `git_dirty=true`；正文不应把 dirty 状态省略。 |
| time budget | A/B/C full100 manifest；`scripts/run_full100_A.ps1/B.ps1/C.ps1` | 300 seconds。 | 是，A | 是正式配置值，不代表每个 job 实际耗满300秒。 |
| max evaluations | A/B/C full100 manifest；`configs/fullrun_stable.yaml` | 64。 | 是，A | 是上限；实际 evaluations 由结果记录决定。 |
| candidate pool / top-k | A/B/C full100 manifest；`configs/fullrun_stable.yaml` | 48 / 3。 | 是，A | 候选池和 top-K 是配置上限，不等价于所有候选都完成官方评价。 |
| max rounds | A/B/C full100 manifest；`configs/fullrun_stable.yaml` | 32。 | 是，A | 是VNS轮数上限。 |
| grains / fine-grain | A/B/C full100 manifest；`configs/fullrun_stable.yaml` | `grains=[4,12,32]`；`fine_grain=2`。 | 是，A | fine-grain=2 是正式 Multi-seed 候选变体，不是独立阶段。 |
| workers | A/B/C full100 manifest；运行脚本 | 2。 | 是，A | workers影响并行执行，不改变目标定义。 |
| adaptive / early stopping | A/B/C full100 manifest；`vns.py` | `adaptive_budget=true`；`min_neighbourhood_trials=3`；`stagnation_patience=8`。 | 是，A | 可确认正式开启；不能从配置推断每个 job 的实际停止原因。 |
| cache/memory weight | A/B/C full100 manifest；`configs/fullrun_stable.yaml` | `cache_weight=0.0`、`memory_weight=0.0`。 | 是，A | P3官方 Cache 仍由官方评估器执行；这两项为solver候选排序启发式权重。 |
| cases | A/B/C full100 manifest；singlecore/P3 manifest | case_001至case_100，共100个；A/B/C分片不重叠且合并覆盖完整。 | 是，A | merged detail.csv不可解析，但case覆盖由正式 manifest 直接支持。 |
| N覆盖 | A/B/C full100 manifest；`figure_numbers.md`、最终图脚本 | 多核full100覆盖P1/P2/P3的N=2、3、4、5；单核基准补N=1。 | 是，A | N=1不是merged多核job，而是独立singlecore/P3 N1正式文件。 |
| full100总job数 | A/B/C full100 manifest与job JSON | 33+33+34=100个不重叠case；每个case覆盖3 problems×4 multicore N(2/3/4/5)，合计1200 jobs；每job含baseline/multiseed/vns三行，合计3600 rows。 | 是，A | 该结论来自只读归档 job JSON/manifest；merged detail.csv本身仍不可解析。 |
| full100配置绑定 | A/B/C full100 manifest；正式运行脚本；stable config | seed、预算、候选池、top-K、轮数、grains、workers、adaptive、fine-grain、cache/memory权重均由三份 manifest 直接记录并一致。 | 是，A | manifest的 `git_dirty=true` 是当前正式 provenance 风险，应保留记录。 |

## E. 正式结果证据

### E1. 当前可引用的统计数字

以下数字来自`results/final_visualization/figure_numbers.md`，统计口径由`scripts/final_visualization.py`和各最终绘图脚本明确。merged CSV无法按文本解析，但已从 A/B/C 正式归档分支的 job JSON 独立重建并逐项复算核心数字；因此结果数值的归档证据为A，CSV文件可读性仍单独列为TBD。

| 结果 | 正式数字 | 真实来源 | 证据等级 | 可否进入正文 |
|---|---:|---|---|---|
| P1 N=1/2/3/4/5平均speedup | 1.0000 / 1.7890 / 2.4163 / 2.9514 / 3.3877 | `figure_numbers.md`；`scripts/final_visualization.py`；singlecore.csv + A/B/C job JSON | A | 可进入；说明为逐case speedup 的均值 |
| P2 N=1/2/3/4/5平均speedup | 1.0000 / 1.9004 / 2.6663 / 3.2978 / 3.8369 | `figure_numbers.md`；`scripts/final_visualization.py`；singlecore.csv + A/B/C job JSON | A | 可进入；说明为逐case speedup 的均值 |
| P3 N=1 L2对比 | no-L2=3124794，L2=3116693，speedup=1.0086，hit=0.092 | `figure_numbers.md`；`p3_singlecore_full100/p3_n1_l2.csv` | A | 100行原始CSV可解析，并完成逐case核验 |
| P3 N=2/3/4/5 L2 speedup | 1.0068 / 1.0136 / 1.0152 / 1.0259 | `figure_numbers.md`；`scripts/final_visualization.py`；A/B/C job JSON | A | N=2~5以P2 vns/P3 vns逐case配对后求均值 |
| P3 N=2/3/4/5平均hit rate | 0.1606 / 0.2412 / 0.2467 / 0.2973 | `figure_numbers.md`；A/B/C job JSON | A | 来自P3 vns记录的`cache_hit_rate` |
| Baseline→Multi-seed | P1 N2/N3/N4/N5=0.0730/0.1285/0.1573/0.1821；P2=0.0435/0.0929/0.1213/0.1635；P3=0.0450/0.0887/0.1273/0.1684 | `figure_numbers.md`；`fig6_stage_ablation.py`；A/B/C job JSON | A | 可作为阶段性比较，不能声称单变量因果 |
| Multi-seed→VNS | P1=0.0179/0.0292/0.0386/0.0244；P2=0.0056/0.0153/0.0209/0.0308；P3=0.0038/0.0144/0.0097/0.0367（N2→N5） | `figure_numbers.md`；`fig6_stage_ablation.py`；A/B/C job JSON | A | 可作为阶段性比较，不能声称全局优化 |

### E2. 结果口径

- P1/P2 speedup：`singlecore.csv`中同一case的makespan ÷ `detail.csv`中同一case、problem、N、algorithm=vns的makespan，然后对100个case逐例speedup求均值；不是先求总和再相除。
- P3 N=1：来自`p3_singlecore_full100/p3_n1_l2.csv`逐case的no-L2/L2；N=2~5：脚本以P2 vns的makespan作为no-L2，以P3 vns的makespan作为L2，再逐case计算P2/P3，最后求均值。
- 消融图将同一full100 detail中的baseline、multiseed、vns分阶段比较；因为三者是嵌套阶段快照，不能写成三个独立、同预算求解器的严格因果对照。
- Added Copy和Cache Hit Rate必须保留其字段含义，不能由speedup或图像反推。

## F. singlecore证据

| 论文内容/结论 | 证据 | 已确认事实 | 可否进入正文 | 风险/限制 |
|---|---|---|---|---|
| 单核覆盖 | `results/singlecore_full100/singlecore.csv`；manifest | CSV可解析，100行，字段为case、makespan、added_copy_bytes、seconds；case范围由manifest为001-100。 | 是，A | 仍需检查CSV无重复case；当前已确认行数和字段。 |
| 单核基准生成 | `code/singlecore_evaluate.py`；singlecore manifest | 将全部非COPY操作合并为一个子图并调度到core 0，调用官方Scene A评估器；hardware来自`data/config.txt`。 | 是，A | 不是把多核结果中的N=1行当作单核基准。 |
| P1/P2共用单核基准 | `scripts/final_visualization.py` | P1、P2均使用同一个singlecore.csv的case makespan作为分母。 | 是，A | 单核函数本身基于Scene A；对P2的使用是统计口径约定，正文应避免称为“P2单独生成的单核仿真”。 |
| 正式平均speedup | `scripts/final_visualization.py` | 先逐case计算`singlecore_makespan / multicore_makespan`，再对100个case取mean。 | 是，A | 禁止使用`sum(singlecore)/sum(multicore)`作为正式平均speedup。 |

## G. P3 N=1与N=2~5证据

| 核验项 | 证据 | 已确认事实 | 可否进入正文 | 风险/限制 |
|---|---|---|---|---|
| P3 N=1覆盖 | `results/p3_singlecore_full100/p3_n1_l2.csv`；manifest | CSV可解析，100行；字段包含no_l2_makespan、l2_makespan、l2_speedup、cache_hit_rate及两个Added Copy字段。 | 是，A | 配置绑定由P3 manifest及正式运行记录支持。 |
| N=1 no-L2/L2 | `results/p3_singlecore_full100/p3_n1_l2.csv`；`docs/FINAL_METRICS.md`；正式工具逻辑 | 总case数100；paired-plan一致100；不一致0；缺失0。每个case的一条`plan_sha256`代表同一计划用于no-L2与readonly-L2两次评估；全表99个不同hash是不同case计划不同，并非错误。 | 是，A | 不得要求100个case共用一个全局plan；应写“逐case固定计划的paired comparison”。 |
| N=2~5 no-L2来源 | `scripts/final_visualization.py`；A/B/C job JSON | 取`(case, problem=2, cores=N, algorithm=vns)`，并已独立复算。 | 是，A | detail.csv自身仍不可解析，但归档 job JSON 可核对。 |
| N=2~5 readonly-L2来源 | `scripts/final_visualization.py`；A/B/C job JSON；P3官方评估器 | 取`(case, problem=3, cores=N, algorithm=vns)`；P3使用正式 `read_only` FIFO Cache，并已独立复算。 | 是，A | 论文若写“L2”，需注明是概括性简称。 |
| L2 speedup | 最终脚本；A/B/C job JSON | 逐case使用P2 vns makespan / P3 vns makespan，再对100 case求均值。 | 是，A | 不得把P3与P2的算法差异误写成只改变Cache而其他求解完全相同。 |

## H. 算法消融边界

| 内容 | 证据状态 | 可写结论 | 不可写结论 |
|---|---|---|---|
| Baseline→Multi-seed | 当前最终阶段统计文件/脚本，B | Multi-seed阶段相对baseline阶段的平均makespan下降及win/tie/loss。 | 不可声称Multi-seed单独的因果贡献，除非确认预算、候选集和其他条件。 |
| Multi-seed→VNS | 当前最终阶段统计文件/脚本，B | VNS阶段在Multi-seed快照基础上的增量改善。 | 不可声称VNS达到全局最优或一定改善所有case。 |
| Multi-seed整体贡献 | full100阶段对照，B | 可作为阶段性经验结果。 | 不可拆分为各seed family的独立贡献；没有单family full100消融。 |
| VNS整体贡献 | 8邻域源码+阶段统计，A/B | 可说明VNS按strict descent在若干case进一步改善。 | 不可声称SA式跳出局部最优或全局优化。 |
| grains/fine-grain | 源码、A/B/C manifest、job JSON，A | full100启用`grains=[4,12,32]`与`fine_grain=2`，后者实际出现在候选来源中。 | 没有独立逐grain full100消融，不能写每个grain的独立收益。 |
| adaptive | `vns.py`和A/B/C full100 manifest，A | full100实际开启`adaptive_budget=true`，并记录停滞参数。 | 不能据配置推断每个job的实际停止原因。 |
| cache/memory heuristic | `estimator.py`、`config.py`，A | 正式权重为0，不能声称求解器利用Cache/Memory启发式优化。 | 不可把P3官方Cache效果等同于solver Cache-aware partitioning。 |
| same-plan L2 | P3 N1 CSV、`docs/FINAL_METRICS.md`及工具逻辑，A | 100个case均为case内固定计划的no-L2/readonly-L2配对比较；不同case之间计划不同是正常的。 | 不可写成100 case共享一个固定plan。 |

### 证据类别

- **正式full100证据**：A/B/C正式 manifest、job JSON、`figure_numbers.md`及其生成脚本、singlecore/P3 N1 100-case文件；核心数值已独立重建并完成A级闭环。merged detail/summary CSV的文件可读性仍是独立风险。
- **开发集证据**：`results/development_v1`、`development_v2`、`development_v3`及其REPORT/benchmark；只能支持开发集描述。
- **探索性证据**：SA分支的 pilot/expansion 结果、旧交接文档中关于Cache感知切分、Memory硬约束、目标阈值等计划或探索描述。
- **无充分证据**：任何单独seed family收益、单独grain收益、SA进入正式full100的收益、全局最优、P1/P2/P3统一单核plan、merged CSV自身的逐行解析结论。

## I. SA最终定位

`experiment/sa-vns-v1` 分支包含真实的 bounded SA-VNS 实现，并有 Stage 1 pilot、Stage 2 multi-seed 与 8任务 expansion；其总结记录了 `case_005 P1 N4` 的局部改善、Added Copy代价及 expansion 全部tie。最终工程决策是保留 strict-descent VNS，SA分支未合并到 stable solver，也未进入 full100。结论：**SA属于已进行的探索性实现/实验，但没有进入当前stable solver或full100正式结果，不得进入最终主算法描述或冒充正式full100算法。**如需提及，应明确写成“探索后未采用”，不能写“SA未实现”。

## J. 最终8张图证据定位

| 图 | 图名/文件 | 数据来源与统计口径 | 支持结论 | 正文/附录 | 解释边界 |
|---|---|---|---|---|---|
| 1 | `fig1_p1_speedup` | singlecore.csv与A/B/C job JSON；P1 vns；逐case单核/多核后取100-case均值，误差棒为标准差 | P1随N变化的平均speedup | 正文候选 | 不等于线性扩展保证；merged detail.csv本身不可解析。 |
| 2 | `fig2_p2_speedup` | 同上，problem=2 | P2随N变化的平均speedup | 正文候选 | 同上。 |
| 3 | `fig3_p1p2_combined` | P1/P2 speedup合并对比 | P1与P2的扩展性差异 | 正文候选 | 不是新增独立数据；依赖图1/2口径。 |
| 4 | `fig4_p3_noL2_vs_L2` | P3 N1 CSV用于N1；N2~5用P2 vns no-L2与P3 vns L2逐case配对 | P3只读Cache下no-L2/L2 makespan对比 | 正文候选 | 需明确N2~5 no-L2来自P2、L2来自P3。 |
| 5 | `fig5_p3_l2_speedup` | N1来自P3 N1 CSV；N2~5逐case P2 vns/P3 vns后取均值 | L2 speedup与Cache hit率随N的统计结果 | 正文候选 | 不是Cache-aware solver消融；“L2”是论文概括性简称。 |
| 6 | `fig6_stage_ablation` | A/B/C job JSON中的baseline/multiseed/vns，按P与N合并统计 | 三阶段的阶段性下降 | 正文候选 | 嵌套阶段比较，不能做单变量因果或全局最优结论。 |
| 7 | `fig7_vns_gain_dist` | A/B/C job JSON中每case `(multiseed-vns)/multiseed`，P1/P2/P3、N=2/3与4/5箱线图 | VNS相对Multi-seed收益分布 | 附录/可选正文 | 探索性分布图；不作机制因果。 |
| 8 | `fig8_cache_hit_vs_speedup` | A/B/C job JSON中P3 cache_hit_rate与P2-vns/P3-vns speedup，N=2~5散点及线性趋势 | Cache hit与L2 speedup的相关性探索 | 附录/可选正文 | 只能写相关性，不能写因果；不得把回归线当机制证明。 |

图1-6在交接文档中被标为正文主图，图7-8被标为可选分析；最终正文是否使用仍须通过篇幅与合规审校。所有图应优先引用`figure_numbers.md`和CSV，不从图片肉眼读取数字。

## K. 历史数字与措辞风险清单

| 历史内容 | 处理 | 证据与原因 |
|---|---|---|
| “100例正式实验”旧表述 | **可使用但注明证据来源** | A/B/C manifest覆盖100个不重叠case，job JSON独立核得1200 jobs/3600 stage rows；merged raw detail.csv仍不可解析，不要声称由该CSV逐行读取。 |
| “400组” | **必须删除** | `docs/PAPER_RESULT_AUDIT.md`标为PLACEHOLDER；当前full100设计是1200 jobs、3600 stage rows，不是400。 |
| 旧6-case/15-case结果 | **可作为开发集证据保留** | `docs/EXPERIMENT_INVENTORY.md`、旧REPORT；不得作为full100正式数字。 |
| 23.51%中位数 | **必须替换/删除** | `docs/PAPER_RESULT_AUDIT.md`标为OUTDATED；当前正式figure_numbers未提供该数字。 |
| 22.58%旧中位数 | **不得直接进入正文** | 来自旧competition REPORT，非当前full100统计。 |
| 旧P1/P2 speedup（如2.42、2.89等） | **必须替换** | 旧6-case开发集或15-case竞赛结果；当前正式figure_numbers给出full100 N=1~5数字。 |
| 旧L2数字1.00007-1.004 | **必须删除** | `docs/PAPER_RESULT_AUDIT.md`标为UNVERIFIED；当前正式P3 N1~5统计不同。 |
| “全部CLI验证” | **必须替换/谨慎** | 旧交接文档明确competition CLI verified=0；当前full100 README未提供CLI验证数量。 |
| “adaptive” | **可用于正式full100配置描述** | 三份full100 manifest均记录`adaptive_budget=true`；只能说明配置开启，不能断言每个job实际因停滞提前终止。 |
| “fine-grain” | **可描述为正式候选变体，不可声称独立收益** | full100 manifest为`fine_grain=2`，job JSON中实际出现`*-2`候选来源；没有独立fine-grain full100消融。 |
| “SA” | **不得进入主算法；可如实写探索后未采用** | SA分支有真实pilot/expansion，但未合并stable solver、未进入full100；见I节。 |

## 当前可安全进入论文的最小集合

1. P1/P2/P3的官方评估机制差异、COPY和P3只读FIFO Cache机制（A级源码证据）。
2. Solver的Multi-seed + VNS(strict descent)结构、8个邻域、HEFT-style分配和官方Evaluator闭环（A级源码证据）。
3. L1/UB、带宽、等待、Cache容量和Cache带宽等`data/config.txt`正式评估参数（A级配置证据）。
4. singlecore 100-case基准及逐case speedup计算方法（A级结果/脚本证据）。
5. `figure_numbers.md`中的最终统计数字已由A/B/C归档 job JSON独立复算，可作为A级正式结果；merged CSV文件本身仍存在可读性风险。

## 仍待核验的问题

- [TBD-VERIFY] 定位或重新导出可解析的`results/full100_merged/detail.csv`、`summary.csv`及最终tables CSV；当前只能确认这些文件字节上不是可解析CSV，不能修改原文件。
- [TBD-VERIFY] 如最终交付流程要求直接读取 merged CSV，需由结果管理方提供未损坏的原始导出；当前论文数值不得依赖该文件的逐行解析。
- [TBD-VERIFY] full100 manifest记录`git_dirty=true`；如需“干净工作树/可完全复现源码快照”的更强 provenance，需要团队决定是否补充归档说明。
- [TBD-VERIFY] 归档 job JSON已闭环核心数字，但 merged CSV与最终tables CSV的文件级一致性无法核验，不能声称二者与重建结果逐字节一致。
