# PLANNING.md — PR Risk Scorer

Solo build · ~50-60 hours · Ubuntu dev machine · Colab free tier · deadline soft ~1 month (extendable if results are strong)

## Week 1 — Data & baseline (~14 hrs)
- Download ApacheJIT, understand commit structure + labels
- Feature extraction with PyDriller/GitPython: diff size, files touched, author bug-history, test presence
- Train logistic regression + random forest baseline → first AUC-PR number
- Build the weighted risk engine (named signals, fixed weights) on top of baseline features
- **Checkpoint:** a script that takes a commit and prints a risk score with signal breakdown

## Week 2 — CodeBERT model (~14 hrs)
- Fine-tune CodeBERT on Colab free tier — **checkpoint to Google Drive every epoch** (sessions disconnect)
- Train on a curated subset (tens of thousands of commits, not the full 100k+)
- Blend CodeBERT score into the weighted engine
- Compare CodeBERT vs. baseline: AUC-PR + recall-at-20% — this comparison is the core research contribution
- **Checkpoint:** a saved, working CodeBERT model that beats the baseline, numbers written down

## Week 3 — Explain layer, CLI, packaging (~16 hrs)
- Day 1: sanity-check RAG first — throwaway script, embed ~500 sample commits, confirm matches make sense
- Build real RAG index (curated subset only) with FAISS, plus similarity threshold
- Wire LLM explanation call (Groq free tier) with local-fallback if the API fails
- Build the CLI (`prscore review`) and git pre-commit/pre-push hook
- PyInstaller build on Ubuntu first, confirm clean run
- GitHub Actions build matrix for Windows + macOS, **with a smoke-test step inside the CI job itself** (run the binary on the runner) since there's no physical Mac/Windows machine to test on
- **Checkpoint:** packaged binary scoring a diff with signals + evidence + explanation, running on 2+ of 3 OSes

## Week 4 — Dashboard, evaluation, report (~14 hrs)
- React + TypeScript dashboard: score list, review card, Approve/Request Changes/Escalate, reading the SQLite audit log — **cut first if behind schedule**
- Full evaluation: AUC-PR, recall-at-20%, false-positive rate, small human-rated explanation-quality check
- Write the report: problem, methodology, dataset, architecture, evaluation results, limitations
- Rehearse the demo with 2-3 real diffs showing different risk levels
- **Checkpoint:** demo + written report with real numbers + packaged binaries, all present

## Cut order if time runs short (bottom first)
1. Dashboard
2. RAG evidence
3. LLM explanation
4. *(never cut)* weighted score + CLI + baseline/CodeBERT comparison

Deadline is soft — if week 3-4 results look strong, ask for the extension rather than rushing the report. If behind by end of week 2, cut the dashboard immediately.
