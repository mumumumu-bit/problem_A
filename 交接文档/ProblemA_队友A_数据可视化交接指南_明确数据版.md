# Problem A：队友 A 最终数据可视化交接指南（数据要求明确版）

> 目标：把正式实验结果整理成论文最终统计、图表和附录。  
> 这一步不再开发算法，只处理最终数据。  
> 正式稳定代码基线：`fullrun/stable-v1 @ 34d0a42`。

---

# 一、队友 A 最终到底需要哪些数据

最终需要的原始数据只有 4 组。

---

## 数据 1：A/B/C 三组 full100 正式结果

三个目录：

```text
results/full100_teammate_A/
results/full100_teammate_B/
results/full100_teammate_C/
```

三组全部到齐后，必须先确认：

```text
100 cases
× 3 problems
× 4 core counts（N=2/3/4/5）
= 1200 jobs
```

即：

```text
P1 N2 = 100
P1 N3 = 100
P1 N4 = 100
P1 N5 = 100

P2 N2 = 100
P2 N3 = 100
P2 N4 = 100
P2 N5 = 100

P3 N2 = 100
P3 N3 = 100
P3 N4 = 100
P3 N5 = 100
```

最终必须：

```text
coverage = 1200 / 1200
```

### 每个正式 job 至少需要的数据

每个 `case × problem × core` 必须能拿到三个算法阶段：

```text
baseline
multiseed
vns
```

每个阶段至少需要：

```text
case
problem
cores
algorithm
makespan
added_copy_bytes
```

P3 还需要：

```text
cache_hit_rate
```

如果现有 CSV 中字段名字不同，只做字段映射，不重新计算原始 evaluator 结果。

### 预期 full100 明细规模

因为每个 job 有 3 个算法阶段：

```text
1200 jobs × 3 algorithms = 3600 rows
```

所以最终 merged `detail.csv` 正常情况下应约为：

```text
3600 行算法结果
```

正式绘图只使用完整结果，不允许把缺失 job 用旧 6-case / 15-case 数据补进去。

---

# 二、full100 合并后需要的文件

A/B/C 收齐后执行：

```powershell
.\.venv\Scripts\python.exe scripts\check_full100_coverage.py
```

达到：

```text
1200 / 1200
```

后再执行：

```powershell
.\.venv\Scripts\python.exe scripts\merge_full100_results.py
```

最终至少需要：

```text
results/full100_merged/detail.csv
results/full100_merged/summary.csv
```

---

# 三、detail.csv 具体需要哪些字段

正式统计时，`detail.csv` 至少应能提供这些信息：

```text
case
problem
cores
algorithm
makespan
added_copy_bytes
cache_hit_rate
```

其中：

```text
case:
case_001 ~ case_100

problem:
1 / 2 / 3

cores:
2 / 3 / 4 / 5

algorithm:
baseline / multiseed / vns
```

### 最终主结果使用哪一阶段

论文正式 P1/P2/P3 性能曲线原则上使用：

```text
algorithm = vns
```

也就是最终稳定求解器的最终结果。

### baseline / multiseed 用来做什么

只用于算法阶段消融：

```text
baseline -> multiseed
multiseed -> vns
```

不能把：

```text
VNS相对baseline的改善
```

写成：

```text
相对官方单核的加速比
```

两者必须严格分开。

---

# 四、数据 2：100-case 官方单核基准

队友 C 已完成：

```text
results/singlecore_full100/
├── manifest.json
└── singlecore.csv
```

## singlecore.csv 必须包含什么

至少：

```text
case
makespan
```

如果字段名称不是 `makespan`，必须能明确找到对应的：

```text
官方固定单核启发式 Makespan
```

### 必须满足

```text
100 unique cases
case_001 ~ case_100
无缺失
无重复
Makespan > 0
```

### 这个数据用在哪里

只用于：

```text
P1 的 1~5 核平均加速比
P2 的 1~5 核平均加速比
```

P1/P2 共用这一套官方单核基准。

---

# 五、P1 最终需要哪些数据

对每一个：

```text
case_001 ~ case_100
```

