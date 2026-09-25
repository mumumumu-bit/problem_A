# 本程序及代码是在人工智能工具辅助下完成的。
"""Report multi-seed Stage 2 SA-VNS results without changing solver objectives."""
import argparse
import json
from pathlib import Path
import statistics


TRADEOFF_NOTE = 'small makespan gain with substantial added-copy increase'


def load_arm(seed_dir, arm):
    records = {}
    arm_dir = seed_dir / arm
    if not arm_dir.is_dir():
        raise FileNotFoundError(f'Missing Stage 2 arm directory: {arm_dir}')
    for job_path in sorted(arm_dir.rglob('job.json')):
        job = json.loads(job_path.read_text(encoding='utf-8'))
        row = next((item for item in job['rows'] if item['algorithm'] == 'vns'), None)
        if row is None:
            raise ValueError(f'Missing VNS row in {job_path}')
        key = (row['case'], int(row['problem']), int(row['cores']))
        if key in records:
            raise ValueError(f'Duplicate Stage 2 task in {arm_dir}: {key}')
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
            evaluator_calls=int(job['evaluator_calls']),
            uphill_accepted=uphill,
            runtime=float(job['total_seconds']),
        )
    return records


def copy_diagnostics(control, sa):
    makespan_improve_ratio = (control['makespan'] - sa['makespan']) / control['makespan']
    copy_delta = sa['added_copy'] - control['added_copy']
    from_zero = control['added_copy'] == 0 and sa['added_copy'] > 0
    copy_relative = None
    if control['added_copy'] > 0:
        copy_relative = copy_delta / control['added_copy']

    if copy_delta <= 0:
        risk = 'low'
    elif from_zero or makespan_improve_ratio <= 0:
        risk = 'high'
    elif makespan_improve_ratio < 0.005 and copy_relative is not None and copy_relative > 0.5:
        risk = 'high'
    else:
        risk = 'moderate'

    risky_small_gain = (makespan_improve_ratio > 0 and makespan_improve_ratio < 0.005
                        and (from_zero or (copy_relative is not None and copy_relative > 0.5)))
    return dict(
        copy_delta=copy_delta,
        copy_relative=copy_relative,
        added_copy_from_zero=from_zero,
        copy_risk=risk,
        tradeoff_note=TRADEOFF_NOTE if risky_small_gain else '',
    )


def task_signal(wins):
    if wins >= 2:
        return 'positive signal'
    if wins == 1:
        return 'weak / unstable signal'
    return 'no replicated improvement'


def copy_status(rows):
    high = sum(row['copy_risk'] == 'high' for row in rows)
    moderate = sum(row['copy_risk'] == 'moderate' for row in rows)
    if high >= 2:
        return 'high copy concern'
    if high or moderate:
        return 'moderate copy concern'
    return 'low copy concern'


def collect_rows(run_root):
    rows = []
    for seed_dir in sorted(run_root.glob('seed_*')):
        try:
            seed = int(seed_dir.name.removeprefix('seed_'))
        except ValueError:
            continue
        control = load_arm(seed_dir, 'control')
        sa = load_arm(seed_dir, 'sa')
        if set(control) != set(sa):
            raise ValueError(f'Task mismatch for seed {seed}: control={sorted(control)}, SA={sorted(sa)}')
        for task in sorted(control):
            c = control[task]
            s = sa[task]
            makespan_delta = s['makespan'] - c['makespan']
            row = dict(
                task=task,
                seed=seed,
                control=c,
                sa=s,
                makespan_delta=makespan_delta,
                makespan_relative=makespan_delta / c['makespan'],
            )
            row.update(copy_diagnostics(c, s))
            rows.append(row)
    if not rows:
        raise ValueError(f'No completed Stage 2 results found in {run_root}')
    return rows


def format_extreme(values, mode):
    selected = max(values) if mode == 'max' else min(values)
    if mode == 'max' and selected <= 0:
        return 'none'
    if mode == 'min' and selected >= 0:
        return 'none'
    return f'{selected:+.4%}'


