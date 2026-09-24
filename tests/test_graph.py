# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
import copy
import pytest
from npu_scheduler.graph import GraphData


def test_json_loading(minimal_raw,tmp_path):
    import json
    path=tmp_path/'中文 图.json'; path.write_text(json.dumps(minimal_raw),encoding='utf-8')
    assert GraphData.load(path).op_ids==(11,)


def test_duplicate_json_key(tmp_path):
    path=tmp_path/'bad.json'; path.write_text('{"ops":[],"ops":[],"tensors":[],"edges":[]}')
    with pytest.raises(ValueError,match='duplicate JSON'):
        GraphData.load(path)


def test_op_dag(branch):
    assert branch.n==16 and len(branch.components)==8
    assert branch.critical_length==240
    assert branch.tensors[1].consumers==tuple(range(0,16,2))


def test_topological_order(branch):
    for order in (branch.topo,branch.locality_order()):
        rank={u:i for i,u in enumerate(order)}
        assert len(rank)==branch.n
        assert all(rank[u]<rank[v] for u in range(branch.n) for v in branch.succ[u])


@pytest.mark.parametrize('change',['cycle','duplicate','negative','endpoint','pipe'])
def test_invalid_graph(minimal_raw,change):
    raw=copy.deepcopy(minimal_raw)
    if change=='cycle': raw['edges'].append(dict(source=3,target=11))
    elif change=='duplicate': raw['ops'][0]['id']=1
    elif change=='negative': raw['tensors'][0]['size']=-1
    elif change=='endpoint': raw['edges'][0]['source']=999
    else: raw['ops'][0]['pipe']='GUESS'
    with pytest.raises(ValueError): GraphData(raw)


def test_copy_contraction(minimal_raw):
    raw=copy.deepcopy(minimal_raw)
    raw['ops'].append(dict(id=13,op='ADD',pipe='PIPE_V',cycles=7))
    raw['edges'].append(dict(source=4,target=13))
    graph=GraphData(raw)
    assert graph.pred[1]==(0,)
