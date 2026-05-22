from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from detectsmith.docs import write_docs_site
from detectsmith.coverage import build_coverage_report, write_coverage_reports
from detectsmith.gap_analyzer import cmd_gap, cmd_backlog
from detectsmith.lint import lint_rules
from detectsmith.reporting import docs_report_envelope, lint_report_envelope, test_report_envelope, write_json_report
from detectsmith.rules import discover_rule_files, parse_rule_file
from detectsmith.test_runner import run_expected_tests
from detectsmith.validate_cmd import validate_app

app = typer.Typer(help="Detection-as-code workbench for Sigma-style rules.")
console = Console()

# Register validate as a subcommand at the Typer level
app.add_typer(validate_app, name="validate")


@app.command()
def lint(
    rules_path: Path,
    output_format: str = typer.Option("text", "--format", help="Output format: text or json."),
    output: Optional[Path] = typer.Option(None, "--output", help="Optional report output path."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show recommendations for each finding."),
) -> None:
    """Lint Sigma-style detection rules."""
    if output_format not in {"text", "json"}:
        raise typer.BadParameter("format must be 'text' or 'json'")

    try:
        rules = [parse_rule_file(path) for path in discover_rule_files(rules_path)]
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    report = lint_rules(rules)
    has_errors = report.summary.findings_error > 0
    status = "completed_with_findings" if (has_errors or report.summary.findings_warn) else "success"

    if output_format == "json" or output is not None:
        report_path = output or Path("reports/lint.json")
        write_json_report(lint_report_envelope(report, Path.cwd(), status), report_path)

    _print_lint_report(report, verbose=verbose)

    if has_errors:
        raise typer.Exit(1)


@app.command("test")
def test_rules(
    expected_path: Path,
    output_format: str = typer.Option("text", "--format", help="Output format: text or json."),
    output: Optional[Path] = typer.Option(None, "--output", help="Optional report output path."),
) -> None:
    """Run detection regression tests."""
    if output_format not in {"text", "json"}:
        raise typer.BadParameter("format must be 'text' or 'json'")
    report = run_expected_tests(expected_path)
    failed = report.summary.tests_failed > 0
    status = "failed" if failed else "success"
    if output_format == "json" or output is not None:
        report_path = output or Path("reports/test_results.json")
        write_json_report(test_report_envelope(report, Path.cwd(), status), report_path)
    _print_test_report(report)
    if failed:
        raise typer.Exit(1)


@app.command("gap")
def gap_cmd(
    scan_db: Path,
    coverage: Optional[Path] = typer.Option(None, "--coverage", help="Path to Detectsmith attack_coverage.json."),
) -> None:
    """Analyze detection gaps against a SepulchrynScan report."""
    code = cmd_gap(scan_db, coverage)
    raise typer.Exit(code)


@app.command("backlog")
def backlog_cmd(
    scan_db: Path,
    coverage: Optional[Path] = typer.Option(None, "--coverage"),
    output: Optional[Path] = typer.Option(None, "--output"),
) -> None:
    """Generate detection backlog JSON from a SepulchrynScan report."""
    code = cmd_backlog(scan_db, coverage, output)
    raise typer.Exit(code)


@app.command()
def coverage(
    rules_path: Path,
    output_format: str = typer.Option("text", "--format", help="Output format: text or json."),
    output: Optional[Path] = typer.Option(None, "--output", help="Optional report output path."),
) -> None:
    """Generate ATT&CK coverage reports."""
    if output_format not in {"text", "json"}:
        raise typer.BadParameter("format must be 'text' or 'json'")
    rules = [parse_rule_file(path) for path in discover_rule_files(rules_path)]
    report = build_coverage_report(rules)
    json_path = output or Path("reports/attack_coverage.json")
    markdown_path = json_path.parent / "attack_coverage.md"
    write_coverage_reports(report, json_path, markdown_path)
    _print_coverage_report(report)


@app.command()
def docs(
    rules_path: Path,
    out: Path = typer.Option(Path("site"), "--out", help="Documentation output directory."),
    output_format: str = typer.Option("text", "--format", help="Output format: text or json."),
    output: Optional[Path] = typer.Option(None, "--output", help="Optional report output path."),
) -> None:
    """Generate Markdown documentation."""
    if output_format not in {"text", "json"}:
        raise typer.BadParameter("format must be 'text' or 'json'")
    rules = [parse_rule_file(path) for path in discover_rule_files(rules_path)]
    result = write_docs_site(rules, out)
    if output_format == "json" or output is not None:
        write_json_report(docs_report_envelope(result, Path.cwd()), output or Path("reports/docs.json"))
    console.print(f"Wrote {result.rule_pages_written} rule pages to {result.output_dir}")


def _print_lint_report(report, *, verbose: bool = False) -> None:
    table = Table(title="Detectsmith lint")
    table.add_column("Rule")
    table.add_column("Score", justify="right")
    table.add_column("Findings")
    for result in report.rules:
        finding_ids = ", ".join(finding.check_id for finding in result.findings) or "ok"
        table.add_row(result.path, str(result.score), finding_ids)
    console.print(table)
    console.print(
        f"Rules: {report.summary.rules_total} | Errors: {report.summary.findings_error} | "
        f"Warnings: {report.summary.findings_warn} | Avg score: {report.summary.average_score}"
    )
    if verbose:
        _print_finding_recommendations(report)


def _print_finding_recommendations(report) -> None:
    console.print()
    for result in report.rules:
        if result.findings:
            console.print(Panel(f"[bold]{result.path}[/bold]", expand=False))
            for finding in result.findings:
                icon = "![red]X[/red]" if finding.severity == "error" else "⚠" if finding.severity == "warn" else "ℹ"
                console.print(f"  {icon} [yellow]{finding.check_id}[/yellow]: {finding.message}")
                console.print(f"    → {finding.recommendation}")


def _print_test_report(report) -> None:
    table = Table(title="Detectsmith tests")
    table.add_column("Test")
    table.add_column("Status")
    table.add_column("Matched", justify="right")
    table.add_column("Reason")
    for result in report.tests:
        table.add_row(result.name, result.status, str(result.matched_events), result.failure_reason or "")
    console.print(table)
    console.print(
        f"Tests: {report.summary.tests_total} | Passed: {report.summary.tests_passed} | "
        f"Failed: {report.summary.tests_failed} | Rules tested: {report.summary.rules_tested}"
    )


def _print_coverage_report(report) -> None:
    console.print(
        f"Rules: {report.summary.rules_total} | Tactics: {report.summary.tactics_covered} | "
        f"Techniques: {report.summary.techniques_covered} | Missing ATT&CK tags: {report.summary.rules_missing_attack_tags}"
    )
