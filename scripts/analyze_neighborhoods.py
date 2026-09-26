# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Analyze N1-N8 neighborhood efficiency from trials.jsonl and diagnostics."""
import json
import csv
from collections import defaultdict
from pathlib import Path


def analyze_neighborhoods(dev2_dir: str, output_csv: str, output_md: str):
    """Aggregate neighborhood statistics from all trials.jsonl files in development_v2."""
    dev2 = Path(dev2_dir)
    stats = defaultdict(lambda: dict(
        generated=0, evaluated=0, improved=0, total_reduction=0.0,
        total_eval_time=0.0, cases_improved=set(), cases_touched=set()))

    # Collect per-neighborhood per-case details
    details = []

    for job_dir in sorted(dev2.glob("case_*_p*_n*")):
        trials_file = job_dir / "trials.jsonl"
        if not trials_file.exists():
            continue
        case = job_dir.name
        baseline = None
        with trials_file.open("r", encoding="utf-8") as f:
            trials = [json.loads(line) for line in f if line.strip()]

        # Find baseline makespan
        for t in trials:
            if t["name"] == "baseline" and t.get("valid"):
                baseline = t["makespan"]
                break

        for t in trials:
            name = t.get("name", "")
            if not name.startswith("N"):
                continue
            try:
                n_idx = int(name[1:])
            except ValueError:
                continue

            key = f"N{n_idx}"
            stats[key]["evaluated"] += 1
            stats[key]["cases_touched"].add(case)
            stats[key]["total_eval_time"] += t.get("seconds", 0)

            if t.get("improved") and t.get("valid"):
                stats[key]["improved"] += 1
                stats[key]["cases_improved"].add(case)
                # Reduction relative to baseline or previous incumbent
                # Use a fixed reference: reduction from baseline across all trials
                reduction = 0
                if baseline:
                    # Estimate: the reduction attributed to this trial
                    # We track cumulative improvements per neighborhood
                    pass
                stats[key]["total_reduction"] += t.get("makespan", 0)

            details.append(dict(
                case=case, name=name, improved=t.get("improved", False),
                makespan=t.get("makespan", 0),
                eval_seconds=t.get("seconds", 0),
                communication_bytes=t.get("communication_bytes", 0),
                score=t.get("score", 0)))

    # Build per-case incumbent progression
    case_improvements = defaultdict(list)
    for job_dir in sorted(dev2.glob("case_*_p*_n*")):
        trials_file = job_dir / "trials.jsonl"
        if not trials_file.exists():
            continue
        with trials_file.open("r", encoding="utf-8") as f:
            trials = [json.loads(line) for line in f if line.strip()]
        best = None
        for t in trials:
            if not t.get("valid", False):
                continue
            ms = t["makespan"]
            name = t.get("name", "")
            if best is None or ms < best[0]:
                # Record improvement and which neighborhood caused it
                if best is not None:
                    reduction = best[0] - ms
                    n_key = name if name.startswith("N") else "seed"
                    case_improvements[n_key].append(reduction)
                best = (ms, name)

    # Supplement with neighborhood_diagnostics.json
    diag_file = dev2 / "neighborhood_diagnostics.json"
    if diag_file.exists():
        diag = json.loads(diag_file.read_text(encoding="utf-8"))
        for n_key, d in diag.items():
            stats[n_key]["evaluated_diag"] = d.get("evaluated", 0)
            stats[n_key]["improved_diag"] = d.get("improved", 0)
            stats[n_key]["total_eval_time_diag"] = d.get("seconds", 0)

    # Write CSV
    rows = []
    for n_key in sorted(stats.keys(), key=lambda k: int(k[1:])):
        s = stats[n_key]
        evals = s.get("evaluated_diag", s["evaluated"])
        impr = s.get("improved_diag", s["improved"])
        etime = s.get("total_eval_time_diag", s["total_eval_time"])
        improvement_rate = impr / max(1, evals)
        mean_reduction = sum(case_improvements.get(n_key, [])) / max(1, impr)
        gain_per_eval = sum(case_improvements.get(n_key, [])) / max(1, evals)
        gain_per_second = sum(case_improvements.get(n_key, [])) / max(0.001, etime)
        rows.append(dict(
            neighborhood=n_key,
            evaluated=evals,
            improved=impr,
            improvement_rate=round(improvement_rate, 4),
            total_makespan_reduction=sum(case_improvements.get(n_key, [])),
            mean_reduction_when_successful=round(mean_reduction, 1),
            evaluator_time=round(etime, 3),
            gain_per_eval=round(gain_per_eval, 2),
            gain_per_second=round(gain_per_second, 2),
            cases_touched=len(s["cases_touched"]),
            cases_improved=len(s["cases_improved"])))

    output_dir = Path(output_csv).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    # Write Markdown
    md_lines = ["# Neighborhood Efficiency Analysis (from development_v2)", ""]
    md_lines.append("| Neighborhood | Evaluated | Improved | Rate | Total Reduction | Mean Reduction | Eval Time (s) | Gain/Eval | Gain/s | Cases Touched | Cases Improved |")
    md_lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md_lines.append(f"| {r['neighborhood']} | {r['evaluated']} | {r['improved']} | {r['improvement_rate']:.1%} | "
                        f"{r['total_makespan_reduction']:.0f} | {r['mean_reduction_when_successful']:.0f} | "
                        f"{r['evaluator_time']:.1f} | {r['gain_per_eval']:.1f} | {r['gain_per_second']:.1f} | "
                        f"{r['cases_touched']} | {r['cases_improved']} |")

    md_lines.append("")
    md_lines.append("## Summary Findings")
    md_lines.append("")
    # Rank by gain_per_eval
    ranked = sorted(rows, key=lambda r: r["gain_per_eval"], reverse=True)
    md_lines.append("### Ranked by gain per evaluator call:")
    for i, r in enumerate(ranked, 1):
        md_lines.append(f"{i}. **{r['neighborhood']}**: {r['gain_per_eval']:.1f} makespan reduction per eval "
                        f"({r['gain_per_second']:.1f} per second), rate={r['improvement_rate']:.1%}")
    md_lines.append("")
    md_lines.append("### Recommended priority for Round 3:")
    high = [r for r in ranked if r["gain_per_second"] > 0.5 or r["improvement_rate"] > 0.15]
    medium = [r for r in ranked if r["improvement_rate"] > 0.05 and r not in high]
    low = [r for r in ranked if r not in high and r not in medium]
    md_lines.append(f"- **High priority** (keep/expand budget): {', '.join(r['neighborhood'] for r in high) or 'none'}")
    md_lines.append(f"- **Medium priority** (maintain): {', '.join(r['neighborhood'] for r in medium) or 'none'}")
    md_lines.append(f"- **Low priority** (reduce budget, keep exploration minimum): {', '.join(r['neighborhood'] for r in low) or 'none'}")

    Path(output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(output_md).write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Wrote {output_csv} ({len(rows)} neighborhoods)")
    print(f"Wrote {output_md}")
    return rows


if __name__ == "__main__":
    import sys
    dev2 = sys.argv[1] if len(sys.argv) > 1 else "results/development_v2"
    out_csv = sys.argv[2] if len(sys.argv) > 2 else "results/neighborhood_analysis.csv"
    out_md = sys.argv[3] if len(sys.argv) > 3 else "docs/neighborhood_analysis.md"
    analyze_neighborhoods(dev2, out_csv, out_md)