# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Sparse graph views, tensor hyperedges and deterministic iterative DAG algorithms."""
from collections import Counter
from dataclasses import dataclass
import heapq
import hashlib
import json
from pathlib import Path


def topological(pred, succ, keys=None):
    degree = list(map(len, pred))
    keys = list(range(len(pred))) if keys is None else keys
    ready = [(keys[i], i) for i, d in enumerate(degree) if not d]
    heapq.heapify(ready)
    order = []
    while ready:
        _, u = heapq.heappop(ready)
        order.append(u)
        for v in succ[u]:
            degree[v] -= 1
            if degree[v] == 0:
                heapq.heappush(ready, (keys[v], v))
    if len(order) != len(pred):
        raise ValueError('dependency cycle')
    return tuple(order)


@dataclass(frozen=True)
class Tensor:
    id: int
    position: str
    size: int
    producers: tuple[int, ...]
    consumers: tuple[int, ...]
    final_output: bool


class GraphData:
    def __init__(self, raw, name='graph'):
        # Use official input checks, including COPY nodes and duplicate edges.
        from .evaluator.official_adapter import official_modules
        official_modules()['validation'].validate_graph(raw)
        self.raw, self.name = raw, name
        self.fingerprint = hashlib.sha256(json.dumps(raw, separators=(',', ':')).encode()).hexdigest()
        all_ops = {o['id']: o for o in raw['ops']}
        ops = sorted((o for o in raw['ops'] if o['op'] not in ('COPY_IN', 'COPY_OUT')), key=lambda o: o['id'])
        self.op_ids = tuple(o['id'] for o in ops)
        self.index = {oid: i for i, oid in enumerate(self.op_ids)}
        self.n = len(ops)
        self.op_type = tuple(o['op'] for o in ops)
        self.pipe = tuple(o['pipe'] for o in ops)
        self.cycles = tuple(max(1, o['cycles']) for o in ops)
        producers, consumers = {}, {}
        full_succ = {i: set() for i in all_ops}
        self.direct_bytes = {}
        for e in raw['edges']:
            u, v = e['source'], e['target']
            if u in all_ops and v in all_ops:
                full_succ[u].add(v)
                if u in self.index and v in self.index:
                    self.direct_bytes[self.index[u], self.index[v]] = e.get('data_size', 0)
            elif u in all_ops:
                producers.setdefault(v, []).append(u)
            else:
                consumers.setdefault(u, []).append(v)
        for tid, ps in producers.items():
            for p in ps:
                full_succ[p].update(consumers.get(tid, ()))
        succ = [set() for _ in ops]
        for oid, i in self.index.items():
            stack, seen = list(full_succ[oid]), set()
            while stack:
                dst = stack.pop()
                if dst in self.index:
                    succ[i].add(self.index[dst])
                elif dst not in seen:
                    seen.add(dst)
                    stack.extend(full_succ[dst])
        pred = [set() for _ in ops]
        for u, vs in enumerate(succ):
            for v in vs:
                pred[v].add(u)
        self.pred = tuple(tuple(sorted(p)) for p in pred)
        self.succ = tuple(tuple(sorted(s)) for s in succ)
        self.topo = topological(self.pred, self.succ)
        self.topo_index = [0] * self.n
        self.depth, self.downward, self.upward = [0]*self.n, [0]*self.n, [0]*self.n
        for k, u in enumerate(self.topo):
            self.topo_index[u] = k
            self.depth[u] = max((self.depth[p] + 1 for p in pred[u]), default=0)
            self.downward[u] = max((self.downward[p] + self.cycles[p] for p in pred[u]), default=0)
        for u in reversed(self.topo):
            self.upward[u] = self.cycles[u] + max((self.upward[v] for v in succ[u]), default=0)
        self.critical_length = max(self.upward, default=0)
        self.critical = tuple(i for i in self.topo if self.downward[i]+self.upward[i] == self.critical_length)
        self.tensors = []
        self.inputs, self.outputs = [[] for _ in ops], [[] for _ in ops]
        self.edge_bytes = dict(self.direct_bytes)
        for t in sorted(raw['tensors'], key=lambda t: t['id']):
            tid = t['id']
            ps = tuple(sorted(self.index[p] for p in producers.get(tid, ()) if p in self.index))
            cs = tuple(sorted(self.index[c] for c in consumers.get(tid, ()) if c in self.index))
            final = any(all_ops[c]['op'] == 'COPY_OUT' for c in consumers.get(tid, ()))
            tx = len(self.tensors)
            self.tensors.append(Tensor(tid, t['pos'], t['size'], ps, cs, final))
            for p in ps:
                self.outputs[p].append(tx)
            for c in cs:
                self.inputs[c].append(tx)
            for p in ps:
                for c in cs:
                    self.edge_bytes[p,c] = self.edge_bytes.get((p,c), 0)+t['size']
        self.input_bytes = [sum(self.tensors[t].size for t in ts) for ts in self.inputs]
        self.output_bytes = [sum(self.tensors[t].size for t in ts) for ts in self.outputs]
        self.pipe_work = dict(Counter())
        for p,c in zip(self.pipe,self.cycles):
            self.pipe_work[p] = self.pipe_work.get(p,0)+c
        # Weak components of eligible-op DAG preserve independent branches even
        # when they share an input tensor. No dense pairwise affinity matrix.
        self.component = [-1]*self.n
        self.components = []
        for root in self.topo:
            if self.component[root] >= 0:
                continue
            cid, stack, members = len(self.components), [root], []
            self.component[root] = cid
            while stack:
                u = stack.pop()
                members.append(u)
                for v in self.pred[u]+self.succ[u]:
                    if self.component[v] < 0:
                        self.component[v] = cid
                        stack.append(v)
            self.components.append(tuple(members))

    @classmethod
    def load(cls, path):
        from .evaluator.official_adapter import official_modules
        return cls(official_modules()['io']._read_json(path), Path(path).stem)

    def features(self):
        return dict(case=self.name, ops=len(self.raw['ops']), eligible_ops=self.n,
                    tensors=len(self.tensors), edges=len(self.raw['edges']),
                    critical_path=self.critical_length, depth=max(self.depth, default=0),
                    width=max(Counter(self.depth).values(), default=0),
                    components=len(self.components), pipe_M=self.pipe_work.get('PIPE_M',0),
                    pipe_V=self.pipe_work.get('PIPE_V',0),
                    communication_compute_ratio=sum(self.edge_bytes.values())/max(1,sum(self.cycles)),
                    max_fan_in=max(map(len,self.pred),default=0),
                    max_fan_out=max(map(len,self.succ),default=0))

    def locality_order(self):
        # Iterative predecessor-first DFS; group branches while retaining DAG order.
        done, order = set(), []
        for root in sorted(range(self.n), key=lambda i:(self.component[i],bool(self.succ[i]),-self.downward[i],i)):
            stack = [(root,False)]
            while stack:
                u, expanded = stack.pop()
                if u in done:
                    continue
                if expanded:
                    done.add(u)
                    order.append(u)
                else:
                    stack.append((u,True))
                    stack.extend((p,False) for p in sorted(self.pred[u], key=lambda p:(self.edge_bytes.get((p,u),0),p)))
        return tuple(order)
