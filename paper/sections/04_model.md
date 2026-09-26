# 4 多核图划分与调度统一模型

本章建立三个问题共用的方案表示、可行性条件与评价目标。统一之处在于：三个问题都从同一计算图出发，生成图划分、子图到计算核的映射以及各核上的子图执行顺序；差异则由官方 Evaluator 对 Task、跨边通信和共享只读L2 Cache的不同执行语义给出。因而，本章只定义“求解什么”和“如何由官方规则评价”，候选如何产生和改进留待第5章说明。

<!-- Evidence: paper/EVIDENCE_MAP.md A-C；src/npu_scheduler/graph.py；src/npu_scheduler/types.py；src/npu_scheduler/evaluator/official_adapter.py -->

## 4.1 统一求解对象与方案表示

### 4.1.1 计算图

将剔除输入文件中显式 `COPY_IN`、`COPY_OUT` 操作后的可调度计算图记为

$$
G=(V,E),
$$

其中，$V=\{v_1,\ldots,v_n\}$ 为可参与图划分与调度的操作节点集合，$E\subseteq V\times V$ 为经正式输入校验并恢复 tensor 数据依赖后得到的有向边集合。图 $G$ 为有向无环图。对节点 $v_i$，记

- $c_i>0$ 为其计算周期数；
- $p_i$ 为其执行流水线类型；
- $\operatorname{Pred}(i)$、$\operatorname{Succ}(i)$ 分别为直接前驱和直接后继集合；
- $D_i^{\mathrm{in}}$、$D_i^{\mathrm{out}}$ 分别为其输入和输出 tensor 字节数之和。

对依赖边 $(v_i,v_j)\in E$，记 $d_{ij}\ge 0$ 为该依赖携带的数据字节数。这里的 $d_{ij}$ 既包括输入中直接记录的边数据量，也包括由 tensor 的生产者—消费者关系归并得到的数据量。

源码还预计算拓扑序、节点深度、向上/向下路径长度、关键节点集合、弱连通分量和各流水线累计工作量。这些量服务于候选生成和启发式排序，不改变原图依赖关系。

<!-- Evidence: src/npu_scheduler/graph.py -->

### 4.1.2 图划分

设图被划分为 $B$ 个非空子图（或块）

$$
\mathcal{B}=\{B_1,B_2,\ldots,B_B\},\qquad B_b\subseteq V.
$$

定义节点到子图的映射

$$
\pi:V\rightarrow\{1,2,\ldots,B\},
$$

其中 $\pi(v_i)=b$ 表示节点 $v_i$ 属于子图 $B_b$。实现中，子图按一个与依赖关系一致的全局块序排列；每个块内部的节点仍按原图拓扑顺序组织。

粗化过程不是任意合并。它先在某个保持DAG约束的节点顺序上形成连续原子单元，再在工作量预算内合并相邻原子单元。连续区间式聚合用于避免任意收缩可能引入的商图环路。

<!-- Evidence: src/npu_scheduler/partition/coarsening.py；paper/EVIDENCE_MAP.md C“图粗化” -->

### 4.1.3 核映射与核内顺序

设可用计算核集合为

$$
\mathcal{C}=\{0,1,\ldots,C-1\}.
$$

定义子图到计算核的映射

$$
\kappa:\{1,2,\ldots,B\}\rightarrow\mathcal{C}.
$$

对每个核 $k\in\mathcal{C}$，将全局块序中满足 $\kappa(b)=k$ 的子图依次投影，得到核内执行序列

$$
\sigma_k=(b_{k,1},b_{k,2},\ldots,b_{k,L_k}).
$$

因此，一个候选方案可统一表示为

$$
X=(\mathcal{B},\kappa,\Sigma),\qquad
\Sigma=\{\sigma_k\mid k\in\mathcal{C}\}.
$$

