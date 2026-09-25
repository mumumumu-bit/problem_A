# 本程序及代码是在人工智能工具辅助下完成的。
"""Complete statistical analysis of 100-case competition benchmark for paper."""
import csv
import json
import statistics
from pathlib import Path

COMPETITION_DIR = Path(__file__).resolve().parents[1] / 'results' / 'competition'
PAPER_DIR = Path(__file__).resolve().parents[1] / 'paper'

def load_benchmark(directory):
    rows = list(csv.DictReader((directory / 'benchmark.csv').open(encoding='utf-8')))
    for r in rows:
        for f in ('problem', 'cores', 'makespan', 'added_copy_bytes', 'spill_bytes', 'evaluations'):
            r[f] = int(r[f])
        r['runtime'] = float(r['runtime'])
    return rows

def compute_stats(rows):
    """Compute per (problem, cores, algorithm) aggregate statistics."""
    by_key = {}
    for r in rows:
        key = (r['problem'], r['cores'], r['algorithm'])
        by_key.setdefault(key, []).append(r['makespan'])

    stats = []
    for (p, n, alg), vals in by_key.items():
        # Baseline for improvement
        baseline_vals = [r['makespan'] for r in rows
                         if r['problem'] == p and r['cores'] == n and r['algorithm'] == 'baseline'
                         and r['case'] in {rr['case'] for rr in rows
                                            if rr['problem'] == p and rr['cores'] == n and rr['algorithm'] == alg}]
        improvements = [100 * (1 - v / b) for v, b in zip(vals, baseline_vals)] if baseline_vals else []
        stats.append({
            'problem': p, 'cores': n, 'algorithm': alg, 'count': len(vals),
            'mean': statistics.mean(vals), 'median': statistics.median(vals),
            'min': min(vals), 'max': max(vals),
            'stdev': statistics.stdev(vals) if len(vals) > 1 else 0,
            'mean_improvement_pct': statistics.mean(improvements) if improvements else None,
            'median_improvement_pct': statistics.median(improvements) if improvements else None,
        })

    # Per-case improvement
    per_case = []
    by_case = {}
    for r in rows:
        by_case.setdefault((r['case'], r['problem'], r['cores']), {})[r['algorithm']] = r['makespan']

    for (case, p, n), algs in by_case.items():
        b = algs.get('baseline')
        m = algs.get('multiseed')
        v = algs.get('vns')
        if b and v:
            per_case.append({
                'case': case, 'problem': p, 'cores': n,
                'baseline': b, 'multiseed': m, 'vns': v,
                'total_improvement_pct': 100 * (1 - v / b),
                'vns_vs_multiseed_pct': 100 * (1 - v / m) if m and v else 0,
            })

    return stats, per_case

def write_stats_csv(stats, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['problem', 'cores', 'algorithm', 'count', 'mean', 'median',
                                           'min', 'max', 'stdev', 'mean_improvement_pct', 'median_improvement_pct'])
        w.writeheader()
        w.writerows(stats)

def write_per_case_csv(per_case, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['case', 'problem', 'cores', 'baseline', 'multiseed', 'vns',
                                           'total_improvement_pct', 'vns_vs_multiseed_pct'])
        w.writeheader()
        w.writerows(sorted(per_case, key=lambda x: (x['case'], x['problem'], x['cores'])))

def generate_latex_summary_table(stats, per_case):
    """Generate a LaTeX summary table for the paper."""
    lines = [r'\begin{table}[!h]', r'\centering',
             r'\caption{100 例竞赛实验汇总统计（A2 配置，300s/64evals）}',
             r'\label{tab:competition_summary}',
             r'\small', r'\begin{tabular}{l c rrrr r}',
             r'\toprule',
             r'\textbf{场景} & \textbf{核心数} & \textbf{算例数} & \textbf{平均Makespan} & \textbf{中位数} & \textbf{标准差} & \textbf{平均改善率} \\',
             r'\midrule']

    for s in stats:
        if s['algorithm'] != 'vns':
            continue
        label = f"P{s['problem']}"
        lines.append(f"{label} & {s['cores']} & {s['count']} & {s['mean']:,.0f} & {s['median']:,.0f} & {s['stdev']:,.0f} & {s['mean_improvement_pct']:.1f}\\% \\\\")

    lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    return '\n'.join(lines)

def generate_improvement_distribution(per_case):
    """Generate improvement distribution statistics."""
    dist = {'improved': 0, 'tied': 0, 'regressed': 0}
    for r in per_case:
        if r['total_improvement_pct'] > 0.5:
            dist['improved'] += 1
        elif r['total_improvement_pct'] < -0.5:
            dist['regressed'] += 1
        else:
            dist['tied'] += 1
    return dist

