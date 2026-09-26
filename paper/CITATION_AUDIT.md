# 参考文献审计

审计日期：2026-09-27。已审阅第1—10章全文，仅依据仓库正文、本次任务提供的4篇人工核验文献及原始来源；未使用旧聊天记录，未读取或复制2025参考论文的bibliography。逐项需求分类与正式参考文献见 `paper/REFERENCES_V1.md`。

4类核心外部知识由4篇文献覆盖，无需新增文献。原正文6处引用占位已清除，剩余0处；重复的HEFT思想引用集中到第5章导言，VNS原始论文引用与本文具体设计明确分开。

| 编号 | 文献名称 | 文献真实性 | 正文引用位置 | 支持的具体论断 | 核验状态 |
|---|---|---|---|---|---|
| [1] | Efficient Processing of Deep Neural Networks: A Tutorial and Survey | 用户已人工核验；IEEE记录与MIT作者公开原文交叉核对 | 1.1背景首句 | DNN加速器计算、存储层次与数据移动的权衡；搬运成本影响效率 | 作者、题名、105(12)、2295–2329、2017及DOI一致；原文第V节支持论断 |
| [2] | DAG Scheduling and Analysis on Multi-Core Systems by Modelling Parallelism and Dependency | 用户已人工核验；IEEE记录与York作者机构记录交叉核对 | 1.1背景第二句 | 多核DAG调度需共同考虑节点依赖与并行性 | 作者、题名、33(12)、4019–4038、2022及DOI一致；IEEE摘要支持论断 |
| [3] | Performance-Effective and Low-Complexity Task Scheduling for Heterogeneous Computing | 用户已人工核验；IEEE原始出版索引核对 | 第5章导言HEFT-style首次思想介绍 | HEFT类列表调度、upward rank与earliest-finish-time思想，对应5.3.4、5.4.2的借鉴说明 | 题名、13(3)、260–274、2002及DOI一致；摘要明确描述两项思想；作者沿用人工核验信息 |
| [4] | Variable Neighborhood Search | 用户已人工核验；Elsevier原始出版索引核对 | 第5章导言VNS首次正式思想介绍 | 在局部搜索中系统切换邻域结构 | 题名、24(11)、1097–1100、1997及DOI一致；摘要支持基本思想；作者沿用人工核验信息 |

## DOI与原始核验来源

- [1] [DOI](https://doi.org/10.1109/JPROC.2017.2761740)、[IEEE记录](https://ieeexplore.ieee.org/document/8114708/)、[MIT作者原文](https://eems.mit.edu/wp-content/uploads/2017/11/2017_pieee_dnn.pdf)。
- [2] [DOI](https://doi.org/10.1109/TPDS.2022.3177046)、[IEEE记录](https://ieeexplore.ieee.org/abstract/document/9779935)、[York作者机构记录](https://pure.york.ac.uk/portal/en/publications/dag-scheduling-and-analysis-on-multi-core-systems-by-modelling-pa/)。
- [3] [DOI](https://doi.org/10.1109/71.993206)、[IEEE记录](https://ieeexplore.ieee.org/document/993206/)。
- [4] [DOI](https://doi.org/10.1016/S0305-0548(97)00031-2)、[Elsevier记录](https://www.sciencedirect.com/science/article/pii/S0305054897000312)。

本次核验使用检索返回的原始出版索引、可访问的作者机构记录及作者原文；部分出版页直接打开受限，不声称均已通读全文。[2]第三方DBLP期号为10，与IEEE原始记录的12不同，采用IEEE记录及用户人工核验的33(12)；[1]MIT个别新闻页卷号有排版差异，采用IEEE记录及原文页脚的105卷。差异已由原始来源解决。

## 引用归因边界

- [1][2]不支持本题NPU参数、Task、DDR/L1/UB或共享L2配置。
- [3]只支持HEFT-style借鉴，本文不声称采用原始HEFT算法；块工作量、等待项、复用及流水线负载修正属于本文实现。
- [4]只支持VNS基本思想；本文8类邻域、strict descent、adaptive、Top-K与候选筛选不归给原始论文。
- 第2章VNS缩写仅为方法预告并指向第5章；第5章正式介绍思想并引用。第3—4章模型、5.8复杂度推导、第6章配置、第7—10章结果与统计、SA-VNS开发探索及未来方向均不追加无关外部引用。

## 尚需人工核验项目

无。没有新增AI推荐文献；本次4篇已由用户人工核验。

## 审计规则

- 不允许虚构文献。
- 不允许虚构作者。
- 不允许虚构DOI。
- 不允许虚构URL。
- 参考论文中的文献不能未经核验直接复制。
- AI推荐的文献必须人工核验后才能进入正文。
- 引用别人的成果或其他公开资料，必须在正文引用处和参考文献中明确列出；正文用方括号标明编号，如[1][3]。
- 书籍正文引用还必须指出页码；程序引用须注明来源。
- 参考文献按正文中的引用次序列出。

## 官方格式核对

- 书籍：`[编号] 作者，书名，出版地：出版社，起止页码，出版年。`
- 期刊：`[编号] 作者，论文名，期刊名，卷(期)：起止页码，出版年。`
- 网络资源：`[编号] 作者，资源标题，网址，访问时间（年月日）。`

上述引用要求与格式来自附件2；审计禁令是团队内部的真实性控制规则，用于防止把未经核验的信息写入正文。
