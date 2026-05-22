from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from detectsmith.rules import discover_rule_files, parse_rule_file
from detectsmith.lint import lint_rules
from detectsmith.coverage import build_coverage_report
from detectsmith.test_runner import run_expected_tests
from detectsmith.docs import write_docs_site

validate_app = typer.Typer(help="Run all checks (lint, test, coverage, docs) before committing.")
console = Console()


@validate_app.command("run")
def validate_run(
    rules_path: Path = typer.Option(Path("rules"), "--rules", help="Rules directory."),
    tests_path: Path = typer.Option(Path("tests/expected.yml"), "--tests", help="Tests expected.yml path."),
    site_out: Path = typer.Option(Path("site"), "--site-out", help="Docs output directory."),
) -> None:
    """Run all four detectsmith commands and exit nonzero if any fail."""
    console.print("[bold]Running Detectsmith validation...[/bold]\n")

    # 1. lint
    console.print("[cyan]1/4 lint...[/cyan]")
    try:
        rules = [parse_rule_file(path) for path in discover_rule_files(rules_path)]
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)
    lint_report = lint_rules(rules)
    _print_lint_summary(lint_report)
    if lint_report.summary.findings_error > 0:
        console.print("\n[red]✗ lint failed — fix errors before committing[/red]")
        raise typer.Exit(1)
    console.print("[green]✓ lint passed[/green]\n")

    # 2. test
    console.print("[cyan]2/4 test...[/cyan]")
    test_report = run_expected_tests(tests_path)
    _print_test_summary(test_report)
    if test_report.summary.tests_failed > 0:
        console.print("\n[red]✗ tests failed — fix failures before committing[/red]")
        raise typer.Exit(1)
    console.print("[green]✓ tests passed[/green]\n")

    # 3. coverage
    console.print("[cyan]3/4 coverage...[/cyan]")
    coverage_report = build_coverage_report(rules)
    console.print(
        f"  Tactics: {coverage_report.summary.tactics_covered} | "
        f"Techniques: {coverage_report.summary.techniques_covered}"
    )
    console.print("[green]✓ coverage generated[/green]\n")

    # 4. docs
    console.print("[cyan]4/4 docs...[/cyan]")
    docs_result = write_docs_site(rules, site_out)
    console.print(f"  Wrote {docs_result.rule_pages_written} rule pages")
    console.print("[green]✓ docs generated[/green]\n")

    console.print("[bold green]✓ All checks passed — ready to commit[/bold green]")


def _print_lint_summary(report) -> None:
    console.print(
        f"  Rules: {report.summary.rules_total} | "
        f"Errors: {report.summary.findings_error} | "
        f"Warnings: {report.summary.findings_warn} | "
        f"Avg score: {report.summary.average_score}"
    )


def _print_test_summary(report) -> None:
    console.print(
        f"  Tests: {report.summary.tests_total} | "
        f"Passed: {report.summary.tests_passed} | "
        f"Failed: {report.summary.tests_failed}"
    )