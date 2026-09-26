# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Development figures explicitly distinguish algorithm baseline from single core."""
import csv
import json
from pathlib import Path
import statistics
import warnings
from .style import apply_style,save as save_fig,COLORS,LABELS,label_bars


def plot_benchmark(directory):
    directory=Path(directory)
    try:
        plt=apply_style()
    except ImportError:
        warnings.warn('Matplotlib is unavailable; benchmark CSV remains usable. Install the dev extra to plot.')
        return []
    rows=list(csv.DictReader((directory/'benchmark.csv').open(encoding='utf-8')))
    for r in rows:
        for key in ('problem','cores','makespan','added_copy_bytes'):
            r[key]=int(r[key])
        r['runtime']=float(r['runtime'])
    figures=directory/'figures'
    baselines={(r['case'],r['problem'],r['cores']):r['makespan'] for r in rows if r['algorithm']=='baseline'}
    single={}
    if (directory/'singlecore.csv').exists():
        single={r['case']:int(r['makespan']) for r in csv.DictReader((directory/'singlecore.csv').open(encoding='utf-8'))}
    for problem in sorted({r['problem'] for r in rows}):
        fig,ax=plt.subplots()
        for alg,marker,line in [('baseline','o','--'),('multiseed','s','-.'),('vns','^','-')]:
            ns=sorted({r['cores'] for r in rows if r['problem']==problem})
            values=[]
            for n in ns:
                group=[r for r in rows if r['problem']==problem and r['cores']==n and r['algorithm']==alg]
                values.append(statistics.mean((single[r['case']] if single and problem in (1,2) else baselines[r['case'],problem,n])/r['makespan'] for r in group))
            if single and problem in (1,2):
                ns,values=[1]+ns,[1]+values
            ax.plot(ns,values,marker=marker,linestyle=line,color=COLORS[alg],label=LABELS[alg])
        ax.set(xlabel='核心数',ylabel='平均逐例加速比' if single and problem in (1,2) else '相对负载均衡初解的平均加速比',xticks=ns,
            title=f'问题 {problem} 加速比')
        ax.legend()
        save_fig(fig,figures,f'p{problem}_speedup'); plt.close(fig)
    # Relative makespan avoids mixing cycle scales across heterogeneous cases.
    fig,ax=plt.subplots()
    for j,alg in enumerate(('baseline','multiseed','vns')):
        vals=[r['makespan']/baselines[r['case'],r['problem'],r['cores']] for r in rows if r['algorithm']==alg]
        mean_val = statistics.mean(vals)
        ax.bar(j, mean_val, color=COLORS[alg], width=.6)
    bars_container = [c for c in ax.containers]
    if bars_container:
        label_bars(ax, bars_container[0], fmt='{:.3f}', offset=0.01)
    ax.set(xticks=range(3),xticklabels=[LABELS[a] for a in ('baseline','multiseed','vns')],
        xlabel='求解阶段',ylabel='平均归一化Makespan',
        title='各阶段归一化Makespan消融实验')
    save_fig(fig,figures,'ablation'); plt.close(fig)
    fig,ax=plt.subplots()
    for alg,marker in [('baseline','o'),('multiseed','s'),('vns','^')]:
        group=[r for r in rows if r['algorithm']==alg]
        ax.scatter([r['runtime'] for r in group],[r['makespan']/baselines[r['case'],r['problem'],r['cores']] for r in group],
            c=COLORS[alg],marker=marker,label=LABELS[alg],s=25,alpha=.7)
    ax.set(xlabel='累计求解时间 (秒)',ylabel='Makespan / 负载均衡初解Makespan',xscale='log',
        title='求解时间与调度质量权衡'); ax.legend()
    save_fig(fig,figures,'runtime_quality'); plt.close(fig)
    p2={(r['case'],r['cores']):r for r in rows if r['problem']==2 and r['algorithm']=='vns'}
    p3={(r['case'],r['cores']):r for r in rows if r['problem']==3 and r['algorithm']=='vns'}
    if p2 and p3:
        fig,ax=plt.subplots()
        ns=sorted({n for _,n in p2})
        values=[statistics.mean(p2[c,n]['makespan']/p3[c,n]['makespan'] for c,k in p2 if k==n and (c,n) in p3) for n in ns]
        ax.plot(ns,[1]*len(ns),'o--',color=COLORS['no_l2'],label='无L2')
        ax.plot(ns,values,'s-',color=COLORS['l2'],label='有L2（独立优化）')
        ax.set(xlabel='核心数',ylabel='平均无L2 / 有L2 Makespan',xticks=ns,
            title='P3 L2 Cache加速效果对比'); ax.legend()
        save_fig(fig,figures,'p3_l2_comparison'); plt.close(fig)
    controlled=directory/'l2_same_plan.csv'
    if controlled.exists():
        paired=list(csv.DictReader(controlled.open(encoding='utf-8')))
        ns=sorted({int(r['cores']) for r in paired})
        values=[statistics.mean(float(r['L2_speedup']) for r in paired if int(r['cores'])==n) for n in ns]
        fig,ax=plt.subplots()
        ax.plot(ns,[1]*len(ns),'o--',color=COLORS['no_l2'],label='无L2，同方案')
        ax.plot(ns,values,'s-',color=COLORS['l2'],label='有L2，同方案')
        ax.set(xlabel='核心数',ylabel='平均无L2 / 有L2 Makespan',xticks=ns,
            title='同方案下P3 L2 Cache加速对比'); ax.legend()
        save_fig(fig,figures,'p3_same_plan_cache'); plt.close(fig)
    captions={'scope':'Development subset only; not the final 100-case competition experiment.',
        'speedup':'Mean of per-case ratios; singlecore.csv is the independent official single-core baseline.',
        'ablation':'Nested baseline, multi-seed and VNS checkpoints under the same run.',
        'runtime':'Cumulative wall time including earlier algorithm stages; CLI verification excluded.',
        'l2':'Independent P2/P3 optimization confounds placement changes and cache benefit; not a controlled same-plan cache ablation.'}
    (figures/'captions.json').write_text(json.dumps(captions,indent=2),encoding='utf-8')
    return sorted(figures.glob('*.png'))
