import csv
import argparse
import pathlib


def read_qs(path):
    q = {}
    with open(path, encoding="utf-8") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for r in rdr:
            _id = int(r["id"])
            qstr = (r["clarify_questions"] or "").strip()
            qstr = " | ".join([s.strip() for s in qstr.replace("\r\n","\n").split("\n") if s.strip()])
            q[_id] = qstr
    return q


def read_ans(path):
    a = {}
    with open(path, encoding="utf-8") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for r in rdr:
            _id = int(r["id"])
            ans = (r["answer"] or "").strip()
            ans = " ".join(ans.replace("\r\n","\n").split("\n"))  # one line
            a[_id] = ans
    return a


def main(qs_path, ans_path, out_path):
    qmap = read_qs(qs_path)
    amap = read_ans(ans_path)
    ids = sorted(set(qmap.keys()) | set(amap.keys()))
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["id","clarify_questions","answer","clarified_suggestion","baseline_suggestion"]
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        for i in ids:
            w.writerow({
                "id": i,
                "clarify_questions": qmap.get(i, ""),
                "answer": amap.get(i, ""),
                "clarified_suggestion": "",
                "baseline_suggestion": "",
            })


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True)
    ap.add_argument("--answers", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    main(args.questions, args.answers, args.out)
