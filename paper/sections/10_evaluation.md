# 10 算法有效性与模型评价

## 10.1 Multi-seed与VNS阶段效果

在正式full100实验中，每个job保存Baseline、Multi-seed及VNS三个嵌套阶段的结果。表5及正式阶段汇总按P1/P2/P3与N=2/3/4/5组合形成12组，每组100个case。对固定问题与核数，记相邻阶段的平均Makespan为 $\overline T_{\mathrm{前}}$ 和 $\overline T_{\mathrm{后}}$，表5的相对下降率为

$$
\frac{\overline T_{\mathrm{前}}-\overline T_{\mathrm{后}}}{\overline T_{\mathrm{前}}}\times100\%.
$$

该比例是阶段平均Makespan之间的相对差，不是逐case相对改善率的组内平均。Multi-seed比较以Baseline均值为分母，VNS比较以Multi-seed均值为分母。图6采用相同的均值相对差定义，但在每个问题内合并N=2、3以及N=4、5，形成6个面板，每个面板每阶段汇集200条记录；图中标注不能与表5的单核数统计逐项等同。win/tie/loss遵循第6章定义：后阶段Makespan严格更小、完全相等、更大分别记为win、tie、loss，Added Copy不用于打破tie。

[FIGURE: fig6_stage_ablation]

<!-- 推荐caption：图6 Baseline、Multi-seed与VNS嵌套阶段的平均Makespan变化。每个问题分别合并N=2、3与N=4、5，每面板每阶段200条记录；标注为合并后阶段均值之间的相对下降。这是阶段性比较，不是独立同预算求解器的单变量因果消融。 -->

表5 正式阶段结果（平均Makespan单位：周期；W/T/L为win/tie/loss）

| 问题/N | Baseline平均Makespan | Multi-seed平均Makespan | VNS平均Makespan | Baseline→Multi-seed下降 | Multi-seed→VNS下降 | 前一比较W/T/L | 后一比较W/T/L |
|---|---:|---:|---:|---:|---:|---|---|
| P1/2 | 1805484.7 | 1673611.0 | 1643683.7 | 7.30% | 1.79% | 95/5/0 | 73/27/0 |
| P1/3 | 1387579.0 | 1209320.7 | 1173970.2 | 12.85% | 2.92% | 93/7/0 | 77/23/0 |
| P1/4 | 1166573.8 | 983125.5 | 945180.6 | 15.73% | 3.86% | 96/4/0 | 80/20/0 |
| P1/5 | 1037999.0 | 849003.4 | 828328.3 | 18.21% | 2.44% | 95/5/0 | 82/18/0 |
| P2/2 | 1751495.8 | 1675330.4 | 1665941.9 | 4.35% | 0.56% | 83/17/0 | 65/35/0 |
| P2/3 | 1285038.4 | 1165658.3 | 1147787.6 | 9.29% | 1.53% | 89/11/0 | 86/14/0 |
| P2/4 | 1074746.2 | 944418.3 | 924639.7 | 12.13% | 2.09% | 86/14/0 | 81/19/0 |
| P2/5 | 951687.4 | 796084.2 | 771569.3 | 16.35% | 3.08% | 90/10/0 | 81/19/0 |
| P3/2 | 1743893.4 | 1665454.5 | 1659154.6 | 4.50% | 0.38% | 84/16/0 | 62/38/0 |
| P3/3 | 1277136.1 | 1163853.1 | 1147097.1 | 8.87% | 1.44% | 89/11/0 | 86/14/0 |
| P3/4 | 1067405.1 | 931553.7 | 922511.9 | 12.73% | 0.97% | 84/16/0 | 79/21/0 |
| P3/5 | 940257.3 | 781947.3 | 753229.9 | 16.84% | 3.67% | 90/10/0 | 86/14/0 |

平均Makespan保留一位小数；下降率由未取整的阶段均值计算，按正式摘要精度显示。上述12组中，Multi-seed相对Baseline的阶段平均Makespan下降率范围为4.35%（P2/N=2）至18.21%（P1/N=5）；VNS相对Multi-seed的阶段平均Makespan下降率范围为0.38%（P3/N=2）至3.86%（P1/N=4）。这些范围取自12组正式汇总，不是图6六个合并面板标注的范围。按1200个job汇总，前一比较为1074 win、126 tie、0 loss，后一比较为938 win、262 tie、0 loss；这些是job配对数，不能解释为独立case数量。

Multi-seed通过多类family与多粒度候选扩大初始方案覆盖，VNS围绕当前最好方案进行局部结构调整。表5支持两个阶段在本次测试中分别取得整体改进与进一步改进，但阶段内包含多种机制，且沿用同一次搜索的候选与预算，不能将差异全部归因于单一family、grain或adaptive机制。

