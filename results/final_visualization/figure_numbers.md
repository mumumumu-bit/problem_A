# Problem A 最终统计数字（论文引用来源）

## 数据来源

- full100 merged: detail.csv (3600 rows)
- singlecore: 100 cases
- P3 N1: 100 cases

## P1 加速比

N=1: mean_speedup=1.0
N=2: mean_speedup=1.789
N=3: mean_speedup=2.4163
N=4: mean_speedup=2.9514
N=5: mean_speedup=3.3877

## P2 加速比

N=1: mean_speedup=1.0
N=2: mean_speedup=1.9004
N=3: mean_speedup=2.6663
N=4: mean_speedup=3.2978
N=5: mean_speedup=3.8369

## P3 L2 对比

N=1: no-L2=3124794, L2=3116693, speedup=1.0086, hit=0.092
N=2: no-L2=1665942, L2=1659155, speedup=1.0068, hit=0.1606
N=3: no-L2=1147788, L2=1147097, speedup=1.0136, hit=0.2412
N=4: no-L2=924640, L2=922512, speedup=1.0152, hit=0.2467
N=5: no-L2=771569, L2=753230, speedup=1.0259, hit=0.2973

## 算法阶段消融

P1 N2: baseline->multiseed=0.0730 (w/t/l=95/5/0), multiseed->vns=0.0179 (w/t/l=73/27/0)
P1 N3: baseline->multiseed=0.1285 (w/t/l=93/7/0), multiseed->vns=0.0292 (w/t/l=77/23/0)
P1 N4: baseline->multiseed=0.1573 (w/t/l=96/4/0), multiseed->vns=0.0386 (w/t/l=80/20/0)
P1 N5: baseline->multiseed=0.1821 (w/t/l=95/5/0), multiseed->vns=0.0244 (w/t/l=82/18/0)
P2 N2: baseline->multiseed=0.0435 (w/t/l=83/17/0), multiseed->vns=0.0056 (w/t/l=65/35/0)
P2 N3: baseline->multiseed=0.0929 (w/t/l=89/11/0), multiseed->vns=0.0153 (w/t/l=86/14/0)
P2 N4: baseline->multiseed=0.1213 (w/t/l=86/14/0), multiseed->vns=0.0209 (w/t/l=81/19/0)
P2 N5: baseline->multiseed=0.1635 (w/t/l=90/10/0), multiseed->vns=0.0308 (w/t/l=81/19/0)
P3 N2: baseline->multiseed=0.0450 (w/t/l=84/16/0), multiseed->vns=0.0038 (w/t/l=62/38/0)
P3 N3: baseline->multiseed=0.0887 (w/t/l=89/11/0), multiseed->vns=0.0144 (w/t/l=86/14/0)
P3 N4: baseline->multiseed=0.1273 (w/t/l=84/16/0), multiseed->vns=0.0097 (w/t/l=79/21/0)
P3 N5: baseline->multiseed=0.1684 (w/t/l=90/10/0), multiseed->vns=0.0367 (w/t/l=86/14/0)
