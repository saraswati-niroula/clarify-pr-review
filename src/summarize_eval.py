import argparse
import csv
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE / "results" / "eval_scored.tsv"
DEFAULT_OUTPUT = BASE / "results" / "eval_summary.tsv"


CORE_FIELDS = [
    ("specificity_baseline", float), ("specificity_clarified", float),
    ("actionability_baseline", float), ("actionability_clarified", float),
    ("assumption_identification_baseline", float), ("assumption_identification_clarified", float),
    ("comment_quality_baseline", float), ("comment_quality_clarified", float),
    ("suggestions_baseline", float), ("suggestions_clarified", float),
]


def to_num(val, cast=float):
    if val is None: return math.nan
    s = str(val).strip()
    if s == "": return math.nan
    if s.endswith("%"):
        try:
            return cast(s[:-1])
        except Exception:
            return math.nan
    try:
        return cast(s)
    except Exception:
        return math.nan


def nanmean(nums):
    xs = [x for x in nums if not math.isnan(x)]
    return sum(xs)/len(xs) if xs else math.nan


def main():
    ap = argparse.ArgumentParser(description="Summarize eval_scored.tsv into dataset-level metrics.")
    ap.add_argument("--input", default=DEFAULT_INPUT, help="Path to eval_scored.tsv")
    ap.add_argument("--output", default=DEFAULT_OUTPUT, help="Where to write the summary TSV")
    ap.add_argument("--print", action="store_true", help="Print summary to stdout")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        raise SystemExit(f"[error] file not found: {src}")

    # read rows
    with src.open(encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        rows = list(r)

    # collect columns
    cols = {name: [] for name, _ in CORE_FIELDS}
    n_rows = len(rows)

    for row in rows:
        for name, caster in CORE_FIELDS:
            cols[name].append(to_num(row.get(name, ""), caster))

    means = {name: nanmean(vals) for name, vals in cols.items()}

    # compute deltas (clarified - baseline)
    deltas = {
        "delta_specificity": means["specificity_clarified"] - means["specificity_baseline"] if not any(
            math.isnan(means[x]) for x in ("specificity_clarified","specificity_baseline")
        ) else math.nan,
        "delta_actionability": means["actionability_clarified"] - means["actionability_baseline"] if not any(
            math.isnan(means[x]) for x in ("actionability_clarified","actionability_baseline")
        ) else math.nan,
        "delta_assumption_identification": means["assumption_identification_clarified"] - means["assumption_identification_baseline"] if not any(
            math.isnan(means[x]) for x in ("assumption_identification_clarified","assumption_identification_baseline")
        ) else math.nan,
        "delta_comment_quality": means["comment_quality_clarified"] - means["comment_quality_baseline"] if not any(
            math.isnan(means[x]) for x in ("comment_quality_clarified","comment_quality_baseline")
        ) else math.nan,
        "delta_suggestions": means["suggestions_clarified"] - means["suggestions_baseline"] if not any(
            math.isnan(means[x]) for x in ("suggestions_clarified","suggestions_baseline")
        ) else math.nan,
    }

    # assemble a single-row summary
    summary_row = {
        "n_samples": n_rows,
        # means
        "specificity_baseline_mean": means["specificity_baseline"],
        "specificity_clarified_mean": means["specificity_clarified"],
        "actionability_baseline_mean": means["actionability_baseline"],
        "actionability_clarified_mean": means["actionability_clarified"],
        "assumption_identification_baseline_mean": means["assumption_identification_baseline"],  # 0-100 scale
        "assumption_identification_clarified_mean": means["assumption_identification_clarified"],
        "comment_quality_baseline_mean": means["comment_quality_baseline"],
        "comment_quality_clarified_mean": means["comment_quality_clarified"],
        "suggestions_baseline_mean": means["suggestions_baseline"],
        "suggestions_clarified_mean": means["suggestions_clarified"],
        # deltas
        **deltas,
    }

    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_row.keys()), delimiter="\t")
        w.writeheader()
        w.writerow({k: ("" if isinstance(v, float) and math.isnan(v) else v) for k, v in summary_row.items()})

    if args.print:
        print(f"n_samples\t{summary_row['n_samples']}")
        print(f"specificity (base/clar)\t{summary_row['specificity_baseline_mean']:.2f}\t{summary_row['specificity_clarified_mean']:.2f}\tΔ={summary_row['delta_specificity']:.2f}")
        print(f"actionability (base/clar)\t{summary_row['actionability_baseline_mean']:.2f}\t{summary_row['actionability_clarified_mean']:.2f}\tΔ={summary_row['delta_actionability']:.2f}")
        print(f"assumption% (base/clar)\t{summary_row['assumption_identification_baseline_mean']:.1f}\t{summary_row['assumption_identification_clarified_mean']:.1f}\tΔ={summary_row['delta_assumption_identification']:.1f}")
        print(f"comment_quality (base/clar)\t{summary_row['comment_quality_baseline_mean']:.2f}\t{summary_row['comment_quality_clarified_mean']:.2f}\tΔ={summary_row['delta_comment_quality']:.2f}")
        print(f"suggestions (base/clar)\t{summary_row['suggestions_baseline_mean']:.2f}\t{summary_row['suggestions_clarified_mean']:.2f}\tΔ={summary_row['delta_suggestions']:.2f}")
        print(f"\nWrote summary -> {outp}")


if __name__ == "__main__":
    main()
