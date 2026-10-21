# Five-Minute Demo Script

## Before presenting

From the project root, use a demo-only database for both processes:

```bash
AUDIT_DB_PATH=demo/demo.db GROQ_API_KEY= .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
AUDIT_DB_PATH=demo/demo.db GROQ_API_KEY= npm --prefix dashboard run dev -- --host 127.0.0.1
```

Generate current synthetic examples and real CLI outputs:

```bash
PRSCORER_DEMO_DB=demo/demo.db make demo
```

Open `http://127.0.0.1:5173/`. The demo cases are synthetic commits created in
temporary Git repositories; the scores are produced by the project pipeline.

## Spoken walkthrough

**0:00–0:40 — Problem.** “This tool helps reviewers prioritize Git changes by
estimating just-in-time defect risk. It does not decide whether a change may be
merged.”

**0:40–1:20 — Pipeline.** “The CLI extracts structured commit features, adds
the weighted risk signals and available model scores, retrieves similar
historical evidence when it clears the configured threshold, and generates an
explanation. The raw diff is not passed to the explanation model.”

**1:20–2:25 — Three cases.** Run `make demo` and open the saved outputs:

```bash
cat demo/outputs/low.txt
cat demo/outputs/medium.txt
cat demo/outputs/high.txt
cat demo/outputs/no-close-match.txt
```

“These cases are synthetic, not ApacheJIT records. The observed run produced
0/100 for low, 45/100 for medium, and 80/100 for high. The fourth case raises
the retrieval threshold to 0.9999 so a below-threshold result is omitted.”

**2:25–3:35 — Dashboard.** “The dashboard reads persisted reviews from the
demo SQLite database. I select the high-risk case to show its score, each
signal contribution, retrieved evidence, and local fallback explanation. I
can choose Approve, Request Changes, or Escalate; each choice is audited and
remains after refresh.”

**3:35–4:25 — Evaluation.** “On the stored 1,200-commit test split, CodeBERT's
AUC-PR is 0.5314 and Random Forest's is 0.5110. Their marginal bootstrap
intervals overlap; no paired difference test is stored, so I do not claim a
statistically significant CodeBERT improvement.”

**4:25–5:00 — Limits.** “The test data are ApacheJIT and the live CLI currently
uses a placeholder author bug rate. RAG can return no match, and a Groq outage
uses a local explanation. The human reviewer remains responsible for the
decision.”

## Groq/network backup

The demo runner clears `GROQ_API_KEY`, so it uses the deterministic local
fallback by design. If testing the Groq path separately, use a valid key in a
private `.env`; never place it in a command transcript or screenshot. If the
network or Groq is unavailable, continue the presentation using the local
fallback outputs. If the embedding model is not cached, scoring and local
explanations still run; RAG can report no match.
