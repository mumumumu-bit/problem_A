# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
import pytest
from npu_scheduler.config import SolverConfig,StrategySelector


@pytest.mark.parametrize('field',['time_budget','max_evaluations','top_k','workers','candidate_pool'])
def test_invalid_config(field):
    with pytest.raises(ValueError): SolverConfig(**{field:0})


def test_strategy():
    config=SolverConfig(max_evaluations=100)
    assert StrategySelector.select(30000,config)[1].max_evaluations==20
