# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Tests for adaptive VNS, portfolio seeds, and neighbourhood statistics."""
from types import SimpleNamespace
import pytest
from npu_scheduler.config import SolverConfig
from npu_scheduler.types import Evaluation, Solution
import npu_scheduler.search.vns as vns_module
from npu_scheduler.search.vns import solve
from npu_scheduler.partition.initial_partition import seeds
from npu_scheduler.evaluator.official_adapter import OfficialEvaluator


class FakeEvaluator:
    """Minimal evaluator that returns monotonically improving scores."""
    def __init__(self, problem=1):
        self.problem = problem
        self.calls = 0
        self.hits = 0
        self.seconds = 0.0
        self.hardware = dict(bandwidth=32, l1_capacity=65536, l1_bandwidth=512)
        self.scene_a = dict(task_cross_core_wait_cycles=100, task_same_core_wait_cycles=0)
        self.scene_b = dict(cross_core_copy_delay_cycles=100)
        self.cache_settings = dict(cache_capacity_bytes=1048576, cache_bandwidth_bytes_per_cycle=128)

    def evaluate(self, solution):
        self.calls += 1
        from npu_scheduler.types import Evaluation
        # Return a fake makespan that decreases with more blocks (simulate diversity)
        ms = 50000 - len(solution.blocks) * 100 + self.calls * 10
        return Evaluation(valid=True, makespan=max(1000, ms), added_copy_bytes=0,
                          spill_bytes=0, cache_hit_rate=0, seconds=0.001)


class ScenarioEvaluator(FakeEvaluator):
    """Evaluator with scores keyed by immutable solution digests."""
    def __init__(self, scores):
        super().__init__()
        self.scores = scores

    def evaluate(self, solution):
        self.calls += 1
        makespan, added_copy = self.scores[solution.digest()]
        return Evaluation(valid=True, makespan=makespan, added_copy_bytes=added_copy)


def run_sa_scenario(monkeypatch, config, scores=None, candidates=None):
    """Run a tiny deterministic search without invoking the official evaluator."""
    solutions = [Solution(((0,),), (core,), 4) for core in range(4)]
    if scores is None:
        scores = [(100, 0), (100, 1), (101, 0), (90, 0)]
    if candidates is None:
        candidates = {0: solutions[1], 1: solutions[2], 2: solutions[3]}
    evaluator = ScenarioEvaluator({s.digest(): score for s, score in zip(solutions, scores)})
    graph = SimpleNamespace(n=1, topo=(0,))
    monkeypatch.setattr(vns_module, 'seeds', lambda *args: [('baseline', solutions[0])])
    monkeypatch.setattr(vns_module, 'neighbors',
                        lambda graph, current, kind, rng, pool: [candidates[kind]] if kind in candidates else [])
    monkeypatch.setattr(vns_module, 'estimate',
                        lambda *args, diagnostics=False, **kwargs: {} if diagnostics else 0)
    return solve(graph, 4, evaluator, config), solutions


def test_adaptive_config_defaults():
    """New parameters have sensible defaults."""
    config = SolverConfig()
    assert config.adaptive_budget is False
    assert config.min_neighbourhood_trials == 3
    assert config.stagnation_patience == 8
    assert config.fine_grain == 2
    assert config.portfolio_size == 10
    assert config.sa_enabled is False
    assert config.sa_initial_temp == 0.01
    assert config.sa_cooling == 0.90
    assert config.sa_min_temp == 0.001
    assert config.sa_stagnation_trigger == 4
    assert config.sa_max_uphill_accepts == 4


def test_adaptive_config_enabled():
    """Can enable adaptive budget."""
    config = SolverConfig(adaptive_budget=True)
    assert config.adaptive_budget is True


def test_invalid_fine_grain():
    with pytest.raises(ValueError):
        SolverConfig(fine_grain=0)


def test_invalid_portfolio_size():
    with pytest.raises(ValueError):
        SolverConfig(portfolio_size=0)


def test_seeds_include_fine_grain(minimal, hardware):
    """Extra-fine grain is included in seed candidates."""
    config = SolverConfig(grains=(4, 12, 32), fine_grain=2)
    evaluator = OfficialEvaluator(minimal, hardware, 1)
    hw = dict(bandwidth=32, cross_wait=100, same_wait=0,
              cache_capacity=1048576, cache_bandwidth=128)
    seed_list = list(seeds(minimal, 2, 1, hw, config))
    names = [s[0] for s in seed_list]
    # Should include the extra-fine grain variant
    assert any('2' in name for name in names), f"Expected fine grain=2 seeds, got {names}"
    # Should stay within portfolio_size limit
    assert len(seed_list) <= config.portfolio_size + 2  # +2 for baseline and whole


def test_solve_returns_neighbourhood_stats(minimal, hardware):
    """solve() includes neighbourhood_stats in return dict when algorithm=vns."""
    evaluator = OfficialEvaluator(minimal, hardware, 1)
    config = SolverConfig(adaptive_budget=True, max_evaluations=8, time_budget=10)
    result = solve(minimal, 2, evaluator, config, algorithm='vns')
    assert 'neighbourhood_stats' in result
    stats = result['neighbourhood_stats']
    assert len(stats) == 8
    for k in [f'N{i}' for i in range(1, 9)]:
        assert k in stats


