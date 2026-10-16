"""cli/main.py — prscore CLI entry point (fully wired).

Usage:
    prscore review <commit-ish> [--repo PATH] [--no-rag] [--no-explain] [--json]
    prscore log [--limit N]
    prscore decide <commit-hash> <score> <decision>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import AUDIT_DB_PATH, GROQ_API_KEY, INDEX_DIR, SIMILARITY_THRESHOLD
from features.schema import CommitFeatures
from models.risk_engine import RiskReport, compute_risk
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

def _try_baseline_prob(features: CommitFeatures) -> float | None:
    """Attempt to get baseline probability; return None if model not trained yet."""
    try:
        from models.baseline import predict_baseline
        return predict_baseline(features, model="rf")
    except FileNotFoundError:
        return None


def _try_codebert_prob(features: CommitFeatures) -> float | None:
    """Attempt to get CodeBERT probability; return None if model not available."""
    try:
        from models.codebert import predict_codebert
        return predict_codebert(features)
    except FileNotFoundError:
        return None


def _try_rag_evidence(features: CommitFeatures) -> RetrievedEvidence | None:
    """Attempt RAG evidence retrieval; return None if index not built yet."""
    try:
        from rag.retrieve import retrieve_evidence
        return retrieve_evidence(features, index_dir=str(INDEX_DIR), threshold=SIMILARITY_THRESHOLD)
    except Exception:
        return None


def _try_explain(report: RiskReport, evidence: RetrievedEvidence | None) -> object | None:
    """Attempt LLM explanation; return None on any failure."""
    try:
        from explain.llm_explain import explain_risk
        return explain_risk(report, evidence, groq_api_key=GROQ_API_KEY)
    except Exception:
        return None


def _print_report(
    commit_ish: str,
    report: RiskReport,
    evidence: RetrievedEvidence | None,
    explanation: object | None,
    as_json: bool = False,
) -> None:
    """Print a formatted risk report to stdout."""
    if as_json:
        out = report.as_dict()
        out["commit"] = commit_ish
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
    console.print(
        f"\n  [bold]Risk Score:[/bold]  [{score_color}]{report.score}/100[/]"
    )

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
    no_rag: bool = typer.Option(False, "--no-rag", help="Skip RAG evidence retrieval."),
    no_explain: bool = typer.Option(False, "--no-explain", help="Skip LLM explanation."),
    as_json: bool = typer.Option(False, "--json", help="Output raw JSON."),
) -> None:
    """Compute and display the risk score for a single commit."""
    from features.extract import extract_features

    console.print(f"[dim]Extracting features from {repo} @ {commit_ish}...[/dim]")
    try:
        features = extract_features(repo, commit_ish)
    except (ValueError, Exception) as exc:
        console.print(f"[red]Feature extraction failed:[/red] {exc}")
        raise typer.Exit(code=1)

    baseline_prob = _try_baseline_prob(features)
    codebert_prob = _try_codebert_prob(features)
    report = compute_risk(features, baseline_prob=baseline_prob, codebert_prob=codebert_prob)

    evidence = None if no_rag else _try_rag_evidence(features)
    explanation = None if no_explain else _try_explain(report, evidence)

    _print_report(commit_ish, report, evidence, explanation, as_json=as_json)


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
            str(row["commit_hash"])[:12],
            str(row["score"]),
            f"[{color}]{dec}[/{color}]",
        )
    console.print(table)


@app.command()
def decide(
    commit_hash: str = typer.Argument(..., help="Commit hash being reviewed."),
    score: int = typer.Argument(..., help="Risk score (0-100)."),
    decision: str = typer.Argument(..., help="approve | request_changes | escalate"),
    explanation: str = typer.Option("", "--explanation", "-e", help="Optional explanation text."),
) -> None:
    """Log a human reviewer decision to the audit database."""
    from api.audit import insert_decision

    try:
        row_id = insert_decision(AUDIT_DB_PATH, commit_hash, score, decision, explanation)
        console.print(f"[green]✓ Decision logged[/green] (row id={row_id})")
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point registered in pyproject.toml."""
    app()


if __name__ == "__main__":
    main()
