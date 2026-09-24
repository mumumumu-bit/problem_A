# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Case-level process parallelism; each official evaluator remains sequential."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import json
import os
from pathlib import Path
import statistics
import time
from ..graph import GraphData
from ..config import SolverConfig
from ..evaluator.official_adapter import OfficialEvaluator
from ..evaluator.cache import atomic_json, digest
from ..search.vns import solve
from .recorder import manifest,write_csv

DEVELOPMENT_CASES=('case_001','case_019','case_005','case_050','case_025','case_085')


def audit(data_dir, output):
    rows=[]
    for path in sorted(Path(data_dir).glob('case_[0-9][0-9][0-9].json')):
        start=time.perf_counter(); graph=GraphData.load(path)
        rows.append(dict(graph.features(),sha256=graph.fingerprint,load_seconds=time.perf_counter()-start))
    write_csv(output,rows)
    return rows


def _job(args):
    graph_path,hardware_path,outdir,problem,cores,config_dict,cache_dir,verify=args
    start=time.perf_counter(); graph=GraphData.load(graph_path)
    load_seconds=time.perf_counter()-start
    evaluator=OfficialEvaluator(graph,hardware_path,problem,cache_dir)
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    def record(trial,incumbent,value):
        with (outdir/'trials.jsonl').open('a',encoding='utf-8') as file:
            file.write(json.dumps(trial,ensure_ascii=False)+'\n')
        if incumbent is not None and trial['improved']:
            atomic_json(outdir/'incumbent.json',incumbent.plan(graph))
    # New solver run replays seed/candidate generation and reuses cached scores.
    # A completed job is resumed by run_benchmark without regenerating it.
    (outdir/'trials.jsonl').write_text('',encoding='utf-8')
    result=solve(graph,cores,evaluator,SolverConfig(**config_dict),on_trial=record)
    rows=[]
    for name,snapshot in result['snapshots'].items():
        ev=snapshot['evaluation']
        rows.append(dict(case=graph.name,problem=problem,cores=cores,algorithm=name,
            makespan=ev.makespan,added_copy_bytes=ev.added_copy_bytes,spill_bytes=ev.spill_bytes,
            cache_hit_rate=ev.cache_hit_rate,runtime=load_seconds+snapshot['seconds'],
            evaluations=snapshot['evaluations'],source=snapshot['source'],scale=result['scale']))
        atomic_json(outdir/f'{name}_plan.json',snapshot['solution'].plan(graph))
    cli_seconds=0.0
    if verify:
        t=time.perf_counter()
        evaluator.verify_cli(graph_path,result['solution'],outdir/'cli')
        cli_seconds=time.perf_counter()-t
    atomic_json(outdir/'job.json',dict(rows=rows,config=result['config'],
        graph_hash=graph.fingerprint,official_hash=evaluator.official_hash,
        evaluator_calls=result['evaluator_calls'],cache_hits=result['cache_hits'],
        evaluator_seconds=result['evaluator_seconds'],total_seconds=result['seconds'],
        cli_verified=verify,cli_seconds=cli_seconds,
        invalid_candidates=sum(not t['valid'] for t in result['trials'])))
    print(f'{graph.name} p{problem} n{cores}: '+', '.join(f"{r['algorithm']}={r['makespan']}" for r in rows),flush=True)
    return rows


def run_benchmark(data_dir, hardware_path, outdir, config, cases=DEVELOPMENT_CASES,
                  problems=(1,2,3),cores=(2,4),workers=None,cache_dir=None,verify=True):
    root=Path(__file__).resolve().parents[3]
    outdir=Path(outdir).resolve(); outdir.mkdir(parents=True,exist_ok=True)
    run_manifest=manifest(root,config,list(cases),list(problems),list(cores))
    identity=digest(dict(source=run_manifest['source_hash'],official=run_manifest['official_hash'],config=config.to_dict(),cases=list(cases),
        problems=list(problems),cores=list(cores),verify=verify,
        hardware=Path(hardware_path).read_text(encoding='utf-8'),
        graphs={c:digest(json.loads((Path(data_dir)/(c+'.json')).read_text(encoding='utf-8'))) for c in cases}))
    previous=outdir/'manifest.json'
    if previous.exists() and json.loads(previous.read_text(encoding='utf-8')).get('identity') != identity:
        raise ValueError('Run directory belongs to a different source/config/dataset. Choose a new --output.')
    if not previous.exists():
        atomic_json(previous,dict(run_manifest,identity=identity))
    jobs,rows=[],[]
    for case in cases:
        for problem in problems:
            for n in cores:
                directory=outdir/f'{case}_p{problem}_n{n}'
                completed=directory/'job.json'
                if completed.exists():
                    rows.extend(json.loads(completed.read_text(encoding='utf-8'))['rows'])
                else:
                    jobs.append((str((Path(data_dir)/(case+'.json')).resolve()),str(Path(hardware_path).resolve()),
                        str(directory),problem,n,config.to_dict(),str(Path(cache_dir).resolve()) if cache_dir else None,verify))
    count=min(os.cpu_count() or 1,workers or config.workers)
    if count==1:
        for job in jobs:
            rows.extend(_job(job)); write_csv(outdir/'benchmark.csv',rows)
    else:
        with ProcessPoolExecutor(max_workers=count) as pool:
            futures=[pool.submit(_job,j) for j in jobs]
            for future in as_completed(futures):
                rows.extend(future.result()); write_csv(outdir/'benchmark.csv',rows)
    rows.sort(key=lambda r:(r['case'],r['problem'],r['cores'],r['algorithm']))
    write_csv(outdir/'benchmark.csv',rows)
    summary=[]
    for problem in problems:
        for n in cores:
            for algorithm in ('baseline','multiseed','vns'):
                group=[r for r in rows if r['problem']==problem and r['cores']==n and r['algorithm']==algorithm]
                bases={r['case']:r['makespan'] for r in rows if r['problem']==problem and r['cores']==n and r['algorithm']=='baseline'}
                summary.append(dict(problem=problem,cores=n,algorithm=algorithm,count=len(group),
                    mean_normalized_makespan=statistics.mean(r['makespan']/bases[r['case']] for r in group),
                    mean_speedup_vs_baseline=statistics.mean(bases[r['case']]/r['makespan'] for r in group),
                    mean_runtime=statistics.mean(r['runtime'] for r in group)))
    write_csv(outdir/'summary.csv',summary)
    return rows
