# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""HEFT-style ready list and earliest finish assignment on coarse DAGs."""
from collections import defaultdict
from ..types import Solution
from ..graph import topological


def block_view(graph, blocks):
    mapping = [0]*graph.n
    work, pipe_work, inputs = [], [], []
    for b,members in enumerate(blocks):
        pipes = defaultdict(int)
        ins = set()
        for u in members:
            mapping[u] = b
            pipes[graph.pipe[u]] += graph.cycles[u]
            ins.update(graph.inputs[u])
        pipe_work.append(dict(pipes))
        work.append(max(pipes.values(),default=0))
        inputs.append(ins)
    pred, succ = [set() for _ in blocks], [set() for _ in blocks]
    edges = defaultdict(int)
    for u in range(graph.n):
        for v in graph.succ[u]:
            a,b = mapping[u],mapping[v]
            if a != b:
                pred[b].add(a)
                succ[a].add(b)
                edges[a,b] += graph.edge_bytes.get((u,v),0)
    return mapping,work,pipe_work,inputs,pred,succ,edges


def assign(graph, blocks, cores, mode, problem, hardware, config):
    _,work,pipes,inputs,pred,succ,edges = block_view(graph,blocks)
    rank = [0]*len(blocks)
    topo = topological(pred,succ)
    for b in reversed(topo):
        rank[b] = work[b] + max((rank[v]+edges[b,v]/hardware['bandwidth'] for v in succ[b]),default=0)
    order = topological(pred,succ, [(-rank[b],b) for b in range(len(blocks))]) if mode in ('critical','pipe') else topo
    end, assignment = [0.0]*len(blocks), [0]*len(blocks)
    available, totals = [0.0]*cores, [defaultdict(float) for _ in range(cores)]
    resident = [set() for _ in range(cores)]
    for b in order:
        options=[]
        for c in range(cores):
            if mode == 'balanced':
                score = sum(totals[c].values())
                finish = available[c]+work[b]
            else:
                ready = max((end[p]+(hardware['cross_wait']+edges[p,b]/hardware['bandwidth']
                           if assignment[p] != c else 0) for p in pred[b]),default=0)
                finish = max(available[c]+(hardware['same_wait'] if available[c] else 0),ready)+work[b]
                reuse = sum(graph.tensors[t].size for t in inputs[b]&resident[c])/hardware['bandwidth']
                affinity = config.affinity_weight*reuse if mode in ('affinity','pipe') else 0
                balance = max((totals[c][p]+pipes[b].get(p,0) for p in ('PIPE_M','PIPE_V')), default=0)
                score = finish-affinity+(config.pipe_balance_weight*balance if mode == 'pipe' else 0)
            options.append((score,c,finish))
        _,c,finish = min(options)
        assignment[b],end[b],available[c]=c,finish,finish
        resident[c].update(inputs[b])
        for p,w in pipes[b].items():
            totals[c][p] += w
    return Solution(tuple(blocks[b] for b in order),tuple(assignment[b] for b in order),cores)
