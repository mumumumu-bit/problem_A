# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Command line interface. Relative user paths are resolved from the working directory."""
import argparse
from dataclasses import replace,asdict
from pathlib import Path
import json
from .config import SolverConfig
from .graph import GraphData
from .evaluator.official_adapter import OfficialEvaluator
from .evaluator.cache import atomic_json
from .search.vns import solve
from .experiment.runner import run_benchmark,audit,load_development_cases

ROOT=Path(__file__).resolve().parents[2]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['solve','benchmark','audit','plot'])
    parser.add_argument('--graph',type=Path)
    parser.add_argument('--data-dir',type=Path,default=ROOT/'data')
    parser.add_argument('--config',type=Path,default=ROOT/'data/config.txt',help='Official hardware config')
    parser.add_argument('--solver-config',type=Path)
    parser.add_argument('--problem',type=int,nargs='+',default=[1,2,3],choices=[1,2,3])
    parser.add_argument('--cores',type=int,nargs='+',default=[2,4])
    parser.add_argument('--cases',nargs='+',default=list(load_development_cases()))
    parser.add_argument('--workers',type=int)
    parser.add_argument('--time-budget',type=float)
    parser.add_argument('--max-evaluations',type=int)
    parser.add_argument('--algorithm',choices=['baseline','multiseed','vns'],default='vns')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cache-dir',type=Path)
    parser.add_argument('--skip-cli-verification',action='store_true')
    args=parser.parse_args(argv)
    config=SolverConfig.load(args.solver_config)
    changes={k:getattr(args,k) for k in ('workers','time_budget','max_evaluations') if getattr(args,k) is not None}
    config=replace(config,**changes)
    if args.command=='audit':
        print(f'Audited {len(audit(args.data_dir,args.output))} cases')
    elif args.command=='benchmark':
        run_benchmark(args.data_dir,args.config,args.output,config,args.cases,args.problem,args.cores,
                      args.workers,args.cache_dir,not args.skip_cli_verification)
    elif args.command=='plot':
        from .visualization.plots import plot_benchmark
        plot_benchmark(args.output)
    else:
        if args.graph is None or len(args.problem)!=1 or len(args.cores)!=1:
            parser.error('solve requires --graph, one --problem and one --cores')
        graph=GraphData.load(args.graph)
        evaluator=OfficialEvaluator(graph,args.config,args.problem[0],args.cache_dir)
        result=solve(graph,args.cores[0],evaluator,config,args.algorithm)
        atomic_json(args.output,result['solution'].plan(graph))
        atomic_json(args.output.with_suffix('.metrics.json'),dict(evaluation=asdict(result['evaluation']),
            seconds=result['seconds'],trials=result['trials'],config=result['config']))
        if not args.skip_cli_verification:
            evaluator.verify_cli(args.graph,result['solution'],args.output.parent/(args.output.stem+'_cli'))
        print(json.dumps(asdict(result['evaluation'])))


if __name__=='__main__':
    main()
