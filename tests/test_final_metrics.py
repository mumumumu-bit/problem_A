"""Final-metrics correctness, provenance and interrupted-run regression checks."""
import csv
import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture
def metrics(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'scripts'))
    assert (Path(__file__).resolve().parents[1] / 'scripts/final_metrics.py').exists(), 'Final metrics tool is missing'
    return importlib.import_module('final_metrics')


@pytest.fixture
def inputs(tmp_path, minimal_raw, hardware):
    data = tmp_path / 'data'
    data.mkdir()
    (data / 'config.txt').write_bytes(hardware.read_bytes())
    for i in (1, 2):
        (data / f'case_{i:03d}.json').write_text(json.dumps(minimal_raw), encoding='utf-8')
    return data


def test_default_cases_exactly_100(metrics):
    assert metrics.select_cases(None) == [f'case_{i:03d}' for i in range(1, 101)]
    for bad in [['case_001', 'case_001'], ['../case_001'], ['case_101'], []]:
        with pytest.raises(ValueError):
            metrics.select_cases(bad)


@pytest.mark.parametrize('mode', ['singlecore', 'p3'])
def test_official_results_and_resume(metrics, inputs, tmp_path, mode):
    output = tmp_path / mode
    rows = metrics.run(mode, output, inputs, ['case_001'])
    graph = metrics.GraphData.load(inputs / 'case_001.json')
    evaluator = metrics.OfficialEvaluator(graph, inputs / 'config.txt', 2)
    plan = evaluator.modules['single'].build_singlecore_plan(graph.raw)
    if mode == 'singlecore':
        expected = evaluator.singlecore()
        assert rows[0]['makespan'] == expected['makespan']
        assert rows[0]['added_copy_bytes'] == expected['data_movement_bytes']['added_copy_bytes']
    else:
        no_l2 = evaluator.raw(plan)
        l2 = metrics.OfficialEvaluator(graph, inputs / 'config.txt', 3).raw(plan)
        assert rows[0]['no_l2_makespan'] == no_l2['makespan']
        assert rows[0]['l2_makespan'] == l2['makespan']
        assert rows[0]['plan_sha256'] == metrics.digest(plan)
        assert rows[0]['l2_speedup'] == no_l2['makespan'] / l2['makespan']
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    metrics.run(mode, output, inputs, ['case_001'])
    assert before == {p.name: p.read_bytes() for p in output.iterdir()}


def test_resume_rejects_changed_config(metrics, inputs, tmp_path):
    output = tmp_path / 'out'
    metrics.run('p3', output, inputs, ['case_001'])
    with (inputs / 'config.txt').open('a') as f:
        f.write('\n# changed\n')
    with pytest.raises(ValueError, match='manifest'):
        metrics.run('p3', output, inputs, ['case_001'])


def test_resume_after_interruption(metrics, inputs, tmp_path, monkeypatch):
    output = tmp_path / 'out'
    original = metrics.evaluate_case
    def interrupted(mode, data_dir, case):
        if case == 'case_002':
            raise RuntimeError('interrupted')
        return original(mode, data_dir, case)
    with monkeypatch.context() as patch:
        patch.setattr(metrics, 'evaluate_case', interrupted)
        with pytest.raises(RuntimeError, match='interrupted'):
            metrics.run('p3', output, inputs, ['case_001', 'case_002'])
    assert len(list(csv.DictReader((output / 'p3_n1_l2.csv').open()))) == 1
    rows = metrics.run('p3', output, inputs, ['case_001', 'case_002'])
    assert [r['case'] for r in rows] == ['case_001', 'case_002']


def test_refuse_old_result_directory(metrics, inputs, tmp_path):
    output = tmp_path / 'old'
    output.mkdir()
    old = output / 'singlecore.csv'
    old.write_text('old results', encoding='utf-8')
    with pytest.raises(ValueError, match='nonempty'):
        metrics.run('singlecore', output, inputs, ['case_001'])
    assert old.read_text() == 'old results'


def test_reject_corrupt_completed_row(metrics, inputs, tmp_path):
    output = tmp_path / 'out'
    metrics.run('p3', output, inputs, ['case_001'])
    csv_path = output / 'p3_n1_l2.csv'
    rows = list(csv.DictReader(csv_path.open()))
    rows[0]['l2_speedup'] = 'NaN'
    with csv_path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError):
        metrics.run('p3', output, inputs, ['case_001'])
