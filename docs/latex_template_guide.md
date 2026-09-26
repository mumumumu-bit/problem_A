# LaTeX 论文模板使用指引

## 一、模板发现状态

**已找到完整模板**，位于 `gmcmthesis/` 目录。

| 文件 | 说明 |
|------|------|
| `gmcmthesis.cls` | 文档类（基于 ctexart，v2.3, 2018/09/11） |
| `gmcm.bst` | 参考文献格式（GB/T 7714 风格） |
| `example.tex` | 示例文档（编译通过可验证） |
| `example.pdf` | 编译后的示例 PDF |
| `example.bib` | 示例参考文献 |
| `logo.png` / `title.png` | 封面标识图片 |
| `gongzhonghao.png` | 公众号推广图（需替换） |

**来源**：`latexstudio.net` 发布的 GMCMthesis（全国研究生数学建模竞赛 / 华为杯专用模板）。

---

## 二、模板适用场景

| 场景 | 匹配度 |
|------|:--:|
| "华为杯" 中国研究生数学建模竞赛 | ⭐⭐⭐⭐⭐ 专用模板 |
| 全国研究生数学建模竞赛 (GMCM) | ⭐⭐⭐⭐⭐ 完全匹配 |
| 中文数学建模论文 | ⭐⭐⭐⭐⭐ |
| 中文毕业论文（工科） | ⭐⭐⭐ 需微调 |
| 英文论文 (IEEE/ACM) | ⭐ 不适用 |

---

## 三、编译要求

### 3.1 编译器
- **必须使用 `xelatex`**（不支持 pdflatex/latex）
- 模板代码中明确检测：`\RequireXeTeX`，强制要求 XeLaTeX 引擎

### 3.2 依赖宏包
自动引入：
- `geometry` — 页面布局 (top=30mm, bottom=25mm, left=22.5mm, right=22.5mm)
- `amsmath/amssymb/bm` — 数学公式
- `graphicx` — 图片插入
- `booktabs/multirow/longtable` — 表格增强
- `natbib[numbers]` — 参考文献（数字编号）
- `hyperref` — 超链接
- `listings` — 代码排版
- `caption` — 图表标题
- `ctexart` — 中文支持（基础类）

### 3.3 字体要求
| 平台 | 中文字体 | 英文字体 |
|------|----------|----------|
| **Windows** ✅ | SimSun(宋体) / SimHei(黑体) / KaiTi(楷体) | Times New Roman |
| macOS | Songti SC / Heiti SC / Kaiti SC | Times New Roman |
| Linux (Fandol) | Fandol 字体族 | texgyretermes |

本项目在 **Windows 10** 上运行，字体均已系统自带，无需额外安装。

### 3.4 编译命令
```bash
xelatex main.tex    # 第一次编译 → 生成 .aux
bibtex main          # 处理参考文献
xelatex main.tex    # 第二次 → 写入引用
xelatex main.tex    # 第三次 → 交叉引用全部正确
```

或一键：
```bash
xelatex main.tex && bibtex main && xelatex main.tex && xelatex main.tex
```

---

## 四、格式配置说明

### 4.1 文档类选项
```latex
\documentclass[bwprint]{gmcmthesis}   % 黑白打印（推荐提交用）
\documentclass[colorprint]{gmcmthesis} % 彩色（默认）
\documentclass[withoutpreface]{gmcmthesis} % 无承诺书页
```

### 4.2 封面信息
```latex
\title{面向多核NPU的DAG划分与自适应变邻域搜索调度}
\baominghao{你的参赛队号}
\schoolname{你的学校名称}
\membera{队员1姓名}
\memberb{队员2姓名}
\memberc{队员3姓名}
```

### 4.3 摘要与关键词
```latex
\begin{abstract}
摘要正文内容...
\keywords{关键词1；关键词2；关键词3}
\end{abstract}
```

### 4.4 章节结构
```
\section{一级标题}       → 1. 居中小四黑体
\subsection{二级标题}    → 1.1 左对齐加粗
\subsubsection{三级标题} → 1.1.1 左对齐加粗
```

### 4.5 参考文献
两种方式：

**方式一（推荐）：BibTeX 自动管理**
```latex
\bibliographystyle{gmcm}     % 使用模板自带的 .bst
\bibliography{references}    % 引用 paper/references.bib
```
**方式二：手工录入**
```latex
\begin{thebibliography}{9}
\bibitem{ref1} 作者. 标题[J]. 期刊, 年份.
\end{thebibliography}
```

