# 论文结果溯源审计
## 生成时间: 2026-09-25

---

## 数字溯源表

| 论文位置 (main.tex) | 论文数字 | 来源文件 | 计算方式 | 状态 |
|---|---|---|---|---|
| L334 | "100例竞赛实验" | results/competition/manifest.json | 实际仅15个case | **UNVERIFIED** — 标题声称100例，实验仅15例 |
| L334 | "60组实验" | results/competition/REPORT.md | 15×P1/P2×N2/N4 | **VERIFIED** |
| L334 | 改善率 95.0% (57/60) | results/competition/REPORT.md | VNS vs Baseline | **VERIFIED** |
| L334 | P1 平均改善 31.94% | results/competition/REPORT.md | 30组均值 | **VERIFIED** |
| L334 | P2 平均改善 20.98% | results/competition/REPORT.md | 30组均值 | **VERIFIED** |
| L334 | N=4 平均收益 30.56% | results/competition/REPORT.md | 30组均值 | **VERIFIED** |
| L339 | 均值 26.46%, 中位 23.51% | results/competition/REPORT.md | 60组均值/中位数 | **VERIFIED** (均值), **OUTDATED** (中位数: REPORT实际报告22.58%) |
| L294 | P1 N=4 加速比 2.42 | paper/main.tex | 6例开发集(A2_final) | **OUTDATED** — 竞赛15例实际=2.478 |
| L294 | P2 N=4 加速比 2.89 | paper/main.tex | 6例开发集(A2_final) | **OUTDATED** — 竞赛15例实际=2.753 |
| L294 | P1 N=2 加速比 1.54 | paper/main.tex | 6例开发集(A2_final) | **OUTDATED** — 竞赛15例实际=1.636 |
| L294 | P2 N=2 加速比 1.72 | paper/main.tex | 6例开发集(A2_final) | **OUTDATED** — 竞赛15例实际=1.723 |
| L249 | A2 消融 10/24 改善 | A2_final/REPORT.md | VNS vs Multi-seed | **VERIFIED** |
| L27 | A2 vs 基线 降低 17.74% | A2_final/REPORT.md | 6例24组均值 | **VERIFIED** |
| L362 | VNS增益 3.03% (38/60) | results/competition/REPORT.md | competition 60组 | **VERIFIED** |
| L365 | case_069 P1/N4 76.73% | results/competition/REPORT.md | 竞赛best case | **VERIFIED** |
| L27 | DAG ops 766-38,666 | 无 | 数据集描述 | **VERIFIED** (来自dataset_audit.csv) |
| L403 | L2加速比 1.00007-1.004 | 无独立实验 | 估算 | **UNVERIFIED** — 无独立受控Cache消融实验 |
| L334 | "400组" | 无 | 计算: 100×P1/P2×N2/N4 | **PLACEHOLDER** — 实际不存在 |

## 关键矛盾

### 矛盾 1: "100例" vs 真实 15 例
- 论文多次写 "100例正式实验"、"100例竞赛实验"
- 实际: 所有结果来自 15 个代表 case，最多 60 组
- **100 个全量 case 数据文件存在，但实验从未运行**

### 矛盾 2: 加速比数字
- 论文 L294 的加速比 (P1/N4=2.42, P2/N4=2.89) 来自 **6例开发集 A2_final**
- 竞赛 REPORT 的加速比 (P1/N4=2.478, P2/N4=2.753) 来自 **15例竞赛实验**
- 两者不一致且来源不同

### 矛盾 3: 中位数
- 论文 L339 写中位数 23.51%
- RESULTS_INDEX.md 报告中位数 22.58%
- REPORT.md 未报告中位数

## 状态标记汇总
- VERIFIED: 11项
- OUTDATED: 4项
- UNVERIFIED: 2项
- PLACEHOLDER: 1项

## 结论
论文中约 1/3 的数字来自**旧版 6 例开发实验**而非**15 例竞赛实验**。"100例"和"400组"的说法**没有实验支撑**。