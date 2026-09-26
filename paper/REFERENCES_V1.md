# 最小必要参考文献配置 V1

审计日期：2026-09-27。已读取 `CITATION_AUDIT.md` 与 `sections/01_problem.md` 至 `sections/10_evaluation.md` 全文。4类核心外部知识需求由4篇已人工核验文献覆盖，无需增加文献。原正文有6处引用占位；下表逐处分类，同时列出未标记的外部知识与易被误判为引用需求的位置。重复位置不重复计为新的知识类别。

## 1. 引用需求审计

A＝必须引用；B＝建议引用；C＝不需要外部引用。A用于明确借鉴外部方法或介绍学术思想，B用于一般背景，C用于题面、本文设计、本文结果、直接推导及编辑说明。

| 正文位置 | 原论断 | 是否需引用 | 使用文献 | 原因 |
|---|---|---|---|---|
| 1.1原占位① | “DAG上的多核NPU调度研究”；占位挂在含题面通信与共享L2规则的整段后 | B：一般DAG背景；题面为C | [2]，移至独立背景句 | 多核DAG文献支持依赖和并行性，不支持本题NPU机制 |
| 1.1未标记背景线索 | “不同划分会改变并行空间、跨任务数据搬运以及核内缓存的使用” | B：一般加速器背景；本题划分后果为C | [1]，移至独立背景句 | 概括计算、存储和数据移动权衡，不把综述当作本题具体划分机制的证明 |
| 2.1、2.2未标记知识 | “图依赖限制可并行执行的操作和子图顺序”；需考虑DAG依赖及并行机会 | B：同一DAG背景 | [2]，已在1.1引用 | 此处结合题面分析，不重复挂同一背景论文 |
| 第5章导言原占位② | “经典ready-list/HEFT与VNS背景需要外部文献支持的位置暂记为……” | C：编辑说明；替换后的正式思想介绍为A | [3][4] | 删除编辑说明，分别介绍HEFT-style与VNS思想，先[3]后[4] |
| 5.1步骤4原占位③ | “受HEFT启发的ready-list调度” | A：方法借鉴 | [3]，导言首次引用 | 明确HEFT-style，后续流程不重复挂原论文 |
| 5.1步骤6原占位④ | “从8类邻域中的一个生成有界候选池……Top-K送入官方Evaluator” | C：本文设计 | 无；VNS基本思想在导言引[4] | 直接替换为[4]会把本文邻域和筛选错误归给原论文 |
| 5.3.4原占位⑤ | “上行rank驱动的最早完成式分配……ready-list思想受HEFT启发” | A：思想借鉴 | [3]，导言首次引用 | upward rank与earliest-finish-time来源已交代；公式和critical具体设计仍属于本文 |
| 5.4.2原占位⑥ | “受HEFT启发的ready-list调度，而非标准HEFT的逐字复现” | A：思想借鉴 | [3]，导言首次引用 | 明确HEFT-style，不归因本文工作量、等待、复用和流水线修正 |
| 第5章导言未标记VNS概念 | “通过变邻域搜索持续维护best-so-far方案” | A：VNS基本思想；本文维护规则为C | [4] | 正式介绍系统切换邻域思想；best-so-far、严格接受及adaptive仍为本文设计 |
| 1.2—1.4、2.3—2.4、3.1、4.2、6.1 | P1/P2/P3、Task、DDR/L1/UB、L2、容量/带宽、FIFO | C | 无 | 官方题面与官方执行规则 |
| 3.2、4.1、4.3—4.5 | 符号、划分、映射、商图可行性、字典序、Evaluator闭环 | C | 无 | 本文模型、实现或拓扑顺序直接推导；未借用外部定理声明 |
| 5.2—5.3、5.4.1、5.4.3—5.8 | Multi-seed、粗化、8类邻域、strict descent、adaptive、Top-K、去重、复杂度 | C（HEFT借鉴已单列） | 无 | 本文构造和实现分析，不以原始HEFT/VNS论文证明具体设计 |
| 6.2—6.6、第7—9章、10.1、10.3—10.5 | 正式配置、指标、实验数字、收益、相关系数、机制讨论 | C | 无 | 本文数据、统计与官方机制，不以外部论文替代实验证据 |
| 10.2、10.6 | 严格下降不能经过非改进解；概率接受非改进解的SA-VNS探索及未采用结论 | C | 无 | 说明本次开发探索；下降限制直接来自本文规则，未展开SA历史或一般理论，不需新增SA论文 |
| 10.7 | 预筛、预算分配、固定plan比较、Cache-aware启发式等未来方向 | C | 无 | 本文建议，不声称外部既有方法或已完成效果 |

