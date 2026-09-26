# 队友A — 最终可视化结果交接文档

> 本文档说明合并代码后所有新增/变更的文件夹路径及内容，供队友B、C查阅。

---

## 一、新增/关键文件夹总览

| 路径 | 说明 |
|---|---|
| `results/full100_merged/` | **三人数据合并后的总数据集**（图表的数据源） |
| `results/full100_teammate_B/` | B队友的原始实验结果 |
| `results/full100_teammate_C/` | C队友的原始实验结果 |
| `results/final_visualization/` | **最终论文可视化输出**（图、表、附录数据） |
| `scripts/` | 图表生成脚本（含8个最终图脚本） |
| `paperfig/` | 论文图表样式包（Icarus-Figures） |
| `logs/` | 运行日志 |
| `交接文档/` | 新增本交接文档 |

---

## 二、合并数据：`results/full100_merged/`

三人（A/B/C）各跑部分用例，通过 `scripts/merge_full100_results.py` 合并为统一数据集。

| 文件 | 内容 |
|---|---|
| `detail.csv` | 3600行：1200个job × 3种算法(baseline/multiseed/vns)，每个job的makespan、runtime等 |
| `summary.csv` | 按 case/problem/cores/algorithm 聚合的均值/标准差 |

---

## 三、最终可视化：`results/final_visualization/`

### 3.1 论文图表 — `figures/`（最重要）

共 **8张图**，每张图输出 **3种格式**（PDF / PNG / SVG），共24个文件：

| 文件名 | 内容 | 备注 |
|---|---|---|
| `fig1_p1_speedup.{pdf,png,svg}` | 图1：P1多核加速比（N=2,3,4,5 vs N=1） | 正文必须 |
| `fig2_p2_speedup.{pdf,png,svg}` | 图2：P2多核加速比 | 正文必须 |
| `fig3_p1p2_combined.{pdf,png,svg}` | 图3：P1/P2加速比合并对比 | 正文必须 |
| `fig4_p3_noL2_vs_L2.{pdf,png,svg}` | 图4：P3无L2Cache与只读L2Cache对比（柱状图） | 正文必须 |
| `fig5_p3_l2_speedup.{pdf,png,svg}` | 图5：P3 L2Cache加速比 | 正文必须 |
| `fig6_stage_ablation.{pdf,png,svg}` | 图6：算法阶段消融（基线→多种子→VNS） | 正文必须 |
| `fig7_vns_gain_dist.{pdf,png,svg}` | 图7：VNS收益分布箱线图（各case提升百分比分布） | **新增，可选分析** |
| `fig8_cache_hit_vs_speedup.{pdf,png,svg}` | 图8：Cache命中率与L2加速比关联散点图 | **新增，可选分析** |

> **说明**：图1-6为指南明确要求的正文图表；图7和图8为指南第13节"可选分析"中提到的探索性图表，后续新增，论文正文中可根据篇幅决定是否纳入。

**论文插图使用 PNG（600dpi）或 PDF 矢量格式。**

### 3.2 数据表格 — `tables/`

| 文件 | 内容 |
|---|---|
| `p1_speedup_1to5.csv` | P1加速比数值表 |
| `p2_speedup_1to5.csv` | P2加速比数值表 |
| `p3_l2_comparison_1to5.csv` | P3 L2对比数值表 |
| `stage_ablation.csv` | 消融实验数值表 |

### 3.3 附录数据 — `appendix/`

| 文件 | 内容 |
|---|---|
| `p1_per_case.csv` | P1每个测试用例的详细makespan |
| `p2_per_case.csv` | P2每个测试用例的详细makespan |
| `p3_per_case.csv` | P3每个测试用例的详细makespan |

### 3.4 参考文档

| 文件 | 内容 |
|---|---|
| `README.md` | 数据来源说明（commit hash, 分支名） |
| `figure_numbers.md` | 论文中引用的所有数值（加速比、消融改进率等） |

---

## 四、图表生成脚本：`scripts/`（⚠️ 禁止修改）

以下 **8个脚本** 是最终论文图表的生成代码，已经过多轮精细排版调整（字号、颜色、间距、标注位置、坐标轴格式等）。

### ⛔ 严禁修改以下文件，否则图表会变形：

| 脚本 | 对应图表 | 备注 |
|---|---|---|
| `scripts/fig1_p1_speedup.py` | 图1 | 正文必须 |
| `scripts/fig2_p2_speedup.py` | 图2 | 正文必须 |
| `scripts/fig3_p1p2_combined.py` | 图3 | 正文必须 |
| `scripts/fig4_p3_noL2_vs_L2.py` | 图4 | 正文必须 |
| `scripts/fig5_p3_l2_speedup.py` | 图5 | 正文必须 |
| `scripts/fig6_stage_ablation.py` | 图6 | 正文必须 |
| `scripts/fig7_vns_gain_dist.py` | 图7 | **新增，可选分析** |
| `scripts/fig8_cache_hit_vs_speedup.py` | 图8 | **新增，可选分析** |

> **注意**：图7和图8为后续新增的可选分析图表，来源指南第13节。如论文篇幅不够可省略，但脚本格式已与图1-6统一，同样禁止随意修改排版参数。

### 这些脚本依赖以下公共模块（也不要随意修改）：

| 文件 | 说明 |
|---|---|
| `scripts/_cn_font.py` | 全局matplotlib样式：字体(SimHei)、配色(Okabe-Ito)、图例字号等 |
| `scripts/_style.py` | 辅助样式函数 |

### 重新生成图表

如果需要重新生成所有图表（比如合并数据更新后），运行：

```bash
cd scripts
python fig1_p1_speedup.py
python fig2_p2_speedup.py
python fig3_p1p2_combined.py
python fig4_p3_noL2_vs_L2.py
python fig5_p3_l2_speedup.py
python fig6_stage_ablation.py
python fig7_vns_gain_dist.py
python fig8_cache_hit_vs_speedup.py
```

> 图表会自动输出到 `results/final_visualization/figures/`，覆盖旧文件。

---
## 五、注意事项

1. **数据源**：图表脚本从 `results/full100_merged/detail.csv` 读取合并数据，图4/5额外读取 `results/p3_singlecore_full100/p3_n1_l2.csv`。如果后续实验数据有变化，需重新运行 `merge_full100_results.py` 合并，再重新运行8个图表脚本。
2. **图表格式已锁定**：图1-8的样式（尺寸、字体、颜色、标注位置）已经过多轮调整定型，**不要修改8个fig脚本中的任何排版参数**。其中图7和图8为后续新增的可选分析图表。
3. **论文中直接引用**：`figure_numbers.md` 中包含论文所需的所有数值，可直接复制使用。
4. **字体依赖**：图表使用 SimHei（黑体），如果队友的电脑上没有 SimHei，需安装或替换 `_cn_font.py` 中的字体配置。