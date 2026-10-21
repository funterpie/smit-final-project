# Demo runbook

From the project directory, seed the isolated presentation data:

```bash
make demo-seed
```

Start the API and dashboard in two terminals:

```bash
AUDIT_DB_PATH=demo/demo.db .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000
npm --prefix dashboard run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173/`. Reviews are already sorted highest risk first. Open them in this order:

1. `fix: prevent token refresh race condition` — high risk; point out the sensitive authentication files, large diff, and pending decision.
2. `fix: make payment capture idempotent` — high risk; show the payment signal and choose Escalate.
3. `refactor: centralize webhook delivery settings` — medium risk; show a cross-file change without tests and choose Request Changes.
4. `docs: clarify local setup and review commands` — low risk; show the small score and choose Approve.
5. `feat: add bounded retries to scheduled jobs` — the seeded no-match case; explain that the RAG panel honestly reports no close historical match.

Use the remaining pending rows to demonstrate a live decision. The explanation badge shows whether the text came from Groq or the local fallback; hovering a Local fallback badge reveals the short reason.
