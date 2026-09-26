# coding=utf-8
"""图4:P3无L2与只读L2对比"""
import csv, statistics; from pathlib import Path
import matplotlib.pyplot as plt; import numpy as np
import _cn_font as S

ROOT = Path(__file__).resolve().parents[1]
dr = list(csv.DictReader(open(ROOT/"results/full100_merged/detail.csv",encoding="utf-8")))
p3 = list(csv.DictReader(open(ROOT/"results/p3_singlecore_full100/p3_n1_l2.csv",encoding="utf-8")))
dk = {(r["case"],int(r["problem"]),int(r["cores"]),r["algorithm"]):r for r in dr}
cs = sorted(set(r["case"] for r in p3)); CC=[1,2,3,4,5]

NOL2COLOR="#555555"
L2COLOR="#0D47A1"
L2ANN="#0A3273"

nm,ns,lm,ls=[],[],[],[]
for N in CC:
    if N==1:
        nl=[float(r["no_l2_makespan"]) for r in p3]; ll=[float(r["l2_makespan"]) for r in p3]
    else:
        nl=[float(dk[(c,2,N,"vns")]["makespan"]) for c in cs]
        ll=[float(dk[(c,3,N,"vns")]["makespan"]) for c in cs]
    nm.append(statistics.mean(nl)/1e6); ns.append(statistics.stdev([v/1e6 for v in nl]) if len(nl)>1 else 0)
    lm.append(statistics.mean(ll)/1e6); ls.append(statistics.stdev([v/1e6 for v in ll]) if len(ll)>1 else 0)

fig,ax=S.new_figure((12,6))
x=np.arange(len(CC)); w=0.35; gap=0.06

b1=ax.bar(x-w/2,nm,w-gap,yerr=ns,capsize=3,color=NOL2COLOR,edgecolor="white",linewidth=0.5,
          label="无L2(P2 VNS)")
b2=ax.bar(x+w/2,lm,w-gap,yerr=ls,capsize=3,color=L2COLOR,edgecolor="white",linewidth=0.5,
          label="只读L2(P3 VNS)")

for b,clr in[(b1,"#333333"),(b2,L2ANN)]:
    for bar in b:
        h=bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2.,h+0.02,f"{h:.2f}",
                ha="center",va="bottom",fontsize=14,color=clr,fontweight="bold")

ax.text(0.98,0.03,"误差棒:±1 标准差($N$=100)\n单位:$\\times10^6$ cycles",transform=ax.transAxes,
        fontsize=11,color="#1a1a1a",ha="right",va="bottom")

ax.set_xlabel("处理器核数$N$",fontsize=16,labelpad=6)
ax.set_ylabel("平均Makespan($\\times10^6$cycles)",fontsize=16,labelpad=4)
fig.suptitle("图4:P3无L2与只读L2Cache对比(100个测试用例)",fontsize=22,fontweight="bold",x=0.5,y=0.03,ha="center")
ax.set_xticks(x); ax.set_xticklabels([str(n) for n in CC])
S.style_legend(ax,loc="upper right")
ax.set_xlim(-0.6,4.6)
from matplotlib.ticker import ScalarFormatter
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
ax.yaxis.set_major_locator(plt.MaxNLocator(6))
ax.tick_params(axis="y",labelsize=14,pad=5)
ax.tick_params(axis="x",labelsize=14,pad=5)
ax.grid(True,alpha=0.2,linewidth=0.5,axis="y")
fig.tight_layout(rect=[0,0.06,1,1],pad=0.5)
O=ROOT/"results/final_visualization/figures"; O.mkdir(parents=True,exist_ok=True)
for f in["pdf","png","svg"]: fig.savefig(O/f"fig4_p3_noL2_vs_L2.{f}",dpi=600,bbox_inches="tight",pad_inches=0.1)
print("图4 OK"); plt.close()




