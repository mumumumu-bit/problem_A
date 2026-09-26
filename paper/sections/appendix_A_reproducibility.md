# 附录A 实验配置与复现说明

## A.1 实验设置

正式测试包含case_001至case_100共100个用例，覆盖P1、P2、P3三个问题。正式full100多核实验采用N=2、3、4、5，共1200个求解任务，每个任务保存Baseline、Multi-seed、VNS三个阶段的记录。附录B的多核最终结果仅取VNS阶段。

N=1采用正式固定单核结果：P1、P2共用正文Speedup统计所用的Scene A single-core baseline；P3采用逐case固定同一plan的no-L2/共享只读L2 Cache配对结果。P3在N=2至5下以P2 VNS为no-L2、P3 VNS为L2，两种场景分别求解，不是same-plan实验。

stable solver的来源commit为 `34d0a423fd99639e2d9c4630cb7979871273a8a7`。A/B/C正式manifest均记录 `git_dirty=true`，因此该commit是源码来源标识，不能仅凭它声称运行时工作树是干净快照或能够逐字节完全复现。正式来源还须结合manifest中的配置、源码和官方代码指纹，以及冻结job归档核对。

固定硬件和场景参数来自 `data/config.txt`，与第6章保持一致。

| 参数 | 固定值 | 单位说明 |
|---|---:|---|
| L1容量 | 524288 | 配置项未显式标明单位，不另补单位 |
| UB容量 | 131072 | 配置项未显式标明单位，不另补单位 |
| DDR bandwidth | 60 | bytes/cycle |
| Scene A cross-core wait | 1000 | cycles |
| Scene A same-core wait | 100 | cycles |
| Scene B cross-core COPY latency | 500 | cycles |
| P3 shared readonly L2 Cache capacity | 1048576 | bytes |
| P3 L2 bandwidth | 250 | bytes/cycle |

<!-- Evidence: paper/EVIDENCE_MAP.md A、D、F、G；paper/sections/06_experiment.md；data/config.txt；paper/APPENDIX_DATA_PROVENANCE.md。 -->

## A.2 正式求解配置

正式配置文件为 `configs/fullrun_stable.yaml`，与A/B/C归档manifest绑定。以下为配置值和预算上限，不表示每个任务均耗满时间或评价次数。

| 参数 | 正式配置 | 含义 |
|---|---|---|
| seed | 2026 | 随机种子 |
| time_budget | 300 s | 搜索时间预算 |
| max_evaluations | 64 | 配置层评价预算上限，实际有效上限按图规模缩减 |
| candidate_pool | 48 | 仅用于VNS邻域候选池 |
| Top-K（top_k） | 3 | 仅用于VNS候选排序后的官方评价筛选 |
| max_rounds | 32 | VNS轮数上限 |
| grains | [4, 12, 32] | 主候选生成粒度 |
| fine_grain | 2 | 额外候选生成变体 |
| workers | 2 | 批量任务并行worker数，不是模拟计算核数N |
| adaptive（adaptive_budget） | true | 自适应邻域选择与停止 |
| base stagnation threshold（stagnation_patience） | 8 | 基础停滞阈值 |
| min_neighbourhood_trials | 3 | 最低邻域探索配置 |
| portfolio_size | 12 | 结构seed portfolio大小配置 |
| cache_weight / memory_weight | 0.0 / 0.0 | 未启用对应估计器权重 |

Multi-seed阶段对未重复且预算允许的seed候选逐个执行官方评价，不采用“48候选池后只评价Top-3”的筛选。fine_grain=2只是候选生成变体，没有独立消融证据；adaptive亦未单独消融，不将正式收益归因于某一配置项。

