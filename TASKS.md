# TASKS.md — PR Risk Scorer Finalization Checklist

> **Resume behavior**: At session start, read this file + HANDOFF.md + AGENTS.md.
> Continue from the first unchecked `[ ]` task. Do not redo `[x]` items.

## Phase 1: Verify and Fix

- [x] 1.1 Run full test suite, `tsc --noEmit`, `npm run build` — fix any failures
- [ ] 1.2 Create `.env.example` — confirm app works WITH Groq key AND without key/internet (local fallback must show score + signals + evidence)
- [ ] 1.3 End-to-end flow: `prscore review HEAD~1` → API → dashboard shows review → Approve/Request Changes/Escalate → row in SQLite audit log. Fix every break.
- [ ] 1.4 Confirm install from clean venv: `pip install -e .` then `prscore --help`. Add pyproject.toml entry point if missing.
- [ ] 1.5 Confirm git pre-commit/pre-push hook installs and fires (add `prscore install-hook` if it doesn't exist).

## Phase 2: Demos

- [ ] 2.1 Create `/demo` with 3 realistic sample diffs/commits: LOW, MEDIUM, HIGH risk. Include one case where RAG returns "no close match found."
- [ ] 2.2 Create `demo/run_demo.sh` (and `make demo`) that runs all 3 through CLI and prints output.
- [ ] 2.3 Seed the audit log with demo reviews so dashboard is populated on first launch.
- [ ] 2.4 Save real outputs as `demo/outputs/*.txt`, plus dashboard screenshots in `demo/screenshots/` (or document exact screenshots to take manually).

## Phase 3: Polish

- [ ] 3.1 Dashboard: clean empty/loading/error states, readable score colors, visible "signals + evidence + explanation + decision buttons" card per PR.
- [ ] 3.2 README: one-page quickstart (install → set key → run demo → open dashboard), architecture diagram in text, honest limitations.
- [ ] 3.3 Remove dead code, scratch files, hardcoded paths. Run `black` on Python code.

## Phase 4: Handoff Pack (create /submission)

- [ ] 4.1 `submission/guide.html` — self-contained HTML how-to-use page (install, setup, CLI, hook, API, dashboard, troubleshooting).
- [ ] 4.2 `submission/RESULTS.md` — all real numbers from `eval/results.json` with honest CI analysis.
- [ ] 4.3 `submission/PPT_OUTLINE.md` — 10-12 slide deck outline with titles, bullets, speaker notes, screenshot/chart refs. Generate results charts (PNG) into `submission/charts/`.
- [ ] 4.4 `submission/REPORT.md` — full report: Abstract → Conclusion. Only real results.
- [ ] 4.5 `submission/DEMO_SCRIPT.md` — 5-minute spoken demo script with exact commands and backup plan.
- [ ] 4.6 `submission/VIVA_QA.md` — 15 examiner questions with honest answers.

## Phase 5: Ship

- [ ] 5.1 Run all tests again — everything green.
- [ ] 5.2 Commit in logical commits with clear messages, push to origin.
- [ ] 5.3 Tag release v1.0.
- [ ] 5.4 Final summary: what passed, what could not be verified, exact demo command.