<!-- Evidence: 本轮只读解析origin/results/full100-A/B/C中1200份job.json，按(case,problem,cores,algorithm)重建3600行；均值、下降比例及W/T/L与results/final_visualization/figure_numbers.md逐组一致。scripts/final_visualization.py按单个(problem,N)取阶段均值，先计算相对差再round(...,4)；scripts/fig6_stage_ablation.py则合并核数对后取均值，计算i1/i2并显示一位小数百分比。tables/stage_ablation.csv未作为可解析数据读取。机制来自paper/EVIDENCE_MAP.md C、H及05_algorithm.md。 -->

## 10.2 SA-VNS替代搜索机制探索

严格下降VNS只接受官方字典序目标改善的候选，因此可能无法经过暂时不改善的方案到达更好的区域。为探索这一限制，开发阶段实现了允许概率接受非改进解的SA-VNS机制，并开展小规模pilot及扩展比较。下表中的每条记录是同任务、同seed下control与SA的最终结果配对，胜负仅按Makespan判定；这些探索采用120秒、36次评价上限的配置，与正式full100实验范围和预算不同。

表6 SA-VNS探索实验汇总

| 实验阶段 | 配对记录数/任务数 | Win | Tie | Loss | 主要观察 |
|---|---|---:|---:|---:|---|
| Stage 1 | 4条/4任务，seed=2026 | 1 | 3 | 0 | case_005 P1 N4改善214周期，Added Copy增加97254字节 |
| Stage 2 | 6条/2任务，各3个seed | 2 | 4 | 0 | case_005 P1 N4在2026、2027改善，2028持平；另一任务3次均持平 |
| Expansion | 8条/8任务，seed=2026 | 0 | 8 | 0 | Makespan及Added Copy均未变化；两条记录多用1次评价 |

Stage 1中，case_005 P1 N4的Makespan从95618降至95404周期；相对下降为 $(95618-95404)/95618\approx0.2238\%$，Added Copy从0增至97254字节，官方评价调用从18增至23次。另3条记录Makespan与Added Copy均不变；case_001 P1 N2仍增加2次评价，其余两条调用数不变。四条记录的SA调用数合计比control多7次。

Stage 2对case_001 P1 N2与case_005 P1 N4分别采用2026、2027、2028三个seed。case_005在前两个seed中均由95618降至95404周期，重复出现214周期改善；两次均伴随97254字节的Added Copy增加及18→23次评价。seed=2028时Makespan、Added Copy和调用数均持平。case_001的三次Makespan、Added Copy均持平，调用数分别增加2、0、2次。六条记录合计多14次评价，Added Copy差值合计194508字节。该结果显示同一任务在两个seed下出现可重复的小幅改善，但没有达到三个seed均稳定改善，也没有形成跨任务收益。

Expansion覆盖8个任务，8条均为tie，Makespan和Added Copy差值全部为0。其中case_054 P2 N2和case_058 P1 N2各多1次官方评价，总调用数增加2次；其余6条调用数不变。该阶段仅使用seed=2026，不能据此评价多seed稳定性。既有报告还记录到一次非改进解接受，说明发生该接受行为本身并不保证最终结果更好。

以上证据支持将SA-VNS定位为“探索后未采用”：小规模pilot的收益局限于个别任务且存在Added Copy代价，扩展验证在当前范围内未表现出足够稳定的额外收益，同时可能增加官方评价调用。最终stable solver仍采用严格下降VNS，SA-VNS没有进入正式full100算法。这里不推断SA在其他参数、预算或任务上无效。详细seed级记录建议放入附录。

<!-- Evidence: 本轮只读核对D:/problem_A/problem_A_sa/results/sa_pilot_stage1、sa_pilot_stage2、sa_expansion下control/sa的benchmark.csv（最终vns行）与manifest.json；逐条Makespan、Added Copy及evaluations同各目录report_console.txt一致。Stage 1/Expansion为seed2026，Stage 2为2026/2027/2028。未读取trials.jsonl。SA实现/最终未采用定位来自paper/EVIDENCE_MAP.md I；非改进接受事件取自既有report_console统计。 -->

## 10.3 VNS收益分布

图7按问题与核数组合展示逐case收益

$$
g_{i,N}=\frac{T_{i,N}^{\mathrm{Multi\text{-}seed}}-T_{i,N}^{\mathrm{VNS}}}{T_{i,N}^{\mathrm{Multi\text{-}seed}}}.
$$

这一分布统计使用每个case的相对下降，区别于10.1节以组内平均Makespan计算的下降比例。图7建议放入附录，正文用表5及必要的分布摘要说明。

<!-- [FIGURE: fig7_vns_gain_dist] 附录位置；本节交叉引用，不重复完整插图。 -->

每组100个case中，VNS改善数量为62至86，tie数量为14至38，所有组的Makespan loss均为0。例如P1 N=2为73 win、27 tie；P3 N=2为62 win、38 tie。收益幅度也不均匀：P1 N=2的逐case收益均值约1.53%、中位数约0.37%、最大值约24.95%，说明较大的改善出现在部分case，不能仅凭均值描述所有case的收益。

