from pathlib import Path

from typer.testing import CliRunner

from detectsmith.cli import app


def test_docs_cli_writes_site_and_json_report(tmp_path: Path):
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "rule.yml").write_text(
        """
title: PowerShell Encoded Command
id: rule-1
description: Detects PowerShell encoded command execution behavior.
logsource:
  product: windows
detection:
  selection:
    CommandLine|contains: " -enc "
  condition: selection
level: medium
status: test
tags:
  - attack.execution
  - attack.t1059.001
""".strip(),
        encoding="utf-8",
    )
    out_dir = tmp_path / "site"
    output = tmp_path / "reports" / "docs.json"
    runner = CliRunner()

    result = runner.invoke(app, ["docs", str(rules), "--out", str(out_dir), "--format", "json", "--output", str(output)])

    assert result.exit_code == 0
    assert (out_dir / "index.md").exists()
    assert output.exists()
    assert '"command": "docs"' in output.read_text(encoding="utf-8")
