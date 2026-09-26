# 正式论文详细大纲 V1

## 使用规则

- 本大纲只规划论文结构，不构成正式正文、正式摘要或正式公式。
- `paper/EVIDENCE_MAP.md` 是算法、机制、参数、实验数字和结论的唯一事实依据。
- `paper/REFERENCE_STRUCTURE_STUDY.md` 只提供结构经验，不提供可写入论文的事实。
- 正式算法主线仅为 Evidence Map 已确认的 Baseline、Multi-seed、HEFT-style 核分配、候选排序、官方 Evaluator 和 strict-descent VNS。
- SA 不属于 stable solver 和 full100，不进入第5章正式算法；正文原则上不写，必要时仅在附录的历史探索说明中用一句话标明“探索后未采用”。
- seed、time budget、max evaluations、workers 等属于第6章实验设置，不作为第5章算法定义。
- fine-grain=2 是正式 full100 的候选生成变体，但没有独立消融；adaptive_budget 在正式 full100 中开启，但没有独立消融。二者均不得宣称具有独立性能贡献。

## 摘要

【本节回答的问题】全文解决什么问题、采用什么真实方法、在哪些正式数据上验证、得到哪些由 Evidence Map 支持的主要结论。

【需要使用的Evidence Map事实】A部分三问场景；B部分评价指标；C部分正式算法；D部分正式实验范围；E部分A级核心结果；G部分P3配对口径。

【计划使用的公式】不放推导；只在需要时以文字概括 Makespan 优先、Added Copy 次序决胜的评价关系。

【计划使用的图/表】摘要不放图表。

【禁止越界的结论】不得写全局最优、线性扩展保证、Cache-aware solver、SA进入正式算法、独立fine-grain/adaptive贡献；不得引用参考论文数字或机制。

# 1 问题重述

## 1.1 研究背景与任务对象

【本节回答的问题】计算图在多核 NPU 调度中的基本对象是什么，为什么需要图划分、核分配和官方执行评价。

【需要使用的Evidence Map事实】A部分“原始计算图”“COPY机制”“Task组织”；计算图由 ops、tensors、edges 构成，求解器图视图与官方评估器职责分开。

【计划使用的公式】计算图记号、节点集与边集的抽象定义；不写参考论文中的硬件模型公式。

【计划使用的图/表】Framework A 的输入端；表1主要符号说明。

【禁止越界的结论】不得自行扩展硬件层级、执行单元、功耗或带宽机制；不得把参考论文的单核调度背景当作本题正式机制。

## 1.2 问题一：Scene A 多核图划分与调度

【本节回答的问题】P1要求输出什么方案，官方执行模型如何解释 Task、COPY 和 makespan。

【需要使用的Evidence Map事实】A部分“P1 / Scene A”“Task组织”“COPY机制”。

【计划使用的公式】P1方案到官方 makespan/Added Copy 输出的符号关系；此处不展开求解算法。

【计划使用的图/表】表2三问机制差异；Framework C 的 P1 分支。

【禁止越界的结论】不得把 P1 描述成仅核内调度，不得忽略 Task 边界 COPY 和跨 Task 等待。

## 1.3 问题二：Scene B 多核调度与跨核通信

【本节回答的问题】P2相对P1改变了什么，跨核边如何形成 COPY_OUT/COPY_IN。

【需要使用的Evidence Map事实】A部分“P2 / Scene B”“Task组织”；P2按核组织 Task，同核 tensor 片上通信，跨核边补 COPY。

【计划使用的公式】跨核边集合或通信量的定义性表达；不构造额外通信代价函数。

【计划使用的图/表】表2；Framework C 的 P2 分支。

【禁止越界的结论】不得把 Added Copy 与 spill 混写；不得虚构未由正式评估器支持的通信机制。

## 1.4 问题三：只读 FIFO Cache 场景

【本节回答的问题】P3在P2执行模型上新增什么正式机制，需要比较哪些输出。

