# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Controlled P2/P3 evaluation of exactly the same saved P3 incumbent."""
from run_all import main
from pathlib import Path
import argparse
import json
from npu_scheduler.graph import GraphData
from npu_scheduler.types import Solution
from npu_scheduler.evaluator.official_adapter import OfficialEvaluator
from npu_scheduler.experiment.recorder import write_csv

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[1]/'data')
    args=p.parse_args(); rows=[]
    for directory in sorted(args.run_dir.glob('case_*_p3_n*')):
        case=directory.name.split('_p')[0]; n=int(directory.name.split('_n')[1])
        graph=GraphData.load(args.data_dir/(case+'.json'))
        solution=Solution.from_plan(graph,json.loads((directory/'vns_plan.json').read_text(encoding='utf-8')))
        no_l2=OfficialEvaluator(graph,args.data_dir/'config.txt',2).evaluate(solution)
        saved=json.loads((directory/'job.json').read_text(encoding='utf-8'))
        l2=next(r for r in saved['rows'] if r['algorithm']=='vns')
        if not no_l2.valid: raise RuntimeError(no_l2.error)
        rows.append(dict(case=case,cores=n,no_L2_makespan=no_l2.makespan,L2_makespan=l2['makespan'],
            L2_speedup=no_l2.makespan/l2['makespan'],cache_hit_rate=l2['cache_hit_rate'],added_copy_bytes=l2['added_copy_bytes']))
        write_csv(args.run_dir/'l2_same_plan.csv',rows)
        print(case,n,rows[-1]['L2_speedup'],flush=True)
