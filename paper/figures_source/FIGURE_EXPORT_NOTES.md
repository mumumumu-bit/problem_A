# 正式框架图导出说明

- 来源：FRAMEWORK_SPECS.md、framework_A.mmd、framework_B.mmd、framework_D.mmd；原文件保留未修改。
- 输出：paper/figures/framework_{A,B,D}.svg 与同名 PNG。
- 白底、深蓝边框、浅蓝普通模块、浅灰评价模块、少量青色强调；统一微软雅黑。
- SVG 中文文字已转为矢量轮廓，不依赖接收电脑字体。PNG 为 3600 像素宽、350 dpi 白底图。
- 建议在 Word 横向页面以约 26 cm 宽度插入，最小字约 9 pt；纵向正文页面需按最终版心检查可读性，避免直接缩小至半栏。
- 复现：在仓库根目录执行 `pwsh -NoProfile -File paper/figures_source/export_frameworks.ps1`。
- 图中文字以中文说明为主，保留规格要求的技术标识；Makespan / Added Copy 分别用“完工时间 / 新增拷贝量”表示。

## 规格与草图的差异处理

无实质技术冲突。A 草图省略“未评价”限定；D 草图省略固定容量及后续请求状态回路。正式版本依据规格补齐，未引入额外机制。

## 工作区事项

- 请从仓库根目录运行导出脚本。
- `paper/figures/` 为正式框架图输出目录。
- 导出脚本不会修改正文、实验结果或算法代码。

## 待人工微调

无待确认的技术细节。插入 Word 后按最终页面尺寸确认字号、图号与图题。
