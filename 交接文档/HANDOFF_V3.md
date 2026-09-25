# 队友交接文档 — 第三轮完成

## 状态

- 分支：`teammate/development-v3`
- 最新 commit：`6aedc3c`（已推送）
- 所有源码、数据、图表均在仓库内
- 100 例竞赛实验已完成

---

## 一、代码交接

### 源码位置：`src/npu_scheduler/`

| 模块 | 文件 | 说明 |
|------|------|------|
| 图解析 | `graph.py`, `types.py` | DAG 解析、COPY 收缩、特征预计算、方案表示 |
| 图划分 | `partition/coarsening.py` | 两层聚合（atomic + coarse），grain=2/4/12/32 |
| 初解 | `partition/initial_partition.py` | 四族种子 + portfolio fine_grain 变体 |
| 核分配 | `schedule/core_assignment.py` | HEFT 风格 ready-list 分配 |
| VNS | `search/vns.py` | 八邻域 + top-K 筛选 + 自适应预算 + 早停 |
| 评估器 | `evaluator/official_adapter.py` | 官方接口适配 + 内容寻址缓存 |
| 实验 | `experiment/runner.py` | 进程并行、断点续跑、manifest 记录 |
| CLI | `cli.py` | 命令行入口：solve / benchmark / audit / plot |

### 配置：`configs/`

| 文件 | 用途 | 参数 |
|------|------|------|
| `default.yaml` | 开发集基准 | 120s, 36evals, seed=2026 |
| `development_v3.yaml` | A2 最终方案 | adaptive_budget=true, fine_grain=2 |
| `competition.yaml` | 竞赛配置 | 300s, 64evals |
| `development_cases.yaml` | 15 例开发集列表 | --- |
| `fast.yaml` | 快速调试 | 30s, 18evals |

### 脚本：`scripts/`

| 文件 | 用途 |
|------|------|
| `report_results.py` | 从 benchmark.csv 生成 REPORT.md + LaTeX 表 |
| `singlecore_baselines.py` | 生成独立单核基线 |
| `plot_results.py` / `run_all.py` | 通用绘图入口 |
| `competition_analysis.py` | 100 例统计分析 + CSV 导出 |
| `plot_competition.py` | 竞赛结果 7 张论文级图表 |
| `analyze_neighborhoods.py` | 邻域效率分析 |

---

## 二、实验数据交接

### 第三轮消融实验：`results/development_v3/`

| 目录 | 说明 | 规模 |
|------|------|:--:|
| `A0_v2_baseline/` | v2 基线 | 24 组 (6×P1/P2×N2/N4) |
| `A1_adaptive/` | 自适应预算 | 24 组 |
| `A2_final/` | 最终方案 | 24 组 + 图表 |
| `A2_final_p3/` | P3 (L2 Cache) | 12 组 (6×P3×N2/N4) |
| `A2_final_verified/` | CLI 复核版 | 24 组 |

### 竞赛实验结果：`results/competition/`

| 文件/目录 | 说明 |
|-----------|------|
| `benchmark.csv` | 180 行 (baseline/multiseed/vns × 60 组) |
| `singlecore.csv` | 15 例独立单核基线 |
| `per_case_improvement.csv` | 逐例改进率 |
| `aggregate_stats.csv` | 按 (problem, cores, algorithm) 汇总 |
| `REPORT.md` | Markdown 报告 |
| `summary_table.tex` | LaTeX 汇总表 |
| `figures/` | 7 张论文级矢量图（PDF+PNG，300DPI） |
| `raw_data/` | 原始 CSV 备份 |
| `RESULTS_INDEX.md` | 完整索引文件 |

### 核心统计数据

| 指标 | 值 |
|------|-----|
| 改善率 | 57/60 组改善（95.0%），3 组持平，0 退化 |
| P1 平均加速比（N=2） | ~1.70 |
| P1 平均加速比（N=4） | ~2.48 |
| P2 平均加速比（N=2） | ~1.79 |
| P2 平均加速比（N=4） | ~2.69 |
| VNS vs Multi-seed 增益 | 均值 3.03%（38/60 组） |
| 测试通过 | 49 passed，1.81s |

---

## 三、论文文件：`paper/`

| 文件 | 说明 |
|------|------|
| `main.tex` | 论文 LaTeX 源文件（完整正文 + 图表 + 附录） |
| `main.pdf` | 编译后的 PDF |
| `gmcmthesis.cls` | 竞赛官方模板类 |
| `gmcm.bst` | 参考文献格式 |
| `logo.png`, `title.png` | 封面图片 |
| `figures/*.pdf` | 全部论文用图表（15 张矢量 PDF） |
| `outline.md` | 章节大纲 |
| `SCHEDULE.md` | 时间规划 |
| `CHECKLIST.md` | 论文提交检查清单 |
| `references.bib` | 参考文献 BibTeX |

### 论文图表清单

| 图表 | 用途 |
|------|------|
| `ablation.pdf` | 消融实验 A0/A1/A2 柱状图 |
| `p1_speedup.pdf` | 问题 1 加速比折线图 |
| `p2_speedup.pdf` | 问题 2 加速比折线图 |
| `p3_speedup.pdf` | 问题 3 加速比折线图 |
| `p3_l2_comparison.pdf` | L2 Cache 对比 |
| `p3_same_plan_cache.pdf` | 同方案 L2 分析 |
| `runtime_quality.pdf` | 时间-质量散点图 |
| `improvement_histogram.pdf` | 竞赛改进率直方图 |
| `improvement_boxplot.pdf` | 按问题/核数箱线图 |
| `scale_improvement_bar.pdf` | 按规模分层改进率 |
| `top15_improvements.pdf` | Top 15 改善组 |
| `problem_comparison.pdf` | P1 vs P2 对比 |

---

## 四、论文编译方式

```bash
cd /d/BAKFILE/9017530/huawei_cup_2026/problem_A/paper
xelatex main.tex
xelatex main.tex    # 两次编译完成交叉引用
start main.pdf
```

编译环境要求：MiKTeX 已安装，隶书字体 SIMLI.TTF 已安装。

---

## 五、文档指引

| 文档 | 路径 |
|------|------|
| 选题可行性分析 | `docs/feasibility_analysis.md` |
| 文献综述框架 | `docs/literature_review_framework.md` |
| LaTeX 模板使用指引 | `docs/latex_template_guide.md` |
| AIGC 去痕全流程规范 | `docs/aigc_trace_removal_guide.md` |
| 学术写作规范体系 | `docs/academic_writing_standards.md` |
| 建模事实校正 | `docs/model_corrections.md` |
| 官方附件 | `官方附件md格式/` |

---

## 六、论文撰写注意事项

1. **遵守附件 2 格式规范**：题目三号黑体，一级标题四号黑体居中，正文小四宋体单倍行距，无页眉
2. **遵守附件 4 AI 使用规定**：附录 B 已写 AI 声明，完稿前补上最终版本号
3. **封面信息**：main.tex 中 `\baominghao{}`、`\schoolname{}`、`\membera/b/c{}` 需填写
4. **AIGC 去痕**：参考 `docs/aigc_trace_removal_guide.md`，重点清除"随着…发展""本文首先其次然后""显著/大幅/良好"等痕迹
5. **加速比数字**：100 例竞赛实验中 `singlecore_speedup_summary.csv` 是逐例平均加速比的权威来源

---

> 生成日期：2026-09-25
> 数据截止 commit：6aedc3c