【需要使用的Evidence Map事实】A部分“P3相对P2的增加”“P3 Cache容量/带宽”；G部分P3 N=1与N=2~5证据。

【计划使用的公式】Cache hit rate 的定义需求；P2/P3逐case speedup 的定义需求。

【计划使用的图/表】表2；Framework C 的 P3 分支；Framework D。

【禁止越界的结论】正式术语优先使用“只读 FIFO Cache”或`read_only` Cache；“L2”只能作为说明过的概括性简称。

## 1.5 三个问题的关系与论文主线

【本节回答的问题】为什么三个问题共享同一求解器主线，但由不同官方执行模型评价。

【需要使用的Evidence Map事实】A部分三问差异；C部分统一流水线；E2结果口径。

【计划使用的公式】不设新公式；只规划输入—方案—三类评价输出的映射。

【计划使用的图/表】Framework A；表2。

【禁止越界的结论】不得写成三个独立算法，也不得声称P1/P2/P3使用完全相同的执行语义。

# 2 问题分析

## 2.1 统一难点：DAG、划分、分配与评价闭环

【本节回答的问题】本题的核心决策链和困难分别位于哪里。

【需要使用的Evidence Map事实】A部分计算图与Task组织；C部分图粗化、核分配、candidate ranking、official evaluator。

【计划使用的公式】决策变量类别清单；不正式定义最终模型。

【计划使用的图/表】Framework A 的高层版本。

【禁止越界的结论】本节只解释难点，不提前讲算法步骤或实验结果。

## 2.2 问题一分析

【本节回答的问题】P1中子图 Task、边界 COPY 与跨 Task 等待如何影响方案质量。

【需要使用的Evidence Map事实】A部分P1事实；B部分Makespan与Added Copy。

【计划使用的公式】P1目标与约束所需公式类别清单。

【计划使用的图/表】Framework C 的简化P1栏；不放结果图。

【禁止越界的结论】不得在分析章给出P1 speedup数字或重复第7章结果。

## 2.3 问题二分析

【本节回答的问题】按核组织 Task 后，跨核通信如何成为调度结果的重要组成。

【需要使用的Evidence Map事实】A部分P2事实；B部分Added Copy字段含义。

【计划使用的公式】跨核边和新增COPY的定义需求。

【计划使用的图/表】Framework C 的简化P2栏。

【禁止越界的结论】不得把跨核COPY数值提前写入；不得把P2描述成只改变参数而不改变Task组织。

## 2.4 问题三分析

【本节回答的问题】只读 FIFO Cache 如何改变 COPY_IN 的读取路径，为什么需要 paired comparison 和 hit rate。

【需要使用的Evidence Map事实】A部分P3机制；G部分P3比较口径。

【计划使用的公式】命中字节占比、逐case no-Cache/Cache 比值的公式需求。

【计划使用的图/表】Framework D 的概念版。

【禁止越界的结论】不得由相关性推导因果；不得称 solver 使用了 Cache-aware partitioning。

## 2.5 总体解决思路

【本节回答的问题】统一求解器如何连接三个执行场景，并形成后续第4至第9章的叙事。

【需要使用的Evidence Map事实】C部分正式流水线；J部分图表定位。

【计划使用的公式】无正式公式；规划阶段映射关系。

【计划使用的图/表】Framework A 完整图。

【禁止越界的结论】只概述模块，不重复第5章候选生成、邻域和停止机制细节。

# 3 模型假设与符号说明

## 3.1 建模边界与必要假设

【本节回答的问题】哪些输入和执行规则由正式数据/评估器给定，哪些不是本文可自由改变的对象。

【需要使用的Evidence Map事实】A部分官方评估机制；D部分hardware config；K部分历史措辞风险。

【计划使用的公式】假设列表，不写推导公式。

【计划使用的图/表】无；必要时在表1脚注注明官方量与求解器量。

