# 5 Multi-seed + VNS求解算法

本章在第4章统一方案表示和字典序目标的基础上，说明正式stable solver如何构造初始方案、形成多样化候选、调用官方 Evaluator，并通过变邻域搜索持续维护best-so-far方案。算法的核心思想是：先用多种图粗化与核分配策略覆盖不同结构偏好，再在正式评价得到的incumbent附近进行受限局部搜索。经典ready-list/HEFT与VNS背景需要外部文献支持的位置暂记为 `[CITATION-NEEDED]`。

<!-- Evidence: paper/EVIDENCE_MAP.md C；src/npu_scheduler/partition/initial_partition.py；src/npu_scheduler/search/vns.py -->

## 5.1 正式算法总体流程

给定计算图 $G=(V,E)$、计算核数 $C$、问题编号 $s$、官方 Evaluator 和求解配置，正式流程由以下阶段组成：

1. **图特征预计算**：校验原始图，移除显式COPY节点以形成可调度DAG，恢复tensor生产者—消费者依赖，计算拓扑序、路径长度、关键节点、连通分量、边数据量和流水线工作量。
2. **Baseline构造**：用中间粒度的balanced粗化产生一个基础划分，再进行balanced核分配，得到阶段比较基准。
3. **Multi-seed候选生成**：构造whole候选以及balanced、affinity、critical、pipe四类主要seed family在多个grain下的候选；正式full100还包含fine-grain=2变体。
4. **核分配**：每个粗化结果通过受HEFT启发的ready-list调度映射到多个计算核，形成全局块序与各核执行序列。[CITATION-NEEDED]
5. **Multi-seed正式评价**：对未重复且预算允许的seed候选逐个调用官方 Evaluator，以字典序目标更新incumbent，并记录Baseline和Multi-seed阶段快照。
6. **VNS候选生成与初筛**：围绕当前incumbent，从8类邻域中的一个生成有界候选池；先由启发式估计器排序，再取Top-K送入官方 Evaluator。[CITATION-NEEDED]
7. **严格下降更新**：只有官方Evaluation在字典序上严格优于当前值时才接受候选并更新incumbent。
8. **adaptive选择与停止**：根据邻域历史尝试次数、成功次数和Makespan收益选择后续邻域；达到轮数、预算、停滞或有效邻域耗尽条件时停止。
9. **输出**：返回最终incumbent、正式Evaluation、三个阶段快照及邻域统计。

需要特别区分两种候选处理方式：Multi-seed阶段的唯一seed候选在预算允许时直接接受官方评价；`candidate pool → heuristic ranking → Top-K → official evaluator`的两级筛选主要用于VNS邻域候选，而不是先把全部Multi-seed seed混入一个48候选池再只评价3个。

整体流程可记为

$$
G
\rightarrow \text{特征预计算}
\rightarrow \text{多粒度Multi-seed}
\rightarrow \text{核分配}
\rightarrow \text{正式评价与初始incumbent}
\rightarrow \text{VNS候选池与Top-K评价}
\rightarrow X^*.
$$

其中 $X^*$ 仅表示本次受限搜索得到的best-so-far有效方案，不表示全局最优解。

<!-- Evidence: src/npu_scheduler/search/vns.py solve；src/npu_scheduler/partition/initial_partition.py seeds -->

## 5.2 Baseline初始方案

Baseline用于提供最先尝试的可行方案和阶段比较起点，不作为独立创新算法。设正式grain序列为 $(g_1,g_2,g_3)$，Baseline取其中间位置的grain，即正式full100中的 $g_2=12$，并采用balanced模式完成粗化与核分配。

balanced粗化直接使用图的确定性拓扑序。设总节点工作量为

$$
W=\sum_{v_i\in V}c_i,
$$

则给定核数 $C$ 和grain $g$ 时，粗化目标工作量为

$$
\tau(C,g)=\max\left\{\max_i c_i,\frac{W}{Cg}\right\}.
$$

算法先在拓扑序上生成保持连通/共享输入倾向的连续原子单元，再按目标工作量 $\tau$ 合并相邻原子单元形成块。balanced核分配依次处理这些块，将当前块放到累计流水线工作量较小的核上。