`StrategySelector.select`依据预处理后可调度图的节点数n设置有效max_evaluations：n<2000为64，2000≤n<10000为40，10000≤n<25000为26，n≥25000为20，并与传入配置取较小值。这是源码中的图规模预算规则，应与VNS阶段的adaptive邻域选择、停滞停止区分。实际评价还受去重、时间预算及停止条件影响，不能写成每个case始终执行64次Evaluator。第5章所述基础停滞阈值为8；n>10000时增加耐心值，且停止还需满足相应评价次数条件。

<!-- Evidence: configs/fullrun_stable.yaml；src/npu_scheduler/config.py StrategySelector；src/npu_scheduler/search/vns.py；第5章5.5、5.7及第6章6.2；paper/APPENDIX_DATA_PROVENANCE.md已核验各job有效配置。 -->

## A.3 结果生成流程

正式流程为：图预处理 → Baseline/Multi-seed划分候选 → HEFT-style核分配与核内序列 → official Evaluator → 当前已评价最好有效方案 → VNS候选生成与排序 → official Evaluator → final best-so-far。

VNS仅接受官方评价有效且字典序 `(Makespan, Added Copy)` 严格改善的候选；估计器只用于候选排序，不能替代官方指标。best-so-far表示受限搜索中已评价的最好有效方案，不表示global optimum。三个阶段快照属于同一次嵌套搜索。

附录数据的整理不重新求解或重新评估：从 `origin/results/full100-A/B/C` 中 `results/full100_teammate_A/B/C/<case>_p<problem>_n<N>/job.json` 读取最终vns行；N=1分别读取 `results/singlecore_full100/singlecore.csv` 和 `results/p3_singlecore_full100/p3_n1_l2.csv` 的正式归档。随后按case、problem、N关联字段，生成附录B的三个标准CSV，并从生成CSV检查完整性及复算聚合指标。

目前merged detail/summary及最终tables CSV存在不可解析问题；本论文使用可核验的归档job JSON来源链，不声称这些merged CSV已被逐行读取或与恢复数据达到文件级一致。逐行来源、冻结分支commit和核验结果分别保存在 `paper/APPENDIX_DATA_PROVENANCE.md` 与 `paper/appendix_data/VALIDATION.md`。

<!-- Evidence: 第5章；paper/EVIDENCE_MAP.md C、E及CSV可读性说明；附录B与来源审计。 -->

## A.4 程序入口与复现方式

以下入口和参数已经只读核对实际源码。命令仅用于说明仓库接口和历史运行方式，本次附录整理未执行求解、批量实验或Evaluator。未来复现应在另备的程序副本及新输出目录中进行；论文正式数据继续使用冻结归档。

### 环境与单case入口

`pyproject.toml`要求Python≥3.10。保持 `src/`、`code/`、`data/` 的相对位置；硬件配置为 `data/config.txt`，求解配置为 `configs/fullrun_stable.yaml`，输入图为 `data/case_XXX.json`。包安装方式在 `docs/solver_usage.md` 中已有说明：

```text
python -m venv .venv
python -m pip install -e ".[dev]"
```

第二条在激活所建虚拟环境后、项目根目录执行。已安装包时，单case入口为 `python -m npu_scheduler.cli solve`；`pyproject.toml`也注册 `npu-schedule` 到同一个 `main`。以下示例的参数均由实际argparse接口支持：

```text
python -m npu_scheduler.cli solve --graph data/case_001.json --problem 1 --cores 2 --config data/config.txt --solver-config configs/fullrun_stable.yaml --algorithm vns --output reproduction/example/plan.json --skip-cli-verification
```

示例输出为 `reproduction/example/plan.json` 和 `plan.metrics.json`；`--problem`可选1、2、3，solve模式须指定一个问题和一个核数。`--skip-cli-verification`仅跳过独立CLI复核，求解过程中仍使用官方Evaluator。

### 正式full100批量入口

实际批量入口是 `scripts/run_all.py`，其调用 `npu_scheduler.cli.main(['benchmark', ...])`。正式A/B/C分片脚本分别读取 `configs/full100_A.txt`、`full100_B.txt`、`full100_C.txt`，显式指定P1/P2/P3、N=2/3/4/5、300秒、64次上限和2个workers。历史脚本入口为：

