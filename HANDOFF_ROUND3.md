# 第三轮交接报告（最终冻结版）
## 时间: 2026-09-25

---

## 1. Git 状态

| 项目 | 值 |
|---|---|
| **Branch** | `teammate/development-v3` |
| **HEAD commit** | `51bc11b` (restore official LiSu font requirement) |
| **Remote** | `origin` → `https://github.com/mumumumu-bit/problem_A.git` |
| **Working tree** | 大量修改 (figures重生成, style.py/plots.py/plot_competition.py 修改) |
| **Untracked** | paper/, results/competition/, results/competition_p3/, scripts/plot_competition.py, docs/, 交接文档/ |

**注意:** `code/`, `data/config.txt`, `data/case_*.json` 均为官方原始文件，未被修改。

---

## 2. 当前真实完成度

### ✅ 已完成

| 项目 | 详情 |
|---|---|
| P1 + P2, 15 case, N2+N4 | competition/ 60组全部完成 |
| P1 + P2, 15 case, N2+N4 (dev) | A2_full15/ 60组全部完成 |
| P3, 6 case, N2+N4 | A2_final_p3 12组完成 (dev_v1/v2也有P3) |
| P1+P2+P3, 6 case, N2+N4 | dev_v1/v2各36组全部完成 + CLI验证 |
| 所有开发子实验 (A0/A1/A2) | 24组完成 |
| 图表生成 | 统一渲染中枢 style.py 完成；plot_competition.py + plots.py 均委托它 |
| pytest | 49 passed |
| 论文草稿 | paper/main.tex 存在（含过时数字，见下文） |

### ❌ 未完成

| 项目 | 详情 |
|---|---|
| **100 个全量 case** | **一个都没跑**。全部实验最多15个代表case |
| **P3 竞赛实验** | competition_p3/ 仅完成 8/30 组 (4个case)，缺11个case |
| **N=3/N=5** | 任何实验都没跑过N=3或N=5 |
| **CLI独立复核** | 只有dev_v1/v2/pilot/locality有CLI验证；竞赛实验全部无CLI复核 |
| **SA/GA/Tabu/全局优化** | **NOT IMPLEMENTED** |
| **Memory/Cache感知切分** | 权重=0，代码存在但未启用 |

---

## 3. 真实实验覆盖度

| 场景 | N=2 | N=4 | N=3 | N=5 |
|---|---|---|---|---|
| P1 | **15/100** | **15/100** | **0/100** | **0/100** |
| P2 | **15/100** | **15/100** | **0/100** | **0/100** |
| P3 | **4/100** | **4/100** | **0/100** | **0/100** |

**结论: 100个case一个都没跑过。N=3和N=5从未测试。**

---

## 4. 当前可信结果 (VERIFIED — 来自 competition/ 15例实验)

可信加速比 (来自 `results/competition/REPORT.md`, 60组):

| 问题 | 核数 | 加速比 |
|---|---|---|
| P1 | 2 | **1.636** |
| P1 | 4 | **2.478** |
| P2 | 2 | **1.723** |
| P2 | 4 | **2.753** |

可信改善率: **均值 26.46%, 中位数 22.58%** (57/60改善, 3持平, 0退化)

P3可信加速比 (来自 A2_final_p3, 6例12组): N2=1.707, N4=2.915

---

## 5. 论文中无实验支撑的数字

| 论文数字 | 实际状态 | 标签 |
|---|---|---|
| "100例正式实验" | 实为15例 | **UNVERIFIED** |
| "400组" | 100×P1/P2×N2/N4 不存在 | **PLACEHOLDER** |
| P1/N4=2.42 | 竞赛15例实际=2.478 | **OUTDATED** (来自6例开发集) |
| P2/N4=2.89 | 竞赛15例实际=2.753 | **OUTDATED** (来自6例开发集) |
| 中位数=23.51% | 实际=22.58% | **OUTDATED** |
| L2加速比 1.00007-1.004 | 无独立受控实验 | **UNVERIFIED** |

---

## 6. 当前算法真正实现到什么程度