若Baseline未能得到官方可执行方案，算法继续尝试后续seed；此时Baseline阶段快照记录随后出现的首个有效起点。若全部常规seed都未形成有效incumbent，则使用whole-graph应急方案再次调用官方 Evaluator。该应急步骤保证搜索不会因为所有常规初始候选无效而静默结束，但它仍需通过官方规则确认。

<!-- Evidence: src/npu_scheduler/partition/initial_partition.py；src/npu_scheduler/partition/coarsening.py；src/npu_scheduler/search/vns.py -->

## 5.3 多粒度Multi-seed候选生成

### 5.3.1 共同粗化框架

四类seed family共享两级粗化框架。首先选择一个保持DAG约束的节点顺序；随后沿该顺序形成原子单元。相邻节点存在直接依赖或共享输入tensor时被视为较强联系，弱联系切断阈值、原子单元工作量阈值和最终块工作量上限共同决定划分边界。第二级再按 $\tau(C,g)$ 贪心合并相邻原子单元。

grain控制目标块规模：在其他条件不变时，较大的 $g$ 使 $W/(Cg)$ 变小，倾向形成更细的块；较小的 $g$ 倾向形成更粗的块。但实际块数还受单节点最大工作量、连通分量边界、强弱联系和原子单元阈值影响，不能把grain直接等同于固定子图数量。

正式full100的主grain为

$$
\mathcal{G}_{\mathrm{main}}=\{4,12,32\},
$$

并加入fine-grain配置值 $g_f=2$。这里“fine-grain”是配置和候选来源名称；由于目标工作量与grain成反比，本文只按实现事实称其为额外的 $g=2$ 候选变体，不据名称推导独立性能性质。

<!-- Evidence: src/npu_scheduler/partition/coarsening.py；A/B/C full100 manifest冻结于paper/EVIDENCE_MAP.md D -->

### 5.3.2 balanced family

balanced family使用原图确定性拓扑序进行连续粗化。核分配时，它不计算关键路径ready time或输入复用奖励，而以各核已累计的流水线工作量总和作为主要负载指标，将当前块分配到该指标最小的核。

因此，该family的真实含义是“拓扑顺序粗化 + 累计负载平衡式核分配”，而不是根据名称推测出的任意均匀切块。

### 5.3.3 affinity family

affinity family使用局部性导向的前驱优先深度遍历顺序进行粗化。该顺序保持DAG可行性，并倾向把同一弱连通分量及具有输入联系的节点相邻组织。

核分配阶段，对候选核 $k$ 先估计前驱就绪时间、核可用时间、同核/跨核等待和块工作量，得到预计完成时间；再根据当前块输入tensor与该核已驻留输入tensor的交集计算复用量，将加权复用收益从评分中扣除。评分越小，候选核越优。

故affinity family的真实含义是“局部性顺序粗化 + 输入tensor复用偏好的最早完成式分配”。复用项只是核分配启发式，不是官方Cache命中模型。

### 5.3.4 critical family

critical family首先依据节点向上路径长度构造优先键，在保证拓扑合法的前提下使剩余关键路径较长的节点优先。块级调度时，再计算

$$
r_b=w_b+\max_{d\in\operatorname{Succ}(b)}
\left(r_d+\frac{D_{bd}}{B_w}\right),
$$

其中，$w_b$ 为块工作量，$D_{bd}$ 为块间数据字节数，$B_w$ 为配置带宽。块按较大的 $r_b$ 优先进入ready-list；每个块选择预计完成时间较小的核。

该式只用于启发式核分配顺序和估计，不替代官方Makespan。critical family的真实含义是“关键路径优先粗化 + 上行rank驱动的最早完成式分配”。其ready-list思想受HEFT启发。[CITATION-NEEDED]

### 5.3.5 pipe family

pipe family与affinity family一样采用局部性导向顺序粗化，但块级处理顺序使用critical family的上行rank。对候选核的评分同时考虑：

1. 预计完成时间；
2. 输入tensor复用收益；
3. 该核上 `PIPE_M`、`PIPE_V` 加入当前块后的投影最大累计负载惩罚。

因此，pipe family的真实含义是“局部性粗化 + 关键rank顺序 + 输入复用收益和 `PIPE_M`/`PIPE_V` 投影最大负载惩罚共同修正的核选择”。该评分产生主要流水线负载的平衡倾向，但不直接最小化两条流水线的负载差，也不是独立的流水线执行模拟；最终优劣仍由官方 Evaluator决定。

### 5.3.6 候选组合、优先级与去重

