# SA-VNS Experimental Summary

## 1. Experimental Motivation

The stable VNS accepts only strict lexicographic improvements, with Makespan as the primary objective and Added Copy as the secondary objective. Because strict descent can become trapped in a local basin, we tested a bounded simulated-annealing escape that permits a small, finite number of uphill Makespan moves after stagnation. The experiment was designed to determine whether this escape produces repeatable improvements without changing the official objective or evaluator budget.

## 2. Experimental Design

The evaluation had three stages:

- **Stage 1:** a four-task pilot at seed 2026.
- **Stage 2:** two tasks repeated with seeds 2026, 2027, and 2028.
- **Expansion:** eight fixed cross-case tasks at seed 2026.

The control and SA arms used identical budgets and search settings within each stage; only `sa_enabled` differed. The SA parameters remained frozen throughout (`T0=0.01`, cooling `0.90`, minimum temperature `0.001`, stagnation trigger `4`, and at most `4` uphill acceptances). No parameter was changed in response to intermediate results.

Results are classified lexicographically. A lower Makespan is a win even if Added Copy increases. Added Copy is reported separately to expose the data-movement trade-off; it does not reverse a Makespan win.

## 3. Stage 1 Results

| Task | Control Makespan | SA Makespan | Relative change | Control Added Copy | SA Added Copy | Calls C/SA | SA uphill | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| case_001 P1 N2 | 117436 | 117436 | 0.0000% | 3456 | 3456 | 22 / 24 | 1 | tie |
| case_005 P1 N4 | 95618 | 95404 | -0.2238% | 0 | 97254 | 18 / 23 | 1 | win |
| case_025 P2 N2 | 2433638 | 2433638 | 0.0000% | 27648 | 27648 | 15 / 15 | 0 | tie |
| case_050 P2 N2 | 93992 | 93992 | 0.0000% | 202950 | 202950 | 36 / 36 | 0 | tie |

Stage 1 produced **1 win, 3 ties, and 0 losses**. The mean relative Makespan change was **-0.0560%**. The only win was `case_005 P1 N4`, where Makespan fell by 214 cycles while Added Copy increased from 0 to 97254 bytes and evaluator calls increased from 18 to 23.

## 4. Stage 2 Multi-seed Results

| Task | Seed | Control Makespan | SA Makespan | Relative change | Control Added Copy | SA Added Copy | Calls C/SA | SA uphill | Result | Copy risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| case_001 P1 N2 | 2026 | 117436 | 117436 | 0.0000% | 3456 | 3456 | 22 / 24 | 1 | tie | low |
| case_001 P1 N2 | 2027 | 117436 | 117436 | 0.0000% | 3456 | 3456 | 22 / 22 | 0 | tie | low |
| case_001 P1 N2 | 2028 | 117436 | 117436 | 0.0000% | 3456 | 3456 | 22 / 24 | 1 | tie | low |
| case_005 P1 N4 | 2026 | 95618 | 95404 | -0.2238% | 0 | 97254 | 18 / 23 | 1 | win | high |
| case_005 P1 N4 | 2027 | 95618 | 95404 | -0.2238% | 0 | 97254 | 18 / 23 | 1 | win | high |
| case_005 P1 N4 | 2028 | 95618 | 95618 | 0.0000% | 0 | 0 | 18 / 18 | 0 | tie | low |

For `case_005 P1 N4`, two of three seeds were wins and one was a tie. Both wins reproduced the same change, from 95618 to 95404 cycles (**-0.2238%**). Both also increased Added Copy from 0 to 97254 bytes and evaluator calls from 18 to 23. The Makespan gain is therefore reproducible on this task, but it carries a clear secondary data-movement and search-cost trade-off. `case_001 P1 N2` accepted two uphill moves across the three seeds but never improved the final Makespan.

## 5. Cross-case Expansion

| Task | Control Makespan | SA Makespan | Relative change | Added Copy C/SA | Calls C/SA | SA uphill | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| case_039 P1 N4 | 385717 | 385717 | 0.0000% | 13852672 / 13852672 | 36 / 36 | 0 | tie |
| case_046 P1 N4 | 140604 | 140604 | 0.0000% | 6512800 / 6512800 | 28 / 28 | 0 | tie |
| case_050 P2 N2 | 93992 | 93992 | 0.0000% | 202950 / 202950 | 36 / 36 | 0 | tie |
| case_053 P1 N2 | 777095 | 777095 | 0.0000% | 6347020 / 6347020 | 25 / 25 | 0 | tie |
| case_054 P2 N2 | 510272 | 510272 | 0.0000% | 49152 / 49152 | 23 / 24 | 0 | tie |
| case_058 P1 N2 | 2230995 | 2230995 | 0.0000% | 37036032 / 37036032 | 17 / 18 | 1 | tie |
| case_062 P2 N4 | 829845 | 829845 | 0.0000% | 7836672 / 7836672 | 16 / 16 | 0 | tie |
| case_065 P2 N4 | 13185 | 13185 | 0.0000% | 46084 / 46084 | 36 / 36 | 0 | tie |

