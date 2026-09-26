# 2026 华为杯 A 题多核调度项目——队友交接文档

## 0. 当前交接状态
- 分支：`main`
- checkpoint commit：`72cc900816ddcab8b5ebab0113b52ed392a96986`
- commit message：`checkpoint: hand off first-round NPU scheduler`
- working tree：clean
- 本地 `main` 比 `origin/main` 超前 1 个提交
- `HANDOFF.md` 已更新并纳入 checkpoint commit

仓库：
`https://github.com/mumumumu-bit/problem_A`

> 队友开始前，项目负责人必须先把 `72cc900` 推送到 GitHub。

## 一、项目负责人交接前操作

### 1. 解决 GitHub 认证并推送
此前 `git push` 使用了无权限账号 `treetree123321`。请切换到对 `mumumumu-bit/problem_A` 有写权限的账号。

```powershell
cd D:\problem_A\problem_A
git credential-manager github logout
git push origin main
```

浏览器认证时登录有写权限的 GitHub 账号。

### 2. 推送后核验
```powershell
git status
git log -3 --oneline
git remote -v
```

应看到：
```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

GitHub 页面应能看到：
```text
72cc900 checkpoint: hand off first-round NPU scheduler
```

## 二、队友第一次接手

### 1. Clone
```powershell
git clone https://github.com/mumumumu-bit/problem_A.git
cd problem_A
```

如果已 clone：
```powershell
git checkout main
git pull origin main
```

### 2. 检查 checkpoint
```powershell
git log -5 --oneline
```

必须能看到：
```text
72cc900 checkpoint: hand off first-round NPU scheduler
```

看不到就不要开始开发。

### 3. 建立第二轮分支
```powershell
git checkout -b teammate/development-v3
```

不要直接在 `main` 上开发。

### 4. 创建环境并测试
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

预期第一轮为：
```text
41 passed
```

测试数量增加但全部通过不算异常；如果失败，先处理交接异常。

### 5. 阅读顺序
1. `AGENTS.md`
2. `HANDOFF.md`
3. `docs/first_round_report.md`
4. `docs/solver_usage.md`
5. `results/development_v2/REPORT.md`
6. `results/development_v2/neighborhood_diagnostics.json`
7. `results/development_v2/version_comparison.csv`

不要重新从头阅读整个赛题，不要重新设计工程。

## 三、第一轮已完成状态

- 41 项 pytest 通过
- 36/36 代表实验通过官方 CLI 独立复核
- 全部 100 个 case 已完成结构审计
- 未启动完整 100 例正式优化
- 当前统一算法：四族多粒度 Multi-seed + VNS
- Baseline → VNS：开发集平均逐组 Makespan 降低 18.79%
- Multi-seed → VNS：平均进一步降低 2.38%
- VNS 在 25/36 组中进一步改善 Multi-seed
- N1/N2 当前最主要有效邻域
- N3 已有较多历史评估但未产生真实改善
- 官方 evaluator 占历史运行时间约 95.7%
- `development_v2` 整体优于 `development_v1`
- `case_019` 存在 regression
- `competition.yaml` 尚未冻结
- P3 同方案 L2 收益目前很小，第二轮优先稳定 P1/P2 通用搜索

当前阶段目标不是重新做 baseline，而是：
> 在固定 evaluator 成本下，提高每一次真实评估调用的价值，扩大开发集，降低 regression，并判断是否可以冻结 competition 配置。

## 四、严禁修改
```text
code/
data/config.txt
data/case_*.json
```

新结果写入：
```text
results/development_v3/
```

禁止覆盖：
```text
results/development_v1/
results/development_v2/
```

## 五、第二轮开发原则
1. 不针对具体 case id 写特殊规则。
2. 不人工给不同 case 挑不同版本结果。
3. 所有候选由统一算法产生，再交给官方 evaluator。
4. Makespan 第一目标，Added Copy 第二目标。
5. 不机械加入 GA / SA / CP-SAT。
6. 每个复杂模块必须由真实 evaluator 证明收益。
7. 随机逻辑保持 deterministic seed。
8. 新增逻辑必须补测试。
9. 实验使用公平预算。
10. 先扩 development set、改进 evaluator budget，再决定是否冻结 competition 配置。

## 六、第二轮具体任务

### Task 1：扩大 development set
从 100 个 case 中分层选择 12~18 个，必须保留：
`001 / 019 / 005 / 050 / 025 / 085`

依据：
- non_copy_ops
- DAG depth
- width
- PIPE_M / PIPE_V workload ratio
- communication/computation ratio
- tensor size / memory pressure
- graph scale

覆盖 small / medium / large / extra-large 与不同 graph shape。

输出：
```text
configs/development_cases.yaml
docs/development_set_selection.md
```

### Task 2：分析 N1~N8 neighborhood efficiency
读取所有 `trials.jsonl` 和 `results/development_v2/neighborhood_diagnostics.json`。

统计：
- generated candidates
- official evaluations
- strict improvements
- improvement rate
- total Makespan reduction
- mean reduction when successful
- evaluator time
- improvement per evaluator call
- improvement per second

输出：
```text
results/neighborhood_analysis.csv
docs/neighborhood_analysis.md
```

### Task 3：Adaptive VNS Budget
基于真实数据动态调整邻域预算。

初始方向：
- 高优先：N1 / N2
- 中优先：N4 / N5
- 低预算探索：N7 / N8
- N3：显著降频但暂不删除
- N6：由数据决定

维护：
`attempts / successes / gain / evaluation_time`

依据近期：
`gain_per_eval / gain_per_second`

必须保留最低探索次数，保持 deterministic seed。

### Task 4：解决 case_019 regression
比较 `development_v1` 与 `development_v2` 的：
- partition/coarsening
- seed family
- target workload
- block 数
- core assignment
- scheduling order

禁止：
```python
if case == "case_019":
    ...