在提交给官方 Evaluator 时，$\pi$ 被转换为节点到子图编号的映射，$\Sigma$ 被转换为各核的子图编号列表。这与实现中的 `node_to_subgraph` 和 `core_schedules` 一一对应，但本文使用数学映射和序列描述方案，而不把程序字段名作为模型概念。

<!-- Evidence: src/npu_scheduler/types.py Solution.plan -->

### 4.1.4 时间与通信符号

对官方执行模型构造出的 Task $q$，记其开始和结束时刻分别为 $S_q$ 与 $F_q$。若 Task $r$ 必须等待 Task $q$，则其时序关系可抽象写为

$$
S_r\ge F_q+\delta_s(q,r;X),
$$

其中，$s\in\{1,2,3\}$ 表示问题场景，$\delta_s$ 由该场景的正式Task构造、COPY规则、等待参数和带宽规则决定。本文不以自定义解析式替代官方执行模拟；$S_q$、$F_q$及最终完工时间均以官方 Evaluator 返回结果为准。

## 4.2 三种执行场景的任务构造

统一方案 $X$ 在三个问题中共享图划分与核映射表示，但官方执行器对 Task 和通信事件的构造不同。为避免把三种场景误写成三套求解算法，定义评价映射

$$
\mathcal{E}_s(X)=
\bigl(M_s(X),A_s(X),P_s(X),H_s(X)\bigr),
\qquad s\in\{1,2,3\},
$$

其中 $M_s$、$A_s$、$P_s$、$H_s$ 分别表示官方返回的 Makespan、Added Copy、spill字节量和Cache命中率。对于没有只读Cache统计的场景，$H_s(X)=0$。

<!-- Evidence: src/npu_scheduler/evaluator/official_adapter.py；src/npu_scheduler/types.py Evaluation -->

### 4.2.1 问题一：Scene A

问题一按子图封装 Task。子图边界处需要根据正式规则插入DDR方向的COPY操作，跨Task依赖使用Scene A的跨核等待参数，同核Task之间使用相应的同核等待规则。因而，图划分不仅改变每个Task包含的计算节点，也改变Task边界和相应数据搬运。

从模型角度看，问题一的Task集合可记为 $\mathcal{T}_1(X)$，通常与子图集合 $\mathcal{B}$ 对应；其依赖、等待和COPY事件由官方Scene A执行器从原始图和plan共同构造。本文不将其简化为“只有核内调度”，也不忽略子图边界产生的通信代价。

<!-- Evidence: paper/EVIDENCE_MAP.md A“P1 / Scene A”“Task组织”“COPY机制”；src/npu_scheduler/evaluator/official_adapter.py OfficialEvaluator.raw -->

### 4.2.2 问题二：Scene B

问题二按计算核组织 Task：分配到同一核的子图被组织进该核对应的Task，同核tensor采用片上直接通信；当依赖边的两端被分配到不同核时，官方执行器插入相应的 `COPY_OUT` 和 `COPY_IN`，并使用Scene B规定的跨核COPY等待参数。

令

$$
E_\times(X)=\{(v_i,v_j)\in E:\kappa(\pi(v_i))\ne\kappa(\pi(v_j))\}
$$

为方案 $X$ 产生的跨核依赖边集合。$E_\times(X)$ 决定哪些原始依赖需要进入跨核COPY构造，但具体COPY合并、等待和数据搬运统计仍由官方Scene B执行器完成。

<!-- Evidence: paper/EVIDENCE_MAP.md A“P2 / Scene B”“Task组织”；src/npu_scheduler/evaluator/official_adapter.py -->

### 4.2.3 问题三：共享L2资源下的多核切图与调度

问题三沿用问题二的按核Task与跨核COPY机制，并在 `COPY_IN` 的读取路径上增加所有核心共享的只读L2 Cache（以下简称共享L2 Cache）。只有 `COPY_IN` 可以查询该Cache：

1. 命中时，读取进入独立的Cache读取带宽池；
2. 未命中时，数据从DDR读取，完成后按FIFO规则写入Cache；
3. 容量不足时按进入顺序淘汰；
4. 命中不会刷新FIFO先后顺序。