候选组合先包含四个优先seed：`affinity-4`、`critical-12`、`pipe-32`和`balanced-32`；随后立即插入 $g_f=2$ 的四类变体，再补充四类family与全部grain的网格组合。相同 `(family, grain)` 只保留一次，并受portfolio大小限制。

whole-graph候选在图规模不超过配置阈值时加入，作为长链或带宽受限情形下的结构性候选。所有方案还通过内容摘要去重，避免对相同划分和核映射重复调用官方 Evaluator。

fine-grain=2确实进入正式full100 Multi-seed候选生成，且正式job记录中出现过相应候选来源；但当前不存在独立fine-grain full100消融，本文不把它的存在解释为独立性能贡献。

<!-- Evidence: src/npu_scheduler/partition/initial_partition.py；src/npu_scheduler/types.py Solution.digest；paper/EVIDENCE_MAP.md C、H -->

## 5.4 HEFT-style核分配与候选排序

### 5.4.1 块级DAG与工作量

给定块集合 $\mathcal{B}$，先建立块级DAG。若原图存在边 $(v_i,v_j)$ 且 $\pi(v_i)\ne\pi(v_j)$，则在对应块之间建立依赖，并累计块间数据字节数 $D_{bd}$。

对块 $B_b$，按流水线类型累计节点周期数。实现将各流水线累计周期数的最大值作为块工作量近似：

$$
w_b=\max_{p}\sum_{v_i\in B_b,\,p_i=p}c_i.
$$

该近似用于候选构造，不是官方执行时间。

<!-- Evidence: src/npu_scheduler/schedule/core_assignment.py block_view -->

### 5.4.2 ready-list与核选择

对critical和pipe模式，块级ready-list按5.3.4定义的上行rank优先；balanced和affinity模式采用块级拓扑序。对非balanced模式，块 $b$ 分配到候选核 $k$ 时的预计就绪时刻为

$$
R_{bk}=\max_{a\in\operatorname{Pred}(b)}
\left\{F_a+\mathbf{1}[\kappa(a)\ne k]
\left(\Delta_{\mathrm{cross}}+\frac{D_{ab}}{B_w}\right)\right\},
$$

预计完成时刻为

$$
\widehat F_{bk}
=\max\{A_k+\mathbf{1}[A_k>0]\Delta_{\mathrm{same}},R_{bk}\}+w_b,
$$

其中 $A_k$ 为核 $k$ 的当前可用时刻；当核尚未安排块时，同核等待项不加入。不同family再按5.3节所述加入复用奖励或 `PIPE_M`/`PIPE_V` 投影最大负载项，选择评分最小的核。该过程属于受HEFT启发的ready-list调度，而非标准HEFT的逐字复现。[CITATION-NEEDED]

### 5.4.3 启发式候选排序

进入VNS后，一个邻域最多生成给定candidate pool规模的合法唯一候选。每个候选由内部估计器产生排序分数，并以方案摘要作为确定性次级排序键：

$$
\operatorname{rank}(X)=
\bigl(\widehat J_s(X),\operatorname{digest}(X)\bigr).
$$

$\widehat J_s(X)$ 只是启发式预筛信号，不等同于 $M_s(X)$。正式full100中与memory和Cache相关的估计器权重均为0，因此不能声称该排序已启用Cache-aware或memory-aware收益项。

<!-- Evidence: src/npu_scheduler/search/vns.py；paper/EVIDENCE_MAP.md C“candidate ranking”“cache/memory heuristic” -->

## 5.5 Top-K官方评价与阶段快照

正式full100的VNS候选池大小为48，Top-K为3。对当前邻域生成的候选集合 $\mathcal{N}_q(X)$，先过滤历史已评价方案并按启发式rank排序，再取

$$
\mathcal{K}_q(X)=\operatorname{TopK}_{K=3}
\bigl(\mathcal{N}_q(X),\operatorname{rank}\bigr)
$$

送入官方 Evaluator。候选池48控制一次邻域搜索最多保留的唯一候选数量；源码最多进行其3倍的扰动尝试，以跳过无变化、重复或本地验证失败的方案。

这种两级评价把计算较轻的启发式排序用于减少正式调用数量，但最终接受仍完全依赖官方Evaluation。它不是学习型ranking，也不从历史结果训练预测模型。

算法保存三个阶段快照：

