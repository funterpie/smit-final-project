"""cli/main.py — prscore CLI entry point (fully wired).

Usage:
    prscore review <commit-ish> [--repo PATH] [--no-rag] [--no-explain] [--json]
    prscore log [--limit N]
    prscore decide <commit-hash> <score> <decision>
    prscore install-hook [--repo PATH] [--hook pre-commit|pre-push]
"""

from __future__ import annotations

import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import AUDIT_DB_PATH, GROQ_API_KEY, INDEX_DIR, SIMILARITY_THRESHOLD
from features.schema import CommitFeatures
from models.risk_engine import RiskReport, compute_risk

if TYPE_CHECKING:
    from rag.retrieve import RetrievedEvidence

app = typer.Typer(
    name="prscore",
    help="PR Risk Scorer — just-in-time software defect prediction.",
    add_completion=False,
)
console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _try_baseline_prob(features: CommitFeatures) -> Optional[float]:
    """Attempt to get baseline probability; return None if model not trained yet."""
    try:
        from models.baseline import predict_baseline

        return predict_baseline(features, model="rf")
    except (FileNotFoundError, ImportError):
        return None


def _try_codebert_prob(features: CommitFeatures) -> Optional[float]:
    """Attempt to get CodeBERT probability; return None if model not available."""
    try:
        from models.codebert import predict_codebert

        return predict_codebert(features)
    except (FileNotFoundError, ImportError):
        return None


def _try_rag_evidence(features: CommitFeatures) -> Optional[RetrievedEvidence]:
    """Attempt RAG evidence retrieval; return None if index not built yet."""
    try:
        from rag.retrieve import retrieve_evidence

        return retrieve_evidence(
            features, index_dir=str(INDEX_DIR), threshold=SIMILARITY_THRESHOLD
        )
    except Exception:
        return None


def _try_explain(report: RiskReport, evidence: Optional[RetrievedEvidence]) -> Optional[object]:
    """Attempt LLM explanation; return None on any failure."""
    try:
        from explain.llm_explain import explain_risk

        return explain_risk(report, evidence, groq_api_key=GROQ_API_KEY)
    except Exception:
        return None


def _print_report(
    commit_ish: str,
    report: RiskReport,
    evidence: Optional[RetrievedEvidence],
    explanation: Optional[object],
    as_json: bool = False,
    review_id: int | None = None,
) -> None:
    """Print a formatted risk report to stdout."""
    if as_json:
        out = report.as_dict()
        out["commit"] = commit_ish
        out["review_id"] = review_id
        if evidence is not None:
            out["evidence"] = {
                "commit_hash": evidence.commit_hash,  # type: ignore
                "similarity": evidence.similarity,  # type: ignore
                "summary": evidence.summary,  # type: ignore
            }
        if explanation is not None:
            out["explanation"] = {
                "text": explanation.text,  # type: ignore
                "source": explanation.source,  # type: ignore
            }
        console.print_json(json.dumps(out))
        return

    score_color = "red" if report.score >= 60 else "yellow" if report.score >= 30 else "green"
    console.print()
    console.rule(f"[bold]PR Risk Scorer — {commit_ish}[/bold]")
    console.print(f"\n  [bold]Risk Score:[/bold]  [{score_color}]{report.score}/100[/]")

    if report.baseline_prob is not None:
        console.print(f"  [dim]Baseline (RF) prob:[/dim] {report.baseline_prob:.3f}")
    if report.codebert_prob is not None:
        console.print(f"  [dim]CodeBERT prob:    [/dim] {report.codebert_prob:.3f}")

    # Signal table
    table = Table(title="\nSignal Breakdown", show_lines=True)
    table.add_column("Signal", style="cyan")
    table.add_column("Weight", justify="right")
    table.add_column("Triggered", justify="center")
    table.add_column("Description")

    for signal in report.signals:
        fired = "[green]✓[/green]" if signal.triggered else "[dim]✗[/dim]"
        table.add_row(signal.name, str(signal.weight), fired, signal.description)

    console.print(table)

    # RAG evidence
    if evidence is not None:
        console.print(
            f"\n  [bold cyan]📎 Similar past bug commit[/bold cyan]  "
            f"(similarity={evidence.similarity:.2f})\n"  # type: ignore
            f"  {evidence.summary}"  # type: ignore
        )
    else:
        console.print("\n  [dim]RAG evidence: no closely matching past bug commit found.[/dim]")

    # Explanation
    if explanation is not None:
        src_tag = f"[dim][{explanation.source}][/dim]"  # type: ignore
        console.print(
            Panel(
                explanation.text,  # type: ignore
                title=f"[bold]LLM Explanation {src_tag}[/bold]",
                border_style="yellow",
            )
        )

    # Decision prompt
    console.print(
        "\n  [bold yellow]⚠ Human decision required:[/bold yellow] "
        "run [bold]prscore decide[/bold] to log your review."
    )
    console.print()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def review(
    commit_ish: str = typer.Argument(..., help="Commit hash, branch, or 'HEAD' to review."),
    repo: str = typer.Option(".", "--repo", "-r", help="Path to the git repository."),
    rag: bool = typer.Option(
        True, "--rag/--no-rag", help="Use RAG evidence retrieval (default: on)."
    ),
    explain: bool = typer.Option(
        True, "--explain/--no-explain", help="Use LLM explanation (default: on)."
    ),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON."),
) -> None:
    """Compute and display the risk score for a single commit."""
    from features.extract import extract_features

    if not json_output:
        console.print(f"[dim]Extracting features from {repo} @ {commit_ish}...[/dim]")
    try:
        features = extract_features(repo, commit_ish)
    except (ValueError, Exception) as exc:
        console.print(f"[red]Feature extraction failed:[/red] {exc}")
        raise typer.Exit(code=1)

    def calculate_report() -> tuple[RiskReport, Optional[RetrievedEvidence], Optional[object]]:
        baseline_prob = _try_baseline_prob(features)
        codebert_prob = _try_codebert_prob(features)
        report = compute_risk(features, baseline_prob=baseline_prob, codebert_prob=codebert_prob)
        evidence = _try_rag_evidence(features) if rag else None
        explanation = _try_explain(report, evidence) if explain else None
        return report, evidence, explanation

    if json_output:
        with redirect_stdout(sys.stderr):
            report, evidence, explanation = calculate_report()
    else:
        report, evidence, explanation = calculate_report()

    from api.audit import insert_review

    evidence_data = (
        {
            "commit_hash": evidence.commit_hash,
            "similarity": evidence.similarity,
            "summary": evidence.summary,
        }
        if evidence is not None
        else None
    )
    review_id = insert_review(
        db_path=AUDIT_DB_PATH,
        commit_ref=commit_ish,
        diff_hash="",
        score=report.score,
        signals=report.as_dict()["signals"],
        evidence=evidence_data,
        explanation=explanation.text if explanation is not None else "",
        explanation_source=(explanation.source if explanation is not None else "not_generated"),
    )

    _print_report(
        commit_ish,
        report,
        evidence,
        explanation,
        as_json=json_output,
        review_id=review_id,
    )
    if not json_output:
        console.print(f"[dim]Review saved to the audit log (review id {review_id}).[/dim]")