def build_report(run_root):
    rows = collect_rows(run_root)
    lines = [
        '| Task | Seed | control Makespan | SA Makespan | Makespan delta | Makespan relative delta | '
        'control Added Copy | SA Added Copy | Added Copy delta | Added Copy relative delta | '
        'added_copy_from_zero | copy_risk | tradeoff_note | control calls | SA calls | '
        'SA uphill accepted | control runtime | SA runtime |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|',
    ]
    for row in sorted(rows, key=lambda item: (item['task'], item['seed'])):
        case, problem, cores = row['task']
        c, s = row['control'], row['sa']
        copy_relative = 'n/a' if row['copy_relative'] is None else f"{row['copy_relative']:+.4%}"
        lines.append(
            f"| {case} P{problem} N{cores} | {row['seed']} | {c['makespan']} | {s['makespan']} | "
            f"{row['makespan_delta']:+d} | {row['makespan_relative']:+.4%} | {c['added_copy']} | "
            f"{s['added_copy']} | {row['copy_delta']:+d} | {copy_relative} | "
            f"{str(row['added_copy_from_zero']).lower()} | {row['copy_risk']} | "
            f"{row['tradeoff_note'] or '-'} | {c['evaluator_calls']} | {s['evaluator_calls']} | "
            f"{s['uphill_accepted']} | {c['runtime']:.3f} | {s['runtime']:.3f} |"
        )

    lines += ['', '## Per-task summaries', '']
    for task in sorted({row['task'] for row in rows}):
        group = [row for row in rows if row['task'] == task]
        relative = [row['makespan_relative'] for row in group]
        wins = sum(value < 0 for value in relative)
        ties = sum(value == 0 for value in relative)
        losses = sum(value > 0 for value in relative)
        high_count = sum(row['copy_risk'] == 'high' for row in group)
        case, problem, cores = task
        lines += [
            f'### {case} P{problem} N{cores}',
            f'wins / ties / losses: {wins} / {ties} / {losses}',
            f'mean relative Makespan change: {statistics.mean(relative):+.4%}',
            f'median relative Makespan change: {statistics.median(relative):+.4%}',
            f'worst Makespan regression: {format_extreme(relative, "max")}',
            f'best Makespan improvement: {format_extreme(relative, "min")}',
            f'mean Added Copy delta: {statistics.mean(row["copy_delta"] for row in group):+.2f}',
            f'high copy-risk count: {high_count}',
            f'SA uphill accepted total: {sum(row["sa"]["uphill_accepted"] for row in group)}',
            f'mean evaluator calls control: {statistics.mean(row["control"]["evaluator_calls"] for row in group):.2f}',
            f'mean evaluator calls SA: {statistics.mean(row["sa"]["evaluator_calls"] for row in group):.2f}',
            f'mean runtime control: {statistics.mean(row["control"]["runtime"] for row in group):.3f}',
            f'mean runtime SA: {statistics.mean(row["sa"]["runtime"] for row in group):.3f}',
            f'signal: {task_signal(wins)}',
            f'copy tradeoff status: {copy_status(group)}',
        ]
        if wins and high_count >= 2:
            lines.append('makespan improvement is accompanied by repeated added-copy inflation')
        lines.append('')

    all_relative = [row['makespan_relative'] for row in rows]
    lines += [
        '## Overall summary',
        '',
        f'total wins: {sum(value < 0 for value in all_relative)}',
        f'total ties: {sum(value == 0 for value in all_relative)}',
        f'total losses: {sum(value > 0 for value in all_relative)}',
        f'overall mean relative Makespan change: {statistics.mean(all_relative):+.4%}',
        f'overall Added Copy delta: {sum(row["copy_delta"] for row in rows):+d}',
        f'total high copy-risk cases: {sum(row["copy_risk"] == "high" for row in rows)}',
        f'total uphill accepted count: {sum(row["sa"]["uphill_accepted"] for row in rows)}',
        f'mean evaluator call difference: '
        f'{statistics.mean(row["sa"]["evaluator_calls"] - row["control"]["evaluator_calls"] for row in rows):+.2f}',
        f'mean runtime difference: '
        f'{statistics.mean(row["sa"]["runtime"] - row["control"]["runtime"] for row in rows):+.3f}',
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-root', type=Path, required=True)
    args = parser.parse_args()
    print(build_report(args.run_root.resolve()))
