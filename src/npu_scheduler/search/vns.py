# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Multi-seed search with monotone incumbent, budget accounting and trial logs."""
from dataclasses import asdict
import random
import time
from ..config import StrategySelector
from ..partition.initial_partition import seeds
from ..schedule.estimator import estimate
from ..types import Solution
from .local_search import neighbors


def hardware_view(evaluator):
    return dict(evaluator.hardware,
        cross_wait=evaluator.scene_a['task_cross_core_wait_cycles'] if evaluator.problem==1 else evaluator.scene_b['cross_core_copy_delay_cycles'],
        same_wait=evaluator.scene_a['task_same_core_wait_cycles'] if evaluator.problem==1 else 0,
        cache_capacity=evaluator.cache_settings['cache_capacity_bytes'],
        cache_bandwidth=evaluator.cache_settings['cache_bandwidth_bytes_per_cycle'])


def solve(graph,cores,evaluator,config,algorithm='vns',on_trial=None):
    if algorithm not in ('baseline','multiseed','vns'):
        raise ValueError('unknown algorithm')
    if cores<1:
        raise ValueError('cores must be positive')
    scale,config=StrategySelector.select(graph.n,config)
    hw=hardware_view(evaluator)
    rng=random.Random(config.seed)
    start=time.perf_counter()
    incumbent,value,best_name=None,None,None
    trials,seen=[],set()
    snapshots={}
    evaluated=0

    def budget():
        return evaluated<config.max_evaluations and time.perf_counter()-start<config.time_budget

    def consider(name,solution):
        nonlocal incumbent,value,best_name,evaluated
        key=solution.digest()
        if key in seen:
            return False
        seen.add(key)
        prediction=estimate(graph,solution,evaluator.problem,hw,config,diagnostics=True)
        result=evaluator.evaluate(solution)
        evaluated+=1
        improved=result.valid and (value is None or result.objective<value.objective)
        if improved:
            incumbent,value,best_name=solution,result,name
        trial=dict(number=len(trials),name=name,solution_hash=key,elapsed=time.perf_counter()-start,
                   improved=improved,**prediction,**asdict(result))
        trials.append(trial)
        if on_trial:
            on_trial(trial,incumbent,value)
        return improved

    def snapshot():
        return dict(solution=incumbent,evaluation=value,seconds=time.perf_counter()-start,
                    evaluations=evaluated,source=best_name)

    families=set()
    for name,solution in seeds(graph,cores,evaluator.problem,hw,config):
        if incumbent is not None and (algorithm=='baseline' or not budget()):
            break
        if (incumbent is not None and algorithm=='vns' and len(families)>=4
                and time.perf_counter()-start>=config.time_budget*config.seed_budget_fraction):
            break
        consider(name,solution)
        if name!='whole':
            families.add('balanced' if name=='baseline' else name.split('-')[0])
        if name=='baseline' and value is not None:
            snapshots['baseline']=snapshot()
        # If the nominal baseline has a global wait cycle, whole-graph fallback
        # is recorded explicitly; never label an invalid score as a baseline.
        elif 'baseline' not in snapshots and value is not None:
            snapshots['baseline']=snapshot()
    if incumbent is None:
        consider('emergency-whole',Solution((tuple(graph.topo),) if graph.n else (), (0,) if graph.n else (),cores))
        if incumbent is not None:
            snapshots['baseline']=snapshot()
    if incumbent is None:
        raise RuntimeError('No officially executable seed: '+str(trials[-1:] ))
    snapshots['multiseed']=snapshot()
    if algorithm=='vns':
        kind,rounds=0,0
        while budget() and rounds<config.max_rounds and kind<8:
            candidates=[s for s in neighbors(graph,incumbent,kind,rng,config.candidate_pool) if s.digest() not in seen]
            ranked=sorted(candidates,key=lambda s:(estimate(graph,s,evaluator.problem,hw,config),s.digest()))
            improved=False
            for candidate in ranked[:config.top_k]:
                if not budget():
                    break
                if consider(f'N{kind+1}',candidate):
                    improved=True
            kind=0 if improved else kind+1
            rounds+=1
    snapshots['vns']=snapshot()
    return dict(solution=incumbent,evaluation=value,trials=trials,snapshots=snapshots,
                seconds=time.perf_counter()-start,scale=scale,config=config.to_dict(),
                evaluator_calls=evaluator.calls,cache_hits=evaluator.hits,evaluator_seconds=evaluator.seconds)
