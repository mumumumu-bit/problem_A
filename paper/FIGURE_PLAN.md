# 正式论文图表规划

## 使用边界

- 本文件只规划已有结果图、新增技术框架图和正文表格，不绘图、不生成新数据、不改变现有结果。
- 所有数据来源、统计口径和可写结论以 `paper/EVIDENCE_MAP.md` 为唯一依据。
- 图题与正文解释不得从图片肉眼读取数字，应引用已核验的正式统计来源。
- 100-case完整明细放附录，不把所有CSV内容塞入正文。

## 一、现有8张结果图审查

| 图 | 数据来源 | 核心信息 | 正文/附录 | 放置章节 | 是否与其他图重复 | 表述边界 |
|---|---|---|---|---|---|---|
| `fig1_p1_speedup` | `singlecore_full100/singlecore.csv` + A/B/C归档job JSON中的P1 vns；逐case计算singlecore/P1后取均值 | P1在N=1~5下的平均speedup及离散程度 | 方案A：正文；方案B：附录 | 方案A放7.2；方案B放附录B | 与fig3的P1曲线完全重复核心信息 | 不得写线性扩展保证、所有case均改善或总makespan之比 |
| `fig2_p2_speedup` | 同一singlecore基准 + A/B/C归档job JSON中的P2 vns；逐case计算singlecore/P2后取均值 | P2在N=1~5下的平均speedup及离散程度 | 方案A：正文；方案B：附录 | 方案A放8.2；方案B放附录B | 与fig3的P2曲线完全重复核心信息 | 单核基准是统计口径约定，不得称为P2独立生成的Scene B单核仿真 |
| `fig3_p1p2_combined` | fig1与fig2相同的两组正式统计 | 在同一坐标中比较P1/P2随N变化的平均speedup | 方案A：不进正文，可移附录或不使用；方案B：正文主图 | 方案B放8.2“P2结果及与P1比较” | 同时重复fig1、fig2的核心曲线，但增加直接横向比较价值 | 不是新增独立实验；不得无证据解释P1/P2差异成因 |
| `fig4_p3_noL2_vs_L2` | N=1来自`p3_n1_l2.csv`；N=2~5来自归档job JSON中P2 vns与P3 vns | 各N下no-L2与只读FIFO Cache的平均makespan对比 | 正文 | 9.4 | 与fig5共享同一P2/P3底层数据，但回答绝对makespan差异 | N=1为逐case固定计划配对；N=2~5不是固定同一优化plan的严格控制实验 |
| `fig5_p3_l2_speedup` | 与fig4相同的逐caseP2/P3比值，并使用P3 `cache_hit_rate` | P3相对P2的平均speedup与Cache hit rate随N变化 | 正文 | 9.4 | 与fig4部分重复，但提供归一化speedup与hit rate，信息不可完全替代 | “L2”须说明为概括性简称；不得把hit rate与speedup写成因果 |
| `fig6_stage_ablation` | A/B/C归档job JSON中的baseline、multiseed、vns阶段快照 | 三个嵌套阶段在P1/P2/P3、N=2~5上的阶段性变化 | 正文 | 10.1 | 与表5重复具体数值，但图负责趋势、表负责精确值 | 不是三个独立同预算求解器的严格因果消融；不得拆出单seed/grain/adaptive贡献 |
| `fig7_vns_gain_dist` | 每case的`(multiseed-vns)/multiseed`，按问题与N分组 | VNS增量收益在case间的分布与异质性 | 附录；版面充足时可在10.2引用 | 附录B | 与fig6都涉及VNS增量，但fig7展示分布而非均值 | 探索性分布；不得写“VNS对所有case均有效”或全局最优 |
| `fig8_cache_hit_vs_speedup` | P3 `cache_hit_rate`与逐caseP2-vns/P3-vns speedup | Cache命中与P3加速之间的相关性探索 | 附录 | 附录B；正文9.4或10.3交叉引用 | 与fig5共享hit rate和speedup，但增加case级散点关系 | 只能写相关性，不能写因果、机制证明或普遍规律 |

## 二、fig1 + fig2 + fig3重复处理方案

### 方案A：P1/P2分别成图

- 正文7.2保留fig1，正文8.2保留fig2。
- fig3不进入正文，可移入附录或不使用。
- 优点：P1、P2两章各自闭环，读者在对应章节即可看到完整曲线和误差棒。
- 缺点：跨场景比较需要读者在两张图之间切换；正文占用两处版面。
- 适用条件：若最终写作强调“每问独立作答”且篇幅允许，采用本方案。

### 方案B：正文只保留组合图

- 正文8.2使用fig3作为P1/P2统一总览。
- 第7章P1结果用表4中的精确数字和文字概括，并前向提示“P1/P2合并趋势见8.2”。
- fig1、fig2移入附录B，分别保留误差棒和单场景细节。
- 优点：正文只用一张图同时回答扩展趋势和P1/P2差异，减少明显重复；证据并未删除，单场景图仍在附录。
- 缺点：第7章不再拥有独立主结果图，需要通过表4维持章节完整性。
- 适用条件：若正文页数紧张、希望突出P1/P2横向比较，采用本方案。