【禁止越界的结论】不得增加功耗、吞吐、额外缓存层级或其他未确认约束；不得把配置值写成普适硬件常数。

## 3.2 计算图、划分与调度符号

【本节回答的问题】后文如何统一表示图、节点、边、子图、核心、Task和调度方案。

【需要使用的Evidence Map事实】A部分“原始计算图”“Task组织”；C部分图粗化与核分配。

【计划使用的公式】图与商图记号、子图集合、核映射、调度方案表示。

【计划使用的图/表】表1主要符号说明。

【禁止越界的结论】符号只能服务于已实现对象，不引入源码不存在的决策变量。

## 3.3 评价量与结果字段符号

【本节回答的问题】Makespan、Added Copy、spill、Cache hit rate分别表示什么。

【需要使用的Evidence Map事实】B部分全部指标；P3官方评估器返回字段。

【计划使用的公式】四类指标的定义性公式需求；具体实现以官方返回为准。

【计划使用的图/表】表1；表2中列出各问题可用指标。

【禁止越界的结论】不得把Added Copy与spill相加为未经定义的新指标，不得从图像反推字段值。

## 3.4 统计量与比较符号

【本节回答的问题】逐case speedup、均值、标准差和win/tie/loss怎样记号化。

【需要使用的Evidence Map事实】E2结果口径；F部分正式平均speedup；H部分阶段比较边界。

【计划使用的公式】逐case比值、算术均值、样本标准差、win/tie/loss判定。

【计划使用的图/表】表1。

【禁止越界的结论】平均speedup不得改成总makespan之比；阶段快照不得解释为严格单变量因果实验。

# 4 多核图划分与调度统一模型

## 4.1 统一求解对象与方案表示

【本节回答的问题】求解器究竟优化何种方案，方案如何连接图划分、核分配和官方评价。

【需要使用的Evidence Map事实】A部分图与Task；C部分正式流水线、图粗化和核分配。

【计划使用的公式】划分映射、核分配映射、核内顺序和最终plan的结构性表示。

【计划使用的图/表】Framework A；表1。

【禁止越界的结论】不得把启发式生成过程写成精确数学规划求解，不得声称保证全局最优。

## 4.2 三种执行场景的任务构造

【本节回答的问题】同一个候选方案在P1、P2、P3中如何形成不同Task/COPY/Cache执行语义。

【需要使用的Evidence Map事实】A部分P1/P2/P3和Task组织；G部分N=2~5来源。

【计划使用的公式】三种场景的评价映射或分段定义需求；不写具体执行器代码。

【计划使用的图/表】Framework C；表2三问机制差异。

【禁止越界的结论】不得把P2/P3差异简化为单一参数开关；不得把L2称为官方原词。

## 4.3 可行性与约束体系

【本节回答的问题】候选方案必须满足哪些由图结构和官方评估器决定的基本条件。

【需要使用的Evidence Map事实】A部分原始计算图、COPY机制；C部分图粗化保证DAG商图约束；官方Evaluator有效性判断。

【计划使用的公式】DAG依赖保持、划分覆盖与互斥、核映射有效性、官方Evaluation有效性的约束类型。

【计划使用的图/表】不新增结果图；可在Framework A中以“可行性检查”节点体现。

【禁止越界的结论】不得加入未由Evidence Map确认的缓存硬约束、精确求解约束或全局可行性定理。

## 4.4 Makespan与Added Copy目标

【本节回答的问题】正式优化目标和方案比较关系如何定义。

【需要使用的Evidence Map事实】B部分Makespan、Added Copy、Solver comparison、正式objective、字典序事实。

【计划使用的公式】Makespan定义；Added Copy定义；字典序比较关系。

【计划使用的图/表】表1；必要时在Framework A的Evaluator输出旁列出两项指标。

【禁止越界的结论】不得自行构造加权目标函数；spill和Cache hit rate不得擅自并入字典序目标。

## 4.5 官方Evaluator闭环

