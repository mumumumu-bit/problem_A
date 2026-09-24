# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Four distinct seed families, fine-grain variants, and a safe whole-graph fallback."""
from .coarsening import coarsen
from ..schedule.core_assignment import assign
from ..types import Solution


def seeds(graph, cores, problem, hardware, config):
    yield 'baseline', assign(graph,coarsen(graph,cores,config.grains[len(config.grains)//2],'balanced',config),cores,'balanced',problem,hardware,config)
    # Whole-graph candidate is also valuable for long chains and bandwidth limits.
    if graph.n <= config.whole_graph_max_ops:
        yield 'whole', Solution((tuple(graph.topo),) if graph.n else (), (0,) if graph.n else (),cores)
    # Portfolio: Cover all four families at coarse/fine scales.
    # Extra-fine grain (e.g. grain=2) recovers v1-like pipe behaviour that
    # produced better VNS outcomes on case_019.
    extra_grains = [config.fine_grain] if config.fine_grain not in config.grains else []
    all_grains = tuple(config.grains) + tuple(extra_grains)
    first=[('affinity',all_grains[0]),('critical',all_grains[len(config.grains)//2]),
           ('pipe',all_grains[-1]),('balanced',all_grains[-1])]
    grid=first+[(mode,grain) for grain in all_grains for mode in ('affinity','critical','pipe','balanced')]
    used, count = set(), 0
    for mode,grain in grid:
        if (mode,grain) not in used and count < config.portfolio_size:
            used.add((mode,grain))
            count += 1
            yield f'{mode}-{grain}', assign(graph,coarsen(graph,cores,grain,mode,config),cores,mode,problem,hardware,config)
