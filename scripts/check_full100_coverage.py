# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Report completed, missing and failed jobs across the three full100 shards."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = tuple(ROOT / "results" / f"full100_teammate_{name}" for name in "ABC")
CASE_FILES = tuple(ROOT / "configs" / f"full100_{name}.txt" for name in "ABC")
PROBLEMS = (1, 2, 3)
CORES = (2, 3, 4, 5)
ALGORITHMS = {"baseline", "multiseed", "vns"}


def load_cases(path):
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def job_state(directory, case, problem, cores):
    if not directory.exists():
        return "missing"
    job_file = directory / "job.json"
    if not job_file.exists():
        return "failed"
    try:
        rows = json.loads(job_file.read_text(encoding="utf-8"))["rows"]
        algorithms = {
            row["algorithm"]
            for row in rows
            if row["case"] == case and int(row["problem"]) == problem and int(row["cores"]) == cores
        }
        return "completed" if algorithms == ALGORITHMS else "failed"
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return "failed"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path, default=DEFAULT_INPUTS)
    parser.add_argument("--missing-output", type=Path, default=ROOT / "results" / "full100_missing_jobs.txt")
    args = parser.parse_args(argv)
    if len(args.inputs) != 3:
        parser.error("provide exactly three result directories: A B C")

    shards = [(name, load_cases(case_file), result_dir) for name, case_file, result_dir in zip("ABC", CASE_FILES, args.inputs)]
    all_cases = [case for _, cases, _ in shards for case in cases]
    if len(all_cases) != 100 or len(set(all_cases)) != 100:
        raise ValueError("full100 case lists must contain each of 100 cases exactly once")

    counts = {(problem, cores): {state: 0 for state in ("completed", "missing", "failed")}
              for problem in PROBLEMS for cores in CORES}
    incomplete = []
    for owner, cases, result_dir in shards:
        for case in cases:
            for problem in PROBLEMS:
                for cores in CORES:
                    job_dir = result_dir / f"{case}_p{problem}_n{cores}"
                    state = job_state(job_dir, case, problem, cores)
                    counts[problem, cores][state] += 1
                    if state != "completed":
                        incomplete.append(f"{case} P{problem} N{cores} {owner} {state}")

    print("problem cores completed missing failed")
    for problem in PROBLEMS:
        for cores in CORES:
            item = counts[problem, cores]
            print(f"P{problem} N{cores} {item['completed']} {item['missing']} {item['failed']}")
    completed = sum(item["completed"] for item in counts.values())
    print(f"total {completed} / 1200 jobs")
    args.missing_output.parent.mkdir(parents=True, exist_ok=True)
    args.missing_output.write_text("\n".join(incomplete) + ("\n" if incomplete else ""), encoding="utf-8")
    print(f"missing list: {args.missing_output}")


if __name__ == "__main__":
    main()
