# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Independent official single-core results for a completed development run."""
from run_all import main
from npu_scheduler.graph import GraphData
from npu_scheduler.evaluator.official_adapter import OfficialEvaluator
from npu_scheduler.experiment.recorder import write_csv
import argparse
import json
from pathlib import Path
import time

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[1]/'data')
    args=parser.parse_args()
    manifest=json.loads((args.run_dir/'manifest.json').read_text(encoding='utf-8'))
    rows=[]
    for case in manifest['cases']:
        start=time.perf_counter()
        graph=GraphData.load(args.data_dir/(case+'.json'))
        result=OfficialEvaluator(graph,args.data_dir/'config.txt',1).singlecore()
        rows.append(dict(case=case,makespan=result['makespan'],added_copy_bytes=result['data_movement_bytes']['added_copy_bytes'],seconds=time.perf_counter()-start))
        write_csv(args.run_dir/'singlecore.csv',rows)
        print(case,result['makespan'],flush=True)