### 4.6 图片插入
```latex
\begin{figure}[!h]
\centering
\includegraphics[width=0.8\textwidth]{../results/development_v3/figures/p1_speedup.pdf}
\caption{问题1加速比}
\end{figure}
```
模板默认从 `figures/`, `figure/`, `pictures/`, `image/` 等子目录搜索图片。

### 4.7 代码排版
```latex
\begin{lstlisting}[language=Python]
import numpy as np
def schedule(dag):
    ...
\end{lstlisting}
```

### 4.8 页面布局
```
纸张: A4
上边距: 30mm, 下边距: 25mm
左边距: 22.5mm, 右边距: 22.5mm
正文行距: 1.38 倍
首行缩进: 2 个汉字
```

---

## 五、适配本项目后的文件结构建议

```
paper/
├── main.tex              # 主文档（新建）
├── gmcmthesis.cls        # 从 ../gmcmthesis/ 复制
├── gmcm.bst              # 从 ../gmcmthesis/ 复制
├── logo.png              # 从 ../gmcmthesis/ 复制
├── title.png             # 从 ../gmcmthesis/ 复制
├── references.bib        # 已创建（15条种子）
├── figures/              # 论文用图（从 results/ 复制或软链接）
├── outline.md            # 已创建
├── SCHEDULE.md           # 已创建
└── CHECKLIST.md          # 已创建
```

### 快速搭建命令
```bash
cd /d/BAKFILE/9017530/huawei_cup_2026/problem_A/paper
cp ../gmcmthesis/gmcmthesis.cls .
cp ../gmcmthesis/gmcm.bst .
cp ../gmcmthesis/logo.png ../gmcmthesis/title.png .
mkdir -p figures
# 链接实验图表（选最新的）
cp ../results/development_v1/figures/*.pdf figures/
```

### main.tex 最小可编译模板
```latex
% !TEX program = xelatex
\documentclass[bwprint]{gmcmthesis}

\title{面向多核NPU的DAG划分与自适应变邻域搜索调度}
\baominghao{4321}
\schoolname{XX大学}
\membera{张三}
\memberb{李四}
\memberc{王五}

\begin{document}
\maketitle

\begin{abstract}
本文针对多核神经网络处理器（NPU）上的AI计算图（DAG）调度问题...
\keywords{多核调度；DAG划分；变邻域搜索；NPU}
\end{abstract}

\section{问题重述}
\subsection{问题背景}
...

\section{模型的假设}
\begin{itemize}
\item NPU核心为同构架构，各核心计算能力相同；
\item 官方评估器为黑箱，仅提供最终makespan和added_copy_bytes。
\end{itemize}

\section{符号说明}
\begin{tabular}{cc}\hline
符号 & 意义 \\\hline
G=(V,E) & DAG计算图 \\\hline
N & 核心数 \\\hline
\end{tabular}

\bibliographystyle{gmcm}
\bibliography{references}

\newpage
\appendix
\section{逐例实验结果}
% 引用 benchmark_table.tex
\input{../results/development_v3/A2_final/benchmark_table.tex}

\end{document}
```

---

## 六、推荐的其他 LaTeX 模板来源

如需备选模板（例如换期刊投稿），以下为推荐来源：

| 来源 | 适用场景 | 链接 |
|------|----------|------|
| **latexstudio.net** | 中文建模竞赛/毕业论文 | http://www.latexstudio.net |
| **Overleaf 模板库** | IEEE/ACM/Springer 期刊 | https://www.overleaf.com/latex/templates |
| **CTAN** | 所有标准宏包 | https://ctan.org |
| **GitHub: latexstudio/GMCMthesis** | GMCM 最新版 | https://github.com/latexstudio/GMCMthesis |

---

## 七、常见问题

| 问题 | 解决 |
|------|------|
| `! LaTeX Error: File 'gmcmthesis.cls' not found` | 复制 `.cls` 到 `paper/` 目录 |
| `! Font ... not found` | 确保用 `xelatex`（不用 `pdflatex`） |
| 中文不显示 | 文件编码必须为 UTF-8 |
| 参考文献 [?] | 先跑 `bibtex main` 再编译两次 |
| `过度hbox` 警告 | 可忽略（长代码/URL引起） |

---

> 生成日期：2026-09-25
> 配套模板：gmcmthesis v2.3 (latexstudio.net)