The expansion produced **0 wins, 8 ties, and 0 losses**. Mean and median relative Makespan changes were both **0.0000%**. No new Makespan improvement appeared. Added Copy was unchanged for every task, one uphill move was accepted in total, and the mean evaluator-call difference was **+0.25**.

### case_062 historical-reference check

The historical value 811802 comes from `results/full100_teammate_B/case_062_p2_n4/job.json` on commit `34d0a42`. That run used seed 2026, a 300-second budget, candidate pool 48, top-k 3, and 32 rounds. Its multiseed phase found `balanced-4` at 811802 after 13 evaluations, and VNS retained that value after 26 evaluations.

The expansion control value 829845 comes from `results/sa_expansion/control/case_062_p2_n4/.../job.json` on commit `cd595bf`. It also used seed 2026, but used a 120-second budget, candidate pool 24, top-k 2, and 16 rounds. Its multiseed result was 832071 after 7 evaluations, and VNS reached 829845 after 16 evaluations. The graph hashes match, while the manifests record different commits, source hashes, configurations, and run identities. Thus, 811802 and 829845 belong to different experimental configurations and stages; the historical value is not used in the final quantitative SA comparison.

## 6. Aggregate Findings

1. SA caused no Makespan regression in any tested task or seed.
2. Cross-case gains were very limited.
3. The only stable positive case was `case_005 P1 N4`.
4. Its repeated improvement was small: 214 cycles, or approximately 0.2238%.
5. Both replicated wins increased Added Copy from 0 to 97254 bytes and required five additional evaluator calls.
6. The eight-task expansion produced no new win.
7. The evidence therefore does not support adopting SA as a principal enhancement in the formal stable solver.

In concise terms, **SA only provides localized improvements and does not demonstrate consistent cross-case gains.** This conclusion does not mean that the bounded escape is universally ineffective; it means that its observed benefit is too narrow to justify replacing the tested stable configuration.

## 7. Final Engineering Decision

The formal full100 result remains on `fullrun/stable-v1`. The experimental branch `experiment/sa-vns-v1` is not merged into it. The stable full100 run is already complete, the SA expansion did not show sufficiently broad benefit, and rerunning full100 would impose substantial cost without supporting evidence.

## 8. Reproducibility

- SA branch: `experiment/sa-vns-v1`
- Bounded SA implementation: `82424cb` — `experiment: add bounded SA escape to VNS`
- Multi-seed Stage 2 preparation: `9b3b4df` — `experiment: add multi-seed SA stage2 pilot`
- Cross-case expansion preparation: `2370d01` — `experiment: add SA cross-case expansion study`
- Expansion runner fix: `cd595bf` — `fix: correct expansion runner path joining`
- HEAD used for the expansion archive: `cd595bf72688075e2454114687467ed8225c8882`
- Final pytest status before archiving: **63 passed**

The detailed machine-readable archive is `analysis/sa_experiments_summary.csv`. It contains 18 records: 4 from Stage 1, 6 from Stage 2, and 8 from the expansion.

## 9. Paper-ready Description

### 中文版

为缓解严格下降 VNS 易陷入局部最优的问题，本文在原搜索框架上增加了受限模拟退火逃逸机制，仅在连续停滞后以有限概率接受少量 Makespan 劣化解，并保持参数和评价预算不变。三阶段实验表明，`case_005 P1 N4` 在 3 个随机种子中取得 2 次小幅改善，Makespan 均由 95618 降至 95404，降幅约 0.2238%；但两次改善均使 Added Copy 从 0 增至 97254 bytes，并增加了评价调用次数。随后开展的 8 任务跨算例验证全部为 tie，未观察到新的 Makespan 收益或回退。结果说明该机制仅带来局部、有限的改善，跨算例泛化不足且存在搬运代价，因此最终求解器保留严格下降 VNS，不采用 SA 增强。

### English version

We evaluated a bounded simulated-annealing escape mechanism on top of the strict-descent VNS. Uphill Makespan moves were permitted only after stagnation, with fixed temperature parameters and a strict cap on accepted uphill moves. On `case_005 P1 N4`, two of three seeds reduced Makespan from 95,618 to 95,404 cycles, a localized improvement of 0.2238%. However, both wins increased Added Copy from 0 to 97,254 bytes and required five additional evaluator calls. The other replicated task showed no final improvement despite uphill acceptance. In the subsequent eight-task cross-case expansion, all comparisons were ties: no new Makespan gain or regression was observed. These results indicate limited cross-case generalization and a material added-copy trade-off in the only repeatable positive case. Therefore, the SA extension was not adopted in the final solver, which retains the strict-descent VNS.

## 10. SA ablation summary

| Setting | Tasks / Seeds | Wins | Ties | Losses | Mean Makespan Change | Added Copy Observation |
|---|---|---:|---:|---:|---:|---|
| Stage 1, case_005 | 1 task / 1 seed | 1 | 0 | 0 | -0.2238% | 0 to 97254 bytes |
| Stage 2, case_005 | 1 task / 3 seeds | 2 | 1 | 0 | -0.1492% | Both wins: 0 to 97254 bytes |
| Expansion aggregate | 8 tasks / 1 seed | 0 | 8 | 0 | 0.0000% | No change across all tasks |
