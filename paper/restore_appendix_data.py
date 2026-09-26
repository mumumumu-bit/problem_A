"""Read frozen Git objects only; never import or run solver/evaluator code."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parent
CASES = {f'case_{i:03}' for i in range(1, 101)}
STABLE = '34d0a423fd99639e2d9c4630cb7979871273a8a7'

def git(*args):
    return subprocess.check_output(['git', *args])

def show(branch, path):
    return git('show', f'{branch}:{path}')

def read_csv(data):
    return list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))

def valid(value, positive=False, rate=False):
    n = float(value)
    assert math.isfinite(n) and (n > 0 if positive else n >= 0), value
    assert not rate or n <= 1, value

def main():
    assert git('branch', '--show-current').decode().strip() == 'paper/draft-v1'
    jobs, sources, manifests = {}, {}, []
    refs = {}
    for shard, expected in [('A', 33), ('B', 33), ('C', 34)]:
        branch = f'origin/results/full100-{shard}'
        refs[branch] = git('rev-parse', branch).decode().strip()
        directory = f'results/full100_teammate_{shard}'
        manifest = json.loads(show(branch, directory + '/manifest.json'))
        assert manifest['git_commit'] == STABLE
        assert len(manifest['cases']) == expected
        manifests.append(manifest)
        archive = tarfile.open(fileobj=io.BytesIO(git('archive', branch, directory)), mode='r:')
        count = 0
        for member in archive:
            if not member.name.endswith('/job.json'):
                continue
            job = json.load(archive.extractfile(member))
            scale = job['rows'][0]['scale']
            effective = dict(manifest['config'])
            effective['max_evaluations'] = min(effective['max_evaluations'], {'small':64,'medium':40,'large':26,'extra-large':20}[scale])
            assert job['config'] == effective, member.name
            assert len(job['rows']) == 3
            assert {r['algorithm'] for r in job['rows']} == {'baseline', 'multiseed', 'vns'}
            rows = [r for r in job['rows'] if r['algorithm'] == 'vns']
            assert len(rows) == 1
            row = rows[0]
            key = (row['case'], row['problem'], row['cores'])
            assert key not in jobs and key[0] in manifest['cases']
            assert member.name.endswith(f'/{key[0]}_p{key[1]}_n{key[2]}/job.json')
            valid(row['makespan'], positive=True)
            valid(row['added_copy_bytes'])
            valid(row['cache_hit_rate'], rate=True)
            jobs[key], sources[key] = row, (branch, member.name)
            count += 1
        assert count == expected * 12
    assert set().union(*(set(m['cases']) for m in manifests)) == CASES
    assert sum(len(m['cases']) for m in manifests) == 100
    assert len(jobs) == 1200
    assert set(jobs) == {(c,p,n) for c in CASES for p in (1,2,3) for n in (2,3,4,5)}
    single_branch = 'origin/results/singlecore-full100'
    refs[single_branch] = git('rev-parse', single_branch).decode().strip()
    refs['origin/results/final-visualization'] = git('rev-parse', 'origin/results/final-visualization').decode().strip()
    refs['origin/results/full100-merged'] = git('rev-parse', 'origin/results/full100-merged').decode().strip()
    single_path = 'results/singlecore_full100/singlecore.csv'
    paired_path = 'results/p3_singlecore_full100/p3_n1_l2.csv'
    single_raw, paired_raw = show(single_branch, single_path), show(single_branch, paired_path)
    single, paired = read_csv(single_raw), read_csv(paired_raw)
    assert len(single) == len(paired) == 100
    assert {r['case'] for r in single} == {r['case'] for r in paired} == CASES
    for path, raw in [(single_path, single_raw), (paired_path, paired_raw)]:
        assert raw == show('origin/results/final-visualization', path)
    for r in single:
        valid(r['makespan'], positive=True)
        valid(r['added_copy_bytes'])
    for r in paired:
        for field in ('no_l2_makespan', 'l2_makespan'):
            valid(r[field], positive=True)
        for field in ('added_copy_no_l2', 'added_copy_l2'):
            valid(r[field])
        valid(r['cache_hit_rate'], rate=True)
        assert re.fullmatch('[0-9a-f]{64}', r['plan_sha256'])
        assert math.isclose(float(r['l2_speedup']), float(r['no_l2_makespan']) / float(r['l2_makespan']), rel_tol=1e-12)
    paired_manifest = json.loads(show(single_branch, 'results/p3_singlecore_full100/manifest.json'))
    single_manifest = json.loads(show(single_branch, 'results/singlecore_full100/manifest.json'))
    assert set(paired_manifest['cases']) == set(single_manifest['cases']) == CASES
    assert paired_manifest['search'] is False and single_manifest['search'] is False
    tool = show(single_branch, 'scripts/final_metrics.py')
    assert hashlib.sha256(tool).hexdigest() == paired_manifest['tool_sha256']['final_metrics.py']
    # Provenance first: all blocks confirmed before any output CSV is created.
    lines = ['# 附录数据来源审计', '', '仅从冻结Git对象恢复；未运行实验或Evaluator。当前分支保持 paper/draft-v1。', '', '| 数据块 | N范围 | 来源branch/文件 | stage | 行数 | 备注 |', '|---|---|---|---|---:|---|']
    multi = '`origin/results/full100-A/B/C:results/full100_teammate_A/B/C/case_XXX_pP_nN/job.json`'
    for block, ns, source, stage, count, note in [
        ('P1 N1','1',f'`{single_branch}:{single_path}`','固定单核baseline',100,'正式Scene A基准'),
        ('P1 N2~5','2~5',multi,'vns',400,'problem=1'),
        ('P2 N1','1',f'`{single_branch}:{single_path}`','固定单核baseline',100,'共用P1基准；不是独立Scene B单核评测'),
        ('P2 N2~5','2~5',multi,'vns',400,'problem=2'),
        ('P3 no-L2 N1','1',f'`{single_branch}:{paired_path}`','固定计划paired',100,'no_l2_makespan / added_copy_no_l2'),
        ('P3 Cache N1','1',f'`{single_branch}:{paired_path}`','固定计划paired',100,'l2_makespan / added_copy_l2 / cache_hit_rate'),
        ('P3 no-L2 N2~5','2~5',multi,'vns',400,'problem=2，分别求解'),
        ('P3 Cache N2~5','2~5',multi,'vns',400,'problem=3，分别求解')]:
        lines.append(f'| {block} | {ns} | {source} | {stage} | {count} | {note} |')
    lines += ['', '## 冻结引用', ''] + [f'- `{b}` → `{sha}`' for b,sha in refs.items()]
    lines += ['', '## 核验与字段映射', '', '- A/B/C manifest分别覆盖33/33/34个不重叠case；1200个job，3600条阶段记录，仅选1200条vns。每个job的有效配置与manifest及stable config.py的StrategySelector规则一致：max_evaluations按small/medium/large/extra-large分别封顶64/40/26/20，其余配置一致。', f'- full100 manifest源码标识 `{STABLE}`，git_dirty=true；不声称是干净源码快照。', '- Makespan取makespan，Added Copy取added_copy_bytes（字节），不是spill_bytes；命中率为[0,1]比例，保持原始精度。', '- 单核CSV与final-visualization分支同路径对象字节一致。', '- P3 N1：100个唯一case，100个合法plan_sha256，99个不同hash。配对依据已审计Evidence Map、归档docs/FINAL_METRICS.md、manifest和与manifest SHA-256一致的scripts/final_metrics.py：同一plan先评估problem=2后评估problem=3，并核验plan未被修改。单个hash不是两份独立plan归档，不将此检查表述为重新评估。', '- P3 N2~5：同case同N匹配P2/P3最终VNS；分别求解，不是same-plan，不支持纯Cache因果消融。', '- 已检查full100-merged/final-visualization正式目录；merged CSV可读性问题沿用Evidence Map，不使用其不可解析数据，不声称文件级一致。', '- 未用旧6/15-case、development、SA或multiseed/baseline多核记录替代正式结果。', '', '## 逐行追溯', '', '多核每一行的源文件可由case_id、问题号与n_cores定位；case所属分片如下。', '']
    for shard,m in zip('ABC',manifests):
        lines.append(f'- {shard}: ' + ', '.join(m['cases']))
    ROOT.joinpath('APPENDIX_DATA_PROVENANCE.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('AUDIT PASS: all eight blocks confirmed; 1200 VNS + 100 singlecore + 100 paired; provenance written.')
    if '--generate' not in sys.argv:
        return
    out = ROOT / 'appendix_data'
    out.mkdir(exist_ok=True)
    single = {r['case']: r for r in single}
    paired = {r['case']: r for r in paired}
    for p in (1,2,3):
        fields = ['case_id','n_cores','makespan','added_copy'] if p < 3 else ['case_id','n_cores','no_l2_makespan','no_l2_added_copy','l2_makespan','l2_added_copy','cache_hit_rate']
        rows = []
        for c in sorted(CASES):
            for n in range(1,6):
                if p < 3:
                    r = single[c] if n == 1 else jobs[c,p,n]
                    values = [r['makespan'],r['added_copy_bytes']]
                elif n == 1:
                    r = paired[c]
                    values = [r['no_l2_makespan'],r['added_copy_no_l2'],r['l2_makespan'],r['added_copy_l2'],r['cache_hit_rate']]
                else:
                    a,b = jobs[c,2,n],jobs[c,3,n]
                    values = [a['makespan'],a['added_copy_bytes'],b['makespan'],b['added_copy_bytes'],b['cache_hit_rate']]
                rows.append(dict(zip(fields,[c,n,*values])))
        with (out/f'p{p}_per_case.csv').open('w',newline='',encoding='utf-8') as f:
            writer = csv.DictWriter(f,fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    # Re-read the actual deliverables for strict checks and recomputation.
    datasets = {}
    for p in (1,2,3):
        data = read_csv((out/f'p{p}_per_case.csv').read_bytes())
        assert len(data) == 500
        keys = [(r['case_id'],int(r['n_cores'])) for r in data]
        assert len(set(keys)) == 500 and set(keys) == {(c,n) for c in CASES for n in range(1,6)}
        for r in data:
            assert all(v != '' for v in r.values())
            for field,value in r.items():
                if field not in ('case_id','n_cores'):
                    valid(value,positive='makespan' in field,rate=field=='cache_hit_rate')
            c,n = r['case_id'],int(r['n_cores'])
            if p<3:
                original = single[c] if n==1 else jobs[c,p,n]
                assert r['makespan']==str(original['makespan'])
                assert r['added_copy']==str(original['added_copy_bytes'])
            else:
                original = paired[c] if n==1 else None
                values = [original[k] for k in ('no_l2_makespan','added_copy_no_l2','l2_makespan','added_copy_l2','cache_hit_rate')] if n==1 else [jobs[c,2,n]['makespan'],jobs[c,2,n]['added_copy_bytes'],jobs[c,3,n]['makespan'],jobs[c,3,n]['added_copy_bytes'],jobs[c,3,n]['cache_hit_rate']]
                assert [r[k] for k in ('no_l2_makespan','no_l2_added_copy','l2_makespan','l2_added_copy','cache_hit_rate')]==list(map(str,values))
        datasets[p] = data
    report = ['# 附录数据完整性与聚合复算', '', '从已生成CSV重新读取并计算；100个唯一case×N=1~5，各500行。重复键、缺失键、空字段、非有限值、负值均为0；makespan均>0，命中率均在[0,1]。', '', '| 指标 | N | CSV复算（原精度） | 正式显示值 | 差值 |', '|---|---:|---:|---:|---:|']
    expected = {1:[1,1.7890,2.4163,2.9514,3.3877],2:[1,1.9004,2.6663,3.2978,3.8369],3:[1.0086,1.0068,1.0136,1.0152,1.0259]}
    for p,data in datasets.items():
        baseline = {r['case_id']:float(r['makespan']) for r in data if r['n_cores']=='1'} if p<3 else {}
        for n in range(1,6):
            subset = [r for r in data if int(r['n_cores'])==n]
            value = statistics.mean(baseline[r['case_id']]/float(r['makespan']) if p<3 else float(r['no_l2_makespan'])/float(r['l2_makespan']) for r in subset)
            target = expected[p][n-1]
            assert abs(value-target) <= 0.00005, (p,n,value,target)
            report.append(f'| P{p}逐case比值平均 | {n} | {value:.12f} | {target:.4f} | {value-target:+.12f} |')
            if p==3:
                hit = statistics.mean(float(r['cache_hit_rate']) for r in subset)
                target_hit = [0.0920,0.1606,0.2412,0.2467,0.2973][n-1]
                assert abs(hit-target_hit)<=0.00005,(n,hit,target_hit)
                report.append(f'| P3命中率平均 | {n} | {hit:.12f} | {target_hit:.4f} | {hit-target_hit:+.12f} |')
    report += ['', '允差为四位小数舍入半单位0.00005；全部通过。未修改正式数字。P3 N1 same-plan配对100/100；N2~5分别求解。', '', '## CSV SHA-256', '']
    report += [f'- p{p}_per_case.csv: `{hashlib.sha256((out/f"p{p}_per_case.csv").read_bytes()).hexdigest()}`' for p in (1,2,3)]
    (out/'VALIDATION.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    tables = out/'word_tables'
    tables.mkdir(exist_ok=True)
    for p,data in datasets.items():
        for n in range(1,6):
            subset = [r for r in data if int(r['n_cores'])==n]
            columns = ['case_id','makespan','added_copy'] if p<3 else ['case_id','no_l2_makespan','no_l2_added_copy','l2_makespan','l2_added_copy','cache_hit_rate']
            labels = ['Case','Makespan','Added Copy'] if p<3 else ['Case','No-L2 Makespan','No-L2 Added Copy','L2 Makespan','L2 Added Copy','Cache Hit Rate']
            with (tables/f'p{p}_n{n}.tsv').open('w',newline='',encoding='utf-8-sig') as f:
                w=csv.writer(f,delimiter='\t')
                w.writerow(labels)
                w.writerows([[r[k] for k in columns] for r in subset])
            with (tables/f'p{p}_n{n}.tsv').open(encoding='utf-8-sig',newline='') as f:
                saved = list(csv.reader(f,delimiter='\t'))
            assert saved == [labels]+[[r[k] for k in columns] for r in subset]
    print('\n'.join(report))

if __name__ == '__main__':
    main()
