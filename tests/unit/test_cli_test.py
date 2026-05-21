from pathlib import Path

from typer.testing import CliRunner

from detectsmith.cli import app


def write_rule(path: Path):
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
""".strip(),
        encoding="utf-8",
    )


def test_test_cli_writes_json_report_and_exits_zero_when_passed(tmp_path: Path):
    rule = tmp_path / "rule.yml"
    fixture = tmp_path / "fixture.jsonl"
    expected = tmp_path / "expected.yml"
    output = tmp_path / "reports" / "test_results.json"
    write_rule(rule)
    fixture.write_text('{"CommandLine":"powershell.exe -enc SQBFAFgA"}\n', encoding="utf-8")
    expected.write_text(
        f"""
tests:
  - name: positive
    rule: {rule.as_posix()}
    fixture: {fixture.as_posix()}
    should_match: true
""".strip(),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(app, ["test", str(expected), "--format", "json", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert '"command": "test"' in output.read_text(encoding="utf-8")


def test_test_cli_exits_nonzero_when_case_fails(tmp_path: Path):
    rule = tmp_path / "rule.yml"
    fixture = tmp_path / "fixture.jsonl"
    expected = tmp_path / "expected.yml"
    write_rule(rule)
    fixture.write_text('{"CommandLine":"powershell.exe -nop"}\n', encoding="utf-8")
    expected.write_text(
        f"""
tests:
  - name: failing
    rule: {rule.as_posix()}
    fixture: {fixture.as_posix()}
    should_match: true
""".strip(),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(app, ["test", str(expected)])

    assert result.exit_code == 1
    assert "failing" in result.output