【本节回答的问题】估计器排序与官方评价各自承担什么角色，最终结果由谁确定。

【需要使用的Evidence Map事实】A部分COPY机制；C部分candidate ranking与正式流水线；B部分正式objective。

【计划使用的公式】估计排序分数与官方objective的角色区分，不要求给出估计器完整公式。

【计划使用的图/表】Framework A和Framework B。

【禁止越界的结论】不得把估计器score当作makespan，不得用solver估计替代官方结果。

# 5 Multi-seed + VNS求解算法

## 5.1 正式算法总体流程

【本节回答的问题】从预计算到最终incumbent的算法阶段怎样连接。

【需要使用的Evidence Map事实】C部分正式流水线、global best和官方Evaluator闭环。

【计划使用的公式】算法输入输出、阶段快照和incumbent更新的符号需求。

【计划使用的图/表】Framework B。

【禁止越界的结论】不得包含SA；不得在本节列seed、时间预算、max evaluations、workers等实验设置。

## 5.2 Baseline初始方案

【本节回答的问题】Baseline如何构成算法起点，并在阶段统计中承担什么角色。

【需要使用的Evidence Map事实】C部分Baseline；H部分阶段消融边界。

【计划使用的公式】Baseline候选的结构性定义，不正式展开启发式评分公式。

【计划使用的图/表】Framework B中的Baseline分支；不单独放性能图。

【禁止越界的结论】不得把Baseline写成独立同预算求解器，也不得提前使用消融数字。

## 5.3 多粒度Multi-seed候选生成

【本节回答的问题】主要seed family、多grain、whole候选和fine-grain候选如何构成候选组合。

【需要使用的Evidence Map事实】C部分Multi-seed、seed family数量、grains/fine-grain、图粗化、核分配。

【计划使用的公式】候选集合并集、去重与portfolio截断的抽象表示。

【计划使用的图/表】Framework B中的候选生成模块；附录可列完整候选来源说明。

【禁止越界的结论】不得写成恰好“4族×3 grain”；fine-grain=2不得宣称有独立收益；具体配置值统一在第6章给出。

## 5.4 HEFT-style核分配与候选排序

【本节回答的问题】粗化块如何分配到核心，估计器如何用于候选预排序。

【需要使用的Evidence Map事实】C部分核分配、candidate ranking、cache/memory heuristic。

【计划使用的公式】ready-list/最早完成时间风格评分需求；候选排序与digest去重关系。

【计划使用的图/表】Framework A、Framework B。

【禁止越界的结论】不得称为标准HEFT的完整复现或精确优化；不得声称正式启用了Cache/Memory启发式权重。

## 5.5 Top-K官方评价与阶段快照

【本节回答的问题】候选池如何经估计排序后进入官方评价，并产生Baseline/Multi-seed阶段快照。

【需要使用的Evidence Map事实】C部分candidate pool/top-K机制、candidate ranking、global best。

【计划使用的公式】Top-K集合、官方Evaluation和best-so-far更新关系。

【计划使用的图/表】Framework B。

【禁止越界的结论】本节只定义Top-K机制，不写正式数值3或候选池48；这些数值放第6章。

## 5.6 VNS邻域搜索

【本节回答的问题】8类邻域如何围绕当前incumbent生成和评价局部候选。

【需要使用的Evidence Map事实】C部分VNS邻域数量及8类邻域名称、正式流水线。

【计划使用的公式】邻域集合、邻域候选生成和评价调用的抽象表示。

【计划使用的图/表】Framework B；必要时附录给邻域分类表。

【禁止越界的结论】不得将N8写成全局跳出机制，不得声称VNS达到全局最优。

## 5.7 严格下降接受、incumbent与adaptive停止

【本节回答的问题】候选何时被接受，best-so-far如何保持，adaptive机制何时允许提前停止。

【需要使用的Evidence Map事实】C部分VNS接受准则、global best、early stopping/adaptive。

