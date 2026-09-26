# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：Trae AI Coding Assistant (ByteDance)
"""竞赛图表生成 —— 委托统一的 style.py 渲染中枢。"""
import csv
import json
import shutil
import statistics
from pathlib import Path
import numpy as np

# ── 路径与数据 ──────────────────────────────────────────────────────
COMP_DIR = Path(__file__).resolve().parents[1] / 'results' / 'competition'
FIG_DIR = COMP_DIR / 'figures'
RAW_DIR = COMP_DIR / 'raw_data'
for d in [FIG_DIR, RAW_DIR]:
    d.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader((COMP_DIR / 'benchmark.csv').open(encoding='utf-8')))
for r in rows:
    for f in ('problem', 'cores', 'makespan', 'added_copy_bytes', 'spill_bytes', 'evaluations'):
        r[f] = int(r[f])
    r['runtime'] = float(r['runtime'])

per_case = list(csv.DictReader((COMP_DIR / 'per_case_improvement.csv').open(encoding='utf-8')))
for r in per_case:
    for f in ('problem', 'cores', 'baseline', 'multiseed', 'vns'):
        r[f] = int(r[f])
    r['total_improvement_pct'] = float(r['total_improvement_pct'])
    r['vns_vs_multiseed_pct'] = float(r['vns_vs_multiseed_pct'])

# ── 统一渲染中枢 ────────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from npu_scheduler.visualization.style import (
    apply_style, save as save_fig, PROBLEM_COLORS, SCALE_COLORS,
    label_bars, label_hbars, stat_vlines,
)

plt = apply_style()

# ── 辅助 ────────────────────────────────────────────────────────────
def save(fig, name):
    """输出到 FIG_DIR，同时关闭 figure。"""
    save_fig(fig, FIG_DIR, name)
    plt.close(fig)

# ================================================================
# Figure 1: 改善率分布直方图
# ================================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
improvements = [r['total_improvement_pct'] for r in per_case]
bins = np.linspace(0, 80, 17)
ax.hist(improvements, bins=bins, color='#4C78A8', edgecolor='white', alpha=0.85)
stat_vlines(ax, improvements)
ax.set_xlabel('Makespan改善率 vs 负载均衡初解 (%)')
ax.set_ylabel('实验组数（case × 问题 × 核心数）')
ax.set_title('60组实验改善率分布（15 case, P1/P2, N=2/4）')
ax.legend(loc='upper left')
save(fig, 'improvement_histogram')

# ================================================================
# Figure 2: 问题×核心数 箱线图
# ================================================================
fig, ax = plt.subplots(figsize=(8, 5))
data_groups, labels_list, colors_list = [], [], []
for p in [1, 2]:
    for n in [2, 4]:
        vals = [r['total_improvement_pct'] for r in per_case
                if r['problem'] == p and r['cores'] == n]
        data_groups.append(vals)
        labels_list.append(f'P{p} N={n}')
        colors_list.append(PROBLEM_COLORS[f'P{p}_N{n}'])

bp = ax.boxplot(data_groups, tick_labels=labels_list, patch_artist=True, widths=0.5,
                medianprops={'color': 'black', 'linewidth': 1.5},
                flierprops={'marker': 'o', 'markersize': 4, 'alpha': 0.5})
for patch, c in zip(bp['boxes'], colors_list):
    patch.set_facecolor(c)
    patch.set_alpha(0.7)
ax.set_xlabel('问题与核心数')
ax.set_ylabel('Makespan改善率 vs 负载均衡初解 (%)')
ax.set_title('不同问题与核心数下的改善率分布')
ax.grid(axis='y', alpha=0.3)
save(fig, 'improvement_boxplot')