```powershell
& .\scripts\run_full100_A.ps1
& .\scripts\run_full100_B.ps1
& .\scripts\run_full100_C.ps1
```

这些脚本的原输出目录分别为 `results/full100_teammate_A`、`results/full100_teammate_B`、`results/full100_teammate_C`；它们使用项目 `.venv\Scripts\python.exe`，不存在时使用 `python`，并设置 `--skip-cli-verification`。因此不能据此声称全部正式任务已完成独立CLI复核。批量入口未显式传入case列表时采用开发集默认值，不能将默认调用当作full100。

### 官方Evaluator与单核工具

适配入口为 `src/npu_scheduler/evaluator/official_adapter.py` 的 `OfficialEvaluator`：`raw`分别调用官方 `evaluate_scene_a`、`evaluate_scene_b`、`evaluate_problem_3`；`singlecore`调用官方 `evaluate_singlecore`。对应文件在 `code/` 下。README中已有官方CLI入口，例如：

```text
python code/multicore_cut_evaluate_problem_1.py data/case_001.json reproduction/example/plan.json --config data/config.txt
```

P2、P3对应 `multicore_cut_evaluate_problem_2.py`、`multicore_cut_evaluate_problem_3.py`。单核正式生成工具 `scripts/singlecore_full100.py`、`scripts/p3_singlecore_l2.py` 及其调用记录位于 `origin/results/singlecore-full100` 归档；当前paper工作树没有这两个脚本，不能将其写成当前目录可直接执行的提交命令。P3工具对同一plan执行problem=2与problem=3评价并核验plan未被修改。

[PROGRAM-PACKAGE-TODO: 最终程序附件README中补充] 最终压缩包名称与目录、提交用单case命令及问题切换方式、安装/激活步骤、单核归档工具是否纳入附件、运行环境及依赖版本、dirty工作树与归档源码指纹的对应说明。上述仓库入口说明不能替代实际程序附件交付，也不表示已验证最终压缩包在独立环境运行。

<!-- Evidence: pyproject.toml；docs/solver_usage.md（仅入口与环境部分，旧开发集结果不作为正式结果）；src/npu_scheduler/cli.py；scripts/run_all.py；scripts/run_full100_A/B/C.ps1；README.md；official_adapter.py；origin/results/singlecore-full100:docs/FINAL_METRICS.md及归档工具。所有示例均未执行。 -->

## A.5 输出与评价指标

正式方案JSON至少包含 `node_to_subgraph` 与 `core_schedules`：前者将计算操作ID映射到子图，后者记录各核的子图执行序列。`Solution.plan`生成该格式，单case入口另存正式评价及搜索记录到 `.metrics.json`。批量任务保存阶段 `*_plan.json`、`job.json`、`trials.jsonl`，运行级保存manifest及汇总文件；最终方案使用VNS阶段记录。

Makespan为官方执行完成时间；Added Copy取官方 `data_movement_bytes.added_copy_bytes`，单位为字节，与单独记录的spill字段区分；P3 Cache Hit Rate取 `cache_stats.hit_rate`，为[0,1]比例，仅作为分析指标。候选比较以Makespan优先，仅在相同时用Added Copy决胜。

P1/P2平均Speedup先计算每个case的正式共同单核Makespan除以相应多核VNS Makespan，再对100个case取算术平均，不是总单核时间/总多核时间。P3同样先逐case计算no-L2/L2 Makespan比值再取平均；N=1为固定plan配对，N=2至5为分别求解的P2/P3结果比较。Cache Hit Rate均值也取100个case命中率的算术平均。

<!-- Evidence: src/npu_scheduler/types.py Solution.plan/Evaluation；cli.py；experiment/runner.py；official_adapter.py；第6章6.3—6.6；paper/EVIDENCE_MAP.md B、E、F、G。 -->
