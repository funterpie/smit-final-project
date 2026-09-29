"""cli/main.py — prscore CLI entry point.

Usage:
    prscore review <commit-ish>

Runs the risk engine on a dummy CommitFeatures (stub for now) and prints the
score + signal breakdown. Real feature extraction (PyDriller) is wired in Week 1.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from features.schema import CommitFeatures
from models.risk_engine import RiskReport, compute_risk

app = typer.Typer(
    name="prscore",
    help="PR Risk Scorer — just-in-time software defect prediction.",
    add_completion=False,
)
console = Console()


@app.callback()
def main_callback() -> None:
    """PR Risk Scorer CLI."""
    pass


def _dummy_features(commit_ish: str) -> CommitFeatures:
    """Return a placeholder CommitFeatures for demo/scaffold purposes.

    TODO (Week 1): Replace with a real call to features.extract.extract_features().
    """
    # Vary the dummy slightly so different commit hashes look different in demos.
    seed = sum(ord(c) for c in commit_ish) % 100
    return CommitFeatures(
        lines_added=50 + seed * 3,
        lines_removed=20 + seed,
        files_touched=3 + seed % 5,
        dispersion=1.5 + (seed % 5) * 0.5,
        author_bug_rate=round(0.05 + (seed % 4) * 0.1, 2),
        hours_since_last_commit=float(8 + seed % 48),
        tests_added=(seed % 3 != 0),
        touches_sensitive_module=(seed % 7 == 0),
    )


def _print_report(commit_ish: str, report: RiskReport) -> None:
    """Print a formatted risk report to stdout."""
    # Header
    console.print()
    console.rule(f"[bold]PR Risk Scorer — {commit_ish}[/bold]")
    console.print(f"\n  [bold]Risk Score:[/bold]  [{'red' if report.score >= 50 else 'yellow' if report.score >= 25 else 'green'}]{report.score}/100[/]")

    # Signal table
    table = Table(title="\nSignal Breakdown", show_lines=True)
    table.add_column("Signal", style="cyan")
    table.add_column("Weight", justify="right")
    table.add_column("Triggered", justify="center")
    table.add_column("Description")

    for signal in report.signals:
        fired = "[green]✓[/green]" if signal.triggered else "[dim]✗[/dim]"
        table.add_row(
            signal.name,
            str(signal.weight),
            fired,
            signal.description,
        )

    console.print(table)

    # Evidence / explanation placeholders
    console.print("\n  [dim]RAG evidence:  [/dim][italic]not yet implemented (Week 3)[/italic]")
    console.print("  [dim]LLM explain:   [/dim][italic]not yet implemented (Week 3)[/italic]")

    # Decision prompt placeholder
    console.print(
        "\n  [bold yellow]⚠ Human decision required:[/bold yellow] "
        "[dim]Approve / Request Changes / Escalate (audit log: not yet wired)[/dim]"
    )
    console.print()


@app.command()
def review(
    commit_ish: str = typer.Argument(
        ...,
        help="Commit hash, branch name, or 'HEAD' to review.",
    ),
    repo: str = typer.Option(
        ".",
        "--repo",
        "-r",
        help="Path to the git repository (default: current directory).",
    ),
) -> None:
    """Compute and display the risk score for a single commit.

    Currently uses a dummy CommitFeatures stub.
    Real PyDriller extraction will replace _dummy_features() in Week 1.
    """
    features = _dummy_features(commit_ish)
    report = compute_risk(features)
    _print_report(commit_ish, report)


def main() -> None:
    """Entry point registered in pyproject.toml."""
    app()


if __name__ == "__main__":
    main()
