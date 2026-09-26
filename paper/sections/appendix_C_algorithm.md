# 附录C 算法补充与历史探索

## C.1 SA-VNS探索后未采用

本节记录开发阶段的SA-VNS探索，未纳入stable solver或full100正式算法；探索预算与正式实验不同，不作为最终方法贡献。

严格下降VNS只接受官方字典序目标改善的候选，因此可能无法经过暂时不改善的方案到达更好的区域。为探索这一限制，开发阶段实现了允许概率接受非改进解的SA-VNS机制，并开展小规模pilot及扩展比较。下表中的每条记录是同任务、同seed下control与SA的最终结果配对，胜负仅按Makespan判定；这些探索采用120秒、36次评价上限的配置，与正式full100实验范围和预算不同。

附表C1 SA-VNS探索实验汇总

| 实验阶段 | 配对记录数/任务数 | Win | Tie | Loss | 主要观察 |
|---|---|---:|---:|---:|---|
| Stage 1 | 4条/4任务，seed=2026 | 1 | 3 | 0 | case_005 P1 N4改善214周期，Added Copy增加97254字节 |
| Stage 2 | 6条/2任务，各3个seed | 2 | 4 | 0 | case_005 P1 N4在2026、2027改善，2028持平；另一任务3次均持平 |
| Expansion | 8条/8任务，seed=2026 | 0 | 8 | 0 | Makespan及Added Copy均未变化；两条记录多用1次评价 |

Stage 1中，case_005 P1 N4的Makespan从95618降至95404周期；相对下降为 $(95618-95404)/95618\approx0.2238\%$，Added Copy从0增至97254字节，官方评价调用从18增至23次。另3条记录Makespan与Added Copy均不变；case_001 P1 N2仍增加2次评价，其余两条调用数不变。四条记录的SA调用数合计比control多7次。

Stage 2对case_001 P1 N2与case_005 P1 N4分别采用2026、2027、2028三个seed。case_005在前两个seed中均由95618降至95404周期，重复出现214周期改善；两次均伴随97254字节的Added Copy增加及18→23次评价。seed=2028时Makespan、Added Copy和调用数均持平。case_001的三次Makespan、Added Copy均持平，调用数分别增加2、0、2次。六条记录合计多14次评价，Added Copy差值合计194508字节。该结果显示同一任务在两个seed下出现可重复的小幅改善，但没有达到三个seed均稳定改善，也没有形成跨任务收益。

Expansion覆盖8个任务，8条均为tie，Makespan和Added Copy差值全部为0。其中case_054 P2 N2和case_058 P1 N2各多1次官方评价，总调用数增加2次；其余6条调用数不变。该阶段仅使用seed=2026，不能据此评价多seed稳定性。既有报告还记录到一次非改进解接受，说明发生该接受行为本身并不保证最终结果更好。

以上证据支持将SA-VNS定位为“探索后未采用”：小规模pilot的收益局限于个别任务且存在Added Copy代价，扩展验证在当前范围内未表现出足够稳定的额外收益，同时可能增加官方评价调用。最终stable solver仍采用严格下降VNS，SA-VNS没有进入正式full100算法。这里不推断SA在其他参数、预算或任务上无效。

<!-- Evidence: 本轮只读核对D:/problem_A/problem_A_sa/results/sa_pilot_stage1、sa_pilot_stage2、sa_expansion下control/sa的benchmark.csv（最终vns行）与manifest.json；逐条Makespan、Added Copy及evaluations同各目录report_console.txt一致。Stage 1/Expansion为seed2026，Stage 2为2026/2027/2028。未读取trials.jsonl。SA实现/最终未采用定位来自paper/EVIDENCE_MAP.md I；非改进接受事件取自既有report_console统计。 -->