def main():
    rows = load_benchmark(COMPETITION_DIR)
    print(f"Loaded {len(rows)} benchmark rows")

    stats, per_case = compute_stats(rows)
    print(f"Computed stats for {len(stats)} (problem, cores, algorithm) groups")
    print(f"Per-case data: {len(per_case)} entries")

    # Write CSVs
    write_stats_csv(stats, COMPETITION_DIR / 'aggregate_stats.csv')
    write_per_case_csv(per_case, COMPETITION_DIR / 'per_case_improvement.csv')
    print("CSVs written")

    # Generate LaTeX table
    latex_table = generate_latex_summary_table(stats, per_case)
    (COMPETITION_DIR / 'summary_table.tex').write_text(latex_table, encoding='utf-8')
    print("LaTeX table written")

    # Improvement distribution
    dist = generate_improvement_distribution(per_case)
    total = len(per_case)
    print(f"\n=== Improvement Distribution (all {total} groups) ===")
    print(f"Improved:  {dist['improved']} ({100*dist['improved']/total:.1f}%)")
    print(f"Tied:      {dist['tied']} ({100*dist['tied']/total:.1f}%)")
    print(f"Regressed: {dist['regressed']} ({100*dist['regressed']/total:.1f}%)")

    # Per-problem breakdown
    for p in [1, 2]:
        group = [r for r in per_case if r['problem'] == p]
        impr = [r['total_improvement_pct'] for r in group]
        print(f"\n=== Problem {p} ({len(group)} groups) ===")
        print(f"Mean improvement: {statistics.mean(impr):.2f}%")
        print(f"Median improvement: {statistics.median(impr):.2f}%")
        if len(impr) > 1:
            print(f"Stdev: {statistics.stdev(impr):.2f}%")
        print(f"Min: {min(impr):.2f}%  Max: {max(impr):.2f}%")

        # By cores
        for n in [2, 4]:
            ng = [r for r in group if r['cores'] == n]
            ni = [r['total_improvement_pct'] for r in ng]
            if ni:
                print(f"  N={n}: mean improvement = {statistics.mean(ni):.2f}% (n={len(ng)})")

    # Scale analysis
    print("\n=== By Scale (case number proxy) ===")
    for label, cases in [
        ("001-020 (small)", [r for r in per_case if 1 <= int(r['case'].split('_')[1]) <= 20]),
        ("021-050 (medium)", [r for r in per_case if 21 <= int(r['case'].split('_')[1]) <= 50]),
        ("051-080 (large)", [r for r in per_case if 51 <= int(r['case'].split('_')[1]) <= 80]),
        ("081-100 (xlarge)", [r for r in per_case if 81 <= int(r['case'].split('_')[1]) <= 100]),
    ]:
        if cases:
            impr = [r['total_improvement_pct'] for r in cases]
            print(f"  {label}: mean={statistics.mean(impr):.2f}%, n={len(cases)}")

    # Top/bottom 5
    by_impr = sorted(per_case, key=lambda r: r['total_improvement_pct'], reverse=True)
    print("\n=== Top 5 improvements ===")
    for r in by_impr[:5]:
        print(f"  {r['case']} P{r['problem']} N{r['cores']}: {r['total_improvement_pct']:.2f}% (baseline={r['baseline']:,} → vns={r['vns']:,})")

    print("\n=== Bottom 5 (worst regression) ===")
    for r in by_impr[-5:]:
        print(f"  {r['case']} P{r['problem']} N{r['cores']}: {r['total_improvement_pct']:.2f}% (baseline={r['baseline']:,} → vns={r['vns']:,})")

    # VNS vs Multi-seed
    vns_gain = [r['vns_vs_multiseed_pct'] for r in per_case if r['vns_vs_multiseed_pct'] > 0.01]
    print(f"\n=== VNS vs Multi-seed ===")
    print(f"Groups with VNS improvement: {len(vns_gain)}/{len(per_case)}")
    if vns_gain:
        print(f"Mean VNS gain: {statistics.mean(vns_gain):.2f}%")

    # Added copy analysis
    added = [(r['case'], r['problem'], r['cores'], r['total_improvement_pct']) for r in per_case]
    print(f"\n=== Summary ===")
    print(f"Total cases analyzed: {len(set(r['case'] for r in per_case))}")
    print(f"All files written to {COMPETITION_DIR}")

if __name__ == '__main__':
    main()