因此，共享L2 Cache状态影响读取完成时间和最终Makespan，同时产生Cache命中率评价量。Cache只读；未命中数据读取完成后的写入、容量不足时的淘汰以及命中不刷新顺序均遵循FIFO规则。正文使用官方题面术语“共享只读L2 Cache”；`read_only` 是实现字段，FIFO仅描述访问状态更新和替换行为。

<!-- Evidence: paper/EVIDENCE_MAP.md A“P3相对P2的增加”；正式说明 `docs/多核并行模拟执行算法.md`，本章事实以EVIDENCE_MAP冻结结论为准 -->

### 4.2.4 场景参数化表达

三种执行语义可统一写成

$$
(\mathcal{T}_s,\mathcal{D}_s,\mathcal{Q}_s)
=\Phi_s(G,X,\Theta_s),
$$

其中，$\mathcal{T}_s$ 为Task集合，$\mathcal{D}_s$ 为执行依赖及COPY事件集合，$\mathcal{Q}_s$ 为场景特有状态（问题三包含FIFO Cache状态，问题一和问题二为空），$\Theta_s$ 为第6章给出的正式硬件与场景配置。函数 $\Phi_s$ 由官方代码实现，本文只调用而不重写。

## 4.3 可行性与约束体系

### 4.3.1 节点唯一归属与完整覆盖

每个可调度节点必须且只能属于一个子图：

$$
B_a\cap B_b=\varnothing\quad(a\ne b),
\qquad
\bigcup_{b=1}^{B}B_b=V,
\qquad
B_b\ne\varnothing.
$$

该约束对应方案验证中的未知节点、重复节点、空块和未覆盖节点检查。

### 4.3.2 核映射合法性

每个子图必须映射到一个合法计算核：

$$
\kappa(b)\in\mathcal{C},\qquad b=1,\ldots,B.
$$

每个子图在其所属核的执行序列中恰好出现一次。不同核上的序列共同覆盖全部子图。

### 4.3.3 DAG依赖与商图可行性

设子图编号同时表示其全局块序位置。对任意依赖 $(v_i,v_j)\in E$，必须满足

$$
\pi(v_i)\le \pi(v_j).
$$

若两节点属于同一子图则等号成立；若属于不同子图，则前驱子图必须位于后继子图之前。该条件保证块级依赖与全局块序一致。粗化阶段采用拓扑顺序上的连续聚合，进一步避免形成有环商图。

<!-- Evidence: src/npu_scheduler/types.py Solution.validate；src/npu_scheduler/partition/coarsening.py -->

### 4.3.4 单核执行顺序

对任意核 $k$，$\sigma_k$ 是全局块序在集合 $\{b:\kappa(b)=k\}$ 上的投影。因此，若同一核上的两个子图 $B_a$、$B_b$ 满足 $a<b$，则在 $\sigma_k$ 中 $B_a$ 先于 $B_b$。从已有plan恢复方案时，核内相邻顺序也被加入块级依赖后再执行拓扑排序。

### 4.3.5 跨核通信与COPY合法性

当依赖边跨越Task或计算核边界时，必须由对应场景的官方规则构造等待或COPY事件。求解器不自行指定最终COPY字节数；它只给出图划分、核映射和顺序，官方 Evaluator 根据原始图、plan及场景配置计算实际 `added_copy_bytes` 和 `spill_added_copy_bytes`。

### 4.3.6 内存与容量限制

对任一正式存储空间类型 $r$，记配置容量为 $C_r$，官方执行过程中时刻 $t$ 的占用为 $U_r(t;X,s)$，则合法执行必须满足

$$
U_r(t;X,s)\le C_r.
$$

