# RESOURCES.md — PR Risk Scorer

## Dataset
- **ApacheJIT** — just-in-time defect prediction dataset, 100k+ labelled commits from Apache projects. Search "ApacheJIT dataset github" for the current repo/paper link (verify the exact URL before use — check it's still the maintained version).

## Core libraries
| Purpose | Library |
|---|---|
| Git/diff parsing | `pydriller`, `GitPython` |
| Baseline ML | `scikit-learn` |
| Code-aware model | `transformers` (HuggingFace) + `microsoft/codebert-base` |
| Fine-tuning environment | Google Colab (free tier) — mount Google Drive for checkpointing |
| Vector search (RAG) | `faiss-cpu` (primary) or `chromadb` (version-pin if used) |
| LLM explanation | `langchain` + Groq API (free tier) |
| CLI | `typer` or `click` |
| Local storage | `sqlite3` (stdlib) |
| Dashboard | React + TypeScript + Vite + Tailwind CSS |
| Backend API | `fastapi` + `uvicorn` |
| Packaging | `pyinstaller` (or `nuitka`), GitHub Actions build matrix (`windows-latest`, `macos-latest`, `ubuntu-latest`) |

## Key concepts to read up on before Week 1-2
- **Just-in-time (JIT) software defect prediction** — the research area this project sits in
- **SZZ algorithm** — how ApacheJIT's bug-inducing-commit labels were generated; know this so you can describe methodology in the report
- **AUC-PR vs. AUC-ROC** — why PR is the right metric for imbalanced defect data
- **Recall@k** — the metric to explain the tool's value to a non-ML examiner

## Reference architecture to point to when writing the report
CyberShield AI (an approved Batch-10 project) uses a similar detect → explain (LLM + evidence citation) → human-approves pattern, applied to SOC/network data instead of code. Useful to cite as precedent for "human-in-the-loop AI system" framing.

## Internal docs (this project's own file set)
- `IDEA.md` — the core idea, rationale, and why this isn't "just ask an LLM"
- `PLANNING.md` — week-by-week build plan and cut order
- `AGENTS.md` — conventions for any AI coding assistant working in this repo
- `guide.html` — visual getting-started walkthrough
