# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
import json
import pytest
from npu_scheduler.types import Solution
from npu_scheduler.evaluator.official_adapter import OfficialEvaluator


@pytest.mark.parametrize('problem',[1,2,3])
def test_official_evaluator_smoke_and_cli(minimal,hardware,tmp_path,problem):
    s=Solution(((0,),),(0,),2)
    ev=OfficialEvaluator(minimal,hardware,problem,tmp_path/'cache')
    result=ev.evaluate(s)
    assert result.valid and result.makespan==6 and result.added_copy_bytes==0
    graph_path=tmp_path/'minimal_graph.json'; graph_path.write_text(json.dumps(minimal.raw),encoding='utf-8')
    assert ev.verify_cli(graph_path,s,tmp_path/'cli')['makespan']==6
    assert ev.singlecore()['makespan']==6


def test_persistent_cache(minimal,hardware,tmp_path):
    s=Solution(((0,),),(0,),2)
    a=OfficialEvaluator(minimal,hardware,1,tmp_path)
    a.evaluate(s)
    b=OfficialEvaluator(minimal,hardware,1,tmp_path)
    assert b.evaluate(s).makespan==6 and b.calls==0 and b.hits==1
    c=OfficialEvaluator(minimal,hardware,2,tmp_path)
    c.evaluate(s)
    assert c.calls==1


def test_cache_hardware_invalidation(minimal,hardware,tmp_path):
    s=Solution(((0,),),(0,),2)
    OfficialEvaluator(minimal,hardware,1,tmp_path/'cache').evaluate(s)
    changed=tmp_path/'config.txt'
    changed.write_text(hardware.read_text(encoding='utf-8').replace('bandwidth 60','bandwidth 1'),encoding='utf-8')
    other=OfficialEvaluator(minimal,changed,1,tmp_path/'cache')
    assert other.evaluate(s).makespan==36 and other.calls==1


def test_global_wait_cycle_is_rejected(branch,hardware):
    # Reversed cross-core branch dependencies and pipe order can create a wait cycle.
    # Official validation remains the final authority even for quotient-valid plans.
    plan={'node_to_subgraph':{str(oid):i for i,oid in enumerate(branch.op_ids)},
          'core_schedules':[[3,0]+list(range(4,16)),[1,2]]}
    for problem in (2,3):
        ev=OfficialEvaluator(branch,hardware,problem)
        with pytest.raises(ValueError,match='dependency cycle'):
            ev.raw(plan)