- **Baseline快照**：有效Baseline；若Baseline无效，则保存随后出现的首个有效起点；
- **Multi-seed快照**：seed阶段结束时的incumbent；
- **VNS快照**：局部搜索结束时的最终incumbent。

三个快照是同一次嵌套搜索的阶段记录，不是三个独立、同预算求解器的严格因果对照。

<!-- Evidence: src/npu_scheduler/search/vns.py consider/snapshot；paper/EVIDENCE_MAP.md H -->

## 5.6 VNS邻域搜索

设当前方案为 $X=(\mathcal{B},\kappa,\Sigma)$，块数为 $B$。算法实现8个有界邻域。每个新方案都要重新执行节点覆盖、核编号和块序依赖检查；非法商图顺序会在调用官方 Evaluator之前被丢弃。

### N1：重块优先换核

- **操作对象**：优先选择工作量较大的块，候选池后段可随机选择块。
- **修改方式**：将选中块循环移动到另一个核，不改变块内节点和全局块序。
- **设计目的**：缓解单核负载集中，并探索不同跨核通信组合。

### N2：两块核归属交换

- **操作对象**：一个优先重块与另一个随机块。
- **修改方式**：交换两个块的核编号，块本身及全局顺序不变。
- **设计目的**：在不改变划分边界的情况下联合调整两个核的负载与通信关系。

### N3：相邻无直接依赖块重排

- **操作对象**：全局块序中相邻且不存在前者直接指向后者块级依赖的两个块。
- **修改方式**：交换两个块的位置及其随位置携带的核归属。
- **设计目的**：调整合法块级执行次序，为核内顺序和跨核等待创造不同组合。

若相邻块存在直接依赖，则不产生该候选；交换后仍须通过完整依赖验证。

### N4：相邻块合并

- **操作对象**：全局块序中的相邻两个块。
- **修改方式**：把后一个块的节点附加到前一个块，并删除后一个块及其核归属；合并块沿用前一块的核。
- **设计目的**：减少子图边界和潜在边界通信，同时改变块粒度。

### N5：按工作量近半拆分

- **操作对象**：至少包含两个节点的块，优先从重块中选择。
- **修改方式**：按节点原拓扑位置排序，在累计周期数首次达到块总周期数一半附近切开；前半保留原核，后半初始放到相邻编号核。
- **设计目的**：细化过重块，为负载再平衡和并行执行提供空间。

### N6：边界节点右移

- **操作对象**：全局块序中一个至少含两个节点的块及其右侧相邻块。
- **修改方式**：把前一块中拓扑位置最靠后的节点移到后一块开头，核归属保持由两个原块分别继承。
- **设计目的**：小幅移动划分边界，减少整块合并/拆分带来的结构变化。

### N7：高通信量连接块对优先同核放置

- **操作对象**：按块间数据字节数从大到小排列的有连接块对。
- **修改方式**：将块对同时放到同一目标核，块划分和全局顺序不变。
- **设计目的**：尝试消除高数据量块对之间的跨核通信。

### N8：关键块优先换核

- **操作对象**：按块内节点的向上路径长度与向下路径长度之和排序的关键块。
- **修改方式**：与N1相同，将选中关键块移动到其他核。
- **设计目的**：优先改变关键路径附近块的核归属，探索对Makespan更敏感的映射。

N8只是关键块优先的换核邻域，不是全局跳出机制，也不提供全局最优保证。

<!-- Evidence: src/npu_scheduler/search/local_search.py；src/npu_scheduler/schedule/core_assignment.py block_view -->

### Algorithm 1：Multi-seed + VNS多核图调度算法

