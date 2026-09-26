# 正式论文图表最终规划

## 使用边界

图表配置已确定。内容依据2026官方A题、现有正文和 `paper/EVIDENCE_MAP.md`；图表整理不引入新数据、不更改正式数字。框架图内容遵循 `paper/figures_source/FRAMEWORK_SPECS.md`，插入位置以下表为准。

## 一、正文方法框架图

| 图 | 唯一插入位置 | 内容与解释边界 |
|---|---|---|
| Framework A | 2.1整体求解思路之后 | 全文输入、统一求解与官方评价闭环；完整图仅放此处 |
| Framework B | 5.1整体算法流程说明之后 | seed逐个评价与VNS候选池、排序、Top-K两条路径；严格改善维护best-so-far，adaptive控制，不含SA |
| Framework D | 4.2.3共享只读L2机制说明之后 | 仅COPY_IN查询Cache，命中走独立Cache读取带宽，未命中DDR读取完成后FIFO更新；命中率不参与solver目标 |

## 二、结果图最终安排

| 图文件标识 | 位置 | 数据及统计口径 | 解释边界 |
|---|---|---|---|
| fig3_p1p2_combined | 正文8.3 | P1/P2共同单核基准，逐case Speedup后平均 | 正文仅此组合图呈现两场景曲线；不把差异归因于单一机制 |
| fig4_p3_noL2_vs_L2 | 正文9.2 | 平均Makespan；单核固定plan配对，多核分别取P2/P3 VNS | 9.3仅交叉引用；caption明确两种计划控制条件 |
| fig5_p3_l2_speedup | 正文9.4 | 逐case no-Cache/Cache比值均值及Cache Hit Rate均值 | 相同比值方向；命中率与比值不构成因果证明 |
| fig6_stage_ablation | 正文10.1 | Baseline、Multi-seed、VNS嵌套阶段，按问题和核数对合并 | 趋势图与表5精确数值互补；不是独立同预算消融 |
| fig1_p1_speedup | 附录B | P1逐case Speedup均值及误差棒 | 7.2提示附录；不在正文重复fig3的P1曲线 |
| fig2_p2_speedup | 附录B | P2逐case Speedup均值及误差棒 | 与P1共用正式单核参考，不称另行生成的P2单核实验 |
| fig7_vns_gain_dist | 附录B | 逐case(Multi-seed−VNS)/Multi-seed收益分布 | 正文10.3交叉引用，不声称所有case改善 |
| fig8_cache_hit_vs_speedup | 附录B | P3 Cache Hit Rate与P2 VNS/P3 VNS逐case比值 | 正文10.4及9.4引用，仅相关性探索 |

## 三、表格最终安排

| 表 | 唯一位置 | 内容及首次引用 |
|---|---|---|
| 表1 主要符号说明 | 3.2 | 已有符号表；Word整稿补编号与引导句，局部量在首次使用处定义 |
| 表2 三个问题的场景与执行机制差异 | 4.2导言后 | P1/P2/P3场景、Task组织、同核复用、跨核通信、共享L2与主要目标；表前首次引用；不罗列全部硬件参数 |
| 表3 正式实验与求解配置 | 6.2 | 已有配置表及首次引用；容量/带宽硬件表留6.1，完整来源记录留附录A |
| 表4(a) P1/P2核心结果 | 7.2 | 完整子表及首次引用；8.2和8.3引用，不再复制 |
| 表4(b) P3核心结果 | 9.2 | 无Cache/Cache结果、逐case比值均值和命中率；区分单核固定plan与多核分别求解 |
| 表5 正式阶段结果 | 10.1 | 三问题与各核数的阶段均值、改善率和win/tie/loss；阶段性比较 |
| 附表C1 SA-VNS探索实验汇总 | 附录C.1 | 从原正文表6迁移，数字不变；仅作探索后未采用记录 |

## 四、附录图表与来源

附录A记录正式配置和manifest provenance。附录B收录完整逐用例结果，以及fig1、fig2、fig7、fig8；逐用例字段满足官方题面，不由均值反推。
附录C收录SA详细表格、必要说明及原始数字，源文件为 `paper/sections/appendix_C_algorithm.md`；正文10.2只保留方法选择总结及“详细探索结果见附录C。”
附录D记录实际AI使用与合规披露。

## 五、正文交叉引用与排版

- 正文方法图固定为A、B、D三张，结果图固定为fig3、fig4、fig5、fig6四张。
- Framework A、B、D锚点分别在2.1后、5.1流程后、4.2.3机制后；Framework D在第9章仅引用。
- 图4仅完整放9.2；图5放9.4。P3两图都区分单核配对与多核分别求解，不描述为全核数固定plan实验。
- 图题正式称“共享只读L2 Cache”，FIFO只用于说明更新与替换；文件名中的noL2/L2保留。
- 图与表的最终出版编号按Word首次出现顺序统一。资产标识fig3—fig6与出版图号建立映射，不把文件标识直接等同于最终图号。
- Markdown锚点转换为真实图片、题注和交叉引用，HTML内部注释不进入论文。
