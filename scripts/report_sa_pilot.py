# 本程序及代码是在人工智能工具辅助下完成的。
"""Compare control and SA-VNS outputs from the stage-one pilot."""
import argparse
import json
from pathlib import Path
import statistics


def load_arm(run_root, arm):
    records = {}
    arm_root = run_root / arm
    if not arm_root.is_dir():
        raise FileNotFoundError(f'Missing pilot arm directory: {arm_root}')
    for job_path in sorted(arm_root.glob('*/job.json')):
        job = json.loads(job_path.read_text(encoding='utf-8'))
        row = next((r for r in job['rows'] if r['algorithm'] == 'vns'), None)
        if row is None:
            raise ValueError(f'Missing VNS row in {job_path}')
        key = (row['case'], int(row['problem']), int(row['cores']))
        if key in records:
            raise ValueError(f'Duplicate pilot task in {arm}: {key}')
        uphill = 0
        trials_path = job_path.with_name('trials.jsonl')
        if not trials_path.exists():
            raise FileNotFoundError(f'Missing trials log: {trials_path}')
        for line in trials_path.read_text(encoding='utf-8').splitlines():
            trial = json.loads(line)
            uphill += bool(trial.get('accepted') and trial.get('accept_reason') == 'sa_uphill')
        records[key] = dict(
            makespan=int(row['makespan']),
            added_copy=int(row['added_copy_bytes']),
            uphill_accepted=uphill,
            evaluations=int(job['evaluator_calls']),
            runtime=float(job['total_seconds']),
        )
    return records


def build_report(run_root):
    control = load_arm(run_root, 'control')
    sa = load_arm(run_root, 'sa')
    if set(control) != set(sa):
        missing_control = sorted(set(sa) - set(control))
        missing_sa = sorted(set(control) - set(sa))
        raise ValueError(f'Pilot task mismatch; missing control={missing_control}, missing SA={missing_sa}')
    if not control:
        raise ValueError(f'No completed pilot tasks found in {run_root}')

    lines = [
        '| Task | control Makespan | SA Makespan | delta | control Added Copy | SA Added Copy | '
        'SA uphill accepted count | official evaluations (control/SA) | runtime s (control/SA) |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    relative_changes = []
    wins = ties = losses = 0
    worst_key = None
    worst_regression = 0.0
    for key in sorted(control):
        c = control[key]
        s = sa[key]
        delta = s['makespan'] - c['makespan']
        relative = delta / c['makespan']
        relative_changes.append(relative)
        if delta < 0:
            wins += 1
        elif delta == 0:
            ties += 1
        else:
            losses += 1
            if worst_key is None or relative > worst_regression:
                worst_key = key
                worst_regression = relative
        task = f'{key[0]} P{key[1]} N{key[2]}'
        lines.append(
            f"| {task} | {c['makespan']} | {s['makespan']} | {delta:+d} | "
            f"{c['added_copy']} | {s['added_copy']} | {s['uphill_accepted']} | "
            f"{c['evaluations']}/{s['evaluations']} | {c['runtime']:.3f}/{s['runtime']:.3f} |"
        )

    worst_label = 'none'
    if worst_key is not None:
        worst_label = f'{worst_key[0]} P{worst_key[1]} N{worst_key[2]} ({worst_regression:+.4%})'
    lines += [
        '',
        f'wins / ties / losses: {wins} / {ties} / {losses}',
        f'mean relative Makespan change: {statistics.mean(relative_changes):+.4%}',
        f'worst regression: {worst_label}',
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-root', type=Path, required=True)
    args = parser.parse_args()
    print(build_report(args.run_root.resolve()))
