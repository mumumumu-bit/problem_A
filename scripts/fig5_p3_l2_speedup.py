# coding=utf-8
"""图5:P3 L2Cache加速比"""
import csv, statistics; from pathlib import Path
import matplotlib.pyplot as plt
import _cn_font as S

ROOT = Path(__file__).resolve().parents[1]
dr = list(csv.DictReader(open(ROOT/"results/full100_merged/detail.csv",encoding="utf-8")))
p3 = list(csv.DictReader(open(ROOT/"results/p3_singlecore_full100/p3_n1_l2.csv",encoding="utf-8")))
dk = {(r["case"],int(r["problem"]),int(r["cores"]),r["algorithm"]):r for r in dr}
cs = sorted(set(r["case"] for r in p3)); CC=[1,2,3,4,5]

LINECOLOR = "#1B5E20"
ANNCOLOR  = "#0D3B0F"
IDECOLOR  = "#B8860B"

m,s=[],[]
for N in CC:
    if N==1: sp=[float(r["l2_speedup"]) for r in p3]
    else:
        sp=[]
        for c in cs:
            nl=float(dk[(c,2,N,"vns")]["makespan"]); ll=float(dk[(c,3,N,"vns")]["makespan"])
            sp.append(nl/ll)
    m.append(statistics.mean(sp)); s.append(statistics.stdev(sp) if len(sp)>1 else 0)

fig,ax=S.new_figure((12,6))
ax.errorbar(CC,m,yerr=s,marker="D",capsize=4,linewidth=3,markersize=9,
            color=LINECOLOR,zorder=3,label="L2Cache加速比")
ax.axhline(y=1.0,color=IDECOLOR,linestyle="--",alpha=0.9,linewidth=2.2,label="基准$y$=1.000")

offsets = [(12,-12),(12,10),(12,10),(12,10),(12,10)]
for i,(x,y) in enumerate(zip(CC,m)):
    ax.annotate(f"{y:.4f}",(x,y),textcoords="offset points",xytext=offsets[i],
                ha="left",va="bottom",fontsize=14,color=ANNCOLOR,fontweight="bold")

# 误差棒说明放左上角图例下方，避免遮挡
ax.text(0.02,0.80,"误差棒:±1标准差($N$=100)",transform=ax.transAxes,
        fontsize=12,color="#1a1a1a",ha="left",va="top")

ax.set_xlabel("处理器核数$N$",fontsize=16,labelpad=6)
ax.set_ylabel("平均L2Cache加速比",fontsize=16,labelpad=4)
fig.suptitle("图5:P3 L2Cache加速比(100个测试用例)",fontsize=22,fontweight="bold",x=0.5,y=0.03,ha="center")
S.style_legend(ax,loc="upper left")
ax.set_xticks(CC); ax.set_xlim(0.7,5.3)
data_min, data_max = min(m), max(m)
ax.set_ylim(bottom=data_min-0.07, top=data_max+max(s)+0.003)
ax.margins(x=0.01)
from matplotlib.ticker import ScalarFormatter
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
ax.yaxis.set_major_locator(plt.MaxNLocator(6))
ax.tick_params(axis="y",labelsize=14)
ax.tick_params(axis="x",labelsize=14)
ax.grid(True,alpha=0.2,linewidth=0.5)
fig.tight_layout(rect=[0,0.06,1,1],pad=0.5)
O=ROOT/"results/final_visualization/figures"; O.mkdir(parents=True,exist_ok=True)
for f in["pdf","png","svg"]: fig.savefig(O/f"fig5_p3_l2_speedup.{f}",dpi=600,bbox_inches="tight",pad_inches=0.1)
print("图5 OK"); plt.close()





