# 本程序及代码是在人工智能工具辅助下完成的。
"""Report the fixed-seed SA cross-case expansion study."""
import argparse
import json
from pathlib import Path
import statistics


TRADEOFF_NOTE = 'small makespan gain with substantial added-copy increase'
NEAR_ZERO = 0.0005


def load_arm(run_root, arm):
    records = {}
    arm_root = run_root / arm
    if not arm_root.is_dir():
        raise FileNotFoundError(f'Missing expansion arm directory: {arm_root}')
    for job_path in sorted(arm_root.rglob('job.json')):
        job = json.loads(job_path.read_text(encoding='utf-8'))
        row = next((item for item in job['rows'] if item['algorithm'] == 'vns'), None)
        if row is None:
            raise ValueError(f'Missing VNS row in {job_path}')
        key = (row['case'], int(row['problem']), int(row['cores']))
        if key in records:
            raise ValueError(f'Duplicate expansion task in {arm}: {key}')
        trials_path = job_path.with_name('trials.jsonl')
        if not trials_path.exists():
            raise FileNotFoundError(f'Missing trials log: {trials_path}')
        uphill = 0
        for line in trials_path.read_text(encoding='utf-8').splitlines():
            trial = json.loads(line)
            uphill += bool(trial.get('accepted') and trial.get('accept_reason') == 'sa_uphill')
        records[key] = dict(
            makespan=int(row['makespan']),
            added_copy=int(row['added_copy_bytes']),
            evaluator_calls=int(job['evaluator_calls']),
            runtime=float(job['total_seconds']),
            uphill_accepted=uphill,
        )
    return records


def copy_diagnostics(control, sa):
    improvement = (control['makespan'] - sa['makespan']) / control['makespan']
    copy_delta = sa['added_copy'] - control['added_copy']
    copy_relative = None
    if control['added_copy'] > 0:
        copy_relative = copy_delta / control['added_copy']
    from_zero = control['added_copy'] == 0 and sa['added_copy'] > 0
    substantial = from_zero or (copy_relative is not None and copy_relative > 0.5)

    if copy_delta <= 0:
        risk = 'low'
    elif improvement >= 0.005:
        risk = 'moderate'
    elif substantial:
        risk = 'high'
    else:
        risk = 'moderate'
    note = TRADEOFF_NOTE if 0 < improvement < 0.005 and substantial else ''
    return dict(copy_delta=copy_delta, copy_risk=risk, tradeoff_note=note)


def classify_signal(wins, losses, mean_relative, high_copy_risks):
    if wins >= 3 and losses == 0 and mean_relative < 0 and high_copy_risks <= wins / 2:
        return 'strong signal'
    if wins >= 2 and losses <= 1 and mean_relative < 0:
        return 'moderate signal'
    if mean_relative > 0 or (losses > 0 and losses >= wins):
        return 'negative signal'
    if wins == 1 or abs(mean_relative) <= NEAR_ZERO:
        return 'weak signal'
    return 'weak signal'


def classify_copy_concern(rows):
    high = sum(row['copy_risk'] == 'high' for row in rows)
    non_low = sum(row['copy_risk'] != 'low' for row in rows)
    if high >= 4:
        return 'high'
    if high >= 2 or non_low:
        return 'moderate'
    return 'low'


def collect_rows(run_root):
    control = load_arm(run_root, 'control')
    sa = load_arm(run_root, 'sa')
    if set(control) != set(sa):
        raise ValueError(f'Expansion task mismatch: control={sorted(control)}, SA={sorted(sa)}')
    if not control:
        raise ValueError(f'No completed expansion tasks found in {run_root}')
    rows = []
    for task in sorted(control):
        c, s = control[task], sa[task]
        delta = s['makespan'] - c['makespan']
        row = dict(
            task=task,
            control=c,
            sa=s,
            makespan_delta=delta,
            makespan_relative=delta / c['makespan'],
            result='win' if delta < 0 else 'loss' if delta > 0 else 'tie',
        )
        row.update(copy_diagnostics(c, s))
        rows.append(row)
    return rows


def extreme(values, mode):
    value = min(values) if mode == 'best' else max(values)
    if mode == 'best' and value >= 0:
        return 'none'
    if mode == 'worst' and value <= 0:
        return 'none'
    return f'{value:+.4%}'


def build_report(run_root):
    rows = collect_rows(run_root)
    lines = [
        '| Task | result | control Makespan | SA Makespan | Makespan delta | Makespan relative delta | '
        'control Added Copy | SA Added Copy | Added Copy delta | control calls | SA calls | call delta | '
        'control runtime | SA runtime | runtime delta | SA uphill accepted | copy_risk | tradeoff_note |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|',
    ]
    for row in rows:
        case, problem, cores = row['task']
        c, s = row['control'], row['sa']
        lines.append(
            f"| {case} P{problem} N{cores} | {row['result']} | {c['makespan']} | {s['makespan']} | "
            f"{row['makespan_delta']:+d} | {row['makespan_relative']:+.4%} | {c['added_copy']} | "
            f"{s['added_copy']} | {row['copy_delta']:+d} | {c['evaluator_calls']} | "
            f"{s['evaluator_calls']} | {s['evaluator_calls'] - c['evaluator_calls']:+d} | "
            f"{c['runtime']:.3f} | {s['runtime']:.3f} | {s['runtime'] - c['runtime']:+.3f} | "
            f"{s['uphill_accepted']} | {row['copy_risk']} | {row['tradeoff_note'] or '-'} |"
        )

    relative = [row['makespan_relative'] for row in rows]
    wins = sum(row['result'] == 'win' for row in rows)
    ties = sum(row['result'] == 'tie' for row in rows)
    losses = sum(row['result'] == 'loss' for row in rows)
    high_count = sum(row['copy_risk'] == 'high' for row in rows)
    mean_relative = statistics.mean(relative)
    lines += [
        '',
        '## Overall summary',
        '',
        f'wins: {wins}',
        f'ties: {ties}',
        f'losses: {losses}',
        f'win rate: {wins / len(rows):.2%}',
        f'mean relative Makespan change: {mean_relative:+.4%}',
        f'median relative Makespan change: {statistics.median(relative):+.4%}',
        f'best Makespan improvement: {extreme(relative, "best")}',
        f'worst Makespan regression: {extreme(relative, "worst")}',
        f'mean Added Copy delta: {statistics.mean(row["copy_delta"] for row in rows):+.2f}',
        f'high copy-risk count: {high_count}',
        f'total SA uphill accepted: {sum(row["sa"]["uphill_accepted"] for row in rows)}',
        f'mean evaluator call delta: '
        f'{statistics.mean(row["sa"]["evaluator_calls"] - row["control"]["evaluator_calls"] for row in rows):+.2f}',
        f'mean runtime delta: '
        f'{statistics.mean(row["sa"]["runtime"] - row["control"]["runtime"] for row in rows):+.3f}',
        '',
        '## Factual diagnosis',
        '',
        f'signal: {classify_signal(wins, losses, mean_relative, high_count)}',
        f'copy concern: {classify_copy_concern(rows)}',
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-root', type=Path, required=True)
    args = parser.parse_args()
    print(build_report(args.run_root.resolve()))
