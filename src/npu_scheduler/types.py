# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Immutable solutions use a global block order projected onto each core."""
from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class Solution:
    blocks: tuple[tuple[int, ...], ...]
    cores: tuple[int, ...]
    num_cores: int

    def plan(self, graph):
        schedules = [[] for _ in range(self.num_cores)]
        mapping = {}
        for b, (members, core) in enumerate(zip(self.blocks, self.cores)):
            schedules[core].append(b)
            for i in members:
                mapping[str(graph.op_ids[i])] = b
        return {'node_to_subgraph': mapping, 'core_schedules': schedules}

    def digest(self):
        return hashlib.sha256(json.dumps((self.blocks, self.cores, self.num_cores), separators=(',', ':')).encode()).hexdigest()

    @classmethod
    def from_plan(cls, graph, plan):
        from .evaluator.official_adapter import official_modules
        import importlib
        official_modules()
        stub=importlib.import_module('stub_multicore_cut_and_schedule')
        view=stub.derive_multicore_plan(graph.raw,plan)
        # Include same-core ordering constraints before reconstructing a global order.
        ids=view['subgraph_ids']; index={b:i for i,b in enumerate(ids)}
        pred,succ=[set() for _ in ids],[set() for _ in ids]
        pairs=list(view['dependency_pairs'])
        for order in plan['core_schedules']:
            pairs.extend(zip(order,order[1:]))
        for a,b in pairs:
            pred[index[b]].add(index[a]); succ[index[a]].add(index[b])
        from .graph import topological
        order=[ids[i] for i in topological(pred,succ)]
        return cls(tuple(tuple(sorted((graph.index[u] for u in view['nodes_by_subgraph'][b]),key=lambda u:graph.topo_index[u])) for b in order),
                   tuple(view['core_by_subgraph'][b] for b in order),len(plan['core_schedules']))

    def validate(self, graph):
        if self.num_cores < 1 or len(self.blocks) != len(self.cores):
            raise ValueError('invalid core assignment')
        mapping = [-1] * graph.n
        for b, members in enumerate(self.blocks):
            if not members or not 0 <= self.cores[b] < self.num_cores:
                raise ValueError('empty block or invalid core')
            for i in members:
                if not 0 <= i < graph.n or mapping[i] != -1:
                    raise ValueError('duplicate or unknown op')
                mapping[i] = b
        if -1 in mapping:
            raise ValueError('incomplete partition')
        if any(mapping[u] > mapping[v] for u in range(graph.n) for v in graph.succ[u]):
            raise ValueError('block order violates dependency')
        return True


@dataclass(frozen=True)
class Evaluation:
    valid: bool
    makespan: int = 0
    added_copy_bytes: int = 0
    spill_bytes: int = 0
    cache_hit_rate: float = 0.0
    seconds: float = 0.0
    error: str = ''

    @property
    def objective(self):
        return (self.makespan, self.added_copy_bytes) if self.valid else (float('inf'), float('inf'))
