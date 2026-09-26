# coding=utf-8
"""图7: VNS收益分布 — 箱线图展示各case上VNS相对多种子初始化的提升百分比"""
import csv, statistics; from pathlib import Path
import matplotlib.pyplot as plt; import numpy as np
import _cn_font as S

ROOT = Path(__file__).resolve().parents[1]
dr = list(csv.DictReader(open(ROOT/"results/full100_merged/detail.csv",encoding="utf-8")))
dk = {(r["case"],int(r["problem"]),int(r["cores"]),r["algorithm"]):r for r in dr}
cas = sorted(set(r["case"] for r in dr))

fig, axes = plt.subplots(2,3,figsize=(14,9))
for ax in axes.flat:
    for sp in ax.spines.values(): sp.set_linewidth(0.8)
    ax.tick_params(width=0.8,labelsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{v:.1f}%"))

for pi,p in enumerate([1,2,3]):
    for ci,(cl,ch) in enumerate([(2,3),(4,5)]):
        ax=axes[ci,pi]
        data={"$N$="+str(cl):[],"$N$="+str(ch):[]}
        for c,k in [(cl,"$N$="+str(cl)),(ch,"$N$="+str(ch))]:
            for cs in cas:
                mr=dk.get((cs,p,c,"multiseed"))
                vr=dk.get((cs,p,c,"vns"))
                if mr and vr:
                    mm,vm=int(mr["makespan"]),int(vr["makespan"])
                    if mm>0: data[k].append((mm-vm)/mm*100)
        bp=ax.boxplot([data[k] for k in data],tick_labels=list(data.keys()),
                      patch_artist=True,widths=0.5,
                      medianprops=dict(color="black",linewidth=1.5),
                      whiskerprops=dict(linewidth=1),capprops=dict(linewidth=1),
                      boxprops=dict(linewidth=1),flierprops=dict(marker="o",markersize=3,alpha=0.5))
        bp["boxes"][0].set_facecolor(S.PALETTE["blue"]); bp["boxes"][0].set_alpha(0.7)
        bp["boxes"][1].set_facecolor(S.PALETTE["orange"]); bp["boxes"][1].set_alpha(0.7)
        # 标注均值
        for idx,k in enumerate(data):
            if data[k]:
                m=statistics.mean(data[k])
                ax.text(idx+1,ax.get_ylim()[1]*1.02,f"{m:.1f}%",ha="center",va="bottom",fontsize=9,
                        fontweight="bold",color="#1a1a1a")
        ax.set_title(f"P{p}($N$={cl},{ch})",fontsize=14,fontweight="bold",pad=6)
        ax.set_ylabel("VNS收益(%)",fontsize=16,labelpad=6)
        ax.axhline(y=0,color=S.PALETTE["darkgray"],linewidth=0.8,linestyle="--",alpha=0.6)

fig.suptitle("图7:VNS收益分布—相对多种子初始化的每用例Makespan提升",fontsize=22,fontweight="bold",x=0.5,y=0.03,ha="center")
fig.tight_layout(rect=[0.02,0.06,1,0.99],pad=0.8)
O=ROOT/"results/final_visualization/figures"; O.mkdir(parents=True,exist_ok=True)
for f in["pdf","png","svg"]: fig.savefig(O/f"fig7_vns_gain_dist.{f}",dpi=600,bbox_inches="tight",pad_inches=0.1)
print("图7 OK"); plt.close()
