# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Convex interval aggregation in locality-oriented topological orders."""
from ..graph import topological


def coarsen(graph, cores, grain, mode='affinity', config=None):
    from ..config import SolverConfig
    config = config or SolverConfig()
    if not graph.n:
        return ()
    if mode == 'balanced':
        order = graph.topo
    elif mode == 'critical':
        order = topological(graph.pred,graph.succ, [(-graph.upward[i],i) for i in range(graph.n)])
    else:
        order = graph.locality_order()
    target = max(max(graph.cycles), sum(graph.cycles)/(cores*grain))
    # Atomic units are connected runs in a topological order. This guarantees
    # a DAG quotient; unlike arbitrary affinity contraction it cannot create cycles.
    atomic, current, work = [],[],0
    for u in order:
        strong = bool(current and (current[-1] in graph.pred[u] or set(graph.inputs[u]) & set(graph.inputs[current[-1]])))
        component_break = bool(current and graph.component[u] != graph.component[current[-1]])
        if current and (component_break or (work >= target*config.weak_link_fraction and not strong) or work >= target*config.atomic_fraction):
            atomic.append(tuple(current))
            current, work = [],0
        current.append(u)
        work += graph.cycles[u]
    if current:
        atomic.append(tuple(current))
    # Second level greedily aggregates atomic units up to a work budget.
    blocks, current, work = [],[],0
    for unit in atomic:
        cost = sum(graph.cycles[u] for u in unit)
        join = not current or work+cost <= target
        if not join:
            blocks.append(tuple(current))
            current,work=[],0
        current.extend(unit)
        work += cost
    if current:
        blocks.append(tuple(current))
    return tuple(blocks)
