from pathlib import Path

import pytest
from typer.testing import CliRunner

from detectsmith.cli import app

runner = CliRunner()


def test_validate_run_all_pass(tmp_path: Path):
    """When all four commands pass, validate run should exit 0."""
    rules = tmp_path / "rules"
    rules.mkdir()
    rules.joinpath("good.yml").write_text("""
title: Good Rule
id: detectsmith-validate-001
description: A valid rule
logsource:
  product: windows
  service: sysmon
detection:
  selection:
    CommandLine|contains: test
  condition: selection
level: low
status: experimental
tags:
  - attack.execution
  - attack.t1059.001
falsepositives:
  - None expected
references:
  - https://attack.mitre.org/
""", encoding="utf-8")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    fixtures_dir = tests_dir / "fixtures"
    fixtures_dir.mkdir()

    good_rule = rules / "good.yml"
    good_pos = fixtures_dir / "good_positive.jsonl"
    good_neg = fixtures_dir / "good_negative.jsonl"

    good_pos.write_text('{"CommandLine": "test command here"}', encoding="utf-8")
    good_neg.write_text('{"CommandLine": "something else entirely"}', encoding="utf-8")

    tests_dir.joinpath("expected.yml").write_text(f"""
tests:
  - name: good_rule_positive
    rule: {good_rule.as_posix()}
    fixture: {good_pos.as_posix()}
    should_match: true
  - name: good_rule_negative
    rule: {good_rule.as_posix()}
    fixture: {good_neg.as_posix()}
    should_match: false
""", encoding="utf-8")

    result = runner.invoke(app, ["validate", "run", "--rules", str(rules), "--tests", str(tests_dir / "expected.yml"), "--site-out", str(tmp_path / "site")])
    assert result.exit_code == 0, result.output
    assert "All checks passed" in result.output


def test_validate_run_lint_fail_triggers_exit_1(tmp_path: Path):
    """When lint finds errors, validate run should exit 1."""
    rules = tmp_path / "rules"
    rules.mkdir()
    rules.joinpath("bad.yml").write_text("title: Missing Fields\n", encoding="utf-8")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    tests_dir.joinpath("expected.yml").write_text("tests: []", encoding="utf-8")

    result = runner.invoke(app, ["validate", "run", "--rules", str(rules), "--tests", str(tests_dir / "expected.yml"), "--site-out", str(tmp_path / "site")])
    assert result.exit_code == 1
    assert "lint failed" in result.output