# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""统一图表渲染中枢：字体、颜色、标签辅助、保存。

所有图表生成代码（plots.py / plot_competition.py / 后续新增图表）
均通过本模块完成 matplotlib 配置与输出，禁止各自设置 rcParams 或
重复定义颜色/保存逻辑。
"""
from pathlib import Path
import statistics

# ── 通用颜色（算法维度）────────────────────────────────────────────
COLORS = {
    'baseline': '#9D9DA1', 'multiseed': '#F58518', 'vns': '#4C78A8',
    'no_l2':    '#9D9DA1', 'l2':         '#54A24B',
    'purple':   '#B279A2', 'teal':       '#72B7B2',
}

# ── 竞赛/问题维度颜色 ───────────────────────────────────────────────
PROBLEM_COLORS = {
    'P1':     '#4C78A8', 'P2':     '#F58518',
    'P1_N2':  '#4C78A8', 'P1_N4':  '#72B0E8',
    'P2_N2':  '#F58518', 'P2_N4':  '#F5A838',
}

SCALE_COLORS = {
    'xsmall': '#54A24B', 'small':  '#72B0E8',
    'medium': '#4C78A8', 'large':  '#F58518', 'xlarge': '#E45756',
}

BLUE_GRAD  = ['#1A3A5C', '#2E5A88', '#4C78A8', '#72B0E8', '#A8D0F0']
ORANGE_GRAD = ['#8B4200', '#C45E00', '#F58518', '#F5A838', '#FAC868']

# ── 中文标签 ────────────────────────────────────────────────────────
LABELS = {
    'baseline':   '负载均衡初解',
    'multiseed':  '多初解最佳',
    'vns':        '多初解+VNS',
}

# ── 一次性 matplotlib 配置 ──────────────────────────────────────────
def apply_style():
    """初始化 matplotlib（Agg 后端 + 中文字体），返回 plt 模块。"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    try:
        import scienceplots  # noqa: F401
        plt.style.use(['science', 'no-latex'])
    except ImportError:
        pass

    available = {f.name for f in font_manager.fontManager.ttflist}
    cjk_fonts = ['SimHei', 'Microsoft YaHei', 'Noto Sans SC',
                 'SimSun', 'DejaVu Sans']
    fonts = [f for f in cjk_fonts if f in available]

    plt.rcParams.update({
        'figure.figsize':       (6.4, 4.0),
        'figure.dpi':           120,
        'savefig.dpi':          300,
        'font.family':          'sans-serif',
        'font.sans-serif':      fonts or ['sans-serif'],
        'axes.unicode_minus':   False,
        'font.size':            10,
        'axes.labelsize':       11,
        'axes.spines.top':      False,
        'axes.spines.right':    False,
        'axes.grid':            True,
        'grid.alpha':           .2,
        'grid.linewidth':       .5,
        'grid.color':           '#9D9DA1',
        'lines.linewidth':      1.9,
        'lines.markersize':     5,
        'legend.frameon':       False,
        'figure.facecolor':     'white',
        'axes.facecolor':       'white',
        'pdf.fonttype':         42,
        'ps.fonttype':          42,
    })
    return plt


# ── 统一保存 ────────────────────────────────────────────────────────
def save(fig, directory, name):
    """同时输出 png（300 dpi）和 pdf 到 directory/figures/。"""
    directory = Path(directory)
    if directory.name != 'figures':
        directory = directory / 'figures'
    directory.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(directory / f'{name}.png', dpi=300, bbox_inches='tight')
    fig.savefig(directory / f'{name}.pdf', bbox_inches='tight')


# ── 柱状图数值标签 ──────────────────────────────────────────────────
def label_bars(ax, bars, fmt='{:.1f}%', offset=1.0, colors=None, **text_kw):
    """在垂直柱状图顶部居中标注数值。

    Args:
        ax:        matplotlib Axes
        bars:      ax.bar() 返回的 BarContainer
        fmt:       数值格式化字符串
        offset:    标签与柱顶的垂直偏移量（坐标单位）
        colors:    可选的 per-bar 颜色列表；为 None 则使用柱自身的颜色
        text_kw:   传给 ax.text 的额外参数
    """
    defaults = dict(ha='center', va='bottom', fontsize=9, fontweight='bold')
    defaults.update(text_kw)
    for i, bar in enumerate(bars):
        h = bar.get_height()
        if colors and i < len(colors):
            defaults['color'] = colors[i]
        ax.text(bar.get_x() + bar.get_width() / 2, h + offset,
                fmt.format(h), **defaults)


def label_hbars(ax, bars, fmt='{:.1f}%', offset=0.5, colors=None, **text_kw):
    """在水平柱状图右侧标注数值。

    Args:
        ax:        matplotlib Axes
        bars:      ax.barh() 返回的 BarContainer
        fmt:       数值格式化字符串
        offset:    标签与柱右端的水平偏移量
        colors:    可选的 per-bar 颜色列表；为 None 则使用柱自身的颜色
        text_kw:   传给 ax.text 的额外参数
    """
    defaults = dict(va='center', fontsize=8, fontweight='bold')
    defaults.update(text_kw)
    for i, bar in enumerate(bars):
        w = bar.get_width()
        if colors and i < len(colors):
            defaults['color'] = colors[i]
        ax.text(w + offset, bar.get_y() + bar.get_height() / 2,
                fmt.format(w), **defaults)


# ── 统计参考线 ──────────────────────────────────────────────────────
def stat_vlines(ax, data, color_mean='#E45756', color_median='#54A24B',
                label_fmt_mean='均值 = {:.1f}%',
                label_fmt_median='中位数 = {:.1f}%'):
    """在图表上添加垂直的均值（虚线）和中位数（点线）参考线。

    Args:
        ax:            matplotlib Axes
        data:          数值列表
        color_mean:    均值线颜色
        color_median:  中位数线颜色
        label_fmt_mean / label_fmt_median: 图例格式字符串
    """
    m = statistics.mean(data)
    med = statistics.median(data)
    ax.axvline(m, color=color_mean, linestyle='--', linewidth=1.5,
               label=label_fmt_mean.format(m))
    ax.axvline(med, color=color_median, linestyle=':', linewidth=1.5,
               label=label_fmt_median.format(med))