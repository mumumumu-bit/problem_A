# coding=utf-8
"""Problem A 最终数据统计与论文可视化 — 一键生成所有表格、图表、附录数据。"""
import csv
import json
import os
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_visualization"
TABLES = OUT / "tables"
FIGURES = OUT / "figures"
APPENDIX = OUT / "appendix"
TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
APPENDIX.mkdir(parents=True, exist_ok=True)

# ── helpers ──────────────────────────────────────────────────
def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {path}")

def make_index(rows, key_fn):
    d = {}
    for r in rows:
        k = key_fn(r)
        if k in d:
            raise ValueError(f"duplicate key {k}")
        d[k] = r
    return d

# ── load data ────────────────────────────────────────────────
print("Loading data...")
detail_rows = read_csv(ROOT / "results" / "full100_merged" / "detail.csv")
singlecore_rows = read_csv(ROOT / "results" / "singlecore_full100" / "singlecore.csv")
p3n1_rows = read_csv(ROOT / "results" / "p3_singlecore_full100" / "p3_n1_l2.csv")

# Index detail by (case, problem, cores, algorithm)
detail_by_key = {}
for r in detail_rows:
    key = (r["case"], int(r["problem"]), int(r["cores"]), r["algorithm"])
    detail_by_key[key] = r

sc_index = make_index(singlecore_rows, lambda r: r["case"])
p3n1_index = make_index(p3n1_rows, lambda r: r["case"])

CORES_LIST = [1, 2, 3, 4, 5]
CASES = sorted(sc_index.keys())

# ── Table 1: P1 speedup 1-5 ──────────────────────────────────
print("\n=== Table 1: P1 speedup ===")
p1_speedup_rows = []
for N in CORES_LIST:
    if N == 1:
        speeds = [1.0] * 100
    else:
        speeds = []
        for case in CASES:
            sc = int(sc_index[case]["makespan"])
            key = (case, 1, N, "vns")
            vns = int(detail_by_key[key]["makespan"])
            speeds.append(sc / vns)
    row = {
        "cores": N,
        "mean_speedup": round(statistics.mean(speeds), 4),
        "std_speedup": round(statistics.stdev(speeds), 4) if len(speeds) > 1 else 0,
        "median_speedup": round(statistics.median(speeds), 4),
        "min_speedup": round(min(speeds), 4),
        "max_speedup": round(max(speeds), 4),
    }
    p1_speedup_rows.append(row)
    print(f"  P1 N={N}: mean_speedup={row['mean_speedup']:.4f}")
write_csv(TABLES / "p1_speedup_1to5.csv", p1_speedup_rows,
          ["cores", "mean_speedup", "std_speedup", "median_speedup", "min_speedup", "max_speedup"])

# ── Table 2: P2 speedup 1-5 ──────────────────────────────────
print("\n=== Table 2: P2 speedup ===")
p2_speedup_rows = []
for N in CORES_LIST:
    if N == 1:
        speeds = [1.0] * 100
    else:
        speeds = []
        for case in CASES:
            sc = int(sc_index[case]["makespan"])
            key = (case, 2, N, "vns")
            vns = int(detail_by_key[key]["makespan"])
            speeds.append(sc / vns)
    row = {
        "cores": N,
        "mean_speedup": round(statistics.mean(speeds), 4),
        "std_speedup": round(statistics.stdev(speeds), 4) if len(speeds) > 1 else 0,
        "median_speedup": round(statistics.median(speeds), 4),
        "min_speedup": round(min(speeds), 4),
        "max_speedup": round(max(speeds), 4),
    }
    p2_speedup_rows.append(row)
    print(f"  P2 N={N}: mean_speedup={row['mean_speedup']:.4f}")
write_csv(TABLES / "p2_speedup_1to5.csv", p2_speedup_rows,
          ["cores", "mean_speedup", "std_speedup", "median_speedup", "min_speedup", "max_speedup"])

