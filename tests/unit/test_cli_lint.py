from pathlib import Path

from typer.testing import CliRunner

from detectsmith.cli import app


def write_valid_rule(path: Path):
    path.write_text(
        """
title: PowerShell Encoded Command
id: rule-1
description: Detects PowerShell encoded command execution behavior.
logsource:
  product: windows
  category: process_creation
detection:
  selection:
    CommandLine|contains: " -enc "
  condition: selection
level: medium
status: test
references:
  - https://attack.mitre.org/techniques/T1059/001/
falsepositives:
  - Administrative scripts may use encoded commands.
tags:
  - attack.execution
  - attack.t1059.001
""".strip(),
        encoding="utf-8",
    )


def test_lint_cli_writes_json_report(tmp_path: Path):
    rules = tmp_path / "rules"
    rules.mkdir()
    write_valid_rule(rules / "rule.yml")
    output = tmp_path / "reports" / "lint.json"
    runner = CliRunner()

    result = runner.invoke(app, ["lint", str(rules), "--format", "json", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    report_text = output.read_text(encoding="utf-8")
    assert '"command": "lint"' in report_text
    assert '"rules_total": 1' in report_text


def test_lint_cli_exits_nonzero_on_error_findings(tmp_path: Path):
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "bad.yml").write_text("title: Missing Fields", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(app, ["lint", str(rules)])

    assert result.exit_code == 1
    assert "missing_id" in result.output
