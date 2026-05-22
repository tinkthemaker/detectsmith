from pathlib import Path

import pytest

from detectsmith.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_lint_bad_yaml_raises_parse_error_and_exits_nonzero(tmp_path: Path):
    """A YAML parse error should be caught and printed as a friendly error, not a traceback."""
    rules = tmp_path / "rules"
    rules.mkdir()
    rules.joinpath("broken.yml").write_text("- list not a dict", encoding="utf-8")
    result = runner.invoke(app, ["lint", str(rules)])
    assert result.exit_code == 1
    # The error message should be human-readable, not a traceback
    assert "RuleParseError" not in result.output
    assert "rule must be a top-level mapping" in result.output


def test_lint_verbose_shows_recommendations_for_warnings(tmp_path: Path):
    """With --verbose, lint should show recommendations for rules with warnings (exit still 0)."""
    rules = tmp_path / "rules"
    rules.mkdir()
    # A rule that has warnings but no errors (score still 100 after penalty)
    # Realistic: good title, description, level, status, logsource, detection — just missing ATT&CK tags
    rules.joinpath("warn_only.yml").write_text("""
title: Suspicious JavaScript Execution
id: detectsmith-test-warn
description: Detects execution of suspicious JavaScript via mshta
logsource:
  product: windows
  service: sysmon
detection:
  selection:
    CommandLine|contains: mshta
  condition: selection
level: high
status: stable
falsepositives:
  - Legitimate use of mshta by administrators
""", encoding="utf-8")
    result = runner.invoke(app, ["lint", str(rules), "--verbose"])
    assert result.exit_code == 0
    assert "missing_attack_tags" in result.output
    assert "Add tactic and technique tags" in result.output


def test_lint_no_args_shows_usage_and_exit_2(tmp_path: Path):
    """Calling lint with no arguments should show usage and exit 2 (Typer's usage exit)."""
    result = runner.invoke(app, ["lint"])
    assert result.exit_code == 2
    assert "Usage:" in result.output or "Missing argument" in result.output