正式接受规则保持incumbent的字典序目标不劣，因此Makespan不会因接受候选而增大；归档中0 loss与这一规则一致。Makespan tie可能仍包含Added Copy改善，不能将其一律解释为方案完全没有变化，也不能声称VNS在每个case都有Makespan收益。

<!-- Evidence: 本轮full100归档复算g=(multiseed-vns)/multiseed；P1 N2未取整g的mean/median/max分别约0.015315/0.003674/0.249454，百分比为乘100后四舍五入到两位。W/T/L与figure_numbers.md一致；图7口径来自scripts/fig7_vns_gain_dist.py；严格下降依据05_algorithm.md 5.7及Evidence Map C。 -->

## 10.4 Cache命中率与性能关系

图8分别在N=2、3、4、5下，将100个case的P3官方Cache Hit Rate与P2 VNS/P3 VNS Makespan比值配对。按图中相同口径复算，四组样本Pearson相关系数依次为0.540、0.463、0.391、0.394。它们均呈正向线性关联，但关联并不紧密一致，不能将命中率作为性能比值的确定性预测量；本节不据此作统计显著性判断。

<!-- [FIGURE: fig8_cache_hit_vs_speedup] 附录位置；正文仅报告可核验相关性结果。 -->

各组比值均同时包含小于1和大于1的case。例如N=4时比值范围约为0.9237至1.3712，对应命中率范围为0至0.7345，反映case间结果存在差异。P2和P3分别求解，数据同时包含场景执行规则与最终plan的变化；图8展示的是观察关联，不能证明命中率提高导致Speedup提高。Cache Hit Rate也不是solver优化目标，正式solver的Cache相关启发式权重为0。

<!-- Evidence: 本轮从A/B/C归档job JSON按(case,N)配对P2/P3 vns；x=P3 cache_hit_rate，y=P2 makespan/P3 makespan，Pearson系数复算0.540476/0.463337/0.391334/0.393792，与fig8 SVG已有r标签一致。N4比值min/max=0.9237399876807781/1.3712340074288072，命中率min/max=0/0.7345093073035156。口径见scripts/fig8_cache_hit_vs_speedup.py；限制见09_problem3.md及Evidence Map G、J。 -->

## 10.5 模型优点

统一方案表示允许同一类图划分、核映射和核内顺序在三种正式执行场景下求解与评价，使场景差异集中于官方执行语义。Multi-seed采用四类family及多粒度设置提供不同结构偏好的候选；正式阶段统计支持其候选组合在本次测试中取得整体改进，而非证明每一种候选机制均有独立收益。

官方Evaluator闭环使最终可行性和目标比较直接依据正式结果，内部估计器仅用于预排序，避免由代理分数替代最终指标。VNS的8类邻域覆盖核映射、块序、合并、拆分及边界调整，严格下降维护best-so-far。正式多核测试覆盖100个case、三问题和四个核数，共1200个job，为上述阶段效果提供了跨实例的统一验证范围。

<!-- Evidence: paper/EVIDENCE_MAP.md A、C、D；05_algorithm.md 5.1、5.3、5.6、5.7；06_experiment.md；本章10.1归档统计。 -->

## 10.6 模型局限

算法属于预算约束下的启发式搜索，不保证全局最优。官方Evaluator调用成本限制可探索候选数量，严格下降也可能无法穿越非改进区域；SA探索尚未提供足够稳定的替代收益。不同case的依赖及通信结构可能影响可用改善空间，正式收益分布表明case间幅度不同，但并未识别这些结构因素的独立贡献。

adaptive、fine-grain及各seed family缺少独立消融，阶段比较不能分离它们的贡献。P3 N=2至5不是same-plan的纯Cache消融；Cache与memory启发式权重均为0，当前solver并未主动使用这些评分项。正式测试覆盖的实例与核数范围有限，现有结果也不能直接外推到更大规模图、更多计算核或其他硬件配置。

<!-- Evidence: paper/EVIDENCE_MAP.md C、D、G、H；05_algorithm.md 5.7、5.8；06_experiment.md 6.2、6.4；07/08/09结果解释边界；本章10.2、10.3。 -->

## 10.7 推广与改进

以下均为未来改进方向。可研究更高效的候选预筛与评价缓存利用，在保留官方评价闭环的前提下减少无收益调用；也可探索更丰富但规模受控的邻域，以及按历史收益和评价成本分配预算的策略，并通过独立实验比较其收益。

对Cache机制，宜补充固定plan、固定配置的多核配对实验，进一步区分硬件访问机制与搜索方案变化的影响；随后可研究Cache-aware启发式，并与当前零权重配置作受控比较。对更大规模计算图，可评估特征预计算、候选构造与官方评价的耗时组成，再针对主要开销改进搜索效率。上述方向尚未完成，不能作为当前正式算法的机制或实验贡献。

<!-- Evidence: 改进动机来自05_algorithm.md 5.8、06_experiment.md、Evidence Map H及本章局限；本节属于未来工作建议，无新增已完成机制或实验声明。 -->
