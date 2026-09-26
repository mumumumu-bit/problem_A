# 技术框架图规格

本文件只规定三张正文技术图的内容和结构。Mermaid 文件是结构草图；不得据此增加第4、5章和 Evidence Map 未确认的机制。图中的数值仅保留与正式求解流程绑定的候选池/Top-K配置，以及已正式启用的grain候选设置；其他实验预算留在实验设置章节。

## Framework A：整体求解框架

1. **图目的**：呈现从计算图、硬件和问题场景输入，经统一求解器产生候选与改进方案，再交给对应官方 Evaluator 得到正式结果的全文主线。
2. **推荐画布方向**：横向；从左至右布局，Evaluator结果在右侧分成P1/P2/P3三个并列出口。
3. **所有节点**：
   - 输入：计算图 $G$、硬件配置、问题场景（P1/P2/P3）。
   - 图特征预计算。
   - Baseline：中间grain的balanced粗化与HEFT-style核分配；作为seed阶段先评价的基线候选，不画成与Multi-seed并列的独立算法。
   - Multi-seed候选生成：balanced、affinity、critical、pipe四类family；主grains 4/12/32，fine-grain=2作为候选变体注记，whole候选可作为可选结构候选注记。
   - HEFT-style核分配。
   - Multi-seed候选逐个调用官方Evaluator并按正式目标比较，形成seed阶段incumbent。
   - VNS：邻域候选生成；候选池（最多48个合法、唯一、未评价候选）→启发式排序→Top-K（最多3个）→官方Evaluator。
   - 严格下降比较与best-so-far更新；adaptive邻域选择/停止（作为搜索控制，不标注独立贡献）。
   - 统一求解流程按P1/P2/P3分别运行，各自得到最终调度方案并进入对应官方评价。
4. **所有箭头**：输入→图特征预计算；预计算→Baseline候选；预计算→Multi-seed生成；Baseline候选→核分配→seed官方评价；Multi-seed生成→核分配→seed官方评价；seed官方评价→incumbent；incumbent→VNS；VNS候选生成→候选池→启发式排序→Top-K→官方Evaluator→严格目标比较；严格改善→更新incumbent，未改善→保持incumbent；比较与adaptive控制→继续VNS或停止；停止→按场景分别输出最终调度方案→对应P1/P2/P3官方评价结果。
5. **分组/泳道**：输入与场景；统一求解器（图特征、seed阶段、VNS阶段）；官方评价与输出。VNS内部循环可用虚线框表示。
6. **图中必须出现的文字**：“Baseline（seed阶段起始候选）”“Multi-seed四类候选”“fine-grain=2（候选变体）”“HEFT-style核分配”“seed候选逐个官方评价”“VNS候选池→启发式排序→Top-K→官方Evaluator”“严格下降”“best-so-far”“统一流程按P1/P2/P3分别运行并评价”。候选池48、Top-K=3可作为当前正式配置注记；不要将其套用于seed阶段。
7. **图中禁止出现的文字**：SA、GA、Tabu、CP-SAT；“fine-grain独立阶段/贡献”；“Cache Hit Rate优化目标”；“global optimum/全局最优”；“Cache-aware partition”；任何把Cache容量画成solver决策变量的文字；未经Evidence Map绑定的实验数字和硬件模块。
8. **推荐caption**：图X 统一求解框架：Multi-seed候选经官方评价形成当前解，VNS仅对邻域候选进行池化、排序和Top-K评价，最终方案按问题场景交由相应官方Evaluator评价。
9. **对应正文位置**：第2章总体求解思路或第5章5.1；正文仅放一处完整图。
10. **Evidence来源**：`paper/EVIDENCE_MAP.md` 的A（场景及Evaluator）、B（正式目标）、C（正式流水线、Baseline、四类seed、fine-grain、VNS排序与接受准则、adaptive）、D（正式候选池/Top-K配置）；`paper/sections/04_model.md` 4.2、4.4、4.5；`paper/sections/05_algorithm.md` 5.1、5.3、5.5、5.7。

## Framework B：Multi-seed + VNS内部流程

1. **图目的**：明确seed阶段与VNS阶段的真实差别，尤其展示seed候选直接逐个官方评价，而48候选池与Top-K=3只用于VNS邻域候选。
2. **推荐画布方向**：横向双泳道；上方Seed阶段，下方/右侧VNS阶段；8邻域用侧栏或小型列表，不进入主流程主体。
3. **所有节点**：
   - 输入：图特征、场景与核数、求解配置接口（不展开预算数值）。
   - Seed阶段：Baseline候选；四类family及多grain候选生成（fine-grain=2作为候选来源注记）；HEFT-style核分配；digest去重；逐个官方Evaluator；$(Makespan, Added Copy)$严格目标比较；incumbent/best-so-far。
   - 阶段连接：seed阶段incumbent作为VNS当前解。
   - VNS阶段：选择邻域；最多48个合法、唯一、未评价候选；启发式估计与排序；Top-K=3；官方Evaluator；是否严格改善；更新或保持incumbent；更新邻域统计；adaptive选择与停止判断；继续下一轮或输出。
   - 8邻域侧栏：N1重块优先换核；N2两块核归属交换；N3相邻无直接依赖块重排；N4相邻块合并；N5按工作量近半拆分；N6边界节点右移；N7高通信量连接块对优先同核；N8关键块优先换核。
