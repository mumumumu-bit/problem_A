# Word整稿纳入清单

状态：**文件纳入边界与唯一图表组装规划 resolved**。本清单是内部操作文件，不进入Word正文。只从A类指定内容组装；B、C、D类均不得作为论文章节导入。历史文件原地保留，不删除、不改名。未列出的新文件须先明确类别，不能自动纳入。

最终顺序：官方封面 → 最终题目、正式摘要、关键词 → 第1—10章 → 4篇正式参考文献 → 附录A—D。本清单确定来源及位置，实际Word排版和PDF验收尚未完成；附录D既有核验状态保持不变。

## A. 最终Word必须纳入

### 正式文字来源

| 顺序 | 文件（路径相对仓库根目录） | 纳入范围 |
|---|---|---|
| 题目、摘要、关键词 | paper/ABSTRACT_V1.md | 第2节仅最终题目这一行，第3节正式摘要正文，第4节关键词；不纳入推荐理由、候选题目、字符统计注释、第5—6节审计说明。 |
| 1 | paper/sections/01_problem.md | 第1章正式文字。 |
| 2 | paper/sections/02_analysis.md | 第2章正式文字与Framework A位置。 |
| 3 | paper/sections/03_assumptions_symbols.md | 第3章正式文字及符号表。 |
| 4 | paper/sections/04_model.md | 第4章正式文字、公式、表2及Framework D位置。 |
| 5 | paper/sections/05_algorithm.md | 第5章正式文字、公式、Algorithm 1伪代码及Framework B位置。 |
| 6 | paper/sections/06_experiment.md | 第6章正式文字、硬件表与正式配置表。 |
| 7 | paper/sections/07_problem1.md | 第7章正式文字及表4(a)。 |
| 8 | paper/sections/08_problem2.md | 第8章正式文字及fig3位置。 |
| 9 | paper/sections/09_problem3.md | 第9章正式文字、表4(b)、fig4/5位置。 |
| 10 | paper/sections/10_evaluation.md | 第10章正式文字、表5、fig6；fig7/8仅交叉引用，SA仅保留现有方法选择说明。 |
| 参考文献 | paper/REFERENCES_V1.md | 仅第3节正式4篇条目；第1、2、4、5节引用审计、核验信息和内部结论不纳入。 |
| 附录A | paper/sections/appendix_A_reproducibility.md | 正式配置、运行来源及程序接口说明，保留已有复现证据边界；不是程序附件待办清单。 |
| 附录B | paper/sections/appendix_B_results.md | 正式逐用例结果说明及4张补充图；数据文件指引须落实为实际附表。 |
| 附录C | paper/sections/appendix_C_algorithm.md | SA探索说明及附表C1，数字原样保留，定位仍为探索后未采用。 |
| 附录D | paper/sections/appendix_D_ai_usage.md | AI集中披露正式说明；现有核验标记只留工作稿，须按PDF_BLOCKERS关闭后冻结，本轮不处理其元数据。 |

所有A类Markdown文件均仅提取正式内容：剔除HTML内部注释、Evidence、caption建议、LAYOUT-DECISION与排版提示。FIGURE标记转真实图片，不直接印入。第7章内部“方案A/B”说明不构成另一图位选择；图位以本清单固定表执行。正式公式、伪代码、数字、统计口径及复现限制保留。

### 必须并入的附录数据与图片素材

| 文件/素材 | Word用途 |
|---|---|
| paper/appendix_data/word_tables/p1_n1.tsv、p1_n2.tsv、p1_n3.tsv、p1_n4.tsv、p1_n5.tsv | 依次转换为附表B1—B5，置于B.1；每表100个用例。 |
| paper/appendix_data/word_tables/p2_n1.tsv、p2_n2.tsv、p2_n3.tsv、p2_n4.tsv、p2_n5.tsv | 依次转换为附表B6—B10，置于B.2；每表100个用例。 |
| paper/appendix_data/word_tables/p3_n1.tsv、p3_n2.tsv、p3_n3.tsv、p3_n4.tsv、p3_n5.tsv | 依次转换为附表B11—B15，置于B.3；保留单核固定plan、多核分别求解的脚注。 |
| paper/appendix_data/p1_per_case.csv、p2_per_case.csv、p3_per_case.csv | A类数据来源；表格内容通过上述15份TSV实际纳入，不重复印入CSV文件或用链接代替附表。 |
| results/final_visualization/figures/下本清单列出的8张结果图 | 已有PNG/SVG/PDF素材，只使用同一图的一种适宜格式插入，不重复插三种格式。 |
| Framework A/D/B成品图 | 必须纳入但当前缺成品；spec/mmd不能直接代替真实图像，A7保持未完成。 |

