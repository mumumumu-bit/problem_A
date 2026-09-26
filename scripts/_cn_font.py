# coding=utf-8
"""Icarus-Figures 中文论文图表全局样式 — 精确对齐版"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── 字体 ──
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.unicode_minus"] = False

# ── 字号 ──
plt.rcParams["font.size"] = 10              # 基准
plt.rcParams["axes.titlesize"] = 12        # 子图标题 12pt bold
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 10        # 坐标轴标题
plt.rcParams["xtick.labelsize"] = 9        # 刻度
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 13       # 图例
plt.rcParams["figure.titlesize"] = 14
plt.rcParams["figure.titleweight"] = "bold"

# ── 线条 ──
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["lines.linewidth"] = 1.5
plt.rcParams["lines.markersize"] = 6
plt.rcParams["xtick.major.width"] = 0.8
plt.rcParams["ytick.major.width"] = 0.8

# ── 对齐 & 边距 ──
plt.rcParams["axes.titlepad"] = 8
plt.rcParams["axes.labelpad"] = 4
plt.rcParams["xtick.major.pad"] = 3
plt.rcParams["ytick.major.pad"] = 3
plt.rcParams["legend.borderpad"] = 0.4
plt.rcParams["legend.handletextpad"] = 0.6
plt.rcParams["legend.labelspacing"] = 0.3
plt.rcParams["legend.columnspacing"] = 0.8
plt.rcParams["legend.handlelength"] = 1.2

# ── 输出 ──
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["savefig.pad_inches"] = 0.08

# ── 配色 ──
PALETTE = {
    "blue":    "#0072B2",
    "red":     "#D55E00",
    "green":   "#009E73",
    "orange":  "#E69F00",
    "purple":  "#CC79A7",
    "cyan":    "#56B4E9",
    "gray":    "#999999",
    "darkgray": "#555555",
    "lightgray":"#CCCCCC",
}


def new_figure(figsize=(5.5, 4)):
    """创建统一排版的学术风格图表"""
    fig, ax = plt.subplots(figsize=figsize)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
    ax.tick_params(width=0.8)
    return fig, ax


def annotate_value(ax, x, y, text, color="#333333", offset=(0, 8), fontsize=8):
    """统一的数据标注：等距、等大、不遮挡"""
    ax.annotate(text, (x, y),
                textcoords="offset points", xytext=offset,
                ha="center", va="bottom",
                fontsize=fontsize, color=color)


def style_legend(ax, **kwargs):
    """统一图例样式"""
    defaults = dict(loc="upper left", framealpha=0.85,
                    edgecolor=PALETTE["lightgray"], borderaxespad=0.5)
    defaults.update(kwargs)
    leg = ax.legend(**defaults)
    leg.get_frame().set_linewidth(0.5)
    return leg


def footnote(ax, text, x=0.02, y=0.02):
    """统一脚注/备注：左对齐、固定边距"""
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=7.5, color=PALETTE["darkgray"],
            ha="left", va="bottom",
            linespacing=1.3)