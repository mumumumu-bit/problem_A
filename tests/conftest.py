# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
import pytest
from pathlib import Path
from npu_scheduler.graph import GraphData

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def hardware():
    return ROOT/'data/config.txt'


@pytest.fixture
def minimal_raw():
    return {'tensors':[{'id':i,'pos':'DDR' if i in (1,4) else 'UB','size':16} for i in range(1,5)],
        'ops':[{'id':10,'op':'COPY_IN','pipe':'PIPE_MTE2','cycles':1},
               {'id':11,'op':'ADD','pipe':'PIPE_V','cycles':4},
               {'id':12,'op':'COPY_OUT','pipe':'PIPE_MTE3','cycles':1}],
        'edges':[{'source':a,'target':b} for a,b in [(1,10),(10,2),(2,11),(11,3),(3,12),(12,4)]]}


@pytest.fixture
def minimal(minimal_raw):
    return GraphData(minimal_raw)


@pytest.fixture
def branch():
    # Eight independent two-op branches, one shared DDR input.
    raw={'ops':[dict(id=100,op='COPY_IN',pipe='PIPE_MTE2',cycles=1)],
         'tensors':[dict(id=1,pos='DDR',size=32),dict(id=2,pos='UB',size=32)],
         'edges':[dict(source=1,target=100),dict(source=100,target=2)]}
    for j in range(8):
        a=200+j*10
        raw['ops'].extend([dict(id=a,op='ADD',pipe='PIPE_V',cycles=30+j*20),
            dict(id=a+1,op='MUL',pipe='PIPE_M',cycles=70),dict(id=a+2,op='COPY_OUT',pipe='PIPE_MTE3',cycles=1)])
        raw['tensors'].extend(dict(id=a+i,pos='DDR' if i==5 else 'UB',size=32) for i in (3,4,5))
        raw['edges'].extend(dict(source=u,target=v) for u,v in [(2,a),(a,a+3),(a+3,a+1),(a+1,a+4),(a+4,a+2),(a+2,a+5)])
    return GraphData(raw,'branches')
