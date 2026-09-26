# 附录B 逐用例评估结果及补充图

本附录列示100个测试用例（case_001至case_100）在核数N=1至5下的最终正式评估结果。Makespan单位为周期，Added Copy为总额外数据搬运量，单位为字节；Cache Hit Rate为[0,1]范围的命中比例。Added Copy不包含另列的spill_bytes，不能将二者混写。

完整逐用例数据保存在以下文件，数值保留正式归档精度：

- [p1_per_case.csv](../appendix_data/p1_per_case.csv)：问题一，共500行。
- [p2_per_case.csv](../appendix_data/p2_per_case.csv)：问题二，共500行。
- [p3_per_case.csv](../appendix_data/p3_per_case.csv)：问题三的两种场景，共500行。

## B.1 问题一逐用例结果

问题一N=2至5采用正式full100最终VNS结果；N=1采用正文平均Speedup使用的正式固定单核基准。按核数拆为附表B1至B5，每表100个用例，列为Case、Makespan、Added Copy。

| 附表 | 核数 | 可直接转换为Word表格的内容 |
|---|---:|---|
| B1 | 1 | [p1_n1.tsv](../appendix_data/word_tables/p1_n1.tsv) |
| B2 | 2 | [p1_n2.tsv](../appendix_data/word_tables/p1_n2.tsv) |
| B3 | 3 | [p1_n3.tsv](../appendix_data/word_tables/p1_n3.tsv) |
| B4 | 4 | [p1_n4.tsv](../appendix_data/word_tables/p1_n4.tsv) |
| B5 | 5 | [p1_n5.tsv](../appendix_data/word_tables/p1_n5.tsv) |

## B.2 问题二逐用例结果

问题二N=2至5采用正式full100最终VNS结果。N=1共用正文统计所采用的Scene A正式单核基准，不代表独立生成的Scene B单核评测。按核数拆为附表B6至B10，每表100个用例，列为Case、Makespan、Added Copy。

| 附表 | 核数 | 可直接转换为Word表格的内容 |
|---|---:|---|
| B6 | 1 | [p2_n1.tsv](../appendix_data/word_tables/p2_n1.tsv) |
| B7 | 2 | [p2_n2.tsv](../appendix_data/word_tables/p2_n2.tsv) |
| B8 | 3 | [p2_n3.tsv](../appendix_data/word_tables/p2_n3.tsv) |
| B9 | 4 | [p2_n4.tsv](../appendix_data/word_tables/p2_n4.tsv) |
| B10 | 5 | [p2_n5.tsv](../appendix_data/word_tables/p2_n5.tsv) |

## B.3 问题三逐用例结果

N=1的无L2与共享只读L2 Cache结果来自已审计的逐case固定计划配对实验：100/100个case在两种执行场景下使用同一plan。这里的配对发生在case内，不表示所有case共用一个plan。

N=2至5的无L2结果取同case、同核数的P2最终VNS结果，共享只读L2 Cache结果取P3最终VNS结果。两种场景分别求解，不是same-plan对照，因此不能将全部差异解释为Cache的独立因果贡献。

按核数拆为附表B11至B15，每表100个用例，列为Case、No-L2 Makespan、No-L2 Added Copy、L2 Makespan、L2 Added Copy、Cache Hit Rate。

| 附表 | 核数 | 可直接转换为Word表格的内容 | 比较口径 |
|---|---:|---|---|
| B11 | 1 | [p3_n1.tsv](../appendix_data/word_tables/p3_n1.tsv) | case内固定plan配对 |
| B12 | 2 | [p3_n2.tsv](../appendix_data/word_tables/p3_n2.tsv) | P2/P3分别求解 |
| B13 | 3 | [p3_n3.tsv](../appendix_data/word_tables/p3_n3.tsv) | P2/P3分别求解 |
| B14 | 4 | [p3_n4.tsv](../appendix_data/word_tables/p3_n4.tsv) | P2/P3分别求解 |
| B15 | 5 | [p3_n5.tsv](../appendix_data/word_tables/p3_n5.tsv) | P2/P3分别求解 |

<!-- Word排版建议：TSV为UTF-8 BOM编码，按制表符转换为表格。各核数独立表题，按case_id升序排列。P1/P2用三列表；P3用六列表，必要时横向页，不缩小文字强塞。每张100行表允许跨页，重复表头、禁止单行跨页；可在case_025/050/075后分为25行续表，标注“续”，保持编号和列含义。Makespan与Added Copy按归档整数显示，Cache Hit Rate版面可显示四位小数，但交付CSV/TSV保留原精度；命中率不转换为未标明的百分数。每个P3表题脚注保留对应比较口径。数据必须实际并入后续Word，不能仅以文件链接替代逐用例附表。内部审计文件和本注释不进入最终论文。 -->

## B.4 补充结果图

问题一与问题二的平均Speedup均先逐case计算正式单核基准与相应多核结果的比值，再对100个case取算术平均。

[FIGURE: fig1_p1_speedup]

<!-- 插图位置：B.4；建议题注：问题一在N=1至5下的平均Speedup。使用已有冻结图，不重新绘制。 -->

[FIGURE: fig2_p2_speedup]

<!-- 插图位置：B.4；建议题注：问题二在N=1至5下的平均Speedup。单核参考共用正式基准。使用已有冻结图。 -->

VNS相对Multi-seed的收益分布用于描述正式流水线相邻阶段的结果变化，不构成独立同预算算法或单一机制的因果消融。

[FIGURE: fig7_vns_gain_dist]

<!-- 插图位置：B.4；正文10.3交叉引用；建议题注：正式full100实验中VNS相对Multi-seed的逐case收益分布。使用已有冻结图。 -->

Cache Hit Rate与no-L2/L2性能比值的散点关系只用于相关性描述。图中N=2至5采用分别求解的P2/P3最终VNS结果，不是same-plan Cache对照。

[FIGURE: fig8_cache_hit_vs_speedup]

<!-- 插图位置：B.4；正文9.4和10.4交叉引用；建议题注：N=2至5下共享只读L2 Cache命中率与P2/P3性能比值的关系。仅说明相关性。使用已有冻结图。 -->

<!-- 内部来源审计见paper/APPENDIX_DATA_PROVENANCE.md；完整性和从交付CSV复算的核验见paper/appendix_data/VALIDATION.md。正式merged CSV不可解析，本附录从冻结归档job JSON恢复，不声称已读取merged CSV。 -->
