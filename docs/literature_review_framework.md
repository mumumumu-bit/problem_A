# 文献综述框架

## 一、DAG 划分与调度 (15-20 篇)

### 1.1 经典 List Scheduling
- HEFT: Topcuoglu et al., "Performance-effective and low-complexity task scheduling for heterogeneous computing", IEEE TPDS, 2002
- CPOP: 同上
- PEFT: Arabnejad & Barbosa, "List scheduling algorithm for heterogeneous systems by an optimistic cost table", IEEE TPDS, 2014
- Lookahead: Bittencourt et al., "A random graph generation to parallel programs simulation", JPDC, 2010
- 综述: Kwok & Ahmad, "Static scheduling algorithms for allocating directed task graphs to multiprocessors", ACM Computing Surveys, 1999

### 1.2 DAG 划分方法
- Metis: Karypis & Kumar, "A fast and high quality multilevel scheme for partitioning irregular graphs", SIAM JSC, 1998
- 谱划分: Hendrickson & Leland, "A multilevel algorithm for partitioning graphs", Supercomputing, 1995
- 流式划分: Stanton & Kliot, "Streaming graph partitioning for large distributed graphs", KDD, 2012
- 亲和度划分: 基于共享输入的算子聚合方法

### 1.3 通信感知调度
- Sinnen & Sousa, "Communication contention in task scheduling", IEEE TPDS, 2005
- Beaumont et al., "Memory-aware list scheduling for hybrid platforms", IPDPS, 2018
- 跨核通信代价建模与优化

## 二、变邻域搜索 (VNS) (8-12 篇)

### 2.1 VNS 基础理论
- **核心**: Mladenović & Hansen, "Variable neighborhood search", Computers & Operations Research, 1997
- Hansen et al., "Variable neighborhood search: Principles and applications", EJOR, 2001
- Hansen et al., "Variable neighborhood search": 专著, Springer, 2017
- 综述: Mladenović et al., "The variable neighborhood search metaheuristic: New variants and recent applications"

### 2.2 VNS 在调度中的应用
- Sevkli & Aydin, "Variable neighbourhood search for job shop scheduling problems", JORS, 2006
- Adibi et al., "A clustering-based modified VNS for dynamic job shop scheduling", IEEE TSM, 2012
- Yazdani et al., "A VNS algorithm for the unrelated parallel machine scheduling problem", IJPR, 2016
- Todo et al., VNS for task scheduling in cloud computing

### 2.3 VNS 在组合优化中的改进
- Adaptive VNS: Hansen et al. 专著第 5 章
- Skewed VNS: Hansen & Mladenović, "Variable neighborhood search: Basics and variants"
- Formulation space search: Mladenović et al., 2008
- Neighborhood analysis: 邻域效率统计方法

## 三、NPU/AI 加速器架构与调度 (10-15 篇)

### 3.1 NPU 架构设计
- Jouppi et al., "In-datacenter performance analysis of a tensor processing unit", ISCA, 2017 (TPU)
- Chen et al., "Eyeriss: A spatial architecture for energy-efficient dataflow for CNNs", ISCA, 2016
- Chen et al., "Eyeriss v2: A flexible accelerator for emerging deep neural networks on mobile devices", IEEE JETCAS, 2019
- Jia et al., "Dissecting the graphcore IPU architecture", ISPASS, 2019
- 华为 Da Vinci 架构相关公开资料

### 3.2 AI 编译器与算子融合
- Chen et al., "TVM: An automated end-to-end optimizing compiler for deep learning", OSDI, 2018
- Rotem et al., "Glow: Graph lowering compiler techniques for neural networks", arXiv, 2018
- Jia et al., "Optimizing DNN computation with relaxed graph substitutions", SysML, 2019
- "TASO: Optimizing deep learning computation with automatic generation of graph substitutions", SOSP, 2019

### 3.3 多核/多芯片 AI 推理
- Jia et al., "Beyond data and model parallelism for deep neural networks", SysML, 2019 (FlexFlow)
- Narayanan et al., "PipeDream: generalized pipeline parallelism for DNN training", SOSP, 2019
- Lepikhin et al., "GShard: scaling giant models with conditional computation and automatic sharding", ICLR, 2021
- Shoeybi et al., "Megatron-LM: Training multi-billion parameter language models", arXiv, 2019

## 四、元启发式算法与超参数优化 (6-8 篇)

### 4.1 候选筛选与 Surrogate 模型
- Jones et al., "Efficient global optimization of expensive black-box functions", JGO, 1998 (EGO)
- Shahriari et al., "Taking the human out of the loop: A review of Bayesian optimization", IEEE Proc., 2016
- Hutter et al., "Sequential model-based optimization for general algorithm configuration", LION, 2011

### 4.2 多目标优化与字典序
- Miettinen, "Nonlinear multiobjective optimization", Springer, 1999
- Marler & Arora, "Survey of multi-objective optimization methods for engineering", SMO, 2004
- 字典序优化的理论与实现

## 五、内存与缓存管理 (4-6 篇)

### 5.1 嵌入式内存管理
- Absl & Lee, "Memory-efficient DNN training on mobile devices", MobiSys, 2020
- Liberis et al., "μNAS: Constrained neural architecture search for microcontrollers", EuroSys, 2021
- 片上 SRAM 分配与 Spill 策略

### 5.2 Cache 复用分析
- Sen & Wood, "Reuse-based online models for caches", SIGMETRICS, 2013
- Cache 命中率与 Makespan 的关系建模

---

## 待检索数据库及检索式

| 数据库 | 检索式模板 |
|--------|----------|
| IEEE Xplore | "DAG partitioning" AND "multi-core" AND "scheduling" |
| ACM DL | "neural network" AND "task scheduling" AND "heterogeneous" |
| Web of Science | "variable neighborhood search" AND "scheduling" |
| CNKI | "多核调度" + "DAG" + "深度学习" |
| Google Scholar | "NPU compiler" "operator fusion" "memory optimization" |
| arXiv | "deep learning compiler" AND "graph optimization" |

---

## 文献筛选标准

1. **优先级 1**：顶会/顶刊 (ISCA, MICRO, DAC, OSDI, SOSP, IEEE TPDS, ACM CSUR)
2. **优先级 2**：知名期刊 (Computers & OR, EJOR, JPDC, FGCS)
3. **优先级 3**：高质量 arXiv 预印本（被引 >100）
4. **排除**：无同行评审的博客/技术报告、与 NPU 调度无关的通用调度论文

---

## 文献管理

- 工具：Zotero / JabRef（任选）
- 格式：BibTeX (`paper/references.bib`)
- 标注字段：在 `note` 中标记 `[核心]`, `[方法]`, `[背景]`, `[对比]`

---

> 生成日期：2026-09-25