# ── Table 3: P3 L2 comparison 1-5 ────────────────────────────
print("\n=== Table 3: P3 L2 comparison ===")
p3_l2_rows = []
for N in CORES_LIST:
    if N == 1:
        speeds = []
        no_l2_makespans = []
        l2_makespans = []
        hit_rates = []
        for case in CASES:
            r = p3n1_index[case]
            nl = float(r["no_l2_makespan"])
            ll = float(r["l2_makespan"])
            no_l2_makespans.append(nl)
            l2_makespans.append(ll)
            speeds.append(float(r["l2_speedup"]))
            hit_rates.append(float(r["cache_hit_rate"]))
    else:
        speeds = []
        no_l2_makespans = []
        l2_makespans = []
        hit_rates = []
        for case in CASES:
            key_p2 = (case, 2, N, "vns")
            key_p3 = (case, 3, N, "vns")
            nl = float(detail_by_key[key_p2]["makespan"])
            ll = float(detail_by_key[key_p3]["makespan"])
            no_l2_makespans.append(nl)
            l2_makespans.append(ll)
            speeds.append(nl / ll)
            hit_rates.append(float(detail_by_key[key_p3].get("cache_hit_rate", 0) or 0))
    row = {
        "cores": N,
        "mean_no_l2_makespan": round(statistics.mean(no_l2_makespans), 1),
        "mean_l2_makespan": round(statistics.mean(l2_makespans), 1),
        "mean_l2_speedup": round(statistics.mean(speeds), 4),
        "std_l2_speedup": round(statistics.stdev(speeds), 4) if len(speeds) > 1 else 0,
        "mean_cache_hit_rate": round(statistics.mean(hit_rates), 4),
    }
    p3_l2_rows.append(row)
    print(f"  P3 N={N}: no-L2={row['mean_no_l2_makespan']:.0f}, L2={row['mean_l2_makespan']:.0f}, speedup={row['mean_l2_speedup']:.4f}")
write_csv(TABLES / "p3_l2_comparison_1to5.csv", p3_l2_rows,
          ["cores", "mean_no_l2_makespan", "mean_l2_makespan", "mean_l2_speedup", "std_l2_speedup", "mean_cache_hit_rate"])

# ── Table 4: Stage ablation ──────────────────────────────────
print("\n=== Table 4: Stage ablation ===")
ablation_rows = []
for p in [1, 2, 3]:
    for c in [2, 3, 4, 5]:
        base_mks = []
        multi_mks = []
        vns_mks = []
        multi_win = multi_tie = multi_loss = 0
        vns_win = vns_tie = vns_loss = 0
        for case in CASES:
            bk = detail_by_key.get((case, p, c, "baseline"))
            mk = detail_by_key.get((case, p, c, "multiseed"))
            vk = detail_by_key.get((case, p, c, "vns"))
            if not (bk and mk and vk):
                continue
            bm = int(bk["makespan"])
            mm = int(mk["makespan"])
            vm = int(vk["makespan"])
            base_mks.append(bm)
            multi_mks.append(mm)
            vns_mks.append(vm)
            if mm < bm: multi_win += 1
            elif mm == bm: multi_tie += 1
            else: multi_loss += 1
            if vm < mm: vns_win += 1
            elif vm == mm: vns_tie += 1
            else: vns_loss += 1
        mean_base = statistics.mean(base_mks)
        mean_multi = statistics.mean(multi_mks)
        mean_vns = statistics.mean(vns_mks)
        ablation_rows.append({
            "problem": p, "cores": c,
            "baseline_mean_makespan": round(mean_base, 1),
            "multiseed_mean_makespan": round(mean_multi, 1),
            "vns_mean_makespan": round(mean_vns, 1),
            "multiseed_vs_baseline_improvement": round((mean_base - mean_multi) / mean_base, 4),
            "vns_vs_multiseed_improvement": round((mean_multi - mean_vns) / mean_multi, 4),
            "multiseed_win": multi_win, "multiseed_tie": multi_tie, "multiseed_loss": multi_loss,
            "vns_win": vns_win, "vns_tie": vns_tie, "vns_loss": vns_loss,
        })
fields_ablation = ["problem", "cores", "baseline_mean_makespan", "multiseed_mean_makespan", "vns_mean_makespan",
                    "multiseed_vs_baseline_improvement", "vns_vs_multiseed_improvement",
                    "multiseed_win", "multiseed_tie", "multiseed_loss",
                    "vns_win", "vns_tie", "vns_loss"]
write_csv(TABLES / "stage_ablation.csv", ablation_rows, fields_ablation)

# ── figure_numbers.md ────────────────────────────────────────
print("\n=== figure_numbers.md ===")
lines = ["# Problem A 最终统计数字（论文引用来源）\n", f"## 数据来源\n",
         f"- full100 merged: detail.csv ({len(detail_rows)} rows)", f"- singlecore: {len(singlecore_rows)} cases",
         f"- P3 N1: {len(p3n1_rows)} cases\n", "## P1 加速比\n"]
for r in p1_speedup_rows:
    lines.append(f"N={r['cores']}: mean_speedup={r['mean_speedup']}")