【计划使用的公式】严格字典序改善条件、incumbent递推、停滞计数与停止条件的公式需求。

【计划使用的图/表】Framework B的循环与停止分支。

【禁止越界的结论】不得写成模拟退火或允许劣解接受；不得宣称adaptive具有独立性能贡献；具体阈值放第6章。

# 6 实验设置与评价指标

## 6.1 数据范围与任务覆盖

【本节回答的问题】正式实验覆盖多少case、problem、N和stage，N=1与多核数据分别来自哪里。

【需要使用的Evidence Map事实】D部分cases、N覆盖、full100总job数；F和G部分singlecore/P3 N1来源。

【计划使用的公式】覆盖数量的乘法关系；不生成新实验数字。

【计划使用的图/表】表3正式实验配置；附录放100-case完整明细。

【禁止越界的结论】不得写“400组”；不得声称N=1来自merged多核job；不得把无法解析的merged CSV描述为已逐行读取。

## 6.2 硬件与官方评价配置

【本节回答的问题】正式评估使用哪些容量、带宽和场景参数。

【需要使用的Evidence Map事实】D部分hardware config；A部分P3 Cache容量/带宽。

【计划使用的公式】参数表，不另构硬件性能模型。

【计划使用的图/表】表3。

【禁止越界的结论】这些参数是正式评估配置，不是求解器搜索参数，也不是普适硬件结论。

## 6.3 正式求解器配置

【本节回答的问题】full100实际使用的seed、预算、候选池、top-K、轮数、grains、workers、adaptive、fine-grain及权重是什么。

【需要使用的Evidence Map事实】D部分solver seed、source commit、time budget、max evaluations、candidate pool/top-k、max rounds、grains/fine-grain、workers、adaptive、cache/memory weight。

【计划使用的公式】无；使用配置表。

【计划使用的图/表】表3正式实验配置。

【禁止越界的结论】参数值不得回写为第5章算法定义；不得说所有job耗满预算或都因停滞停止；不得声称权重为0的启发式被正式启用。

## 6.4 评价指标与统计口径

【本节回答的问题】P1/P2 speedup、P3比较、均值和阶段win/tie/loss如何计算。

【需要使用的Evidence Map事实】E2结果口径；F部分平均speedup；G部分P3口径；H部分阶段边界。

【计划使用的公式】逐case speedup、均值、标准差、P3 P2/P3比值、win/tie/loss定义。

【计划使用的图/表】表4核心结果汇总的口径说明；表5阶段消融结果。

【禁止越界的结论】不得以总和之比替代逐case均值；不得把嵌套阶段快照写成严格单变量因果消融。

## 6.5 结果证据与可复现性边界

【本节回答的问题】正式结果由哪些归档证据支持，当前还存在哪些文件级风险。

【需要使用的Evidence Map事实】当前总风险；full100 CSV状态；D部分source commit与git_dirty；“仍待核验的问题”。

【计划使用的公式】无。

【计划使用的图/表】表3脚注；附录提供数据来源与复算链。

【禁止越界的结论】不得声称merged CSV已经可解析或与重建结果逐字节一致；不得隐去`git_dirty=true`的provenance风险。

# 7 问题一求解与结果分析

## 7.1 P1方案评价流程

【本节回答的问题】统一算法输出如何进入P1官方评估器并产生结果。

【需要使用的Evidence Map事实】A部分P1/COPY/Task组织；C部分official evaluator闭环。

【计划使用的公式】P1方案到Evaluation的映射，不重复第4章完整模型。

【计划使用的图/表】引用Framework C；不重复Framework A/B。

【禁止越界的结论】不得重复讲Multi-seed与VNS内部算法；不得加入P1专属未实现优化。

## 7.2 P1多核加速结果

【本节回答的问题】P1在N=1~5下的正式平均speedup如何变化。

【需要使用的Evidence Map事实】E1 P1 speedup；F部分singlecore基准与统计口径。

