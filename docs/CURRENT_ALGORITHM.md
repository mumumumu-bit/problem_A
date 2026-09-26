# 当前算法真实实现状态
## 生成时间: 2026-09-25
## 仅包含已实现的代码，不含计划

---

## 1. 种子/初始解 (initial_partition.py)
**已实现:** 4 个族 × 3 种 grain
- balanced (workload均衡拓扑序)
- affinity (局部性拓扑序)
- critical (上行关键路径秩)
- pipe (局部性+pipe感知)
- fine_grain=2 变体（超细粒度）
- portfolio_size 最多10个全排列种子

## 2. 粗化策略 (coarsening.py)
**已实现:**
- 两级粗化: atomic units → blocks
- 3 种 grain: g=4, 12, 32
- work budget = total_cycles / (cores × grain)

## 3. Core 分配 (core_assignment.py)
**已实现:**
- HEFT 风格 ready-list 分配
- affinity_weight=0.5, pipe_balance_weight=0.2

## 4. VNS 邻域 (local_search.py + vns.py)
**已实现 (8个):**
| N | 名称 | 状态 |
|---|---|---|
| N1 | Move (单block移动) | ✅ |
| N2 | Swap (交换core) | ✅ |
| N3 | Adjacent independent reorder | ✅ |
| N4 | Adjacent merge | ✅ |
| N5 | Split | ✅ |
| N6 | Shift boundary op | ✅ |
| N7 | Connected block pair placement | ✅ |
| N8 | Critical move | ✅ |

## 5. 接受准则
**已实现: 严格下降 (strict descent only)**
- 仅接受 objective < incumbent.objective
- **NOT IMPLEMENTED: SA (模拟退火)**
- **NOT IMPLEMENTED: GA (遗传算法)**
- **NOT IMPLEMENTED: Tabu list**
- **NOT IMPLEMENTED: CP-SAT**

## 6. 候选排序 (estimator.py)
**已实现:**
- HEFT-style makespan 估算
- communication_weight=1.0
- memory_weight=0.0 (代码存在但关闭)
- cache_weight=0.0 (代码存在但关闭)
- pipe_balance_weight=0.2

## 7. 早停
**已实现:**
- max_rounds=16
- stagnation_patience=8 (仅 adaptive_budget=True 时生效)
- 时间预算 (time_budget)

## 8. 自适应邻域选择
**已实现但默认关闭:**
- adaptive_budget=False (默认)
- 当启用时: 20%随机探索 + 80%贪婪选择

## 9. 评估器
**已实现:**
- OfficialEvaluator 封装 P1/P2/P3 三个场景
- 结果缓存 (EvaluationCache)
- 并行 job 级 ProcessPoolExecutor

## 10. P3 (问题3 / Cache)
**已实现:**
- 评估器: evaluate_problem_3 (FIFO Cache模拟)
- 求解器: 与P1/P2使用同一套plan生成逻辑
- 注意: cache_weight=0 → 求解器不针对Cache优化

## 汇总: 缺失模块
| 模块 | 状态 |
|---|---|
| SA (模拟退火) | **NOT IMPLEMENTED** |
| GA (遗传算法) | **NOT IMPLEMENTED** |
| Tabu search | **NOT IMPLEMENTED** |
| CP-SAT / ILP | **NOT IMPLEMENTED** |
| Cache感知切分 | **NOT IMPLEMENTED** (cache_weight=0) |
| Memory硬约束 | **NOT IMPLEMENTED** (memory_weight=0) |
| 全局优化 | **NOT IMPLEMENTED** (仅局部VNS) |