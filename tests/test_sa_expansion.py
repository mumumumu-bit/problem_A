import importlib.util
import json
from pathlib import Path
import re

import yaml

from npu_scheduler.config import SolverConfig


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'report_sa_expansion', ROOT / 'scripts' / 'report_sa_expansion.py')
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def test_expansion_configs_only_differ_by_sa_switch():
    control_path = ROOT / 'configs' / 'sa_expansion_control.yaml'
    sa_path = ROOT / 'configs' / 'sa_expansion_sa.yaml'
    control = yaml.safe_load(control_path.read_text(encoding='utf-8'))
    sa = yaml.safe_load(sa_path.read_text(encoding='utf-8'))
    differences = {key for key in control.keys() | sa.keys() if control.get(key) != sa.get(key)}
    assert differences == {'sa_enabled'}
    assert control['sa_enabled'] is False
    assert sa['sa_enabled'] is True
    assert control['seed'] == sa['seed'] == 2026
    assert control['time_budget'] == sa['time_budget'] == 120
    assert control['max_evaluations'] == sa['max_evaluations'] == 36
    assert control['sa_initial_temp'] == sa['sa_initial_temp'] == 0.01
    assert control['sa_cooling'] == sa['sa_cooling'] == 0.90
    assert control['sa_min_temp'] == sa['sa_min_temp'] == 0.001
    assert control['sa_stagnation_trigger'] == sa['sa_stagnation_trigger'] == 4
    assert control['sa_max_uphill_accepts'] == sa['sa_max_uphill_accepts'] == 4
    assert SolverConfig.load(control_path).seed == SolverConfig.load(sa_path).seed == 2026


def test_expansion_runner_has_exactly_eight_fixed_tasks_and_one_seed():
    text = (ROOT / 'scripts' / 'run_sa_expansion.ps1').read_text(encoding='utf-8')
    tasks = re.findall(r'Case = "(case_\d+)"; Problem = (\d); Cores = (\d)', text)
    assert len(tasks) == 8
    assert len(set(tasks)) == 8
    assert '$Seed = 2026' in text
    assert '2027' not in text
    assert '2028' not in text


def write_result(root, arm, case, makespan, added_copy, calls, runtime, uphill=0):
    task = f'{case}_p1_n2'
    directory = root / arm / task / task
    directory.mkdir(parents=True)
    row = dict(case=case, problem=1, cores=2, algorithm='vns',
               makespan=makespan, added_copy_bytes=added_copy)
    job = dict(rows=[row], evaluator_calls=calls, total_seconds=runtime)
    (directory / 'job.json').write_text(json.dumps(job), encoding='utf-8')
    trials = [dict(accepted=True, accept_reason='sa_uphill') for _ in range(uphill)]
    (directory / 'trials.jsonl').write_text(
        ''.join(json.dumps(trial) + '\n' for trial in trials), encoding='utf-8')


def test_expansion_report_wins_ties_losses_and_copy_risk(tmp_path):
    pairs = [
        ('case_101', (100000, 0), (99700, 90000)),
        ('case_102', (100000, 1000), (100000, 1000)),
        ('case_103', (100000, 1000), (100100, 1000)),
    ]
    for case, control, sa in pairs:
        write_result(tmp_path, 'control', case, *control, calls=20, runtime=1.0)
        write_result(tmp_path, 'sa', case, *sa, calls=22, runtime=1.2, uphill=1)
    report = REPORT.build_report(tmp_path)
    assert '| case_101 P1 N2 | win |' in report
    assert '| case_102 P1 N2 | tie |' in report
    assert '| case_103 P1 N2 | loss |' in report
    assert 'wins: 1' in report
    assert 'ties: 1' in report
    assert 'losses: 1' in report
    assert '| high | small makespan gain with substantial added-copy increase |' in report


def test_expansion_signal_classifications():
    assert REPORT.classify_signal(3, 0, -0.001, 1) == 'strong signal'
    assert REPORT.classify_signal(2, 1, -0.001, 2) == 'moderate signal'
    assert REPORT.classify_signal(1, 0, -0.001, 0) == 'weak signal'
    assert REPORT.classify_signal(1, 1, 0.001, 0) == 'negative signal'