【计划使用的公式】逐case speedup及其均值；引用第6章，不重复推导。

【计划使用的图/表】方案B下正文使用fig3的P1曲线；表4列P1核心数字。若采用方案A则使用fig1。

【禁止越界的结论】不得写线性扩展保证、所有case均改善或未由数据支持的原因解释。

## 7.3 P1阶段结果与小结

【本节回答的问题】P1的Baseline→Multi-seed→VNS阶段变化支持什么有限结论。

【需要使用的Evidence Map事实】E1 P1阶段数字；H部分消融边界。

【计划使用的公式】阶段均值改善率和win/tie/loss定义，引用第6章。

【计划使用的图/表】表5中的P1行；fig6统一留到第10章，避免重复。

【禁止越界的结论】不得声称各seed family、各grain、fine-grain或adaptive的独立贡献。

# 8 问题二求解与结果分析

## 8.1 P2方案评价流程

【本节回答的问题】统一算法输出如何按核组织Task并由P2评估跨核COPY。

【需要使用的Evidence Map事实】A部分P2、Task组织、COPY机制；C部分official evaluator闭环。

【计划使用的公式】P2方案到Evaluation的映射；跨核边集合引用第4章。

【计划使用的图/表】引用Framework C。

【禁止越界的结论】不得重复第5章算法；不得声称P2仅是P1参数变化。

## 8.2 P2多核加速结果

【本节回答的问题】P2在N=1~5下的正式平均speedup及其与P1的关系是什么。

【需要使用的Evidence Map事实】E1 P2 speedup；F部分P1/P2共用单核基准的口径和风险说明。

【计划使用的公式】逐case speedup及其均值，引用第6章。

【计划使用的图/表】方案B下正文使用fig3；表4列P2核心数字。若采用方案A则使用fig2。

【禁止越界的结论】不得称单核基准是P2独立生成的Scene B单核仿真；不得无证据解释P1/P2差异成因。

## 8.3 P2阶段结果与小结

【本节回答的问题】P2的阶段变化如何描述，哪些解释必须留在边界内。

【需要使用的Evidence Map事实】E1 P2阶段数字；H部分消融边界。

【计划使用的公式】阶段均值改善率和win/tie/loss定义，引用第6章。

【计划使用的图/表】表5中的P2行；fig6留第10章。

【禁止越界的结论】不得把阶段下降解释成严格单变量因果，不得宣称VNS对所有case改善。

# 9 问题三只读FIFO Cache求解与结果分析

## 9.1 P3只读FIFO Cache执行机制

【本节回答的问题】COPY_IN命中与未命中分别走什么路径，FIFO容量管理和带宽池如何作用。

【需要使用的Evidence Map事实】A部分P3相对P2的增加、P3 Cache容量/带宽；正式代码与说明使用`read_only` FIFO Cache。

【计划使用的公式】命中判定、容量更新和命中率的公式需求；不写源码级完整模拟公式。

【计划使用的图/表】Framework D；表2。

【禁止越界的结论】不得强化成官方未写的硬件机制；不得把“共享只读L2”作为官方原词。

## 9.2 N=1逐case固定计划配对比较

【本节回答的问题】P3 N=1如何确保no-L2与readonly-L2在每个case内使用同一计划。

【需要使用的Evidence Map事实】G部分N=1 no-L2/L2：100 case一致、0不一致、0缺失，99个不同hash属于跨case正常差异。

【计划使用的公式】每case成对比值与100-case均值。

【计划使用的图/表】fig4/fig5的N=1数据；表4脚注说明paired-plan。

【禁止越界的结论】不得要求100个case共用全局plan；不得把跨case不同hash写成配对失败。

## 9.3 N=2~5 P2/P3比较口径

【本节回答的问题】多核no-L2与readonly-L2分别来自何处，如何逐case计算speedup。

【需要使用的Evidence Map事实】G部分N=2~5来源和L2 speedup；E2口径。

