# HANDOFF.md — PR Risk Scorer Agent Handoff State

> **Updated**: 2026-10-21T19:50 PKT
> **Agent**: Starting Phase 1

## Current Phase/Task

**Phase 1, Task 1.2** — Verify `.env.example` and test with/without Groq key.

## Last Completed

- **1.1** — Full test suite (64/64 pass), `tsc --noEmit` clean, `npm run build` succeeds (162 KB bundle). No failures.

## In Progress / Half-Done

- 12 files have uncommitted changes from prior sessions (api/audit.py, api/main.py, cli/main.py, tests/test_audit.py, .gitignore, requirements.txt, requirements-ml.txt, README.md, docs/eval_report.md, eval/results.json, Makefile, dashboard/README.md). All tests pass with these changes. Need to commit.
- `.env.example` already exists with correct fields. Next: verify local fallback works without Groq key.

## Known Issues

- No `install-hook` CLI command exists yet — needs to be added (Task 1.5).
- CLI `log` command shows decisions but the column mapping uses `.get()` fallbacks (works but needs confirmation with real data).
- No `/demo` directory yet.
- No `/submission` directory yet.
- Dashboard has never been tested end-to-end with a real API + real reviews.

## Key Commands

```bash
# Activate venv
cd /home/funter-pie/Desktop/Final\ project && source .venv/bin/activate

# Run tests
pytest tests/ -v

# TypeScript check
cd dashboard && npx tsc --noEmit

# Dashboard build
cd dashboard && npm run build

# Start API
uvicorn api.main:app --reload --port 8000

# Start dashboard dev server
cd dashboard && npm run dev

# CLI
prscore review HEAD --no-rag --no-explain
prscore review HEAD
prscore log
prscore decide <hash> <score> approve
```

## Decisions Made

1. **Two-table audit schema** (`reviews` + `decisions` with FK) — replaces the old single `decisions` table. All tests updated.
2. **CORS restricted** to `localhost:5173` / `127.0.0.1:5173` — was `*`.
3. **Diff hash stored, raw diff never stored** — privacy by design per AGENTS.md.
4. **CLI `--note` flag** replaces `--explanation` on the `decide` command.
5. **`GROQ_API_KEY` defaults to empty string** — triggers local fallback, never crashes.

## Next 3 Actions

1. Verify local fallback works without Groq key (Task 1.2).
2. Test end-to-end: CLI review → API → dashboard → decision → audit log (Task 1.3).
3. Verify `pip install -e .` and `prscore --help` work from clean state (Task 1.4).
