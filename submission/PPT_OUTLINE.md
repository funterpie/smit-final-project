# Presentation Outline — 12 Slides

Use the existing values in `RESULTS.md`; do not add institutional or supervisor
details that are not supplied by the project owner.

## 1. PR Risk Scorer

- Just-in-time risk triage for Git commits.
- SMIT Batch 10 FYP; presenter and institutional details to be completed by the author.
- A score, interpretable signals, historical evidence, and a human decision.

Speaker notes: Open with the goal: help a reviewer prioritize attention while
keeping the final decision with a person.

Visual: `submission/charts/system_architecture.png`.

## 2. The review bottleneck

- Every change competes for limited review time.
- Large or cross-cutting changes can be difficult to triage consistently.
- JIT defect prediction estimates risk at change time.

Speaker notes: Define the task as prioritization, not automatic bug adjudication.

Visual: `submission/charts/system_architecture.png` (left-to-right input flow).

## 3. Why not ask only an LLM?

- A general LLM has no project-specific defect labels by default.
- The local scoring path is repeatable for the same structured features and model artifacts.
- The LLM explains derived metadata; it does not inspect or receive the raw diff.
- A reviewer remains responsible for the decision.

Speaker notes: The language model is a constrained explanation component, not
the defect predictor or decision maker.

Visual: `demo/screenshots/dashboard_selected_review.png` (manual capture outstanding).

## 4. Dataset and SZZ labels

- The evaluation uses the repository's processed ApacheJIT split.
- Test CSV: 1,200 commits; positive rate 26.5%.
- ApacheJIT provides commit-level JIT defect data; SZZ-style tracing links fixes to earlier bug-inducing changes.
- SZZ labels are heuristic and can be noisy.

Speaker notes: Distinguish the dataset's broader published size from this
project's stored test split. Do not claim an unverified training sample size.

Visual: `submission/charts/model_metrics.png` (test-set context in caption).

## 5. System architecture

- Git commit → PyDriller feature extraction.
- Heuristic plus optional LR/RF and CodeBERT signals.
- FAISS retrieval → constrained Groq or local explanation.
- FastAPI, React dashboard, and SQLite review/decision audit.

Speaker notes: Walk across the diagram and point out where raw source is not
sent to the explanation model.

Visual: `submission/charts/system_architecture.png`.

## 6. Features and risk engine

- Change size and file dispersion.
- Sensitive-path and test-file indicators.
- Author bug-rate feature and elapsed-time feature.
- Weighted named signals produce a capped 0–100 score.

Speaker notes: In the current live extractor, author bug rate is a 0.0
placeholder; identify that as a limitation rather than presenting it as
personalized history.

Visual: `demo/screenshots/dashboard_selected_review.png` (manual capture outstanding).

## 7. Heuristic, LR, RF, and CodeBERT

- Keep the heuristic, Logistic Regression, Random Forest, and CodeBERT comparison.
- The baselines learn from structured commit features.
- CodeBERT receives a structured text encoding of features, not the diff.
- On this split, CodeBERT and RF have close point estimates with overlapping intervals.

Speaker notes: Report the comparison without implying that the transformer is
proven superior.

Visual: `submission/charts/model_metrics.png`.

## 8. Retrieval and evidence

- A normalized embedding is searched in the FAISS index.
- The configured similarity threshold is applied before returning a match.
- A below-threshold query produces an explicit no-close-match state.
- Evidence is context, not proof that a defect will occur.

Speaker notes: Show the matched commit and similarity, then contrast it with
the no-close-match demo case.

Visual: `demo/outputs/no-close-match.txt` and `demo/screenshots/dashboard_selected_review.png` (manual capture outstanding).

## 9. Explanations and human review

- Groq receives only score, triggered signal names, and retrieved evidence summary.
- Missing key or API failure uses a local explanation.
- Approve, Request Changes, and Escalate decisions are stored in SQLite.
- The latest decision appears in review history and the audit log.

Speaker notes: Explain the privacy boundary and that the model never makes the
merge decision.

Visual: `demo/screenshots/dashboard_selected_review.png` (manual capture outstanding).

## 10. Live demonstration

- Run `make demo` with an isolated demo database.
- Compare the low, medium, and high synthetic commit cases.
- Open the dashboard and select a review to see signals, RAG, explanation, and decision controls.
- Use the no-close-match case to demonstrate threshold behavior.

Speaker notes: Follow `DEMO_SCRIPT.md`; keep the local fallback available for
network outages.

Visual: `demo/outputs/low.txt`, `medium.txt`, `high.txt`, and `no-close-match.txt`.

## 11. Evaluation results

- CodeBERT: AUC-PR 0.5314, AUC-ROC 0.7604, Recall@20% 0.4245.
- Random Forest: AUC-PR 0.5110, AUC-ROC 0.7423, Recall@20% 0.4182.
- Random Forest has the lowest FPR@0.5: 0.1020.
- The stored confidence intervals overlap; no paired significance test is available.

Speaker notes: Read the exact metrics from `RESULTS.md`; avoid saying CodeBERT
is statistically better.

Visual: `submission/charts/model_metrics.png`.

## 12. Limitations and next steps

- ApacheJIT is an open-source, Java-heavy context and may not generalize to every repository.
- Live author bug-rate history is not yet computed by the CLI extractor.
- RAG quality depends on the curated index and embedding availability.
- Expand project-local history, strengthen evaluation, and study paired model differences.

Speaker notes: End with the limits and the most concrete next engineering steps.

Visual: `submission/charts/system_architecture.png` with the extractor and
evaluation gaps highlighted verbally.