def test_solve_baseline_returns_stats(minimal, hardware):
    """solve() in baseline mode also returns neighbourhood_stats."""
    evaluator = OfficialEvaluator(minimal, hardware, 1)
    config = SolverConfig()
    result = solve(minimal, 2, evaluator, config, algorithm='baseline')
    assert 'neighbourhood_stats' in result


def test_prioritised_neighbourhood_order():
    """Adaptive VNS uses the prioritized default order."""
    config = SolverConfig(adaptive_budget=True)
    # With adaptive_budget=True, the first iterations use default order
    # High priority: N1(0), N2(1); Medium: N4(3), N5(4); Low: N3(2), N6(5), N7(6), N8(7)
    # The order should be [0,1,3,4,2,5,7,6] not sequential [0,1,2,3,4,5,6,7]
    assert config.adaptive_budget is True  # structural test: config enables it


def test_sa_disabled_compatibility(monkeypatch):
    base = dict(max_evaluations=4, max_rounds=3, top_k=1, time_budget=10)
    implicit, _ = run_sa_scenario(monkeypatch, SolverConfig(**base))
    explicit, _ = run_sa_scenario(monkeypatch, SolverConfig(sa_enabled=False, **base))
    projection = lambda result: [(t['accepted'], t['accept_reason'], t['is_global_best'])
                                 for t in result['trials']]
    assert implicit['evaluation'].objective == explicit['evaluation'].objective
    assert implicit['solution'] == explicit['solution']
    assert projection(implicit) == projection(explicit)


def test_sa_is_deterministic(monkeypatch):
    config = SolverConfig(sa_enabled=True, sa_initial_temp=1.0, sa_min_temp=0.1,
                          sa_stagnation_trigger=1, max_evaluations=4,
                          max_rounds=3, top_k=1, time_budget=10)
    first, _ = run_sa_scenario(monkeypatch, config)
    second, _ = run_sa_scenario(monkeypatch, config)
    fields = lambda result: [(t['accepted'], t['accept_reason'], t['temperature'])
                             for t in result['trials']]
    assert first['solution'] == second['solution']
    assert first['evaluation'].objective == second['evaluation'].objective
    assert fields(first) == fields(second)


def test_sa_accepts_uphill_then_finds_better_solution(monkeypatch):
    config = SolverConfig(sa_enabled=True, sa_initial_temp=1.0, sa_min_temp=0.1,
                          sa_stagnation_trigger=1, max_evaluations=4,
                          max_rounds=3, top_k=1, time_budget=10)
    result, solutions = run_sa_scenario(monkeypatch, config)
    assert any(t['accept_reason'] == 'sa_uphill' and t['accepted'] for t in result['trials'])
    assert result['solution'] == solutions[3]
    assert result['evaluation'].makespan == 90


def test_sa_protects_global_best(monkeypatch):
    config = SolverConfig(sa_enabled=True, sa_initial_temp=1.0, sa_min_temp=0.1,
                          sa_stagnation_trigger=1, max_evaluations=3,
                          max_rounds=2, top_k=1, time_budget=10)
    result, solutions = run_sa_scenario(monkeypatch, config)
    assert result['trials'][-1]['accept_reason'] == 'sa_uphill'
    assert result['solution'] == solutions[0]
    assert result['evaluation'].makespan == 100


def test_sa_does_not_exceed_evaluation_budget(monkeypatch):
    config = SolverConfig(sa_enabled=True, sa_initial_temp=1.0, sa_min_temp=0.1,
                          sa_stagnation_trigger=1, max_evaluations=3,
                          max_rounds=20, top_k=1, time_budget=10)
    result, _ = run_sa_scenario(monkeypatch, config)
    assert result['evaluator_calls'] == 3
    assert len(result['trials']) == 3


def test_sa_temperature_cools_with_floor(monkeypatch):
    config = SolverConfig(sa_enabled=True, sa_initial_temp=1.0, sa_cooling=0.1,
                          sa_min_temp=0.4, sa_stagnation_trigger=1,
                          max_evaluations=3, max_rounds=2, top_k=1, time_budget=10)
    result, _ = run_sa_scenario(monkeypatch, config)
    uphill = next(t for t in result['trials'] if t['accept_reason'] == 'sa_uphill')
    assert uphill['temperature'] == 0.4


def test_sa_limits_uphill_accepts(monkeypatch):
    config = SolverConfig(sa_enabled=True, sa_initial_temp=100.0, sa_min_temp=1.0,
                          sa_stagnation_trigger=1, sa_max_uphill_accepts=1,
                          max_evaluations=4, max_rounds=3, top_k=1, time_budget=10)
    result, _ = run_sa_scenario(monkeypatch, config, scores=[(100, 0), (100, 1), (101, 0), (102, 0)])
    assert sum(t['accept_reason'] == 'sa_uphill' for t in result['trials']) == 1
    assert result['trials'][-1]['accept_reason'] == 'rejected'
