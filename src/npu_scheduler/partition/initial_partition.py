# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Four distinct seed families and a safe whole-graph fallback."""
from .coarsening import coarsen
from ..schedule.core_assignment import assign
from ..types import Solution


def seeds(graph, cores, problem, hardware, config):
    yield 'baseline', assign(graph,coarsen(graph,cores,config.grains[len(config.grains)//2],'balanced',config),cores,'balanced',problem,hardware,config)
    # Whole-graph candidate is also valuable for long chains and bandwidth limits.
    if graph.n <= config.whole_graph_max_ops:
        yield 'whole', Solution((tuple(graph.topo),) if graph.n else (), (0,) if graph.n else (),cores)
    # Cover all four families and coarse/fine scales before spending time on
    # redundant grid points. Large-case seed deadlines may truncate the grid.
    first=[('affinity',config.grains[0]),('critical',config.grains[len(config.grains)//2]),
           ('pipe',config.grains[-1]),('balanced',config.grains[-1])]
    grid=first+[(mode,grain) for grain in config.grains for mode in ('affinity','critical','pipe','balanced')]
    used=set()
    for mode,grain in grid:
        if (mode,grain) not in used:
            used.add((mode,grain))
            yield f'{mode}-{grain}', assign(graph,coarsen(graph,cores,grain,mode,config),cores,mode,problem,hardware,config)