```text
输入：计算图 G，核数 C，问题场景 s，官方评价器 E_s，求解配置 θ
输出：best-so-far方案 X*，官方评价 y*，阶段快照 snapshots

1  预计算 G 的拓扑、路径、tensor、连通分量和流水线特征
2  X* ← 空，y* ← 空，Seen ← 空，snapshots ← 空
3  依次生成 Baseline、可选whole以及Multi-seed portfolio中的候选 X
4      若已有有效incumbent且达到外部时间/评价调用预算，则结束seed阶段
5      若已有有效incumbent、已覆盖四类family且seed阶段时间份额耗尽，则结束seed阶段
6      若 digest(X) ∈ Seen，则跳过
7      将 digest(X) 加入 Seen；计算诊断性估计；调用官方评价器得到 y ← E_s(X)
8      若 y 有效且 (y.makespan, y.added_copy) 严格优于 y*，则 X* ← X，y* ← y
9      若Baseline快照尚不存在且已有有效incumbent，则记录Baseline快照
10 若仍无有效方案，则构造whole-graph应急候选并执行步骤7—8
11 记录Multi-seed快照
12 初始化8类邻域统计、活动邻域集合、轮数和停滞计数
13 while 未达到外部预算、轮数上限且仍有活动邻域 do
14     按warm-up顺序或adaptive规则选择邻域 q
15     从当前 X* 生成至多48个合法、唯一、未评价的邻域候选
16     按内部估计分数与digest排序，取前3个候选
17     for 每个Top-K候选 X' do
18         若达到外部预算，则退出循环
19         调用官方评价器得到 y' ← E_s(X')
20         更新邻域 q 的尝试、耗时、成功与Makespan收益统计
21         若 y' 有效且字典序严格优于 y*，则 X* ← X'，y* ← y'
22     end for
23     根据本轮是否改善更新停滞计数
24     adaptive开启时，淘汰尝试充分但从未成功的邻域
25     若满足动态停滞条件，则停止
26     若本轮改善则继续adaptive选择；否则切换到后续/重新选择邻域
27 end while
28 记录VNS快照并返回 X*、y*、snapshots及邻域统计
```

该伪代码对应真实程序中的去重、官方评价、阶段快照、VNS排序、严格接受与adaptive停止。第6章将给出外部seed、时间预算、最大评价次数和workers等正式实验配置；这些数值不作为算法定义在本章反复展开。

## 5.7 严格下降接受、incumbent与adaptive停止

### 5.7.1 incumbent与严格下降

令第 $t$ 次正式评价后的incumbent为 $X_t^*$，其官方目标为 $\mathbf f_s(X_t^*)$。对新候选 $Y_t$，更新规则为

$$
X_{t+1}^*=
\begin{cases}
Y_t, & Y_t\text{有效且 }\mathbf f_s(Y_t)<_{\mathrm{lex}}\mathbf f_s(X_t^*),\\
X_t^*, & \text{其他情况}.
\end{cases}
$$

因此，incumbent的官方字典序目标单调不增。程序中的“best”或“global best”仅表示截至当前已评价候选的best-so-far，不表示对全部可行方案的全局最优证明。

### 5.7.2 邻域warm-up与adaptive选择

VNS默认优先顺序为

$$
N1\rightarrow N2\rightarrow N4\rightarrow N5
\rightarrow N3\rightarrow N6\rightarrow N8\rightarrow N7.
$$

前8轮按该顺序收集统计。之后，在`adaptive_budget=true`时：

1. 优先补足尝试次数低于最低探索次数的活动邻域；
2. 探索要求满足后，以“累计Makespan收益/尝试次数”作为主要选择分数；
3. 保留20%的随机探索概率，从活动邻域中随机选择；
4. 若某邻域尝试次数已达到充分阈值而成功次数仍为0，则将其从活动集合移除。

这是一种在线预算分配和邻域选择机制，不是学习型模型。正式full100开启了adaptive，但当前没有其独立消融，因此不能把总体结果中的提升单独归因于该机制。

<!-- Evidence: src/npu_scheduler/search/vns.py select_neighbourhood/deactivation；paper/EVIDENCE_MAP.md C、H -->

### 5.7.3 停止条件

VNS在任一以下条件满足时停止：

1. 达到第6章给出的外部时间预算；
2. 达到第6章给出的最大官方评价次数；
3. 达到最大轮数，正式full100为32轮；
4. adaptive启用且连续无改善达到动态停滞条件；
5. 活动邻域集合为空。

正式配置的基础停滞阈值为8。源码对节点数超过10000的图增加2轮耐心，即使用不小于10的阈值。动态停滞还要求当前评价次数已经超过“上次改善时评价次数 + 当前耐心值”，避免仅按轮数过早终止。

当某轮找到改善时，停滞计数归零并更新最后改善位置；否则停滞计数加一。严格下降和动态停止共同保证搜索始终保存当前已知最好有效方案，但不构成最优性证明。

## 5.8 算法复杂度分析