需要：

### N=1

来自：

```text
singlecore.csv
```

定义：

```text
speedup = 1.0
```

### N=2/3/4/5

来自：

```text
full100_merged/detail.csv
problem = 1
algorithm = vns
cores = 2/3/4/5
```

每个 case 需要：

```text
singlecore_makespan
p1_vns_makespan
```

逐 case 计算：

```text
speedup(case,N)
=
singlecore_makespan(case)
/
p1_vns_makespan(case,N)
```

最后：

```text
P1 mean speedup(N)
=
100个case的speedup平均值
```

禁止：

```text
sum(singlecore makespan)
/
sum(multicore makespan)
```

---

# 六、P2 最终需要哪些数据

与 P1 完全相同，只是：

```text
problem = 2
algorithm = vns
```

每 case：

```text
speedup(case,N)
=
singlecore_makespan(case)
/
p2_vns_makespan(case,N)
```

最终得到：

```text
N=1,2,3,4,5
```

五个平均加速比。

---

# 七、数据 3：P3 N=1 双模式结果

队友 C 已完成：

```text
results/p3_singlecore_full100/
├── manifest.json
└── p3_n1_l2.csv
```

## p3_n1_l2.csv 必须包含

至少：

```text
case
no_l2_makespan
l2_makespan
l2_speedup
cache_hit_rate
```

推荐同时保留：

```text
no_l2_added_copy
l2_added_copy
```

### 必须满足

```text
100 unique cases
case_001 ~ case_100
无缺失
无重复
no_l2_makespan > 0
l2_makespan > 0
```

并且：

```text
l2_speedup
=
no_l2_makespan / l2_makespan
```

---

# 八、P3 N=2~5 具体需要哪些数据

P3 的正式比较是：

```text
no-L2
vs
readonly-L2
```

对应：

```text
P2 = Scene B，无 L2
P3 = Scene B + readonly L2
```

因此对于 N=2/3/4/5：

## no-L2

从：

```text
full100_merged/detail.csv
problem = 2
algorithm = vns
```

取：

```text
case
cores
makespan
added_copy_bytes
```

## readonly-L2

从：

```text
full100_merged/detail.csv
problem = 3
algorithm = vns
```

取：

```text
case
cores
makespan
added_copy_bytes
cache_hit_rate
```

## 每个 case 每个 N 计算

```text
l2_speedup(case,N)
=
P2_makespan(case,N)
/
P3_makespan(case,N)
```

最终：

```text
mean_l2_speedup(N)
=
100个case的l2_speedup平均
```

N=1 则直接使用：

```text
p3_n1_l2.csv
```

---

# 九、最终必须生成的数据表

A 最终至少生成以下 4 张正式统计表。

---

## 表 1：P1 1~5 核平均加速比

文件：

```text
results/final_visualization/tables/p1_speedup_1to5.csv
```

格式：

```text
cores,mean_speedup
1,1.000...
2,...
3,...
4,...
5,...
```

推荐额外保存：

```text
std
median
min
max
```

但正文主曲线只需要：

```text
cores
mean_speedup
```

---

## 表 2：P2 1~5 核平均加速比

```text
results/final_visualization/tables/p2_speedup_1to5.csv
```

字段同 P1。

---

## 表 3：P3 1~5 核 L2 对比

```text
results/final_visualization/tables/p3_l2_comparison_1to5.csv
```

至少：

```text
cores
mean_no_l2_makespan
mean_l2_makespan
mean_l2_speedup
mean_cache_hit_rate
```

注意：

```text
mean_l2_speedup
```

必须是：

```text
逐case ratio后求mean
```

不是：

```text
mean_no_l2_makespan / mean_l2_makespan
```

---

## 表 4：算法阶段消融

```text
results/final_visualization/tables/stage_ablation.csv
```

至少按：

```text
problem
cores
```

统计：

```text
baseline_mean_makespan
multiseed_mean_makespan
vns_mean_makespan

multiseed_vs_baseline_improvement
vns_vs_multiseed_improvement

multiseed_win
multiseed_tie
multiseed_loss

vns_win
vns_tie
vns_loss
```

