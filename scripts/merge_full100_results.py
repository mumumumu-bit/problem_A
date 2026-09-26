# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Merge only completed full100 job records and summarize per-case ratios."""
import argparse
import csv
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = tuple(ROOT / "results" / f"full100_teammate_{name}" for name in "ABC")
DETAIL_FIELDS = ("case", "problem", "cores", "algorithm", "makespan", "added_copy_bytes",
                 "spill_bytes", "cache_hit_rate", "runtime", "evaluations", "source", "scale")
SUMMARY_FIELDS = ("problem", "cores", "algorithm", "count", "mean_normalized_makespan",
                  "mean_speedup_vs_baseline", "mean_runtime")


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path, default=DEFAULT_INPUTS)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "full100_merged")
    args = parser.parse_args(argv)
    if len(args.inputs) != 3:
        parser.error("provide exactly three result directories: A B C")

    merged = {}
    for result_dir in args.inputs:
        if not result_dir.exists():
            continue
        for job_file in sorted(result_dir.glob("case_*_p*_n*/job.json")):
            try:
                rows = json.loads(job_file.read_text(encoding="utf-8"))["rows"]
            except (KeyError, TypeError, json.JSONDecodeError):
                continue
            if {row.get("algorithm") for row in rows} != {"baseline", "multiseed", "vns"}:
                continue
            for row in rows:
                normalized = {field: row.get(field, "") for field in DETAIL_FIELDS}
                key = (normalized["case"], int(normalized["problem"]), int(normalized["cores"]), normalized["algorithm"])
                if key in merged and merged[key] != normalized:
                    raise ValueError(f"conflicting duplicate result for {key}")
                merged[key] = normalized

    detail = [merged[key] for key in sorted(merged)]
    write_csv(args.output / "detail.csv", detail, DETAIL_FIELDS)

    baselines = {(row["case"], int(row["problem"]), int(row["cores"])): int(row["makespan"])
                 for row in detail if row["algorithm"] == "baseline"}
    summary = []
    groups = sorted({(int(row["problem"]), int(row["cores"]), row["algorithm"]) for row in detail})
    for problem, cores, algorithm in groups:
        group = [row for row in detail
                 if int(row["problem"]) == problem and int(row["cores"]) == cores and row["algorithm"] == algorithm]
        ratios = [(int(row["makespan"]) / baselines[row["case"], problem, cores],
                   baselines[row["case"], problem, cores] / int(row["makespan"])) for row in group]
        summary.append({
            "problem": problem,
            "cores": cores,
            "algorithm": algorithm,
            "count": len(group),
            "mean_normalized_makespan": statistics.mean(value[0] for value in ratios),
            "mean_speedup_vs_baseline": statistics.mean(value[1] for value in ratios),
            "mean_runtime": statistics.mean(float(row["runtime"]) for row in group),
        })
    write_csv(args.output / "summary.csv", summary, SUMMARY_FIELDS)
    print(f"merged {len(detail)} rows from {len(detail) // 3} completed jobs into {args.output}")


if __name__ == "__main__":
    main()
