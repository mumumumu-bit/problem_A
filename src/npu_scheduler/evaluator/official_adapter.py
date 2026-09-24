# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""One explicit adapter for all three official evaluators and independent CLI QA."""
from dataclasses import asdict
from functools import lru_cache
import hashlib
import importlib
from pathlib import Path
import subprocess
import sys
import time
import json

from ..types import Evaluation
from .cache import EvaluationCache, digest, atomic_json


@lru_cache(maxsize=1)
def official_modules():
    code = Path(__file__).resolve().parents[3]/'code'
    if not code.is_dir():
        raise FileNotFoundError('Keep the official code/ directory beside src/, or use an editable installation.')
    sys.path.insert(0, str(code))
    names = {'validation':'evaluation_validation', 'io':'contest_io',
             'p1':'multicore_cut_evaluate_problem_1', 'p2':'multicore_cut_evaluate_problem_2',
             'p3':'multicore_cut_evaluate_problem_3', 'single':'singlecore_evaluate'}
    return {key:importlib.import_module(name) for key,name in names.items()}


class OfficialEvaluator:
    def __init__(self, graph, config_path, problem, cache_dir=None):
        if problem not in (1,2,3):
            raise ValueError('problem must be 1, 2 or 3')
        self.graph, self.problem = graph, problem
        self.config_path = Path(config_path).resolve()
        self.modules = official_modules()
        self.hardware = self.modules['validation'].read_evaluation_config(str(self.config_path))
        self.scene_a = self.modules['p1'].read_scene_a_config(str(self.config_path))
        self.scene_b = self.modules['p2'].read_scene_b_config(str(self.config_path))
        self.cache_settings = self.modules['p3'].read_cache_config(str(self.config_path))
        source_dir = Path(self.modules['p1'].__file__).parent
        self.official_hash = digest({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_dir.glob('*.py'))})
        self.context = dict(graph=graph.fingerprint, problem=problem,
                            hardware=hashlib.sha256(self.config_path.read_bytes()).hexdigest(),
                            official=self.official_hash, schema=1)
        self.cache = EvaluationCache(cache_dir)
        self.calls, self.hits, self.seconds = 0,0,0.0

    def raw(self, plan):
        common = self.hardware
        if self.problem == 1:
            return self.modules['p1'].evaluate_scene_a(self.graph.raw, plan, **common,
                cross_core_wait=self.scene_a['task_cross_core_wait_cycles'],
                same_core_wait=self.scene_a['task_same_core_wait_cycles'])
        common = dict(common, cross_core_copy_delay=self.scene_b['cross_core_copy_delay_cycles'])
        if self.problem == 2:
            return self.modules['p2'].evaluate_scene_b(self.graph.raw, plan, **common)
        return self.modules['p3'].evaluate_problem_3(self.graph.raw, plan, **common, **self.cache_settings)

    def evaluate(self, solution):
        solution.validate(self.graph)
        plan = solution.plan(self.graph)
        key = digest(dict(self.context, plan=plan))
        cached = self.cache.get(key)
        if cached is not None:
            self.hits += 1
            return Evaluation(**cached)
        start = time.perf_counter()
        self.calls += 1
        try:
            result = self.raw(plan)
            movement = result['data_movement_bytes']
            value = Evaluation(True, result['makespan'], movement['added_copy_bytes'],
                movement['spill_added_copy_bytes'], result.get('cache_stats',{}).get('hit_rate',0),
                time.perf_counter()-start)
        except (ValueError, RuntimeError) as error:
            # Global FIFO/memory/cross-core cycles are candidate infeasibility.
            # Do not catch coding errors (KeyError/TypeError etc.) as bad candidates.
            value = Evaluation(False, seconds=time.perf_counter()-start,
                               error=f'{type(error).__name__}: {error}')
        self.seconds += value.seconds
        self.cache.put(key, asdict(value))
        return value

    def singlecore(self):
        return self.modules['single'].evaluate_singlecore(self.graph.raw, **self.hardware)

    def verify_cli(self, graph_path, solution, directory, timeout=300):
        directory = Path(directory).resolve()
        directory.mkdir(parents=True,exist_ok=True)
        plan_path, result_path = directory/'plan.json', directory/'result.json'
        atomic_json(plan_path, solution.plan(self.graph))
        script = Path(self.modules[f'p{self.problem}'].__file__)
        command = [sys.executable, str(script), str(Path(graph_path).resolve()), str(plan_path),
                   '--config',str(self.config_path), '-o',str(result_path),
                   '--trace-output', str(directory/'perfetto_trace.json'),
                   '--log-output',str(directory/'official_log.txt')]
        run = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        (directory/'cli_stdout.txt').write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
        if run.returncode:
            raise RuntimeError(f'Official CLI failed: {run.stderr}')
        result = json.loads(result_path.read_text(encoding='utf-8'))
        expected = self.evaluate(solution)
        actual = (result['makespan'],result['data_movement_bytes']['added_copy_bytes'])
        if actual != expected.objective:
            raise AssertionError(f'CLI/adapter mismatch: {actual} != {expected.objective}')
        return result