```

目标是抽取 v1 的通用优势机制，并实现为所有 case 都可尝试的 seed/coarsening variant。

### Task 5：Incumbent Portfolio
保留当前四族 seed，只加入少量真正结构不同的候选：
- coarsening granularity
- affinity threshold
- critical-path weighting
- recovered-v1 variant

目标：8~12 个高质量结构候选，而不是大量细微参数组合。

先 cheap ranking，再让少量最有价值候选调用官方 evaluator。

### Task 6：Early Stopping / Budget Allocation
至少考虑：
- graph size
- 单次 evaluator 平均耗时
- 最近 evaluator improvement
- 距离上次 improvement 的调用次数

保留 hard max evaluations 和 soft time budget。

### Task 7：Development v3 实验
先跑：
```text
Problem 1
Problem 2
cores = 2, 4
```

比较：
```text
A0 = current development_v2 solver
A1 = adaptive neighborhood budget
A2 = + recovered v1 candidate mechanism
A3 = final combined
```

公平预算，并报告：
- Mean normalized Makespan
- Mean speedup
- Median improvement
- Worst-case regression
- Improved / tied / regressed count
- Official evaluator calls
- Wall-clock time

### Task 8：Regression Gate
至少保留：
```text
case_019 P1/N2
case_019 P1/N4
```

以及 small / medium / large 代表组。

允许统一 solver 同时生成 old/new seeds，再由 evaluator 选优。
禁止人工按 case 拼结果。

### Task 9：高级算法判断
本轮不实现：
- GA
- SA
- Tabu
- CP-SAT

完成扩展开发集实验后再判断是否值得引入。

### Task 10：Competition config 冻结条件
仅当同时满足：
- development set >= 12 cases
- small / medium / large 均覆盖
- P1/P2 N=2/4 完成
- 无明显系统性 regression
- adaptive budget 有稳定收益
- 结果可重复

才允许冻结：
```text
configs/competition.yaml
```

并创建：
```text
docs/competition_config.md
```

否则明确输出 `No`。

## 七、Git 工作方式

开发分支：
```text
teammate/development-v3
```

建议阶段性提交：
```powershell
git add .
git commit -m "analyze neighborhood evaluation efficiency"

git add .
git commit -m "add adaptive VNS budget scheduler"

git add .
git commit -m "recover general seed mechanism from v1"

git add .
git commit -m "complete development v3 benchmark"
```

首次：
```powershell
git push -u origin teammate/development-v3
```

后续：
```powershell
git push
```

不要 force push，不要直接覆盖 main。

## 八、队友完成后交还

完成后：
```powershell
git status
.\.venv\Scripts\python.exe -m pytest -q
git push
```

并交付：
1. 最新 commit hash
2. branch 名
3. pytest 结果
4. `development_v3` 报告
5. competition.yaml 是否冻结
6. 已知 regression
7. 下一步唯一建议

项目负责人审核后再决定是否 merge 回 main。
