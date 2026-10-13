# IDEA.md — PR Risk Scorer

## Problem
A developer opens a pull request. Nobody knows how risky the change is until someone reads every line. Small teams can't review everything in depth — risky changes slip through, junior devs' PRs get rubber-stamped or over-scrutinized at random.

This is the research problem of **just-in-time (JIT) software defect prediction**: predicting, at commit time, whether a code change will later be linked to a bug.

## Core principle
A bare `1` or `0` is not enough — it's what separates a "Need Improvement" ML project from an "Approved" one. Every score must come with:
1. A **weighted signal breakdown**, not an opaque probability
2. **RAG evidence** — a similar past bug-inducing commit, or an honest "no match found"
3. An **LLM explanation** in plain English with a concrete suggestion
4. A **human decision** — Approve / Request Changes / Escalate — always human-final, logged

## Why it's not "just ask Claude/Gemini to review the diff"
- It's a **calibrated probability** from a model trained on ~100k real labelled commits (ApacheJIT, SZZ methodology) — empirical pattern-matching against real defect history, not an LLM's stylistic opinion.
- It's **reproducible** — same diff, same score, every time. An LLM asked twice can give different answers.
- It's **free and fast at scale** — milliseconds, local, no per-call API cost, unlike running an LLM over every commit in a busy repo.
- It **personalizes to the codebase** — author bug-rate and file history are specific to this repo's real past, which a general LLM reviewing a diff in isolation doesn't have.
- The LLM's job here is intentionally small: the model predicts, the LLM only translates the prediction into English. That's a defensible division of labor, not a redundant wrapper.

## Users
| Who | Need |
|---|---|
| Senior developer / reviewer | Ranked list — review the riskiest PRs first |
| Junior / intermediate developer | A warning before pushing, to self-check |
| Small team, no dedicated QA | A safety net without hiring or heavy CI setup |

## Architecture (one line each)
```
diff → feature extraction → baseline + CodeBERT → weighted risk engine
     → RAG evidence retrieval → LLM explanation → reviewer decision → audit log
```

## Data
**ApacheJIT** — public, 100k+ labelled commits from major Apache projects, purpose-built for JIT defect prediction, labelled via the standard SZZ algorithm. Use a curated subset for training/RAG, not the full set (see PLANNING.md, Week 1-3 notes).

## Evaluation
- AUC-PR (not accuracy — labels are imbalanced)
- Recall-at-20% — "if reviewers only check the riskiest 20% of commits, what fraction of real bugs do they catch?"
- Baseline vs. CodeBERT comparison — proves the extra complexity is earned
- False-positive rate — a tool that flags everything gets ignored
- Small human-rated check that LLM explanations actually match the signals/evidence (no hallucination)

## Known limitations (state these plainly in the report)
- ApacheJIT is Java-heavy open-source code, not necessarily like an arbitrary codebase
- Explanation layer depends on a cloud LLM call (Groq) — scoring/retrieval are fully local, only the explanation sentence isn't
- RAG evidence is only as good as the curated subset — a genuinely novel bug pattern may return "no match found," which is correct behavior, not a failure

## Status
Submitted and marked **Approved** on the SMIT Batch-10 project sheet. Working title "PR Risk Scorer" — public-facing name TBD (avoiding "Alphaguard," which collides with an existing disinfectant brand and an AI compliance company).
