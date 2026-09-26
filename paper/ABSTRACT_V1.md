# 论文题目、摘要与关键词 V2

## 1. 五个题目候选

1. 面向多核NPU的计算图划分与调度统一优化方法
2. 多核NPU计算图划分与调度的统一建模及求解（最终推荐）
3. 多场景下多核NPU计算图划分与调度优化
4. 多核NPU计算图划分与调度的协同优化方法
5. 基于统一搜索框架的多核NPU计算图划分与调度

## 2. 最终推荐题目

《多核NPU计算图划分与调度的统一建模及求解》

推荐理由：突出多核NPU计算图划分与调度的统一模型及求解主线，覆盖三个执行场景，题目不堆叠算法术语。

## 3. 正式摘要V2

多核NPU计算图划分与调度涉及子图粒度、核映射和核内执行顺序的耦合决策，需要在并行执行、数据复用与跨核通信之间权衡。本文将计算图划分、核映射及核内调度统一建模，以总体任务执行时间Makespan为首要目标、总额外数据搬运量Added Copy为第二目标，采用严格字典序比较，仅在Makespan相同时比较Added Copy。通过官方评价器刻画不同场景的任务组织、通信等待、容量约束与缓存访问规则，形成统一方案表示与场景评价相结合的模型。

针对模型求解，构建多粒度Multi-seed与变邻域搜索VNS相结合的启发式框架。Multi-seed从负载均衡、数据亲和、关键路径和投影负载平衡等不同偏好生成初始候选，采用HEFT风格的就绪列表策略进行核分配，并依据官方评价结果维护当前已评价的最好有效方案。VNS通过多类结构邻域联合调整划分、核归属及执行顺序，仅接受官方字典序目标严格改善的候选，形成候选生成、官方评价与严格下降更新的闭环；正式求解启用自适应邻域选择与停止机制。

正式全量测试覆盖100个用例、三个问题及2～5核配置，共1200个求解任务。问题一、问题二在5核条件下，相对共同单核基准的逐用例平均加速比分别达到3.3877和3.8369。对于共享L2资源场景，5核时逐用例无Cache/共享只读L2 Cache的Makespan比值平均为1.0259；两场景分别求解，该结果不作为Cache纯独立贡献的估计。嵌套阶段验证表明，Multi-seed相对Baseline在1074个任务上降低Makespan，VNS相对Multi-seed在938个任务上进一步改善，两个阶段均未出现Makespan退化。结果表明，该统一建模与搜索框架在所测通信与缓存场景下取得了多核调度收益，并表现出稳定的阶段性改善。

<!-- 字符统计口径：仅统计本节摘要正文，不含标题、空白和本注释；含中文、标点、数字及英文字符共743个，其中汉字520个。 -->

## 4. 关键词

多核NPU；计算图划分；多核调度；启发式搜索；变邻域搜索

## 5. 摘要数字审计表

本轮依据现有摘要、指定章节与证据地图核对冻结事实，未扫描历史results或重新运行实验。表中A级判断承接证据地图所记录的正式归档复算闭环及第10章的逐组核验；并不表示本轮重新读取了归档job JSON。

