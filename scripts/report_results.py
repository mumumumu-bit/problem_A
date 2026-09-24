# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Rebuild per-case Markdown/LaTeX tables and diagnostic correlations from real logs."""
from run_all import main
import argparse
import csv
import json
import math
from pathlib import Path
import statistics
from npu_scheduler.experiment.recorder import write_csv


def correlation(xs,ys):
    if len(xs)<3:
        return None
    mx,my=statistics.mean(xs),statistics.mean(ys)
    xx=sum((x-mx)**2 for x in xs); yy=sum((y-my)**2 for y in ys)
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(xx*yy) if xx and yy else None


def report(directory):
    rows=list(csv.DictReader((directory/'benchmark.csv').open(encoding='utf-8')))
    by={}
    for r in rows:
        for f in ('problem','cores','makespan','added_copy_bytes','spill_bytes','evaluations'):
            r[f]=int(r[f])
        r['runtime']=float(r['runtime'])
        by.setdefault((r['case'],r['problem'],r['cores']),{})[r['algorithm']]=r
    lines=['# 第一轮代表算例实验结果','',
        '范围：6个固定开发算例，3个问题，N=2/4。不是100例正式竞赛结果。',
        'B=工作量均衡初解；M=多初解最佳；V=在M上进行VNS。时间为累计墙钟秒数，包含前序阶段，不包含独立CLI复核。',
        '改进率=(B−V)/B，VNS增益=(M−V)/M；所有Makespan单位为cycles，搬运量单位为bytes。','']
    detail=[]
    for problem in (1,2,3):
        lines += [f'## 问题 {problem}','',
            '| Case | N | B Makespan | M Makespan | V Makespan | 总改进 | VNS增益 | B/M/V时间(s) | B/M/V Added Copy |',
            '|---|---:|---:|---:|---:|---:|---:|---|---|']
        for (case,p,n),algs in sorted(by.items()):
            if p!=problem: continue
            b,m,v=[algs[a] for a in ('baseline','multiseed','vns')]
            gain=100*(1-v['makespan']/b['makespan']); local=100*(1-v['makespan']/m['makespan'])
            lines.append(f"| {case} | {n} | {b['makespan']:,} | {m['makespan']:,} | {v['makespan']:,} | {gain:.2f}% | {local:.2f}% | "+'/'.join(f"{x['runtime']:.2f}" for x in (b,m,v))+' | '+' / '.join(str(x['added_copy_bytes']) for x in (b,m,v))+' |')
            detail.append(dict(case=case,problem=p,cores=n,baseline=b['makespan'],multiseed=m['makespan'],vns=v['makespan'],improvement_percent=gain,vns_gain_percent=local,runtime=v['runtime']))
        lines.append('')
    write_csv(directory/'comparison.csv',detail)
    lines+=['## 统计说明','',
        f"36组中VNS严格改善多初解的组数：{sum(r['vns_gain_percent']>0 for r in detail)}。",
        f"平均逐组Makespan降低：{statistics.mean(r['improvement_percent'] for r in detail):.2f}%；VNS相对多初解平均降低：{statistics.mean(r['vns_gain_percent'] for r in detail):.2f}%。",'']
    trials=[]
    for path in directory.glob('*/trials.jsonl'):
        problem=int(path.parent.name.split('_p')[1].split('_')[0])
        trials.extend(dict(json.loads(l),problem=problem) for l in path.read_text(encoding='utf-8').splitlines())
    diagnostics=[]
    for problem in (1,2,3):
        group=[t for t in trials if t['problem']==problem and t['valid']]
        diagnostics.append(dict(problem=problem,trials=len(group),
            memory_spill_pearson=correlation([t['memory_excess'] for t in group],[t['spill_bytes'] for t in group]),
            memory_makespan_pearson=correlation([t['memory_excess'] for t in group],[t['makespan'] for t in group]),
            surrogate_makespan_pearson=correlation([t['score'] for t in group],[t['makespan'] for t in group])))
    write_csv(directory/'estimator_diagnostics.csv',diagnostics)
    lines+=['内存估计相关性见 estimator_diagnostics.csv。跨case的Pearson受规模混杂影响，不能据此宣称因果或单例排序可靠；默认内存/Cache奖励权重仍为0。','',
            '## 独立复核','']
    jobs=[json.loads(p.read_text(encoding='utf-8')) for p in directory.glob('*/job.json')]
    lines += [f"已完成job：{len(jobs)}；官方CLI复核通过：{sum(j['cli_verified'] for j in jobs)}；真实评估调用：{sum(j['evaluator_calls'] for j in jobs)}；缓存命中：{sum(j['cache_hits'] for j in jobs)}。",'']
    lines += [f"求解总墙钟时间之和（并行任务相加）：{sum(j['total_seconds'] for j in jobs):.2f}s；其中官方评估函数累计：{sum(j['evaluator_seconds'] for j in jobs):.2f}s。",'']
    singlefile=directory/'singlecore.csv'
    if singlefile.exists():
        single={r['case']:int(r['makespan']) for r in csv.DictReader(singlefile.open(encoding='utf-8'))}
        speed=[]
        for p in (1,2):
            for n in sorted({n for _,_,n in by}):
                group=[algs['vns'] for (case,prob,k),algs in by.items() if prob==p and k==n]
                speed.append(dict(problem=p,cores=n,mean_speedup=statistics.mean(single[r['case']]/r['makespan'] for r in group)))
        write_csv(directory/'singlecore_speedup_summary.csv',speed)
        lines+=['## 相对官方独立单核的平均加速比','', '| 问题 | 核数 | 平均逐例加速比 |','|---|---:|---:|']
        lines.extend(f"| {r['problem']} | {r['cores']} | {r['mean_speedup']:.3f} |" for r in speed)
    (directory/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    latex=['\\begin{tabular}{llrrrrr}','\\toprule','Case & P/N & Baseline & Multi-seed & VNS & Gain (\\%) & Time (s) \\\\','\\midrule']
    for r in detail:
        escaped_case=r['case'].replace('_','\\_')
        latex.append(f"{escaped_case} & {r['problem']}/{r['cores']} & {r['baseline']} & {r['multiseed']} & {r['vns']} & {r['improvement_percent']:.2f} & {r['runtime']:.2f} \\\\")
    latex+=['\\bottomrule','\\end{tabular}']
    (directory/'benchmark_table.tex').write_text('\n'.join(latex)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run-dir',type=Path,required=True)
    report(parser.parse_args().run_dir)
