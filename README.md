# PR Risk Scorer

**A just-in-time defect-risk triage tool for Git commits.** PR Risk Scorer extracts change-level features, calculates an interpretable score, optionally retrieves similar historical commits, and provides an explanation with a human review workflow.

The score helps reviewers prioritize attention. It is not a guarantee that a commit contains a defect, and it does not make merge decisions.

> **FYP project:** SMIT Batch 10

## Features

- **Commit analysis:** extract change size, file dispersion, test-file and sensitive-path indicators, and other structured features.
- **Risk scoring:** combine named heuristic signals with available Logistic Regression, Random Forest, and CodeBERT model outputs.
- **Historical context:** search a local FAISS index and show a match only when it meets the configured similarity threshold.
- **Explanations:** use Groq with derived risk metadata and retrieved evidence, or fall back to a local explanation. Raw code diffs are not sent to Groq.
- **Review audit:** inspect reviews in a React dashboard and record approve, request-changes, or escalate decisions in SQLite.
- **CLI, API, and demo:** run a review from the command line, use the FastAPI service, or try the reproducible synthetic demo cases.

## Evaluation snapshot

The checked-in evaluation artifacts report results on 1,200 test commits, with a 26.5% positive rate.

| Model | AUC-ROC | AUC-PR | Recall@20% | FPR@0.5 |
|---|---:|---:|---:|---:|
| Heuristic | 0.6345 | 0.3785 | 0.3711 | 0.1224 |
| Logistic Regression | 0.6878 | 0.4520 | 0.3365 | 0.2846 |
| Random Forest | 0.7423 | 0.5110 | 0.4182 | **0.1020** |
| CodeBERT | **0.7604** | **0.5314** | **0.4245** | 0.1281 |

The available bootstrap intervals cover AUC-PR and Recall@20% only. The stored analysis does not test paired differences between models, so these point estimates do not establish that CodeBERT significantly outperforms Random Forest. See [submission/RESULTS.md](submission/RESULTS.md) and [docs/eval_report.md](docs/eval_report.md) for definitions, intervals, and interpretation.

## Quick start

### Requirements

- Python 3.11 or newer
- Node.js and npm for the dashboard
- Git

### Install and configure

```bash
git clone https://github.com/funterpie/smit-final-project.git
cd smit-final-project
python3 -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
```

Set `GROQ_API_KEY` in `.env` to enable Groq explanations. Leave it empty to use the local fallback. The `.env` file contains private configuration and must not be committed.

### Review a commit

```bash
prscore review HEAD
prscore review HEAD --json --no-rag
prscore review HEAD --no-explain
```

Each review is saved to the configured SQLite audit database. JSON output includes the review ID. To record a decision from the CLI:

```bash
prscore decide <commit-sha> <score> approve
prscore decide <commit-sha> <score> request_changes --note "Add a regression test"
prscore decide <commit-sha> <score> escalate --note "Needs security review"
prscore log --limit 10
```

For command details, run `prscore --help` or `prscore review --help`.

## Run the dashboard

Start the API from the project root:

```bash
.venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, install the dashboard dependencies and start Vite:

```bash
npm --prefix dashboard ci
npm --prefix dashboard run dev -- --host 127.0.0.1
```

Open [http://127.0.0.1:5173/](http://127.0.0.1:5173/). Check API status at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health). Available API routes include `GET /health`, `POST /review`, `GET /reviews`, `POST /decisions`, `GET /audit`, and `GET /metrics`.

## Run the demo

The demo creates temporary Git repositories for three synthetic risk cases and a no-close-RAG-match case. It scores them through the real CLI pipeline and writes outputs and review records to the demo database.

```bash
PRSCORER_DEMO_DB=demo/demo.db make demo
```

Then start the API with that same database:

```bash
AUDIT_DB_PATH=demo/demo.db GROQ_API_KEY= .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Start the dashboard as described above and open [http://127.0.0.1:5173/](http://127.0.0.1:5173/). Demo cases and outputs are in [demo/](demo/README.md). Use a separate path for demo data to keep it isolated from the default audit database.

## Architecture

```text
Git commit
    ↓
PyDriller feature extraction
    ↓
Heuristic risk engine + optional LR / RF / CodeBERT outputs
    ↓
Thresholded local FAISS retrieval
    ↓
Groq explanation from derived metadata, or local fallback
    ↓
FastAPI → React dashboard → SQLite reviews and human decisions
```

The explanation component receives the score, triggered signal names, and evidence summary; it does not receive the raw diff. If no indexed example meets the configured similarity threshold, the review reports that no close match was found and continues without evidence.

## Pre-push hook (optional)

Install the hook in this repository with:

```bash
prscore install-hook --repo . --hook pre-push
```

The installer refuses to overwrite an existing hook. The hook blocks if scoring fails or if a pushed commit reaches `RISK_THRESHOLD` (default `60`). A recorded decision does not itself bypass the risk threshold.

## Development

```bash
make test       # Python tests
make lint       # Ruff checks
make format     # Black formatting
npm --prefix dashboard run build
```

## Limitations

- The live CLI currently uses `0.0` as the author bug-rate feature; it does not yet calculate repository-specific author history.
- Evaluation results come from the checked-in ApacheJIT split and may not generalize to other projects.
- SZZ-derived labels can be noisy. The score is for review prioritization, not a calibrated guarantee.
- Retrieval depends on the local index and embedding model. A missing index or below-threshold result does not prevent scoring.
- Groq needs a valid key and network access. Without it, explanations use the local fallback.

## Project resources

- [Evaluation results](submission/RESULTS.md)
- [Full project report](submission/REPORT.md)
- [Five-minute demo script](submission/DEMO_SCRIPT.md)
- [Presentation outline](submission/PPT_OUTLINE.md)
- [Viva questions and answers](submission/VIVA_QA.md)
- [Usage guide](submission/guide.html)
- [Project rationale](IDEA.md) · [Development plan](PLANNING.md)

## Credits

| Credit | Attribution |
|---|---|
| Project author | [@funterpie](https://github.com/funterpie) |
| Project | PR Risk Scorer — SMIT Batch 10 Final Year Project |
| Evaluation dataset | [ApacheJIT](https://arxiv.org/abs/2203.00101) |
| Core methods and tools | PyDriller, scikit-learn, CodeBERT, FAISS, FastAPI, React, and SQLite |
