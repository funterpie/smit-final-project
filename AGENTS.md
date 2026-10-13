# AGENTS.md — PR Risk Scorer

Instructions for any AI coding agent (Claude Code, Cursor, Copilot, etc.) working in this repo.

## What this project is
Just-in-time (JIT) software defect prediction. Given a git diff or commit range, output:
1. A weighted risk score (0-100), broken into named signals
2. RAG-retrieved evidence: similar past bug-inducing commits (or "no match found")
3. An LLM-generated plain-English explanation + suggestion
4. A human decision point: Approve / Request Changes / Escalate — logged to SQLite

**Never** output a bare classifier probability with no explanation. That's the whole point of this project — see IDEA.md.

## Environment
- Dev machine: **Ubuntu**. Assume Linux paths and tooling (no Windows-specific code).
- GPU training happens on **Google Colab free tier** — assume sessions can disconnect. Any training script must support resuming from a checkpoint.
- No paid APIs except Groq's free tier for the explanation LLM.

## Repo structure (target)
```
/data/              raw + processed ApacheJIT subset
/features/          diff feature extraction (PyDriller-based)
/models/
  baseline.py        logistic regression / random forest
  codebert.py         fine-tuning + inference
  risk_engine.py       weighted signal combiner
/rag/
  build_index.py       embeds curated bug-inducing commits (FAISS)
  retrieve.py           similarity search + threshold logic
/explain/
  llm_explain.py         Groq call, local-fallback if it fails
/cli/                  prscore CLI (typer/click) + git hook scripts
/dashboard/           React + TypeScript + Vite + Tailwind
/api/                  FastAPI backend serving the dashboard
/eval/                 AUC-PR, recall@k, false-positive-rate scripts
/notebooks/            Colab notebooks for CodeBERT fine-tuning
AGENTS.md, PLANNING.md, IDEA.md, RESOURCES.md   (this doc set)
```

## Coding conventions
- Python: type hints on every function signature. `black` formatting.
- No hardcoded paths — use a `config.py` or `.env` for dataset/model paths.
- Every model-facing function takes a diff as structured input (not a raw string dump) — see `features/` for the schema once defined.
- The LLM explanation function must **never** see the raw diff — only the computed signals + retrieved evidence. This is a stated design decision (privacy + hallucination control), don't "simplify" it by passing the raw diff.
- RAG retrieval must apply a similarity threshold and return `None`/explicit "no match" below it — don't force a top-k result if nothing is actually similar.

## What NOT to suggest
- Don't suggest embedding the full ApacheJIT dataset (100k+ commits) — too slow/large for a laptop demo. Use a curated subset of bug-inducing commits only.
- Don't suggest ChromaDB over FAISS without flagging the version-pinning/cross-OS packaging risk noted in PLANNING.md.
- Don't suggest ditching the baseline model "since CodeBERT is better" — the baseline vs. CodeBERT comparison is the core evaluation result for the report.
- Don't suggest a cloud-hosted always-on backend — this is meant to run locally/offline except for the one LLM explanation call.

## Priority order if scope needs cutting
1. Weighted risk engine + baseline/CodeBERT comparison (never cut)
2. CLI + git hook
3. LLM explanation layer
4. RAG evidence retrieval
5. React dashboard (cut first if behind schedule)

See PLANNING.md for the week-by-week schedule and IDEA.md for the full rationale.
