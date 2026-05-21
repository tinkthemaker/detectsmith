from pathlib import Path

from typer.testing import CliRunner

from detectsmith.cli import app


def test_coverage_cli_writes_json_and_markdown_reports(tmp_path: Path):
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "rule.yml").write_text(
        """
title: Example
id: rule-1
description: Example rule.
logsource:
  product: windows
detection:
  selection:
    Image: cmd.exe
  condition: selection
level: low
status: test
tags:
  - attack.execution
  - attack.t1059.001
""".strip(),
        encoding="utf-8",
    )
    output = tmp_path / "reports" / "attack_coverage.json"
    runner = CliRunner()

    result = runner.invoke(app, ["coverage", str(rules), "--format", "json", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert (output.parent / "attack_coverage.md").exists()
    assert '"command": "coverage"' in output.read_text(encoding="utf-8")