### 推荐

推荐方案B。理由是fig3完整承载fig1与fig2的核心曲线，并额外支持P1/P2横向比较；fig1、fig2保留在附录可维持单场景细节和误差证据。正文证据由fig3 + 表4共同承担，不因去重而丢失必要结果。

## 三、新增技术框架图规划

### Framework A：整体求解框架

- **图目的**：用一张图连接问题输入、统一求解器、最终方案和P1/P2/P3官方评价，建立全文主线。
- **输入**：计算图；硬件配置。
- **核心模块**：图特征预计算；多粒度候选生成；Multi-seed；HEFT-style核分配；Candidate pool；Top-K筛选与official evaluator；VNS；最终调度方案；P1/P2/P3评价。
- **箭头逻辑**：输入 → 预计算 → 多粒度/Multi-seed候选 → 核分配 → 候选池与去重排序 → Top-K官方评价 → VNS迭代 → 最终方案 → 三个官方评价分支。
- **输出**：正式plan/调度方案；P1/P2/P3官方Evaluation结果。
- **推荐放置章节**：2.5总体解决思路；第5章可引用但不重复绘制。
- **必须来自Evidence Map的信息**：正式流水线、图粗化、核分配、candidate ranking、official evaluator、VNS、P1/P2/P3执行模型。
- **不能自行补充的内容**：SA、GA、Tabu、CP-SAT；未启用的Cache/Memory启发式；未确认的硬件执行单元；新的优化阶段；具体实验参数。

### Framework B：Multi-seed + VNS内部算法流程

- **图目的**：解释正式stable solver内部如何从Baseline和候选组合产生incumbent，再经VNS严格下降更新。
- **输入**：图特征；候选生成配置接口；对应problem与core数量。
- **核心模块**：Baseline；主要seed family；多grain/whole/fine-grain候选；候选去重；估计排序；Top-K官方评价；incumbent；8类VNS邻域；strict-descent接受；adaptive停滞/预算检查。
- **箭头逻辑**：Baseline与多类候选汇入候选集合 → 去重与估计排序 → Top-K官方评价 → 形成Multi-seed incumbent → 进入VNS邻域循环 → 官方评价 → 严格改善则更新，否则继续/停止 → 输出best-so-far。
- **输出**：Baseline、Multi-seed、VNS阶段快照；最终incumbent。
- **推荐放置章节**：5.1正式算法总体流程。
- **必须来自Evidence Map的信息**：四个主要seed family、whole/fine-grain变体、portfolio截断、HEFT-style分配、Top-K、8邻域、字典序严格改善、adaptive机制。
- **不能自行补充的内容**：劣解接受、温度、SA逃逸、全局最优标识；seed/time budget/max evaluations/workers具体数值；fine-grain或adaptive的独立贡献箭头。

### Framework C：P1/P2/P3执行机制差异

- **图目的**：把同一候选方案在三个官方执行场景中的Task组织、COPY和Cache差异并列展示。
- **输入**：同一类多核划分与调度方案。
- **核心模块**：P1子图Task与边界COPY；P2按核Task、同核通信与跨核COPY_OUT/COPY_IN；P3在P2基础上的只读FIFO Cache查询、DDR读取和CACHE_READ带宽池。
- **箭头逻辑**：候选plan分成P1/P2/P3三条并列分支 → 各自Task/COPY构造 → 官方执行模拟 → 对应Evaluation字段。
- **输出**：各场景makespan、Added Copy；P3额外给出Cache hit rate。
- **推荐放置章节**：4.2三种执行场景的任务构造；第7~9章只引用。
- **必须来自Evidence Map的信息**：A部分P1/P2/P3、Task组织、COPY机制和P3 Cache事实。
- **不能自行补充的内容**：P1/P2/P3未确认的硬件拓扑；把P3简化为单一开关；把“共享只读L2”标成官方术语；把三个场景画成三套不同solver。

### Framework D：P3只读FIFO Cache数据访问机制

- **图目的**：清楚说明P3中COPY_IN访问Cache、命中/未命中、DDR和FIFO写入/淘汰的执行路径。
- **输入**：COPY_IN对逻辑tensor id的读取请求；Cache当前状态；正式容量与带宽配置。
- **核心模块**：只读Cache查询；hit/miss判定；hit进入CACHE_READ带宽池；miss进入DDR读取；miss完成后写入FIFO；容量不足时按FIFO淘汰；命中不刷新FIFO顺序。
- **箭头逻辑**：COPY_IN → Cache查询 → 命中/未命中分支；命中 → CACHE_READ → 完成；未命中 → DDR读取 → 完成后写入FIFO → 必要时淘汰。
- **输出**：读取完成事件；Cache状态更新；命中字节统计/Cache hit rate；最终P3 makespan。
- **推荐放置章节**：9.1 P3只读FIFO Cache执行机制。
- **必须来自Evidence Map的信息**：只有COPY_IN查询Cache、命中与DDR路径、FIFO顺序、独立带宽池、容量/带宽参数来源。
- **不能自行补充的内容**：写回Cache、命中刷新、LRU/LFU、预取、一致性协议、可写共享缓存、solver Cache-aware切分或未确认的硬件层级。

