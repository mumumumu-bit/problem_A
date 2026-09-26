# 9 问题三共享L2资源下的多核切图与调度

## 9.1 共享只读L2 Cache场景建模落地

依据第4章模型和第5章算法求解问题三，并沿用第6章正式配置。P3在Scene B的按核Task与跨核COPY规则基础上，为COPY_IN增加共享只读L2 Cache读取路径；命中走Cache读取带宽，未命中从DDR读取并在完成后按FIFO规则更新Cache，命中不刷新FIFO顺序。Cache容量和访问行为由官方Evaluator处理，最终候选仍按Makespan、Added Copy的字典序目标比较。正式solver没有启用Cache相关候选估计权重，本文不将其描述为Cache-aware划分算法。

<!-- Evidence: paper/EVIDENCE_MAP.md A、B、C、D；paper/sections/04_model.md 4.2.3、4.4；paper/sections/05_algorithm.md 5.4.3；paper/sections/06_experiment.md 6.2、6.4 -->

本章以官方术语“共享只读L2 Cache”指称该硬件资源；“FIFO”仅用于说明其访问状态更新和替换规则。图4、图5文件名中的“L2”与题面术语一致。

## 9.2 N=1同计划配对实验

N=1实验覆盖100个case，每个case的no-Cache与共享只读L2 Cache评估使用同一个plan，paired-plan一致100/100、不一致0、缺失0。不同case之间计划可以不同；该实验是逐case固定调度计划后比较两种执行机制，而不是100个case共用一个计划。

<!-- Evidence: paper/EVIDENCE_MAP.md G；paper/sections/06_experiment.md 6.4；正式P3 N1配对记录 -->

图4展示各核数下no-Cache与共享只读L2 Cache的平均Makespan，其中N=1来自上述固定计划配对，N=2至5来自下一节的正式场景比较。N=1时，no-Cache平均Makespan为3124794周期，共享只读L2 Cache版本为3116693周期（均按正式摘要的整数显示值报告）；平均逐case Speedup为1.0086。该1.0086先对100个case分别计算no-Cache makespan / 共享只读L2 Cache makespan，再对100个比值求平均；它不是3124794 / 3116693这一对平均Makespan的商。

[FIGURE: fig4_p3_noL2_vs_L2]

<!-- 推荐caption：图4 no-Cache与共享只读L2 Cache的平均Makespan。N=1为100-case固定plan配对；N=2至5分别取P2 VNS与P3 VNS结果，属于独立求解的场景比较。首次完整插图置于9.2，9.3仅引用。 -->

表4(b) 核心结果汇总：P3比较指标

| 核数N | no-Cache平均Makespan（周期） | Cache平均Makespan（周期） | 平均逐case no-Cache/Cache比值 | 平均Cache Hit Rate |
|---:|---:|---:|---:|---:|
| 1 | 3124794 | 3116693 | 1.0086 | 0.0920 |
| 2 | 1665942 | 1659155 | 1.0068 | 0.1606 |
| 3 | 1147788 | 1147097 | 1.0136 | 0.2412 |
| 4 | 924640 | 922512 | 1.0152 | 0.2467 |
| 5 | 771569 | 753230 | 1.0259 | 0.2973 |

表中Makespan按 `figure_numbers.md` 的整数展示值报告；比值均为100个case逐case比值的平均，命中率均为逐case官方命中率的算术平均。因此N=1的1.0086不是表中两个平均Makespan相除所得。N=1与N=2至5采用不同的计划控制条件，不能将各行视为同一固定plan实验的核数扩展。表4(b)与表4(a)分别列示不同参照口径，避免将P1/P2相对单核的Speedup与P3的no-Cache/Cache比值混作同一指标。

<!-- Evidence: results/final_visualization/figure_numbers.md“P3 L2对比”；paper/EVIDENCE_MAP.md E、G（归档独立复算）；目标汇总表为tables/p3_l2_comparison_1to5.csv，当前文件不可解析，表4(b)使用正式摘要显示精度，不虚构CSV原始精度。 -->

**数据直接支持的事实。** N=1时Cache版本的平均Makespan低于no-Cache版本，平均比值1.0086高于1。固定case内plan的设置使这组比较比N=2至5更接近隔离Cache执行机制的影响，但均值不能推出100个case均获得加速。

