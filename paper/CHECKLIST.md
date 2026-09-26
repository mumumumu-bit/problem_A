# 前期基础筹备核查清单

## 一、实验环境

| # | 检查项 | 状态 | 备注 |
|---|--------|:--:|------|
| 1.1 | Python 3.11.9 安装 | ✅ | `which python` → `/d/BAKFILE/python` |
| 1.2 | 虚拟环境 .venv 创建 | ✅ | `source .venv/Scripts/activate` |
| 1.3 | 依赖安装 `pip install -e ".[dev]"` | ✅ | pytest + matplotlib + PyYAML |
| 1.4 | pytest 全部通过 (49 passed) | ✅ | 1.81s |
| 1.5 | 官方 code/ 未修改 | ✅ | 指纹哈希已记录 |
| 1.6 | 官方 data/ 未修改 | ✅ | 100例 + config.txt 原样 |
| 1.7 | 评估缓存可用 | ✅ | `results/evaluation_cache` 跨进程复用 |

## 二、数据素材就绪

| # | 素材 | 路径 | 用途 |
|---|------|------|------|
| 2.1 | 100 例结构审计 | `results/dataset_audit.csv` | 论文§2.2 数据集统计 |
| 2.2 | v2 36组完整结果 | `results/development_v2/` | 论文§5.1 对标 |
| 2.3 | v3 A0 (v2基线) | `results/development_v3/A0_v2_baseline/` | 消融基准 |
| 2.4 | v3 A1 (adaptive) | `results/development_v3/A1_adaptive/` | §5.2.1 |
| 2.5 | v3 A2 (final) 6例 | `results/development_v3/A2_final/` | §5.2.2-5.2.3 |
| 2.6 | v3 A2 P3 (L2) | `results/development_v3/A2_final_p3/` | §5.5 |
| 2.7 | v3 A2 15例扩展 | `results/development_v3/A2_full15/` | §5.4 |
| 2.8 | 邻域效率诊断 | `results/development_v2/neighborhood_diagnostics.json` | §5.3 |
| 2.9 | v2 版本对比 | `results/development_v2/version_comparison.csv` | §5.1 |
| 2.10 | v1 基准报告 | `results/development_v1/REPORT.md` | §4.1 第一轮 |
| 2.11 | v1/v2 figures | `results/development_v*/figures/` | 论文插图备选 |
| 2.12 | single-core 基线 | `results/development_v1/singlecore.csv` | §5.1 加速比 |

## 三、LaTeX 排版环境

| # | 检查项 | 当前 | 下一步 |
|---|--------|:--:|------|
| 3.1 | TeXLive ISO | ✅ E:\ 已解压 | 运行 install-tl-windows.bat |
| 3.2 | 华为杯模板 | ❌ 未获取 | 从竞赛官网/队友获取 |
| 3.3 | xelatex 可运行 | ❌ 未安装 | 安装后 `which xelatex` |
| 3.4 | bibtex 可运行 | ❌ 未安装 | 安装后 `which bibtex` |
| 3.5 | 中文字体 | ⚠️ | Windows 自带宋体/黑体，可能需配置 |
| 3.6 | 模板编译测试 | ❌ | 第一章草稿后执行 |

## 四、实验补跑清单

```bash
# 待执行命令（需要在论文撰写间隙并行跑）

# 1. 生成 v3 报告和图表
python scripts/report_results.py --run-dir results/development_v3/A2_final
python scripts/report_results.py --run-dir results/development_v3/A2_full15
python scripts/report_results.py --run-dir results/development_v3/A2_final_p3
python scripts/plot_results.py --run-dir results/development_v3/A2_final --output results/development_v3/A2_final/figures

# 2. 导出依赖清单
pip freeze > requirements.txt

# 3. 100 例正式实验（每例约 5 分钟 × 100 = ~8小时）
#    建议分批跑，每批 10 例，利用缓存加速
python -m npu_scheduler.cli benchmark \
  --data-dir data --config data/config.txt \
  --solver-config configs/development_v3.yaml \
  --output results/competition \
  --problem 1 2 3 --cores 2 4 \
  --skip-cli-verification

# 4. 官方 CLI 复核
python scripts/benchmark.py \
  --output results/development_v3/A2_final --cli-verify
```

## 五、学术写作工具

| # | 工具 | 用途 | 推荐 |
|---|------|------|:--:|
| 5.1 | Zotero | 文献管理 | ✅ |
| 5.2 | JabRef | BibTeX 编辑 | ✅ |
| 5.3 | MathType / LaTeXiT | 公式编辑 | 可选 |
| 5.4 | Grammarly / Writefull | 英文校对 | 仅英文摘要 |
| 5.5 | draw.io / Inkscape | 流程图/架构图 | ✅ |
| 5.6 | PDF 阅读器 | 审稿 | Adobe Acrobat |

## 六、合规性

| # | 检查项 | 状态 |
|---|--------|:--:|
| 6.1 | AI 辅助声明文件头 | ⚠️ 部分 .py 文件有声明 |
| 6.2 | 官方代码未修改声明 | ✅ |
| 6.3 | 实验可复现性 (seed=2026) | ✅ |
| 6.4 | 数据未篡改 | ✅ |
| 6.5 | 无第三方求解器 | ✅ |
| 6.6 | requirements.txt | ⬜ 待 pip freeze |

---

> 生成日期：2026-09-25