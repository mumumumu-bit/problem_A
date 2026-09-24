# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Algorithm configuration; hardware values are always read by official code."""
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass(frozen=True)
class SolverConfig:
    seed: int = 2026
    time_budget: float = 120.0
    max_evaluations: int = 36
    candidate_pool: int = 24
    top_k: int = 2
    max_rounds: int = 16
    grains: tuple = (4, 12, 32)
    affinity_weight: float = 0.5
    communication_weight: float = 1.0
    memory_weight: float = 0.0
    cache_weight: float = 0.0
    atomic_fraction: float = 0.5
    weak_link_fraction: float = 0.25
    pipe_balance_weight: float = 0.2
    seed_budget_fraction: float = 0.45
    whole_graph_max_ops: int = 10000
    workers: int = 2
    # Adaptive VNS neighbourhood budget parameters
    adaptive_budget: bool = False  # enable dynamic neighbourhood selection
    min_neighbourhood_trials: int = 3  # minimum exploration per neighbourhood
    stagnation_patience: int = 8  # early stop after N consecutive non-improving evals
    fine_grain: int = 2  # extra-fine coarsening grain for v1-recovered variants
    portfolio_size: int = 10  # max structural seed candidates

    def __post_init__(self):
        for name in ('time_budget', 'max_evaluations', 'candidate_pool', 'top_k', 'workers'):
            if getattr(self, name) <= 0:
                raise ValueError(f'{name} must be positive')
        if self.max_rounds < 0 or not self.grains or any(x <= 0 for x in self.grains):
            raise ValueError('invalid rounds or grains')
        if not 0 < self.seed_budget_fraction <= 1 or self.whole_graph_max_ops < 0:
            raise ValueError('invalid seed budget or whole-graph threshold')
        if self.fine_grain <= 0 or self.portfolio_size <= 0:
            raise ValueError('invalid fine grain or portfolio size')

    @classmethod
    def load(cls, path=None):
        if path is None:
            return cls()
        text = Path(path).read_text(encoding='utf-8')
        try:
            data = json.loads(text)  # JSON is a portable YAML subset.
        except json.JSONDecodeError:
            import yaml
            data = yaml.safe_load(text)
        return cls(**data)

    def to_dict(self):
        return asdict(self)


class StrategySelector:
    @staticmethod
    def select(n_ops, config):
        from dataclasses import replace
        scale = 'small' if n_ops < 2000 else 'medium' if n_ops < 10000 else 'large' if n_ops < 25000 else 'extra-large'
        cap = {'small': 64, 'medium': 40, 'large': 26, 'extra-large': 20}[scale]
        return scale, replace(config, max_evaluations=min(config.max_evaluations, cap))
