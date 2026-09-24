# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Eight bounded neighborhoods; invalid quotient orders are rejected early."""
from ..types import Solution
from ..schedule.core_assignment import block_view


def neighbors(graph, solution, kind, rng, limit):
    blocks,cores = solution.blocks,solution.cores
    n=len(blocks)
    if not n:
        return
    mapping,work,_,_,pred,succ,edges=block_view(graph,blocks)
    heavy=sorted(range(n),key=lambda b:-work[b])
    critical=sorted(range(n),key=lambda b:-max(graph.upward[u]+graph.downward[u] for u in blocks[b]))
    pairs=sorted(edges,key=lambda e:-edges[e])
    seen=set()
    for attempt in range(limit*3):
        b=(critical if kind==7 else heavy)[attempt % n] if attempt < n else rng.randrange(n)
        bs,cs=list(blocks),list(cores)
        if kind in (0,7):  # N1 move; N8 critical move
            cs[b]=(cs[b]+1+attempt//max(1,n))%solution.num_cores
        elif kind==1 and n>1:  # N2 swap core assignments
            d=rng.randrange(n)
            cs[b],cs[d]=cs[d],cs[b]
        elif kind==2 and n>1:  # N3 adjacent independent reordering
            b=attempt%(n-1); d=b+1
            if d in succ[b]:
                continue
            bs[b],bs[d]=bs[d],bs[b]
            cs[b],cs[d]=cs[d],cs[b]
        elif kind==3 and n>1:  # N4 adjacent merge (convex in block order)
            b=attempt%(n-1)
            bs[b]=bs[b]+bs[b+1]
            del bs[b+1]; del cs[b+1]
        elif kind==4:  # N5 split near half workload, not half node count
            if len(bs[b])<2:
                continue
            ordered=sorted(bs[b],key=lambda u:graph.topo_index[u])
            total=sum(graph.cycles[u] for u in ordered); acc=0; cut=1
            for j,u in enumerate(ordered[:-1],1):
                acc+=graph.cycles[u]; cut=j
                if acc>=total/2:
                    break
            bs[b:b+1]=[tuple(ordered[:cut]),tuple(ordered[cut:])]
            cs.insert(b+1,(cs[b]+1)%solution.num_cores)
        elif kind==5 and n>1:  # N6 shift a boundary op
            b=attempt%(n-1)
            if len(bs[b])<=1:
                continue
            u=max(bs[b],key=lambda u:graph.topo_index[u])
            bs[b]=tuple(v for v in bs[b] if v!=u)
            bs[b+1]=(u,)+bs[b+1]
        elif kind==6 and pairs:  # N7 connected block pair placement
            b,d=pairs[attempt%len(pairs)]
            target=(cs[b]+attempt//len(pairs))%solution.num_cores
            cs[b]=cs[d]=target
        else:
            continue
        candidate=Solution(tuple(bs),tuple(cs),solution.num_cores)
        key=candidate.digest()
        if key==solution.digest() or key in seen:
            continue
        try:
            candidate.validate(graph)
        except ValueError:
            continue
        seen.add(key)
        yield candidate
        if len(seen)>=limit:
            break

