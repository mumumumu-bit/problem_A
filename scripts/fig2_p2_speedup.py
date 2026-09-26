# coding=utf-8
"""图2:P2多核加速比"""
import csv, statistics; from pathlib import Path
import matplotlib.pyplot as plt
import _cn_font as S

ROOT = Path(__file__).resolve().parents[1]
dr = list(csv.DictReader(open(ROOT/"results/full100_merged/detail.csv",encoding="utf-8")))
sr = list(csv.DictReader(open(ROOT/"results/singlecore_full100/singlecore.csv",encoding="utf-8")))
sc = {r["case"]:int(r["makespan"]) for r in sr}
dk = {(r["case"],int(r["problem"]),int(r["cores"]),r["algorithm"]):r for r in dr}
cs = sorted(sc.keys()); CC=[1,2,3,4,5]

LINECOLOR = "#8E0000"
ANNCOLOR  = "#5C0000"
IDECOLOR  = "#B8860B"

def sp(p):
    m,s=[],[]
    for N in CC:
        v=[1.0]*100 if N==1 else [sc[c]/int(dk[(c,p,N,"vns")]["makespan"]) for c in cs]
        m.append(statistics.mean(v)); s.append(statistics.stdev(v) if len(v)>1 else 0)
    return m,s

fig,ax=S.new_figure((12,6))
m2,s2=sp(2)
ax.errorbar(CC,m2,yerr=s2,marker="s",capsize=4,linewidth=3,markersize=9,
            color=LINECOLOR,label="P2(场景B)",zorder=3)
ax.plot(CC,CC,"--",color=IDECOLOR,alpha=0.9,linewidth=2.2,label="理想线性$y=N$")

offsets = [(12,-12),(12,10),(12,10),(12,10),(12,10)]
for i,(x,y) in enumerate(zip(CC,m2)):
    ax.annotate(f"{y:.3f}",(x,y),textcoords="offset points",xytext=offsets[i],
                ha="left",va="bottom",fontsize=14,color=ANNCOLOR,fontweight="bold")

ax.text(0.98,0.03,"误差棒:±1 标准差($N$=100)",transform=ax.transAxes,
        fontsize=11,color="#1a1a1a",ha="right",va="bottom")

ax.set_xlabel("处理器核数$N$",fontsize=16,labelpad=6)
ax.set_ylabel("平均加速比(相对于单核)",fontsize=16,labelpad=4)
S.style_legend(ax,loc="upper left")
ax.set_xticks(CC); ax.set_xlim(0.7,5.3)
data_min, data_max = min(m2), max(m2)
ax.set_ylim(bottom=data_min-0.3, top=data_max+max(s2)+0.3)
ax.margins(x=0.01)
from matplotlib.ticker import ScalarFormatter
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
ax.yaxis.set_major_locator(plt.MaxNLocator(6))
ax.tick_params(axis="y",labelsize=14)
ax.tick_params(axis="x",labelsize=14)
ax.grid(True,alpha=0.2,linewidth=0.5)
fig.suptitle("图2:P2多核加速比曲线(100个测试用例)",fontsize=22,fontweight="bold",x=0.5,y=0.03,ha="center")
fig.tight_layout(rect=[0,0.06,1,1],pad=0.5)
O=ROOT/"results/final_visualization/figures"; O.mkdir(parents=True,exist_ok=True)
for f in["pdf","png","svg"]: fig.savefig(O/f"fig2_p2_speedup.{f}",dpi=600,bbox_inches="tight",pad_inches=0.1)
print("图2 OK"); plt.close()