4. **所有箭头**：输入→Baseline与seed生成；seed生成→核分配→digest去重→官方Evaluator逐个评价→严格目标比较→incumbent；incumbent→邻域选择→候选生成→启发式排序→Top-K→官方Evaluator→严格改善判断；改善→更新incumbent并更新邻域统计；不改善→保持incumbent并更新邻域统计；两分支→adaptive选择/停止判断；继续→邻域选择，停止→输出best-so-far。
5. **分组/泳道**：Seed阶段；VNS阶段；右侧窄栏为8邻域动作。Seed与VNS官方评价框可以复用同一视觉样式，但标签须分别标明“逐个评价”和“Top-K评价”。
6. **图中必须出现的文字**：“Seed阶段：Baseline + 四类Multi-seed family”“digest去重”“seed候选逐个官方评价”“VNS阶段”“最多48个合法、唯一、未评价候选”“启发式排序”“Top-K=3”“严格改善：$(Makespan, Added Copy)$”“接受/更新或保持当前best-so-far”“adaptive选择/停止”“达到停止条件则输出best-so-far”。
7. **图中禁止出现的文字**：“Seed阶段candidate_pool=48→Top-K=3”；“劣解接受”；“SA”；“global optimum”；fine-grain=2独立阶段；adaptive独立消融贡献；把内部启发式分数标成Makespan。
8. **推荐caption**：图X Multi-seed与VNS的两阶段搜索流程。Multi-seed候选在预算允许时逐个进行官方评价；候选池与Top-K筛选用于VNS邻域候选，最终更新依据官方字典序目标的严格改善。
9. **对应正文位置**：第5章5.1，作为Algorithm 1的流程图对应图；避免重复绘制Framework A全局主线。
10. **Evidence来源**：`paper/EVIDENCE_MAP.md` C、D；`paper/sections/05_algorithm.md` 5.1、5.3、5.5、5.6、5.7及Algorithm 1。

## Framework D：P3只读FIFO Cache访问机制

1. **图目的**：展示P3相对P2执行模型新增的只读FIFO Cache读取路径，区分Cache查询、命中路径和DDR未命中路径。
2. **推荐画布方向**：横向数据路径；计算核/COPY事件在左，Cache与DDR在中部，评价输出在右；FIFO状态更新在Cache框下方。
3. **所有节点**：
   - P2基础执行路径提示：按核Task及跨核COPY_IN/COPY_OUT由官方执行规则构造（简洁标注，不展开成solver模块）。
   - 计算核/发起端。
   - COPY_IN读取请求。
   - 只读FIFO Cache查询及命中/未命中判断。
   - 命中：Cache读取路径及对应Cache带宽。
   - 未命中：DDR读取路径；读取完成后按FIFO规则更新Cache；若容量不足则FIFO淘汰。
   - 命中不刷新FIFO顺序的注释。
   - 官方Evaluator结果：Makespan、Added Copy、Cache Hit Rate（评价指标；不是优化目标）。
4. **所有箭头**：计算核/执行端→COPY_IN读取请求→Cache查询；命中→Cache读取路径→读取完成；未命中→DDR读取→读取完成→FIFO Cache写入/状态更新→（容量不足时）FIFO淘汰→后续请求状态；读取/执行事件→官方Evaluator→结果字段。只将COPY_IN连接到Cache查询。COPY_OUT只作为P2基础场景标识，不连入Cache查询。
5. **分组/泳道**：P2基础执行语义（窄标题带）；P3只读Cache读取路径；DDR；官方Evaluator输出。Cache容量作为固定硬件参数注释放在Cache框旁，不画为决策节点。
6. **图中必须出现的文字**：“仅COPY_IN查询Cache”“只读FIFO Cache”“命中→Cache读取带宽”“未命中→DDR读取”“读取完成后按FIFO规则更新”“容量不足时FIFO淘汰”“命中不刷新FIFO顺序”“Cache Hit Rate为评价指标，非优化目标”“Cache容量由正式配置给定”。
7. **图中禁止出现的文字**：“可写Cache”“写回”“命中刷新/LRU/LFU”“预取”“solver主动替换/优化Cache容量”“Cache-aware partition”“所有访问均可命中”“cache_weight启用Cache机制”。可在图注或规格中说明正式solver的`cache_weight=0`；不建议将代码变量名放入图面。
8. **推荐caption**：图X P3只读FIFO Cache访问路径。仅COPY_IN请求查询Cache；命中走Cache读取路径，未命中从DDR读取并在读取完成后按FIFO规则更新状态，Cache命中率由官方Evaluator统计。
9. **对应正文位置**：第4章4.2.3（机制定义）；第9章P3结果部分可引用，不重复画机制图。
10. **Evidence来源**：`paper/EVIDENCE_MAP.md` A（P3相对P2增加、Cache容量/带宽、COPY机制）、B（Cache Hit Rate指标与非优化目标）、D（正式solver cache_weight=0）；`paper/sections/04_model.md` 4.2.2、4.2.3、4.4.3、4.5；`paper/sections/05_algorithm.md` 5.4.3。

## 绘图前风险核对

- Framework A、B中Baseline先作为seed阶段起始候选表示；不能画成与整个Multi-seed阶段平行的独立优化器。
- Seed候选评价与VNS Top-K评价是不同路径，只有后者经过48候选池和Top-K=3。
- Framework D不把场景规则误画成solver主动控制，也不暗示Cache命中率参与正式字典序目标。
- 最终美化时可以用颜色区分场景和执行路径，但颜色不得引入新的语义或因果解释。
