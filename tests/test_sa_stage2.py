import importlib.util
import json
from pathlib import Path

import yaml

from npu_scheduler.config import SolverConfig


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'report_sa_stage2', ROOT / 'scripts' / 'report_sa_stage2.py')
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def test_stage2_configs_differ_only_by_sa_switch():
    control_path = ROOT / 'configs' / 'pilot_stage2_control.yaml'
    sa_path = ROOT / 'configs' / 'pilot_stage2_sa.yaml'
    control = yaml.safe_load(control_path.read_text(encoding='utf-8'))
    sa = yaml.safe_load(sa_path.read_text(encoding='utf-8'))
    differences = {key for key in control.keys() | sa.keys() if control.get(key) != sa.get(key)}
    assert differences == {'sa_enabled'}
    assert control['sa_enabled'] is False
    assert sa['sa_enabled'] is True
    assert control['time_budget'] == sa['time_budget'] == 120
    assert control['max_evaluations'] == sa['max_evaluations'] == 36
    assert control['sa_initial_temp'] == sa['sa_initial_temp'] == 0.01
    assert control['sa_cooling'] == sa['sa_cooling'] == 0.90
    assert control['sa_min_temp'] == sa['sa_min_temp'] == 0.001
    assert control['sa_stagnation_trigger'] == sa['sa_stagnation_trigger'] == 4
    assert control['sa_max_uphill_accepts'] == sa['sa_max_uphill_accepts'] == 4
    assert SolverConfig.load(control_path).seed == SolverConfig.load(sa_path).seed == 2026


def write_result(root, seed, arm, case, problem, cores, makespan, added_copy,
                 calls, runtime, uphill=0):
    directory = root / f'seed_{seed}' / arm / f'{case}_p{problem}_n{cores}' / f'{case}_p{problem}_n{cores}'
    directory.mkdir(parents=True)
    row = dict(case=case, problem=problem, cores=cores, algorithm='vns',
               makespan=makespan, added_copy_bytes=added_copy)
    job = dict(rows=[row], evaluator_calls=calls, total_seconds=runtime)
    (directory / 'job.json').write_text(json.dumps(job), encoding='utf-8')
    trials = [dict(accepted=True, accept_reason='sa_uphill') for _ in range(uphill)]
    (directory / 'trials.jsonl').write_text(
        ''.join(json.dumps(trial) + '\n' for trial in trials), encoding='utf-8')


def test_stage2_report_synthetic_tradeoffs_and_signals(tmp_path):
    cases = {
        'case_005': [
            ((100000, 0), (99700, 90000)),
            ((100000, 10000), (99600, 20000)),
            ((100000, 10000), (100000, 10000)),
        ],
        'case_001': [
            ((120000, 3000), (120000, 3000)),
            ((120000, 3000), (120000, 3000)),
            ((120000, 3000), (120100, 4000)),
        ],
    }
    for case, pairs in cases.items():
        cores = 4 if case == 'case_005' else 2
        for offset, (control, sa) in enumerate(pairs):
            seed = 2026 + offset
            write_result(tmp_path, seed, 'control', case, 1, cores,
                         control[0], control[1], 20, 1.0)
            write_result(tmp_path, seed, 'sa', case, 1, cores,
                         sa[0], sa[1], 22, 1.2, uphill=1)

    report = REPORT.build_report(tmp_path)
    assert 'small makespan gain with substantial added-copy increase' in report
    assert 'case_005 P1 N4' in report
    assert 'signal: positive signal' in report
    assert 'copy tradeoff status: high copy concern' in report
    assert 'makespan improvement is accompanied by repeated added-copy inflation' in report
    assert 'case_001 P1 N2' in report
    assert 'signal: no replicated improvement' in report
    assert 'total wins: 2' in report
    assert 'total ties: 3' in report
    assert 'total losses: 1' in report


def test_copy_risk_from_zero_is_high():
    control = dict(makespan=95618, added_copy=0)
    sa = dict(makespan=95404, added_copy=97254)
    diagnostics = REPORT.copy_diagnostics(control, sa)
    assert diagnostics['added_copy_from_zero'] is True
    assert diagnostics['copy_risk'] == 'high'
    assert diagnostics['tradeoff_note'] == REPORT.TRADEOFF_NOTE
    assert REPORT.task_signal(2) == 'positive signal'
    assert REPORT.task_signal(1) == 'weak / unstable signal'
    assert REPORT.task_signal(0) == 'no replicated improvement'
