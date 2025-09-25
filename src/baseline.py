import argparse
import json
from gemini_utils import configure_gemini

BASELINE_PROMPT = """You are a senior code reviewer.
Write a concise review for the following PR:
{pr_text}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="gemini-1.5-flash")
    args = ap.parse_args()

    model = configure_gemini(args.model)

    with open(args.input, "r", encoding="utf-8") as fin, \
         open(args.output, "w", encoding="utf-8") as fout:
        for line in fin:
            obj = json.loads(line)
            pid = str(obj.get("id"))
            pr_text = obj.get("pr_text") or obj.get("prompt") or ""
            resp = model.generate_content(BASELINE_PROMPT.format(pr_text=pr_text))
            review = (resp.text or "").strip()
            fout.write(json.dumps({"id": pid, "prompt": pr_text, "baseline_review": review}) + "\n")


if __name__ == "__main__":
    main()
