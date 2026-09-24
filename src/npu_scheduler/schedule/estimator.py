# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Cheap surrogates are ranking signals, never substitutes for official scores."""
from collections import defaultdict
from .core_assignment import block_view


def estimate(graph, solution, problem, hw, config, diagnostics=False):
    mapping,work,pipes,inputs,pred,_,edges = block_view(graph,solution.blocks)
    end, start = [0.0]*len(work), [0.0]*len(work)
    available = [0.0]*solution.num_cores
    total_pipe = [defaultdict(float) for _ in available]
    for b,c in enumerate(solution.cores):
        ready = max((end[p]+(hw['cross_wait']+edges[p,b]/hw['bandwidth']
                    if solution.cores[p] != c else 0) for p in pred[b]),default=0)
        start[b] = max(ready,available[c]+(hw['same_wait'] if available[c] else 0))
        end[b] = start[b]+work[b]
        available[c] = end[b]
        for p,w in pipes[b].items():
            total_pipe[c][p] += w
    communication = 0
    touches = defaultdict(list)
    reuse_events=[]
    for t in graph.tensors:
        ps = {mapping[p] if problem == 1 else solution.cores[mapping[p]] for p in t.producers}
        cs = {mapping[c] if problem == 1 else solution.cores[mapping[c]] for c in t.consumers}
        if not ps:
            communication += t.size*len(cs)
        elif problem == 1:
            communication += t.size*(len(cs-ps)+int(bool(cs-ps) or t.final_output or not cs))
        else:
            communication += 2*t.size*sum(p != c for p in ps for c in cs)
            if t.final_output or not cs:
                communication += t.size*len(ps)
        if diagnostics or config.memory_weight:
            positions=defaultdict(list)
            for u in t.producers+t.consumers:
                b=mapping[u]
                unit=b if problem == 1 else solution.cores[b]
                positions[unit].append(b)
            for unit,bs in positions.items():
                if t.position != 'DDR':
                    touches[unit,t.position].extend(((min(bs)*2,t.size),(max(bs)*2+1,-t.size)))
        if problem == 3 and (diagnostics or config.cache_weight) and not ps and len(cs)>1:
            # Reuse-distance proxy: estimate distinct bytes between first-use
            # arrivals. Require first DDR read to finish; simultaneous misses
            # do not count as hits. No FIFO simulator is duplicated here.
            first={}
            for u in t.consumers:
                b=mapping[u]; c=solution.cores[b]
                first[c]=min(first.get(c,float('inf')),start[b])
            reuse_events.extend((time,t.id,t.size) for time in first.values())
    memory=0.0
    for (_,pos),events in touches.items():
        live,peak=0,0
        for _,delta in sorted(events):
            live+=delta; peak=max(peak,live)
        memory+=max(0,peak-hw['capacity'][pos])
    seen, distinct_bytes, hit = {},0,0
    for time,tid,size in sorted(reuse_events):
        old=seen.get(tid)
        if old and time >= old[0]+size/hw['bandwidth'] and distinct_bytes-old[1]+size <= hw['cache_capacity']:
            hit+=size
        elif size <= hw['cache_capacity']:
            distinct_bytes+=size
            seen[tid]=(time,distinct_bytes)
    cache_saving=hit*(1/hw['bandwidth']-1/hw['cache_bandwidth'])
    score=max(max(end,default=0),communication/hw['bandwidth'])
    score+=config.communication_weight*communication/hw['bandwidth']
    score+=config.memory_weight*memory/hw['bandwidth']-config.cache_weight*cache_saving
    return dict(score=score,communication_bytes=communication,memory_excess=memory,
                cache_reuse_bytes=hit) if diagnostics else score

