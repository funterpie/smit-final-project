# PR Risk Scorer

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey)

**Just-in-time (JIT) software defect prediction**: given a Git commit, output a weighted risk score (0–100), similar past bug-inducing commits (RAG evidence), a plain-English explanation, and a logged human decision.

See [`IDEA.md`](IDEA.md) for the full rationale, [`PLANNING.md`](PLANNING.md) for the build plan, and [`AGENTS.md`](AGENTS.md) for AI agent conventions.

---

## Model Comparison Results

Evaluated on 1,200 test commits (26.5% positive rate) from the ApacheJIT dataset.

| Model | AUC-ROC | AUC-PR | Recall@20% | FPR@0.5 |
|---------------|---------|--------|------------|---------|
| Heuristic | 0.6345 | 0.3785 | 0.3711 | 0.1224 |
| Baseline LR | 0.6878 | 0.4520 | 0.3365 | 0.2846 |
| Baseline RF | 0.7423 | 0.5110 | 0.4182 | **0.1020** |
| **CodeBERT** | **0.7604** | **0.5314** | **0.4245** | 0.1281 |

**Key takeaway**: CodeBERT achieves the best AUC-ROC/AUC-PR, while Random Forest has the lowest false positive rate. See [`docs/eval_report.md`](docs/eval_report.md) for the full analysis.

---

## Quickstart

### 1. Clone & create virtual environment

```bash
git clone <repo-url>
cd pr-risk-scorer
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
make install                         # core runtime deps (pip install -e . + requirements.txt)
pip install -r requirements-dev.txt  # dev tools: pytest, black, ruff, mypy
pip install -r requirements-ml.txt   # ML: scikit-learn, torch, transformers, faiss-cpu, etc.
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env to set your GROQ_API_KEY (optional — local fallback works without it)
```

### 4. Prepare the dataset & train models

```bash
# Download and process the ApacheJIT dataset (one-time)
python scripts/prepare_dataset.py --sample 6000

# Train baseline models (Logistic Regression + Random Forest)
python scripts/train_baseline.py

# Build RAG index (embeds bug-inducing commits into FAISS)
python scripts/build_rag_index.py
```

### 5. (Optional) Fine-tune CodeBERT on Google Colab

Open [`notebooks/codebert_finetune.ipynb`](notebooks/codebert_finetune.ipynb) on Google Colab (free tier GPU). Upload the trained model to `models/artefacts/codebert/best_model/`.

### 6. Run the evaluation

```bash
python eval/evaluate.py --test-csv data/processed/test_features.csv --codebert
# Results saved to eval/results.json
```

---

## Usage

### CLI — score a commit

```bash
prscore review HEAD
prscore review <commit-sha>
prscore review main --repo /path/to/other/repo
prscore review HEAD --json           # raw JSON output
prscore review HEAD --no-rag         # skip RAG evidence
prscore review HEAD --no-explain     # skip LLM explanation
```

Example output:

```
──────────── PR Risk Scorer — HEAD ────────────

  Risk Score:  35/100

  Signal Breakdown
  ┌───────────────────────────┬────────┬───────────┬──────────────────────────────────────┐
  │ Signal                    │ Weight │ Triggered │ Description                          │
  ├───────────────────────────┼────────┼───────────┼──────────────────────────────────────┤
  │ large_diff                │ 25     │ ✗         │ Diff has 80 lines changed (>300)      │
  │ touches_sensitive_module  │ 30     │ ✗         │ …                                    │
  │ high_author_bug_rate      │ 20     │ ✗         │ …                                    │
  │ no_tests                  │ 15     │ ✓         │ No test files added or modified.      │
  │ high_dispersion           │ 10     │ ✓         │ Dispersion 3.5 (>3.0)                │
  │ ml_model_flag             │ 20     │ ✓         │ ML model prob 0.62 exceeds 0.5.      │
  └───────────────────────────┴────────┴───────────┴──────────────────────────────────────┘

  📎 Similar past bug commit (similarity=0.87)
    apache/kafka | +423/-89 lines | 12 files | dispersion=4.21

  ┌─ LLM Explanation [groq] ───────────────────────────┐
  │ This commit touches 3 files with moderate risk...   │
  └─────────────────────────────────────────────────────┘

  ⚠ Human decision required: run `prscore decide` to log your review.
```

### CLI — log and view decisions

```bash
prscore decide <commit-hash> <score> approve
prscore decide <commit-hash> <score> escalate -n "Needs senior review"
prscore log --limit 10
```

### API — FastAPI backend

```bash
uvicorn api.main:app --reload --port 8000
# Endpoints: POST /review, GET /decisions, POST /decisions, GET /health
```

### Run tests

```bash
make test
```

### Lint + format

```bash
make lint     # ruff check
make format   # black
```

---

## Git Hook — Pre-Push Risk Check

Install the pre-push hook to automatically score commits before pushing:

```bash
cp scripts/git_hook.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

The hook runs `prscore review` on each commit being pushed. If any commit scores ≥ 60, the push is blocked. Override with `git push --no-verify`.

Configure the threshold via the `RISK_THRESHOLD` environment variable (default: 60).

---

## Project Structure

```
config.py              Central settings loader (reads .env)
features/
  schema.py            CommitFeatures pydantic model
  extract.py           PyDriller-based feature extraction
models/
  risk_engine.py       Weighted signal combiner (heuristic + ML blend)
  baseline.py          Logistic regression + random forest (sklearn)
  codebert.py          CodeBERT fine-tuning (Colab) + inference
rag/
  build_index.py       FAISS index builder (sentence-transformers)
  retrieve.py          Similarity search with threshold (returns None below threshold)
explain/
  llm_explain.py       Groq LLM explanation layer + local fallback
cli/
  main.py              prscore CLI entry point (typer + rich)
api/
  main.py              FastAPI backend (review, decisions, health)
  audit.py             SQLite audit log (decisions table)
eval/
  evaluate.py          AUC-PR, recall@20%, FPR evaluation
  results.json         Latest evaluation results
scripts/
  prepare_dataset.py   ApacheJIT → processed feature CSVs
  train_baseline.py    Train LR + RF baselines
  build_rag_index.py   Embed bug commits → FAISS index
  git_hook.sh          Pre-push git hook
notebooks/
  codebert_finetune.ipynb   Colab fine-tuning notebook
docs/
  eval_report.md       Full evaluation report with analysis
data/
  raw/                 ApacheJIT dataset
  processed/           Train/test CSVs + bug-inducing JSONL
tests/                 pytest suite
```

---

## Design Decisions

- **No hardcoded paths** — everything through `config.py` / `.env`.
- **LLM never sees the raw diff** — only computed signals + RAG evidence (privacy + hallucination control).
- **RAG returns `None` below the similarity threshold** — no forced top-k results.
- **GPU training on Colab free tier** — scripts support checkpoint resume for disconnects.
- **Groq API is the only cloud call** — scoring + retrieval are fully local/offline.
- **Baseline vs CodeBERT comparison is the core evaluation result** — neither is removed.

---

## Groq API Key Setup

The LLM explanation layer uses [Groq](https://groq.com) (free tier). To enable it:

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. Add to your `.env` file:
   ```
   GROQ_API_KEY=gsk_your_api_key_here
   ```

Without a key, `prscore` gracefully falls back to a locally-generated explanation (no API call made).
