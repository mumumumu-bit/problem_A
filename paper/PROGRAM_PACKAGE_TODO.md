# 程序附件待办（不进入最终PDF）

本清单承接附录A原 PROGRAM-PACKAGE-TODO 和附录D程序代码头模板。仅转移交付工作，不表示程序附件已经验证，不修改stable solver，不运行实验或Evaluator。

1. 最终压缩包名称、目录结构及实际提交文件清单。
2. README：提交用单case命令、问题切换方式、输入输出说明。
3. 安装与激活步骤、运行环境及依赖版本。
4. 单核归档工具是否纳入附件；不得把当前工作树缺失的工具写成可执行命令。
5. dirty工作树与归档源码指纹对应说明；仓库接口说明不能代替最终包交付。
6. 最终包独立环境可用性确认（本轮不执行）。
7. 每个实际AI辅助程序前补充规定声明及对应工具元数据；不以附录D替代代码头，不把当前Codex元数据套到历史solver。原附录D模板如下：

```text
# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具名称：[EXTERNAL-VERIFY-REQUIRED]
# 版本/型号：[EXTERNAL-VERIFY-REQUIRED]
# 开发机构/公司：[EXTERNAL-VERIFY-REQUIRED]
# 版本颁布日期：[EXTERNAL-VERIFY-REQUIRED]
```

`scripts/plot_competition.py:1-2`已有Trae AI Coding Assistant (ByteDance)记录；`src/npu_scheduler/search/vns.py:1-5`等已有声明但工具字段为空。只读查证不等于完成代码头补齐。若PDF实际收入程序代码，该代码前说明随代码进入PDF，并成为PDF冻结项。

输入与后处理记录按附件4第6条及最终提交要求准备。所读A题正文未检出专门要求提交AI输入记录的条款；不能把条件性要求扩大为已确定的PDF必交内容，后续通知及提交界面仍需核对。
