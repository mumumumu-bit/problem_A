# coding=utf-8
"""图6: 算法阶段消融 — 精确排版版"""
import csv, statistics; from pathlib import Path
import matplotlib.pyplot as plt; import numpy as np
import _cn_font as S

ROOT = Path(__file__).resolve().parents[1]
dr = list(csv.DictReader(open(ROOT/"results/full100_merged/detail.csv",encoding="utf-8")))
dk = {(r["case"],int(r["problem"]),int(r["cores"]),r["algorithm"]):r for r in dr}
cas = sorted(set(r["case"] for r in dr))
LBL=["基线","多种子初始化","VNS"]
COL=[S.PALETTE["gray"],S.PALETTE["orange"],S.PALETTE["green"]]

fig, axes = plt.subplots(2,3,figsize=(14,9))
for ax in axes.flat:
    for sp in ax.spines.values(): sp.set_linewidth(0.8)
    ax.tick_params(width=0.8,labelsize=12)
    from matplotlib.ticker import FormatStrFormatter
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))

for pi,p in enumerate([1,2,3]):
    for ci,(cl,ch) in enumerate([(2,3),(4,5)]):
        ax=axes[ci,pi]
        d={"baseline":[],"multiseed":[],"vns":[]}
        for c in[cl,ch]:
            for cs in cas:
                for s in["baseline","multiseed","vns"]:
                    r=dk.get((cs,p,c,s))
                    if r: d[s].append(int(r["makespan"]))
        ms=[statistics.mean(d[s])/1e3 for s in["baseline","multiseed","vns"]]
        bars=ax.bar(np.arange(3),ms,color=COL,edgecolor="white",linewidth=0.5,width=0.55,
                    tick_label=LBL)
        # 柱体顶部标注 + 白底防遮挡
        for b in bars:
            h=b.get_height()
            ax.text(b.get_x()+b.get_width()/2.,h+1.5,f"{h:.1f}",
                    ha="center",va="bottom",fontsize=7.5,
                    bbox=dict(facecolor="white",edgecolor="none",pad=0.3,alpha=0.7))
        i1=(ms[0]-ms[1])/ms[0]*100; i2=(ms[1]-ms[2])/ms[1]*100
        ax.set_title(f"P{p}($N$={cl},{ch})",fontsize=14,fontweight="bold",pad=6)
        ax.set_ylabel("Makespan($\\times10^3$cycles)",fontsize=16,labelpad=6)
        mid1=(ms[0]+ms[1])/2; mid2=(ms[1]+ms[2])/2
        ax.annotate(f"$\\downarrow${i1:.1f}%",xy=(0.5,mid1),ha="center",va="center",fontsize=9,
                    color="white",fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15",fc=S.PALETTE["red"],alpha=0.9))
        ax.annotate(f"$\\downarrow${i2:.1f}%",xy=(1.5,mid2),ha="center",va="center",fontsize=9,
                    color="white",fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15",fc=S.PALETTE["green"],alpha=0.9))

fig.suptitle("图6:算法阶段消融—基线→多种子初始化→变邻域搜索(VNS)",fontsize=22,fontweight="bold",x=0.5,y=0.03,ha="center")
fig.tight_layout(rect=[0.02,0.06,1,0.99],pad=0.8)
O=ROOT/"results/final_visualization/figures"; O.mkdir(parents=True,exist_ok=True)
for f in["pdf","png","svg"]: fig.savefig(O/f"fig6_stage_ablation.{f}",dpi=600)
print("图6 OK"); plt.close()