【计划使用的公式】每case P2-vns/P3-vns 比值与均值。

【计划使用的图/表】fig4、fig5；表4。

【禁止越界的结论】不得把P2/P3写成完全固定同一优化plan的严格控制实验；不得混用N=1与N=2~5的数据生成流程。

## 9.4 Cache效果与命中率结果

【本节回答的问题】P3正式结果中的makespan、speedup和Cache hit rate呈现什么统计现象。

【需要使用的Evidence Map事实】E1 P3 N=1~5正式数字；J部分fig4/fig5解释边界。

【计划使用的公式】均值、标准差和逐case比值，引用第6章。

【计划使用的图/表】fig4、fig5；表4。

【禁止越界的结论】不得把hit rate与speedup的相关性写成因果；不得宣称solver进行了Cache-aware优化。

## 9.5 P3阶段结果与小结

【本节回答的问题】P3的Baseline、Multi-seed、VNS阶段变化和只读Cache结论应如何分开表达。

【需要使用的Evidence Map事实】E1 P3阶段数字；H部分消融边界；P3官方Cache与solver权重为0的区别。

【计划使用的公式】阶段改善率和win/tie/loss，引用第6章。

【计划使用的图/表】表5中的P3行；fig6留第10章。

【禁止越界的结论】不得把阶段优化贡献与Cache效果混为一谈；不得声称cache_weight已启用。

# 10 算法有效性与模型评价

## 10.1 三阶段结果的统一分析

【本节回答的问题】Baseline、Multi-seed和VNS三个嵌套阶段在P1/P2/P3及N=2~5上的总体表现是什么。

【需要使用的Evidence Map事实】E1阶段数字；H部分Baseline→Multi-seed、Multi-seed→VNS边界。

【计划使用的公式】阶段均值改善率、win/tie/loss汇总。

【计划使用的图/表】fig6_stage_ablation；表5阶段消融结果。

【禁止越界的结论】不得声称是三个独立同预算求解器的严格因果消融；不得拆出单独seed family、grain、fine-grain或adaptive贡献。

## 10.2 VNS增量收益与分布

【本节回答的问题】VNS相对Multi-seed的收益在case间如何分布。

【需要使用的Evidence Map事实】J部分fig7定位；H部分VNS整体贡献边界。

【计划使用的公式】逐case `(multiseed-vns)/multiseed` 的分布统计。

【计划使用的图/表】fig7放附录，正文仅在必要时引用一句概括；若版面充足可作为第10章补充图。

【禁止越界的结论】不得称VNS一定改善所有case或达到全局最优；不得引入SA式解释。

## 10.3 Cache命中与加速的相关性探索

【本节回答的问题】P3 hit rate与P2/P3 speedup之间是否存在可观察的统计相关现象。

【需要使用的Evidence Map事实】J部分fig8定位与相关性边界。

【计划使用的公式】相关性或趋势线的说明性统计需求；正式使用前需与现有图脚本口径一致。

【计划使用的图/表】fig8放附录，正文可在P3讨论末尾交叉引用。

【禁止越界的结论】不得写因果关系、机制证明或普遍规律。

## 10.4 模型与算法优点

【本节回答的问题】在Evidence Map允许范围内，统一方法有哪些可验证的工程优点。

【需要使用的Evidence Map事实】C部分统一流水线、官方Evaluator闭环、正式候选机制；E部分A级结果。

【计划使用的公式】无。

【计划使用的图/表】不新增图表，引用前文结果。

【禁止越界的结论】不得用“最优”“普适”“显著”而无统计或证据支撑；不得把实现存在等同于独立贡献。

## 10.5 局限性、证据风险与适用边界

【本节回答的问题】当前算法、实验和数据归档有哪些明确局限。

【需要使用的Evidence Map事实】H部分消融边界；K部分措辞风险；merged CSV不可解析；manifest `git_dirty=true`；剩余TBD。