**核心架构:** Multi-seed (4 families × 3 grains) + VNS (8 neighborhoods, strict descent only)

**已实现:** 8种邻域(N1-N8), HEFT-style core assignment, 三粒度coarsening, candidate ranking with estimator, adaptive neighborhood selection (默认关闭), stagnation early stopping (默认关闭)

**未实现:** SA, GA, Tabu, CP-SAT, Cache感知切分(cache_weight=0), Memory硬约束(memory_weight=0), 任何全局优化

详细算法审计见 `docs/CURRENT_ALGORITHM.md`

---

## 7. 当前最严重的3个问题

### P0: 论文声称与实验事实不符
- 论文写"100例"，实际跑了15例
- 加速比数字部分来自旧版6例实验，非最新15例竞赛结果
- **必须修正论文中所有数字匹配真实实验结果**

### P0: 100个case全量未跑
- 国赛要求全量100 case结果
- 必须执行三分方案（见HANDOFF_ROUND3_old.md）

### P1: VNS 效率瓶颈
- 38/60组VNS有增益，但22组完全无增益（约37%卡在局部最优）
- 纯strict descent无全局跳出机制
- **最直接改善方向: 加入SA接受准则**

---

## 8. 当前最值得继续的3个方向

1. **加入SA到VNS** — 改动最小(vns.py 约20行)，直接解决22/60组卡局部最优的问题
2. **完成100 case全量实验** — 三分方案已有，每人～33 case
3. **修正论文数字** — 全部替换为15例竞赛实验的真实数字，删除"100例"说法或标注为"后续工作"

---

## 9. 下一位开发者的第一步

1. `git pull` 获取最新代码
2. 阅读 `docs/EXPERIMENT_INVENTORY.md` 了解实验库存
3. 阅读 `docs/PAPER_RESULT_AUDIT.md` 知道哪些论文数字需要修正
4. 阅读 `docs/CURRENT_ALGORITHM.md` 了解算法边界
5. 从三分方案中认领一组case（见 HANDOFF_ROUND3_old.md 的第二节）
6. 跑实验: `python scripts/run_all.py --output results/full100_YOUR_NAME --problem 1 2 3 --cases <your_cases> --config data/config.txt --workers 2 --time-budget 300 --max-evaluations 64 --skip-cli-verification`

---

## 10. 可复现命令

```bash
cd /d/BAKFILE/9017530/huawei_cup_2026/problem_A

# pytest (验证代码完整)
.venv/Scripts/python.exe -m pytest -q

# 生成所有图表
.venv/Scripts/python.exe -c "
from npu_scheduler.visualization.plots import plot_benchmark
for d in ['development_v1','development_v2','development_v3/A2_final','development_v3/A2_final_p3','development_v3/A2_full15']:
    plot_benchmark('results/'+d)
" ; .venv/Scripts/python.exe scripts/plot_competition.py

# 单case求解示例
.venv/Scripts/python.exe -m npu_scheduler.cli solve --graph data/case_001.json --config data/config.txt --problem 1 --cores 4 --output results/test_output.json
```

---

## 11. 关键警告

- **不要修改 `code/` 目录下的官方文件**
- **不要修改 `data/config.txt` 或 `data/case_*.json`**
- **competition.yaml 配置未冻结为最终竞赛配置**
- **Memory/Cache权重为0，不要声称已启用**
- **VNS 是纯局部下降，不是全局优化**

---

## 12. 官方要求 vs 团队内部目标

| 指标 | 来源 | 性质 |
|---|---|---|
| 三个子问题全部求解 | 赛题要求 | **官方要求** |
| P1 N4 ≥ 3.0x | 无官方来源 | **内部目标** |
| 平均改善率 ≥ 35% | 无官方来源 | **内部目标** |
| VNS有效比例 ≥ 80% | 无官方来源 | **内部目标** |

*没有官方公布的"国赛硬性门槛"数字。所有阈值均为团队内部经验目标。*

---

*本文档冻结于 2026-09-25。详细材料见 docs/ 目录下的三个审计文件。*