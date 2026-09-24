# 开源设计参考与使用范围

本轮未复制第三方算法实现或源代码，也未把外部项目当成赛题事实来源。实际阅读的上游文档如下。

| 项目 | 参考内容 | 本工程对应 |
|---|---|---|
| [NetworkX DAG API](https://networkx.org/documentation/stable/reference/algorithms/dag.html) | DAG 操作边界、确定性拓扑排序与最长路径 API 的组织 | GraphData、独立 topological 函数、显式异常；热循环自写稀疏数组，不依赖 NetworkX。 |
| [pytest 参数化测试](https://docs.pytest.org/en/stable/how-to/parametrize.html) | fixture、parametrize、不同参数组合复用测试 | minimal/branch fixture，问题1/2/3与核数1～5参数化。 |
| [Optuna Study](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.study.Study.html) | 将研究过程组织为 trial、保留记录和最佳结果 | trials.jsonl、incumbent.json、manifest.json；没有安装或运行 Optuna 调参。 |
| [Matplotlib 样式定制](https://matplotlib.org/stable/users/explain/customizing.html) | 集中 rcParams、样式复用 | style.py、固定算法颜色、PNG/PDF输出、可迁移字体。 |

OR-Tools、pymoo、joblib 本轮未实际引入或复制实现。并行使用 Python 标准库 ProcessPoolExecutor；未实现 CP-SAT、GA、SA，不把这些方法写作已完成贡献。SciencePlots 为可选样式插件，缺失时使用自定义 rcParams。
