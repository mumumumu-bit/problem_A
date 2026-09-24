# 求解器运行说明

保留项目根目录 `code/`、`data/` 与 `src/` 的相对关系。求解器核心仅依赖 Python 标准库（Python>=3.10）。以下路径均为项目相对路径；Windows 与 Linux 可使用同一 Python 命令。

## 安装与入口

```text
python -m venv .venv
# 激活虚拟环境后：
python -m pip install -e ".[dev]"
python -m pytest -q
```

在项目目录直接用 `scripts/*.py`，无需 editable 安装。使用包入口 `python -m npu_scheduler.cli` 需要先执行 editable 安装。安装后可以从任意工作目录调用，官方代码位置从模块自身路径定位；`--graph`、`--config`、`--output` 等显式路径相对于当前工作目录。

```text
python scripts/audit_dataset.py --data-dir data --output results/dataset_audit.csv

python -m npu_scheduler.cli solve --graph data/case_019.json --problem 1 --cores 4 --config data/config.txt --solver-config configs/default.yaml --output results/example/plan.json

python scripts/benchmark.py --output results/my_development_run --solver-config configs/default.yaml --workers 2

python scripts/singlecore_baselines.py --run-dir results/my_development_run
python scripts/compare_l2.py --run-dir results/my_development_run
python scripts/report_results.py --run-dir results/my_development_run
python scripts/plot_results.py --output results/my_development_run
```

`benchmark.py` 默认六例：001、019、005、050、025、085，问题1/2/3、N=2/4。不会默认启动 100 例全量求解。可用 `--cases case_001 case_019 --problem 1 --cores 2 4` 缩小范围。

所有最终解默认通过官方 CLI 再评估一次，输出 `cli/result.json`、Perfetto trace 和官方日志；临时开发可显式 `--skip-cli-verification`，其状态写入 job.json。CSV 中 runtime 包含输入图构造和前序算法阶段，不包含独立 CLI 复核耗时。后者单独写入 job.json。

```text
python scripts/benchmark.py --output results/resumable --cache-dir results/evaluation_cache
```

相同命令再次运行时跳过已完成 job；输入、源码或配置有变化必须使用新目录。缓存只保存真实官方结果；运行时间比较请使用全新目录且省略 `--cache-dir`，避免将缓存命中误记为算法加速。

## 输出

- `dataset_audit.csv`：100例合法性检查后的结构特征，不是100例求解结果。
- `<run>/manifest.json`：源码/官方代码版本指纹、环境、seed、配置、案例范围。
- `<run>/benchmark.csv`：逐 case/problem/core/algorithm 的 Makespan、Added Copy、Spill、Cache命中率、累计运行时间。
- `<run>/summary.csv`：逐例归一化后的均值，不使用均值之比。
- `<run>/<case>_pX_nY/*_plan.json`：三阶段方案；`incumbent.json` 为实时最优可行解。
- `trials.jsonl`：每个实际评估候选的结果、估计值、耗时与改善状态。
- `job.json`：评估器调用数、缓存命中数、CLI复核状态、失败候选数。
- `singlecore.csv`：独立官方单核基准。
- `l2_same_plan.csv`：把问题3最终方案交给问题2评估器，控制方案不变的 L2 对照。
- `REPORT.md`、`comparison.csv`、`benchmark_table.tex`：完整逐例三阶段比较与 booktabs 表格。
- `figures/`：300dpi PNG、矢量 PDF 与图注语义。

`fast/default/competition.yaml` 是预算预设。competition 尚未经过10～20例调参冻结，不得标注为最终竞赛配置。现有实验只支持第一轮开发结论。

## 复现限制

时间预算为调用间软截止，不会强杀正在执行的官方函数。大图整图评估可能显著超时；默认只在阈值内把整图作为常规候选，若所有种子不可行才使用紧急整图兜底。超过软预算的实际时间必须按日志报告。

不同机器若触及时间预算，候选数可能不同。严格重复给定实验可以使用充足 `--time-budget` 并固定 `--max-evaluations`、源码和 seed。官方数据与代码不得修改。

已预留 AI 使用声明，工具/模型版本/发布日期由使用者核对后填写，不自动猜测。
