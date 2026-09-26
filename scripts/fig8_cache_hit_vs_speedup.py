# coding=utf-8
"""图8: Cache命中率与L2加速比关联散点图 — P3只读L2Cache效果分析"""
import csv, statistics; from pathlib import Path
import matplotlib.pyplot as plt; import numpy as np
import _cn_font as S

ROOT = Path(__file__).resolve().parents[1]
dr = list(csv.DictReader(open(ROOT/"results/full100_merged/detail.csv",encoding="utf-8")))
dk = {(r["case"],int(r["problem"]),int(r["cores"]),r["algorithm"]):r for r in dr}
cas = sorted(set(r["case"] for r in dr))

fig, axes = plt.subplots(2,2,figsize=(13,10))
CS=[2,3,4,5]
COLORS=[S.PALETTE["blue"],S.PALETTE["orange"],S.PALETTE["green"],S.PALETTE["red"]]

for idx,(c,ax) in enumerate(zip(CS,axes.flat)):
    for sp in ax.spines.values(): sp.set_linewidth(0.8)
    ax.tick_params(width=0.8,labelsize=12)
    xvals=[]; yvals=[]
    for cs in cas:
        p2r=dk.get((cs,2,c,"vns"))
        p3r=dk.get((cs,3,c,"vns"))
        if p2r and p3r:
            p2m=int(p2r["makespan"]); p3m=int(p3r["makespan"])
            ch=float(p3r.get("cache_hit_rate",0))
            if p3m>0 and p2m>0:
                spd=p2m/p3m
                xvals.append(ch); yvals.append(spd)
    ax.scatter(xvals,yvals,c=COLORS[idx],alpha=0.6,edgecolors="white",linewidth=0.3,s=40)
    # 添加回归趋势线
    if len(xvals)>2:
        z=np.polyfit(xvals,yvals,1); p=np.poly1d(z)
        xs=np.linspace(min(xvals),max(xvals),50)
        ax.plot(xs,p(xs),color=COLORS[idx],linewidth=2,alpha=0.8,linestyle="--")
        # 计算Pearson相关系数
        r=np.corrcoef(xvals,yvals)[0,1]
        ax.text(0.95,0.92,f"$r={r:.3f}$",transform=ax.transAxes,fontsize=11,
                ha="right",va="top",color="#333333",
                bbox=dict(facecolor="white",edgecolor=S.PALETTE["lightgray"],boxstyle="round,pad=0.3",alpha=0.85))
    ax.axhline(y=1.0,color=S.PALETTE["darkgray"],linewidth=0.8,linestyle="--",alpha=0.5)
    ax.set_title(f"$N$={c}",fontsize=16,fontweight="bold",pad=8)
    ax.set_xlabel("Cache命中率",fontsize=14,labelpad=4)
    ax.set_ylabel("L2加速比",fontsize=14,labelpad=4)
    ax.grid(True,alpha=0.15,linewidth=0.5)

fig.suptitle("图8:Cache命中率与L2加速比关联分析(P3只读L2Cache)",fontsize=22,fontweight="bold",x=0.5,y=0.03,ha="center")
fig.tight_layout(rect=[0.02,0.06,1,0.99],pad=0.8)
O=ROOT/"results/final_visualization/figures"; O.mkdir(parents=True,exist_ok=True)
for f in["pdf","png","svg"]: fig.savefig(O/f"fig8_cache_hit_vs_speedup.{f}",dpi=600,bbox_inches="tight",pad_inches=0.1)
print("图8 OK"); plt.close()