**结合模型机制的解释。** Cache命中可改变COPY_IN读取路径，这与配对结果中观察到的平均性能差异一致。该实验固定了调度方案，仍不据此声称Cache在所有图上均有效，或给出普遍的因果保证。

<!-- Evidence: 直接事实来自figure_numbers.md和Evidence Map G；机制来自04_model.md 4.2.3。 -->

## 9.3 N=2至5正式场景比较

图4中N=2至5的no-Cache柱分别取P2 VNS正式结果，Cache柱取同case、同核数的P3 VNS正式结果。表4(b)给出的平均Makespan依次为1665942/1659155、1147788/1147097、924640/922512、771569/753230周期，前项为P2、后项为P3。

**数据直接支持的事实。** N=2～5的平均逐case比较比值随核数单调上升：1.0068→1.0136→1.0152→1.0259。若纳入N=1的1.0086，N=1～5整体并非严格单调，因为N=2的1.0068略低于N=1。两场景的平均Makespan也分别随核数增加而降低。

**结合模型机制的解释。** P3增加Cache读取路径，可能改变数据读取完成时间，观察到的场景差异与这一执行机制一致。然而P2、P3分别在各自场景下独立求解，最终plan并未固定为相同方案。因此，N=2至5可比较两场景最终性能，不能把全部Makespan差异解释成Cache的纯粹独立贡献，也不能据均值判断每个case的结果方向。

<!-- Evidence: results/final_visualization/figure_numbers.md“P3 L2对比”；paper/EVIDENCE_MAP.md G；paper/sections/06_experiment.md 6.4；机制来自04_model.md 4.2.3。 -->

## 9.4 Cache Hit Rate分析

图5同时展示平均逐case no-Cache/Cache比值与平均Cache Hit Rate；它提供归一化性能对比和命中统计，与图4的绝对Makespan互补。N=1、2、3、4、5的平均命中率依次为0.0920、0.1606、0.2412、0.2467、0.2973，对应平均逐case比值为1.0086、1.0068、1.0136、1.0152、1.0259。N=2～5比值单调上升；纳入N=1后整体不严格单调，N=2略低于N=1。

[FIGURE: fig5_p3_l2_speedup]

<!-- 推荐caption：图5 平均no-Cache/共享只读L2 Cache比值及平均Cache命中率。比值为逐case比值的算术平均；N=1固定plan，N=2至5分别采用P2/P3 VNS结果。命中率是官方评价指标，不参与solver目标。首次完整插图置于9.4。 -->

**数据直接支持的事实。** 在已测核数上，平均命中率从0.0920增长至0.2973；N=2～5的平均逐case比值1.0068→1.0136→1.0152→1.0259单调上升。纳入N=1的1.0086后，整体并非严格单调，因为N=2略低于N=1。以上均为集合均值，不能推出case级命中率分布、所有case的一致关系或统计显著性。

**结合模型机制的解释。** 官方Cache命中改变的是COPY_IN读取路径，而最终Makespan还受图依赖、执行顺序、计算及通信等待影响。N=2～5的比值上升不能直接解释为Cache的纯因果贡献，因为P2与P3分别求解，使用的最终plan未固定为同一方案。现有汇总不足以证明提高命中率会导致加速比提高。Cache Hit Rate也没有进入正式字典序目标。case级散点图 `fig8_cache_hit_vs_speedup` 按规划留在附录，如整稿引用，其解释仅限相关性，不作为Cache独立贡献的证明。

<!-- Evidence: figure_numbers.md“P3 L2对比”；paper/EVIDENCE_MAP.md A、B、G、J；FIGURE_PLAN.md 对fig5/fig8的表述边界；不从附录散点反推相关系数或因果关系。 -->

## 9.5 本问小结

N=1固定plan配对得到平均no-Cache/共享只读L2 Cache比值1.0086；N=2至5分别求解的正式P2/P3场景比较得到1.0068、1.0136、1.0152、1.0259。两类实验共同给出共享只读L2 Cache场景的正式性能与命中统计，但解释范围不同：前者固定case内计划，后者包含场景下求解方案的变化，不能作为same-plan的Cache独立贡献对照。

<!-- Evidence: results/final_visualization/figure_numbers.md；paper/EVIDENCE_MAP.md E、G；paper/sections/06_experiment.md 6.4 -->
