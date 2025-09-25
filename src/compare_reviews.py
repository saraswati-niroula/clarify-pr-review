import argparse
import pandas as pd
import json
import csv


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description="Compare baseline vs clarified reviews")
    ap.add_argument("--baseline", required=True, help="Path to baseline.jsonl")
    ap.add_argument("--clarified", required=True, help="Path to clarified.jsonl")
    ap.add_argument("--output", required=True, help="Path to write comparison.tsv")
    args = ap.parse_args()

    baseline_df = load_jsonl(args.baseline)
    clarified_df = load_jsonl(args.clarified)

    merged = pd.merge(
        baseline_df[["id", "prompt", "baseline_review"]],
        clarified_df[["id", "clarified_review"]],
        on="id",
        how="inner"
    )

    merged = merged.applymap(
        lambda x: x.replace("\n", "\\n").strip() if isinstance(x, str) else x
    )

    # Save without quoting unless absolutely necessary
    merged.to_csv(
        args.output,
        sep="\t",
        index=False,
        quoting=csv.QUOTE_NONE,
        escapechar="\\",
        lineterminator="\n"
    )

    print(f"Wrote clean TSV with {len(merged)} rows -> {args.output}")


if __name__ == "__main__":
    main()