| 摘要数字 | 来源文件 | 含义 | 是否A级证据 |
|---|---|---|---|
| 三个问题；问题一、问题二 | paper/EVIDENCE_MAP.md A、D；paper/sections/04_model.md 4.2；paper/sections/06_experiment.md 6.1；题面来源由证据地图定位至根目录官方题面问题1—3 | 三种官方执行场景及摘要所用的问题编号；不是三个独立算法 | 是，官方题面及正式覆盖记录支持 |
| 100个用例 | paper/EVIDENCE_MAP.md D及“full100原始CSV与只读重建状态”；paper/sections/06_experiment.md 6.1 | 正式多核测试覆盖100个不同case | 是，证据地图记录正式manifest及job JSON已核验 |
| 2～5核 | paper/EVIDENCE_MAP.md D；paper/sections/06_experiment.md 6.1 | 正式多核核数分别为2、3、4、5，共四种配置 | 是，正式manifest覆盖范围 |
| 1200个求解任务 | paper/EVIDENCE_MAP.md D；paper/sections/06_experiment.md 6.1；paper/sections/10_evaluation.md 10.1 | 100个case × 三个问题 × 四种多核配置；不是1200个不同case，也不含另行生成的单核基准任务 | 是，正式manifest及job JSON的既有核验 |
| 5核（两处，分别为P1/P2及P3结果条件） | paper/sections/07_problem1.md 7.2表4(a)；paper/sections/08_problem2.md 8.2；paper/sections/09_problem3.md 9.2表4(b)、9.3 | 摘要选择的代表性核数，不表示仅测试五核 | 是，正式结果条件 |
| 3.3877 | paper/sections/07_problem1.md 7.2表4(a)；paper/EVIDENCE_MAP.md E1、F；底层来源由证据地图定位至results/final_visualization/figure_numbers.md、正式singlecore基准与A/B/C归档job JSON | P1五核VNS结果相对共同单核基准的逐case加速比算术平均；不是平均Makespan之比 | 是，E1记录已完成归档独立复算 |
| 3.8369 | paper/sections/08_problem2.md 8.2；paper/sections/07_problem1.md 7.2表4(a)；paper/EVIDENCE_MAP.md E1、F；底层来源同上 | P2五核VNS结果相对共同单核基准的逐case加速比算术平均；分母不是另行生成的P2专属单核结果 | 是，E1记录已完成归档独立复算 |
| 1.0259 | paper/sections/09_problem3.md 9.2表4(b)、9.3；paper/sections/06_experiment.md 6.4；paper/EVIDENCE_MAP.md E1、G；底层来源为figure_numbers.md及A/B/C正式归档job JSON | 五核时逐case计算无Cache场景（P2 VNS）Makespan / 共享只读L2 Cache场景（P3 VNS）Makespan，再求100个比值的平均；明确分子、分母，两个场景分别求解，非固定计划Cache纯消融 | 是，E1、G记录已独立复算 |
| 1074 | paper/sections/10_evaluation.md 10.1表5及总计；paper/sections/06_experiment.md 6.5；paper/EVIDENCE_MAP.md E及正式归档复算状态 | 1200个job中Multi-seed相对Baseline的Makespan严格下降任务数；不按Added Copy打破Makespan平局 | 是，第10章记录正式job JSON逐组核验闭环 |
| 938 | paper/sections/10_evaluation.md 10.1表5及总计；paper/sections/06_experiment.md 6.5；paper/EVIDENCE_MAP.md E及正式归档复算状态 | 1200个job中VNS相对Multi-seed的Makespan严格下降任务数 | 是，第10章记录正式job JSON逐组核验闭环 |
| 两个阶段均未出现Makespan退化（各为0 loss） | paper/sections/10_evaluation.md 10.1表5及总计、10.3；paper/sections/06_experiment.md 6.5 | 两次相邻阶段比较均无Makespan增大的job；允许持平，不代表所有任务均改善或Added Copy均下降 | 是，第10章记录归档阶段统计；与严格下降规则一致 |
| L2中的“2” | 根目录官方题面1.5、问题3；paper/EVIDENCE_MAP.md A；paper/sections/04_model.md 4.2.3 | 官方二级缓存名称的一部分，非实验统计量 | 是，官方术语直接支持 |

证据口径说明：Evidence Map的E部分与“证据类别”已记录核心结果达到A级闭环，H部分个别阶段条目仍保留早期B级标签。本表采用更新后的结果闭环状态，并以第10章10.1明确记录的归档逐组核验支持1074、938及0 loss；不由配置存在推断独立机制收益。

## 6. 刻意未写入摘要的重要内容及原因

- 全部核数的P1/P2加速比序列：正文已有完整结果；摘要以五核代表值控制数字密度。
- P3单核同计划配对结果，包括100/100、3124794/3116693周期与平均逐case比值1.0086：该组证据与多核分别求解的比较不同，留在第9章说明，避免在摘要同时引入两种控制条件和过多数字。1.0086不是两个平均Makespan的商。
- P3其余多核比值与Cache命中率：用于完整场景分析；摘要仅保留五核比值，并明示独立求解边界，不声称Cache的纯因果贡献。
- 阶段平均Makespan下降范围4.35%～18.21%、0.38%～3.86%，以及126/262个tie：摘要已用1074/938个改善任务和无退化表述体现阶段结果。百分比范围留在第10章，保持其“固定问题与核数后的阶段均值相对差”口径，不改写为逐case改善率的平均。
- 四类seed family的英文名称balanced、affinity、critical、pipe：摘要用负载均衡、数据亲和、关键路径及投影负载平衡概括其偏好；投影负载平衡仅概括核选择评分的负载倾向，不描述为完整流水线优化，具体实现见第5章。
- digest去重、预算允许的seed逐个评价与内部估计器实现：压缩为基于官方评价维护当前已评价的最好有效方案及多类结构邻域搜索，保留评价闭环与严格下降，不改变算法事实。
- 8类邻域的数量及详细名称、候选池48、Top-K=3：属于实现结构与筛选配置，留在算法和实验章节；摘要只保留邻域调整与官方评价闭环。
- seed=2026、time budget=300秒、workers=2、fine-grain=2及其他配置值：不属于摘要所需核心信息。fine-grain是已启用候选变体，但缺少独立消融，不能声称独立收益。
- adaptive的详细选择与停止规则：摘要仅说明正式测试启用自适应机制，未量化或归因其独立贡献。
- SA-VNS：属于后续探索实验，未进入stable solver和full100正式算法，故不进入正式摘要。
- FIFO状态更新与淘汰规则、L2容量和带宽：留在模型与实验设置；FIFO仅描述状态更新与替换行为，不替代官方硬件名称。
- 复杂度推导、内部CSV问题、git_dirty及CLI验证状态：分别属于算法分析、内部审计或复现信息，按任务要求不进入摘要。
- 全局最优、对现有方法的显著领先、所有case均改善及Cache导致性能提升等结论：现有证据不支持，未作此类表述。

人工终审提示：最终题目及关键词已按本轮要求确定；仅需核对最终排版的字符统计方式及摘要与整稿措辞衔接。本轮只修改本文件，未修改其他章节，未新增正式事实或结果数字。
