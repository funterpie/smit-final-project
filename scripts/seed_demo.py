"""Create an isolated, reproducible set of real-pipeline demo reviews."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo"
DEFAULT_DB = DEMO_DIR / "demo.db"


@dataclass(frozen=True)
class Case:
    slug: str
    message: str
    files: dict[str, str]
    decision: str | None = None
    no_match: bool = False


def _module(title: str, blocks: int, prefix: str) -> str:
    """Build valid, readable synthetic Python changes with realistic names."""
    lines = [f'"""{title}."""', "from __future__ import annotations", "", "from typing import Any", ""]
    for n in range(blocks):
        lines.extend([
            f"def {prefix}_{n}(record: dict[str, Any]) -> dict[str, Any]:",
            '    """Validate and normalize one workflow record."""',
            '    result = dict(record)',
            f'    result["stage"] = "{prefix}-{n}"',
            '    result["validated"] = bool(result.get("id"))',
            '    result["attempt"] = int(result.get("attempt", 0))',
            '    if result["attempt"] < 0:',
            '        raise ValueError("attempt cannot be negative")',
            '    return result',
            "",
        ])
    return "\n".join(lines)


def cases() -> list[Case]:
    return [
        Case("docs-cli", "docs: clarify local setup and review commands", {
            "README.md": "# PR Risk Scorer\n\n## Local review\n\nCreate a virtual environment, install the project dependencies, and run `prscore review HEAD --repo .`. The review reports risk signals and any historical evidence available in the configured index.\n",
        }, "approve"),
        Case("test-backed-refactor", "refactor: simplify token claim parsing", {
            "src/parsing/claims.py": '"""Small helpers for claim parsing."""\n\ndef normalize_claims(claims):\n    return {str(key).strip(): value for key, value in claims.items()}\n',
            "tests/test_claims.py": 'from src.parsing.claims import normalize_claims\n\ndef test_normalize_claims_trims_keys():\n    assert normalize_claims({" sub ": "u1"}) == {"sub": "u1"}\n',
        }, "approve"),
        Case("payment-retry", "fix: prevent duplicate refund retries", {
            "src/payment/refund_service.py": _module("Refund retry validation", 5, "validate_refund"),
        }, "request_changes"),
        Case("cross-service-config", "refactor: centralize webhook delivery settings", {
            "api/webhooks.py": _module("Webhook request handling", 4, "parse_webhook"),
            "config/delivery.py": _module("Delivery configuration", 4, "load_delivery"),
            "workers/dispatcher.py": _module("Webhook dispatch", 4, "dispatch_event"),
            "payment/outbox.py": _module("Payment webhook outbox", 4, "save_event"),
        }, "approve"),
        Case("scheduler-window", "feat: add bounded retries to scheduled jobs", {
            "src/scheduler/retry_policy.py": _module("Scheduled job retry policy", 5, "retry_job"),
            "src/payment/retry_policy.py": _module("Payment retry policy", 5, "retry_payment"),
        }, None, no_match=True),
        Case("auth-refresh", "fix: prevent token refresh race condition", {
            "src/auth/refresh.py": _module("Refresh token rotation", 10, "rotate_token"),
            "src/api/session.py": _module("Session refresh endpoint", 10, "refresh_session"),
            "src/storage/session_store.py": _module("Session persistence", 10, "save_session"),
            "src/config/security.py": _module("Authentication policy", 10, "check_policy"),
        }, "escalate"),
        Case("payment-ledger", "fix: make payment capture idempotent", {
            "src/payment/capture.py": _module("Payment capture workflow", 10, "capture_payment"),
            "src/api/checkout.py": _module("Checkout capture endpoint", 10, "submit_checkout"),
            "src/storage/ledger.py": _module("Ledger persistence", 10, "write_ledger"),
            "src/workers/settlement.py": _module("Settlement processing", 10, "settle_payment"),
        }, None),
        Case("auth-session", "feat: rotate session credentials on privilege change", {
            "src/auth/session_manager.py": _module("Session credential rotation", 10, "rotate_session"),
            "src/auth/permissions.py": _module("Permission refresh", 10, "refresh_permissions"),
            "src/api/admin.py": _module("Administrative session endpoints", 10, "update_admin"),
            "src/storage/credentials.py": _module("Credential persistence", 10, "store_credential"),
        }, None),
    ]


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def _write_case(repo: Path, case: Case) -> str:
    (repo / "README.md").write_text("# Synthetic demo repository\n\nGenerated for a local presentation.\n")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "PR Risk Scorer Demo")
    _git(repo, "config", "user.email", "demo@example.invalid")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-qm", "chore: initialize synthetic repository")
    for name, content in case.files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", case.message)
    return _git(repo, "rev-parse", "HEAD")


def _reset_database(db_path: Path) -> None:
    resolved = db_path.resolve()
    if not resolved.is_relative_to(DEMO_DIR.resolve()):
        raise ValueError(f"Demo database must stay inside {DEMO_DIR}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-wal", "-shm"):
        Path(f"{resolved}{suffix}").unlink(missing_ok=True)


def main() -> None:
    os.environ.setdefault("AUDIT_DB_PATH", str(DEFAULT_DB))
    db_path = Path(os.environ["AUDIT_DB_PATH"])
    _reset_database(db_path)
    env_base = os.environ.copy()
    env_base["AUDIT_DB_PATH"] = str(db_path.resolve())
    created: list[tuple[Case, str, int, dict[str, object]]] = []

    with tempfile.TemporaryDirectory(prefix="prscore-demo-") as tmp:
        for case in cases():
            repo = Path(tmp) / case.slug
            repo.mkdir()
            commit = _write_case(repo, case)
            env = env_base.copy()
            if case.no_match:
                env["SIMILARITY_THRESHOLD"] = "0.9999"
            else:
                env.setdefault("SIMILARITY_THRESHOLD", "0.75")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "cli.main", "review", commit,
                     "--repo", str(repo), "--json"],
                    cwd=ROOT, env=env, check=True, capture_output=True, text=True,
                )
            except subprocess.CalledProcessError as exc:
                print(exc.stdout, end="")
                print(exc.stderr, end="", file=sys.stderr)
                raise
            from api.audit import insert_decision, list_reviews

            review = next(row for row in list_reviews(db_path) if row["commit_ref"] == commit)
            if case.decision:
                insert_decision(db_path, int(review["id"]), case.decision,
                                f"Recorded synthetic demo decision for {case.slug}.")
                review = next(row for row in list_reviews(db_path) if row["commit_ref"] == commit)
            created.append((case, commit, int(review["id"]), review))

    print("ID  SCORE  RAG                         SOURCE          DECISION             COMMIT MESSAGE")
    for case, commit, review_id, review in sorted(created, key=lambda row: int(row[3]["score"]), reverse=True):
        evidence = review.get("evidence")
        rag = f"match {evidence['similarity']:.3f}" if evidence else "no close match"
        decision = review.get("decision") or "pending"
        source = str(review.get("explanation_source", ""))
        print(f"{review_id:<3} {review['score']:>3}/100  {rag:<27} {source:<15} {decision:<20} {case.message}")

    scores = [int(item[3]["score"]) for item in created]
    print(f"\nCreated {len(created)} reviews in {db_path}; risk counts: "
          f"low={sum(s < 20 for s in scores)}, medium={sum(30 <= s <= 60 for s in scores)}, "
          f"high={sum(s >= 70 for s in scores)}.")
    print("RAG evidence shown above comes only from the configured index; no match was fabricated.")


if __name__ == "__main__":
    main()
