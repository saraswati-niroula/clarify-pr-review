import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "results" / "eval.tsv"
DST = BASE / "results" / "eval_scored.tsv"

new_fields = [
    "specificity_baseline", "specificity_clarified",
    "actionability_baseline", "actionability_clarified",
    "assumption_identification_baseline", "assumption_identification_clarified",
    "comment_quality_baseline", "comment_quality_clarified",
    "suggestions_baseline", "suggestions_clarified",
]

with open(SRC, encoding="utf-8") as fin:
    r = csv.DictReader(fin, delimiter="\t")
    rows = list(r)
    # keep only id, pr_title, and the new fields
    fields = ["id", "pr_title"] + new_fields

with open(DST, "w", newline="", encoding="utf-8") as fout:
    w = csv.DictWriter(fout, fieldnames=fields, delimiter="\t")
    w.writeheader()
    for row in rows:
        clean = {"id": row.get("id", ""), "pr_title": row.get("pr_title", "")}
        for f in new_fields:
            clean[f] = ""
        w.writerow(clean)

print(f"Wrote {DST} with {len(rows)} rows and simplified fields.")