## B. 仅内部审计，不纳入Word

| 文件 | 仅供整稿人员使用的用途 |
|---|---|
| paper/WORD_INCLUDE_MANIFEST.md | 本纳入清单；不是论文内容。 |
| paper/FINAL_ASSEMBLY_CHECKLIST.md | 整稿执行与验收清单。 |
| paper/OUTLINE_V1.md | 最终结构指引，不复制为额外章节。 |
| paper/FIGURE_PLAN.md | 图表位置与解释边界参考，不复制为论文图表说明章。 |
| paper/EVIDENCE_MAP.md | 内部证据映射及历史数字风险。 |
| paper/APPENDIX_DATA_PROVENANCE.md | 附录数据来源审计；正式复现说明已由附录A承接。 |
| paper/appendix_data/VALIDATION.md | 完整性与聚合核验报告，不能作正式附录。 |
| paper/PDF_BLOCKERS.md | PDF冻结阻塞记录。 |
| paper/AI_USAGE.md | 内部使用事实与核验记录，正式集中披露来源为附录D。 |
| paper/COMPLIANCE_CHECKLIST.md | 规则核验及内部建议。 |
| paper/CITATION_AUDIT.md | 引用需求审计，不能当正式参考文献。 |
| paper/MD5_FREEZE_CHECKLIST.md | 冻结与提交登记，不作正文。 |
| paper/restore_appendix_data.py | 数据整理工具，既不是论文章节也不是stable solver；本轮不运行。 |
| paper/figures_source/FRAMEWORK_SPECS.md、framework_A.mmd、framework_B.mmd、framework_D.mmd | 方法图制作依据；仅未来成品图进入Word。 |
| paper/reference/official_template_original.pdf | 官方版式参考，不将整份参考PDF拼入论文。 |
| paper/logo.png、paper/title.png | 版式素材，先按官方模板核对用途；不当作结果图或独立论文章节。 |
| ABSTRACT_V1、REFERENCES_V1的非A类指定部分；sections所有HTML内部注释 | 内部理由、审计及排版提示，禁止随整文件复制。 |

## C. 程序附件阶段使用

| 文件 | 用途 |
|---|---|
| paper/PROGRAM_PACKAGE_TODO.md | 程序压缩包、README、命令、环境、依赖、工具收录、指纹及代码头工作；不进入Word。 |

实际程序、依赖与README由该清单在附件阶段落实。附录A中的已核验接口说明属于A类论文内容，不因存在程序附件而删除。若PDF实际收入程序代码，规定的代码前说明随代码落实。

## D. 历史/旧稿，不纳入Word

| 文件 | 隔离理由 |
|---|---|
| paper/main.tex | 旧论文稿，仍有top-2、旧开发集与旧结果说明，已由冻结Markdown正式稿替代。 |
| paper/main.pdf | 旧编译产物，不能当本轮最终PDF或直接抽取正文。 |
| paper/main.aux、main.log、main.out、main.synctex.gz | 旧编译中间产物，不纳入论文。 |
| paper/outline.md | 旧6章大纲，最终结构为OUTLINE_V1的10章及A—D附录。 |
| paper/REFERENCE_STRUCTURE_STUDY.md | 早期结构研究与旧P3表述，不能替代冻结大纲。 |
| paper/CHECKLIST.md | 前期筹备与开发集状态，包含旧测试/环境记录，不作正式结果说明。 |
| paper/SCHEDULE.md | 旧人员排期与实验任务，不据此触发新实验。 |
| paper/references.bib | 旧LaTeX稿文献库，正式Word仅用REFERENCES_V1第3节4篇。 |
| paper/gmcmthesis.cls、gmcm.bst | 原LaTeX排版工具，不作为Word内容。 |
| paper/figures | 空普通文件，不是可插入图片或有效图片目录。 |

