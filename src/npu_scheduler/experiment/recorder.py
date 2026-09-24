# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""CSV, manifests and per-trial JSON records."""
import csv
import hashlib
import platform
from pathlib import Path
import subprocess
import sys
import importlib.metadata
from datetime import datetime, timezone
from .. import __version__
from ..evaluator.cache import atomic_json


def source_hash(root):
    files=list((root/'src').rglob('*.py'))+list((root/'scripts').glob('*.py'))
    return hashlib.sha256(b''.join(p.relative_to(root).as_posix().encode()+p.read_bytes() for p in sorted(files))).hexdigest()


def manifest(root, config, cases, problems, cores):
    try:
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
        dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True))
    except (OSError,subprocess.CalledProcessError):
        commit,dirty=None,None
    return dict(created=datetime.now(timezone.utc).isoformat(),git_commit=commit,git_dirty=dirty,
        python=sys.version,platform=platform.platform(),algorithm_version=__version__,source_hash=source_hash(root),
        config=config.to_dict(),seed=config.seed,cases=cases,problems=problems,cores=cores,
        official_hash=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((root/'code').glob('*.py')))).hexdigest(),
        dependencies={p.metadata['Name']:p.version for p in importlib.metadata.distributions()},
        timing='Wall time, cumulative across baseline -> multi-seed -> VNS. Cache hits recorded separately.',
        budget='Soft wall deadline checked between official calls; one in-flight evaluation may overrun.')


def write_csv(path,rows):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        return
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
