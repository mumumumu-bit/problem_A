# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
import random
import pytest
from npu_scheduler.config import SolverConfig
from npu_scheduler.types import Solution
from npu_scheduler.partition.initial_partition import seeds
from npu_scheduler.search.local_search import neighbors
from npu_scheduler.search.vns import hardware_view,solve
from npu_scheduler.evaluator.official_adapter import OfficialEvaluator


@pytest.mark.parametrize('cores',[1,2,3,4,5])
def test_partition_and_core_schedule_complete(branch,hardware,cores):
    ev=OfficialEvaluator(branch,hardware,1)
    for _,s in seeds(branch,cores,1,hardware_view(ev),SolverConfig()):
        assert s.validate(branch)
        plan=s.plan(branch)
        assert len(plan['node_to_subgraph'])==branch.n
        flat=sum(plan['core_schedules'],[])
        assert sorted(flat)==list(range(len(s.blocks)))
        assert ev.evaluate(s).valid


@pytest.mark.parametrize('kind',range(8))
def test_neighborhood_legality(branch,hardware,kind):
    s=Solution(tuple((u,) for u in branch.topo),tuple(u%2 for u in branch.topo),2)
    if kind in (4,5):
        s=Solution(tuple(tuple(branch.topo[i:i+2]) for i in range(0,branch.n,2)),tuple(i%2 for i in range(branch.n//2)),2)
    candidates=list(neighbors(branch,s,kind,random.Random(2026),12))
    assert candidates
    assert all(c.validate(branch) for c in candidates)


@pytest.mark.parametrize('kind',['missing','duplicate','reversed','core'])
def test_reject_invalid_solution(branch,kind):
    blocks=tuple((u,) for u in branch.topo); cores=(0,)*len(blocks)
    if kind=='missing': blocks=blocks[:-1]; cores=cores[:-1]
    elif kind=='duplicate': blocks=blocks[:-1]+(blocks[0],)
    elif kind=='reversed': blocks=tuple(reversed(blocks))
    else: cores=(2,)*len(blocks)
    with pytest.raises(ValueError): Solution(blocks,cores,2).validate(branch)


def test_solution_serialization(branch):
    s=Solution(tuple((u,) for u in branch.topo),(0,)*branch.n,2)
    restored=Solution.from_plan(branch,s.plan(branch))
    assert restored.plan(branch)==s.plan(branch)


def test_reproducibility_and_monotonicity(branch,hardware):
    cfg=SolverConfig(max_evaluations=24,time_budget=30)
    a=solve(branch,2,OfficialEvaluator(branch,hardware,1),cfg)
    b=solve(branch,2,OfficialEvaluator(branch,hardware,1),cfg)
    assert a['solution']==b['solution']
    assert a['evaluation'].objective==b['evaluation'].objective
    snapshots=a['snapshots']
    assert snapshots['vns']['evaluation'].objective<=snapshots['multiseed']['evaluation'].objective<=snapshots['baseline']['evaluation'].objective
