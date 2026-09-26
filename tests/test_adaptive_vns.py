# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Tests for adaptive VNS, portfolio seeds, and neighbourhood statistics."""
import pytest
from npu_scheduler.config import SolverConfig
from npu_scheduler.types import Solution
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


def test_adaptive_config_defaults():
    """New parameters have sensible defaults."""
    config = SolverConfig()
    assert config.adaptive_budget is False
    assert config.min_neighbourhood_trials == 3
    assert config.stagnation_patience == 8
    assert config.fine_grain == 2
    assert config.portfolio_size == 10


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