---

# 十、论文必须生成哪些图

## 图 1：P1 1~5 核平均加速比

数据来源：

```text
singlecore.csv
+
full100 P1 VNS
```

横轴：

```text
1,2,3,4,5 cores
```

纵轴：

```text
Mean Speedup
```

---

## 图 2：P2 1~5 核平均加速比

数据来源：

```text
singlecore.csv
+
full100 P2 VNS
```

---

## 图 3：P1/P2 合并版

数据：

```text
P1 mean speedup
P2 mean speedup
```

可加参考线：

```text
Ideal linear speedup: y=N
```

---

## 图 4：P3 no-L2 vs readonly-L2

数据来源：

```text
N=1:
p3_n1_l2.csv

N=2~5:
P2 VNS = no-L2
P3 VNS = readonly-L2
```

必须保证两条曲线统计口径一致。

---

## 图 5：P3 L2 speedup

横轴：

```text
N=1~5
```

纵轴：

```text
Mean L2 Speedup
```

数据：

```text
mean(P2_makespan / P3_makespan)
```

N=1 读取 C2 数据。

加参考线：

```text
y = 1.0
```

---

## 图 6：Baseline → Multi-seed → VNS

来源：

```text
full100 detail.csv
```

需要三个阶段：

```text
baseline
multiseed
vns
```

建议展示：

```text
平均Makespan改善率
+
win/tie/loss
```

至少其中一种。

---

# 十一、附录逐 case 数据具体需要什么

这是非常重要的一部分。

## P1 每 case

对于：

```text
case_001 ~ case_100
N=2/3/4/5
```

至少列：

```text
Case
N
Makespan
Added Copy
```

使用：

```text
problem=1
algorithm=vns
```

---

## P2 每 case

同样：

```text
Case
N
Makespan
Added Copy
```

使用：

```text
problem=2
algorithm=vns
```

---

## P3 每 case

对于 N=1：

从：

```text
p3_n1_l2.csv
```

至少：

```text
Case
N=1
No-L2 Makespan
L2 Makespan
L2 Speedup
Cache Hit Rate
```

对于 N=2~5：

从：

```text
P2 VNS + P3 VNS
```

至少：

```text
Case
N
No-L2 Makespan
No-L2 Added Copy
L2 Makespan
L2 Added Copy
Cache Hit Rate
L2 Speedup
```

---

# 十二、算法阶段收益需要哪些数据

为了做：

```text
Baseline -> Multi-seed -> VNS
```

每个正式 job 需要：

```text
case
problem
cores
baseline_makespan
multiseed_makespan
vns_makespan
```

计算：

```text
multiseed_gain
=
(baseline - multiseed)
/
baseline
```

```text
vns_gain
=
(multiseed - vns)
/
multiseed
```

win/tie/loss：

```text
win  = later < earlier
tie  = later == earlier
loss = later > earlier
```

正式稳定求解器理论上应避免明显 loss，但必须按真实结果统计，不得强行归零。

---

# 十三、可选分析需要哪些数据

## VNS 收益分布

需要：

```text
case
problem
cores
multiseed_makespan
vns_makespan
```

指标：

```text
(multiseed - vns) / multiseed
```

---

## Cache hit rate vs L2 speedup

需要：

```text
case
cores
P2 makespan
P3 makespan
P3 cache_hit_rate
```

计算：

```text
l2_speedup = P2 / P3
```

这是探索性关联图，不用于因果结论。

---

# 十四、数据完整性验收数字

正式绘图前必须看到：

```text
full100 jobs = 1200 / 1200

full100 detail:
约 3600 algorithm rows

singlecore:
100 unique cases

P3 N1:
100 unique cases
```

并验证：

```text
P1 VNS:
4 core counts × 100 = 400 rows

P2 VNS:
4 core counts × 100 = 400 rows

P3 VNS:
4 core counts × 100 = 400 rows
```

算法阶段三阶段：

```text
1200 × 3 = 3600 rows
```

---

# 十五、必须保留的数据来源信息

