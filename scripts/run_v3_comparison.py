# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Development v3 comparison: A0 (baseline v2) vs A1 (adaptive) vs A2 (+recovered v1) vs A3 (combined)."""
import argparse
import json
import statistics
from pathlib import Path
import subprocess
import sys
import time


def run_config(name, config_path, outdir, cases, problems, cores, data_dir, hw_config):
    """Run benchmark with a specific solver config."""
    start = time.perf_counter()
    cmd = [
        sys.executable, '-m', 'npu_scheduler.cli', 'benchmark',
        '--data-dir', str(data_dir),
        '--config', str(hw_config),
        '--solver-config', str(config_path),
        '--output', str(outdir),
        '--cases', *cases,
        '--problem', *map(str, problems),
        '--cores', *map(str, cores),
        '--skip-cli-verification'
    ]
    print(f'[{name}] Running: {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parents[1]))
    elapsed = time.perf_counter() - start
    print(f'[{name}] {result.stdout}')
    if result.stderr:
        print(f'[{name}] STDERR: {result.stderr}', file=sys.stderr)
    return elapsed


def compare_results(results_dir, output):
    """Compare A0-A3 results and produce report."""
    rows = []
    configs = ['A0_v2_baseline', 'A1_adaptive_budget', 'A2_recovered_v1', 'A3_combined']
    all_data = {}
    for cfg in configs:
        csv_path = results_dir / cfg / 'benchmark.csv'
        if csv_path.exists():
            text = csv_path.read_text(encoding='utf-8')
            parsed = []
            for line in text.strip().split('\n')[1:]:  # skip header
                parts = line.strip().split(',')
                if len(parts) >= 7:
                    parsed.append(dict(case=parts[0], problem=int(parts[1]), cores=int(parts[2]),
                                       algorithm=parts[3], makespan=int(parts[4]),
                                       added_copy=int(parts[5]), spill=int(parts[6]),
                                       cache_rate=float(parts[7]), runtime=float(parts[8]),
                                       evaluations=int(parts[9]), source=parts[10], scale=parts[11]))
            all_data[cfg] = parsed

    if len(all_data) < 2:
        print("Not enough configs completed for comparison")
        return

    # Compare VNS results across configs
    report = ['# Development v3 Comparison Report', '']
    report.append('## A0 (v2 baseline) vs A1 (adaptive) vs A2 (+recovered v1) vs A3 (combined)')
    report.append('')
    report.append('| Case | P | N | A0 Makespan | A1 Makespan | A2 Makespan | A3 Makespan | A1 vs A0 | A2 vs A0 | A3 vs A0 |')
    report.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')

    improvements = {c: [] for c in configs[1:]}

    for case in sorted(set(r['case'] for r in all_data[configs[0]])):
        for p in [1, 2, 3]:
            for n in [2, 4]:
                vns = {}
                for cfg in configs:
                    matches = [r for r in all_data.get(cfg, [])
                               if r['case'] == case and r['problem'] == p and r['cores'] == n and r['algorithm'] == 'vns']
                    vns[cfg] = matches[0]['makespan'] if matches else None

                if vns[configs[0]] is not None:
                    a0 = vns[configs[0]]
                    diffs = []
                    for cfg in configs[1:]:
                        if vns[cfg] is not None:
                            pct = (a0 - vns[cfg]) / a0 * 100
                            diffs.append(f'{pct:+.1f}%')
                            improvements[cfg].append(pct)
                        else:
                            diffs.append('N/A')
                    report.append(f'| {case} | {p} | {n} | {a0} | {vns.get(configs[1], "N/A")} | '
                                  f'{vns.get(configs[2], "N/A")} | {vns.get(configs[3], "N/A")} | '
                                  f'{diffs[0]} | {diffs[1]} | {diffs[2]} |')

    report.append('')
    report.append('## Summary')
    report.append('')
    for cfg in configs[1:]:
        imps = improvements[cfg]
        if imps:
            report.append(f'### {cfg}')
            report.append(f'- Mean improvement vs A0: {statistics.mean(imps):+.1f}%')
            report.append(f'- Median improvement vs A0: {statistics.median(imps):+.1f}%')
            report.append(f'- Improved: {sum(1 for x in imps if x > 0)} / Tied: {sum(1 for x in imps if x == 0)} / '
                          f'Regressed: {sum(1 for x in imps if x < 0)}')
            report.append(f'- Worst regression: {min(imps):+.1f}%')
            report.append('')

    report_path = Path(output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text('\n'.join(report), encoding='utf-8')
    print(f'Report written to {report_path}')


def main():
    parser = argparse.ArgumentParser(description='Run A0-A3 comparison')
    parser.add_argument('--output', type=Path, default=Path('results/development_v3'))
    parser.add_argument('--cases', nargs='+', default=None)
    parser.add_argument('--problems', type=int, nargs='+', default=[1, 2])
    parser.add_argument('--cores', type=int, nargs='+', default=[2, 4])
    parser.add_argument('--skip-benchmark', action='store_true')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    data_dir = root / 'data'
    hw_config = root / 'data' / 'config.txt'

    # Load extended cases
    if args.cases is None:
        yaml_path = root / 'configs' / 'development_cases.yaml'
        if yaml_path.exists():
            import yaml
            cases = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))['development_cases']
        else:
            cases = ['case_001', 'case_019', 'case_005', 'case_050', 'case_025', 'case_085']
    else:
        cases = args.cases

    configs = {
        'A0_v2_baseline': root / 'configs' / 'default.yaml',
        'A1_adaptive_budget': root / 'configs' / 'development_v3.yaml',
        'A2_recovered_v1': root / 'configs' / 'development_v3.yaml',
        'A3_combined': root / 'configs' / 'development_v3.yaml',
    }

    if not args.skip_benchmark:
        for name, cfg_path in configs.items():
            outdir = args.output / name
            outdir.mkdir(parents=True, exist_ok=True)
            run_config(name, cfg_path, outdir, cases, args.problems, args.cores, data_dir, hw_config)

    compare_results(args.output, args.output / 'COMPARISON_REPORT.md')


if __name__ == '__main__':
    main()