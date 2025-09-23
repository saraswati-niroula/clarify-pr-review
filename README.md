This repo implements a small experiment testing whether explicit clarification
improves LLM-based PR review.  
Pipeline:  
1. Baseline review (PR description → Gemini).  
2. Clarified review (ClarifyCoder questions → developer answers → Gemini).  
3. Compare baseline vs clarified reviews.

## Usage
```bash
python src/baseline.py
python src/clarified.py
python src/add_scoring_columns.py
python src/summarize_eval.py

Repo structure

data/ — input examples (e.g. examples.jsonl).

src/ — scripts.

results/ — generated outputs.

report/ — LaTeX paper.
