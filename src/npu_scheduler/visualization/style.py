# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Stable scientific colors, portable font fallback and vector exports."""
from pathlib import Path

COLORS={'baseline':'#9D9DA1','multiseed':'#F58518','vns':'#4C78A8',
        'no_l2':'#9D9DA1','l2':'#54A24B','purple':'#B279A2','teal':'#72B7B2'}
LABELS={'baseline':'Load-balanced','multiseed':'Multi-seed','vns':'Multi-seed + VNS'}


def apply_style():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    try:
        import scienceplots  # noqa: F401
        plt.style.use(['science','no-latex'])
    except ImportError:
        pass
    available={f.name for f in font_manager.fontManager.ttflist}
    fonts=[f for f in ('Times New Roman','DejaVu Serif','SimSun','Noto Serif CJK SC','Microsoft YaHei','Source Han Serif SC') if f in available]
    plt.rcParams.update({'figure.figsize':(6.4,4.0),'figure.dpi':120,'savefig.dpi':300,
        'font.family':fonts or ['serif'],'font.size':10,'axes.labelsize':11,
        'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,
        'grid.alpha':.2,'grid.linewidth':.5,'grid.color':'#9D9DA1',
        'lines.linewidth':1.9,'lines.markersize':5,'legend.frameon':False,
        'figure.facecolor':'white','axes.facecolor':'white','pdf.fonttype':42,'ps.fonttype':42})
    return plt


def save(fig,directory,name):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    fig.tight_layout()
    fig.savefig(directory/(name+'.png'),dpi=300,bbox_inches='tight')
    fig.savefig(directory/(name+'.pdf'),bbox_inches='tight')
