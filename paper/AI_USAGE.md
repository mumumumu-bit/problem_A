# AI使用记录

本表只记录团队实际使用过的AI工具，不照抄网上示例，不猜测模型版本或发布日期。无法确认的元数据填写`[EXTERNAL-VERIFY-REQUIRED]`。

## 已有证据支持的使用事实

本表是内部记录，不把当前工具或模型推定为历史全部使用记录。未知元数据统一标为`[EXTERNAL-VERIFY-REQUIRED]`，待团队核验的实际采用范围标为`[VERIFY-BEFORE-PDF]`。未登记的日期和人工签认不声明为已完成。

| 使用记录/证据 | 工具名称 | 版本/型号 | 开发机构/公司 | 版本颁布日期 | 使用环节 | 论文写作 | 数据分析 | 辅助编程 |
|---|---|---|---|---|---|---|---|---|
| 附录D.1/D.2既有记录 | Codex | [EXTERNAL-VERIFY-REQUIRED] | OpenAI | [EXTERNAL-VERIFY-REQUIRED] | 仓库阅读、接口核对、归档字段整理、统计一致性检查、附录文字与目录整理 | 是（附录文字） | 是（归档整理与核对；未重新实验） | 本轮未改solver；整理脚本采用范围[VERIFY-BEFORE-PDF] |
| scripts/plot_competition.py:1—2 | Trae AI Coding Assistant | [EXTERNAL-VERIFY-REQUIRED] | ByteDance（代码头记载） | [EXTERNAL-VERIFY-REQUIRED] | 历史图表程序辅助；是否用于正式图[VERIFY-BEFORE-PDF] | 未有证据确认 | 脚本含统计/绘图，但实际分析输出采用范围[VERIFY-BEFORE-PDF] | 是（代码头声明） |
| src/npu_scheduler/search/vns.py:1—5及其他源码声明 | [EXTERNAL-VERIFY-REQUIRED] | [EXTERNAL-VERIFY-REQUIRED] | [EXTERNAL-VERIFY-REQUIRED] | [EXTERNAL-VERIFY-REQUIRED] | 历史solver及其他分析程序辅助 | [VERIFY-BEFORE-PDF] | [VERIFY-BEFORE-PDF] | 是（源码声明；具体采用范围待核验） |
| 当前PDF前审计会话（2026-09-27） | Codex | GPT-6家族（环境说明）；精确型号/工具版本[EXTERNAL-VERIFY-REQUIRED] | OpenAI | [EXTERNAL-VERIFY-REQUIRED] | 文件扫描、合规分类、占位转移及清单整理 | 是（仅AI披露及内部审计文字） | 本轮未新增实验结果分析 | 本轮未修改程序源码 |

### 需要外部核验的AI元数据

- Codex历史附录/数据整理会话的实际版本或模型、相应版本颁布日期；本轮精确型号/工具版本及发布日期。
- Trae实际使用的版本或模型、对应版本颁布日期；不得根据工具名推定底层模型。
- 历史solver及其他程序的工具名称、版本或模型、开发机构、版本颁布日期。
- 上述未知字段均为[EXTERNAL-VERIFY-REQUIRED]。历史用途、采用内容和团队理解/修改/签认由真实使用记录另行补证，不以当前环境代填。

## 使用规则

- 后续每新增一次重要AI辅助用途，都应补充一行，并由团队人工核验。
- 最终呈现在论文中的文字必须经过团队理解、核验和重新组织，不能把AI输出直接作为未经修改的最终论文内容。
- AI辅助数据分析时，在数据分析结果的前导或后面添加注释，写明参考输出来自AI工具，并注明名称、版本/型号、开发机构/公司、版本颁布日期。
- AI辅助编程时，在程序前添加规定说明，并注明名称、版本/型号、开发机构/公司、版本颁布日期。
- AI生成且无法确认来源的模型或公式不得无推导、无引用标识地直接使用；如选择标注使用，按附件4要求在参考文献中列出工具字段，并接受其可能不被评阅认可的风险。
- 若赛题要求，保留AI输入内容及输出后处理策略，包括算法组合采用的开发框架、开源软件、技术路线、假设条件、参数和超参数等。

## 官方依据

以上规则对应附件4第1-7条；“只记录实际使用”“不猜测版本/发布日期”是本团队记录控制要求，不是附件4新增的官方条款。