## 四、正文核心表格规划

| 表 | 核心内容 | 证据来源 | 推荐位置 | 正文控制与表述边界 |
|---|---|---|---|---|
| 表1：主要符号说明 | 图、节点、边、子图、核心、Task、plan、makespan、Added Copy、spill、Cache hit rate、逐case speedup | Evidence Map A、B、F、G | 3.2~3.4后 | 只列正文实际使用符号；不从参考论文复制符号体系，不引入未实现决策变量 |
| 表2：三问机制差异 | P1/P2/P3的Task组织、同核/跨核通信、COPY、Cache和主要输出字段 | Evidence Map A、G | 4.2 | “只读FIFO Cache”是正式表述；L2如出现必须注明为概括性简称 |
| 表3：正式实验配置 | source commit、seed、time budget、max evaluations、candidate pool、top-K、max rounds、grains/fine-grain、workers、adaptive参数、cache/memory权重、case/problem/N覆盖 | Evidence Map D | 6.2~6.3 | 明确这些是正式运行配置；记录`git_dirty=true`；不得把参数写成方法定义或独立贡献 |
| 表4：核心结果汇总 | P1/P2 N=1~5 speedup；P3 N=1~5 no-Cache/Cache、speedup、hit rate的必要摘要 | Evidence Map E、F、G | 第7~9章分段引用，完整表可放9.4后 | 只放正文支撑结论所需数字；P3 N=1与N=2~5的统计来源脚注明确区分 |
| 表5：阶段消融结果 | P1/P2/P3、N=2~5的Baseline→Multi-seed与Multi-seed→VNS改善及win/tie/loss | Evidence Map E、H | 10.1 | 称“阶段性比较”而非严格单变量因果消融；不拆分seed family、grain、fine-grain或adaptive贡献 |

### 附录表格

- 附表A：100-case完整结果明细及来源标识。
- 附表B：正式配置和manifest字段完整记录。
- 附表C：8类VNS邻域与源码映射。
- 附表D：P3 N=1逐case paired-plan审计摘要。
- 附表E：图表数据字段、统计口径和复算来源。

## 五、正文图表组合建议

推荐正文主图为：

1. Framework A 整体求解框架。
2. Framework B Multi-seed + VNS内部流程。
3. Framework C P1/P2/P3机制差异。
4. Framework D P3只读FIFO Cache访问机制。
5. fig3 P1/P2 combined speedup。
6. fig4 P3 no-L2 vs readonly Cache。
7. fig5 P3 speedup与Cache hit rate。
8. fig6阶段性比较。

推荐附录图为：fig1、fig2、fig7、fig8。若最终页数充足且希望P1/P2章节完全独立，可改用方案A，但不得同时在正文保留fig1、fig2、fig3。

## 六、章节与图表去重规则

### 第2章问题分析与第4章模型

- 第2章只写“困难、冲突和需要解决的问题”，不定义完整变量、约束和评价映射。
- 第4章集中定义“优化对象、可行性、目标和三场景官方评价”。
- Framework A在第2章首次出现；第4章只引用或使用Framework C展开，不再复制整张总体图。

### 第4章模型与第5章算法

- 第4章回答“什么是方案、什么是有效、如何比较”。
- 第5章回答“如何生成候选、如何评价候选、如何搜索和停止”。
- Makespan/Added Copy字典序只在4.4正式定义，第5章引用该关系，不重复定义。

### 第6章实验设置与第7~9章结果

- 第6章只出现一次完整配置表、数据范围和统计公式。
- 第7~9章引用第6章，不重复seed、预算、workers、候选池等配置。
- 三个结果章只解释各自Evaluator接口和结果，不重新列整个full100运行环境。

### P1/P2/P3三章与统一算法

- 第5章完整讲Multi-seed + VNS。
- 第7~9章各用一个短小节说明“同一最终方案如何进入对应Evaluator”。
- P1/P2/P3章不得重复候选生成、Top-K、8邻域和adaptive流程。
- 三问共有的阶段分析统一移至第10章，避免每章重复fig6和表5。

## 七、仍需人工决策

1. 最终采用方案A还是方案B；本规划推荐方案B。
2. 正文允许的总页数，以及4张新增框架图是否全部进入正文。
3. 表4采用一张跨三问总表，还是在第7、8、9章分别放子表并在第9章给总表。
4. fig7是否因版面充足进入10.2，还是严格留在附录。
5. fig8是否只放附录，正文仅作一句相关性说明。
6. “L2”是否在图题中保留为读者友好简称；若保留，首次必须定义为本文概括性称呼而非官方原词。
7. `git_dirty=true`和merged CSV不可解析风险在正文6.5写到何种详细程度，还是把完整技术记录放附录。
8. SA历史探索是否完全不出现；若团队认为必须交代，只能放附录一条“探索后未采用”，不得进入Framework B或第5章。
