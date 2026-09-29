# PR Risk Scorer

Just-in-time (JIT) software defect prediction: given a Git commit, output a weighted risk score (0–100), similar past bug-inducing commits (RAG evidence), a plain-English explanation, and a logged human decision.

See `IDEA.md` for the full rationale, `PLANNING.md` for the week-by-week build plan, and `AGENTS.md` for conventions followed by every AI agent working in this repo.

---

## Setup

### 1. Clone + create virtual environment

```bash
git clone <repo-url>
cd pr-risk-scorer
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
make install        # core runtime deps (pip install -e . + requirements.txt)
pip install -r requirements-dev.txt   # dev/CI tools: pytest, black, ruff, mypy
# Optional — only needed for ML model training/inference:
pip install -r requirements-ml.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env: set GROQ_API_KEY if you have one; other defaults are fine
```

---

## Running

### CLI — score a commit

```bash
prscore review HEAD
prscore review <commit-sha>
prscore review main --repo /path/to/other/repo
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
  └───────────────────────────┴────────┴───────────┴──────────────────────────────────────┘

  RAG evidence:  not yet implemented (Week 3)
  LLM explain:   not yet implemented (Week 3)
  ⚠ Human decision required: Approve / Request Changes / Escalate
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

## Project structure

```
config.py              central settings loader (reads .env)
features/
  schema.py            CommitFeatures pydantic model
  extract.py           PyDriller-based feature extraction (stub → Week 1)
models/
  risk_engine.py       weighted signal combiner (real implementation)
  baseline.py          logistic regression / random forest (stub → Week 1)
  codebert.py          CodeBERT fine-tuning + inference (stub → Week 2)
rag/
  build_index.py       FAISS index builder (stub → Week 3)
  retrieve.py          similarity search with threshold (stub → Week 3)
explain/
  llm_explain.py       Groq LLM explanation layer (stub → Week 3)
cli/
  main.py              prscore CLI entry point
api/
  audit.py             SQLite audit log (decisions table)
eval/                  AUC-PR, recall@k scripts (→ Week 4)
notebooks/             Colab fine-tuning notebooks (→ Week 2)
dashboard/             React + TypeScript dashboard (→ Week 4, cut first if behind)
data/                  raw/ and processed/ ApacheJIT subsets
tests/                 pytest suite
```

---

## Development notes

- **No hardcoded paths** — everything goes through `config.py` / `.env`.
- **LLM never sees the raw diff** — only computed signals + RAG evidence.
- **RAG returns `None` below the similarity threshold** — no forced top-k.
- GPU training happens on Google Colab free tier; scripts must support checkpoint resume.
- Groq API is the only paid/cloud call; scoring + retrieval are fully local.