【计划使用的公式】无。

【计划使用的图/表】可使用一张简短“结论—证据—边界”表，若篇幅不足则纯文字。

【禁止越界的结论】不得隐去数据文件和provenance风险；不得以参考论文或开发实验填补正式full100缺失的独立消融。

## 10.6 推广条件与后续工作

【本节回答的问题】方法若推广到其他图或配置，需要满足哪些前提，哪些结论仍需新增实验。

【需要使用的Evidence Map事实】当前可安全进入论文的最小集合；无充分证据项目；剩余TBD。

【计划使用的公式】无。

【计划使用的图/表】无。

【禁止越界的结论】不得把当前100-case结果外推为任意硬件和任意图的保证；不得把尚未进行的敏感性实验写成已完成结果。

# 参考文献

- 本阶段不创建正式条目。
- 后续条目必须经过 `paper/CITATION_AUDIT.md` 审计，并遵守 `paper/COMPLIANCE_CHECKLIST.md`。
- 不复制4篇参考论文的参考文献。

# 附录

## 附录A 正式配置与复现信息

【本节回答的问题】如何保存正式配置、commit、manifest、运行范围和证据链。

【需要使用的Evidence Map事实】D部分正式实验配置；当前总风险与剩余TBD。

【计划使用的公式】无。

【计划使用的图/表】完整配置表、provenance表。

【禁止越界的结论】不得声称dirty运行可由commit单独完全复现；不得改写正式结果文件。

## 附录B 100-case完整结果与补充统计

【本节回答的问题】正文未展开的case级结果如何提供审计入口。

【需要使用的Evidence Map事实】E、F、G部分正式结果和口径。

【计划使用的公式】与第6章一致的统计公式，不增加新指标。

【计划使用的图/表】100-case明细；fig1/fig2或fig3的替补图；fig7、fig8。

【禁止越界的结论】不得直接把不可解析的merged CSV作为已验证明细；附录数据来源必须标明归档job JSON或可解析正式文件。

## 附录C 算法补充说明

【本节回答的问题】正文省略的候选来源、邻域定义和伪代码细节如何补充。

【需要使用的Evidence Map事实】C部分正式算法。

【计划使用的公式】候选集合和邻域操作的补充定义。

【计划使用的图/表】邻域分类表、补充伪代码。

【禁止越界的结论】不得加入SA、GA、Tabu、CP-SAT等未进入stable solver的机制；如必须记录SA，只能单独标为历史探索且不与正式算法混排。

## 附录D AI使用与合规记录

【本节回答的问题】如何按官方规定披露实际AI用途、人工核验和必要的Prompt/后处理信息。

【需要使用的Evidence Map事实】不使用算法事实；使用 `COMPLIANCE_CHECKLIST.md` 和 `AI_USAGE.md` 的真实记录。

【计划使用的公式】无。

【计划使用的图/表】AI工具使用记录表。

【禁止越界的结论】不得猜测工具版本、发布日期或实际用途；不得把未经团队理解和重写的AI输出作为最终正文。

## 章节去重规则

1. 第2章只回答“难点是什么、为什么需要统一方案”；第4章才定义对象、约束、目标和三场景评价映射。
2. 第4章只回答“优化什么、什么是有效方案、如何由官方评估”；第5章回答“如何生成和改进方案”。
3. 第5章只描述机制，不写正式seed、预算和workers；所有数值配置集中在第6章。
4. 第6章统一定义数据范围、配置和统计口径；第7~9章只引用，不重复整张配置表和公式推导。
5. 第7~9章不再讲完整Multi-seed + VNS，只各用一个“方案进入对应Evaluator”的短小节说明场景接口。
6. fig6和表5统一放第10章；第7~9章只引用各自对应行，避免三次重复阶段分析。
7. P1/P2 speedup若采用fig3总览，fig1/fig2移附录；正文不同时放三张表达同一组数据的图。