@app.command()
def log(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of recent decisions to show."),
) -> None:
    """Show recent human review decisions from the audit log."""
    from api.audit import list_decisions

    rows = list_decisions(AUDIT_DB_PATH)[:limit]
    if not rows:
        console.print("[dim]No decisions logged yet.[/dim]")
        return

    table = Table(title="Audit Log", show_lines=True)
    table.add_column("ID", justify="right")
    table.add_column("Timestamp")
    table.add_column("Commit")
    table.add_column("Score", justify="right")
    table.add_column("Decision")

    for row in rows:
        dec = str(row["decision"])
        color = "green" if dec == "approve" else "red" if dec == "escalate" else "yellow"
        table.add_row(
            str(row["id"]),
            str(row["timestamp"])[:19],
            str(row.get("commit_ref", row.get("commit_hash", "")))[:12],
            str(row.get("score", "")),
            f"[{color}]{dec}[/{color}]",
        )
    console.print(table)


@app.command()
def decide(
    commit_hash: str = typer.Argument(..., help="Commit hash being reviewed."),
    score: int = typer.Argument(..., help="Risk score (0-100)."),
    decision: str = typer.Argument(..., help="approve | request_changes | escalate"),
    note: str = typer.Option("", "--note", "-n", help="Optional reviewer note."),
) -> None:
    """Log a human reviewer decision to the audit database."""
    from api.audit import insert_decision, insert_review, list_reviews

    try:
        # Find the most recent review for this commit, or create a stub
        existing = list_reviews(AUDIT_DB_PATH)
        review_id = None
        for r in existing:
            if r["commit_ref"] == commit_hash:
                review_id = r["id"]
                break
        if review_id is None:
            review_id = insert_review(
                AUDIT_DB_PATH, commit_hash, "", score, [], None, "", "local_fallback"
            )

        row_id = insert_decision(AUDIT_DB_PATH, review_id, decision, note)
        console.print(f"[green]✓ Decision logged[/green] (row id={row_id})")
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command(name="install-hook")
def install_hook(
    repo: str = typer.Option(".", "--repo", "-r", help="Path to the git repository."),
    hook: str = typer.Option("pre-push", "--hook", "-H", help="Hook type: pre-push."),
) -> None:
    """Install a git hook that runs prscore review on each commit/push."""
    import stat

    repo_path = Path(repo).resolve()
    hooks_dir = repo_path / ".git" / "hooks"

    if not hooks_dir.exists():
        console.print(f"[red]Not a git repository:[/red] {repo_path}")
        raise typer.Exit(code=1)

    if hook != "pre-push":
        console.print(f"[red]Unsupported hook type:[/red] {hook}. Use pre-push.")
        raise typer.Exit(code=1)

    hook_path = hooks_dir / hook
    if hook_path.exists():
        console.print(f"[red]Hook already exists at {hook_path}. Refusing to overwrite it.[/red]")
        console.print(
            "[dim]Review and merge the prscore hook manually to preserve its behavior.[/dim]"
        )
        raise typer.Exit(code=1)

    hook_source = Path(__file__).parent.parent / "scripts" / "git_hook.sh"
    if not hook_source.is_file():
        console.print(f"[red]Bundled pre-push hook not found:[/red] {hook_source}")
        raise typer.Exit(code=1)

    hook_path.write_text(hook_source.read_text())
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    console.print(f"[green]✓ Installed {hook} hook at {hook_path}[/green]")


def main() -> None:
    """Entry point registered in pyproject.toml."""
    app()


if __name__ == "__main__":
    main()