问题三的共享只读L2 Cache还具有独立容量参数。需要强调的是，当前方案对象的本地 `validate` 主要检查划分、核映射和块序；内存、Cache FIFO状态和跨核执行等场景合法性最终由官方 Evaluator 检查。若官方执行器因容量或执行规则返回不可行错误，该候选的评价被标记为无效，而不是由求解器修改官方规则使其通过。

<!-- Evidence: src/npu_scheduler/evaluator/official_adapter.py OfficialEvaluator.evaluate；paper/EVIDENCE_MAP.md A、D -->

## 4.4 Makespan与Added Copy目标

### 4.4.1 Makespan

对场景 $s$ 的官方Task集合 $\mathcal{T}_s(X)$，定义

$$
M_s(X)=\max_{q\in\mathcal{T}_s(X)}F_q,
$$

即全部正式Task完成的最晚时刻。实际数值直接取官方 Evaluator 返回的 `makespan`，而不是由本文另建的近似模型替代。

### 4.4.2 Added Copy

记

$$
A_s(X)=\operatorname{OfficialAddedCopyBytes}(G,X,s),
$$

其中 $A_s(X)$ 为官方结果字段 `data_movement_bytes.added_copy_bytes`。它表示场景规则因方案边界、跨核通信等产生的新增COPY字节量。spill字节量是独立字段 $P_s(X)$，不得与 $A_s(X)$混写。

### 4.4.3 字典序目标

正式候选比较采用字典序目标

$$
\mathbf{f}_s(X)=\bigl(M_s(X),A_s(X)\bigr).
$$

给定两个有效方案 $X$ 和 $Y$，$X$ 优于 $Y$ 当且仅当

$$
M_s(X)<M_s(Y),
$$

或

$$
M_s(X)=M_s(Y)\quad\text{且}\quad A_s(X)<A_s(Y).
$$

也就是说，第一目标是最小化Makespan；只有Makespan相同时，才以Added Copy作为次序决胜指标。本文不构造

$$
\alpha M_s(X)+\beta A_s(X)
$$

形式的加权目标。对无效候选，目标值按正无穷处理，不参与有效解竞争。

上述比较直接使用整数Makespan和Added Copy的精确元组比较，不设置数值容差。`spill_bytes`、`cache_hit_rate`、评价耗时等字段均不参与正式候选优劣比较。

Cache hit rate $H_3(X)$ 是问题三的重要评价量，但不在当前正式字典序目标中；spill字节量同样作为结果字段记录，而非自动加入目标。

<!-- Evidence: src/npu_scheduler/types.py Evaluation.objective；src/npu_scheduler/search/vns.py consider -->

## 4.5 官方Evaluator闭环

求解器内部存在用于候选预排序的估计器，但估计分数不等于官方Makespan，也不决定最终方案。正式闭环如下：

$$
X
\longrightarrow
\operatorname{Validate}(X)
\longrightarrow
\operatorname{Plan}(X)
\longrightarrow
\operatorname{OfficialEvaluator}_s
\longrightarrow
\mathcal{E}_s(X)
\longrightarrow
\text{字典序比较}.
$$

首先，本地方案验证检查节点覆盖、子图顺序与核映射；随后将方案转换为官方plan。适配层按问题编号分别调用问题一、问题二或问题三的官方执行函数，并把返回结果统一封装为 Makespan、Added Copy、spill、Cache hit rate 和运行时间。若候选违反正式内存、FIFO或跨核执行规则，适配层将其标记为无效候选。

为了避免重复计算，同一图、问题、硬件配置、官方代码版本和plan构成的评价可以使用缓存；缓存命中只复用已经得到的官方结果，不改变评价定义。最终incumbent只由官方Evaluation的字典序目标更新。

本文的求解器因此承担“生成和改进方案”的职责，官方 Evaluator承担“判定正式可执行性并给出最终指标”的职责。本文没有重写、替代或近似官方 Evaluator。

<!-- Evidence: src/npu_scheduler/evaluator/official_adapter.py；src/npu_scheduler/search/vns.py；paper/EVIDENCE_MAP.md C“candidate ranking” -->