# ================================================================
# Figure 3: 图规模改善率柱状图
# ================================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
scale_data = [
    ('极小图\n(<1k ops)', [r for r in per_case if 1 <= int(r['case'].split('_')[1]) <= 10]),
    ('小图\n(1k-2k)',    [r for r in per_case if 11 <= int(r['case'].split('_')[1]) <= 30]),
    ('中图\n(2k-10k)',   [r for r in per_case if 31 <= int(r['case'].split('_')[1]) <= 60]),
    ('大图\n(10k-20k)',  [r for r in per_case if 61 <= int(r['case'].split('_')[1]) <= 80]),
    ('超大图\n(>20k)',   [r for r in per_case if 81 <= int(r['case'].split('_')[1]) <= 100]),
]
scale_names = [s[0] for s in scale_data]
scale_means = [statistics.mean([r['total_improvement_pct'] for r in s[1]]) if s[1] else 0
               for s in scale_data]
scale_colors_list = [SCALE_COLORS[k] for k in ['xsmall', 'small', 'medium', 'large', 'xlarge']]
bars = ax.bar(range(len(scale_names)), scale_means, color=scale_colors_list,
              edgecolor='white', width=0.6)
label_bars(ax, bars, offset=0.5)
ax.set_xticks(range(len(scale_names))); ax.set_xticklabels(scale_names)
ax.set_xlabel('图规模类别')
ax.set_ylabel('平均Makespan改善率 (%)')
ax.set_title('不同图规模下的改善率')
ax.set_ylim(0, max(scale_means) * 1.2)
ax.grid(axis='y', alpha=0.3)
save(fig, 'scale_improvement_bar')

# ================================================================
# Figure 4: VNS vs 多初解 增益散点图
# ================================================================
fig, ax = plt.subplots(figsize=(8, 5))
vns_gains = [r['vns_vs_multiseed_pct'] for r in per_case]
multiseed_impr = [100 * (1 - r['multiseed'] / r['baseline']) for r in per_case]
ax.scatter(multiseed_impr, vns_gains, c='#4C78A8', alpha=0.6, s=30,
           edgecolors='white', linewidth=0.5)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('多初解改善率 vs 负载均衡初解 (%)')
ax.set_ylabel('VNS相对多初解的增益 (%)')
improved = sum(1 for g in vns_gains if g > 0.01)
ax.set_title(f'VNS vs 多初解：{improved}/{len(vns_gains)} 组有增益')
ax.grid(alpha=0.3)
save(fig, 'vns_vs_multiseed_scatter')

# ================================================================
# Figure 5: Top 15 改善率排名（水平柱状图）
# ================================================================
fig, ax = plt.subplots(figsize=(8, 6))
sorted_cases = sorted(per_case, key=lambda r: r['total_improvement_pct'], reverse=True)[:15]
case_labels = [f"{r['case']} P{r['problem']} N{r['cores']}" for r in sorted_cases]
case_vals = [r['total_improvement_pct'] for r in sorted_cases]
case_colors_list = [PROBLEM_COLORS[f'P{r["problem"]}_N{r["cores"]}'] for r in sorted_cases]

bars_h = ax.barh(range(len(case_labels)), case_vals, color=case_colors_list,
                 edgecolor='white', height=0.7)
label_hbars(ax, bars_h, colors=case_colors_list)
ax.set_yticks(range(len(case_labels)))
ax.set_yticklabels(case_labels, fontsize=8)
ax.set_xlabel('Makespan改善率 (%)')
ax.set_ylabel('实验组（case × 问题 × 核心数）')
ax.set_title('Top 15 改善率排名')
ax.invert_yaxis(); ax.grid(axis='x', alpha=0.3)
save(fig, 'top15_improvements')

