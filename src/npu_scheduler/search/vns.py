# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Multi-seed search with bounded SA escape, budget accounting and trial logs."""
from dataclasses import asdict
import math
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
    current_solution,current_value=None,None
    best_solution,best_value,best_name=None,None,None
    trials,seen=[],set()
    snapshots={}
    evaluated=0
    temperature=config.sa_initial_temp
    uphill_accepts=0
    # Adaptive neighbourhood tracking
    neighbourhood_stats = {k: dict(attempts=0,successes=0,gain=0.0,eval_time=0.0)
                           for k in range(8)}

    def budget():
        return evaluated<config.max_evaluations and time.perf_counter()-start<config.time_budget

    def consider(name,solution,allow_uphill=False):
        nonlocal current_solution,current_value,best_solution,best_value,best_name
        nonlocal evaluated,temperature,uphill_accepts
        if not budget():
            return False,False
        key=solution.digest()
        if key in seen:
            return False,False
        seen.add(key)
        prediction=estimate(graph,solution,evaluator.problem,hw,config,diagnostics=True)
        result=evaluator.evaluate(solution)
        evaluated+=1
        is_global_best=result.valid and (best_value is None or result.objective<best_value.objective)
        accepted=False
        accept_reason='rejected'
        delta_relative=None
        strict_improvement=False
        if result.valid and current_value is None:
            accepted=True
            strict_improvement=True
            accept_reason='strict_improvement'
        elif result.valid and result.makespan < current_value.makespan:
            accepted=True
            strict_improvement=True
            accept_reason='strict_improvement'
        elif (result.valid and result.makespan == current_value.makespan
              and result.added_copy_bytes < current_value.added_copy_bytes):
            accepted=True
            strict_improvement=True
            accept_reason='same_makespan_lower_copy'
        elif result.valid and result.makespan > current_value.makespan:
            delta_relative=(result.makespan-current_value.makespan)/current_value.makespan
            if (allow_uphill and config.sa_enabled
                    and uphill_accepts < config.sa_max_uphill_accepts
                    and rng.random() < math.exp(-delta_relative/temperature)):
                accepted=True
                accept_reason='sa_uphill'
                uphill_accepts+=1
                temperature=max(config.sa_min_temp,temperature*config.sa_cooling)
        if accepted:
            current_solution,current_value=solution,result
        if is_global_best:
            best_solution,best_value,best_name=solution,result,name
            if config.sa_enabled:
                temperature=config.sa_initial_temp
        trial=dict(number=len(trials),name=name,solution_hash=key,elapsed=time.perf_counter()-start,
                   improved=is_global_best,accepted=accepted,accept_reason=accept_reason,
                   temperature=temperature,delta_relative=delta_relative,
                   is_global_best=is_global_best,**prediction,**asdict(result))
        trials.append(trial)
        if on_trial:
            on_trial(trial,best_solution,best_value)
        return accepted,strict_improvement

    def snapshot():
        return dict(solution=best_solution,evaluation=best_value,seconds=time.perf_counter()-start,
                    evaluations=evaluated,source=best_name)

    families=set()
    for name,solution in seeds(graph,cores,evaluator.problem,hw,config):
        if best_solution is not None and (algorithm=='baseline' or not budget()):
            break
        if (best_solution is not None and algorithm=='vns' and len(families)>=4
                and time.perf_counter()-start>=config.time_budget*config.seed_budget_fraction):
            break
        consider(name,solution)
        if name!='whole':
            families.add('balanced' if name=='baseline' else name.split('-')[0])
        if name=='baseline' and best_value is not None:
            snapshots['baseline']=snapshot()
        elif 'baseline' not in snapshots and best_value is not None:
            snapshots['baseline']=snapshot()
    if best_solution is None:
        consider('emergency-whole',Solution((tuple(graph.topo),) if graph.n else (), (0,) if graph.n else (),cores))
        if best_solution is not None:
            snapshots['baseline']=snapshot()
    if best_solution is None:
        raise RuntimeError('No officially executable seed: '+str(trials[-1:] ))
    snapshots['multiseed']=snapshot()
    if algorithm=='vns':
        # --- Adaptive VNS with neighbourhood budget tracking and early stopping ---
        # Neighbourhood priorities (0-indexed: N1=0 ... N8=7)
        # High: N1(0), N2(1); Medium: N4(3), N5(4); Low: N3(2), N6(5), N7(6), N8(7)
        default_order = [0, 1, 3, 4, 2, 5, 7, 6]
        active_neighbourhoods = set(default_order)
        kind = 0
        rounds = 0
        stagnation_count = 0
        last_improvement_at = evaluated

        def neighbourhood_index(order_idx):
            return default_order[order_idx % len(default_order)]

        def select_neighbourhood():
            """Adaptive selection: prefer neighbourhoods with high historical gain per eval,
            but enforce minimum exploration for all active neighbourhoods."""
            nonlocal active_neighbourhoods
            if not config.adaptive_budget or rounds < 8:
                # Initial rounds: use default order for warm-up data collection
                return neighbourhood_index(rounds)
            # Check which neighbourhoods are below minimum exploration
            under_explored = [k for k in active_neighbourhoods
                              if neighbourhood_stats[k]['attempts'] < config.min_neighbourhood_trials]
            if under_explored:
                return under_explored[0]
            # Greedy: pick neighbourhood with highest gain_per_eval from recent history
            scores = {}
            for k in active_neighbourhoods:
                s = neighbourhood_stats[k]
                attempts = max(s['attempts'], 1)
                gain_per_eval = s['gain'] / attempts
                # Add small epsilon for neighbourhoods with zero attempts to ensure diversity
                scores[k] = gain_per_eval if s['attempts'] > 0 else -1.0
            # Pick best, with 20% chance of random exploration among active
            if rng.random() < 0.2:
                return rng.choice(sorted(active_neighbourhoods))
            return max(scores, key=scores.get)

        kind = select_neighbourhood()
        while budget() and rounds < config.max_rounds and kind < 8 and len(active_neighbourhoods) > 0:
            candidates = [s for s in neighbors(graph, current_solution, kind, rng, config.candidate_pool)
                          if s.digest() not in seen]
            ranked = sorted(candidates, key=lambda s: (estimate(graph, s, evaluator.problem, hw, config), s.digest()))
            improved = False
            allow_uphill=(config.sa_enabled and stagnation_count>=config.sa_stagnation_trigger
                          and uphill_accepts<config.sa_max_uphill_accepts)
            for candidate in ranked[:config.top_k]:
                if not budget():
                    break
                before = current_value
                t_start = time.perf_counter()
                accepted,strict_improvement = consider(f'N{kind+1}',candidate,allow_uphill)
                t_elapsed = time.perf_counter() - t_start
                # Update neighbourhood statistics
                neighbourhood_stats[kind]['attempts'] += 1
                neighbourhood_stats[kind]['eval_time'] += t_elapsed
                if strict_improvement:
                    allow_uphill = False
                    neighbourhood_stats[kind]['successes'] += 1
                    if before is not None:
                        gain = before.makespan - current_value.makespan
                        neighbourhood_stats[kind]['gain'] += gain
                    improved = True

            # Adaptive: deactivate consistently unproductive neighbourhoods
            if config.adaptive_budget and rounds > 8:
                for k in list(active_neighbourhoods):
                    s = neighbourhood_stats[k]
                    if s['attempts'] >= max(6, config.min_neighbourhood_trials * 2) and s['successes'] == 0:
                        # N3-like behaviour: many attempts, zero success → deactivate
                        active_neighbourhoods.discard(k)

            # Early stopping: stale search detection
            if improved:
                stagnation_count = 0
                last_improvement_at = evaluated
            else:
                stagnation_count += 1

            # Dynamic early stop: stop if no improvement for too long
            # Threshold scales with graph size (larger graphs need more patience)
            patience = config.stagnation_patience
            if graph.n > 10000:
                patience = max(patience, config.stagnation_patience + 2)
            if config.adaptive_budget and stagnation_count >= patience and evaluated > last_improvement_at + patience:
                break

            # Neighbourhood transition: stay on current if improved, else move to next
            if improved:
                kind = select_neighbourhood() if config.adaptive_budget else 0
            else:
                kind = select_neighbourhood() if config.adaptive_budget else kind + 1
            rounds += 1
    snapshots['vns']=snapshot()
    return dict(solution=best_solution,evaluation=best_value,trials=trials,snapshots=snapshots,
                seconds=time.perf_counter()-start,scale=scale,config=config.to_dict(),
                evaluator_calls=evaluator.calls,cache_hits=evaluator.hits,evaluator_seconds=evaluator.seconds,
                neighbourhood_stats={f'N{k+1}': v for k, v in neighbourhood_stats.items()})