共4类核心需求：DNN加速器效率、多核DAG调度、HEFT类列表调度、VNS基本思想。实际配置4个引用点，清除6处原占位。第2章及第3—4、6—10章无需修改；没有必须新增文献才能支撑的重要背景论断。

## 2. 正文引用顺序

1. [1] 1.1：“在DNN加速器中，计算、存储层次与数据移动需要协同考虑，数据搬运成本是影响处理效率的重要因素。”
2. [2] 1.1：“在多核DAG调度中，节点间依赖关系与可利用的并行性是需要共同考虑的关键因素。”
3. [3] 第5章导言：“核分配借鉴HEFT类列表调度思想，采用HEFT-style实现。”5.1步骤4、5.3.4、5.4.2不重复挂原论文。
4. [4] 第5章导言：“变邻域搜索（Variable Neighborhood Search，VNS）的基本思想是在局部搜索中系统切换邻域结构。”第2章缩写为方法预告，此处正式介绍思想；不归因本文邻域、下降、adaptive与筛选设计。

## 3. 正式参考文献

[1] V. Sze, Y.-H. Chen, T.-J. Yang, J. S. Emer，Efficient Processing of Deep Neural Networks: A Tutorial and Survey，Proceedings of the IEEE，105(12)：2295–2329，2017。

[2] S. Zhao, X. Dai, I. Bate，DAG Scheduling and Analysis on Multi-Core Systems by Modelling Parallelism and Dependency，IEEE Transactions on Parallel and Distributed Systems，33(12)：4019–4038，2022。

[3] H. Topcuoglu, S. Hariri, M.-Y. Wu，Performance-Effective and Low-Complexity Task Scheduling for Heterogeneous Computing，IEEE Transactions on Parallel and Distributed Systems，13(3)：260–274，2002。

[4] N. Mladenović, P. Hansen，Variable Neighborhood Search，Computers & Operations Research，24(11)：1097–1100，1997。

## 4. DOI / 官方核验信息

内部审计信息，不并入正式参考文献格式。核验日期：2026-09-27。4篇均由用户先行人工核验，本次补核原始出版记录、索引或作者机构来源；部分出版页直接打开受限，不声称全部全文已通读。

| 编号 | DOI | 出版方 / 作者机构来源 | 核验内容与支持边界 |
|---|---|---|---|
| [1] | [10.1109/JPROC.2017.2761740](https://doi.org/10.1109/JPROC.2017.2761740) | [IEEE](https://ieeexplore.ieee.org/document/8114708/)；[MIT作者原文](https://eems.mit.edu/wp-content/uploads/2017/11/2017_pieee_dnn.pdf) | 核对作者、题名、105(12)、2295–2329、2017和DOI；原文第V节尤其2309–2310页讨论存储层次、搬运及复用。仅支持一般DNN效率背景 |
| [2] | [10.1109/TPDS.2022.3177046](https://doi.org/10.1109/TPDS.2022.3177046) | [IEEE](https://ieeexplore.ieee.org/abstract/document/9779935)；[York](https://pure.york.ac.uk/portal/en/publications/dag-scheduling-and-analysis-on-multi-core-systems-by-modelling-pa/) | 核对作者、题名、33(12)、4019–4038、2022和DOI；摘要明确节点依赖与并行性，不引入其实时调度理论或具体算法 |
| [3] | [10.1109/71.993206](https://doi.org/10.1109/71.993206) | [IEEE](https://ieeexplore.ieee.org/document/993206/) | 核对题名、13(3)、260–274、2002和DOI；作者沿用人工核验信息；摘要明确upward rank与最早完成时间。本文只是HEFT-style |
| [4] | [10.1016/S0305-0548(97)00031-2](https://doi.org/10.1016/S0305-0548(97)00031-2) | [Elsevier / ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0305054897000312) | 原始出版索引核对题名、24(11)、1097–1100、1997、DOI及系统切换邻域的摘要；作者沿用人工核验信息。只支持VNS基本思想 |

元数据差异处理：[2]第三方DBLP期号为10，IEEE原始记录为12，采用33(12)；[1]MIT个别新闻页卷号排版不同，采用IEEE记录及作者原文页脚的105卷。差异已由原始来源解决，不形成待核验项。

## 5. 尚需人工核验项目

无。

建议新增文献：无。正文剩余引用占位：0。技术模型、公式、实验数字与正式算法事实未修改；仅补充一般学术背景、配置引用并明确思想归因。