# ================================================================
# Figure 6: 问题1 vs 问题2 对比（柱状图 + 误差棒 + 散点）
# ================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
for p, ax, title in [(1, ax1, '问题 1'), (2, ax2, '问题 2')]:
    for n, color, pos in [(2, PROBLEM_COLORS[f'P{p}_N2'], 0),
                           (4, PROBLEM_COLORS[f'P{p}_N4'], 1)]:
        group = [r for r in per_case if r['problem'] == p and r['cores'] == n]
        vals = [r['total_improvement_pct'] for r in group]
        bar_val = statistics.mean(vals)
        bar = ax.bar(pos, bar_val, color=color, width=0.5, edgecolor='white')
        ax.text(pos, bar_val + 1.0, f'{bar_val:.1f}%', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=color)
        if len(vals) > 1:
            ax.errorbar(pos, bar_val, yerr=statistics.stdev(vals),
                        fmt='none', ecolor='black', capsize=5, linewidth=1)
        jitter = np.random.default_rng(2026).uniform(-0.15, 0.15, len(vals))
        ax.scatter([pos]*len(vals) + jitter, vals, c='black', alpha=0.3, s=10, zorder=3)
    ax.set_xticks([0, 1]); ax.set_xticklabels(['N=2', 'N=4'])
    ax.set_xlabel('核心数')
    ax.set_ylabel('平均改善率 (%)')
    ax.set_title(title); ax.grid(axis='y', alpha=0.3)
fig.suptitle('改善率分布：问题 1 vs 问题 2', fontsize=12)
plt.tight_layout()
save(fig, 'problem_comparison')

# ================================================================
# Figure 7: 评估函数调用次数分布
# ================================================================
fig, ax = plt.subplots(figsize=(8, 4))
eval_calls = [r['evaluations'] for r in rows if r['algorithm'] == 'vns']
ax.hist(eval_calls, bins=20, color='#54A24B', edgecolor='white', alpha=0.85)
ax.axvline(statistics.mean(eval_calls), color='#E45756', linestyle='--',
           label=f'均值 = {statistics.mean(eval_calls):.1f}')
ax.set_xlabel('每组评估函数调用次数')
ax.set_ylabel('组数')
ax.set_title('评估函数调用分布（最多64次, 预算300秒）')
ax.legend()
save(fig, 'evaluator_calls')

# ================================================================
# 备份原始数据 + 生成索引
# ================================================================
for f in ['benchmark.csv', 'per_case_improvement.csv', 'aggregate_stats.csv',
          'singlecore.csv', 'summary.csv', 'comparison.csv']:
    src = COMP_DIR / f
    if src.exists():
        shutil.copy2(src, RAW_DIR / f)

index_lines = [
    '# Competition Results Index',
    'Generated: 2026-09-25',
    '',
    '## Figures',
    '',
]
fig_files = sorted(FIG_DIR.glob('*.pdf'))
for f in fig_files:
    name = f.stem
    desc = {
        'improvement_histogram': '改善率分布直方图',
        'improvement_boxplot': '问题×核心数箱线图',
        'scale_improvement_bar': '图规模改善率柱状图',
        'vns_vs_multiseed_scatter': 'VNS增益散点图',
        'top15_improvements': 'Top 15 改善率排名',
        'problem_comparison': '问题1 vs 问题2 对比',
        'evaluator_calls': '评估函数调用次数分布',
    }.get(name, '')
    index_lines.append(f'- `figures/{f.name}`: {desc}')

overall_impr = [r['total_improvement_pct'] for r in per_case]
index_lines += [
    '',
    '## 关键统计',
    f'- 平均改善率: {statistics.mean(overall_impr):.2f}%',
    f'- 中位数: {statistics.median(overall_impr):.2f}%',
    f'- 改善组数: {sum(1 for r in per_case if r["total_improvement_pct"] > 0.5)}/60',
    f'- 持平: {sum(1 for r in per_case if abs(r["total_improvement_pct"]) <= 0.5)}/60',
    f'- 退化: {sum(1 for r in per_case if r["total_improvement_pct"] < -0.5)}/60',
]
(COMP_DIR / 'RESULTS_INDEX.md').write_text('\n'.join(index_lines), encoding='utf-8')

print(f"Generated {len(fig_files)} figures in {FIG_DIR}")
print(f"Raw data backed up to {RAW_DIR}")
print("Done.")