# Clarify-PR-Review

This repository contains the implementation and experiments for our assignment on **clarifying questions in pull request (PR) reviews**, inspired by [ClarifyCoder](https://arxiv.org/pdf/2504.16331).

---

## Repository Structure

```
clarify-pr-review/
├── data/
│   ├── pr_examples.jsonl      # PR descriptions (input)
│
├── results/
│   ├── baseline.jsonl         # Reviews without clarifications
│   ├── clarified.jsonl        # Reviews with clarifications
│   ├── comparison.tsv         # Side-by-side baseline vs clarified
│   ├── eval_scored.tsv        # Manual per-PR scores
│   ├── eval_summary.tsv       # Aggregated averages/deltas
│   ├── questions.tsv          # Clarifying questions generated
│   ├── answers.tsv            # Manual answers to clarifying questions
│   └── plots/                 # evaluation charts
│
├── src/
│   ├── baseline.py            # Baseline review script
│   ├── clarified.py           # Clarified review script
│   ├── clarifier.py           # Generate clarifying questions
│   ├── compare_reviews.py     # Merge baseline & clarified into TSV
│   ├── add_scoring_columns.py # Prepare eval scoring file
│   ├── summarize_eval.py      # Summarize metrics into eval_summary
│
├── notebooks/
│   └── ask_questions.ipynb    # Kaggle notebook for clarifier runs
│
├── report/
│   ├── report.tex             # IEEE LaTeX source
│
└── README.md
```

---

## Workflow

1. **Clarification phase**  
   - Run `ask-clarifying-questions.ipynb` notebook to generate clarifying questions for each PR.  
   - Save outputs → `results/questions.tsv`.

2. **Answering phase**  
   - Manually answer clarifying questions as a senior reviewer.  
   - Save outputs → `results/answers.tsv`.

3. **Review phase**  
   - Run `baseline.py` → `results/baseline.jsonl`  
   - Run `clarified.py` → `results/clarified.jsonl`

4. **Comparison**  
   - Merge reviews with `compare_reviews.py` → `results/comparison.tsv`.

5. **Evaluation**  
   - Create `results/eval_scored.tsv` and fill in scores for each PR (specificity, actionability, assumption identification, comment quality, suggestions).  
   - Run `summarize_eval.py` → `results/eval_summary.tsv`.

6. **Reporting**  
   - Results and discussion are written in `report/report.tex` (IEEE format).  
   - Final PDF is included as `report/report.pdf`.

---

## Evaluation Metrics

- **Specificity (1–5)** – how concrete the review is.  
- **Actionability (1–5)** – how easy it is to act on.  
- **Assumption Rate (0–100%)** – amount of speculation.  
- **Comment Quality (1–5)** – overall usefulness.  
- **Suggestions (count)** – number of distinct actionable suggestions.

---

## How to Reproduce

From the project root:

```bash
# 1. Generate clarifying questions
python src/clarifier.py --input data/pr_examples.jsonl --output results/questions.tsv

# 2. Answer questions manually (edit results/questions.tsv -> results/answers.tsv)

# 3. Run baseline reviewer
python src/baseline.py --input data/pr_examples.jsonl --output results/baseline.jsonl

# 4. Run clarified reviewer (with Q&A context)
python src/clarified.py --prs data/pr_examples.jsonl     --questions results/questions.tsv     --answers results/answers.tsv     --output results/clarified.jsonl

# 5. Merge baseline & clarified reviews
python src/compare_reviews.py     --baseline results/baseline.jsonl     --clarified results/clarified.jsonl     --output results/comparison.tsv

# 6. Prepare scoring file
python src/add_scoring_columns.py

# 7. Fill in results/eval_scored.tsv manually with scores

# 8. Summarize evaluation
python src/summarize_eval.py --input results/eval_scored.tsv --output results/eval_summary.tsv --print
```

---

## Setup

```bash
git clone https://github.com/saraswati-niroula/clarify-pr-review.git
cd clarify-pr-review
pip install -r requirements.txt
```

Dependencies include:
- `transformers`
- `peft`
- `pandas`
- `matplotlib`
- `google-generativeai`

> Note: Running the clarifier requires Kaggle (GPU). See `notebooks/ask_questions.ipynb`.

---

## Notes

- All **results are included** (`results/`) for reproducibility.  
- Large model weights (DeepSeek Coder + ClarifyCoder adapter) are not stored here.  
- To re-run clarifications, download weights from [Hugging Face](https://huggingface.co/jie-jw-wu/clarify-coder).
