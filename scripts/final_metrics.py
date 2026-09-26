# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：OpenAI Codex；模型/版本：GPT-6；日期：2026-09-26。
"""Fixed official single-core evaluations; no solver or search is invoked."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from npu_scheduler.graph import GraphData
from npu_scheduler.evaluator.official_adapter import OfficialEvaluator

FIELDS = {
    'singlecore': ['case', 'makespan', 'added_copy_bytes', 'seconds'],
    'p3': ['case', 'no_l2_makespan', 'l2_makespan', 'l2_speedup',
           'cache_hit_rate', 'added_copy_no_l2', 'added_copy_l2', 'plan_sha256', 'seconds'],
}
FILENAMES = {'singlecore': 'singlecore.csv', 'p3': 'p3_n1_l2.csv'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_cases(cases):
    selected = list(cases) if cases is not None else [f'case_{i:03d}' for i in range(1, 101)]
    allowed = {f'case_{i:03d}' for i in range(1, 101)}
    if not selected or len(set(selected)) != len(selected) or not set(selected) <= allowed:
        raise ValueError('Cases must be unique members of case_001 through case_100')
    return sorted(selected)


def make_manifest(mode, data_dir, cases):
    # Hash only input graphs, official code, adapter dependencies and these tools.
    tools = [Path(__file__), ROOT / 'scripts/singlecore_full100.py', ROOT / 'scripts/p3_singlecore_l2.py']
    identity = dict(schema=1, mode=mode, cases=cases, cores=[1], search=False,
                    config_sha256=file_hash(data_dir / 'config.txt'),
                    graph_sha256={case: file_hash(data_dir / (case + '.json')) for case in cases},
                    official_sha256={p.name: file_hash(p) for p in sorted((ROOT / 'code').glob('*.py'))},
                    source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): file_hash(p)
                                   for p in sorted((ROOT / 'src/npu_scheduler').rglob('*.py'))},
                    tool_sha256={p.name: file_hash(p) for p in tools},
                    evaluator=('official singlecore_evaluate.evaluate_singlecore' if mode == 'singlecore'
                               else 'same build_singlecore_plan: OfficialEvaluator.raw(problem=2), then raw(problem=3)'))
    return dict(identity, identity=digest(identity), created=datetime.now(timezone.utc).isoformat(),
                git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                python=sys.version, platform=platform.platform(),
                config_path=str((data_dir / 'config.txt').resolve()))


def evaluate_case(mode, data_dir, case):
    started = time.perf_counter()
    graph = GraphData.load(data_dir / (case + '.json'))
    config = data_dir / 'config.txt'
    if mode == 'singlecore':
        result = OfficialEvaluator(graph, config, 1).singlecore()
        row = dict(case=case, makespan=result['makespan'],
                   added_copy_bytes=result['data_movement_bytes']['added_copy_bytes'])
    else:
        p2, p3 = OfficialEvaluator(graph, config, 2), OfficialEvaluator(graph, config, 3)
        plan = p2.modules['single'].build_singlecore_plan(graph.raw)
        if len(plan['core_schedules']) != 1:
            raise ValueError('Expected exactly one core')
        plan_hash = digest(plan)
        no_l2 = p2.raw(plan)
        if digest(plan) != plan_hash:
            raise ValueError('P2 evaluator mutated the plan')
        l2 = p3.raw(plan)
        if digest(plan) != plan_hash:
            raise ValueError('P3 evaluator mutated the plan')
        row = dict(case=case, no_l2_makespan=no_l2['makespan'], l2_makespan=l2['makespan'],
                   l2_speedup=no_l2['makespan'] / l2['makespan'],
                   cache_hit_rate=l2['cache_stats']['hit_rate'],
                   added_copy_no_l2=no_l2['data_movement_bytes']['added_copy_bytes'],
                   added_copy_l2=l2['data_movement_bytes']['added_copy_bytes'], plan_sha256=plan_hash)
    row['seconds'] = time.perf_counter() - started
    return row


def validate_row(mode, row):
    if set(row) != set(FIELDS[mode]):
        raise ValueError('Unexpected CSV fields')
    integers = (['makespan', 'added_copy_bytes'] if mode == 'singlecore' else
                ['no_l2_makespan', 'l2_makespan', 'added_copy_no_l2', 'added_copy_l2'])
    parsed = dict(row)
    for key in integers:
        parsed[key] = int(str(row[key]))
        if parsed[key] < 0 or ('makespan' in key and parsed[key] == 0):
            raise ValueError(f'Invalid {key}')
    floats = ['seconds'] if mode == 'singlecore' else ['seconds', 'l2_speedup', 'cache_hit_rate']
    for key in floats:
        parsed[key] = float(row[key])
        if not math.isfinite(parsed[key]) or parsed[key] < 0:
            raise ValueError(f'Invalid {key}')
    if mode == 'p3':
        if not 0 <= parsed['cache_hit_rate'] <= 1 or not re.fullmatch(r'[0-9a-f]{64}', row['plan_sha256']):
            raise ValueError('Invalid cache hit rate or plan hash')
        if not math.isclose(parsed['l2_speedup'], parsed['no_l2_makespan'] / parsed['l2_makespan'], rel_tol=1e-12):
            raise ValueError('Incorrect L2 speedup')
    return parsed


def write_rows(path, mode, rows):
    temporary = path.with_suffix('.csv.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS[mode])
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def run(mode, output, data_dir, cases=None):
    if mode not in FIELDS:
        raise ValueError('Unknown evaluation mode')
    cases = select_cases(cases)
    output, data_dir = Path(output), Path(data_dir)
    current = make_manifest(mode, data_dir, cases)
    manifest_path = output / 'manifest.json'
    csv_path = output / FILENAMES[mode]
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding='utf-8'))
        if old.get('identity') != current['identity']:
            raise ValueError('Incompatible manifest: inputs, tools, cases or mode changed; use a new output directory')
    else:
        if output.exists() and any(output.iterdir()):
            raise ValueError('Refusing nonempty output directory without a matching manifest')
        output.mkdir(parents=True, exist_ok=True)
        temporary = output / 'manifest.json.tmp'
        temporary.write_text(json.dumps(current, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        temporary.replace(manifest_path)
    completed = {}
    if csv_path.exists():
        with csv_path.open(encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != FIELDS[mode]:
                raise ValueError('Unexpected CSV header')
            for row in reader:
                row = validate_row(mode, row)
                if row['case'] not in cases or row['case'] in completed:
                    raise ValueError('Unexpected or duplicate case in CSV')
                completed[row['case']] = row
    print(f'{mode}: resume {len(completed)}/{len(cases)}; no search', flush=True)
    for case in cases:
        if case in completed:
            continue
        completed[case] = validate_row(mode, evaluate_case(mode, data_dir, case))
        write_rows(csv_path, mode, [completed[c] for c in cases if c in completed])
        print(f'{len(completed)}/{len(cases)} {case}: ' + json.dumps(completed[case]), flush=True)
    print(f'COMPLETE {len(completed)}/{len(cases)} unique cases: {csv_path}', flush=True)
    return [completed[case] for case in cases]


def main(mode):
    parser = argparse.ArgumentParser(description=__doc__)
    default = 'singlecore_full100' if mode == 'singlecore' else 'p3_singlecore_full100'
    parser.add_argument('--output', type=Path, default=ROOT / 'results' / default)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--cases', nargs='+', help='Default: all 100 official cases; use case_001 for smoke')
    args = parser.parse_args()
    run(mode, args.output, args.data_dir, args.cases)
