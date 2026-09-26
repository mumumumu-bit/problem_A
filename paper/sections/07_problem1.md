# 7 问题一求解与结果分析

## 7.1 问题一的求解实现

依据第4章统一模型和第5章Multi-seed + VNS算法求解问题一，并采用第6章的正式配置与评价口径。Scene A按子图封装Task，子图边界依据官方规则插入DDR方向的COPY操作，Task间依赖及同核、跨核等待由官方执行器处理。求解器输出图划分、核映射及核内顺序，将其转换为plan后调用问题一官方Evaluator，以正式Makespan和Added Copy的字典序比较维护当前最好有效方案。

<!-- Evidence: paper/EVIDENCE_MAP.md A、B、C；paper/sections/04_model.md 4.2.1、4.4、4.5；paper/sections/05_algorithm.md 5.1；paper/sections/06_experiment.md 6.1—6.3 -->

## 7.2 多核加速结果

表4(a)汇总P1、P2在100个case上的正式平均Speedup。各项均先用同一case的正式单核基准除以对应多核VNS结果，再求100个比值的算术平均；N=1为共同单核参考点。

表4(a) 核心结果汇总：P1/P2平均Speedup

| 核数N | P1平均Speedup | P2平均Speedup |
|---:|---:|---:|
| 1 | 1.0000 | 1.0000 |
| 2 | 1.7890 | 1.9004 |
| 3 | 2.4163 | 2.6663 |
| 4 | 2.9514 | 3.2978 |
| 5 | 3.3877 | 3.8369 |

<!-- Evidence: results/final_visualization/figure_numbers.md“P1加速比”“P2加速比”；paper/EVIDENCE_MAP.md E、F（归档job JSON独立复算闭环）；目标汇总表为tables/p1_speedup_1to5.csv、p2_speedup_1to5.csv，当前文件不可解析，本表不声称由其逐行读取。 -->

P1平均加速比由N=2时的1.7890提高到N=5时的3.3877，在N=1至5的正式汇总中保持单调增长。与理想线性参考值N相比，N=2、3、4、5时的平均加速比1.7890、2.4163、2.9514、3.3877均低于相应的2、3、4、5。这里的线性参考用于描述扩展趋势，不构成对每个case可达到加速比的保证。

<!-- Evidence: results/final_visualization/figure_numbers.md“P1加速比”；理想参考值为核数N本身，不新增效率指标。 -->

本节通过正文数字和表4(a)报告P1结果；P1/P2合并图在第8章对比小节首次完整出现，单场景图 `fig1_p1_speedup` 留在附录。

## 7.3 结果分析

**数据直接支持的事实。** 在本次100-case测试集上，核数由2增加到5时，P1平均加速比从1.7890增长至3.3877；各多核点均高于1且低于理想线性参考值N。这说明当前正式结果在集合平均意义上获得了多核加速，但汇总均值本身不能推出所有case均改善，也不能推出每个case的加速比都随核数单调增长。

**结合模型机制的解释。** Scene A中，可并行执行的范围受到原图依赖约束，Task边界还引入COPY与等待。因而，增加计算核并不必然将所有执行工作均匀分摊；平均加速比低于N的现象可能与依赖限制、核间负载不均、跨核等待及通信开销共同有关。这一解释与第4章Scene A执行模型一致，现有正式汇总没有分别隔离这些因素，不能据此量化任一因素对差距的独立贡献。

<!-- Evidence: 数据来自figure_numbers.md“P1加速比”；机制边界来自paper/EVIDENCE_MAP.md A、C及04_model.md 4.2.1、4.3；本段机制解释不作为独立实验归因。 -->

## 7.4 本问小结

在Scene A正式规则下，统一模型与求解算法得到的P1平均Speedup由单核参考值1.0000增长至N=5时的3.3877。后续与P2的比较沿用同一单核基准和逐case比值平均口径，见第8章。

<!-- Evidence: results/final_visualization/figure_numbers.md；paper/EVIDENCE_MAP.md E、F -->

<!-- [LAYOUT-DECISION] Word整稿时确认表4(a)置于7.2、合并图首次置于8.3的跨章引用是否顺畅；当前采用FIGURE_PLAN方案B，保留fig1/fig2于附录，不改用方案A。 -->