为避免猜测官方 Evaluator内部实现，记一次官方评价成本为 $T_{\mathrm{eval}}$；记一次内部候选估计成本为 $T_{\mathrm{est}}$。设

- $n=|V|$，$m=|E|$；
- $z$ 为tensor生产者—消费者配对及节点输入集合处理的总规模；
- $h$ 为从各可调度节点穿过非调度节点以恢复依赖时的累计遍历工作量；
- $B$ 为粗化后的块数；
- $C$ 为计算核数；
- $P_g$ 为seed阶段实际构造的候选数，$P_e$ 为该阶段去重后送入官方评价的候选数（包括Baseline、whole及必要的应急whole候选）；
- $Q$ 为单轮VNS候选池大小，正式full100为48；
- $K$ 为Top-K大小，正式full100为3；
- $R$ 为最大VNS轮数，正式full100为32。

### 5.8.1 图特征预计算

拓扑排序、路径长度、连通分量和主要图统计均以稀疏图结构处理；但依赖恢复会从各可调度节点分别穿过非调度节点，因此不能无条件简化为严格线性复杂度。以 $h$ 记录这部分累计遍历工作量后，预计算成本写为

$$
O(n+m+z+h).
$$

在最坏情况下，重复依赖恢复遍历可能使 $h$ 高于 $n+m$。本文不对官方输入校验、原始COPY展开和tensor关系恢复另作未经源码证明的更紧上界。

### 5.8.2 单个候选的粗化与核分配

在给定节点顺序后，两级连续粗化对节点和输入关联进行线性扫描，其主体成本为 $O(n+z)$。构造块级DAG需要扫描图依赖，成本为 $O(n+m+z)$。

ready-list核分配对每个块枚举 $C$ 个核，并计算前驱就绪、输入复用和流水线累计量。忽略常数规模的流水线类型集合，写成

$$
O(m_B+B C+z_B),
$$

其中 $m_B$ 为块级边数，$z_B$ 为块输入集合交集处理总成本。故单个seed候选的构造成本可概括为

$$
T_{\mathrm{seed}}
=O(n+m+z+B C).
$$

### 5.8.3 Multi-seed阶段

若实际构造 $P_g$ 个seed候选，其中 $P_e\le P_g$ 个唯一候选进入官方评价，则Multi-seed阶段的上界写为

$$
O\!\left(P_g\left(n+m+z+B C\right)+P_eT_{\mathrm{eval}}\right).
$$

该式包含每个seed的构造与正式评价。实际调用次数还受去重和第6章外部预算限制。

### 5.8.4 单轮VNS候选生成与筛选

邻域生成最多进行 $3Q$ 次扰动尝试，以得到至多 $Q$ 个唯一合法候选。单个候选的块操作、摘要与完整验证最坏需要扫描块/节点/边，记为 $T_{\mathrm{nbr}}=O(n+m+B)$。随后对 $Q$ 个候选计算估计分数并排序，成本为

$$
O\!\left(QT_{\mathrm{nbr}}+QT_{\mathrm{est}}+Q\log Q\right).
$$

Top-K阶段最多增加 $K$ 次官方评价，因此单轮VNS成本为

$$
O\!\left(
QT_{\mathrm{nbr}}+QT_{\mathrm{est}}+Q\log Q+KT_{\mathrm{eval}}
\right).
$$

### 5.8.5 总体上界与解释边界

在不考虑更早预算停止的情况下，整体成本可表示为

$$
O\!\left(
n+m+z+h
+P_gT_{\mathrm{seed}}+P_eT_{\mathrm{eval}}
+R\left(QT_{\mathrm{nbr}}+QT_{\mathrm{est}}+Q\log Q+KT_{\mathrm{eval}}\right)
\right).
$$

正式参数下，VNS理论上每轮最多正式评价3个Top-K候选，但总调用数仍受第6章的最大评价次数限制，实际不超过 $P_e+RK$，并可能因去重、候选不足或提前停止而更少。由于 $T_{\mathrm{eval}}$ 取决于官方执行模拟和具体图结构，本文不猜测其内部复杂度。

上述分析说明算法通过有界portfolio、有界邻域池、Top-K和预算控制正式评价次数；它不意味着算法在多项式时间内保证最优，也不提供全局最优证明。

<!-- Evidence: src/npu_scheduler/search/vns.py；src/npu_scheduler/search/local_search.py；其余Evaluator内部复杂度显式记为T_eval -->