不能只有 CSV 数字，还必须记录 provenance。

A 最终需要保存：

```text
fullrun stable commit:
34d0a42

full100 A result commit
full100 B result commit
full100 C result commit

singlecore result commit
P3 N1 result commit

data/config.txt
```

以及：

```text
coverage结果
merge时间
可视化脚本commit
```

这些写入：

```text
results/final_visualization/README.md
```

---

# 十六、figure_numbers.md 必须包含的最终数字

```text
P1:
N1/N2/N3/N4/N5 mean speedup

P2:
N1/N2/N3/N4/N5 mean speedup

P3:
N1/N2/N3/N4/N5
mean no-L2 makespan
mean L2 makespan
mean L2 speedup
mean cache hit rate

Algorithm stages:
Baseline -> Multi-seed mean improvement
Multi-seed -> VNS mean improvement
win/tie/loss
```

以后论文正文只从：

```text
figure_numbers.md
```

复制数字，不再从旧 REPORT 或截图里找。

---

# 十七、给 Codex 的最终提示词

```text
你现在只负责 Problem A 的最终数据统计与论文可视化。

不要修改 solver，不要启动新实验。

正式数据必须来自：

1. results/full100_merged/detail.csv
2. results/full100_merged/summary.csv
3. results/singlecore_full100/singlecore.csv
4. results/p3_singlecore_full100/p3_n1_l2.csv

================================================
首先检查数据字段
================================================

full100 detail 至少需要：

case
problem
cores
algorithm
makespan
added_copy_bytes
cache_hit_rate

如果列名不同，只做字段映射。

期望：

1200正式jobs
×3 algorithm stages
≈3600 detail rows

singlecore.csv 至少需要：

case
official_singlecore_makespan

P3 N1 至少需要：

case
no_l2_makespan
l2_makespan
l2_speedup
cache_hit_rate

================================================
严格验证数量
================================================

P1 N2/N3/N4/N5：
各100个VNS结果

P2 N2/N3/N4/N5：
各100个VNS结果

P3 N2/N3/N4/N5：
各100个VNS结果

singlecore：
100 cases

P3 N1：
100 cases

missing=[]
duplicate=[]
NaN=0

未达到要求时停止正式绘图。

================================================
P1/P2正式加速比
================================================

对每个case：

speedup(case,N)
=
singlecore(case)
/
VNS_makespan(case,N)

N=1固定1.0。

最终：

mean_speedup(N)
=
100个case逐例speedup的均值

禁止：

sum(singlecore)/sum(multicore)

================================================
P3正式统计
================================================

N=1：
读取 p3_n1_l2.csv

N=2~5：

no-L2：
problem=2, algorithm=vns

readonly-L2：
problem=3, algorithm=vns

逐case：

l2_speedup
=
P2_makespan / P3_makespan

最终对100个case求均值。

================================================
必须生成
================================================

tables:

p1_speedup_1to5.csv
p2_speedup_1to5.csv
p3_l2_comparison_1to5.csv
stage_ablation.csv
figure_numbers.md

figures:

P1 1~5核平均加速比
P2 1~5核平均加速比
P1/P2合并图
P3 no-L2 vs readonly-L2
P3 L2 speedup
Baseline -> Multi-seed -> VNS

附录数据：

P1：
Case,N,Makespan,Added Copy

P2：
Case,N,Makespan,Added Copy

P3：
Case,N,No-L2 Makespan,No-L2 Added Copy,
L2 Makespan,L2 Added Copy,Cache Hit Rate,L2 Speedup

================================================
最终验证
================================================

随机抽至少3个case手算：

P1 speedup
P2 speedup
P3 L2 speedup

确保和CSV一致。

不要读取trials.jsonl。
不要扫描plan JSON。
不要使用旧6-case/15-case数字填补缺失数据。
```

---

# 十八、最终原则

> 队友 A 最终需要的不是“越多数据越好”，而是四套可信数据：full100 正式结果、100-case 单核、P3 N=1、三阶段 baseline/multiseed/VNS。所有正式图表和论文数字都必须能追溯到这四套数据。