## 唯一最终图表组装表（resolved）

### 图

资产标识不等于最终出版图号。Word按首次出现顺序建立图号与交叉引用；不修改文件名。11张完整图仅各插入一次。

| 范围 | 图标识 | 唯一位置 | 实际素材/状态 |
|---|---|---|---|
| 正文 | Framework A | 2.1之后 | paper/figures_source/framework_A.mmd；只有源文件，成品未完成。 |
| 正文 | Framework D | 4.2.3机制说明之后 | paper/figures_source/framework_D.mmd；只有源文件，成品未完成。 |
| 正文 | Framework B | 5.1整体流程说明之后 | paper/figures_source/framework_B.mmd；只有源文件，成品未完成。 |
| 正文 | fig3_p1p2_combined | 8.3 | results/final_visualization/figures/fig3_p1p2_combined.png（另有SVG/PDF）。 |
| 正文 | fig4_p3_noL2_vs_L2 | 9.2 | results/final_visualization/figures/fig4_p3_noL2_vs_L2.png（另有SVG/PDF）；9.3仅引用。 |
| 正文 | fig5_p3_l2_speedup | 9.4 | results/final_visualization/figures/fig5_p3_l2_speedup.png（另有SVG/PDF）。 |
| 正文 | fig6_stage_ablation | 10.1 | results/final_visualization/figures/fig6_stage_ablation.png（另有SVG/PDF）。 |
| 附录 | fig1_p1_speedup | B.4 | results/final_visualization/figures/fig1_p1_speedup.png（另有SVG/PDF）。 |
| 附录 | fig2_p2_speedup | B.4 | results/final_visualization/figures/fig2_p2_speedup.png（另有SVG/PDF）。 |
| 附录 | fig7_vns_gain_dist | B.4 | results/final_visualization/figures/fig7_vns_gain_dist.png（另有SVG/PDF）；正文10.3引用。 |
| 附录 | fig8_cache_hit_vs_speedup | B.4 | results/final_visualization/figures/fig8_cache_hit_vs_speedup.png（另有SVG/PDF）；正文9.4、10.4引用。 |

图4/5保留单核固定plan与多核P2/P3分别求解的区别；图8仅说明相关性。图6为嵌套阶段比较，不能写成单一机制独立贡献。现有正式数字和图像不重绘、不改结果。

### 表

| 最终表 | 唯一来源/位置 | 组装操作 |
|---|---|---|
| 表1 符号说明 | sections/03_assumptions_symbols.md，3.2 | 保留现有内容，补正式题注及首引。 |
| 表2 三问题机制差异 | sections/04_model.md，4.2导言后 | 题注及首引已有，统一表格宽度。 |
| 表3 正式实验配置 | sections/06_experiment.md，6.1硬件配置、6.2求解配置 | 按FINAL_ASSEMBLY_CHECKLIST将6.1硬件表及6.2配置表作为表3子表统一编号，保留两处原位置，补6.1首引。 |
| 表4 核心结果 | sections/07_problem1.md，7.2的表4(a)；sections/09_problem3.md，9.2的表4(b) | (a) P1/P2、(b) P3，不重复插入；8.2交叉引用(a)，补(b)首引。 |
| 表5 阶段消融（正式阶段比较） | sections/10_evaluation.md，10.1 | 保留原表题“正式阶段结果”及全部数字；阶段消融仅为组装分类，不能改为单变量因果消融。 |
| 附表B1—B15 | appendix_B_results.md，B.1—B.3，及上述15份TSV | 实际并入Word，跨页重复表头，保留列含义与比较口径。 |
| 附表C1 SA-VNS探索实验汇总 | appendix_C_algorithm.md，C.1 | SA详细表仅附录C，正文10.2仅交叉引用，不能混入表5。 |

组装规划已关闭；真实图片插入、题注、首引、跨页表头、出版图号、目录与交叉引用仍属于A8实际Word组装工作，不标为完成。