lines.append("")
lines.append("## P2 加速比\n")
for r in p2_speedup_rows:
    lines.append(f"N={r['cores']}: mean_speedup={r['mean_speedup']}")
lines.append("")
lines.append("## P3 L2 对比\n")
for r in p3_l2_rows:
    lines.append(f"N={r['cores']}: no-L2={r['mean_no_l2_makespan']:.0f}, L2={r['mean_l2_makespan']:.0f}, speedup={r['mean_l2_speedup']}, hit={r['mean_cache_hit_rate']}")
lines.append("")
lines.append("## 算法阶段消融\n")
for r in ablation_rows:
    lines.append(f"P{r['problem']} N{r['cores']}: baseline->multiseed={r['multiseed_vs_baseline_improvement']:.4f} (w/t/l={r['multiseed_win']}/{r['multiseed_tie']}/{r['multiseed_loss']}), multiseed->vns={r['vns_vs_multiseed_improvement']:.4f} (w/t/l={r['vns_win']}/{r['vns_tie']}/{r['vns_loss']})")
(OUT / "figure_numbers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"  -> {OUT / 'figure_numbers.md'}")

# ── Appendix data ────────────────────────────────────────────
print("\n=== Appendix data ===")
# P1 appendix
p1_app = []
for case in CASES:
    for N in [2, 3, 4, 5]:
        key = (case, 1, N, "vns")
        r = detail_by_key[key]
        p1_app.append({"Case": case, "N": N, "Makespan": r["makespan"], "Added_Copy": r["added_copy_bytes"]})
write_csv(APPENDIX / "p1_per_case.csv", p1_app, ["Case", "N", "Makespan", "Added_Copy"])

# P2 appendix
p2_app = []
for case in CASES:
    for N in [2, 3, 4, 5]:
        key = (case, 2, N, "vns")
        r = detail_by_key[key]
        p2_app.append({"Case": case, "N": N, "Makespan": r["makespan"], "Added_Copy": r["added_copy_bytes"]})
write_csv(APPENDIX / "p2_per_case.csv", p2_app, ["Case", "N", "Makespan", "Added_Copy"])

# P3 appendix
p3_app = []
for case in CASES:
    # N=1
    n1 = p3n1_index[case]
    p3_app.append({"Case": case, "N": 1, "NoL2_Makespan": n1["no_l2_makespan"], "NoL2_AddedCopy": n1["added_copy_no_l2"],
                    "L2_Makespan": n1["l2_makespan"], "L2_AddedCopy": n1["added_copy_l2"],
                    "CacheHitRate": n1["cache_hit_rate"], "L2_Speedup": n1["l2_speedup"]})
    # N=2-5
    for N in [2, 3, 4, 5]:
        kp2 = (case, 2, N, "vns")
        kp3 = (case, 3, N, "vns")
        no_l2 = detail_by_key[kp2]
        l2 = detail_by_key[kp3]
        p3_app.append({"Case": case, "N": N,
                        "NoL2_Makespan": no_l2["makespan"], "NoL2_AddedCopy": no_l2["added_copy_bytes"],
                        "L2_Makespan": l2["makespan"], "L2_AddedCopy": l2["added_copy_bytes"],
                        "CacheHitRate": l2.get("cache_hit_rate", 0),
                        "L2_Speedup": round(int(no_l2["makespan"]) / int(l2["makespan"]), 4)})
write_csv(APPENDIX / "p3_per_case.csv", p3_app,
          ["Case", "N", "NoL2_Makespan", "NoL2_AddedCopy", "L2_Makespan", "L2_AddedCopy", "CacheHitRate", "L2_Speedup"])

# ── Spot check ───────────────────────────────────────────────
print("\n=== Spot check (3 random cases) ===")
check_cases = ["case_010", "case_050", "case_090"]
for case in check_cases:
    sc = int(sc_index[case]["makespan"])
    n = 4
    p1_vns = int(detail_by_key[(case, 1, n, "vns")]["makespan"])
    p2_vns = int(detail_by_key[(case, 2, n, "vns")]["makespan"])
    p3_vns = int(detail_by_key[(case, 3, n, "vns")]["makespan"])
    print(f"  {case} N={n}: SC={sc}, P1={p1_vns} (sp={sc/p1_vns:.4f}), P2={p2_vns} (sp={sc/p2_vns:.4f}), L2_sp={p2_vns/p3_vns:.4f}")

print("\n=== All done ===")
print(f"Tables:  {TABLES}")
print(f"Figures: {FIGURES}")
print(f"Appendix: {APPENDIX}")
print(f"Numbers: {OUT / 'figure_numbers.md'}")