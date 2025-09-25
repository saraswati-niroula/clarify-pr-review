import argparse
import json
import sys
from collections import defaultdict
from typing import List, Dict

import pandas as pd
from gemini_utils import configure_gemini

REVIEW_PROMPT = """You are a senior code reviewer.

PR title:
{pr_title}

PR description:
{pr_text}

Clarifying Q&A:
{qa_block}

Write specific, actionable review comments or code suggestions.
- Be concise (bullets are fine).
- Call out risks, tests to add, and concrete code changes.
"""


# I/O helpers
def load_prs_jsonl(path: str, limit: int | None) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                sys.stderr.write(f"[WARN] Bad JSON line {i+1}: {e}\n")
    return rows


def parse_multiline_questions(cell: str) -> List[str]:
    """
    Accepts text like:
      Q1: Which envs...?
      Q2: Does this affect...?
    Returns ["Which envs...?", "Does this affect...?"]
    """
    if not isinstance(cell, str):
        return []
    qs = []
    for ln in cell.splitlines():
        ln = ln.strip()
        if ln.lower().startswith("q") and ":" in ln[:5]:
            ln = ln.split(":", 1)[1].strip()
        if ln.endswith("?") and len(ln) > 3:
            qs.append(ln)
    return qs


def parse_answers_wide(cell: str) -> List[str]:
    """
    Accepts text like:
      A1: Staging only
      A2: No mobile impact
    Returns ["Staging only", "No mobile impact"]
    """
    if not isinstance(cell, str):
        return []
    ans = []
    for ln in cell.splitlines():
        ln = ln.strip()
        if ln.lower().startswith("a") and ":" in ln[:5]:
            ln = ln.split(":", 1)[1].strip()
        if ln:
            ans.append(ln)
    return ans


def load_questions_tsv(path: str) -> Dict[str, dict]:
    """
    Expected header: id<TAB>pr_title<TAB>clarify_questions
    Returns map[id] -> {"pr_title": str, "questions": [q1, q2, ...]}
    """
    df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    required = {"id", "pr_title", "clarify_questions"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"{path} must have columns: id, pr_title, clarify_questions")
    out = {}
    for _, row in df.iterrows():
        pid = str(row["id"])
        out[pid] = {
            "pr_title": row["pr_title"],
            "questions": parse_multiline_questions(row["clarify_questions"]),
        }
    return out


def load_answers_any(path: str) -> Dict[str, List[str]]:
    """
    Supports two formats:

    Wide (header):
      id<TAB>answers
      1  <A1...\\nA2...>

    Tall (no header or id<TAB>answer rows):
      id<TAB>answer
      1  Staging only
      1  No mobile impact
    """
    df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    cols = [c.lower() for c in df.columns]

    if "answers" in cols and "id" in cols:
        id_col = df.columns[cols.index("id")]
        ans_col = df.columns[cols.index("answers")]
        amap = {}
        for _, row in df.iterrows():
            pid = str(row[id_col])
            amap[pid] = parse_answers_wide(row[ans_col])
        return amap

    if "id" in cols and ("answer" in cols or "answers" in cols):
        id_col = df.columns[cols.index("id")]
        ans_col = df.columns[cols.index("answer")] if "answer" in cols else df.columns[cols.index("answers")]
        amap = defaultdict(list)
        for _, row in df.iterrows():
            pid = str(row[id_col])
            val = str(row[ans_col]).strip()
            if val:
                amap[pid].append(val)
        return dict(amap)

    if len(df.columns) == 2 and set(cols) == {"0", "1"}:
        amap = defaultdict(list)
        for _, row in df.iterrows():
            pid = str(row.iloc[0])
            val = str(row.iloc[1]).strip()
            if val:
                amap[pid].append(val)
        return dict(amap)

    raise ValueError(
        f"Unrecognized answers format in {path}. "
        "Use either: (1) id<TAB>answers (newline-separated A1/A2), or (2) id<TAB>answer per row."
    )


def build_qa_block(numbered_questions: List[str], answers: List[str]) -> str:
    """
    Takes plain questions (no Q#: prefixes) and answers.
    Returns a nicely numbered Q/A block with Q1/A1 etc.
    """
    lines = []
    for i, q in enumerate(numbered_questions, start=1):
        a = answers[i - 1] if i - 1 < len(answers) else "[no answer provided]"
        lines.append(f"Q{i}: {q}\nA{i}: {a}")
    return "\n\n".join(lines)


def run_review(args):
    reviewer = configure_gemini(args.review_model)

    # Inputs
    pr_rows = load_prs_jsonl(args.input, args.limit)
    qmap = load_questions_tsv(args.questions)
    amap = load_answers_any(args.answers)

    wrote = 0
    with open(args.output, "w", encoding="utf-8") as fout:
        for obj in pr_rows:
            pid = str(obj.get("id"))
            pr_text = obj.get("prompt") or ""
            if not pid or not pr_text:
                continue

            pr_title = qmap.get(pid, {}).get("pr_title", "")
            questions = qmap.get(pid, {}).get("questions", [])
            answers = amap.get(pid, [])

            qa_block = build_qa_block(questions, answers)
            prompt = REVIEW_PROMPT.format(
                pr_title=pr_title or "(untitled)",
                pr_text=pr_text,
                qa_block=qa_block,
            )
            resp = reviewer.generate_content(prompt)
            review = (resp.text or "").strip()

            rec = {
                "id": pid,
                "pr_title": pr_title,
                "pr_text": pr_text,
                "questions": [f"Q{i+1}: {q}" for i, q in enumerate(questions)],
                "answers": [f"A{i+1}: {a}" for i, a in enumerate(answers)],
                "clarified_review": review,
            }
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            wrote += 1

    print(f"[REVIEW] wrote {wrote} rows -> {args.output}")


def main():
    ap = argparse.ArgumentParser(description="Clarified review (review step only).")
    ap.add_argument("--input", required=True, help="PR JSONL with {id, pr_text|prompt}")
    ap.add_argument("--questions", required=True, help="TSV with columns: id, pr_title, clarify_questions (newline-separated Q1/Q2)")
    ap.add_argument("--answers", required=True, help="Answers TSV (wide: id,answers with newlines; or tall: id,answer per row)")
    ap.add_argument("--output", required=True, help="Output JSONL for clarified reviews")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--review_model", default="gemini-1.5-flash")
    args = ap.parse_args()
    run_review(args)


if __name__ == "__main__":
    main()
